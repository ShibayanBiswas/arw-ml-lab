"""Golden: DS3 / DS22 / DS30 EDA tables + plot groups."""

from __future__ import annotations

import pytest
from labcore.data.samples import load_sample_frame
from labcore.eda.plots import PLOT_GROUP_IDS
from labcore.eda.run import ALL_TABLE_IDS, run_eda


@pytest.mark.parametrize("ds_id", ["DS3", "DS22", "DS30"])
def test_eda_full_catalogue(ds_id: str) -> None:
    df, task, schema = load_sample_frame(ds_id)
    result = run_eda(df, schema=schema, task=task, seed=42, render_png=False)
    assert set(result.table_ids) == set(ALL_TABLE_IDS)
    assert len(ALL_TABLE_IDS) == 19
    # Plot groups present for applicable families
    expected_groups = {
        "univariate_numeric",
        "univariate_categorical",
        "missingness",
        "outliers",
        "bivariate",
        "multivariate",
        "quality",
    }
    if task.target:
        expected_groups.add("target")
    if task.sequential:
        expected_groups.add("sequential")
    # categorical empty placeholder still tags univariate_categorical
    got = set(result.plot_groups)
    assert expected_groups <= got, f"{ds_id}: missing groups {expected_groups - got}; got {got}"
    # Every artefact has numbers
    for a in result.artefacts:
        assert isinstance(a.numbers, dict)
        assert a.edu_key
    # PNG smoke on one plot when kaleido available (optional)
    one_plot = next(a for a in result.artefacts if a.kind == "plot")
    assert one_plot.plotly is not None


def test_ds3_missingness_numbers() -> None:
    df, task, schema = load_sample_frame("DS3")
    result = run_eda(df, schema=schema, task=task, seed=42, render_png=False)
    miss = next(a for a in result.artefacts if a.id == "EDA.T.MISSING")
    rows = {r["column"]: r for r in (miss.table or {}).get("rows", []) if "column" in r}
    assert "Age" in rows
    age_pct = float(rows["Age"]["missing_pct"])
    # Age ≈ 19.87%
    assert 19.0 <= age_pct <= 21.0
    assert "Cabin" in rows
    cabin_pct = float(rows["Cabin"]["missing_pct"])
    assert 75.0 <= cabin_pct <= 80.0


def test_plot_group_catalogue_complete() -> None:
    assert "sequential" in PLOT_GROUP_IDS
    assert len(PLOT_GROUP_IDS) >= 8
