# Canonical relational dataset (`data/db/`)

Source-of-truth CSVs for the study's two anchor tables — **varieties** and **regions** —
and the tables that connect them. Compiled to SQLite by `scripts/build_db.py`. Full schema
in [`../../docs/SCHEMA.md`](../../docs/SCHEMA.md).

| File | Rows are | Key |
|---|---|---|
| `varieties.csv` | one *V. vinifera* variety | `variety_id` |
| `regions.csv` | one wine region | `region_id` |
| `wineries.csv` | one climate anchor (extreme) in a region | `winery_id` → `region_id` |
| `variety_region.csv` | variety grown in a region | `region_id` + `variety_id` |
| `synonyms.csv` | a synonym for a variety | `variety_id` |

## What is real vs. to-be-sourced

**Real, curated facts** (`source = curated_v1`): variety names/colors/origins, region
locations, which varieties are grown in which regions, and synonyms. Anchor localities are
real places; their coordinates are **approximate** (`coord_precision = approx`).

**Left blank / flagged for the loaders:**
- `varieties.fps_status = unverified` → reconciled by `scripts/sources/fetch_fps_catalog.py`
- `variety_region.bearing_ha` (empty) → filled from Anderson by `scripts/sources/fetch_anderson.py`
- all weather & `region_climate` values → produced by the weather pipeline (runs on open
  network, i.e. GitHub Actions — see `.github/workflows/data-refresh.yml`)

Retrievals are recorded in [`../PROVENANCE.md`](../PROVENANCE.md). Coverage today is an
initial Europe + Caucasus slice meant to be **expanded** by the FPS loader (full catalog)
and further curation, not a complete census.
