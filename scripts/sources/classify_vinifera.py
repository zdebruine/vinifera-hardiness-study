#!/usr/bin/env python3
"""Classify scraped FPS varieties as true Vitis vinifera vs. hybrid/rootstock/other.

We KEEP only pure V. vinifera and EXCLUDE interspecific hybrids (including vinifera x
hybrid crosses), American species, muscadines, and rootstocks. Anything the rules can't
decide is kept but flagged needs_review=1 so it gets a second look (VIVC/Wikipedia) rather
than guessed.

Inputs : data/interim/fps_catalog_raw.csv (from scrape_fps.py)
Outputs: data/db/varieties.csv          -- accepted vinifera (+ flagged unresolved)
         data/interim/fps_classified.csv -- full audit incl. excluded rows + reason

``classify`` is pure and unit-tested; the driver only does IO.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "interim" / "fps_catalog_raw.csv"
VARIETIES = ROOT / "data" / "db" / "varieties.csv"
AUDIT = ROOT / "data" / "interim" / "fps_classified.csv"

NON_VINIFERA_SPECIES = re.compile(
    r"\bvitis\s+(labrusca|riparia|rupestris|aestivalis|berlandieri|rotundifolia|cinerea|"
    r"champinii|amurensis|mustangensis|x\b)", re.I)


def _norm(name: str) -> str:
    s = re.sub(r"[^a-z0-9 ]+", " ", name.lower())
    return re.sub(r"\s+", " ", s).strip()


KNOWN_NON_VINIFERA = {_norm(n) for n in [
    # American species / labrusca table & juice
    "Concord", "Niagara", "Catawba", "Delaware", "Isabella", "Ives", "Norton", "Cynthiana",
    "Diamond", "Steuben", "Fredonia", "Worden",
    # muscadines (V. rotundifolia)
    "Carlos", "Noble", "Magnolia", "Scuppernong", "Tara", "Doreen",
    # French-American & modern interspecific hybrids
    "Baco noir", "Baco blanc", "Chambourcin", "Seyval blanc", "Vidal blanc", "Vignoles",
    "Marechal Foch", "Leon Millot", "Chancellor", "Chelois", "De Chaunac", "Villard blanc",
    "Villard noir", "Rougeon", "Aurore", "Cascade", "Colobel", "Rayon d'Or", "Verdelet",
    "Frontenac", "Frontenac gris", "Frontenac blanc", "Marquette", "La Crescent", "Itasca",
    "Petite Pearl", "St. Croix", "Sabrevois", "Prairie Star", "Louise Swenson", "Edelweiss",
    "Brianna", "St. Pepin", "Swenson Red", "Petite Amie", "Crimson Pearl", "Verona",
    "Traminette", "Cayuga White", "Noiret", "Corot noir", "Valvin Muscat", "Aromella",
    "Geneva Red", "GR7", "Melody", "Horizon", "Chardonel", "Vincent",
    "Black Spanish", "Lenoir", "Blanc du Bois", "Roucaneuf", "Vidal",
    # common rootstocks (non-vinifera / hybrid)
    "Freedom", "Harmony", "Salt Creek", "Ramsey", "Dog Ridge", "St. George",
]}


def slugify(name: str) -> str:
    s = _norm(name).replace(" ", "-")
    return re.sub(r"-+", "-", s).strip("-")


def classify(name: str, species_text: str = "", is_hybrid_text: str = "0",
             is_rootstock_text: str = "0") -> tuple[int, str, int]:
    """Return (is_vinifera 0/1, classification, needs_review 0/1).

    classification in {vinifera, rootstock, hybrid_or_nonvinifera, unverified}.
    """
    n = _norm(name)
    st = species_text.lower()

    if is_rootstock_text == "1":
        return 0, "rootstock", 0
    if n in KNOWN_NON_VINIFERA:
        return 0, "hybrid_or_nonvinifera", 0
    if NON_VINIFERA_SPECIES.search(st) or is_hybrid_text == "1":
        return 0, "hybrid_or_nonvinifera", 0
    if "vinifera" in st:
        return 1, "vinifera", 0
    # No decisive signal -> keep but flag for a second-source lookup.
    return 1, "unverified", 1


def main() -> int:
    if not RAW.exists():
        print("data/interim/fps_catalog_raw.csv not found -- run scrape_fps.py first "
              "(on open-network CI).", file=sys.stderr)
        return 1
    with RAW.open(newline="", encoding="utf-8") as fh:
        raw = list(csv.DictReader(fh))

    audit, accepted, seen = [], [], {}
    for r in raw:
        is_vin, cls, review = classify(r["name"], r.get("species_text", ""),
                                       r.get("is_hybrid_text", "0"), r.get("is_rootstock_text", "0"))
        slug = slugify(r["name"])
        while slug in seen and seen[slug] != r["fps_variety_id"]:
            slug = f"{slug}-{r['fps_variety_id']}"
        seen[slug] = r["fps_variety_id"]
        audit.append({**r, "variety_id": slug, "is_vinifera": is_vin,
                      "classification": cls, "needs_review": review})
        if is_vin == 1:
            accepted.append({
                "variety_id": slug, "prime_name": r["name"], "color": "", "species": "Vitis vinifera",
                "origin_country": "", "is_vinifera": "1", "classification": cls,
                "fps_variety_id": r["fps_variety_id"], "vivc_number": "",
                "needs_review": str(review), "source": "fps_scrape_v1", "notes": "",
            })

    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(raw[0].keys()) +
                           ["variety_id", "is_vinifera", "classification", "needs_review"])
        w.writeheader(); w.writerows(audit)
    with VARIETIES.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["variety_id", "prime_name", "color", "species",
            "origin_country", "is_vinifera", "classification", "fps_variety_id",
            "vivc_number", "needs_review", "source", "notes"])
        w.writeheader(); w.writerows(accepted)

    n_excl = sum(1 for a in audit if a["is_vinifera"] == 0)
    n_review = sum(1 for a in accepted if a["needs_review"] == "1")
    print(f"Classified {len(audit)} varieties: {len(accepted)} vinifera kept "
          f"({n_review} need review), {n_excl} excluded (hybrid/rootstock/other).")
    print(f"  -> data/db/varieties.csv, audit in data/interim/fps_classified.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
