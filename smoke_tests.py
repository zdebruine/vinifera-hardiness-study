#!/usr/bin/env python3
"""Fast smoke test of pipeline stage interfaces.

Verifies that every stage module imports and exposes its documented interface, that the
two closed-form pieces (ripening CDF, score combination) behave sanely, and that the
not-yet-implemented stages fail loudly rather than silently returning fake results.

Run: python smoke_tests.py   (exit 0 = ok)
"""
from __future__ import annotations

import sys

sys.path.insert(0, "src")

from vinifera import (  # noqa: E402
    ancestry, climate, graph_impute, lt50, ripening, score, survival,
)


def _expect_not_implemented(label: str, fn, *args, **kwargs) -> None:
    try:
        fn(*args, **kwargs)
    except NotImplementedError:
        return
    raise AssertionError(f"{label}: expected NotImplementedError (stub must fail loudly)")


def test_modules_import() -> None:
    for mod in (climate, survival, lt50, graph_impute, ancestry, ripening, score):
        assert mod is not None


def test_ripening_cdf_is_monotone_and_centered() -> None:
    req = ripening.RipeningRequirement(variety_id="v", gdd_req_f=3000.0, sigma_f=300.0)
    at_req = ripening.p_ripen(3000.0, req)
    assert abs(at_req - 0.5) < 1e-9, "P(ripen) at GDD == GDD_req must be 0.5"
    assert ripening.p_ripen(2000.0, req) < at_req < ripening.p_ripen(4000.0, req)
    assert ripening.p_ripen(10000.0, req) > 0.999
    try:
        ripening.p_ripen(3000.0, ripening.RipeningRequirement("v", 3000.0, 0.0))
    except ValueError:
        pass
    else:
        raise AssertionError("sigma_f <= 0 must raise ValueError")


def test_score_combination_and_error_propagation() -> None:
    s = score.combine(0.8, 0.1, 0.5, 0.2, variety_id="v", site_id="s")
    assert abs(s.suitability - 0.40) < 1e-9
    # Var = 0.5^2 * 0.1^2 + 0.8^2 * 0.2^2 = 0.0025 + 0.0256 = 0.0281
    assert abs(s.suitability_sd - 0.0281 ** 0.5) < 1e-9


def test_unimplemented_stages_fail_loudly() -> None:
    site = climate.Site(site_id="s", latitude=44.0, longitude=-69.0)
    _expect_not_implemented("climate.compute_features", climate.compute_features, site, "1940-01-01", "2024-12-31")
    _expect_not_implemented("survival.build_observations", survival.build_observations)
    _expect_not_implemented("lt50.harmonize", lt50.harmonize, [])
    _expect_not_implemented("graph_impute.build_graph", graph_impute.build_graph)
    _expect_not_implemented("ancestry.numerator_relationship_matrix", ancestry.numerator_relationship_matrix, None)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
