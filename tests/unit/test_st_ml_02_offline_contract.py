"""MI.STML02.OFFLINE — ST-ML-02 rollup (oneshot-c176)."""

from __future__ import annotations

import pytest

from labcore.integrity.st_ml_02_contract import (
    ARTEFACT_ID,
    StMl02ContractError,
    assert_st_ml_02_offline_contract,
    st_ml_02_offline_manifest,
)


def test_repo_st_ml_02_offline_rollup() -> None:
    checks = assert_st_ml_02_offline_contract()
    assert len(checks) >= 18


def test_manifest_seed_42() -> None:
    manifest = st_ml_02_offline_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["stress_test"] == "ST-ML-02"
    assert "MI.MULTICOLLINEARITY" in manifest["offline_artefacts"]
    assert "DEEP.GPU.GUARD" in manifest["offline_artefacts"]


def test_st_ml_02_row_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    import labcore.integrity.st_ml_02_contract as mod

    def _fake_row(*_a: object, **_k: object) -> dict[str, object]:
        raise StMl02ContractError("ST-ML-02 row missing offline artefact ids: MI.FAKE")

    monkeypatch.setattr(mod, "assert_stress_test_st_ml_02_row", _fake_row)
    with pytest.raises(StMl02ContractError, match="MI.FAKE"):
        mod.assert_st_ml_02_offline_contract()