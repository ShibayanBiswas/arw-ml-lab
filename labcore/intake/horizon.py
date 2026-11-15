"""Thin HorizonGuard — ARCHITECTURE §20 (Phase 1A: caps for intake proposals)."""

from __future__ import annotations

from typing import Any

# Step 1 frequency caps (recommended, hard_max, typical_m)
_FREQ_CAPS: dict[str, tuple[int, int, list[float]]] = {
    "T": (60, 1440, [60, 1440]),
    "min": (60, 1440, [60, 1440]),
    "H": (24, 168, [24, 168]),
    "h": (24, 168, [24, 168]),
    "D": (14, 90, [7, 365.25]),
    "B": (5, 21, [5, 21, 252]),
    "trading": (5, 21, [5, 21, 252]),
    "W": (13, 52, [52.18]),
    "M": (12, 36, [12]),
    "MS": (12, 36, [12]),
    "ME": (12, 36, [12]),
    "Q": (8, 16, [4]),
    "QS": (8, 16, [4]),
    "QE": (8, 16, [4]),
    "Y": (3, 10, [1]),
    "A": (3, 10, [1]),
}


def _norm_freq(freq: str | None) -> str:
    if not freq:
        return "D"
    f = freq.strip()
    if "trading" in f.lower() or "xnse" in f.lower() or "xbom" in f.lower():
        return "trading"
    # pandas aliases
    for key in ("MS", "ME", "QS", "QE", "min", "trading"):
        if f.startswith(key) or f == key:
            return key if key != "min" else "min"
    return f[0].upper() if f else "D"


def horizon_guard(
    n: int,
    freq: str | None,
    *,
    m: float | None = None,
    w: int = 4,
) -> dict[str, Any]:
    """Return h_default, h_max and reasons (no fabricated metrics beyond formulas)."""
    reasons: list[str] = []
    key = _norm_freq(freq)
    recommended, hard_max, typical_m = _FREQ_CAPS.get(key, (14, 90, [7.0]))
    m_use = float(m) if m is not None else float(typical_m[0])
    n_min_train = max(int(2 * m_use), 24)
    data_cap = max(1, (n - n_min_train) // (w + 1))
    third = max(1, n // 3)
    if n < 50:
        third = max(1, n // 4)
        reasons.append("n_lt_50_cap_n_over_4")
    h_max = min(hard_max, data_cap, third)
    if m_use > 0:
        h_max = min(h_max, max(1, int(2 * m_use)))
        reasons.append("seasonal_2m_cap")
    h_default = min(recommended, h_max)
    if m_use > 0:
        h_default = min(h_default, int(2 * m_use), h_max)
    reasons.append(f"freq_cap:{key}:{hard_max}")
    return {
        "h_default": int(h_default),
        "h_max": int(max(1, h_max)),
        "m": m_use,
        "reasons": reasons,
    }
