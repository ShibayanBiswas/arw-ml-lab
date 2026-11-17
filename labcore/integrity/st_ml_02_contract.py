"""ST-ML-02 offline rollup — MI-01…MI-18 contract registry (ARCHITECTURE §46.1).

Closes the offline portion of STRESS **ST-ML-02** after per-rule kits (oneshot-c159…c175).
Hosted worker/UI prove stays Phase 2/4/5.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path

ARTEFACT_ID = "MI.STML02.OFFLINE"
STRESS_ID = "ST-ML-02"
LAB_DEFAULT_SEED = 42


@dataclass(frozen=True, slots=True)
class MiKitSpec:
    mi_rules: tuple[str, ...]
    artefact_id: str
    module: str
    stress_test: str


class StMl02ContractError(ValueError):
    """Raised when ST-ML-02 offline rollup contract is violated."""


# Every MI-01…MI-18 row in §46.1 must map to an offline contract module (+ tests elsewhere).
MI_KIT_REGISTRY: tuple[MiKitSpec, ...] = (
    MiKitSpec(("MI-01",), "MI.PREPROCESS.FIT", "labcore.integrity.preprocess_fit_contract", STRESS_ID),
    MiKitSpec(("MI-02",), "MI.TARGET.ENCODING", "labcore.integrity.target_encoding_contract", STRESS_ID),
    MiKitSpec(("MI-03",), "MI.NESTED.CV", "labcore.integrity.nested_cv_contract", STRESS_ID),
    MiKitSpec(("MI-04",), "MI.PURGED.SPLIT", "labcore.integrity.purged_split_contract", STRESS_ID),
    MiKitSpec(("MI-05",), "MI.TS.TARGET_TRANSFORM", "labcore.integrity.ts_target_transform_contract", STRESS_ID),
    MiKitSpec(("MI-06",), "MI.SEED.DRIFT", "labcore.integrity.seed_drift_contract", STRESS_ID),
    MiKitSpec(("MI-07",), "MI.CLASS.RESAMPLE", "labcore.integrity.class_imbalance_contract", STRESS_ID),
    MiKitSpec(("MI-08", "MI-09"), "MI.SAMPLE.SIZE", "labcore.integrity.small_large_data_contract", "ST-ML-05"),
    MiKitSpec(("MI-10",), "MI.HIGH.CARD", "labcore.integrity.high_cardinality_contract", STRESS_ID),
    MiKitSpec(("MI-11", "MI-12"), "MI.DATA.QUALITY", "labcore.integrity.data_quality_contract", "ST-ML-03"),
    MiKitSpec(("MI-13",), "MI.MULTI.TARGET", "labcore.integrity.multi_target_contract", STRESS_ID),
    MiKitSpec(("MI-14",), "MI.MULTICOLLINEARITY", "labcore.integrity.multicollinearity_contract", STRESS_ID),
    MiKitSpec(("MI-15",), "MI.TARGET.LEAKAGE", "labcore.integrity.target_leakage_contract", STRESS_ID),
    MiKitSpec(("MI-16",), "MI.HOLDOUT.REUSE", "labcore.integrity.holdout_reuse", "ST-ML-04"),
    MiKitSpec(("MI-17",), "MI.HORIZON.GUARD", "labcore.integrity.horizon_guard_contract", STRESS_ID),
    MiKitSpec(("MI-18",), "MI.DUPLICATE.GROUP", "labcore.integrity.duplicate_split_contract", STRESS_ID),
)

STML02_OFFLINE_ARTEFACTS: tuple[str, ...] = tuple(
    k.artefact_id for k in MI_KIT_REGISTRY if k.stress_test == STRESS_ID
)

GPU_GUARD_SPEC = MiKitSpec(
    ("DEEP.GPU",),
    "DEEP.GPU.GUARD",
    "labcore.deep.gpu_guard_contract",
    STRESS_ID,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _import_artefact_id(module_path: str) -> str:
    mod = importlib.import_module(module_path)
    artefact_id = getattr(mod, "ARTEFACT_ID", None)
    if not isinstance(artefact_id, str) or not artefact_id.strip():
        msg = f"{module_path}: missing ARTEFACT_ID"
        raise StMl02ContractError(msg)
    return artefact_id


def assert_mi_kit(spec: MiKitSpec) -> dict[str, object]:
    found = _import_artefact_id(spec.module)
    if found != spec.artefact_id:
        raise StMl02ContractError(
            f"{spec.module}: expected ARTEFACT_ID {spec.artefact_id!r}, got {found!r}",
        )
    return {
        "mi_rules": list(spec.mi_rules),
        "artefact_id": spec.artefact_id,
        "module": spec.module,
        "stress_test": spec.stress_test,
    }


def assert_stress_test_st_ml_02_row(
    stress_path: Path | None = None,
) -> dict[str, object]:
    """``docs/STRESS_TEST.md`` ST-ML-02 row must mark offline rollup + cite contract modules."""
    path = stress_path or (_repo_root() / "docs" / "STRESS_TEST.md")
    if not path.is_file():
        msg = f"STRESS_TEST.md missing: {path}"
        raise StMl02ContractError(msg)
    text = path.read_text(encoding="utf-8")
    if "| ST-ML-02 |" not in text:
        raise StMl02ContractError("STRESS_TEST.md: missing ST-ML-02 row")
    row = next(line for line in text.splitlines() if line.startswith("| ST-ML-02 |"))
    if "fixed + tested" not in row:
        raise StMl02ContractError("ST-ML-02 row: expected fixed + tested status")
    if "MI.STML02.OFFLINE" not in row:
        raise StMl02ContractError("ST-ML-02 row: must cite MI.STML02.OFFLINE rollup")
    if "st_ml_02_contract.py" not in row:
        raise StMl02ContractError("ST-ML-02 row: must cite st_ml_02_contract.py")
    need_modules = [
        *(spec.module.rsplit(".", 1)[-1] + ".py" for spec in MI_KIT_REGISTRY if spec.stress_test == STRESS_ID),
        GPU_GUARD_SPEC.module.rsplit(".", 1)[-1] + ".py",
    ]
    missing = [name for name in need_modules if name not in row]
    if missing:
        raise StMl02ContractError(
            f"ST-ML-02 row missing contract modules: {', '.join(missing)}",
        )
    return {"stress_doc": path.name, "n_modules": len(need_modules)}


def assert_mi_rules_complete() -> dict[str, object]:
    """MI-01…MI-18 each appear exactly once across registry entries."""
    covered: list[str] = []
    for spec in MI_KIT_REGISTRY:
        covered.extend(spec.mi_rules)
    expected = [f"MI-{i:02d}" for i in range(1, 19)]
    missing = [r for r in expected if r not in covered]
    dupes = [r for r in expected if covered.count(r) > 1]
    if missing or dupes:
        raise StMl02ContractError(
            f"MI coverage broken: missing={missing}, dupes={dupes}",
        )
    return {"mi_rules": expected, "n_kits": len(MI_KIT_REGISTRY)}


def assert_st_ml_02_offline_contract() -> list[dict[str, object]]:
    checks: list[dict[str, object]] = [assert_mi_rules_complete()]
    for spec in MI_KIT_REGISTRY:
        checks.append(assert_mi_kit(spec))
    checks.append(assert_mi_kit(GPU_GUARD_SPEC))
    checks.append(assert_stress_test_st_ml_02_row())
    return checks


def st_ml_02_offline_manifest(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    checks = assert_st_ml_02_offline_contract()
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "n_checks": len(checks),
        "offline_artefacts": list(STML02_OFFLINE_ARTEFACTS) + [GPU_GUARD_SPEC.artefact_id],
        "checks": checks,
    }