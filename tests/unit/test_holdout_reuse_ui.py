"""MI.HOLDOUT.REUSE FE badge — oneshot-c196."""

from labcore.integrity.holdout_reuse_ui import assert_holdout_ui_contract, holdout_reuse_badge


def test_holdout_ui_contract_seed_42() -> None:
    out = assert_holdout_ui_contract(seed=42)
    assert out["first"]["use_count"] == 1
    assert out["second"]["use_count"] == 2
    assert out["second"]["tone"] == "warn"
    assert "test set used" in holdout_reuse_badge(out["second"])["label"]
