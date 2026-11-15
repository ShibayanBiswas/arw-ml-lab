"""Explainability thin wrappers (Phase 3)."""

from labcore.explain.shap_trees import pdp_equals_mean_ice, tree_shap_explain

__all__ = ["tree_shap_explain", "pdp_equals_mean_ice"]
