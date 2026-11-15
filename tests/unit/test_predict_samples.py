"""Checks the Prediction Studio sample files (ARCHITECTURE §45.9).

Run: pytest tests/unit/test_predict_samples.py   (needs pandas + jsonschema; no network)
"""

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
PRED = ROOT / "data" / "samples" / "predict"
MAN = json.loads((PRED / "predict_manifest.json").read_text())["files"]
SCHEMA = json.loads((ROOT / "docs" / "contracts" / "feature_contract.schema.json").read_text())
FORECAST_CAPS = {
    "DS22": 24,
    "DS23": 9,
    "DS24": 30,
    "DS25": 24,
    "DS26": 24,
    "DS27": 16,
    "DS28": 48,
    "DS29": 48,
}


def test_every_dataset_has_a_sample():
    assert {r["id"] for r in MAN} == {f"DS{i}" for i in range(1, 34)}


def test_presets_reference_existing_samples():
    for p in (ROOT / "data" / "samples" / "presets").glob("ds*.yaml"):
        refs = [
            l.split(":", 1)[1].strip() if ":" in l else l.strip()[2:]
            for l in p.read_text().splitlines()
            if l.startswith(("predict_sample:", "feature_contract:", "  - "))
        ]
        assert refs, f"{p.name} has no predict sample"
        for r in refs:
            assert (ROOT / r).exists(), f"{p.name}: {r} missing"


@pytest.mark.parametrize("entry", MAN, ids=[r["name"] for r in MAN])
def test_sample_matches_contract(entry):
    df = pd.read_csv(ROOT / entry["file"], dtype=str, keep_default_na=False)
    con = json.loads((ROOT / entry["contract"]).read_text())
    import jsonschema

    jsonschema.validate(con, SCHEMA)
    if entry["id"] in FORECAST_CAPS:
        assert len(df) == FORECAST_CAPS[entry["id"]]
        assert con["horizon_max"] is None or len(df) <= con["horizon_max"] or entry["id"] == "DS29"
    else:
        assert 20 <= len(df) <= 50
    target = con["target"]
    if target and target in df.columns:
        pytest.fail(f"target {target!r} present in {entry['file']}")
    expected = list(con["id_columns"]) + [f["name"] for f in con["features"]]
    assert list(df.columns) == expected
    for f in con["features"]:
        if f["kind"] == "categorical" and f.get("categories") and not f.get("categories_truncated"):
            unseen = set(df[f["name"]]) - set(f["categories"]) - {""}
            # unseen categories are allowed in a hold-out but must be rare (they are flagged at predict time)
            assert len(unseen) <= max(3, len(df) // 5), (f["name"], unseen)


def test_no_identifier_values_stored_in_contracts():
    for entry in MAN:
        con = json.loads((ROOT / entry["contract"]).read_text())
        for f in con["features"]:
            if f["kind"] == "identifier_like":
                assert not f.get("categories"), (
                    f"{entry['name']}:{f['name']} stores identifier values"
                )
