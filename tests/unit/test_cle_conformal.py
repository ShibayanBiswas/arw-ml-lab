"""CLE.P.CONFORMAL — MAPIE conformal set diagnostics."""

from __future__ import annotations

import numpy as np
from mapie.classification import SplitConformalClassifier
from mapie.metrics.classification import classification_coverage_score
from mapie.utils import train_conformalize_test_split
from sklearn.base import clone
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

from labcore.eval.classification.plots import plot_conformal


def test_conformal_plot_synthetic():
    y_true = np.array([0, 0, 1, 1, 2])
    sets = np.array(
        [
            [True, False, False],
            [True, True, False],
            [False, True, False],
            [False, True, True],
            [False, False, True],
        ]
    )
    art = plot_conformal(y_true, sets, class_labels=[0, 1, 2], confidence_level=0.9)
    assert art["id"] == "CLE.P.CONFORMAL"
    expected = float(classification_coverage_score(y_true, sets)[0])
    assert art["numbers"]["overall_coverage"] == expected
    assert art["numbers"]["coverage_per_class"][0] == 1.0
    assert art["numbers"]["coverage_per_class"][1] == 1.0
    assert art["numbers"]["set_size_hist"]["1"] == 3
    assert art["numbers"]["set_size_hist"]["2"] == 2
    assert "plotly" in art and art["plotly"]["data"]


def test_conformal_plot_mapie_aps_sets():
    X, y = make_classification(
        n_samples=500,
        n_features=8,
        n_informative=6,
        n_classes=3,
        random_state=42,
    )
    X_train, X_conf, X_test, y_train, y_conf, y_test = train_conformalize_test_split(
        X,
        y,
        train_size=0.5,
        conformalize_size=0.25,
        test_size=0.25,
        random_state=42,
    )
    est = RandomForestClassifier(n_estimators=30, random_state=42)
    mapie = SplitConformalClassifier(
        estimator=clone(est),
        confidence_level=0.9,
        conformity_score="aps",
        prefit=False,
        random_state=42,
    )
    mapie.fit(X_train, y_train)
    mapie.conformalize(X_conf, y_conf)
    _pred, y_ps = mapie.predict_set(X_test, conformity_score_params={"include_last_label": True})
    sets = np.asarray(y_ps, dtype=bool)
    leaf = getattr(mapie, "estimator_", None) or getattr(mapie, "_estimator", None)
    class_labels = list(getattr(leaf, "classes_", np.unique(y)))
    art = plot_conformal(y_test, sets, class_labels=class_labels, confidence_level=0.9)
    assert art["numbers"]["n_samples"] == len(y_test)
    assert 0.0 <= art["numbers"]["overall_coverage"] <= 1.0
    assert art["numbers"]["mean_set_size"] >= 1.0