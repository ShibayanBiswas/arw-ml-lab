"""OPS.CONTABO.CONCURRENCY — oneshot-c205."""

from labcore.ops.contabo_concurrency import assert_contabo_concurrency_contract


def test_contabo_train_concurrency_one() -> None:
    m = assert_contabo_concurrency_contract()
    assert m["id"] == "OPS.CONTABO.CONCURRENCY"
    assert m["check"]["concurrency"] == "1"
