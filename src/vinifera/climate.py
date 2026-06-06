"""Stage 1 — Climate features from Open-Meteo / ERA5 (CC BY 4.0).

Per cold-exposed site, derive:
  * GDD base 50 degF over Apr-Oct (Winkler), and
  * the minimum temperature of each historical freeze event (ERA5 from 1940 covers the
    canonical Feb-1956, Jan-1985, Jan-1987 events).

CAVEAT: the ERA5 grid is ~9-25 km. Vineyard frost pockets and cold-air drainage -- the
actual vine-kill mechanism -- are sub-grid. Treat returned site minima as *regional*
proxies and flag the bias; do not present them as site truth.
"""
from __future__ import annotations

from dataclasses import dataclass

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
GDD_BASE_F = 50.0  # Winkler base temperature, degrees Fahrenheit


@dataclass(frozen=True)
class Site:
    """A cold-exposed growing site."""

    site_id: str
    latitude: float
    longitude: float
    name: str = ""
    burial_flag: bool = False  # vines buried/hilled over winter -> survival signal unreliable


@dataclass(frozen=True)
class ClimateFeatures:
    site_id: str
    gdd_winkler_f: float                 # season GDD, base 50 degF, Apr-Oct
    freeze_event_minima_c: dict[str, float]  # event label -> grid min temperature (degC)
    grid_resolution_km: float            # ERA5 ~9-25 km; carried so bias is explicit


def fetch_daily_temperatures(site: Site, start: str, end: str) -> object:
    """Pull cached/fresh daily min/max temperatures for a site from Open-Meteo.

    Implementations must cache raw responses under ``data/raw/`` and record the pull in
    ``data/PROVENANCE.md`` (URL + retrieval date + checksum). Retries with backoff.
    """
    raise NotImplementedError("Stage 1: Open-Meteo daily temperature pull not implemented")


def compute_features(site: Site, start: str, end: str) -> ClimateFeatures:
    """Compute GDD and per-event freeze minima for a site."""
    raise NotImplementedError("Stage 1: climate feature computation not implemented")
