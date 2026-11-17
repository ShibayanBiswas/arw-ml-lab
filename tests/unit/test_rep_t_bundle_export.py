"""REP.T.BUNDLE — ST-UX-02 reproduction zip export (oneshot-c178)."""

from __future__ import annotations

import json
import zipfile
from io import BytesIO

import nbformat

from labcore.reports.reproduction_bundle import (
    ARTEFACT_ID,
    LAB_TIMEZONE,
    STRESS_ID,
    build_reproduction_bundle_manifest,
    build_reproduction_bundle_zip,
    bundle_to_base64,
)


def test_reproduction_bundle_manifest_seed_42() -> None:
    manifest = build_reproduction_bundle_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["stress_test"] == STRESS_ID
    assert manifest["seed"] == 42
    assert manifest["timezone"] == LAB_TIMEZONE
    assert len(manifest["checks"]) == 1


def test_reproduction_bundle_zip_notebook_validates() -> None:
    blob = build_reproduction_bundle_zip(
        title="DS3",
        dataset_id="DS3",
        algorithm_key="clf.logistic",
        seed=42,
        facts={"cv_mean_balanced_accuracy": 0.71},
    )
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        manifest = json.loads(zf.read("manifest.json"))
        assert manifest["data_sha256"]
        nb = nbformat.reads(zf.read("notebook/reproduction.ipynb").decode("utf-8"), as_version=4)
    nbformat.validate(nb)


def test_bundle_base64_roundtrip() -> None:
    blob = build_reproduction_bundle_zip(
        title="t",
        dataset_id="DS1",
        algorithm_key="x",
        seed=42,
    )
    enc = bundle_to_base64(blob)
    assert enc
    assert blob[:2] == b"PK"