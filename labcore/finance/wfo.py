"""Walk-forward optimisation planner (ARCHITECTURE §32) — thin Phase 5A.

Plans expanding/rolling windows with gap/purge/embargo counts. Full re-tune
loop lands when TradingLab + Optuna window driver are wired.
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd

Mode = Literal["expanding", "rolling"]


def plan_wfo_windows(
    n: int,
    *,
    n_windows: int = 5,
    l_is: int | None = None,
    l_oos: int | None = None,
    step: int | None = None,
    gap: int = 0,
    embargo: int = 0,
    mode: Mode = "expanding",
) -> dict[str, Any]:
    """Return a WFO window plan (indices only — no fabricated metrics)."""
    if n < 20:
        raise ValueError(f"n={n} too small for WFO")
    n_windows = int(np.clip(n_windows, 1, 10))
    l_oos_i = int(l_oos if l_oos is not None else max(5, n // (n_windows + 2)))
    l_is_i = int(l_is if l_is is not None else max(l_oos_i * 3, n // 3))
    step_i = int(step if step is not None else l_oos_i)
    gap_i = int(gap)
    embargo_i = int(embargo)

    windows: list[dict[str, Any]] = []
    # First OOS starts after minimum IS (+ gap)
    oos_start = l_is_i + gap_i
    while oos_start + l_oos_i <= n and len(windows) < n_windows:
        oos_end = oos_start + l_oos_i
        if mode == "expanding":
            is_start = 0
            is_end = oos_start - gap_i
        else:
            is_end = oos_start - gap_i
            is_start = max(0, is_end - l_is_i)
        n_purged = min(gap_i + embargo_i, max(0, is_end - is_start))
        if is_end - is_start - n_purged < 5:
            break
        windows.append(
            {
                "window": len(windows),
                "is_start": int(is_start),
                "is_end": int(is_end),
                "oos_start": int(oos_start),
                "oos_end": int(oos_end),
                "n_is": int(is_end - is_start - n_purged),
                "n_oos": int(oos_end - oos_start),
                "n_purged": int(n_purged),
                "n_embargo": int(embargo_i),
            }
        )
        oos_start += step_i

    return {
        "mode": mode,
        "n": n,
        "n_windows": len(windows),
        "l_is": l_is_i,
        "l_oos": l_oos_i,
        "step": step_i,
        "gap": gap_i,
        "embargo": embargo_i,
        "windows": windows,
        "seed": 42,
    }


def plan_wfo_from_index(
    index: pd.DatetimeIndex | pd.Index,
    **kwargs: Any,
) -> dict[str, Any]:
    plan = plan_wfo_windows(len(index), **kwargs)
    plan["index_dtype"] = str(getattr(index, "dtype", type(index)))
    return plan
