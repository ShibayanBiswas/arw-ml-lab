"""KNNImputer recipe path (ARCHITECTURE preprocess catalogue)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from labcore.preprocess.recipe import RecipeSpec, compile_recipe
from sklearn.pipeline import Pipeline


def test_knn_imputer_fills_numeric_nan():
    rng = np.random.default_rng(42)
    X = pd.DataFrame(
        {
            "a": [1.0, np.nan, 3.0, 4.0, 5.0],
            "b": rng.normal(size=5),
            "c": ["x", "y", "x", "y", "x"],
        }
    )
    pipe, cols, meta = compile_recipe(X, RecipeSpec(numeric_imputer="knn", knn_n_neighbors=2))
    assert isinstance(pipe, Pipeline)
    Xt = pipe.fit_transform(X)
    assert not np.isnan(np.asarray(Xt, dtype=float)).any()
    assert "a" in cols or any("a" in str(c) for c in cols) or Xt.shape[1] >= 2
    _ = meta
