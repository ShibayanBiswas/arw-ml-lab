"""Numbers-only AI fallback — §40 / Phase 8.2 AC (oneshot-c200).

When the provider key is missing, the circuit is open, the workspace is
``restricted``, or the daily budget is exhausted, insights degrade to a
deterministic FACTS-only payload labelled ``numbers-only``. Never calls the
network; never fabricates metrics (only echoes supplied FACTS keys).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

ARTEFACT_ID = "AI.NUMBERS.ONLY"
FALLBACK_LABEL = "numbers-only"
CIRCUIT_FAIL_THRESHOLD = 3
CIRCUIT_COOLDOWN_S = 300.0  # 5 min


@dataclass
class CircuitBreaker:
    """Simple process-local breaker (Redis-backed on Contabo later)."""

    fail_threshold: int = CIRCUIT_FAIL_THRESHOLD
    cooldown_s: float = CIRCUIT_COOLDOWN_S
    failures: int = 0
    opened_at: float | None = None

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.fail_threshold:
            self.opened_at = time.monotonic()

    def is_open(self, *, now: float | None = None) -> bool:
        if self.opened_at is None:
            return False
        t = now if now is not None else time.monotonic()
        if t - self.opened_at >= self.cooldown_s:
            # half-open: allow a probe by clearing open state
            self.opened_at = None
            self.failures = 0
            return False
        return True


@dataclass
class NumbersOnlyPolicy:
    workspace_class: str = "internal"  # public | internal | restricted
    budget_exhausted: bool = False
    key_present: bool = False
    circuit: CircuitBreaker = field(default_factory=CircuitBreaker)

    def must_use_numbers_only(self) -> bool:
        if self.workspace_class == "restricted":
            return True
        if self.budget_exhausted:
            return True
        if not self.key_present:
            return True
        if self.circuit.is_open():
            return True
        return False


def numbers_only_insight(facts: dict[str, Any], *, seed: int = 42) -> dict[str, Any]:
    """Build a grounded stub that cites FACTS keys only (no invented numbers)."""
    keys = sorted(str(k) for k in facts.keys())
    findings = [
        {
            "severity": "info",
            "text": f"FACTS key present: {k}",
            "citation": f"FACTS.{k}",
        }
        for k in keys[:12]
    ]
    return {
        "mode": FALLBACK_LABEL,
        "artefact": ARTEFACT_ID,
        "seed": seed,
        "summary": f"{FALLBACK_LABEL} insight ({len(keys)} FACTS keys; seed {seed}).",
        "findings": findings,
        "citations": ["FACTS"],
        "apply_patch": None,
        "provider": FALLBACK_LABEL,
    }


def resolve_insight(
    facts: dict[str, Any],
    *,
    policy: NumbersOnlyPolicy,
    seed: int = 42,
) -> dict[str, Any]:
    if policy.must_use_numbers_only():
        out = numbers_only_insight(facts, seed=seed)
        out["reason"] = _reason(policy)
        return out
    # Live path is outside this module; callers invoke the provider then fall back
    return numbers_only_insight(facts, seed=seed) | {"mode": "provider_pending", "reason": "caller"}


def _reason(policy: NumbersOnlyPolicy) -> str:
    if policy.workspace_class == "restricted":
        return "workspace_restricted"
    if policy.budget_exhausted:
        return "budget_exhausted"
    if not policy.key_present:
        return "key_missing"
    if policy.circuit.is_open():
        return "circuit_open"
    return "numbers_only"


def assert_numbers_only_contract(*, seed: int = 42) -> dict[str, object]:
    facts = {"roc_auc_cv_mean": 0.81, "n_train": 100}  # supplied FACTS, not fabricated for display claim
    pol = NumbersOnlyPolicy(key_present=False)
    out = resolve_insight(facts, policy=pol, seed=seed)
    if out["mode"] != FALLBACK_LABEL:
        raise AssertionError("missing key must force numbers-only")
    if "FACTS" not in out["citations"]:
        raise AssertionError("must cite FACTS")

    br = CircuitBreaker(fail_threshold=3, cooldown_s=300)
    for _ in range(3):
        br.record_failure()
    if not br.is_open():
        raise AssertionError("circuit must open after 3 failures")
    pol2 = NumbersOnlyPolicy(key_present=True, circuit=br)
    out2 = resolve_insight(facts, policy=pol2, seed=seed)
    if out2.get("reason") != "circuit_open":
        raise AssertionError("open circuit → numbers-only")

    pol3 = NumbersOnlyPolicy(key_present=True, workspace_class="restricted")
    if resolve_insight(facts, policy=pol3, seed=seed)["mode"] != FALLBACK_LABEL:
        raise AssertionError("restricted → numbers-only")

    return {"id": ARTEFACT_ID, "seed": seed, "checks": 3}
