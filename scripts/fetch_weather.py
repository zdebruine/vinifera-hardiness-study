#!/usr/bin/env python3
"""Pull historical daily weather for each climate anchor and derive per-anchor features.

Runs against Open-Meteo's ERA5 archive (CC BY 4.0, no key). This needs OUTBOUND NETWORK,
which the in-session sandbox does not have -- it is intended to run on the open-network
side (GitHub Actions; see .github/workflows/data-refresh.yml) or any open machine.

Outputs:
  data/raw/weather/<winery_id>.json   cached raw response (immutable; provenance recorded)
  data/interim/anchor_climate.csv     per-anchor GDD + winter-minima features

The HTTP call is isolated in ``fetch_one``; ``features_from_daily`` is pure and unit-tested.
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vinifera.climate_score import c_to_f, daily_gdd_f  # noqa: E402

WINERIES = ROOT / "data" / "db" / "wineries.csv"
RAW_DIR = ROOT / "data" / "raw" / "weather"
INTERIM = ROOT / "data" / "interim" / "anchor_climate.csv"
PROVENANCE = ROOT / "data" / "PROVENANCE.md"

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
START, END = "1991-01-01", "2020-12-31"   # 30-year climate normal period
NH_SEASON = range(4, 11)                   # Apr-Oct
SH_SEASON = {10, 11, 12, 1, 2, 3, 4}       # Southern Hemisphere growing season


def fetch_one(lat: float, lon: float, start: str = START, end: str = END,
              retries: int = 4) -> dict:
    """GET daily min/max from Open-Meteo ERA5 archive, with backoff. Network required."""
    q = (f"{ARCHIVE_URL}?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}"
         "&daily=temperature_2m_min,temperature_2m_max&timezone=UTC")
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(q, timeout=60) as resp:
                return json.load(resp)
        except Exception as e:  # noqa: BLE401 - network/parse, retry
            last = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Open-Meteo fetch failed after {retries} tries: {last}")


def features_from_daily(dates: list[str], tmin_c: list[float], tmax_c: list[float],
                        southern: bool) -> dict:
    """Pure: daily series -> mean season GDD, coldest min, mean annual min.

    Skips days with missing values. Season is Apr-Oct (N) or Oct-Apr (S).
    """
    season = SH_SEASON if southern else set(NH_SEASON)
    gdd_by_year: dict[int, float] = {}
    min_by_year: dict[int, float] = {}
    coldest = float("inf")
    for d, lo, hi in zip(dates, tmin_c, tmax_c):
        if lo is None or hi is None:
            continue
        y, m = int(d[:4]), int(d[5:7])
        coldest = min(coldest, lo)
        min_by_year[y] = min(min_by_year.get(y, float("inf")), lo)
        if m in season:
            gdd_by_year[y] = gdd_by_year.get(y, 0.0) + daily_gdd_f(c_to_f(lo), c_to_f(hi))
    n = max(1, len(gdd_by_year))
    mean_gdd = sum(gdd_by_year.values()) / n
    annual_mins = list(min_by_year.values())
    mean_annual_min = sum(annual_mins) / len(annual_mins) if annual_mins else None
    return {
        "mean_season_gdd_f": round(mean_gdd, 1),
        "coldest_winter_min_c": None if coldest == float("inf") else round(coldest, 1),
        "mean_annual_min_c": None if mean_annual_min is None else round(mean_annual_min, 1),
        "n_years": len(gdd_by_year),
    }


def read_wineries() -> list[dict]:
    with WINERIES.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def append_provenance(lines: list[str]) -> None:
    stamp = datetime.now(timezone.utc).date().isoformat()
    block = f"\n### Open-Meteo weather pull ({stamp})\n\n" + "\n".join(lines) + "\n"
    with PROVENANCE.open("a", encoding="utf-8") as fh:
        fh.write(block)


def main(argv: list[str]) -> int:
    refresh = "--refresh" in argv
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM.parent.mkdir(parents=True, exist_ok=True)
    rows, prov = [], []
    for w in read_wineries():
        wid = w["winery_id"]
        cache = RAW_DIR / f"{wid}.json"
        if cache.exists() and not refresh:
            data = json.loads(cache.read_text(encoding="utf-8"))
        else:
            lat, lon = float(w["latitude"]), float(w["longitude"])
            data = fetch_one(lat, lon)
            cache.write_text(json.dumps(data), encoding="utf-8")
            prov.append(f"- `{wid}` ({lat},{lon}) -> `data/raw/weather/{wid}.json` "
                        f"from {ARCHIVE_URL} [{START}..{END}], CC BY 4.0")
            time.sleep(1)  # be polite
        daily = data["daily"]
        feats = features_from_daily(daily["time"], daily["temperature_2m_min"],
                                    daily["temperature_2m_max"], southern=float(w["latitude"]) < 0)
        rows.append({"winery_id": wid, "region_id": w["region_id"], **feats})
        print(f"  {wid:24} GDD {feats['mean_season_gdd_f']:>7} "
              f"coldest {feats['coldest_winter_min_c']}C")

    with INTERIM.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["winery_id", "region_id", "mean_season_gdd_f",
                                "coldest_winter_min_c", "mean_annual_min_c", "n_years"])
        writer.writeheader()
        writer.writerows(rows)
    if prov:
        append_provenance(prov)
    print(f"\nWrote {len(rows)} anchor feature rows to data/interim/anchor_climate.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
