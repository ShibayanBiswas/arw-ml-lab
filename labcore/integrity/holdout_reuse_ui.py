"""MI.HOLDOUT.REUSE UI label helper — ST-ML-04 (oneshot-c196)."""

from __future__ import annotations

from typing import Any

from labcore.integrity.holdout_reuse import (
    ARTEFACT_ID,
    HoldoutReuseRegistry,
    log_holdout_test_use,
)


def holdout_reuse_badge(manifest: dict[str, Any]) -> dict[str, Any]:
    """Shape the train-result holdout_reuse blob for the FE badge."""
    use_count = int(manifest.get("use_count") or 0)
    is_reuse = bool(manifest.get("is_reuse"))
    return {
        "artefact": ARTEFACT_ID,
        "label": f"test set used {use_count} time{'s' if use_count != 1 else ''}",
        "use_count": use_count,
        "is_reuse": is_reuse,
        "tone": "warn" if is_reuse else "info",
        "seed": manifest.get("seed", 42),
    }


def assert_holdout_ui_contract(*, seed: int = 42) -> dict[str, object]:
    reg = HoldoutReuseRegistry()
    first = log_holdout_test_use(
        reg,
        workspace_id="offline",
        run_id="ui-1",
        dataset_id="holdout-ui",
        test_size=0.2,
        seed=seed,
    )
    b1 = holdout_reuse_badge(first)
    if b1["is_reuse"] or b1["tone"] != "info":
        raise AssertionError("first use must be info")
    second = log_holdout_test_use(
        reg,
        workspace_id="offline",
        run_id="ui-2",
        dataset_id="holdout-ui",
        test_size=0.2,
        seed=seed,
    )
    b2 = holdout_reuse_badge(second)
    if not b2["is_reuse"] or b2["tone"] != "warn":
        raise AssertionError("reuse must warn")
    return {"first": b1, "second": b2, "seed": seed}
