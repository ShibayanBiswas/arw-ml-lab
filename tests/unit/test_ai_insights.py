"""Mocked NVIDIA AI client + insights validator."""

from __future__ import annotations

from labcore.ai import MockAIClient, get_ai_client, validate_insights_payload


def test_mock_client_deterministic():
    client = MockAIClient(seed=42)
    out = client.chat([{"role": "user", "content": "summarise FACTS"}])
    assert out["provider"] == "mock"
    assert "FACTS" in out["choices"][0]["message"]["content"]
    assert len(client.calls) == 1


def test_get_ai_client_prefers_mock():
    c = get_ai_client(prefer_mock=True)
    assert isinstance(c, MockAIClient)


def test_validator_requires_facts_citation():
    bad = {"summary": "ok", "findings": [{"id": 1}], "citations": []}
    r = validate_insights_payload(bad)
    assert not r["ok"]
    assert any("FACTS" in e for e in r["errors"])


def test_validator_flags_unknown_number():
    good = {
        "summary": "MAE is 1.23 on OOF",
        "findings": [],
        "citations": ["FACTS"],
    }
    r = validate_insights_payload(good, facts={"mae": 0.5})
    assert r["ok"]
    assert any("1.23" in w for w in r["warnings"])
