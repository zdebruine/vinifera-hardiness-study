"""Stage 4 — Colocation knowledge graph + imputation.

Nodes = varieties; edges = colocation weighted by co-bearing hectares (Anderson & Nelgen).
Propagate observed LT50 / survival to unobserved varieties via a Gaussian-field (harmonic)
solution.

CAVEAT (circularity, docs/ANALYSIS.md #1): colocation encodes tradition and market, not
only hardiness -- AND it is the same production-presence signal Stage 2 uses for survival
labels. Propagating Stage-2 labels along this graph can self-confirm. Keep the two
independent, or prefer a single hierarchical model. Report imputation as a PRIOR with
cross-validated error, not a measurement.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImputationResult:
    variety_id: str
    value: float          # imputed LT50 or survival prior
    sd: float             # cross-validated uncertainty (wider far from observations)
    observed: bool        # True if anchored by direct data, False if purely imputed


def build_graph(*args, **kwargs) -> object:
    """Build the weighted colocation graph (networkx) from co-bearing hectares."""
    raise NotImplementedError("Stage 4: colocation graph construction not implemented")


def harmonic_impute(graph: object, observed: dict[str, float]) -> list[ImputationResult]:
    """Gaussian-field / harmonic propagation of observed values over the graph.

    Must report leave-one-out cross-validated error so the imputation is presented as a
    prior, not a measurement.
    """
    raise NotImplementedError("Stage 4: harmonic imputation not implemented")
