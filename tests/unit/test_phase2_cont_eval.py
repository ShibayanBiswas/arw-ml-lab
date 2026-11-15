"""Phase 2-cont Eval Core ACs."""

from __future__ import annotations

import numpy as np
from labcore.eval.classification.cm import confusion_suite
from labcore.eval.classification.compare import delong_test, mcnemar_test, paired_5x2cv
from labcore.eval.classification.metrics import compute_cle_metrics
from labcore.eval.classification.suite import run_classification_eval
from labcore.eval.classification.threshold import tune_threshold_oof
from labcore.eval.regression.diagnostics import influence_table, residual_tests
from labcore.registry.algorithms import build_estimator, thin_algorithm_specs
from labcore.train.run import TrainConfig, run_supervised_cv
from sklearn.datasets import load_breast_cancer, load_iris, make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, matthews_corrcoef, r2_score


def test_catalog_at_least_30():
    specs = thin_algorithm_specs()
    assert len(specs) >= 30
    for s in specs:
        assert build_estimator(s) is not None


def test_cm_norms_and_pool():
    y = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    p = np.array([0, 1, 1, 1, 0, 0, 0, 1])
    cm = confusion_matrix(y, p)
    folds = [cm[:], cm[:]]
    suite = confusion_suite(y, p, labels=[0, 1], fold_matrices=folds)
    assert suite["counts"] == cm.tolist()
    # norms sum ~1
    assert abs(sum(suite["norm_all"][0]) + sum(suite["norm_all"][1]) - 1.0) < 1e-9
    assert suite["cv_norm_mean"] is not None


def test_cle_m_oracle_equality():
    X, y = make_classification(n_samples=200, n_features=8, random_state=42)
    clf = LogisticRegression(max_iter=500, random_state=42).fit(X, y)
    pred = clf.predict(X)
    proba = clf.predict_proba(X)
    m = compute_cle_metrics(y, pred, proba, task="binary")
    assert abs(m["CLE.M.01"] - accuracy_score(y, pred)) < 1e-12
    assert abs(m["CLE.M.14"] - matthews_corrcoef(y, pred)) < 1e-12


def test_threshold_never_reads_test():
    spy: list[str] = []
    y = np.array([0, 0, 1, 1, 0, 1, 0, 1, 0, 1] * 5)
    scores = np.linspace(0.1, 0.9, len(y))
    proba = np.column_stack([1 - scores, scores])
    # Tuning only gets OOF
    out = tune_threshold_oof(y, proba)
    assert "youden" in out["methods"]
    assert spy == []  # test never appended
    # Full suite with spy on test metrics only
    run_classification_eval(
        y_oof=y,
        y_pred_oof=(scores >= 0.5).astype(int),
        y_proba_oof=proba,
        y_test=y[:10],
        y_pred_test=(scores[:10] >= 0.5).astype(int),
        y_proba_test=proba[:10],
        task="binary",
        test_touch_spy=spy,
    )
    assert "metrics_test" in spy
    # Threshold object exists and was built from OOF
    assert out["methods"]["youden"]["t_star"] is not None


def test_mcnemar_delong_5x2():
    rng = np.random.default_rng(42)
    y = rng.integers(0, 2, size=80)
    a = y.copy()
    b = y.copy()
    b[:10] = 1 - b[:10]
    m = mcnemar_test(y, a, b)
    assert "pvalue" in m
    scores_a = rng.random(80)
    scores_b = scores_a + 0.01
    d = delong_test(y, scores_a, scores_b)
    assert "pvalue" in d

    X, y2 = make_classification(n_samples=120, n_features=6, random_state=42)
    e1 = LogisticRegression(max_iter=300, random_state=42)
    e2 = LogisticRegression(max_iter=300, C=0.1, random_state=42)
    r = paired_5x2cv(e1, e2, X, y2, seed=42)
    assert "pvalue" in r


def test_ds4_binary_eval():
    data = load_breast_cancer(as_frame=True)
    df = data.frame.copy()
    df["target"] = data.target
    # subsample for speed
    df = df.sample(n=300, random_state=42)
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="binary",
            target="target",
            algorithm_keys=["clf.logistic", "clf.rf"],
            n_splits=3,
        ),
    )
    cle = out["eval"]["classification"]
    assert cle["cm"]["counts"]
    assert cle["report"]["rows"]
    assert cle["cv_metrics"]["id"] == "CLE.T.CV_METRICS"
    assert any(p["id"].startswith("CLE.P") for p in cle["plots"])


def test_ds10_multiclass_eval():
    data = load_iris(as_frame=True)
    df = data.frame.copy()
    df["target"] = data.target
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="multiclass",
            target="target",
            algorithm_keys=["clf.logistic", "clf.rf"],
            n_splits=3,
        ),
    )
    cle = out["eval"]["classification"]
    assert len(cle["cm"]["labels"]) == 3
    assert cle["report"]["footer"]["accuracy"] is not None


def test_ds12_regression_eval():
    from sklearn.datasets import fetch_california_housing

    bunch = fetch_california_housing(as_frame=True)
    df = bunch.frame.sample(n=800, random_state=42)
    out = run_supervised_cv(
        df,
        TrainConfig(
            task="regression",
            target="MedHouseVal",
            algorithm_keys=["reg.ridge", "reg.rf"],
            n_splits=3,
        ),
    )
    ree = out["eval"]["regression"]
    assert ree["residuals"]["id"] == "REE.T.RESIDUALS"
    assert ree["resid_tests"]["id"] == "REE.T.RESID_TESTS"
    assert ree["influence"]["id"] == "REE.T.INFLUENCE"
    assert "REE.M.01" in ree["metrics"]
    # oracle r2 on OOF
    y = np.array([r["y_true"] for r in ree["residuals"]["rows"]])
    yp = np.array([r["y_pred"] for r in ree["residuals"]["rows"]])
    assert abs(ree["metrics"]["REE.M.01"] - r2_score(y, yp)) < 1e-12


def test_ree_influence_matches_statsmodels():
    rng = np.random.default_rng(42)
    y = rng.normal(size=100)
    pred = y + rng.normal(scale=0.2, size=100)
    infl = influence_table(y, pred)
    assert infl["cooks_d_max"] >= 0
    tests = residual_tests(y, pred)
    names = {t["test"] for t in tests["tests"]}
    assert "Shapiro-Wilk" in names
    assert "Breusch-Pagan" in names
