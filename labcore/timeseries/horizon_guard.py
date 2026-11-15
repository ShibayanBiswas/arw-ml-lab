"""HorizonGuard — ARCHITECTURE §20 (canonical Phase 4 implementation).

Steps 1–2–4 are hard caps. Step 3 (empirical h*) is soft and applied after
backtest elsewhere; this module only returns the structural h_max / reasons.
"""

from __future__ import annotations

from typing import Any

# Step 1 — frequency caps: recommended, hard_max, typical_m
_FREQ_CAPS: dict[str, tuple[int, int, list[float]]] = {
    "T": (60, 1440, [60.0, 1440.0]),
    "min": (60, 1440, [60.0, 1440.0]),
    "H": (24, 168, [24.0, 168.0]),
    "h": (24, 168, [24.0, 168.0]),
    "D": (14, 90, [7.0, 365.25]),
    "B": (5, 21, [5.0, 21.0, 252.0]),
    "trading": (5, 21, [5.0, 21.0, 252.0]),
    "W": (13, 52, [52.18]),
    "M": (12, 36, [12.0]),
    "MS": (12, 36, [12.0]),
    "ME": (12, 36, [12.0]),
    "Q": (8, 16, [4.0]),
    "QS": (8, 16, [4.0]),
    "QE": (8, 16, [4.0]),
    "Y": (3, 10, [1.0]),
    "A": (3, 10, [1.0]),
}


def norm_freq(freq: str | None) -> str:
    if not freq:
        return "D"
    f = freq.strip()
    low = f.lower()
    if "trading" in low or "xnse" in low or "xbom" in low:
        return "trading"
    for key in ("MS", "ME", "QS", "QE", "min", "trading"):
        if f == key or f.startswith(key):
            return key if key != "min" else "min"
    return f[0].upper() if f else "D"


def seasonal_allowed(n: int, m: float, h: int) -> tuple[bool, str | None]:
    """ETS/Holt-Winters / seasonal SARIMA gate: n ≥ 2m + h (§20 Step 2).

    Uses strict inequality on the boundary so n == 2m+h is insufficient
    (need one extra observation beyond the textbook minimum for fitting).
    """
    need = int(2 * m + h)
    if n <= need:
        return False, f"n={n} < 2m+h={need} (need n≥2m+h+1)"
    return True, None


def sarima_allowed(
    n: int,
    h: int,
    *,
    m: int = 12,
    order: tuple[int, int, int] = (0, 1, 1),
    seasonal_order: tuple[int, int, int, int] = (0, 1, 1, 12),
) -> tuple[bool, str | None]:
    """SARIMA needs n ≥ p+q+P+Q+d+m·D+1 + h (Hyndman & Kostenko)."""
    p, d, q = order
    P, D, Q, m_s = seasonal_order
    m_use = m_s if m_s else m
    need = p + q + P + Q + d + m_use * D + 1 + h
    if n < need:
        return False, f"n={n} < SARIMA_min+h={need}"
    return True, None


def compute_horizon_guard(
    n: int,
    freq: str | None,
    *,
    m: float | None = None,
    w: int = 4,
    h_request: int | None = None,
    model_family: str | None = None,
    garch: bool = False,
    deep_learning: bool = False,
) -> dict[str, Any]:
    """Return h_default, h_max, reasons, disabled_models (no fabricated metrics)."""
    reasons: list[str] = []
    caps_detail: dict[str, int] = {}
    key = norm_freq(freq)
    recommended, hard_max, typical_m = _FREQ_CAPS.get(key, (14, 90, [7.0]))
    m_use = float(m) if m is not None else float(typical_m[0])
    n_min_train = max(int(2 * m_use), 24)

    data_cap = max(1, (n - n_min_train) // (w + 1))
    caps_detail["data_feasibility"] = int(data_cap)
    reasons.append(f"data_cap:(n-n_min_train)/(W+1)={data_cap}")

    if n < 50:
        third = max(1, n // 4)
        reasons.append("n_lt_50_cap_n_over_4")
        caps_detail["n_fraction"] = int(third)
    else:
        third = max(1, n // 3)
        reasons.append("n_over_3_cap")
        caps_detail["n_fraction"] = int(third)

    caps_detail["freq_hard"] = int(hard_max)
    reasons.append(f"freq_cap:{key}:{hard_max}")

    h_max = min(hard_max, data_cap, third)

    # Model-family hard caps (§20 Step 2)
    disabled: list[dict[str, str]] = []
    h_for_gate = int(h_request) if h_request is not None else int(h_max)

    ok_seas, reason_seas = seasonal_allowed(n, m_use, h_for_gate)
    if not ok_seas:
        disabled.append({"model": "seasonal_ets", "reason": reason_seas or "seasonal_gate"})
        disabled.append({"model": "holt_winters", "reason": reason_seas or "seasonal_gate"})
        reasons.append(f"seasonal_disabled:{reason_seas}")

    ok_sarima, reason_sarima = sarima_allowed(n, h_for_gate, m=int(m_use) if m_use else 12)
    if not ok_sarima:
        disabled.append({"model": "sarima", "reason": reason_sarima or "sarima_gate"})
        reasons.append(f"sarima_disabled:{reason_sarima}")

    if garch or (model_family or "").lower() == "garch":
        if n < 250:
            disabled.append({"model": "garch", "reason": f"n={n} < 250 hard"})
            reasons.append("garch_n_lt_250")
            h_max = min(h_max, 66)
        elif n < 500:
            reasons.append("garch_n_lt_500_recommended")
        h_max = min(h_max, 66)
        caps_detail["garch"] = 66

    dl_family = (model_family or "").lower() in {"dl", "neuralforecast", "nhits"}
    if (deep_learning or dl_family) and n < 300:
        # Thin stub: grey-out when n is small (< 300 effective windows heuristic)
        disabled.append(
            {
                "model": "deep_learning",
                "reason": f"n={n} < 300 recommended windows for DL",
            }
        )
        reasons.append("dl_greyed_n_lt_300")

    h_max = int(max(1, h_max))
    h_default = min(recommended, h_max)
    if m_use > 0:
        h_default = min(h_default, max(1, int(2 * m_use)), h_max)
        reasons.append("h_default_capped_2m")

    out: dict[str, Any] = {
        "h_default": int(h_default),
        "h_max": h_max,
        "m": m_use,
        "n": int(n),
        "freq": key,
        "n_min_train": int(n_min_train),
        "w": int(w),
        "recommended_freq": int(recommended),
        "reasons": reasons,
        "caps": caps_detail,
        "disabled_models": disabled,
    }
    if h_request is not None:
        out["h_request"] = int(h_request)
        out["request_allowed"] = int(h_request) <= h_max
        if int(h_request) > h_max:
            out["reject_reasons"] = [
                f"h_request={h_request} > h_max={h_max}",
                *reasons,
            ]
    return out


# Back-compat name used by intake
def horizon_guard(
    n: int,
    freq: str | None,
    *,
    m: float | None = None,
    w: int = 4,
) -> dict[str, Any]:
    return compute_horizon_guard(n, freq, m=m, w=w)
