# Methodology analysis & known risks

A critical review of `PLAN.md`. The goal is to keep the project honest about what the
score can and cannot claim.

## What the plan gets right

- **Three-way data honesty** (in-session facts / repo bulk pulls / cannot-be-obtained).
  The third bucket — *vine-level survival ground truth largely does not exist* — is stated
  up front rather than hand-waved.
- **Two explicit axes** (survival × ripening). A variety can be hardy but never ripen, or
  ripen easily but die; collapsing these prematurely hides the real decision.
- **Survival modeled as a noisy observation, not ground truth**, with uncertainty carried
  forward.
- **Reproducibility discipline**: pinned env, cached pulls with retrieval date + URL,
  provenance manifest, per-stage tests.

## Risks, in rough order of how much they threaten the result

### 1. Stage 2 ↔ Stage 4 circularity (highest priority)
Stage 2 derives survival labels from *commercial production presence*. Stage 4 propagates
those labels along a graph whose edges are *co-bearing hectares* (also production presence).
Imputing a production-derived signal across a production-derived graph can self-confirm.
**Mitigation:** keep the two statistically independent, or fold them into a single
hierarchical model rather than chaining point estimates, so the same signal is not counted
twice.

### 2. Viticulture confound (burial/hilling)
Much cold-climate vinifera is buried/hilled over winter (China, Russia, parts of Eastern
Europe and the US Midwest). "Present before and after a freeze" at such a site says little
about *unburied* genetic hardiness. **Mitigation:** a first-class `burial_flag` region
field; down-weight or exclude buried-region presence from the survival signal.

### 3. Narrow intrinsic vinifera hardiness range
Midwinter bud LT50 across *V. vinifera* clusters tightly (~ −18 to −25 °C). Truly
"cold-hardy" material is mostly interspecific hybrids, excluded here. Method noise
(DTA/LTE vs electrolyte leakage vs tetrazolium; tissue; acclimation date) can exceed
between-variety differences; with ~23 genotypes in the good WSU dataset the among-variety
variance may be smaller than the noise. **Mitigation:** lead with this caveat; prefer the
mechanistic WSU dynamic model; treat the survival association as soft validation only.

### 4. No external validation target
With no vine-level ground truth, cross-validation tests *internal consistency*, not
*correctness*. **Mitigation:** frame the deliverable explicitly as decision support /
hypothesis generation, not validated prediction, in both README and output.

### 5. ERA5 sub-grid
Frost pockets and cold-air drainage — the actual kill mechanism — are sub-grid at
9–25 km. Site minima are biased regional proxies. The 1956/1985/1987 anchors are good
calibration events but their minima are not site truth.

### 6. "Ripe to target style" is subjective and survivorship-biased
GDD_req anchored from DOC/DOCG/AVA sites that *succeed* self-selects for success. Define
"ripe to target style" operationally (e.g., Brix/TA targets by style) before anchoring,
and rely on the σ sensitivity analysis — σ drives the ripening CDF.

### 7. Pedigree A-matrix from admixed, patchy records
Wikidata/VIVC parentage is incomplete and error-prone; the A-matrix will have heavy
missingness. Marker-based NJ/UPGMA (Myles/Laucou) is preferable where the genotype matrix
is obtainable because it does not depend on correct recorded parentage. Expect a modest
ancestry signal regardless.

## Recommendations

- Prefer a **single Bayesian hierarchical model** over chained imputations so uncertainty
  is coherent end-to-end and Stage 2/4 circularity is structurally avoided.
- When mechanistic LT50 and observational survival disagree, **trust LT50**; use survival
  as soft validation.
- Add the **`burial_flag`** as a first-class data field.
- State explicitly that this is **decision support, not validated prediction**.
- Respect FPS/VIVC terms; rate-limit scraping; **cite** Anderson rather than redistributing
  raw Excel.
