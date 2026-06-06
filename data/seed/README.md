# Seed data — small illustrative sample

This directory holds a **small seeded sample** of every data type the full pipeline will
collect (see `../../docs/PLAN.md`). It exists so the website tools and the build pipeline
have something real to run against before the bulk pulls (Open-Meteo, Anderson, FPS, VIVC)
are wired up.

> **These are illustrative seed values, not the sourced dataset.** Variety names,
> synonyms, and parentage are real published facts. Climate figures, freeze minima, LT50
> values, ripening requirements, survival observations, and colocation hectares are
> **realistic ballparks for demonstration**, not retrieved measurements. Sources are
> tagged `*_illustrative`. Do not cite these numbers. Real pulls land in `data/raw/` with
> provenance recorded in `../PROVENANCE.md` and replace these seeds field by field.

## Files

| File | Stage | Contents |
|---|---|---|
| `varieties.csv` | universe | variety_id, prime name, color, species |
| `synonyms.csv` | crosswalk | variety_id, synonym |
| `pedigree.csv` | ancestry | variety_id, parent1_id, parent2_id |
| `sites.csv` | climate | site_id, coords, Winkler GDD (base 50F), burial_flag |
| `freeze_events.csv` | climate | canonical freeze events |
| `site_freeze_minima.csv` | climate | per-site event minimum temperature (degC) |
| `lt50.csv` | hardiness | midwinter bud LT50, method, tissue, sampling date, source |
| `ripening_req.csv` | ripening | GDD requirement (base 50F) + sigma to ripen to style |
| `colocation.csv` | graph | region x variety bearing hectares |
| `survival_obs.csv` | survival | noisy (variety, event) survival observations |

## Column notes

- `burial_flag = 1`: vines are buried/hilled over winter at this site, so survival
  presence there is largely uninformative about *unburied* genetic hardiness.
- `any_burial = 1` on a survival observation: the observation includes buried-region
  sites and should be treated as weak (note its wider `p_survived_sd`).
- LT50 is negative degrees Celsius; more negative = hardier.
- GDD is growing degree days, base 50 degF, Apr-Oct (Winkler).
