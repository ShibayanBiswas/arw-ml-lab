"""FE predict batch Idempotency-Key header — oneshot-c251."""

from labcore.predict.fe_idempotency_contract import (
    ARTEFACT_ID,
    assert_fe_predict_batch_idempotency_header,
)


def test_fe_predict_batch_idempotency_header() -> None:
    out = assert_fe_predict_batch_idempotency_header()
    assert out["id"] == ARTEFACT_ID
    assert out["ok"] is True
