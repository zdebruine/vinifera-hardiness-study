# Worked climate-extreme anchors (flagship regions)

Applying the method in `climatic-extremes.md`: for each flagship region, 2 anchors chosen to
**bracket the dominant within-region climate gradient**, as real localities/sub-zones with
coordinates. These are the template for the `wineries` table (one row per anchor) and the
points the weather step (deferred) will sample.

**Coordinate honesty:** these are **representative localities / sub-zones** (real places),
`coord_precision = approx`; swap in specific estate coordinates (Wikidata/OSM/GeoNames) in
the retrieval phase. Elevations are approximate. Valley-floor anchors are *regional proxies*
for frost/winter-cold (ERA5 is sub-grid).

| region | anchor (locality) | gradient / role | lat | lon | elev_m | note |
|---|---|---|---|---|---|---|
| Mosel (DE) | Bernkastel (Doctor) | warm — steep slate sun-trap | 49.92 | 7.07 | 120 | river-warmed S-facing |
| Mosel (DE) | Upper Saar (Wiltingen/Saarburg) | cool — frost-prone tributary | 49.60 | 6.55 | 210 | latest-ripening, frost risk |
| Wachau (AT) | Loiben/Dürnstein river terrace | warm — Smaragd zone | 48.39 | 15.52 | 220 | Danube-warmed low terrace |
| Wachau (AT) | Spitz (Tausendeimerberg) high terrace | cool — high altitude | 48.37 | 15.41 | 450 | cooler upper terraces |
| Barolo (IT) | La Morra (Brunate) | cooler/earlier — west, higher | 44.64 | 7.92 | 400 | Tortonian soils, perfumed |
| Barolo (IT) | Serralunga d'Alba | warm mesoclimate — latest-ripening | 44.62 | 7.99 | 420 | Helvetian soils, structured |
| Etna (IT) | Biancavilla/Belpasso (SW base) | warm — lower south slope | 37.62 | 14.97 | 600 | warmest, earliest |
| Etna (IT) | Solicchiata/Rovittello (N high) | cool — high-elevation N | 37.83 | 15.02 | 1000 | high contrade, late |
| Côte de Nuits (FR) | Vosne-Romanée mid-slope | prime — valley/mid-slope | 47.16 | 4.96 | 260 | classic east-facing |
| Côte de Nuits (FR) | Hautes-Côtes de Nuits (above) | cool — high benchland | 47.15 | 4.85 | 400 | cooler, later |
| Rioja (ES) | Rioja Alta (Haro) | cool — Atlantic, higher W | 42.58 | -2.85 | 480 | fresher, higher acidity |
| Rioja (ES) | Rioja Oriental (Alfaro) | warm — Mediterranean, lower E | 42.18 | -1.75 | 300 | riper, earlier |
| Douro (PT) | Baixo Corgo (Peso da Régua) | cool — wetter west | 41.16 | -7.79 | 150 | most rainfall, freshest |
| Douro (PT) | Douro Superior (V.N. de Foz Côa) | hot/dry — east | 41.08 | -7.14 | 150 | extreme heat, aridity |
| Kakheti (GE) | Alazani valley floor (Telavi) | warm — valley floor | 41.92 | 45.47 | 500 | warm, frost-pool risk |
| Kakheti (GE) | Caucasus foothills (Kvareli high) | cool — higher slopes | 41.95 | 45.81 | 800 | cooler, later |
| Vayots Dzor (AM) | Areni village | warm-for-altitude | 39.72 | 45.19 | 1000 | valley sites |
| Vayots Dzor (AM) | Upper Vayots Dzor (high plots) | extreme altitude — cool | 39.75 | 45.30 | 1400 | very high vineyards |

## How these feed the model
Each row → a `wineries` anchor (`winery_id, region_id, name, role, latitude, longitude,
elevation_m, coord_precision='approx', notes`). Two anchors per region give a GDD range +
coldest-winter-minimum spread → the region's `variation_score` once weather is pulled. The
existing curated `data/db/wineries.csv` already follows this pattern for Bordeaux, Etna,
Kakheti, Rioja, Douro, Wachau, etc.; this table extends it toward flagship **leaf** regions.

## Next (retrieval phase)
- Replace locality centroids with specific estate/vineyard coordinates (Wikidata/OSM).
- Where a polygon exists (US AVAs, EU PDO geo-inventory), derive min/max-elevation sample
  points from a DEM instead of prose-chosen localities — more objective.
