# Documented region directory

Per-country enumeration of wine regions at the **mid tier** (the appellations/districts
just above the leaf), built LLM-first from cited web searches. Each file gives a one-line
classification recap, the **leaf level** to drill to next, the enumerated mid-tier table
(`name | parent | level | note | source`), and sources.

The **leaf level** itself (individual climats, Einzellagen, MGAs, Riede, Viñedos Singulares,
nested AVAs) is intentionally **not** hand-enumerated — that's the page-retrieval/local
phase (see `../classification-systems.md` and `../data-sources.md`).

## Files

| File | Coverage | Status |
|---|---|---|
| [`france.md`](france.md) | France — all major regions, ~110 communal/district/cru AOCs | done |
| [`italy.md`](italy.md) | Italy — 20 regions, principal DOCG/DOC | done |
| [`spain-portugal.md`](spain-portugal.md) | Spain (~45 DO/DOCa) + Portugal (DOCs + sub-regions) | done |
| [`germany-austria.md`](germany-austria.md) | Germany (13 Anbaugebiete + Bereiche) + Austria (18 DACs) | done |
| [`central-eastern-europe.md`](central-eastern-europe.md) | Hungary, Greece, Switzerland, Slovenia, Croatia, Romania, Bulgaria, Moldova | done |
| [`caucasus-south-america.md`](caucasus-south-america.md) | Georgia, Armenia, Azerbaijan; Argentina, Chile | done |

## Leaf level by country (drill target)

| Country | Leaf level | Mid tier enumerated here |
|---|---|---|
| France | climat / lieu-dit / named Grand Cru | communal & district AOCs, crus |
| Italy | MGA / UGA (vineyard mention) | DOCG/DOC |
| Spain | Viñedo Singular / Vino de Pago | DO / DOCa, zones |
| Portugal | DOC sub-region | DOCs + sub-regions |
| Germany | Einzellage (~2,600) | Anbaugebiet → Bereich |
| Austria | Ried (+ Erste/Große Lage) | DAC |
| Hungary | Tokaj dűlők etc. | wine regions |
| Georgia | PDO microzone | PDO appellations (≈leaf) |
| USA | innermost nested AVA | (see classification-systems) |

> Counts drift year to year; tables capture principal appellations, not every minor one.
> Entries marked "(unverified)" need confirmation in the retrieval phase.
