#!/usr/bin/env python3
"""Scrape the UC Davis FPS / National Grape Registry grape catalog.

Enumerates every variety in the registry and fetches its detail page, caching raw HTML so
re-runs are incremental and the parsing can be refined offline. Outputs
data/interim/fps_catalog_raw.csv for the vinifera classifier (classify_vinifera.py).

Needs outbound network with a browser-like User-Agent (UC Davis 403s default clients) --
runs on GitHub Actions, not the in-session sandbox. Polite: caching, delays, retries.

ITERATION 1: the exact listing markup/parameters are unconfirmed from inside the sandbox.
``extract_detail_links`` and the enumeration try several patterns and log what worked;
expect to tighten selectors after the first live run's diagnostics.
"""
from __future__ import annotations

import csv
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "fps"
OUT = ROOT / "data" / "interim" / "fps_catalog_raw.csv"

BASE = "https://ngr.ucdavis.edu/"
LIST_URL = BASE + "fgrvarieties.cfm"
DETAIL_URL = BASE + "fgrdetails.cfm?varietyid={vid}"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 vinifera-hardiness-study/0.1 (research; contact via GitHub)")

DETAIL_LINK_RE = re.compile(r"fgrdetails\.cfm\?varietyid=(\d+)[^>]*>\s*([^<]{1,80})", re.I)
SPECIES_RE = re.compile(
    r"\bVitis\s+(vinifera|labrusca|riparia|rupestris|aestivalis|berlandieri|"
    r"rotundifolia|cinerea|champinii|amurensis|x?\s*[a-z]+)\b", re.I)
HYBRID_RE = re.compile(r"\b(hybrid|interspecific|complex hybrid)\b", re.I)
ROOTSTOCK_RE = re.compile(r"\brootstock\b", re.I)


def fetch(url: str, retries: int = 4) -> str:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(5 * (attempt + 1))
            last = e
        except Exception as e:  # noqa: BLE001 - network, retry
            last = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"fetch failed {url}: {last}")


def extract_detail_links(html: str) -> dict[str, str]:
    """Return {variety_id: name} for every fgrdetails link found in a listing page."""
    out: dict[str, str] = {}
    for vid, name in DETAIL_LINK_RE.findall(html):
        name = re.sub(r"\s+", " ", name).strip()
        if name:
            out[vid] = name
    return out


def enumerate_varieties() -> dict[str, str]:
    """Collect every (variety_id -> name) from the registry listing(s).

    Tries the base list page, then A-Z letter-indexed variants (parameter name unknown,
    so a few candidates are attempted). Logs which patterns yielded results.
    """
    found: dict[str, str] = {}
    candidates = [LIST_URL]
    for letter in "abcdefghijklmnopqrstuvwxyz":
        candidates += [f"{LIST_URL}?letter={letter}", f"{LIST_URL}?alpha={letter}",
                       f"{LIST_URL}?CFGRP={letter.upper()}"]
    for url in candidates:
        try:
            links = extract_detail_links(fetch(url))
        except RuntimeError as e:
            print(f"  (skip {url}: {e})", file=sys.stderr)
            continue
        if links:
            print(f"  {len(links):4d} links from {url}")
            found.update(links)
        time.sleep(1)
    return found


def parse_detail(html: str) -> dict:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    species = SPECIES_RE.search(text)
    return {
        "species_text": species.group(0) if species else "",
        "is_hybrid_text": "1" if HYBRID_RE.search(text) else "0",
        "is_rootstock_text": "1" if ROOTSTOCK_RE.search(text) else "0",
        "page_excerpt": text[:300].strip(),
    }


def main(argv: list[str]) -> int:
    limit = next((int(a.split("=")[1]) for a in argv if a.startswith("--limit=")), None)
    refresh = "--refresh" in argv
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    print("Enumerating FPS/NGR varieties...")
    varieties = enumerate_varieties()
    print(f"Discovered {len(varieties)} varieties.")
    if not varieties:
        print("No varieties found -- listing markup likely differs; inspect a cached page.",
              file=sys.stderr)
        return 1

    items = sorted(varieties.items(), key=lambda kv: int(kv[0]))
    if limit:
        items = items[:limit]
    rows = []
    for i, (vid, name) in enumerate(items, 1):
        cache = RAW_DIR / f"{vid}.html"
        if cache.exists() and not refresh:
            html = cache.read_text(encoding="utf-8")
        else:
            html = fetch(DETAIL_URL.format(vid=vid))
            cache.write_text(html, encoding="utf-8")
            time.sleep(1)  # polite
        rows.append({"fps_variety_id": vid, "name": name, **parse_detail(html)})
        if i % 50 == 0:
            print(f"  fetched {i}/{len(items)} detail pages")

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["fps_variety_id", "name", "species_text",
            "is_hybrid_text", "is_rootstock_text", "page_excerpt"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
