"""Global empty/loading/error + PV UI map — UX.GLOBAL.STATES / ST-UX-03 (§46.4)."""

from __future__ import annotations

import re
from pathlib import Path

from labcore.ux.pv_messages import IMPLEMENTED_PV_CODES, PV_MESSAGES

ARTEFACT_ID = "UX.GLOBAL.STATES"
STRESS_ID = "ST-UX-03"
WCAG_TARGET = "2.2 AA"
LAB_DEFAULT_SEED = 42

_CURSUR_PROMPT = "CURSOR_PROMPT.md"
_MODULE_PLACEHOLDER = "frontend/src/components/panels/ModulePlaceholder.tsx"
_PV_MESSAGES_TS = "frontend/src/lib/pv-messages.ts"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    path = _repo_root() / rel
    if not path.is_file():
        raise ValueError(f"{ARTEFACT_ID}: missing kit file {rel}")
    return path.read_text(encoding="utf-8")


def assert_module_placeholder_states() -> dict[str, object]:
    src = _read(_MODULE_PLACEHOLDER)
    for token in ('"empty"', '"loading"', '"error"', "data-state"):
        if token not in src:
            raise ValueError(f"{ARTEFACT_ID}: ModulePlaceholder must wire {token}")
    return {"component": _MODULE_PLACEHOLDER, "states": ["empty", "loading", "error"]}


def assert_cursor_axe_checklist() -> dict[str, object]:
    text = _read(_CURSUR_PROMPT)
    if "axe-core" not in text:
        raise ValueError(f"{ARTEFACT_ID}: CURSOR_PROMPT must mention axe-core (§000)")
    if "empty, loading and error states" not in text:
        raise ValueError(f"{ARTEFACT_ID}: CURSOR_PROMPT must require empty/loading/error states")
    return {"doc": _CURSUR_PROMPT, "wcag_target": WCAG_TARGET}


def _ts_pv_keys(src: str) -> set[str]:
    return set(re.findall(r"\b(PV\d{2})\b", src))


def assert_pv_messages_sync() -> dict[str, object]:
    py_keys = set(PV_MESSAGES)
    if tuple(sorted(py_keys)) != IMPLEMENTED_PV_CODES:
        raise ValueError(f"{ARTEFACT_ID}: IMPLEMENTED_PV_CODES must match PV_MESSAGES keys")
    ts = _read(_PV_MESSAGES_TS)
    ts_keys = _ts_pv_keys(ts)
    for code in py_keys:
        if code not in ts_keys:
            raise ValueError(f"{ARTEFACT_ID}: frontend pv-messages missing {code}")
    if "export const PV_MESSAGES" not in ts:
        raise ValueError(f"{ARTEFACT_ID}: pv-messages.ts must export PV_MESSAGES")
    return {"n_codes": len(py_keys), "frontend": _PV_MESSAGES_TS}


def assert_global_states_contract(*, seed: int = LAB_DEFAULT_SEED) -> list[dict[str, object]]:
    _ = seed
    return [
        assert_module_placeholder_states(),
        assert_cursor_axe_checklist(),
        assert_pv_messages_sync(),
    ]


def build_global_states_manifest(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    checks = assert_global_states_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "wcag_target": WCAG_TARGET,
        "pv_codes": list(IMPLEMENTED_PV_CODES),
        "checks": checks,
    }