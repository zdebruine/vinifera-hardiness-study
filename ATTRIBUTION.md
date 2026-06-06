# Attribution & data licenses

This project's **code** is MIT-licensed (`LICENSE`). Each external **data source** retains
its own license and must be cited. No raw third-party dataset is redistributed in this repo;
provenance (URL + retrieval date) is recorded in `data/PROVENANCE.md`.

| Source | Use | License / terms | Citation |
|---|---|---|---|
| Open-Meteo Historical (ERA5 / ERA5-Land) | Climate: GDD, winter minima, freeze events | CC BY 4.0 | Zippenfenig, P. (2023). Open-Meteo.com Weather API. <https://open-meteo.com/> · ERA5: Hersbach et al. (2020), Copernicus Climate Change Service. |
| UC Davis FPS / National Grape Registry | Variety universe (~584) | UC Regents — cite, respect terms of use; rate-limit scraping | Foundation Plant Services, UC Davis. <https://ngr.ucdavis.edu/> |
| Anderson & Nelgen, *Which Winegrape Varieties are Grown Where?* | Variety × region colocation + ha weights, synonyms | Free ebook/data — cite, do not redistribute raw | Anderson, K. & Nelgen, S. (2020), Univ. of Adelaide Press. |
| Robinson, Harding & Vouillamoz, *Wine Grapes* | Synonym crosswalk | Copyrighted — cite, no redistribution | Robinson, Harding & Vouillamoz (2012), Allen Lane. |
| VIVC (Vitis International Variety Catalogue) | Prime names, pedigree | Cite; respect terms | JKI Geilweilerhof. <https://www.vivc.de/> |
| Wikidata / Wikipedia | Parentage crosswalk | CC0 (Wikidata) / CC BY-SA (Wikipedia) | <https://www.wikidata.org/> |
| Laucou et al. 2011 (SSR) | Genotype for marker tree | Cite | Laucou et al. (2011), *Theor. Appl. Genet.* |
| Myles et al. 2011 (SNP; GRIN/Dryad) | Genotype for marker tree | Cite | Myles et al. (2011), *PNAS* 108(9):3530–3535. |
| Ferguson et al. (WSU dynamic cold-hardiness model) | LT50 by date, ~23 genotypes | Cite | Ferguson et al. (2014), *Am. J. Enol. Vitic.* |
| Chinese 124-cultivar vinifera LT50 study | LT50 meta-analysis | Cite (check access) | (fill in on retrieval) |
| Iranian 20-cultivar LT50 study | LT50 meta-analysis | Cite (check access) | (fill in on retrieval) |
| TAMU cold-hardiness class table | LT50 priors | Cite | Texas A&M AgriLife. |

> Per-source citations are completed as data is actually retrieved; update both this file
> and `data/PROVENANCE.md` at retrieval time.
