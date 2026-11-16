"""MI-11 — drop constant / all-NaN columns with warning (§46.1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from labcore.preprocess.recipe import drop_constant_columns


def test_drop_all_nan_and_constant():
    df = pd.DataFrame(
        {
            "keep": [1.0, 2.0, 3.0],
            "all_nan": [np.nan, np.nan, np.nan],
            "const": [7, 7, 7],
        }
    )
    out, dropped = drop_constant_columns(df)
    assert list(out.columns) == ["keep"]
    assert set(dropped) == {"all_nan", "const"}
