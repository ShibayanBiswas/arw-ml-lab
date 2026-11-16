"""Reproduction notebook export (nbformat / §46.4)."""

from __future__ import annotations

import nbformat
from labcore.reports.notebook import build_reproduction_notebook, notebook_to_json


def test_reproduction_notebook_valid_and_embeds_facts():
    facts = {"cv_mean_roc_auc": 0.91, "seed": 42, "split": "oof"}
    nb = build_reproduction_notebook(
        title="DS3 LGBM",
        dataset_id="DS3",
        algorithm_key="lightgbm",
        seed=42,
        facts=facts,
    )
    nbformat.validate(nb)
    text = notebook_to_json(nb)
    assert "lightgbm" in text
    assert "DS3" in text
    # FACTS round-trip from the code cell
    code = nb.cells[1].source
    assert "FACTS = json.loads" in code
    assert "0.91" in code
    # Ensure JSON in notebook parses
    parsed = nbformat.reads(text, as_version=4)
    assert parsed.nbformat == 4
