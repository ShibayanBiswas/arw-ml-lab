"""Pipeline graph HTML via sklearn estimator HTML repr (ARCHITECTURE preprocess UI)."""

from __future__ import annotations

from typing import Any


def pipeline_graph_html(estimator: Any) -> dict[str, Any]:
    """
    Return sklearn's interactive HTML diagram for a fitted/unfitted Pipeline.

    Uses ``sklearn.utils._estimator_html_repr`` (same as Jupyter display).
    """
    from sklearn.utils import estimator_html_repr

    html = estimator_html_repr(estimator)
    return {
        "id": "PRE.P.PIPELINE_GRAPH",
        "html": html,
        "estimator_type": type(estimator).__name__,
    }
