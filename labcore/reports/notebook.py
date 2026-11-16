"""Reproduction notebook export via nbformat (ARCHITECTURE §46.4 / ST-UX-02)."""

from __future__ import annotations

import json
from typing import Any


def build_reproduction_notebook(
    *,
    title: str,
    dataset_id: str,
    algorithm_key: str,
    seed: int = 42,
    facts: dict[str, Any] | None = None,
    pip_pins: list[str] | None = None,
) -> dict[str, Any]:
    """
    Return an nbformat v4 notebook dict (not executed).

    Cells document how to re-run a lab experiment; FACTS are embedded as JSON
    for audit — never invented metrics.
    """
    import nbformat
    from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

    facts = facts or {}
    pins = pip_pins or ["scikit-learn", "pandas", "numpy"]
    nb = new_notebook(
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "lab": {
                "dataset_id": dataset_id,
                "algorithm_key": algorithm_key,
                "seed": seed,
            },
        }
    )
    nb.cells.append(
        new_markdown_cell(
            f"# {title}\n\n"
            f"Reproduction bundle for `{algorithm_key}` on `{dataset_id}` "
            f"(seed **{seed}**). Numbers below are copied from FACTS."
        )
    )
    facts_literal = json.dumps(facts, sort_keys=True)
    nb.cells.append(
        new_code_cell(
            "import json\n"
            f"SEED = {seed}\n"
            f"DATASET_ID = {dataset_id!r}\n"
            f"ALGORITHM_KEY = {algorithm_key!r}\n"
            f"FACTS = json.loads({facts_literal!r})\n"
            f"PIP_PINS = {pins!r}\n"
            "print(DATASET_ID, ALGORITHM_KEY, SEED)\n"
            "print('facts keys', sorted(FACTS.keys())[:20])\n"
        )
    )
    nb.cells.append(
        new_markdown_cell(
            "## Next steps\n"
            "1. Install pins from `PIP_PINS` / `backend/requirements`.\n"
            "2. Reload the dataset and feature contract from the lab store.\n"
            "3. Fit with the same seed; do not use the hold-out test for selection."
        )
    )
    # Validate structure
    nbformat.validate(nb)
    return nb


def notebook_to_json(nb: dict[str, Any]) -> str:
    import nbformat

    return nbformat.writes(nb) if not isinstance(nb, str) else nb
