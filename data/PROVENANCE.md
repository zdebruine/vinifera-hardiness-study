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
| _none yet_ | | | | | | | scaffold only — no pulls performed |
