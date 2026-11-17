"""REE.P.STUDENTISED_INDEX — studentised residual vs row index."""

from __future__ import annotations

import numpy as np
from labcore.eval.regression.diagnostics import influence_table
from labcore.eval.regression.plots import plot_studentised_residuals


def test_studentised_index_matches_influence_table_and_bands():
    rng = np.random.default_rng(42)
    n = 60
    x = rng.normal(0, 1, n)
    y = 1.5 * x + rng.normal(0, 0.4, n)
    pred = 1.48 * x
    infl = influence_table(y, pred)
    stud = np.asarray([r["studentised_resid"] for r in infl["rows"]], dtype=float)

    art = plot_studentised_residuals(stud)
    assert art["id"] == "REE.P.STUDENTISED_INDEX"
    nums = art["numbers"]
    assert nums["n"] == n
    assert nums["bands"] == [-3.0, 3.0]
    np.testing.assert_allclose(nums["studentised_resid"], stud, atol=1e-9)
    np.testing.assert_allclose(nums["index"], np.arange(n), atol=1e-12)

    shapes = art["plotly"]["layout"]["shapes"]
    y_refs = sorted(s["y0"] for s in shapes if s.get("type") == "line")
    assert y_refs == [-3.0, 0.0, 3.0]