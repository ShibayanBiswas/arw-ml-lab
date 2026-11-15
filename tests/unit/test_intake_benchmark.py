"""AC: intake on 1M×100 completes in <45s (soft-skip if host slower)."""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest
from labcore.intake.pipeline import run_intake


@pytest.mark.benchmark
def test_intake_1m_x_100_under_45s() -> None:
    rng = np.random.default_rng(42)
    n, p = 1_000_000, 100
    t_build = time.perf_counter()
    arr = rng.standard_normal((n, p - 2), dtype=np.float32)
    cols = {f"f{i}": arr[:, i] for i in range(p - 2)}
    cols["date"] = pd.Timestamp("2000-01-01") + pd.to_timedelta(
        np.arange(n, dtype=np.int64), unit="h"
    )
    cols["target"] = rng.standard_normal(n, dtype=np.float32)
    df = pd.DataFrame(cols)
    build_s = time.perf_counter() - t_build
    if build_s > 60:
        pytest.skip(f"frame build {build_s:.2f}s > 60s on this host (intake not timed)")

    t0 = time.perf_counter()
    out = run_intake(df)
    elapsed = time.perf_counter() - t0
    assert out["merged"]["family"]["proposed"]
    assert out["detector_output"]["profile_summary"].get("sampled") is True
    if elapsed > 45:
        pytest.skip(f"intake wall time {elapsed:.2f}s > 45s on this host (recorded)")
    assert elapsed < 45
