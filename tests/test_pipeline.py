"""Tests for the data-model build and the network-free parts of the sourcing pipeline."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "sources"))

from vinifera import climate_score as cs  # noqa: E402


# ---- climate scoring -------------------------------------------------------
def test_daily_gdd_floors_at_zero():
    assert cs.daily_gdd_f(30, 40) == 0.0          # avg 35F < 50F base
    assert cs.daily_gdd_f(50, 70) == 10.0         # avg 60F -> 10 GDD


def test_region_variation_score_rises_with_spread():
    tight = [cs.AnchorClimate("a", "r", 2500, -20, -15),
             cs.AnchorClimate("b", "r", 2550, -21, -15)]
    wide = [cs.AnchorClimate("a", "r", 2000, -25, -20),
            cs.AnchorClimate("b", "r", 3200, -15, -8)]
    assert cs.region_climate(wide).variation_score > cs.region_climate(tight).variation_score
    rc = cs.region_climate(wide)
    assert rc.gdd_spread_f == 1200
    assert rc.coldest_winter_min_c == -25


# ---- weather feature extraction (pure) -------------------------------------
def test_features_from_daily():
    import fetch_weather as fw
    # two years, one warm summer day and one cold winter day each
    dates = ["2019-07-15", "2019-01-10", "2020-07-15", "2020-01-10"]
    tmin = [15.0, -12.0, 16.0, -18.0]
    tmax = [30.0, -2.0, 31.0, -5.0]
    f = fw.features_from_daily(dates, tmin, tmax, southern=False)
    assert f["n_years"] == 2
    assert f["coldest_winter_min_c"] == -18.0      # worst over all days
    assert f["mean_annual_min_c"] == -15.0         # mean of -12 and -18
    assert f["mean_season_gdd_f"] > 0              # July days contribute GDD


def test_features_skips_missing():
    import fetch_weather as fw
    f = fw.features_from_daily(["2019-07-15", "2019-07-16"], [None, 15.0], [None, 30.0], southern=False)
    assert f["n_years"] == 1


# ---- FPS reconciliation (pure) ---------------------------------------------
def test_normalize_strips_accents_and_punctuation():
    import fetch_fps_catalog as fps
    assert fps.normalize("Gewürztraminer") == "gewurztraminer"
    assert fps.normalize("Saint-Laurent") == "saint laurent"


def test_reconcile_marks_listed_absent_and_reports_unmatched():
    import fetch_fps_catalog as fps
    varieties = [
        {"variety_id": "riesling", "prime_name": "Riesling", "in_fps": "", "fps_status": "unverified"},
        {"variety_id": "grenache-noir", "prime_name": "Grenache noir", "in_fps": "", "fps_status": "unverified"},
        {"variety_id": "areni-noir", "prime_name": "Areni noir", "in_fps": "", "fps_status": "unverified"},
    ]
    synonyms = {"grenache-noir": ["Garnacha"]}
    catalog = {"Riesling", "Garnacha", "Some Other Selection"}
    rows, unmatched = fps.reconcile(catalog, varieties, synonyms)
    by_id = {r["variety_id"]: r for r in rows}
    assert by_id["riesling"]["fps_status"] == "listed"
    assert by_id["grenache-noir"]["fps_status"] == "listed"   # matched via synonym
    assert by_id["areni-noir"]["fps_status"] == "absent"
    assert "Some Other Selection" in unmatched


# ---- relational build ------------------------------------------------------
def test_build_db_passes_integrity():
    import build_db
    assert build_db.main() == 0
