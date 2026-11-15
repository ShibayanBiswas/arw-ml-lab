"""Phase 3A thin Prediction Studio: PV core, template, DS3 parity."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from labcore.predict.contract import validate_feature_contract
from labcore.predict.score import predict_batch, predict_single
from labcore.predict.template import (
    sample_row_from_contract,
    template_csv_bytes,
)
from labcore.predict.validate import validate_predict_frame
from labcore.train.run import TrainConfig, run_supervised_cv

ROOT = Path(__file__).resolve().parents[2]
TITANIC = ROOT / "data" / "samples" / "titanic.csv"
TITANIC_PREDICT = ROOT / "data" / "samples" / "predict" / "titanic_predict.csv"


@pytest.fixture(scope="module")
def ds3_train():
    df = pd.read_csv(TITANIC)
    cfg = TrainConfig(
        task="binary",
        target="Survived",
        algorithm_keys=["clf.lgbm"],
        n_splits=3,
        seed=42,
        dataset_id="DS3",
        run_eval=True,
    )
    result = run_supervised_cv(df, cfg)
    assert result["champion_pipeline"] is not None
    assert result["feature_contract"]
    errs = validate_feature_contract(result["feature_contract"])
    assert errs == [], errs
    return result


def test_pv04_missing_column(ds3_train):
    contract = ds3_train["feature_contract"]
    names = ds3_train["feature_names"]
    row = sample_row_from_contract(contract, feature_names=names)
    df = pd.DataFrame([{k: v for k, v in row.items() if k != names[0]}])
    report = validate_predict_frame(df, contract, required_names=names)
    assert not report.ok
    assert any(i.code == "PV04" for i in report.blocking)


def test_pv05_extra_and_target(ds3_train):
    contract = ds3_train["feature_contract"]
    names = ds3_train["feature_names"]
    row = sample_row_from_contract(contract, feature_names=names)
    row["Survived"] = 1
    row["extra_col"] = "x"
    report = validate_predict_frame(pd.DataFrame([row]), contract, required_names=names)
    assert report.ok
    codes = {i.code for i in report.warnings}
    assert "PV05" in codes


def test_pv06_dtype_block(ds3_train):
    contract = ds3_train["feature_contract"]
    names = ds3_train["feature_names"]
    # Find a numeric feature
    num = next(
        f["name"] for f in contract["features"] if f["name"] in names and f.get("kind") == "numeric"
    )
    rows = []
    for i in range(20):
        row = sample_row_from_contract(contract, feature_names=names)
        row[num] = "not-a-number" if i < 3 else row[num]
        rows.append(row)
    # 3/20 = 15% > 5% → block
    report = validate_predict_frame(pd.DataFrame(rows), contract, required_names=names)
    assert not report.ok
    assert any(i.code == "PV06" and i.severity == "block" for i in report.blocking)


def test_pv08_range_warn(ds3_train):
    contract = ds3_train["feature_contract"]
    names = ds3_train["feature_names"]
    num_feat = next(
        f
        for f in contract["features"]
        if f["name"] in names and f.get("kind") == "numeric" and f.get("max") is not None
    )
    row = sample_row_from_contract(contract, feature_names=names)
    row[num_feat["name"]] = float(num_feat["max"]) + abs(float(num_feat["max"]) or 1) * 10 + 100
    report = validate_predict_frame(pd.DataFrame([row]), contract, required_names=names)
    assert report.ok
    assert any(i.code == "PV08" for i in report.warnings)


def test_ds3_template_roundtrip_and_predict_sample(ds3_train):
    contract = ds3_train["feature_contract"]
    names = ds3_train["feature_names"]
    pipe = ds3_train["champion_pipeline"]
    raw = template_csv_bytes(contract, feature_names=names)
    from io import BytesIO

    tmpl = pd.read_csv(BytesIO(raw))
    assert list(tmpl.columns) == names
    report_t = validate_predict_frame(tmpl, contract, required_names=names)
    assert report_t.ok

    pred_df = pd.read_csv(TITANIC_PREDICT)
    report = validate_predict_frame(
        pred_df, contract, required_names=names, source_name="titanic_predict.csv"
    )
    assert report.ok, report.to_dict()
    assert not report.blocking
    scored = predict_batch(pipe, report.coerced, feature_names=names)
    assert scored["refit"] is False
    assert scored["n_rows"] == len(pred_df)
    assert len(scored["predictions"]) == len(pred_df)


def test_single_batch_parity_30_rows(ds3_train):
    contract = ds3_train["feature_contract"]
    names = ds3_train["feature_names"]
    pipe = ds3_train["champion_pipeline"]
    pred_df = pd.read_csv(TITANIC_PREDICT).head(30)
    report = validate_predict_frame(pred_df, contract, required_names=names)
    assert report.ok and report.coerced is not None
    X = report.coerced
    batch = predict_batch(pipe, X, feature_names=names)
    singles = [
        predict_single(pipe, X.iloc[i].to_dict(), feature_names=names)["prediction"]
        for i in range(len(X))
    ]
    b = np.asarray(batch["predictions"], dtype=float)
    s = np.asarray(singles, dtype=float)
    # classification labels may be 0/1 ints
    np.testing.assert_allclose(b, s, atol=1e-9, rtol=0)


def test_contract_still_schema_valid_after_train(ds3_train):
    errs = validate_feature_contract(ds3_train["feature_contract"])
    assert errs == []
    from labcore.predict.contract import assert_no_identifier_values

    assert_no_identifier_values(ds3_train["feature_contract"])
