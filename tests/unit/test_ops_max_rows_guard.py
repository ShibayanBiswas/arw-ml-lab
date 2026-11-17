"""OPS.MAX_ROWS — oneshot-c216."""

from labcore.ops.max_rows_guard import guard_max_rows


def test_under_cap_allows() -> None:
    d = guard_max_rows(n_rows=100, lab_max_rows=2_000_000)
    assert d["refused"] is False


def test_over_cap_refuses() -> None:
    d = guard_max_rows(n_rows=2_000_001, lab_max_rows=2_000_000)
    assert d["refused"] is True
    assert "LAB_MAX_ROWS" in d["message"]
