"""ONNX export + parity for sklearn estimators (skl2onnx + onnxruntime)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np


def export_sklearn_onnx(
    estimator: Any,
    X_sample: np.ndarray,
    path: str | Path,
    *,
    target_opset: int = 15,
) -> dict[str, Any]:
    """Convert fitted sklearn estimator to ONNX bytes on disk.

    Uses ``skl2onnx.to_onnx`` with zipmap disabled for stable probability outputs.
    """
    from skl2onnx import to_onnx  # type: ignore[import-untyped]

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    X = np.asarray(X_sample, dtype=np.float32)
    onx = to_onnx(estimator, X[:1], options={"zipmap": False}, target_opset=target_opset)
    raw = onx.SerializeToString()
    path.write_bytes(raw)
    return {
        "path": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "format": "onnx",
        "target_opset": target_opset,
    }


def onnx_parity(
    estimator: Any,
    onnx_path: str | Path,
    X: np.ndarray,
    *,
    atol: float = 1e-4,
) -> dict[str, Any]:
    """Compare sklearn ``predict`` / ``predict_proba`` to ONNX Runtime outputs."""
    from onnxruntime import InferenceSession  # type: ignore[import-untyped]

    X = np.asarray(X, dtype=np.float32)
    sk_pred = np.asarray(estimator.predict(X))
    sess = InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    in_name = sess.get_inputs()[0].name
    outs = sess.run(None, {in_name: X})
    onnx_label = np.asarray(outs[0]).reshape(-1)
    label_ok = bool(np.array_equal(sk_pred.astype(onnx_label.dtype), onnx_label))
    proba_max_abs: float | None = None
    proba_ok = True
    if hasattr(estimator, "predict_proba") and len(outs) > 1:
        sk_proba = np.asarray(estimator.predict_proba(X), dtype=float)
        onnx_proba = np.asarray(outs[1], dtype=float)
        if onnx_proba.ndim == 1:
            onnx_proba = onnx_proba.reshape(-1, 1)
        proba_max_abs = float(np.max(np.abs(sk_proba - onnx_proba)))
        proba_ok = bool(proba_max_abs <= atol)
    return {
        "label_match": label_ok,
        "proba_ok": proba_ok,
        "proba_max_abs": proba_max_abs,
        "n": int(X.shape[0]),
        "passed": bool(label_ok and proba_ok),
    }
