"""VLM deterministic guards (§38)."""

from __future__ import annotations

from labcore.decisions import apply_deterministic_guards


def test_blocks_shuffled_cv_on_financial():
    out = apply_deterministic_guards(
        {"apply_patch": {"cv_scheme": "kfold", "n_splits": 5}},
        facts={"financial": True, "h_max": 12},
    )
    assert out["overrode"]
    assert "cv_scheme" not in out["allowed_patch"]
    assert out["allowed_patch"].get("n_splits") == 5


def test_blocks_horizon_above_h_max():
    out = apply_deterministic_guards(
        {"apply_patch": {"horizon": 100}},
        facts={"h_max": 24},
    )
    assert any("h_max" in b for b in out["blocked"])


def test_blocks_secrets_and_tabpfn():
    out = apply_deterministic_guards(
        {"apply_patch": {"NVIDIA_API_KEY": "x", "use_tabpfn": True}},
        facts={"tabpfn_enabled": False},
    )
    assert len(out["blocked"]) >= 2
    assert out["allowed_patch"] == {}
