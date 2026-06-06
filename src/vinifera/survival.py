"""Stage 2 — Survival association (noisy binary proxy).

For each (variety, freeze event): did the variety appear in commercial production at
exposed sites both BEFORE and AFTER the event?

This is a WEAK, CONFOUNDED signal. It conflates replanting, variety switching, market
forces, microclimate, and -- critically -- burial/hilling (see ``climate.Site.burial_flag``).
Model it as a noisy *observation* with explicit uncertainty, never as ground truth, and
keep it statistically INDEPENDENT of the Stage 4 colocation graph (whose edges are also
production presence) to avoid self-confirming circularity. See ``docs/ANALYSIS.md`` #1, #2.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SurvivalObservation:
    variety_id: str
    event_label: str
    present_before: bool
    present_after: bool
    n_sites: int                 # support: how many exposed sites this is based on
    any_burial_region: bool      # if True, treat as largely uninformative re: genetic hardiness
    # Probability the variety survived, NOT a hard label. Wide where support is thin or
    # burial confounds. Carried forward into imputation / scoring.
    p_survived: float
    p_survived_sd: float


def build_observations(*args, **kwargs) -> list[SurvivalObservation]:
    """Assemble noisy survival observations from production-presence tables + freeze events.

    Must down-weight or exclude burial-region presence and widen uncertainty where site
    support is thin.
    """
    raise NotImplementedError("Stage 2: survival association not implemented")
