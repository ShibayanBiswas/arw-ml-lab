"""AI.RESILIENT.CHAT — oneshot-c240."""

from __future__ import annotations

import time

from labcore.ai.client import MockAIClient
from labcore.ai.numbers_only import CircuitBreaker
from labcore.ai.resilient import ARTEFACT_ID, resilient_chat


class _BoomClient:
    def chat(self, messages, *, model=None, temperature=0.0):  # noqa: ANN001
        raise TimeoutError("simulated")


def test_resilient_chat_falls_back_on_error_under_10s() -> None:
    br = CircuitBreaker(fail_threshold=3, cooldown_s=300)
    t0 = time.perf_counter()
    out = resilient_chat(
        [{"role": "user", "content": "hi"}],
        facts={"roc_auc_cv_mean": 0.8},
        client=_BoomClient(),  # type: ignore[arg-type]
        circuit=br,
        key_present=True,
        seed=42,
    )
    elapsed = time.perf_counter() - t0
    assert out["mode"] == "numbers-only"
    assert out["artefact"] == ARTEFACT_ID
    assert out["reason"] == "TimeoutError"
    assert elapsed < 10.0
    assert br.failures == 1


def test_resilient_chat_success_with_mock() -> None:
    br = CircuitBreaker()
    out = resilient_chat(
        [{"role": "user", "content": "hi"}],
        facts={},
        client=MockAIClient(seed=42),
        circuit=br,
        key_present=True,
        seed=42,
    )
    assert out["mode"] == "provider"
    assert br.failures == 0
