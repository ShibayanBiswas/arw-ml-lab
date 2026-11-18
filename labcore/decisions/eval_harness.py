"""Offline VLM decision-agent eval harness (§38 / Phase 6A) — oneshot-c266.

Runs deterministic guard cases with seed 42. Never calls a live provider.
"""

from __future__ import annotations

from typing import Any

from labcore.decisions.guards import apply_deterministic_guards

ARTEFACT_ID = "DEC.EVAL.HARNESS"


def _cases() -> list[dict[str, Any]]:
    return [
        {
            "id": "block_shuffled_cv_on_sequential",
            "facts": {"sequential": True, "h_max": 5, "tabpfn_enabled": False},
            "proposal": {"apply_patch": {"cv_scheme": "KFold"}},
            "expect_blocked_substr": "shuffled CV",
        },
        {
            "id": "block_horizon_over_h_max",
            "facts": {"sequential": True, "h_max": 5, "tabpfn_enabled": False},
            "proposal": {"apply_patch": {"horizon": 12}},
            "expect_blocked_substr": "h_max",
        },
        {
            "id": "block_tabpfn_when_disabled",
            "facts": {"sequential": False, "tabpfn_enabled": False},
            "proposal": {"apply_patch": {"tabpfn_enabled": True}},
            "expect_blocked_substr": "TabPFN",
        },
        {
            "id": "block_secret_keys",
            "facts": {},
            "proposal": {"apply_patch": {"NVIDIA_API_KEY": "x"}},
            "expect_blocked_substr": "secrets",
        },
        {
            "id": "allow_safe_patch",
            "facts": {"sequential": False, "tabpfn_enabled": False},
            "proposal": {"apply_patch": {"n_estimators": 100}},
            "expect_allowed_key": "n_estimators",
        },
    ]


def run_decision_eval_harness(*, seed: int = 42) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    for case in _cases():
        out = apply_deterministic_guards(case["proposal"], facts=case["facts"])
        ok = True
        if "expect_blocked_substr" in case:
            blob = " ".join(out.get("blocked") or [])
            if case["expect_blocked_substr"] not in blob:
                ok = False
                failures.append(f"{case['id']}: expected block containing {case['expect_blocked_substr']!r}")
            if not out.get("overrode"):
                ok = False
                failures.append(f"{case['id']}: expected overrode=True")
        if "expect_allowed_key" in case:
            if case["expect_allowed_key"] not in (out.get("allowed_patch") or {}):
                ok = False
                failures.append(f"{case['id']}: expected allowed key")
            if out.get("blocked"):
                ok = False
                failures.append(f"{case['id']}: unexpected blocks")
        results.append({"id": case["id"], "ok": ok, "guards": out})
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "n_cases": len(results),
        "n_pass": sum(1 for r in results if r["ok"]),
        "failures": failures,
        "results": results,
        "ok": len(failures) == 0,
    }
