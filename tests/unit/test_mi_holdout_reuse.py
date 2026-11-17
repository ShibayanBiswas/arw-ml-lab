"""MI.HOLDOUT.REUSE — ST-ML-04 hold-out reuse audit log (oneshot-c158)."""

from __future__ import annotations

import pandas as pd

from labcore.integrity.holdout_reuse import (
    ARTEFACT_ID,
    AUDIT_ACTION_HOLDOUT,
    HoldoutReuseRegistry,
    log_holdout_test_use,
    persist_holdout_audit_row,
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


def test_persist_holdout_audit_row_with_mock_executor() -> None:
    calls: list[tuple[str, tuple[object, ...]]] = []

    class _Cur:
        def fetchone(self) -> tuple[int]:
            return (99,)

    def execute(sql: str, params: tuple[object, ...]) -> _Cur:
        calls.append((sql, params))
        return _Cur()

    row = {
        "workspace_id": "00000000-0000-0000-0000-000000000010",
        "action": AUDIT_ACTION_HOLDOUT,
        "entity": "run",
        "entity_id": "run-x",
        "detail": {"use_count": 2, "is_reuse": True, "seed": 42},
    }
    assert persist_holdout_audit_row(row)["persisted"] is False
    assert persist_holdout_audit_row({**row, "workspace_id": "offline"}, execute=execute)[
        "reason"
    ] == "workspace_id_not_uuid"
    out = persist_holdout_audit_row(row, execute=execute)
    assert out["persisted"] is True
    assert out["audit_id"] == 99
    assert "audit_log" in calls[0][0]
    assert calls[0][1][1] == AUDIT_ACTION_HOLDOUT


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