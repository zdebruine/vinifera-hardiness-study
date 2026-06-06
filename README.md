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

Early scaffold. The pipeline stages below are stubbed with documented interfaces and
caveats; none are implemented yet. See `docs/PLAN.md` for the full plan and data
disclosure, and the analysis notes for known methodological risks.

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
src/vinifera/      pipeline stages (one module per stage)
data/raw/          immutable external pulls (gitignored; provenance in data/PROVENANCE.md)
data/interim/      intermediate artifacts (gitignored)
data/processed/    final tables/scores (gitignored)
docs/              plan, data disclosure, methodology notes
scripts/           reproducible entry points (pulls, builds)
tests/             per-stage unit tests
smoke_tests.py     fast end-to-end smoke test of stage interfaces
```

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
