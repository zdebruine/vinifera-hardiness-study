# Wine classification systems — the leaf level by country

For each country: the appellation hierarchy from broadest tier to the **leaf (lowest
classified) level**, the approximate number of leaves, the authoritative source, and a
search strategy toward an exhaustive list. We always target the leaf level — never a broad
cluster when a finer official level exists. Counts/links were grounded via web search this
session (see Sources); exact totals drift, so treat them as current-ish, not frozen.

## The EU umbrella (most of our focus area)

Most European wine names are EU **PDO** (Protected Designation of Origin) or **PGI**
(Protected Geographical Indication), registered in **eAmbrosia**, the EU's legal register.
There were on the order of **~1,177 wine PDOs** in Europe (2021 figure). National systems
(AOC, DOC, DAC, etc.) map onto PDO/PGI but keep their own internal sub-tiers — and those
national sub-tiers are usually where the true leaf level lives (a climat, an Einzellage, a
Ried). So: use eAmbrosia for the PDO/PGI backbone, then go *inside* each PDO via the
national body for the leaves.

## France

- **Tiers:** Vin de France → IGP → **AOP/AOC**; and *within* AOC: Régional → Sub-regional →
  Village/Commune → Premier Cru → Grand Cru.
- **Leaf level:** the **climat / lieu-dit** (named vineyard parcel). Burgundy alone has
  **1,247 registered climats** (UNESCO, 2015), of which ~600 are Premier/Grand Cru and the
  rest village/regional; a climat is always a lieu-dit but not vice-versa.
- **Authoritative source:** INAO (Institut National de l'Origine et de la Qualité) — the
  cahiers des charges per AOC list the communes, and for Burgundy the climats; regional
  bodies (e.g. Bourgogne Wines) publish climat/lieu-dit lists.
- **Search strategy:** enumerate AOCs from INAO, then per AOC pull the commune list and (for
  cru-classified regions: Burgundy, Alsace Grands Crus, Champagne crus, etc.) the named
  vineyards. Bordeaux's leaf is effectively the commune/château; Burgundy's is the climat.

## Italy

- **Tiers:** Vino da Tavola → IGT → DOC → **DOCG**; with **sottozone** (sub-zones) inside
  many DOC/DOCG, and named single-vineyard areas below that.
- **Leaf level:** the **MGA / UGA** (*Menzione/Unità Geografica Aggiuntiva*, "additional
  geographical mention") — officially mapped vineyard areas named on the label, most
  developed in Piedmont (Barolo and Barbaresco have full MGA maps) and spreading to other
  appellations. Where no MGA exists, the leaf is the sottozona or the DOC/DOCG itself.
- **Counts:** ~**330 DOC**, ~**120 IGT**, plus several dozen **DOCG**.
- **Authoritative source:** Italian Ministry (MASAF) disciplinari di produzione per
  denomination; consorzi publish MGA/UGA lists.

## Germany

- **Tiers:** **Anbaugebiet** (13 regions) → **Bereich** (39 districts) → **Großlage**
  (collective site) → **Einzellage** (individual site).
- **Leaf level:** the **Einzellage** — **~2,600** registered individual vineyard sites
  (stable since the 1971 Wine Law). The 2021 wine-law reform adds a romance-style origin
  pyramid (Gebietswein → Ortswein → Einzellagenwein, phasing in through ~2026), and the VDP
  growers' association overlays its own Gutswein → Ortswein → Erste Lage → **Große Lage**
  classification.
- **Authoritative source:** German wine law / regional Weinbauverbände; VDP for the premium
  site classification.

## Spain

- **Tiers:** Vino de Mesa → Vino de Calidad (VC) → **DO** → **DOCa/DOQ**; plus **Vino de
  Pago** (single-estate PDO) as a parallel top tier.
- **Leaf level:** **Viñedo Singular** (single vineyard; e.g. Rioja) and **Vino de Pago**;
  intermediate locality tiers are **Vino de Zona** and **Vino de Pueblo/Municipio** (Rioja
  recognises **144 villages**).
- **Counts:** **69 DOs** (2024).
- **Authoritative source:** each DO's Consejo Regulador; Ministry (MAPA) for Pagos and the
  DO register.

## Portugal

- **Tiers:** Vinho Regional (VR, the PGI tier) and **DOC/DOP**; many DOCs carry **sub-regions**.
- **Leaf level:** the **DOC sub-region** (e.g. Douro → Baixo Corgo, Cima Corgo, Douro
  Superior). Single-vineyard naming is informal vs. France/Germany.
- **Authoritative source:** IVV (Instituto da Vinha e do Vinho) and regional CVRs.

## Austria

- **Tiers:** Wein → Landwein → Qualitätswein; origin profiled as **Gebietswein → Ortswein →
  Riedenwein** within the **DAC** system.
- **Leaf level:** the **Ried** (single vineyard). Since 2023 Austrian law allows an official
  single-vineyard hierarchy with optional **Erste Lage** and **Große Lage** tiers, phasing in
  across DACs.
- **Authoritative source:** Österreich Wein (austrianwine.com); the Riedenkataster vineyard
  register.

## Caucasus

- **Georgia:** **29–30 PDO** "microzones" (as of April 2025), **20 of them in Kakheti**;
  Kakheti further splits into **Shida (inner)** and **Gare (outer) Kakheti**. **Leaf = the
  PDO microzone** (e.g. Tsinandali, Mukuzani, Kindzmarauli, Napareuli, Khvanchkara, Tvishi).
  Authoritative source: **National Wine Agency (wine.gov.ge)**; Wikipedia "List of Georgian
  wine appellations" mirrors it. *(The full named list is not reliably enumerable from search
  snippets — pull it from the register in the retrieval phase.)*
- **Armenia:** **no formal appellation system yet**; wines are organised by **6 regions** —
  Aragatsotn, Tavush, Ararat, Vayots Dzor, Kotayk, Armavir (plus Yerevan). Leaf currently =
  region; watch for a forthcoming PDO scheme.
- **Azerbaijan:** no formal appellation system; organise by administrative wine districts
  (e.g. Ganja-Gazakh) until one exists.

## Other Europe (to verify/extend)

- **Hungary:** OEM (PDO)/OFJ (PGI); Tokaj has historically classified named **dűlők**
  (vineyards) — the leaf. *Counts to verify.*
- **Greece:** PDO (formerly OPAP) ~30+, with sub-zones (e.g. Mantinia, Nemea sub-zones).
  *To verify.*
- Also pending: Switzerland (communal/lieu-dit), Slovenia, Croatia, Romania, Bulgaria,
  Moldova, Austria's neighbours.

## New World (anchors / contrasts)

- **USA:** **AVA** (American Viticultural Area), **nested** — **279 AVAs** (2026; 154 in
  California). **Leaf = the innermost nested AVA** (e.g. within Napa: Oakville, Stags Leap
  District). Authoritative + geospatial source: **TTB** and the **UC Davis AVA** boundary
  dataset (see data-sources).
- **Australia:** **GI** hierarchy super-zone → state → **zone** (~28) → **region** (~65) →
  **sub-region** (only **14** legally defined). Leaf = sub-region where defined, else region.
  Source: Wine Australia GI register.
- **New Zealand:** **21 GIs**; 11 main regions subdivided into sub-regions. Leaf = sub-region
  GI (e.g. within Marlborough: Wairau, Awatere). Source: NZ Wine / IPONZ.
- **South Africa:** **WO** scheme: geographical unit → region → district → **ward**. **Leaf =
  ward** (e.g. Elgin). Source: WOSA / SAWIS.

## How to drive toward exhaustive leaf lists

1. **Backbone:** pull the PDO/PGI (EU) or GI/AVA/WO list per country from the authoritative
   register — this is bounded (tens–hundreds) and search-verifiable.
2. **Descend:** for each PDO/appellation, fetch its specification (cahier des charges /
   disciplinare / Riedenkataster / consorzio map) to get the leaf entities inside it.
3. **Geolocate:** attach coordinates/boundaries from the geospatial datasets in
   `data-sources.md` (these often *are* the leaf list, with geometry).
4. Steps 2–3 are page-retrieval-heavy → run them in the local Claude Code phase; this doc +
   `data-sources.md` are the map for that work.

## Sources

- eAmbrosia register: <https://ec.europa.eu/agriculture/eambrosia/geographical-indications-register/> ·
  GI overview: <https://agriculture.ec.europa.eu/farming/geographical-indications-and-quality-schemes/geographical-indications-and-quality-schemes-explained_en>
- France/Burgundy climats: <https://www.bourgogne-wines.com/wine-and-terroir/our-climats-and-lieux-dits/> ·
  classification overview: <https://winefolly.com/deep-dive/what-is-aoc-wine/>
- Italy: <https://www.wine-searcher.com/wine-label-italy> · <https://www.decanter.com/learn/italian-wine-labels-understanding-docg-doc-igt-439719/>
- Germany: <https://en.wikipedia.org/wiki/German_wine_classification> · <https://en.wikipedia.org/wiki/List_of_German_wine_regions>
- Spain: <https://www.winewithseth.com/winewiki/do-hierarchy-region-sub-region-zone-area-most-specific/> · <https://en.wikipedia.org/wiki/Spanish_wine_regions>
- Portugal: <https://en.wikipedia.org/wiki/List_of_Portuguese_wine_regions>
- Austria: <https://www.austrianwine.com/our-wine/strategy-for-origin-marketing/qualitaetswein-with-regional-typicity-dac> · <https://en.wikipedia.org/wiki/Districtus_Austriae_Controllatus>
- Georgia: <https://wine.gov.ge/En/Wine> · <https://en.wikipedia.org/wiki/List_of_Georgian_wine_appellations>
- Armenia: <https://en.wikipedia.org/wiki/Armenian_wine> · <https://www.wsetglobal.com/knowledge-centre/blog/2026/a-guide-to-armenian-wines>
- USA AVA: <https://en.wikipedia.org/wiki/List_of_American_Viticultural_Areas> · <https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/ava-map-explorer>
- Australia: <https://www.wineaustralia.com/labelling/register-of-protected-gis-and-other-terms/australian-wine-geographical-indications>
- New Zealand: <https://www.nzwine.com/en/regions/>
- South Africa: <https://www.wosa.co.za/The-Industry/Wines-Of-Origin/Wine-Of-Origin-Scheme/>
