"""ONNX export parity + skops round-trip (seed 42)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from labcore.export.onnx_export import export_sklearn_onnx, onnx_parity
from labcore.export.skops_store import load_skops, save_skops
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def test_skops_roundtrip(tmp_path: Path) -> None:
    data = load_breast_cancer()
    X, y = data.data[:120], data.target[:120]
    clf = LogisticRegression(max_iter=5000, random_state=42).fit(X, y)
    meta = save_skops(clf, tmp_path / "model.skops")
    loaded = load_skops(tmp_path / "model.skops", expected_sha256=str(meta["sha256"]))
    assert np.array_equal(clf.predict(X[:10]), loaded.predict(X[:10]))


def test_onnx_parity_logistic(tmp_path: Path) -> None:
    data = load_breast_cancer()
    X, y = data.data, data.target
    X_train, X_test, y_train, _y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    clf = LogisticRegression(max_iter=800, random_state=42).fit(X_train, y_train)
    meta = export_sklearn_onnx(clf, X_train.astype(np.float32), tmp_path / "m.onnx")
    assert Path(str(meta["path"])).exists()
    assert int(meta["size_bytes"]) > 100
    result = onnx_parity(clf, tmp_path / "m.onnx", X_test[:40].astype(np.float32), atol=1e-3)
    assert result["passed"] is True
    assert result["label_match"] is True
