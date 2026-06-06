# Region data sources — registers & geospatial boundaries

Where to get (a) the **names/hierarchy** of regions and (b) their **boundaries/coordinates**.
Boundaries matter twice: they define the leaf regions *and* they give us the geometry to
place climate-extreme sample points (see `climatic-extremes.md`). Most of these need page
retrieval/download → use them in the local Claude Code phase; this is the catalog for it.

## Cross-country / EU

| Source | Provides | Format | License | URL |
|---|---|---|---|---|
| **eAmbrosia** (EU GI register) | Every EU wine PDO/PGI name + legal spec | web register; bulk export on data.europa.eu | EU open data | <https://ec.europa.eu/agriculture/eambrosia/geographical-indications-register/> · dataset: <https://data.europa.eu/data/datasets/eambrosia-eu-geographical-indications-register> |
| **Geospatial inventory of EU wine PDOs** (PMC paper + dataset) | Regulatory + geospatial info for European wine PDOs | dataset accompanying paper | per paper | <https://pmc.ncbi.nlm.nih.gov/articles/PMC9276794/> |
| Wikidata (SPARQL) | Appellations with parent/coords; good for hierarchy | JSON/SPARQL | CC0 | <https://query.wikidata.org/> |

## United States — best-in-class open boundaries

| Source | Provides | Format | License | URL |
|---|---|---|---|---|
| **UC Davis AVA Digitizing Project** | **All AVA boundaries** ever defined (current + historical), per state | GeoJSON + Shapefile | **CC0** | <https://github.com/UCDavisLibrary/ava> · data: <https://ucdavislibrary.github.io/ava/data.html> |
| **TTB AVA Map Explorer** | Official AVA boundaries + nesting (contains/within) | Shapefiles | US gov | <https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/ava-map-explorer> |

`avas_allboundaries.geojson` from the UC Davis repo is the single most useful file for the
US: it *is* the AVA list with geometry and nesting, so leaf AVAs + coordinates come for free.

## National registers (names + specs; geometry varies)

| Country | Body | URL |
|---|---|---|
| France | INAO (cahiers des charges) | <https://www.inao.gouv.fr/> |
| France/Burgundy | BIVB climats & lieux-dits | <https://www.bourgogne-wines.com/> |
| Italy | MASAF disciplinari; regional consorzi (MGA/UGA maps) | (per appellation) |
| Germany | Weinbauverbände; VDP site classification | <https://www.vdp.de/> |
| Spain | DO Consejos Reguladores; MAPA | <https://www.mapa.gob.es/> |
| Portugal | IVV | <https://www.ivv.gov.pt/> |
| Austria | Österreich Wein; Riedenkataster | <https://www.austrianwine.com/> |
| Georgia | National Wine Agency (PDO register) | <https://wine.gov.ge/En/Wine> |
| Australia | Wine Australia GI register | <https://www.wineaustralia.com/labelling/register-of-protected-gis-and-other-terms/> |
| New Zealand | NZ Wine / IPONZ GIs | <https://www.nzwine.com/en/regions/> |
| South Africa | WOSA / SAWIS (WO scheme) | <https://www.wosa.co.za/> |

## Coordinates for sample points (when boundaries aren't available)

When we only have a region name (no polygon), we still need points to sample climate at its
extremes (`climatic-extremes.md`). Useful for geocoding named places/estates/villages:

| Source | Provides | License | URL |
|---|---|---|---|
| Wikidata / Wikipedia | coords (P625) for appellations, communes, many estates | CC0 / CC BY-SA | <https://www.wikidata.org/> |
| OpenStreetMap / Nominatim | geocode villages, named vineyards, estates | ODbL | <https://nominatim.openstreetmap.org/> |
| GeoNames | populated-place coords + elevation | CC BY | <https://www.geonames.org/> |

## Notes on use

- Prefer **boundaries (polygons)** where they exist (US AVAs, EU PDO geo-inventory): they
  define the leaf set *and* let us derive min/max-elevation or coolest/warmest sample points
  inside each region.
- Where only **names** exist, descend the national register to the leaf, then **geocode**
  representative localities/estates for the climate-extreme points.
- Record every retrieval (URL + date + license) in `data/PROVENANCE.md`, per repo policy.
