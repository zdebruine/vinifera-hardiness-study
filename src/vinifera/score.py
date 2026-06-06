"""Stage 7 — Composite suitability score.

Report TWO explicit axes -- survival and ripening -- plus a combined suitability
(survival x ripening), with propagated uncertainty and a sensitivity analysis on weights
and sigma.

The multiplicative combination means a variety that cannot ripen anywhere scores ~0
regardless of hardiness, and vice versa -- appropriate for a "suitability" screen. Always
surface the two component axes alongside the product so the reason for a low score is
visible.

Reminder: this is decision support, not validated prediction (docs/ANALYSIS.md #4).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SuitabilityScore:
    variety_id: str
    site_id: str
    p_survive: float
    p_survive_sd: float
    p_ripen: float
    p_ripen_sd: float
    suitability: float        # p_survive * p_ripen
    suitability_sd: float     # propagated


def combine(p_survive: float, p_survive_sd: float,
            p_ripen: float, p_ripen_sd: float,
            variety_id: str, site_id: str) -> SuitabilityScore:
    """Combine the two axes with first-order error propagation for independent factors.

    Var(XY) ~= (E[Y])^2 Var(X) + (E[X])^2 Var(Y) for independent X, Y.
    """
    suitability = p_survive * p_ripen
    var = (p_ripen ** 2) * (p_survive_sd ** 2) + (p_survive ** 2) * (p_ripen_sd ** 2)
    return SuitabilityScore(
        variety_id=variety_id,
        site_id=site_id,
        p_survive=p_survive,
        p_survive_sd=p_survive_sd,
        p_ripen=p_ripen,
        p_ripen_sd=p_ripen_sd,
        suitability=suitability,
        suitability_sd=var ** 0.5,
    )
