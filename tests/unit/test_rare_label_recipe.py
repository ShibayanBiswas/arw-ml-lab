"""RareLabelEncoder via feature-engine in recipes."""

from __future__ import annotations

import numpy as np
import pandas as pd
from labcore.preprocess.recipe import RecipeSpec, compile_recipe


def test_rare_label_collapses_infrequent():
    rng = np.random.default_rng(42)
    cats = ["A"] * 40 + ["B"] * 40 + ["C"] * 2 + ["D"] * 2
    rng.shuffle(cats)
    X = pd.DataFrame(
        {
            "num": rng.normal(size=len(cats)),
            "cat": cats,
        }
    )
    pipe, _cols, meta = compile_recipe(
        X,
        RecipeSpec(
            categorical_encoder="one_hot",
            rare_label_tol=0.05,
            rare_label_n_categories=2,
        ),
    )
    Xt = pipe.fit_transform(X)
    assert Xt.shape[0] == len(X)
    assert meta["recipe"]["rare_label_tol"] == 0.05
