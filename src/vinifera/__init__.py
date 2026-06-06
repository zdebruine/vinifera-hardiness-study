"""Cold-hardy vinifera suitability scoring.

Two explicit axes — winter survival and ripening attainability — combined into an
open, reproducible suitability score. See ``docs/PLAN.md`` and ``docs/ANALYSIS.md``.

This is decision-support / hypothesis-generating output, NOT a validated predictive
model: vine-level survival ground truth largely does not exist, so the survival axis
is an uncertainty-carrying imputation, not a measurement.
"""

__version__ = "0.0.0"

__all__ = [
    "climate",
    "survival",
    "lt50",
    "graph_impute",
    "ancestry",
    "ripening",
    "score",
]
