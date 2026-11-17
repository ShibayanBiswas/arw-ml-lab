"""MI.HOLDOUT.REUSE — ST-ML-04 hold-out reuse audit log (oneshot-c158)."""

from __future__ import annotations

import pandas as pd

from labcore.integrity.holdout_reuse import (
    ARTEFACT_ID,
    AUDIT_ACTION_HOLDOUT,
    HoldoutReuseRegistry,
    log_holdout_test_use,
)
from labcore.train.run import TrainConfig, run_supervised_cv


def test_first_use_then_reuse_counts_and_audit() -> None:
    reg = HoldoutReuseRegistry()
    first = log_holdout_test_use(
        reg,
        workspace_id="00000000-0000-0000-0000-000000000010",
        run_id="run-a",
        dataset_id="DS1",
        test_size=0.2,
        seed=42,
    )
    assert first["use_count"] == 1
    assert first["is_reuse"] is False
    assert first["audit_row"]["action"] == AUDIT_ACTION_HOLDOUT
    assert first["audit_row"]["detail"]["ui_label"] == "test set used 1 time"

    second = log_holdout_test_use(
        reg,
        workspace_id="00000000-0000-0000-0000-000000000010",
        run_id="run-b",
        dataset_id="DS1",
        test_size=0.2,
        seed=42,
    )
    assert second["use_count"] == 2
    assert second["is_reuse"] is True
    assert second["id"] == ARTEFACT_ID


def test_run_supervised_cv_includes_holdout_reuse() -> None:
    rng = __import__("numpy").random.default_rng(42)
    n = 120
    df = pd.DataFrame(
        {
            "x1": rng.normal(size=n),
            "x2": rng.normal(size=n),
            "y": rng.integers(0, 2, size=n),
        }
    )
    cfg = TrainConfig(target="y", task="binary", dataset_id="SYN-HOLDOUT", algorithm_keys=["clf.logistic"])
    out = run_supervised_cv(df, cfg, spy_fit_counts={})
    hr = out["holdout_reuse"]
    assert hr["use_count"] >= 1
    assert hr["seed"] == 42
    assert hr["audit_row"]["detail"]["split"] == "holdout"