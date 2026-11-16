"""Explainability thin wrappers (Phase 3)."""

from labcore.explain.ale import ale_1d
from labcore.explain.dice_cf import dice_counterfactuals
from labcore.explain.lime_tabular import lime_explain_row
from labcore.explain.permutation import permutation_explain
from labcore.explain.shap_trees import pdp_equals_mean_ice, tree_shap_explain

__all__ = [
    "tree_shap_explain",
    "pdp_equals_mean_ice",
    "permutation_explain",
    "lime_explain_row",
    "dice_counterfactuals",
    "ale_1d",
]
