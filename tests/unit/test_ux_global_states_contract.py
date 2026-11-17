"""UX.GLOBAL.STATES — ST-UX-03 global UX offline contract (oneshot-c179)."""

from __future__ import annotations

from labcore.ux.global_states_contract import (
    ARTEFACT_ID,
    STRESS_ID,
    WCAG_TARGET,
    build_global_states_manifest,
)
from labcore.ux.pv_messages import IMPLEMENTED_PV_CODES, pv_message_for_code


def test_global_states_manifest_seed_42() -> None:
    manifest = build_global_states_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["stress_test"] == STRESS_ID
    assert manifest["seed"] == 42
    assert manifest["wcag_target"] == WCAG_TARGET
    assert manifest["pv_codes"] == list(IMPLEMENTED_PV_CODES)
    assert len(manifest["checks"]) == 3


def test_pv_message_roundtrip() -> None:
    msg = pv_message_for_code("PV04")
    assert msg["title"]
    assert msg["fix"]