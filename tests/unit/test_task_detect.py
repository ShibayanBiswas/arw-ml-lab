"""AC: DS22 monthly; DS30 daily business + OHLCV."""

from __future__ import annotations

from labcore.data.samples import load_sample_frame


def test_ds22_monthly() -> None:
    _df, task, _schema = load_sample_frame("DS22")
    assert task.sequential is True
    assert task.frequency == "monthly"
    assert task.family in {"timeseries", "supervised"}


def test_ds30_ohlcv_daily_business() -> None:
    _df, task, _schema = load_sample_frame("DS30")
    assert task.sequential is True
    assert task.ohlcv is not None
    assert set(task.ohlcv) >= {"open", "high", "low", "close"}
    assert task.frequency in {"daily_business", "daily", "B", "C"}
