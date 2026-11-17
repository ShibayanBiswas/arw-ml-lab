"""Numbers-only decision baseline — §38 VD / Phase 6A (oneshot-c201).

When the VLM is unreachable the rule baseline is shown as the proposal,
labelled ``numbers-only``. Deterministic guards still run over any patch.
"""

from __future__ import annotations

from typing import Any

from labcore.decisions.guards import apply_deterministic_guards

ARTEFACT_ID = "VD.NUMBERS.ONLY"
FALLBACK_LABEL = "numbers-only"


def rule_baseline_proposal(
    *,
    decision_point: str,
    facts: dict[str, Any],
    seed: int = 42,
) -> dict[str, Any]:
    """Conservative baseline: empty apply_patch; cite FACTS; never invent metrics."""
    proposal = {
        "decision_point": decision_point,
        "mode": FALLBACK_LABEL,
        "artefact": ARTEFACT_ID,
        "seed": seed,
        "summary": f"{FALLBACK_LABEL} baseline for {decision_point} (seed {seed}).",
        "rationale": "Provider unavailable or workspace restricted — use deterministic baseline.",
        "citations": ["FACTS"],
        "apply_patch": {},
        "facts_keys": sorted(str(k) for k in facts.keys()),
    }
    guarded = apply_deterministic_guards(proposal, facts=facts)
    proposal["guards"] = guarded
    return proposal


def assert_decision_baseline_contract(*, seed: int = 42) -> dict[str, object]:
    facts = {"sequential": True, "h_max": 5, "tabpfn_enabled": False}
    base = rule_baseline_proposal(decision_point="VD1", facts=facts, seed=seed)
    if base["mode"] != FALLBACK_LABEL:
        raise AssertionError("baseline must be numbers-only")
    # Attempt a bad patch through guards
    bad = {
        "apply_patch": {"cv_scheme": "kfold", "api_key": "x", "h": 99},
    }
    g = apply_deterministic_guards(bad, facts=facts)
    if not g["overrode"] or len(g["blocked"]) < 2:
        raise AssertionError("guards must block shuffled CV, secrets, and horizon")
    return {"id": ARTEFACT_ID, "seed": seed, "blocked": g["blocked"]}
