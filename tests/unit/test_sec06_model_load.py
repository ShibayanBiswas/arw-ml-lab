"""SEC.MODEL.LOAD — artefact store + skops + weights_only torch (ST-SEC-06 / oneshot-c152)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from labcore.export.skops_store import save_skops
from labcore.security.model_load_policy import (
    ARTEFACT_ID,
    POLICY_SEED,
    ModelLoadRejected,
    assert_lab_store_object_key,
    load_sklearn_lab,
    load_torch_checkpoint,
    policy_manifest,
    reject_user_model_upload,
)
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression


def test_artefact_id_and_manifest_seed_42() -> None:
    assert ARTEFACT_ID == "SEC.MODEL.LOAD"
    manifest = policy_manifest()
    assert manifest["seed"] == POLICY_SEED == 42
    assert manifest["torch_weights_only"] is True
    assert manifest["user_uploaded_models_v1"] is False


def test_reject_user_upload_and_pickle_suffix() -> None:
    with pytest.raises(ModelLoadRejected, match="user-uploaded"):
        reject_user_model_upload(source="user_upload")
    with pytest.raises(ModelLoadRejected, match="forbidden"):
        reject_user_model_upload(path=Path("evil.pkl"))


def test_assert_lab_store_object_key() -> None:
    wid = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
    mid = "11111111-2222-4333-8444-555555555555"
    key = f"{wid}/models/{mid}/pipeline.skops"
    assert_lab_store_object_key(key)
    with pytest.raises(ModelLoadRejected, match="lab artefact store"):
        assert_lab_store_object_key("uploads/evil.pkl")


def test_load_sklearn_lab_roundtrip(tmp_path: Path) -> None:
    data = load_breast_cancer()
    X, y = data.data[:80], data.target[:80]
    clf = LogisticRegression(max_iter=5000, random_state=42).fit(X, y)
    store_dir = tmp_path / "models" / "run-1"
    store_dir.mkdir(parents=True)
    meta = save_skops(clf, store_dir / "model.skops")
    loaded = load_sklearn_lab(
        store_dir / "model.skops",
        expected_sha256=str(meta["sha256"]),
    )
    assert np.array_equal(clf.predict(X[:5]), loaded.predict(X[:5]))


def test_load_sklearn_lab_rejects_sha_mismatch(tmp_path: Path) -> None:
    data = load_breast_cancer()
    X, y = data.data[:40], data.target[:40]
    clf = LogisticRegression(max_iter=5000, random_state=42).fit(X, y)
    store_dir = tmp_path / "models" / "run-2"
    store_dir.mkdir(parents=True)
    save_skops(clf, store_dir / "model.skops")
    with pytest.raises(ModelLoadRejected, match="sha256"):
        load_sklearn_lab(store_dir / "model.skops", expected_sha256="0" * 64)


def test_load_torch_weights_only(tmp_path: Path) -> None:
    torch = pytest.importorskip("torch")
    store_dir = tmp_path / "models" / "torch-1"
    store_dir.mkdir(parents=True)
    ckpt = store_dir / "weights.pt"
    state = {"w": torch.tensor([1.0, 2.0, 3.0], dtype=torch.float32)}
    torch.save(state, ckpt)
    digest = __import__("hashlib").sha256(ckpt.read_bytes()).hexdigest()
    loaded = load_torch_checkpoint(ckpt, expected_sha256=digest)
    assert torch.allclose(loaded["w"], state["w"])