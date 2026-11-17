"""PRED.HUMILITY API wire — oneshot-c195 (router helper + predict_single)."""

from __future__ import annotations

from types import SimpleNamespace

from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np

from backend.app.routers.predict import _humility_opts_for_row
from labcore.predict.score import predict_single


def _fitted() -> tuple[Pipeline, list[str], dict, np.ndarray]:
    X, y = make_classification(
        n_samples=60,
        n_features=3,
        n_informative=2,
        n_redundant=0,
        n_repeated=0,
        random_state=42,
    )
    pipe = Pipeline(
        [("sc", StandardScaler()), ("m", LogisticRegression(random_state=42, max_iter=200))]
    )
    pipe.fit(X, y)
    names = ["f0", "f1", "f2"]
    contract = {
        "dataset_id": "humility-api",
        "task": "binary",
        "target": "y",
        "seed": 42,
        "features": [
            {
                "name": n,
                "kind": "numeric",
                "mean": float(X[:, i].mean()),
                "std": float(max(X[:, i].std(), 1e-6)),
                "min": float(X[:, i].min()),
                "max": float(X[:, i].max()),
            }
            for i, n in enumerate(names)
        ],
    }
    return pipe, names, contract, X


def test_humility_opts_merges_ood_from_validate() -> None:
    pipe, names, contract, X = _fitted()
    m = SimpleNamespace(feature_contract=contract, feature_names=names, pipeline=pipe)
    mean0 = float(X[:, 0].mean())
    std0 = float(max(X[:, 0].std(), 1e-6))
    row = {"f0": mean0 + 20 * std0, "f1": float(X[0, 1]), "f2": float(X[0, 2])}
    opts = _humility_opts_for_row(m, row, {})
    assert "f0" in opts.get("flag_out_of_range", [])


def test_predict_single_default_humility_warns_on_oor() -> None:
    pipe, names, contract, X = _fitted()
    m = SimpleNamespace(feature_contract=contract, feature_names=names, pipeline=pipe)
    mean0 = float(X[:, 0].mean())
    std0 = float(max(X[:, 0].std(), 1e-6))
    row = {"f0": mean0 + 20 * std0, "f1": float(X[0, 1]), "f2": float(X[0, 2])}
    opts = _humility_opts_for_row(m, row, {"action_out_of_range": "warn"})
    out = predict_single(pipe, row, feature_names=names, humility=opts)
    assert out["refit"] is False
    assert "humility" in out
    assert out["humility"]["humility_action"] == "warn"
    assert "out_of_range" in out["humility"]["humility_triggers"]


def test_predict_single_humility_none_path_skips() -> None:
    pipe, names, _contract, X = _fitted()
    row = {n: float(X[0, i]) for i, n in enumerate(names)}
    out = predict_single(pipe, row, feature_names=names, humility=None)
    assert "humility" not in out
