#!/usr/bin/env python3
"""Scrape wine regions/appellations from Wikidata, at the LOWEST level available.

Wikidata models appellations hierarchically (P131 'located in' / P361 'part of') with
coordinates (P625), so one SPARQL query yields thousands of regions with parents and
coords. We keep every node and mark ``is_leaf=1`` for those that are not the parent of any
other node in the set -- the lowest classified level, never a broad cluster when a finer
one exists.

Needs network with a descriptive User-Agent (Wikidata requires one). Runs on CI.

ITERATION 1: the class QIDs below are a best guess from inside the sandbox (no network to
verify). The scraper dumps raw JSON + counts so the query can be corrected after the first
live run. ``parse_bindings`` and ``compute_leaves`` are pure and unit-tested.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "wikidata_regions.json"
OUT = ROOT / "data" / "db" / "regions.csv"

ENDPOINT = "https://query.wikidata.org/sparql"
UA = ("vinifera-hardiness-study/0.1 (https://github.com/zdebruine/vinifera-hardiness-study; "
      "research) python-urllib")

# Candidate classes for "wine appellation / wine region". UNION so wrong guesses just add
# nothing; refine after run 1 using the raw dump.
QUERY = """
SELECT ?region ?regionLabel ?parent ?country ?countryLabel ?coord WHERE {
  VALUES ?cls { wd:Q2140391 wd:Q1827682 wd:Q2376123 wd:Q1990546 wd:Q1010967 }
  ?region wdt:P31/wdt:P279* ?cls .
  OPTIONAL { ?region wdt:P131 ?parent. }
  OPTIONAL { ?region wdt:P17 ?country. }
  OPTIONAL { ?region wdt:P625 ?coord. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""


def run_sparql(query: str, retries: int = 4) -> dict:
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp)
        except Exception as e:  # noqa: BLE001 - network/429, retry
            last = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"SPARQL failed: {last}")


def _qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1] if uri else ""


def parse_bindings(payload: dict) -> list[dict]:
    """SPARQL JSON -> region rows (qid, name, parent_qid, country, lat, lon).

    Deduplicates by region; coordinates parsed from 'Point(lon lat)'.
    """
    by_qid: dict[str, dict] = {}
    for b in payload.get("results", {}).get("bindings", []):
        qid = _qid(b["region"]["value"])
        if not qid:
            continue
        row = by_qid.setdefault(qid, {
            "region_id": qid, "name": "", "parent_id": "", "country": "",
            "latitude": "", "longitude": "", "wikidata_id": qid,
        })
        if "regionLabel" in b:
            row["name"] = b["regionLabel"]["value"]
        if "parent" in b and not row["parent_id"]:
            row["parent_id"] = _qid(b["parent"]["value"])
        if "countryLabel" in b:
            row["country"] = b["countryLabel"]["value"]
        if "coord" in b and not row["latitude"]:
            m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", b["coord"]["value"])
            if m:
                row["longitude"], row["latitude"] = m.group(1), m.group(2)
    return list(by_qid.values())


def compute_leaves(rows: list[dict]) -> None:
    """Set is_leaf=1 on rows that are not a parent of any other row; keep parent_id only
    when the parent is itself in the set (so the hierarchy stays within our regions)."""
    ids = {r["region_id"] for r in rows}
    parents = set()
    for r in rows:
        if r["parent_id"] in ids:
            parents.add(r["parent_id"])
        else:
            r["parent_id"] = ""  # parent is outside the wine set -> treat as top-level
    for r in rows:
        r["is_leaf"] = "0" if r["region_id"] in parents else "1"
        r["level"] = "appellation"
        r["macro_region"] = ""
        r["source"] = "wikidata_v1"


def main() -> int:
    print("Querying Wikidata for wine regions...")
    payload = run_sparql(QUERY)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(payload)[:5_000_000], encoding="utf-8")
    rows = parse_bindings(payload)
    print(f"Parsed {len(rows)} regions.")
    if not rows:
        print("No regions returned -- class QIDs likely wrong; inspect "
              "data/raw/wikidata_regions.json and refine QUERY.", file=sys.stderr)
        return 1
    compute_leaves(rows)
    cols = ["region_id", "name", "parent_id", "level", "is_leaf", "country",
            "macro_region", "latitude", "longitude", "wikidata_id", "source"]
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows({c: r.get(c, "") for c in cols} for r in rows)
    leaves = sum(1 for r in rows if r["is_leaf"] == "1")
    print(f"Wrote {len(rows)} regions ({leaves} leaf/lowest-level) to data/db/regions.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
