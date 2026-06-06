#!/usr/bin/env python3
"""Reconcile data/db/varieties.csv against the UC Davis FPS / National Grape Registry.

Goal: flip every ``fps_status = unverified`` to ``listed`` or ``absent`` by matching our
varieties (and their synonyms) against the public NGR catalog, and discover FPS varieties
we don't yet have.

Split by testability:
  * ``fetch_catalog_names`` -- NETWORK; scrapes ngr.ucdavis.edu. Selectors are best-effort
    and must be confirmed on first live run (the sandbox has no outbound network). Runs on
    the open-network side (GitHub Actions / any open machine).
  * ``normalize`` / ``reconcile`` -- PURE; matching logic, unit-tested offline.

Caches the raw catalog to data/raw/fps_catalog.json and records provenance.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VARIETIES = ROOT / "data" / "db" / "varieties.csv"
SYNONYMS = ROOT / "data" / "db" / "synonyms.csv"
RAW = ROOT / "data" / "raw" / "fps_catalog.json"
PROVENANCE = ROOT / "data" / "PROVENANCE.md"

NGR_BASE = "https://ngr.ucdavis.edu/"
# The plan documents per-variety pages at fgrdetails.cfm?varietyid=N; the public search/list
# page enumerates Vitis selections. Confirm these against the live site on first run.
NGR_LIST_URL = "https://ngr.ucdavis.edu/GRSearch.cfm"


def normalize(name: str) -> str:
    """Lowercase, strip accents/punctuation, collapse whitespace for matching."""
    s = name.lower().strip()
    accents = str.maketrans("àáâäãåçèéêëìíîïñòóôöõùúûüý  ", "aaaaaaceeeeiiiinooooouuuuy  ")
    s = s.translate(accents)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_variety_list(html: str) -> set[str]:
    """Extract candidate variety names from an NGR listing page.

    Tries BeautifulSoup if available, else a permissive regex over anchor/cell text.
    Selectors are intentionally broad; tighten once the live markup is confirmed.
    """
    names: set[str] = set()
    try:
        from bs4 import BeautifulSoup  # type: ignore
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a[href*='fgrdetails.cfm']"):
            txt = a.get_text(strip=True)
            if txt:
                names.add(txt)
        if not names:  # fall back to table cells
            for td in soup.select("td"):
                txt = td.get_text(strip=True)
                if txt and len(txt) < 60:
                    names.add(txt)
    except ImportError:
        for m in re.finditer(r"fgrdetails\.cfm\?varietyid=\d+[^>]*>([^<]{2,60})<", html):
            names.add(m.group(1).strip())
    return {n for n in names if n}


def fetch_catalog_names() -> set[str]:
    """NETWORK: download and parse the NGR Vitis catalog listing(s)."""
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(NGR_LIST_URL, headers={"User-Agent": "vinifera-hardiness-study/0.1"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                html = resp.read().decode("utf-8", "replace")
            names = parse_variety_list(html)
            RAW.parent.mkdir(parents=True, exist_ok=True)
            RAW.write_text(json.dumps(sorted(names), indent=2), encoding="utf-8")
            return names
        except Exception as e:  # noqa: BLE401 - network, retry
            last = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"NGR fetch failed: {last}")


def reconcile(catalog: set[str], varieties: list[dict],
              synonyms: dict[str, list[str]]) -> tuple[list[dict], list[str]]:
    """PURE: set in_fps/fps_status from catalog membership; return (updated rows, unmatched).

    A variety is ``listed`` if its prime name or any synonym normalizes to a catalog entry,
    else ``absent``. Returns catalog names we matched to nothing (candidate new varieties).
    """
    norm_catalog = {normalize(c) for c in catalog}
    matched_catalog: set[str] = set()
    for v in varieties:
        candidates = [v["prime_name"], *synonyms.get(v["variety_id"], [])]
        norms = {normalize(c) for c in candidates}
        hit = norms & norm_catalog
        if hit:
            v["in_fps"], v["fps_status"] = "1", "listed"
            matched_catalog |= hit
        else:
            v["in_fps"], v["fps_status"] = "0", "absent"
    unmatched = sorted(c for c in catalog if normalize(c) not in matched_catalog)
    return varieties, unmatched


def _read_synonyms() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    with SYNONYMS.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["variety_id"], []).append(r["synonym"])
    return out


def main() -> int:
    with VARIETIES.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = reader.fieldnames
        rows = list(reader)
    catalog = fetch_catalog_names()
    rows, unmatched = reconcile(catalog, rows, _read_synonyms())
    with VARIETIES.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    stamp = datetime.now(timezone.utc).date().isoformat()
    with PROVENANCE.open("a", encoding="utf-8") as fh:
        fh.write(f"\n### FPS/NGR reconciliation ({stamp})\n\n- {len(catalog)} catalog names "
                 f"from {NGR_LIST_URL}; {len(unmatched)} unmatched (candidate additions).\n")
    print(f"Reconciled {len(rows)} varieties against {len(catalog)} NGR names.")
    print(f"{len(unmatched)} catalog names matched nothing we have (candidate new varieties).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
