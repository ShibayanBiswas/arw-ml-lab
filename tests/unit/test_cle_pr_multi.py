"""CLE.P.PR_MULTI — multiclass OvR / micro precision-recall."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.plots import plot_pr_multi
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def test_pr_multi_matches_sklearn_oracle():
    X, y = make_classification(
        n_samples=240,
        n_features=8,
        n_informative=4,
        n_classes=3,
        random_state=42,
    )
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.35, random_state=42)
    clf = LogisticRegression(max_iter=500, random_state=42)
    clf.fit(X_tr, y_tr)
    proba = clf.predict_proba(X_te)
    art = plot_pr_multi(y_te, proba)
    assert art["id"] == "CLE.P.PR_MULTI"
    nums = art["numbers"]
    assert len(nums["ap_per_class"]) == 3
    np.testing.assert_allclose(nums["ap_micro"], nums["ap_micro_oracle"], rtol=1e-9)
    per = np.asarray(list(nums["ap_per_class"].values()))
    np.testing.assert_allclose(per, nums["ap_per_class_oracle"], rtol=1e-9)
    assert len(art["plotly"]["data"]) == 4