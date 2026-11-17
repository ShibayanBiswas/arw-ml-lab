"""LAB_MAX_ROWS enqueue guard — Contabo §12 / OPS-01 (oneshot-c216)."""

from __future__ import annotations

from typing import Any

ARTEFACT_ID = "OPS.MAX_ROWS"


def guard_max_rows(*, n_rows: int, lab_max_rows: int) -> dict[str, Any]:
    """Return a decision dict; ``refused`` True when over the configured cap."""
    cap = int(lab_max_rows)
    n = int(n_rows)
    if n > cap:
        return {
            "refused": True,
            "artefact": ARTEFACT_ID,
            "n_rows": n,
            "lab_max_rows": cap,
            "message": (
                f"dataset has {n:,} rows; LAB_MAX_ROWS={cap:,}. "
                "Sample or raise the limit after load tests (Contabo §12)."
            ),
        }
    return {
        "refused": False,
        "artefact": ARTEFACT_ID,
        "n_rows": n,
        "lab_max_rows": cap,
    }
