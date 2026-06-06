"""Climate feature + region-variation scoring (pure functions).

The network-dependent pulls live in ``scripts/fetch_weather.py``; the math that turns daily
temperatures into per-anchor features and aggregates anchors into a region score lives here
so it is deterministic and unit-tested without any network.

Conventions: temperatures in degrees Celsius unless a name ends in ``_f``. GDD uses the
Winkler base of 50 degF over the Apr-Oct growing season (Northern Hemisphere).
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev

GDD_BASE_F = 50.0


def c_to_f(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0


def daily_gdd_f(tmin_f: float, tmax_f: float, base_f: float = GDD_BASE_F) -> float:
    """Single-day growing degree days, base 50 degF, floored at zero (Winkler)."""
    avg = (tmin_f + tmax_f) / 2.0
    return max(0.0, avg - base_f)


def season_gdd_f(daily_min_c: list[float], daily_max_c: list[float]) -> float:
    """Sum GDD over the supplied (already season-filtered) daily series, in degF-days."""
    if len(daily_min_c) != len(daily_max_c):
        raise ValueError("min/max series length mismatch")
    return sum(daily_gdd_f(c_to_f(lo), c_to_f(hi)) for lo, hi in zip(daily_min_c, daily_max_c))


@dataclass(frozen=True)
class AnchorClimate:
    """Per-anchor climate features derived from a multi-year daily series."""

    winery_id: str
    region_id: str
    mean_season_gdd_f: float      # averaged across years
    coldest_winter_min_c: float   # absolute minimum observed (worst freeze)
    mean_annual_min_c: float      # mean of yearly minima (hardiness-zone style)


@dataclass(frozen=True)
class RegionClimate:
    region_id: str
    n_anchors: int
    gdd_min_f: float              # coolest anchor
    gdd_max_f: float              # warmest anchor
    gdd_spread_f: float           # within-region growing-season variation
    coldest_winter_min_c: float   # worst anchor (drives survival screening)
    mean_annual_min_c: float
    variation_score: float        # 0..~1, higher = more internally varied


def region_climate(anchors: list[AnchorClimate],
                   gdd_ref_f: float = 1500.0,
                   min_ref_c: float = 12.0) -> RegionClimate:
    """Aggregate per-anchor features into a region summary + variation score.

    ``variation_score`` blends the within-region spread of growing-season GDD (normalized
    by ``gdd_ref_f``) and of annual winter minima (normalized by ``min_ref_c``). It captures
    how much a single region's climate spans its extremes -- the point of sampling multiple
    anchors. Reference scales are documented defaults, adjustable in sensitivity analysis.
    """
    if not anchors:
        raise ValueError("need at least one anchor")
    gdds = [a.mean_season_gdd_f for a in anchors]
    mins = [a.mean_annual_min_c for a in anchors]
    gdd_spread = max(gdds) - min(gdds)
    min_spread = max(mins) - min(mins)
    score = 0.5 * (gdd_spread / gdd_ref_f) + 0.5 * (min_spread / min_ref_c)
    return RegionClimate(
        region_id=anchors[0].region_id,
        n_anchors=len(anchors),
        gdd_min_f=min(gdds),
        gdd_max_f=max(gdds),
        gdd_spread_f=gdd_spread,
        coldest_winter_min_c=min(a.coldest_winter_min_c for a in anchors),
        mean_annual_min_c=mean(mins),
        variation_score=round(score, 4),
    )
