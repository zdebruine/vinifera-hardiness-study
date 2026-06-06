"""Tests for the network-free logic in the scrapers/classifiers."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "sources"))


# ---- vinifera classification ----------------------------------------------
def test_classify_excludes_rootstock_and_known_hybrids():
    import classify_vinifera as cv
    assert cv.classify("Freedom", is_rootstock_text="1") == (0, "rootstock", 0)
    assert cv.classify("Concord")[0] == 0                     # known American/labrusca
    assert cv.classify("Chambourcin")[1] == "hybrid_or_nonvinifera"


def test_classify_species_text_signals():
    import classify_vinifera as cv
    assert cv.classify("Some Grape", species_text="Vitis labrusca")[0] == 0
    assert cv.classify("Some Grape", is_hybrid_text="1")[0] == 0
    assert cv.classify("Riesling", species_text="Vitis vinifera") == (1, "vinifera", 0)


def test_classify_unknown_is_kept_but_flagged():
    import classify_vinifera as cv
    is_vin, cls, review = cv.classify("Obscure Selection")
    assert (is_vin, cls, review) == (1, "unverified", 1)


def test_slugify():
    import classify_vinifera as cv
    assert cv.slugify("Cabernet Sauvignon") == "cabernet-sauvignon"
    assert cv.slugify("Müller-Thurgau") == "m-ller-thurgau" or cv.slugify("Muller-Thurgau") == "muller-thurgau"


# ---- Wikidata region parsing + leaf computation ----------------------------
def _payload():
    def b(qid, label, parent=None, coord=None, country=None):
        d = {"region": {"value": f"http://www.wikidata.org/entity/{qid}"},
             "regionLabel": {"value": label}}
        if parent:
            d["parent"] = {"value": f"http://www.wikidata.org/entity/{parent}"}
        if coord:
            d["coord"] = {"value": coord}
        if country:
            d["countryLabel"] = {"value": country}
        return d
    return {"results": {"bindings": [
        b("Q1", "Burgundy", coord="Point(4.8 47.0)", country="France"),
        b("Q2", "Cote de Nuits", parent="Q1"),
        b("Q3", "Gevrey-Chambertin", parent="Q2", coord="Point(4.97 47.23)"),
    ]}}


def test_parse_bindings_extracts_coords_and_parents():
    import scrape_regions_wikidata as w
    rows = w.parse_bindings(_payload())
    by = {r["region_id"]: r for r in rows}
    assert by["Q1"]["latitude"] == "47.0" and by["Q1"]["longitude"] == "4.8"
    assert by["Q2"]["parent_id"] == "Q1"
    assert by["Q3"]["name"] == "Gevrey-Chambertin"


def test_compute_leaves_marks_lowest_level():
    import scrape_regions_wikidata as w
    rows = w.parse_bindings(_payload())
    w.compute_leaves(rows)
    by = {r["region_id"]: r for r in rows}
    assert by["Q1"]["is_leaf"] == "0"   # parent of Q2
    assert by["Q2"]["is_leaf"] == "0"   # parent of Q3
    assert by["Q3"]["is_leaf"] == "1"   # lowest level
