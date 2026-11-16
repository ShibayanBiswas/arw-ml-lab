"""DiCE counterfactual explanations (ARCHITECTURE §17)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd


def dice_counterfactuals(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series | np.ndarray,
    query_rows: pd.DataFrame,
    *,
    total_cfs: int = 3,
    method: Literal["random", "genetic", "kdtree"] = "random",
    desired_class: str | int = "opposite",
    seed: int = 42,
) -> dict[str, Any]:
    """
    Minimal-change counterfactuals via ``dice_ml.Dice``.

    Returns CF table rows plus diversity (mean pairwise L1 among CFs).
    Classification only (DiCE model_type='classifier').
    """
    import dice_ml
    from dice_ml import Dice

    _ = seed  # DiCE random method uses internal RNG; documented for audit
    feature_names = list(X.columns)
    outcome = "_lab_y"
    train = X.copy()
    train[outcome] = np.asarray(y).ravel()
    continuous = [c for c in feature_names if pd.api.types.is_numeric_dtype(X[c])]
    data = dice_ml.Data(
        dataframe=train,
        continuous_features=continuous,
        outcome_name=outcome,
    )
    dice_model = dice_ml.Model(model=model, backend="sklearn", model_type="classifier")
    explainer = Dice(data, dice_model, method=method)
    query = query_rows[feature_names].copy()
    result = explainer.generate_counterfactuals(
        query,
        total_CFs=total_cfs,
        desired_class=desired_class,
    )
    cf_tables: list[list[dict[str, Any]]] = []
    diversities: list[float] = []
    for ex in result.cf_examples_list:
        cf_df = ex.final_cfs_df
        if cf_df is None or len(cf_df) == 0:
            cf_tables.append([])
            diversities.append(float("nan"))
            continue
        feats = cf_df[feature_names]
        cf_tables.append(feats.to_dict(orient="records"))
        arr = feats.to_numpy(dtype=float)
        if len(arr) < 2:
            diversities.append(0.0)
        else:
            dists = []
            for i in range(len(arr)):
                for j in range(i + 1, len(arr)):
                    dists.append(float(np.mean(np.abs(arr[i] - arr[j]))))
            diversities.append(float(np.mean(dists)))

    return {
        "id": "EXPLAIN.T.DICE",
        "method": method,
        "total_cfs": total_cfs,
        "desired_class": desired_class,
        "feature_names": feature_names,
        "counterfactuals": cf_tables,
        "diversity_mean_l1": diversities,
        "seed": seed,
    }
