"""LIME + DiCE thin wrappers (ARCHITECTURE §17)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from labcore.explain.dice_cf import dice_counterfactuals
from labcore.explain.lime_tabular import lime_explain_row
from lightgbm import LGBMClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


def _binary_frame(n: int = 400):
    X, y = make_classification(
        n_samples=n,
        n_features=8,
        n_informative=5,
        n_redundant=1,
        weights=[0.55, 0.45],
        random_state=42,
    )
    cols = [f"f{i}" for i in range(X.shape[1])]
    return pd.DataFrame(X, columns=cols), pd.Series(y, name="y")


def test_lime_local_fidelity_and_weights():
    X, y = _binary_frame()
    X_tr, X_te, y_tr, _ = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    model = LGBMClassifier(n_estimators=40, max_depth=3, random_state=42, verbose=-1)
    model.fit(X_tr, y_tr)
    out = lime_explain_row(
        model,
        X_tr,
        X_te.iloc[0],
        num_features=6,
        num_samples=800,
        seed=42,
    )
    assert out["id"] == "EXPLAIN.T.LIME"
    assert len(out["weights"]) <= 6
    assert out["local_fidelity_r2"] is not None
    assert np.isfinite(out["local_fidelity_r2"])
    assert 0.0 <= out["stability_jaccard_top5"] <= 1.0


def test_dice_counterfactuals_flip_class():
    X, y = _binary_frame(300)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = LGBMClassifier(n_estimators=40, max_depth=3, random_state=42, verbose=-1)
    model.fit(X_tr, y_tr)
    query = X_te.iloc[[0]]
    pred0 = int(model.predict(query)[0])
    out = dice_counterfactuals(
        model,
        X_tr,
        y_tr,
        query,
        total_cfs=2,
        method="random",
        seed=42,
    )
    assert out["id"] == "EXPLAIN.T.DICE"
    assert len(out["counterfactuals"]) == 1
    cfs = out["counterfactuals"][0]
    assert len(cfs) >= 1
    # At least one CF should flip the predicted class when scored
    flipped = False
    for row in cfs:
        frame = pd.DataFrame([row])[list(X.columns)]
        if int(model.predict(frame)[0]) != pred0:
            flipped = True
            break
    assert flipped, {"pred0": pred0, "cfs": cfs}
    assert np.isfinite(out["diversity_mean_l1"][0])
