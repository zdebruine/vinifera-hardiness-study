"""Stage 5 — Ancestry refinement.

Pedigree -> Wright numerator-relationship (A) matrix -> kinship clusters; optionally a
marker-based NJ/UPGMA tree if a genotype matrix (Laucou SSR / Myles SNP) is obtained.
Relatedness is used as a regularizer / hierarchical prior on the survival score.

CAVEAT: within pure vinifera the hardiness range is narrow and the pedigree is admixed
(Pinot, Gouais, Traminer as super-parents) -- expect a MODEST, not dominant, ancestry
signal. Recorded parentage (Wikidata/VIVC) is patchy and error-prone, so the A-matrix has
heavy missingness; a marker-based tree is preferable where genotypes are available because
it does not depend on correct recorded parentage.
"""
from __future__ import annotations


def numerator_relationship_matrix(pedigree: object) -> object:
    """Wright's A-matrix from a (possibly incomplete) pedigree."""
    raise NotImplementedError("Stage 5: A-matrix construction not implemented")


def marker_tree(genotype_matrix: object) -> object:
    """NJ/UPGMA tree from an SSR/SNP genotype matrix (preferred over A when available)."""
    raise NotImplementedError("Stage 5: marker-based tree not implemented")
