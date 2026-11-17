"""Predict batch Idempotency-Key — oneshot-c250."""

from __future__ import annotations

from labcore.predict.idempotency_contract import (
    ARTEFACT_ID,
    assert_job_store_idempotency_runtime,
    assert_predict_batch_idempotency_wiring,
)


def test_predict_batch_idempotency_wiring() -> None:
    out = assert_predict_batch_idempotency_wiring()
    assert out["id"] == ARTEFACT_ID


def test_job_store_idempotency_runtime() -> None:
    out = assert_job_store_idempotency_runtime(seed=42)
    assert out["reuse"] is True
    assert out["distinct"] is True
