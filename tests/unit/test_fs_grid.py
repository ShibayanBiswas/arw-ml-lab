"""FS.P.GRID — §37.6 suitability parameter grid heatmap."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.suitability import (
    compute_suitability_parameter_grid,
    plot_suitability_grid,
    run_suitability,
)
from labcore.suitability.fs_checks import CUSUM_H_GRID, PT_SL_GRID, VERTICAL_BARRIER_GRID

ROOT = Path(__file__).resolve().parents[2]


def test_parameter_grid_has_36_cells_seed_42():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    grid = compute_suitability_parameter_grid(df, price_col="close", seed=42)
    assert grid["seed"] == 42
    assert grid["n_cells"] == 36
    assert len(grid["cells"]) == 36
    keys = {(tuple(c["pt_sl"]), c["vertical"], c["cusum_mult"]) for c in grid["cells"]}
    assert len(keys) == 36
    for pt in PT_SL_GRID:
        for v in VERTICAL_BARRIER_GRID:
            for h in CUSUM_H_GRID:
                row = next(
                    c
                    for c in grid["cells"]
                    if c["pt_sl"] == list(pt) and c["vertical"] == v and c["cusum_mult"] == h
                )
                assert "minority_share" in row or "error" in row


def test_default_cell_maximises_n_eff_among_minority_pass():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    grid = compute_suitability_parameter_grid(df, price_col="close", seed=42)
    default = grid["default_cell"]
    assert default is not None
    assert default["minority_share"] is not None
    eligible = [
        c
        for c in grid["cells"]
        if c.get("minority_share") is not None and float(c["minority_share"]) >= 0.15
    ]
    if eligible:
        best = max(eligible, key=lambda c: float(c.get("n_eff") or 0.0))
        assert default["pt_sl"] == best["pt_sl"]
        assert default["vertical"] == best["vertical"]
        assert default["cusum_mult"] == best["cusum_mult"]


def test_plot_suitability_grid_artefact():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    art = plot_suitability_grid(df, price_col="close", seed=42)
    assert art["id"] == "FS.P.GRID"
    assert art["numbers"]["n_cells"] == 36
    assert len(art["plotly"]["data"]) == 6  # 3 minority + 3 n_eff heatmaps
    report = run_suitability(df, time_col="date", asset="NIFTY")
    assert report["status"] in ("SUITABLE", "SUITABLE_WITH_CAUTIONS", "NOT_SUITABLE")