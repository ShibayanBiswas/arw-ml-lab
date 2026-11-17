"""FS16–FS18 thin AFML suitability (oneshot-c190)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from labcore.suitability.fs_checks import (
    check_fs16_structural_breaks,
    check_fs17_trend_scanning,
    check_fs18_meta_labelling,
    run_suitability,
)


def _series(n: int = 400, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    px = 100 * np.exp(0.0004 * t + 0.012 * rng.normal(size=n))
    return pd.DataFrame(
        {
            "date": pd.date_range("2018-01-01", periods=n, freq="B"),
            "close": px,
        }
    )


def test_fs16_info_not_deferred() -> None:
    r = check_fs16_structural_breaks(_series())
    assert r.code == "FS16"
    assert r.status == "INFO"
    assert "peak_sadf" in r.details


def test_fs17_share_computed() -> None:
    r = check_fs17_trend_scanning(_series())
    assert r.code == "FS17"
    assert r.status in {"PASS", "WARN", "FAIL"}
    assert "share_abs_t_gt_2" in r.details


def test_fs18_ma_cross_signals() -> None:
    r = check_fs18_meta_labelling(_series(n=600))
    assert r.code == "FS18"
    assert r.details["n_signals"] >= 0
    assert r.status in {"PASS", "WARN", "FAIL"}


def test_run_suitability_includes_fs16_18() -> None:
    report = run_suitability(_series(), time_col="date")
    by = {c["code"]: c for c in report["checks"]}
    assert by["FS16"]["status"] != "DEFERRED"
    assert by["FS17"]["status"] != "DEFERRED"
    assert by["FS18"]["status"] != "DEFERRED"
    assert report["methods"]["trend_scanning"]["status"] != "DEFERRED"
    assert report["methods"]["meta_labeling"]["status"] != "DEFERRED"
