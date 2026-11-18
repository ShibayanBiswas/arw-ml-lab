"""Decision-agent eval harness — oneshot-c266."""

from labcore.decisions.eval_harness import ARTEFACT_ID, run_decision_eval_harness


def test_decision_eval_harness_all_pass() -> None:
    out = run_decision_eval_harness(seed=42)
    assert out["id"] == ARTEFACT_ID
    assert out["ok"] is True
    assert out["n_pass"] == out["n_cases"]
    assert out["failures"] == []
