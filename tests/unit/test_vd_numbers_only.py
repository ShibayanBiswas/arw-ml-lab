"""VD.NUMBERS.ONLY — oneshot-c201."""

from labcore.decisions.baseline import assert_decision_baseline_contract, rule_baseline_proposal


def test_decision_baseline_contract() -> None:
    out = assert_decision_baseline_contract(seed=42)
    assert out["id"] == "VD.NUMBERS.ONLY"
    assert len(out["blocked"]) >= 2


def test_baseline_empty_patch() -> None:
    p = rule_baseline_proposal(decision_point="VD2", facts={"n": 10}, seed=42)
    assert p["apply_patch"] == {}
    assert p["mode"] == "numbers-only"
    assert "FACTS" in p["citations"]
