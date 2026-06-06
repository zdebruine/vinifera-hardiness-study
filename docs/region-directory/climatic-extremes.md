# Climatic variation within a region — finding the extremes

Each region gets a **climate envelope**, not a single number, captured by a few **anchor
points** (real vineyards/estates/localities with coordinates) chosen to **bracket the
region's climatic extremes**. Weather is later pulled at each anchor (deferred), and the
spread across anchors becomes the region's climate-variation signal — which is what makes a
region's survival/ripening behaviour meaningful rather than averaged-away.

This is the same "anchors that bracket extremes" idea already in the data model
(`wineries` table + `src/vinifera/climate_score.py`); this doc is the **search-driven method**
for choosing those anchors honestly.

## What drives within-region climate spread (what to bracket)

Pick anchors that span the dominant local gradient(s):

1. **Elevation** — usually the biggest lever. Highest vs. lowest vineyard elevation (cooler,
   later-ripening, more frost/winter-cold up high; warmer down low). E.g. Etna, Alto Adige,
   Vayots Dzor, Mendoza's Uco.
2. **Maritime ↔ continental** — distance from sea/large lake. Cooler, milder-winter maritime
   vs. larger-diurnal, colder-winter continental. E.g. Bordeaux Médoc vs. inland; Finger Lakes
   lakeshore vs. upland.
3. **Latitude / aspect** — within elongated regions (Mosel, Douro, Rhône): north vs. south
   ends, sun-facing vs. shaded slopes.
4. **Valley floor ↔ slope** — cold-air drainage pools on floors (frost/winter-kill risk);
   mid-slopes are warmer ("thermal belt"). Critical for the *survival* axis.

Record which gradient each anchor represents in the anchor's `role` (e.g. `high_altitude`,
`cool_maritime`, `warm`, `valley_floor`).

## Search workflow per region (LLM + web search)

For a leaf region, run targeted searches and read the consensus across reputable sources:

- `"<region> highest elevation vineyard"` / `"<region> lowest / valley floor vineyard"`
- `"<region> coolest site"` / `"<region> warmest sub-zone"`
- `"<region> wineries map elevation"` / `"<region> cru / Ried / climat altitude"`
- `"<region> climate continental maritime diurnal"`

From the results, identify 2–3 concrete, real places at the extremes — a named **estate,
single vineyard, or village** (not an invented name) — and get coordinates from Wikidata /
OpenStreetMap-Nominatim / GeoNames (see `data-sources.md`). Mark `coord_precision` honestly
(`exact` only if from a gazetteer/estate listing; otherwise `approx`).

## Honesty rules

- **Never invent** an estate name or coordinate. If a real extreme site can't be pinned,
  use a real **locality/sub-zone** centroid and mark it `approx`.
- ERA5/Open-Meteo grid is ~9–25 km; frost pockets and cold-air drainage are **sub-grid**, so
  valley-floor anchors are *regional proxies*, not site truth — carry that caveat (already
  flagged in the climate module).
- Prefer **boundary-derived** extremes where a polygon exists (min/max elevation point inside
  the AVA/PDO from a DEM) — more objective than prose. That's a retrieval-phase enhancement.

## Output shape (feeds the existing model)

Per anchor, the fields the pipeline already expects:
`winery_id, region_id, name, role, latitude, longitude, elevation_m, coord_precision, notes`.
Two or more anchors per leaf region; the weather step (deferred) turns them into per-region
GDD range, coldest winter minimum, and a variation score (`build_climate.py`).

## Status

Method documented. Population of real anchors is intentionally **not** mass-produced by hand
here — it pairs naturally with the leaf-region enumeration and geocoding in the local
retrieval phase. The curated `wineries` examples already in the repo (Bordeaux Médoc vs.
Sauternes, Etna low vs. high, Kakheti valley vs. foothills, etc.) are the pattern to follow.
