"""Unit tests for the two closed-form stages (ripening CDF, score combination)."""
import sys

sys.path.insert(0, "src")

from vinifera import ripening, score  # noqa: E402


def test_p_ripen_centered_at_requirement():
    req = ripening.RipeningRequirement(variety_id="v", gdd_req_f=2800.0, sigma_f=250.0)
    assert abs(ripening.p_ripen(2800.0, req) - 0.5) < 1e-9


def test_p_ripen_monotone():
    req = ripening.RipeningRequirement(variety_id="v", gdd_req_f=2800.0, sigma_f=250.0)
    vals = [ripening.p_ripen(g, req) for g in (2000, 2500, 2800, 3100, 3600)]
    assert all(b > a for a, b in zip(vals, vals[1:]))


def test_p_ripen_rejects_nonpositive_sigma():
    import pytest

    with pytest.raises(ValueError):
        ripening.p_ripen(2800.0, ripening.RipeningRequirement("v", 2800.0, 0.0))


def test_combine_product():
    s = score.combine(0.9, 0.05, 0.6, 0.1, variety_id="v", site_id="s")
    assert abs(s.suitability - 0.54) < 1e-9


def test_combine_error_propagation_independent_factors():
    s = score.combine(0.5, 0.1, 0.5, 0.1, variety_id="v", site_id="s")
    # Var = 0.5^2*0.1^2 * 2 = 0.005 -> sd = sqrt(0.005)
    assert abs(s.suitability_sd - 0.005 ** 0.5) < 1e-12
