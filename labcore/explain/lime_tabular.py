"""LIME tabular local explanations (ARCHITECTURE §17)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd


def lime_explain_row(
    model: Any,
    X_background: pd.DataFrame | np.ndarray,
    row: pd.Series | np.ndarray | dict[str, Any],
    *,
    num_features: int = 10,
    num_samples: int = 5000,
    seed: int = 42,
    predict_fn: Callable[[np.ndarray], np.ndarray] | None = None,
) -> dict[str, Any]:
    """
    Local LIME via ``lime.lime_tabular.LimeTabularExplainer``.

    Spec defaults: discretize_continuous=True, num_features=10,
    num_samples=5000, kernel_width=0.75√p. Returns feature weights,
    local fidelity (score) and a small stability check across 3 seeds.
    """
    from lime.lime_tabular import LimeTabularExplainer

    if isinstance(X_background, pd.DataFrame):
        feature_names = list(X_background.columns)
        X_arr = X_background.to_numpy(dtype=float)
    else:
        X_arr = np.asarray(X_background, dtype=float)
        feature_names = [f"f{i}" for i in range(X_arr.shape[1])]

    if isinstance(row, dict):
        x0 = np.asarray([float(row[c]) for c in feature_names], dtype=float)
    elif isinstance(row, pd.Series):
        x0 = row.reindex(feature_names).to_numpy(dtype=float)
    else:
        x0 = np.asarray(row, dtype=float).ravel()

    p = X_arr.shape[1]
    kernel_width = 0.75 * np.sqrt(p)

    def _default_predict(data: np.ndarray) -> np.ndarray:
        frame = pd.DataFrame(data, columns=feature_names)
        if hasattr(model, "predict_proba"):
            return np.asarray(model.predict_proba(frame), dtype=float)
        preds = np.asarray(model.predict(frame), dtype=float).ravel()
        # binary-ish: stack as two-class probs for LIME
        return np.column_stack([1.0 - preds, preds])

    fn = predict_fn or _default_predict
    class_names = ["0", "1"]
    sample = fn(x0.reshape(1, -1))
    if sample.ndim == 2 and sample.shape[1] > 2:
        class_names = [str(i) for i in range(sample.shape[1])]

    explainer = LimeTabularExplainer(
        X_arr,
        feature_names=feature_names,
        class_names=class_names,
        discretize_continuous=True,
        kernel_width=float(kernel_width),
        random_state=seed,
    )
    explanation = explainer.explain_instance(
        x0,
        fn,
        num_features=num_features,
        num_samples=num_samples,
    )
    weights = explanation.as_list()
    # Stability: two cheaper reruns (≤500 samples) vs primary top-5
    primary_top = {t[0] for t in weights[:5]}
    overlaps: list[float] = []
    for s in (seed + 1, seed + 2):
        e2 = LimeTabularExplainer(
            X_arr,
            feature_names=feature_names,
            class_names=class_names,
            discretize_continuous=True,
            kernel_width=float(kernel_width),
            random_state=s,
        )
        w2 = e2.explain_instance(
            x0, fn, num_features=num_features, num_samples=min(num_samples, 500)
        )
        top2 = {t[0] for t in w2.as_list()[:5]}
        union = primary_top | top2
        overlaps.append(len(primary_top & top2) / max(1, len(union)))
    jaccard = float(np.mean(overlaps)) if overlaps else 0.0

    return {
        "id": "EXPLAIN.T.LIME",
        "feature_names": feature_names,
        "weights": [{"feature": f, "weight": float(w)} for f, w in weights],
        "local_fidelity_r2": float(explanation.score) if explanation.score is not None else None,
        "stability_jaccard_top5": float(jaccard),
        "num_features": num_features,
        "num_samples": num_samples,
        "kernel_width": float(kernel_width),
        "seed": seed,
    }
