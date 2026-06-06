"""Stage 3 — LT50 meta-analysis (method-harmonized).

Harmonize published cold-hardiness values to a common target (max midwinter bud LT50),
adjusting for:
  * method  -- DTA/LTE vs electrolyte leakage vs tetrazolium,
  * tissue  -- bud vs cane vs root,
  * sampling date / acclimation state.

Where the WSU dynamic model exists (~23 genotypes), PREFER model-predicted hardiness on
each freeze date over a single literature point.

CAVEAT: within pure vinifera the hardiness range is narrow and method effects can exceed
between-variety differences. This mechanistic axis is more trustworthy than the Stage 2
survival association; on conflict, trust LT50 and use survival as soft validation only.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Method(str, Enum):
    DTA_LTE = "dta_lte"                # differential thermal analysis / low-temp exotherm
    ELECTROLYTE_LEAKAGE = "electrolyte_leakage"
    TETRAZOLIUM = "tetrazolium"
    WSU_DYNAMIC_MODEL = "wsu_dynamic_model"


class Tissue(str, Enum):
    BUD = "bud"
    CANE = "cane"
    ROOT = "root"


@dataclass(frozen=True)
class LT50Record:
    variety_id: str
    lt50_c: float
    method: Method
    tissue: Tissue
    sampling_date: str | None     # ISO; needed to place acclimation state
    source: str                   # citation key (see ATTRIBUTION.md)


@dataclass(frozen=True)
class HarmonizedLT50:
    variety_id: str
    midwinter_bud_lt50_c: float   # common target
    sd_c: float                   # includes method/harmonization uncertainty
    n_records: int


def harmonize(records: list[LT50Record]) -> list[HarmonizedLT50]:
    """Random-effects meta-analysis with method/tissue/date fixed effects.

    Returns one harmonized midwinter bud LT50 (with uncertainty) per variety.
    """
    raise NotImplementedError("Stage 3: LT50 harmonization not implemented")
