"""OPS.SSE.PROGRESS — oneshot-c211."""

from labcore.ops.sse_progress import assert_sse_progress_contract


def test_sse_progress_contract() -> None:
    m = assert_sse_progress_contract()
    assert m["id"] == "OPS.SSE.PROGRESS"
    assert len(m["checks"]) == 3
