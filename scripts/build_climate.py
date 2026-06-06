#!/usr/bin/env python3
"""Aggregate per-anchor weather features into per-region climate + a variation score.

Reads data/interim/anchor_climate.csv (produced by fetch_weather.py) and writes
data/processed/region_climate.csv using the pure aggregation in vinifera.climate_score.

Run fetch_weather.py first (on an open-network machine / CI). Stdlib only.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vinifera.climate_score import AnchorClimate, region_climate  # noqa: E402

INTERIM = ROOT / "data" / "interim" / "anchor_climate.csv"
OUT = ROOT / "data" / "processed" / "region_climate.csv"


def main() -> int:
    if not INTERIM.exists():
        print("data/interim/anchor_climate.csv not found -- run scripts/fetch_weather.py "
              "first (needs open network; runs in the data-refresh GitHub Action).",
              file=sys.stderr)
        return 1

    by_region: dict[str, list[AnchorClimate]] = {}
    with INTERIM.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if not r["mean_annual_min_c"] or not r["coldest_winter_min_c"]:
                continue
            ac = AnchorClimate(
                winery_id=r["winery_id"], region_id=r["region_id"],
                mean_season_gdd_f=float(r["mean_season_gdd_f"]),
                coldest_winter_min_c=float(r["coldest_winter_min_c"]),
                mean_annual_min_c=float(r["mean_annual_min_c"]),
            )
            by_region.setdefault(ac.region_id, []).append(ac)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["region_id", "n_anchors", "gdd_min_f", "gdd_max_f", "gdd_spread_f",
                         "coldest_winter_min_c", "mean_annual_min_c", "variation_score"])
        for region_id, anchors in sorted(by_region.items()):
            rc = region_climate(anchors)
            writer.writerow([rc.region_id, rc.n_anchors, round(rc.gdd_min_f, 1),
                             round(rc.gdd_max_f, 1), round(rc.gdd_spread_f, 1),
                             rc.coldest_winter_min_c, round(rc.mean_annual_min_c, 1),
                             rc.variation_score])
    print(f"Wrote region climate for {len(by_region)} regions to "
          f"data/processed/region_climate.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
