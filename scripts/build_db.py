#!/usr/bin/env python3
"""Compile the data/db CSVs into a relational SQLite database.

Anchor tables: varieties and regions (regions are hierarchical via parent_id; the lowest
level is is_leaf=1). Child tables (wineries, variety_region, synonyms) hang off them.

During the sourcing transition the scrapers regenerate varieties/regions with new ids, so
curated child rows can become orphaned. Such rows are SKIPPED with a warning (not a hard
failure); genuinely malformed data still exits non-zero. Stdlib only.
"""
from __future__ import annotations

import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "data" / "db"
OUT = ROOT / "data" / "processed" / "vinifera.db"

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE varieties (
    variety_id TEXT PRIMARY KEY,
    prime_name TEXT NOT NULL,
    color TEXT, species TEXT, origin_country TEXT,
    is_vinifera INTEGER, classification TEXT,
    fps_variety_id TEXT, vivc_number TEXT,
    needs_review INTEGER, source TEXT, notes TEXT
);
CREATE TABLE regions (
    region_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id TEXT REFERENCES regions(region_id),
    level TEXT, is_leaf INTEGER,
    country TEXT, macro_region TEXT,
    latitude REAL, longitude REAL,
    wikidata_id TEXT, source TEXT
);
CREATE TABLE wineries (
    winery_id TEXT PRIMARY KEY,
    region_id TEXT NOT NULL REFERENCES regions(region_id),
    name TEXT, role TEXT,
    latitude REAL, longitude REAL, elevation_m REAL,
    coord_precision TEXT, notes TEXT
);
CREATE TABLE variety_region (
    region_id TEXT NOT NULL REFERENCES regions(region_id),
    variety_id TEXT NOT NULL REFERENCES varieties(variety_id),
    role TEXT, evidence TEXT, bearing_ha REAL, source TEXT,
    PRIMARY KEY (region_id, variety_id)
);
CREATE TABLE synonyms (
    variety_id TEXT NOT NULL REFERENCES varieties(variety_id),
    synonym TEXT NOT NULL, context TEXT,
    PRIMARY KEY (variety_id, synonym)
);
CREATE VIEW variety_climate AS
    SELECT vr.variety_id, v.prime_name, vr.region_id, r.name AS region_name,
           r.macro_region, r.country, r.is_leaf, vr.role, vr.evidence
    FROM variety_region vr
    JOIN varieties v ON v.variety_id = vr.variety_id
    JOIN regions r   ON r.region_id  = vr.region_id;
CREATE VIEW leaf_regions AS
    SELECT * FROM regions WHERE is_leaf = 1;
"""

# table -> (csv, columns, int cols, real cols, nullable-fk text cols -> '' becomes NULL)
TABLES = {
    "varieties": ("varieties.csv",
        ["variety_id", "prime_name", "color", "species", "origin_country", "is_vinifera",
         "classification", "fps_variety_id", "vivc_number", "needs_review", "source", "notes"],
        {"is_vinifera", "needs_review"}, set(), set()),
    "regions": ("regions.csv",
        ["region_id", "name", "parent_id", "level", "is_leaf", "country", "macro_region",
         "latitude", "longitude", "wikidata_id", "source"],
        {"is_leaf"}, {"latitude", "longitude"}, {"parent_id"}),
    "wineries": ("wineries.csv",
        ["winery_id", "region_id", "name", "role", "latitude", "longitude", "elevation_m",
         "coord_precision", "notes"], set(), {"latitude", "longitude", "elevation_m"}, set()),
    "variety_region": ("variety_region.csv",
        ["region_id", "variety_id", "role", "evidence", "bearing_ha", "source"],
        set(), {"bearing_ha"}, set()),
    "synonyms": ("synonyms.csv", ["variety_id", "synonym", "context"], set(), set(), set()),
}

# child table -> list of (fk column, parent table) for orphan filtering
FKS = {
    "wineries": [("region_id", "regions")],
    "variety_region": [("region_id", "regions"), ("variety_id", "varieties")],
    "synonyms": [("variety_id", "varieties")],
}


def coerce(value, col, ints, reals, nullable):
    if value == "" and (col in ints or col in reals or col in nullable):
        return None
    if col in ints:
        return int(value)
    if col in reals:
        return float(value)
    return value


def read_rows(spec):
    fname, cols, ints, reals, nullable = spec
    path = DB_DIR / fname
    if not path.exists():
        return cols, []
    with path.open(newline="", encoding="utf-8") as fh:
        rows = [tuple(coerce(r[c], c, ints, reals, nullable) for c in cols)
                for r in csv.DictReader(fh)]
    return cols, rows


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    conn = sqlite3.connect(OUT)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)

    counts, skipped = {}, {}
    # parents first so we can filter orphaned children
    present_ids = {"varieties": set(), "regions": set()}
    for table in ["varieties", "regions", "wineries", "variety_region", "synonyms"]:
        cols, rows = read_rows(TABLES[table])
        if table in FKS:
            valid, dropped = [], 0
            for row in rows:
                rowd = dict(zip(cols, row))
                if all(rowd[fk] in present_ids[parent] for fk, parent in FKS[table]):
                    valid.append(row)
                else:
                    dropped += 1
            rows, skipped[table] = valid, dropped
        placeholders = ", ".join("?" * len(cols))
        try:
            conn.executemany(
                f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})", rows)
        except sqlite3.IntegrityError as e:
            print(f"INTEGRITY ERROR loading {table}: {e}", file=sys.stderr)
            return 1
        counts[table] = len(rows)
        if table in present_ids:
            present_ids[table] = {r[0] for r in rows}
    conn.commit()

    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        print("FOREIGN KEY violations:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print("Built data/processed/vinifera.db")
    for t, n in counts.items():
        extra = f"  ({skipped[t]} orphans skipped)" if skipped.get(t) else ""
        print(f"  {t:16} {n} rows{extra}")
    leaves = conn.execute("SELECT COUNT(*) FROM regions WHERE is_leaf = 1").fetchone()[0]
    vinifera = conn.execute("SELECT COUNT(*) FROM varieties WHERE is_vinifera = 1").fetchone()[0]
    review = conn.execute("SELECT COUNT(*) FROM varieties WHERE needs_review = 1").fetchone()[0]
    print(f"  leaf (lowest-level) regions: {leaves}")
    print(f"  vinifera varieties: {vinifera}   needs_review: {review}")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
