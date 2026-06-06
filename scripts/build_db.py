#!/usr/bin/env python3
"""Compile the data/db CSVs into a relational SQLite database.

Loads varieties, regions, wineries, variety_region, and synonyms; enforces referential
integrity and id uniqueness; creates convenience views joining the two anchor tables; and
writes data/processed/vinifera.db. Stdlib only.

Exit non-zero on any integrity violation so CI fails loudly.
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
    in_fps INTEGER, fps_status TEXT, notes TEXT
);
CREATE TABLE regions (
    region_id TEXT PRIMARY KEY,
    name TEXT NOT NULL, country TEXT, macro_region TEXT,
    latitude REAL, longitude REAL, notes TEXT
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
           r.macro_region, r.country, vr.role, vr.evidence
    FROM variety_region vr
    JOIN varieties v ON v.variety_id = vr.variety_id
    JOIN regions r   ON r.region_id  = vr.region_id;
CREATE VIEW region_anchor_counts AS
    SELECT r.region_id, r.name, COUNT(w.winery_id) AS n_anchors
    FROM regions r LEFT JOIN wineries w ON w.region_id = r.region_id
    GROUP BY r.region_id, r.name;
"""

# table -> (csv file, columns, integer columns, real columns)
TABLES = {
    "varieties": ("varieties.csv", ["variety_id", "prime_name", "color", "species",
                  "origin_country", "in_fps", "fps_status", "notes"], {"in_fps"}, set()),
    "regions": ("regions.csv", ["region_id", "name", "country", "macro_region",
                "latitude", "longitude", "notes"], set(), {"latitude", "longitude"}),
    "wineries": ("wineries.csv", ["winery_id", "region_id", "name", "role", "latitude",
                 "longitude", "elevation_m", "coord_precision", "notes"], set(),
                 {"latitude", "longitude", "elevation_m"}),
    "variety_region": ("variety_region.csv", ["region_id", "variety_id", "role",
                       "evidence", "bearing_ha", "source"], set(), {"bearing_ha"}),
    "synonyms": ("synonyms.csv", ["variety_id", "synonym", "context"], set(), set()),
}


def coerce(value: str, col: str, ints: set, reals: set):
    if value == "" and (col in ints or col in reals):
        return None
    if col in ints:
        return int(value)
    if col in reals:
        return float(value)
    return value


def load_table(conn, table, spec):
    fname, cols, ints, reals = spec
    rows = []
    with (DB_DIR / fname).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(tuple(coerce(r[c], c, ints, reals) for c in cols))
    placeholders = ", ".join("?" * len(cols))
    conn.executemany(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})", rows)
    return len(rows)


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    conn = sqlite3.connect(OUT)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)

    counts = {}
    try:
        # load parents before children (varieties, regions first)
        for table in ["varieties", "regions", "wineries", "variety_region", "synonyms"]:
            counts[table] = load_table(conn, table, TABLES[table])
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"INTEGRITY ERROR while loading: {e}", file=sys.stderr)
        return 1

    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        print("FOREIGN KEY violations:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print("Built data/processed/vinifera.db")
    for t, n in counts.items():
        print(f"  {t:16} {n} rows")
    regions_with = conn.execute(
        "SELECT COUNT(*) FROM region_anchor_counts WHERE n_anchors > 0").fetchone()[0]
    total_regions = conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0]
    fps_unverified = conn.execute(
        "SELECT COUNT(*) FROM varieties WHERE fps_status = 'unverified'").fetchone()[0]
    print(f"  regions with >=1 climate anchor: {regions_with}/{total_regions}")
    print(f"  varieties needing FPS verification: {fps_unverified}")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
