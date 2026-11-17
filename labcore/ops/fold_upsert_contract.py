"""Offline artefact OPS.FOLD.UPSERT — idempotent fold writes."""

from __future__ import annotations

from pathlib import Path

from labcore.ops.fold_upsert import (
    ARTEFACT_ID,
    STRESS_ID,
    UNIQUE_INDEX_SQL,
    UPSERT_CV_FOLDS_SQL,
    InMemoryFoldStore,
)

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = ROOT / "supabase" / "migrations"


class FoldUpsertContractError(ValueError):
    """Raised when fold upsert contract fails."""


def assert_sql_on_conflict() -> dict[str, object]:
    if "ON CONFLICT (run_id, fold, algorithm_key)" not in UPSERT_CV_FOLDS_SQL:
        raise FoldUpsertContractError("UPSERT missing conflict target")
    if "cv_folds_run_fold_algo_uidx" not in UNIQUE_INDEX_SQL:
        raise FoldUpsertContractError("unique index SQL missing")
    return {"sql_ok": True}


def assert_migration_present() -> dict[str, object]:
    hits = list(MIGRATIONS.glob("*fold_upsert*.sql")) + list(
        MIGRATIONS.glob("*cv_folds_upsert*.sql")
    )
    if not hits:
        # also accept hardening-adjacent name
        hits = [
            p
            for p in MIGRATIONS.glob("*.sql")
            if "algorithm_key" in p.read_text(encoding="utf-8")
            and "cv_folds" in p.read_text(encoding="utf-8")
        ]
    if not hits:
        raise FoldUpsertContractError("no migration adds cv_folds.algorithm_key unique index")
    text = hits[0].read_text(encoding="utf-8")
    if "cv_folds_run_fold_algo_uidx" not in text:
        raise FoldUpsertContractError(f"{hits[0].name} missing unique index")
    return {"migration": hits[0].name}


def assert_idempotent_memory(*, seed: int = 42) -> dict[str, object]:
    store = InMemoryFoldStore()
    store.upsert(
        run_id="r1",
        fold=0,
        algorithm_key="clf.lgbm",
        n_train=80,
        metrics={"balanced_accuracy": 0.7},
    )
    store.upsert(
        run_id="r1",
        fold=0,
        algorithm_key="clf.lgbm",
        n_train=80,
        metrics={"balanced_accuracy": 0.71},
    )
    if len(store) != 1:
        raise FoldUpsertContractError("retry must not create a second row")
    row = store.get("r1", 0, "clf.lgbm")
    if row is None or row["metrics"]["balanced_accuracy"] != 0.71:
        raise FoldUpsertContractError("upsert did not replace metrics")
    store.upsert(run_id="r1", fold=1, algorithm_key="clf.lgbm", metrics={"x": 1})
    if len(store) != 2:
        raise FoldUpsertContractError("different fold must insert")
    return {"n_rows": len(store), "seed": seed}


def assert_fold_upsert_contract(*, seed: int = 42) -> list[dict[str, object]]:
    return [
        assert_sql_on_conflict(),
        assert_migration_present(),
        assert_idempotent_memory(seed=seed),
    ]


def fold_upsert_manifest(*, seed: int = 42) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "checks": assert_fold_upsert_contract(seed=seed),
    }
