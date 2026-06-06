"""Stage 6 — Ripening fitness.

P(ripen) = Phi( (GDD_site - GDD_req_variety) / sigma ), where Phi is the standard normal
CDF (its logistic-shaped curve reconciles the "Gaussian" and "logistic" framings).
GDD_req is anchored from established DOC/DOCG/AVA sites that ripen the variety to a target
style.

CAVEAT: "ripe to target style" is subjective and the anchor sites self-select for success
(survivorship bias). Define the target operationally (e.g., Brix/TA by style) before
anchoring GDD_req, and run the sigma sensitivity analysis -- sigma drives this curve.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class RipeningRequirement:
    variety_id: str
    gdd_req_f: float          # GDD (base 50 degF) to ripen to target style
    sigma_f: float            # spread; the dominant lever -- subject to sensitivity analysis
    anchor_sources: tuple[str, ...] = ()  # DOC/DOCG/AVA anchor site ids


def p_ripen(gdd_site_f: float, req: RipeningRequirement) -> float:
    """Probability the variety ripens to target style at a site with the given GDD.

    Standard normal CDF of the standardized GDD surplus. This is the one stage with a
    closed-form implementation; it is pure and deterministic given its inputs.
    """
    if req.sigma_f <= 0:
        raise ValueError("sigma_f must be positive")
    z = (gdd_site_f - req.gdd_req_f) / req.sigma_f
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
