# Cold-Hardy Vinifera Suitability Scoring

An open, reproducible score for 200+ *Vitis vinifera* varieties — anchored to the
UC Davis FPS / National Grape Registry universe (~584 varieties) — combining two
explicit axes:

1. **Winter survival** — how likely the variety is to survive midwinter cold at a site.
2. **Ripening attainability** — how likely the variety is to ripen to a target style at that site.

All sources, retrieval dates, and code are publicly disclosed.

> **What this is, and is not.** This is a **decision-support / hypothesis-generating
> score**, not a validated predictive model. Vine-level survival ground truth largely
> does not exist (see [`docs/PLAN.md`](docs/PLAN.md)), so the survival axis is an
> uncertainty-carrying *imputation* built from noisy proxies and the published LT50
> literature — not a measurement. Within pure *V. vinifera* the genetic hardiness range
> is intrinsically narrow; expect much of the useful variance to come from ripening and
> viticulture rather than intrinsic genetics. Read the caveats before trusting a number.

## Status

Early scaffold with a working tools site. The data-dependent pipeline stages are stubbed
with documented interfaces and caveats; the two closed-form stages (ripening, scoring) are
implemented and drive the live tools. See `docs/PLAN.md` for the full plan and data
disclosure, and `docs/ANALYSIS.md` for known methodological risks.

## Web tools (GitHub Pages)

**Live site:** https://zdebruine.github.io/vinifera-hardiness-study/
*(goes live once Pages is enabled — see "Deploying the site" below).*

Six mobile-responsive, client-side tools built from the seed data:

1. **Suitability explorer** — variety × site → survival × ripening, with propagated uncertainty.
2. **Ripening calculator** — interactive P(ripen) = Φ((GDD−GDD_req)/σ) with a live curve.
3. **Climate & freezes** — seed sites, Winkler GDD, per-event freeze minima, burial flags.
4. **Cold hardiness** — sortable/filterable midwinter bud LT50 table.
5. **Varieties & pedigree** — universe with synonyms and recorded parents.
6. **Colocation** — region × variety bearing hectares.

The site is static (no build tooling, no npm); `scripts/build_site.py` converts
`data/seed/*.csv` into `site/data/*.json` using the real `src/vinifera` math.

### Deploying the site

`.github/workflows/pages.yml` rebuilds the data and deploys on every push. **One-time
setup:** in the repo, go to **Settings → Pages → Source → "GitHub Actions"**. The
`github-pages` environment deploys from the default branch (`main`), so the site goes live
after this branch is merged to `main` (or run the workflow manually via *Actions →
Deploy site to GitHub Pages → Run workflow*).

### Preview locally

```bash
python3 scripts/build_site.py
python3 -m http.server -d site 8000   # then open http://localhost:8000
```

## Pipeline

| Stage | Module | Status |
|---|---|---|
| 1. Climate → features (GDD, freeze minima) | `src/vinifera/climate.py` | stub |
| 2. Survival association (noisy binary proxy) | `src/vinifera/survival.py` | stub |
| 3. LT50 meta-analysis (method-harmonized) | `src/vinifera/lt50.py` | stub |
| 4. Knowledge graph + imputation | `src/vinifera/graph_impute.py` | stub |
| 5. Ancestry refinement (A-matrix / NJ tree) | `src/vinifera/ancestry.py` | stub |
| 6. Ripening fitness P(ripen) | `src/vinifera/ripening.py` | stub |
| 7. Composite score (survival × ripening) | `src/vinifera/score.py` | stub |

## Known methodological risks (read these)

- **Stage 2 ↔ Stage 4 circularity.** Survival labels derive from commercial production
  presence; the imputation graph's edges are co-bearing hectares (also production
  presence). Keep them statistically independent, or fold into one hierarchical model,
  or the same signal is double-counted and self-confirms.
- **Viticulture confound.** Many cold-climate vinifera regions bury/hill vines over
  winter. Presence at such a site ≠ unburied genetic hardiness. Tracked via a
  burial/hilling region flag (`burial_flag`).
- **Narrow vinifera hardiness range.** Method noise across LT50 assays can exceed
  between-variety differences. Prefer the mechanistic WSU dynamic model where available;
  use the survival association only as soft validation.
- **ERA5 sub-grid.** Frost pockets / cold-air drainage are sub-grid (~9–25 km). Site
  minima are biased regional proxies, not site truth.
- **No external ground truth.** Cross-validation tests internal consistency, not
  correctness.

## Layout

```
src/vinifera/      pipeline stages + pure scoring math (one module per stage)
data/db/           canonical relational dataset (varieties, regions, wineries, ...)
site/              static GitHub Pages tools site (index.html, styles.css, app.js)
site/data/         generated JSON consumed by the tools (built from data/seed/)
data/seed/         small illustrative seed sample of every source type (committed)
data/raw/          immutable bulky caches (gitignored; provenance in data/PROVENANCE.md)
data/interim/      intermediate artifacts (anchor_climate.csv committed; rest gitignored)
data/processed/    final tables/scores (region_climate.csv committed; .db gitignored)
docs/              plan, data disclosure, SCHEMA, methodology notes
scripts/           pipelines (build_db, build_site, fetch_weather, build_climate)
scripts/sources/   external-source loaders (FPS catalog, Anderson hectares)
tests/             per-stage + pipeline unit tests
smoke_tests.py     fast end-to-end smoke test of stage interfaces
.claude/           SessionStart hook: auto-installs deps and runs smoke tests
```

## Data model (relational)

The two anchor tables — **varieties** and **regions** — are curated as CSVs under
`data/db/` and compiled to SQLite (`scripts/build_db.py`, with referential-integrity
checks). They connect through `variety_region` (what grows where) and `wineries` (climate
anchors that bracket each region's extremes). Full schema in
[`docs/SCHEMA.md`](docs/SCHEMA.md); honesty notes in [`data/db/README.md`](data/db/README.md).

```bash
python3 scripts/build_db.py        # -> data/processed/vinifera.db
```

**Sourcing approach (current direction):** LLM-first via web search, building a documented
directory of the world's wine regions drilled to the lowest classified level, plus the
varieties and per-region climate signal. See **[`docs/region-directory/`](docs/region-directory/)**
— the classification systems per country, where the authoritative/geospatial lists live, and
the climate-extremes method.

Bulk page retrieval (the FPS catalog scrape, region leaf enumeration, weather pulls) is
**deferred to a local Claude Code instance** with open web access; the in-session sandbox
can only web-search, not fetch. The `scripts/sources/` scrapers and the (now manual-only)
`scrape-sources.yml` / `data-refresh.yml` workflows are retained for that local phase, not
auto-run here.

## Setup

```bash
python3 -m pip install -r requirements.txt
python3 smoke_tests.py        # dependency-free interface check
python3 -m pytest tests/ -q   # unit tests for the closed-form stages
```

## Reproducibility

- Pinned environment (`requirements.txt`).
- Every external pull cached under `data/raw/` with retrieval date + source URL recorded
  in `data/PROVENANCE.md`.
- Deterministic seeds; per-stage unit tests; data-provenance manifest.
- Attribution for every source in `ATTRIBUTION.md`.

## License

Code: MIT (`LICENSE`). Data sources retain their own licenses — see `ATTRIBUTION.md`.
