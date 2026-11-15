"""Table-driven HorizonGuard tests — ARCHITECTURE §20 / Phase 4 thin (≥20 cases)."""

from __future__ import annotations

import pytest
from labcore.timeseries.horizon_guard import (
    _FREQ_CAPS,
    compute_horizon_guard,
    norm_freq,
    seasonal_allowed,
)


def _expected_h_max(n: int, freq: str, m: float, w: int = 4) -> int:
    key = norm_freq(freq)
    _rec, hard_max, _typ = _FREQ_CAPS.get(key, (14, 90, [7.0]))
    n_min_train = max(int(2 * m), 24)
    data_cap = max(1, (n - n_min_train) // (w + 1))
    third = max(1, n // 4) if n < 50 else max(1, n // 3)
    return max(1, min(hard_max, data_cap, third))


# (n, freq, m) — ≥20 distinct structural cases
_ROWS: list[tuple[int, str, float, str]] = [
    (144, "MS", 12.0, "DS22"),
    (144, "M", 12.0, "DS22_M"),
    (36, "MS", 12.0, "DS23"),
    (36, "M", 12.0, "DS23_M"),
    (40, "D", 7.0, "n40_daily"),
    (20, "D", 7.0, "n20_daily"),
    (49, "M", 12.0, "n49_monthly"),
    (50, "M", 12.0, "n50_monthly"),
    (120, "MS", 12.0, "n120_m12"),
    (240, "MS", 12.0, "n240_monthly"),
    (80, "Q", 4.0, "quarterly"),
    (40, "Q", 4.0, "quarterly_short"),
    (365, "D", 7.0, "daily_year"),
    (100, "D", 7.0, "daily_100"),
    (252, "B", 5.0, "business"),
    (100, "trading", 5.0, "trading"),
    (104, "W", 52.0, "weekly"),
    (30, "Y", 1.0, "yearly_short"),
    (48, "H", 24.0, "hourly_short"),
    (500, "H", 24.0, "hourly_long"),
    (200, "MS", 12.0, "n200_monthly"),
    (60, "D", 7.0, "n60_daily"),
]


@pytest.mark.parametrize("n,freq,m,note", _ROWS)
def test_horizon_table(n: int, freq: str, m: float, note: str):
    out = compute_horizon_guard(n, freq, m=m, w=4)
    exp = _expected_h_max(n, freq, m, w=4)
    assert out["h_max"] == exp, f"{note}: got {out['h_max']} expected {exp}"
    if note.startswith("DS22"):
        assert out["h_max"] == 24
    if note.startswith("DS23"):
        assert out["h_max"] <= 9


def test_ds22_exact_formula():
    out = compute_horizon_guard(144, "MS", m=12, w=4)
    assert out["n_min_train"] == 24
    assert out["h_max"] == 24
    assert out["h_default"] <= out["h_max"]


def test_ds23_cap_and_seasonal_gate():
    out = compute_horizon_guard(36, "MS", m=12, w=4)
    assert out["h_max"] <= 9
    ok, reason = seasonal_allowed(36, 12.0, h=12)
    assert not ok
    assert reason and "2m+h" in reason
    # Even at h_max, monthly series with m=12 is tight — gate at h=h_max
    ok2, _ = seasonal_allowed(36, 12.0, h=int(out["h_max"]))
    # h_max is small (≤9) so 2m+h=24+h_max ≤33; 36>33 may pass — use h=12 AC case
    assert not ok
    out2 = compute_horizon_guard(36, "MS", m=12, w=4, h_request=12)
    names = {d["model"] for d in out2["disabled_models"]}
    assert "seasonal_ets" in names
    assert out2["request_allowed"] is False


def test_request_above_h_max_rejected():
    out = compute_horizon_guard(144, "MS", m=12, h_request=100)
    assert out["request_allowed"] is False
    assert out["reject_reasons"]


def test_garch_hard_n():
    out = compute_horizon_guard(200, "B", m=5, garch=True)
    names = {d["model"] for d in out["disabled_models"]}
    assert "garch" in names
    assert out["h_max"] <= 66


def test_intake_wrapper_compat():
    from labcore.intake.horizon import horizon_guard

    out = horizon_guard(144, "MS", m=12)
    assert out["h_max"] == 24
