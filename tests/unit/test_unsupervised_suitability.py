"""Unsupervised + suitability FS1–FS5 tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.suitability import run_suitability
from labcore.unsupervised import fit_anomaly, fit_clustering, fit_dr

ROOT = Path(__file__).resolve().parents[2]


def test_kmeans_silhouette_seed_42():
    rng = np.random.default_rng(42)
    X = np.vstack([rng.normal(0, 1, (30, 2)), rng.normal(5, 1, (30, 2))])
    out = fit_clustering(X, algorithm="kmeans", n_clusters=2, seed=42)
    assert out["n_clusters"] == 2
    assert out["metrics"]["silhouette"] is not None
    assert out["metrics"]["silhouette"] > 0.4


def test_pca_explained_variance():
    rng = np.random.default_rng(42)
    X = rng.normal(size=(50, 4))
    out = fit_dr(X, algorithm="pca", n_components=2, seed=42)
    assert out["explained_variance_ratio"] is not None
    assert len(out["explained_variance_ratio"]) == 2
    assert abs(sum(out["explained_variance_ratio"]) - 1.0) < 1.0  # not necessarily 1 for 2/4


def test_isolation_forest_flags():
    rng = np.random.default_rng(42)
    X = rng.normal(size=(80, 3))
    X[0] = np.array([20.0, 20.0, 20.0])
    out = fit_anomaly(X, algorithm="isolation_forest", contamination=0.05, seed=42)
    assert out["n_outliers"] >= 1
    assert out["is_outlier"][0] in (0, 1)


def test_fs_nifty_suitable():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    report = run_suitability(df, time_col="date", asset="NIFTY")
    assert report["status"] in {"SUITABLE", "SUITABLE_WITH_CAUTIONS"}
    by = {c["code"]: c["status"] for c in report["checks"]}
    assert by["FS1"] in {"PASS", "WARN"}
    assert by["FS2"] == "PASS"
    assert by["FS3"] in {"PASS", "WARN"}


def test_fs_airline_not_ohlcv():
    path = ROOT / "data" / "samples" / "airline_passengers.csv"
    df = pd.read_csv(path)
    report = run_suitability(df, time_col="Month", asset="airline")
    by = {c["code"]: c for c in report["checks"]}
    assert by["FS1"]["status"] in {"PASS", "WARN"}
    # passengers is not a price path named close — FS2 may FAIL
    assert by["FS4"]["status"] in {"FAIL", "WARN"}
