"""Target encoding in-pipeline — MI-02 (ARCHITECTURE §46.1).

``sklearn.preprocessing.TargetEncoder`` must live inside the recipe pipeline with
internal cross-fitting — never pre-computed on the full frame before CV.
"""

from __future__ import annotations

from typing import Any

from sklearn.preprocessing import TargetEncoder

MI02_RULE = "MI-02"
MI02_SYNTHETIC_ROWS = 5000
MI02_MAX_AUC_DEVIATION = 0.03
MI02_DEFAULT_TARGET_ENCODER_CV = 5


def auc_deviation_from_chance(auc: float) -> float:
    return abs(float(auc) - 0.5)


def noise_auc_passes_mi02(
    auc: float,
    *,
    max_deviation: float = MI02_MAX_AUC_DEVIATION,
) -> bool:
    return auc_deviation_from_chance(auc) < max_deviation


def target_encoder_shuffle(*, sequential: bool) -> bool:
    """MI-02: sequential tasks must not shuffle TargetEncoder inner CV."""
    return not sequential


def extract_recipe_target_encoder(preprocess_step: Any) -> TargetEncoder | None:
    """Return the ``TargetEncoder`` inside a compiled recipe preprocess step, if any."""
    cat = None
    if hasattr(preprocess_step, "named_transformers_"):
        cat = preprocess_step.named_transformers_.get("cat")
    elif hasattr(preprocess_step, "transformers"):
        for name, trans, _cols in preprocess_step.transformers:
            if name == "cat":
                cat = trans
                break
    if cat is None:
        return None
    steps = getattr(cat, "named_steps", None)
    if not steps or "encoder" not in steps:
        return None
    enc = steps["encoder"]
    return enc if isinstance(enc, TargetEncoder) else None