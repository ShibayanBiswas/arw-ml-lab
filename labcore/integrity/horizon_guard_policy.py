"""HorizonGuard policy helpers — MI-17 (ARCHITECTURE §46.1, §20)."""

from __future__ import annotations

from typing import Any

from labcore.timeseries.horizon_guard import compute_horizon_guard

MI17_RULE = "MI-17"
LAB_DEFAULT_SEED = 42


def horizon_request_allowed(
    n: int,
    freq: str | None,
    h_request: int,
    *,
    m: float | None = None,
    w: int = 4,
) -> bool:
    """True when ``h_request`` is within structural ``h_max`` (PV13 / batch guard)."""
    guard = compute_horizon_guard(n, freq, m=m, w=w, h_request=h_request)
    return bool(guard.get("request_allowed", h_request <= int(guard["h_max"])))


def horizon_reject_reasons(
    n: int,
    freq: str | None,
    h_request: int,
    *,
    m: float | None = None,
    w: int = 4,
) -> list[str]:
    """Rejection reasons when ``h_request`` exceeds ``h_max`` (empty when allowed)."""
    guard = compute_horizon_guard(n, freq, m=m, w=w, h_request=h_request)
    if guard.get("request_allowed", h_request <= int(guard["h_max"])):
        return []
    return list(guard.get("reject_reasons") or [f"h_request={h_request} > h_max={guard['h_max']}"])