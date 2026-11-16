"""PV02/03/10/14/15 deepen tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from labcore.predict.template import sample_row_from_contract
from labcore.predict.validate import (
    load_predict_table,
    sniff_csv_meta,
    validate_predict_frame,
)
from labcore.train.run import TrainConfig, run_supervised_cv

ROOT = Path(__file__).resolve().parents[2]
TITANIC = ROOT / "data" / "samples" / "titanic.csv"


@pytest.fixture(scope="module")
def contract_bundle():
    df = pd.read_csv(TITANIC)
    result = run_supervised_cv(
        df,
        TrainConfig(
            task="binary",
            target="Survived",
            algorithm_keys=["clf.lgbm"],
            n_splits=3,
            seed=42,
            dataset_id="DS3",
            run_eval=False,
        ),
    )
    return result


def test_pv02_row_cap(contract_bundle):
    contract = contract_bundle["feature_contract"]
    names = contract_bundle["feature_names"]
    row = sample_row_from_contract(contract, feature_names=names)
    df = pd.DataFrame([row] * 10)
    report = validate_predict_frame(df, contract, required_names=names, max_rows=5)
    assert not report.ok
    assert any(i.code == "PV02" for i in report.blocking)


def test_pv03_duplicate_headers(contract_bundle):
    contract = contract_bundle["feature_contract"]
    names = contract_bundle["feature_names"]
    row = sample_row_from_contract(contract, feature_names=names)
    df = pd.DataFrame([row])
    # simulate duplicate via csv_meta
    report = validate_predict_frame(
        df,
        contract,
        required_names=names,
        csv_meta={"encoding": "utf-8", "delimiter": ",", "duplicate_headers": ["Age"]},
    )
    assert not report.ok
    assert any(i.code == "PV03" for i in report.blocking)


def test_pv14_constant_column(contract_bundle):
    contract = contract_bundle["feature_contract"]
    names = contract_bundle["feature_names"]
    rows = [sample_row_from_contract(contract, feature_names=names) for _ in range(8)]
    # force a numeric feature constant
    num = next(
        f["name"]
        for f in contract["features"]
        if f["name"] in names and f.get("kind") == "numeric"
    )
    for r in rows:
        r[num] = 1.0
    report = validate_predict_frame(pd.DataFrame(rows), contract, required_names=names)
    assert report.ok
    assert any(i.code == "PV14" for i in report.warnings)


def test_pv15_formula_sanitise(contract_bundle):
    contract = contract_bundle["feature_contract"]
    names = contract_bundle["feature_names"]
    cat = next(
        (
            f["name"]
            for f in contract["features"]
            if f["name"] in names and f.get("kind") == "categorical"
        ),
        None,
    )
    if cat is None:
        pytest.skip("no categorical feature")
    row = sample_row_from_contract(contract, feature_names=names)
    row[cat] = "=CMD()"
    report = validate_predict_frame(pd.DataFrame([row]), contract, required_names=names)
    assert report.ok
    assert any(i.code == "PV15" for i in report.info)
    assert report.coerced is not None
    assert str(report.coerced.iloc[0][cat]).startswith("'")


def test_pv10_ood_flag(contract_bundle):
    contract = contract_bundle["feature_contract"]
    names = contract_bundle["feature_names"]
    num_feat = next(
        f
        for f in contract["features"]
        if f["name"] in names and f.get("kind") == "numeric" and f.get("median") is not None
    )
    row = sample_row_from_contract(contract, feature_names=names)
    row[num_feat["name"]] = float(num_feat["median"]) + 1e6
    report = validate_predict_frame(pd.DataFrame([row]), contract, required_names=names)
    assert report.ok
    assert any(i.code == "PV10" for i in report.warnings)


def test_sniff_csv_and_load(tmp_path, contract_bundle):
    _ = contract_bundle
    p = tmp_path / "tiny.csv"
    p.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    meta = sniff_csv_meta(p.read_bytes())
    assert meta["delimiter"] == ","
    df, load_meta = load_predict_table(p)
    assert len(df) == 2
    assert load_meta["csv_meta"]["encoding"] in {"utf-8", "utf-8-sig"}
