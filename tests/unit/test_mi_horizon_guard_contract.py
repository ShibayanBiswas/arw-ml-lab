"""MI.HORIZON.GUARD — ST-ML-02 MI-17 offline (oneshot-c171)."""

from __future__ import annotations

import pytest

from labcore.integrity.horizon_guard_contract import (
    ARTEFACT_ID,
    HorizonGuardContractError,
    assert_horizon_guard_contract,
    horizon_guard_manifest,
)
from labcore.integrity.horizon_guard_policy import horizon_request_allowed, horizon_reject_reasons


def test_repo_horizon_guard_contract() -> None:
    checks = assert_horizon_guard_contract(seed=42)
    assert len(checks) == 4


def test_horizon_request_allowed_ds22() -> None:
    assert horizon_request_allowed(144, "MS", 12, m=12, w=4)
    assert not horizon_request_allowed(144, "MS", 100, m=12, w=4)


def test_horizon_reject_reasons_nonempty() -> None:
    reasons = horizon_reject_reasons(144, "MS", 100, m=12, w=4)
    assert reasons
    assert any("h_max" in r for r in reasons)


def test_manifest_seed_42() -> None:
    manifest = horizon_guard_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42


def test_mi17_reject_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.horizon_guard_contract as mod

    monkeypatch.setattr(mod, "horizon_request_allowed", lambda *a, **k: True)
    with pytest.raises(HorizonGuardContractError, match="MI-17"):
        mod.assert_mi17_rejects_over_h_max(seed=42)