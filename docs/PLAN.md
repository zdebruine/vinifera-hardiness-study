# Cold-Hardy Vinifera Suitability Scoring — Plan & Data Disclosure

Goal: an open, reproducible score for 200+ *V. vinifera* varieties (anchored to the
UC Davis FPS / National Grape Registry universe, ~584 varieties) combining
(a) **winter survival** and (b) **ripening attainability**, with all sources and
code publicly disclosed.

## Data sources (availability + license)

| Pillar | Source | Access in *this* session | Access in repo code (open net) | License |
|---|---|---|---|---|
| Climate (GDD, winter minima, freeze events) | Open-Meteo Historical / ERA5 & ERA5-Land, 1940– | Docs only (host not whitelisted for fetch) | Yes — HTTP GET, no key | CC BY 4.0 |
| Variety universe | UC Davis FPS / National Grape Registry (~584 varieties) | Per-variety pages readable | Yes — scrape `fgrdetails.cfm?varietyid=N` | UC Regents; cite |
| Variety × region (colocation + ha weights) | Anderson & Nelgen, *Which Winegrape Varieties are Grown Where?* (Adelaide), 9 Excel files, 700+ regions, 1700+ varieties, incl. regional climate + synonyms | Pages readable; Excel not fetchable here | Yes — download Excel; or user uploads | Free ebook/data; cite |
| Synonym crosswalk | Robinson/Harding/Vouillamoz *Wine Grapes*; VIVC prime names; JKI | Partial (records) | Partial | mixed; cite |
| Pedigree / ancestry | VIVC pedigree module (~23k cultivars); Wikipedia/Wikidata parent1×parent2 | Record-by-record readable | Yes — scrape/Wikidata SPARQL | cite |
| Genotype (for true NJ tree) | Laucou 2011 (SSR), Myles 2011 (SNP, GRIN/Dryad) | Supplement readable | Yes — download | cite |
| Cold hardiness LT50/LT90 | WSU/Ferguson AJEV 2014 dynamic model (~23 genotypes, data since 1988); Chinese 124-cultivar vinifera LT50 study; Iranian 20-cultivar; TAMU class table; many single-variety papers | Open PDFs readable; paywalled = abstract only | Some downloadable | cite; some paywalled |
| Vine-level survival after a specific freeze | **Mostly does not exist as data** | No | No | — |

## What "autonomous collection" means here (honest split)
1. **In-session via web tools (Claude):** discrete published facts — variety lists, site
   coordinates, appellation/permitted-variety rules, parentage records, LT50 values from
   *open-access* papers, DOC/DOCG ripeness anchors. Good for building seed tables and
   spot-validation; not for bulk harvest.
2. **Repo code on your open-network machine:** bulk Open-Meteo pulls, Anderson Excel
   download, FPS/VIVC scraping, Wikidata SPARQL, genotype-file downloads. This is where
   the heavy lifting lives (and what goes on GitHub).
3. **Needs you / cannot be obtained:** full text of paywalled journals; proprietary or
   unpublished vineyard survival logs; true vine-level survival ground truth.

## Pipeline (stages smoke-tested in `smoke_tests.py`)
1. **Climate → features.** Per cold-exposed site: GDD base 50°F (Apr–Oct, Winkler) and
   the minimum temperature of each historical freeze event (ERA5 back to 1940 covers the
   canonical Feb-1956, Jan-1985, Jan-1987 events). *Caveat: ERA5 grid is ~9–25 km; vineyard
   frost pockets / cold-air drainage are sub-grid — treat site minima as regional, flag bias.*
2. **Survival association (binary).** For each (variety, freeze event): does the variety
   appear in commercial production at exposed sites before AND after the event? *Weak signal —
   confounds replanting, burial/hilling, variety switching, microclimate. Model as a noisy
   observation, not ground truth; carry uncertainty forward.*
3. **LT50 meta-analysis.** Harmonize literature to a common target (max midwinter bud LT50)
   adjusting for method (DTA/LTE vs electrolyte leakage vs tetrazolium), tissue (bud/cane/root),
   and sampling date/acclimation. Where the WSU dynamic model exists (~23 genotypes), prefer
   model-predicted hardiness on each freeze date vs the event minimum.
4. **Knowledge graph + imputation.** Nodes = varieties; edges = colocation weighted by
   co-bearing hectares (Anderson). Propagate LT50 / survival via Gaussian-field (harmonic)
   solution. *Caveat: colocation encodes tradition/market, not only hardiness — report
   imputation as a prior with cross-validated error, not measurement.*
5. **Ancestry refinement.** Pedigree → Wright numerator-relationship (A) matrix → kinship
   clusters; optionally a marker-based NJ/UPGMA tree if a genotype matrix is obtained. Use
   relatedness as a regularizer / hierarchical prior on the survival score. *Caveat: within
   pure vinifera the hardiness range is narrow and the pedigree is admixed (Pinot, Gouais,
   Traminer as super-parents) — expect modest, not dominant, ancestry signal.*
6. **Ripening fitness.** P(ripen) = Φ((GDD_site − GDD_req,variety)/σ); GDD_req anchored from
   established DOC/DOCG/AVA sites that ripen the variety to a target style. Normal CDF gives
   the logistic-shaped curve (reconciles "Gaussian" + "logistic").
7. **Composite score.** Survival × ripening as two explicit axes (report both, plus a combined
   suitability), with propagated uncertainty and a sensitivity analysis on weights/σ.

## Reproducibility
- Pinned environment; every external pull cached with retrieval date + source URL.
- Deterministic seeds; unit tests per stage; data-provenance manifest.
- License/attribution file crediting Open-Meteo (CC BY 4.0), Anderson & Nelgen, VIVC, FPS,
  and each LT50 source.
