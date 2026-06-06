# Data provenance manifest

Every external pull is recorded here at retrieval time: what, from where, when, how, and
the license. Raw bytes live under `data/raw/` (gitignored) — this manifest is the committed
record of what they are and where they came from.

## Conventions

- One row per discrete pull. Use the source URL exactly as fetched.
- `retrieved` = ISO date (UTC) the bytes were obtained.
- `sha256` = checksum of the cached file under `data/raw/` (fill once cached).
- Keep raw files immutable; derived artifacts go to `data/interim/` and `data/processed/`.

## Manifest

| id | source | url | retrieved | cached path | sha256 | license | notes |
|---|---|---|---|---|---|---|---|
| _none yet_ | | | | | | | no automated pulls performed in-session (sandbox egress blocked) |

## Curated relational dataset (`data/db/`)

The varieties/regions/wineries/variety_region/synonyms tables are **hand-curated real
facts** tagged `curated_v1` (not an automated retrieval). They are the initial Europe +
Caucasus slice. Numeric fields still to be sourced are blank/flagged and filled by the
loaders below, which append dated entries here on each run:

- `scripts/fetch_weather.py` → Open-Meteo ERA5 per anchor (appends an "Open-Meteo weather
  pull" block).
- `scripts/sources/fetch_fps_catalog.py` → UC Davis NGR membership (appends an
  "FPS/NGR reconciliation" block).
- `scripts/sources/fetch_anderson.py` → Anderson & Nelgen bearing hectares.
