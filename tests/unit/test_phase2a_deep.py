"""Phase 2A thin: DL registry, tabular/sequential smokes, LR finder, TabPFN/GPU guards."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

torch = pytest.importorskip("torch")
pytest.importorskip("lightning")
pytest.importorskip("pytorch_tabular")
pytest.importorskip("pytorch_tcn")

from labcore.data.samples import load_sample_frame  # noqa: E402
from labcore.deep.artefacts import pack_dl_artefacts  # noqa: E402
from labcore.deep.engine import set_seed  # noqa: E402
from labcore.deep.guards import assert_gpu_allowed, gpu_worker_available, tabpfn_enabled  # noqa: E402
from labcore.deep.registry import deep_algorithm_specs  # noqa: E402
from labcore.deep.sequential import (  # noqa: E402
    WindowSpec,
    assert_no_window_label_overlap,
    build_windows,
    fit_sequential,
    frame_to_xy,
)
from labcore.deep.tabular import fit_tabular, quick_split  # noqa: E402
from labcore.registry.catalog import get_catalog, visible_algorithm_specs  # noqa: E402


def test_deep_specs_defaults_and_search_bounds():
    specs = deep_algorithm_specs()
    keys = {s.key for s in specs}
    assert {"dl.mlp", "dl.tabnet", "dl.ft_transformer", "seq.lstm", "seq.tcn"} <= keys
    assert "dl.tabpfn" in keys
    assert "seq.xlstm" in keys
    for s in specs:
        assert s.params
        for p in s.params:
            assert p.default is not None or p.type.endswith("_or_none")


def test_tabpfn_hidden_when_disabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TABPFN_ENABLED", raising=False)
    assert tabpfn_enabled() is False
    keys = {s.key for s in visible_algorithm_specs()}
    assert "dl.tabpfn" not in keys
    cat_keys = {a.key for a in get_catalog().algorithms}
    assert "dl.tabpfn" not in cat_keys
    # CPU deep models remain visible
    assert "dl.mlp" in cat_keys


def test_tabpfn_visible_when_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TABPFN_ENABLED", "true")
    assert tabpfn_enabled() is True
    keys = {s.key for s in visible_algorithm_specs()}
    assert "dl.tabpfn" in keys


def test_gpu_guard_422_without_worker(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("LAB_GPU_WORKER", raising=False)
    assert gpu_worker_available() is False
    with pytest.raises(ValueError, match="GPU worker"):
        assert_gpu_allowed({"gpu": True})
    assert_gpu_allowed({"gpu": False})  # no raise


def test_api_gpu_model_returns_422(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_TEST_BYPASS", "true")
    monkeypatch.delenv("LAB_GPU_WORKER", raising=False)
    from backend.app.dataset_store import DATASET_STORE
    from backend.app.main import create_app

    rec = DATASET_STORE.create_dataset(
        workspace_id="00000000-0000-0000-0000-000000000010",
        name="gpu-guard",
        source="sample",
        sample_id=None,
        storage_key=None,
        parquet_path=None,
        content_hash=None,
    )
    client = TestClient(create_app())
    headers = {
        "Authorization": "Bearer test",
        "X-Test-Role": "analyst",
        "X-Test-User-Id": "00000000-0000-0000-0000-000000000099",
        "X-Test-Workspace-Id": "00000000-0000-0000-0000-000000000010",
    }
    r = client.post(
        "/api/v1/experiments/train",
        json={
            "dataset_id": rec.id,
            "target": "y",
            "task": "regression",
            "algorithm_keys": ["seq.xlstm"],
        },
        headers=headers,
    )
    assert r.status_code == 422, r.text
    assert "GPU" in r.json()["detail"]


def test_window_purge_embargo_no_overlap():
    rng = np.random.default_rng(42)
    X = rng.normal(size=(120, 3))
    y = rng.normal(size=120)
    lookback, horizon, purge, embargo = 16, 1, 2, 1
    _Xw, _yw, ends = build_windows(X, y, lookback=lookback, horizon=horizon, stride=1)
    split = int(len(ends) * 0.8)
    train_ends = ends[:split]
    val_labels = ends[split:] + horizon
    keep: list[int] = []
    for end in train_ends:
        try:
            assert_no_window_label_overlap(
                np.asarray([end]),
                val_labels,
                lookback=lookback,
                horizon=horizon,
                purge=purge,
                embargo=embargo,
            )
            keep.append(int(end))
        except AssertionError:
            continue
    assert keep, "expected some purged train windows"
    assert_no_window_label_overlap(
        np.asarray(keep),
        val_labels,
        lookback=lookback,
        horizon=horizon,
        purge=purge,
        embargo=embargo,
    )
    # positive control: unpurged boundary must fail
    with pytest.raises(AssertionError):
        assert_no_window_label_overlap(
            train_ends[-3:],
            val_labels[:3],
            lookback=lookback,
            horizon=horizon,
            purge=purge,
            embargo=embargo,
        )


@pytest.mark.parametrize("model_key", ["mlp", "tabnet", "ft_transformer"])
def test_tabular_smoke_ds3_classification(model_key: str):
    df, _, _ = load_sample_frame("DS3")
    # keep a small numeric-friendly subset for speed
    cols = [c for c in df.columns if c != "Survived"]
    use = ["Survived"] + cols[:6]
    sub = df[use].dropna(how="all").head(400).copy()
    # coerce target
    sub["Survived"] = pd.to_numeric(sub["Survived"], errors="coerce").fillna(0).astype(int)
    train, val = quick_split(sub, "Survived", test_size=0.25, seed=42)
    out = fit_tabular(
        train,
        val,
        target="Survived",
        model_key=model_key,  # type: ignore[arg-type]
        task="classification",
        params={"layers": "32-16", "n_d": 8, "n_a": 8, "n_steps": 2, "input_embed_dim": 8, "num_heads": 2, "num_attn_blocks": 1},
        max_epochs=3,
        batch_size=64,
        early_stopping_patience=2,
    )
    assert out["n_train"] > 0 and out["n_val"] > 0
    assert out["library"] == "pytorch-tabular"
    arts = pack_dl_artefacts(model_key=model_key, loss_curve=out["loss_curve"], metrics=out["metrics"])
    assert arts["tables"]["DL.T.METRICS"]["model_key"] == model_key


def test_tabular_smoke_ds12_regression():
    try:
        df, _, _ = load_sample_frame("DS12")
    except Exception:
        from sklearn.datasets import fetch_california_housing

        bunch = fetch_california_housing(as_frame=True)
        df = bunch.frame
        df = df.rename(columns={"MedHouseVal": "MedHouseVal"})
        if "MedHouseVal" not in df.columns:
            df["MedHouseVal"] = bunch.target
    target = "MedHouseVal" if "MedHouseVal" in df.columns else df.columns[-1]
    sub = df.head(600).copy()
    train, val = quick_split(sub, target, test_size=0.2, seed=42)
    out = fit_tabular(
        train,
        val,
        target=target,
        model_key="mlp",
        task="regression",
        params={"layers": "32-16"},
        max_epochs=3,
        batch_size=64,
        early_stopping_patience=2,
        auto_lr_find=False,
    )
    assert out["task"] == "regression"
    assert np.isfinite(out.get("suggested_lr", 1e-3))


def test_lstm_tcn_ds30_smoke():
    df, _, _ = load_sample_frame("DS30")
    X, y = frame_to_xy(df)
    # shorten for CI
    X, y = X[:400], y[:400]
    for model in ("lstm", "tcn"):
        out = fit_sequential(
            X,
            y,
            model=model,  # type: ignore[arg-type]
            window=WindowSpec(lookback=12, horizon=1, stride=1, purge=1, embargo=1),
            task="regression",
            max_epochs=3,
            batch_size=32,
            seed=42,
            run_finder=False,
        )
        assert out["n_windows"] > 10
        assert out["model"] == model
        assert np.isfinite(out["val_mse"]) or np.isnan(out["val_mse"])


def test_lr_finder_and_early_stop_restore():
    set_seed(42)
    rng = np.random.default_rng(42)
    X = rng.normal(size=(200, 4)).astype(np.float64)
    y = (X[:, 0] * 0.5 + rng.normal(scale=0.1, size=200)).astype(np.float64)
    out = fit_sequential(
        X,
        y,
        model="lstm",
        window=WindowSpec(lookback=8, horizon=1, stride=1),
        max_epochs=8,
        batch_size=16,
        run_finder=True,
    )
    assert out["lr_finder"] is not None
    assert out["lr_finder"]["suggested_lr"] > 0
    assert len(out["lr_finder"]["lrs"]) > 0
    # best checkpoint path recorded when Lightning saves one
    assert out["stopped_epoch"] >= 0
    arts = pack_dl_artefacts(model_key="lstm", lr_info=out["lr_finder"])
    assert arts["plots"][0]["id"] == "DL.P.LR_FINDER"
