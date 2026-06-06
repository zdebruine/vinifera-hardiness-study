# Data model

The canonical relational dataset lives as CSVs under `data/db/` (git-friendly, reviewable
diffs) and is compiled into a SQLite database at `data/processed/vinifera.db` by
`scripts/build_db.py`. Varieties and regions are the two anchor tables; everything else
hangs off them.

```
                         variety_region (M:N)
                    ┌──────────────────────────────┐
                    │ region_id  variety_id          │
        varieties ──┤ role  evidence  bearing_ha     ├── regions
            │       └──────────────────────────────┘     │
            │                                             │
        synonyms (1:N)                              wineries (1:N)
        variety_id → synonym                        region_id → climate anchor
                                                          │
                                                    (weather pulls)
                                                          │
                                                    region_climate (derived)
```

## Tables

### `varieties` — the orchestrating unit
One row per **true *V. vinifera*** variety. Sourced from the UC Davis FPS / National Grape
Registry catalog (`scripts/sources/scrape_fps.py`) and filtered to pure vinifera by
`scripts/sources/classify_vinifera.py`, which **excludes interspecific hybrids (incl.
vinifera × hybrid crosses), American species, muscadines, and rootstocks**. Columns:
`species`, `is_vinifera` (1/0), `classification` (`vinifera` / `hybrid_or_nonvinifera` /
`rootstock` / `unverified`), `fps_variety_id`, `vivc_number`, and `needs_review` — set when
the rules can't decide, so it gets a second-source look rather than a guess. `source` is
`fps_scrape_v1` for scraped rows, `curated_v1` for the initial hand seed.

### `regions` — wine regions / appellations (hierarchical, lowest level)
One row per region at **every** level, linked by `parent_id` (self-referencing). We operate
at the **lowest classified level**: `is_leaf = 1` marks regions that are not the parent of
any other region in the set — sub-sub-appellations / crus / climats, never a broad cluster
when a finer level exists. Sourced from Wikidata (`scripts/sources/scrape_regions_wikidata.py`)
with `wikidata_id`, `latitude`/`longitude` (from P625), `level`, `country`, and `source`
(`wikidata_v1` / `curated_v1`). The `leaf_regions` view exposes just the leaves.

### `wineries` — climate anchors (climatic extremes within a region)
Two or more points per flagship region, chosen to **bracket that region's climatic
extremes** (e.g. warm valley floor vs. cool high-altitude). These are the coordinates the
weather pipeline pulls. To stay honest, anchors are **real localities / sub-zones** (not
invented winery names) with `coord_precision = approx`; specific commercial vineyards can
be substituted later without schema change.

### `variety_region` — what grows where (the bridge)
M:N association linking the two anchor tables. `evidence` records why the link exists
(`signature`, `principal`, `grown_over_1_acre`). `bearing_ha` is left blank in the curated
seed and filled from Anderson & Nelgen by `scripts/sources/fetch_anderson.py`. This table
is how *region → climate* and *variety → region* compose into *variety → climate*.

### `synonyms` — crosswalk
`variety_id → synonym` with a `context` (country/region/language), for reconciling FPS,
VIVC, and Anderson naming.

### `region_climate` — derived
Produced by `scripts/build_climate.py` from the per-anchor weather features. Per region:
GDD range across anchors (within-region variation), coldest winter minimum, mean season
GDD, and a `climate_variation_score`. Not committed by hand — generated from weather pulls.

## Referential integrity (enforced by `build_db.py`)

- every `variety_region.variety_id` and `synonyms.variety_id` exists in `varieties`
- every `variety_region.region_id` and `wineries.region_id` exists in `regions`
- ids are unique within each table

## Provenance & honesty

Curated rows are tagged `curated_v1` and represent real, checkable facts (which varieties
are grown where, where regions are). Numeric specifics still to be sourced — exact FPS
membership, VIVC numbers, bearing hectares, and all weather/climate values — are left blank
or flagged and are filled by the loaders in `scripts/sources/` and the weather pipeline,
with retrieval recorded in `data/PROVENANCE.md`. See `data/db/README.md`.
