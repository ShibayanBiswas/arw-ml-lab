"""Pipeline graph HTML artefact."""

from __future__ import annotations

import pandas as pd
from labcore.preprocess.pipeline_graph import pipeline_graph_html
from labcore.preprocess.recipe import RecipeSpec, compile_recipe
from sklearn.pipeline import Pipeline


def test_pipeline_graph_html_contains_steps():
    X = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": ["x", "y", "x"]})
    pipe, _cols, _meta = compile_recipe(X, RecipeSpec())
    assert isinstance(pipe, Pipeline)
    out = pipeline_graph_html(pipe)
    assert out["id"] == "PRE.P.PIPELINE_GRAPH"
    assert "html" in out and len(out["html"]) > 50
    assert "Pipeline" in out["html"] or "pipeline" in out["html"].lower()
