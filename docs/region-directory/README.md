# World wine region directory — working context

A documented, search-built directory of the world's wine regions, drilled toward the
**lowest classified level** in each country, plus the climate signal we need per region.
Built LLM-first with web search (no scraping in this environment). Bulk leaf-level
enumeration that needs page retrieval is handled later on a local Claude Code instance.

## Why this exists

The study attaches **climate** and **variety presence** to wine regions. To do that well
we must operate at the **finest official granularity** — a single Burgundy *climat* or a
German *Einzellage*, not a country-sized blob — because climate (and the survival/ripening
signal) varies enormously inside a broad region. This directory is the scaffold that lets
us (a) know what the leaf level *is* in each country, (b) know where the authoritative and
geospatial lists live, and (c) enumerate toward an exhaustive set.

## What's here

| File | Purpose |
|---|---|
| [`classification-systems.md`](classification-systems.md) | Per-country appellation hierarchies, the **leaf (lowest) level** and its approx count, and how to search toward an exhaustive list. The core reference. |
| [`data-sources.md`](data-sources.md) | Authoritative registers + **open geospatial datasets** (boundaries/coordinates) per country/region. What each provides and its license. |
| [`climatic-extremes.md`](climatic-extremes.md) | Method for characterizing within-region climate variation and selecting **extreme-representative vineyards/estates with coordinates**. |

## What search can and can't do here (learned)

- **Search is excellent for:** the *structure* (tiers, the name of the leaf level), current
  *counts*, and *authoritative source URLs*. These are verifiable and citable.
- **Search is unreliable for:** exhaustively *enumerating* thousands of leaf regions by name
  (e.g. all 1,247 Burgundy climats, ~2,600 German Einzellagen, Georgia's 29–30 PDOs). Snippets
  are lossy; doing this by hand risks fabrication. → That enumeration is deferred to the
  page-retrieval/scraping phase, pointed at the registers catalogued in `data-sources.md`.

## Status

Iteration 1: classification reference + data-source catalog + climate-extreme method drafted
and grounded in cited searches. Named leaf-level enumeration is intentionally **not** filled
in by hand; it will be ingested from the authoritative/geospatial sources.
