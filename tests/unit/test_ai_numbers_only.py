"""AI.NUMBERS.ONLY — oneshot-c200."""

from labcore.ai.numbers_only import (
    CircuitBreaker,
    NumbersOnlyPolicy,
    assert_numbers_only_contract,
    numbers_only_insight,
    resolve_insight,
)


def test_numbers_only_contract() -> None:
    out = assert_numbers_only_contract(seed=42)
    assert out["id"] == "AI.NUMBERS.ONLY"
    assert out["seed"] == 42


def test_insight_echoes_facts_keys_only() -> None:
    facts = {"balanced_accuracy": 0.7, "mcc": 0.4}
    out = numbers_only_insight(facts, seed=42)
    assert out["mode"] == "numbers-only"
    cited = {f["citation"] for f in out["findings"]}
    assert cited == {"FACTS.balanced_accuracy", "FACTS.mcc"}


def test_circuit_opens_after_three() -> None:
    br = CircuitBreaker(fail_threshold=3, cooldown_s=300)
    assert br.is_open() is False
    br.record_failure()
    br.record_failure()
    assert br.is_open() is False
    br.record_failure()
    assert br.is_open() is True
    pol = NumbersOnlyPolicy(key_present=True, circuit=br)
    assert resolve_insight({"a": 1}, policy=pol)["reason"] == "circuit_open"
