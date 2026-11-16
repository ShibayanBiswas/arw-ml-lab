"""Deterministic guards that override VLM suggestions (ARCHITECTURE §38)."""

from __future__ import annotations

from typing import Any


def apply_deterministic_guards(
    proposal: dict[str, Any],
    *,
    facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Filter/override a VLM ``apply_patch`` proposal.

    Hard rules (non-exhaustive thin set):
    - Never enable shuffled K-fold when ``sequential=True`` / ``financial=True``.
    - Never raise forecast horizon above ``h_max``.
    - Never set TabPFN when ``tabpfn_enabled`` is false.
    - Strip any patch that touches secrets / API keys.
    """
    facts = facts or {}
    patch = dict(proposal.get("apply_patch") or {})
    blocked: list[str] = []
    allowed: dict[str, Any] = {}

    sequential = bool(facts.get("sequential") or facts.get("financial"))
    h_max = facts.get("h_max")
    tabpfn_ok = bool(facts.get("tabpfn_enabled", False))

    for key, value in patch.items():
        k = str(key).lower()
        if "secret" in k or "api_key" in k or "password" in k or "token" in k:
            blocked.append(f"{key}: secrets cannot be patched by VLM")
            continue
        if (
            sequential
            and k in {"cv_scheme", "cv", "splitter"}
            and str(value).lower()
            in {
                "kfold",
                "stratified_kfold",
                "shuffle_split",
                "stratified_shuffle_split",
            }
        ):
            blocked.append(f"{key}={value}: shuffled CV forbidden on sequential/financial")
            continue
        if k in {"h", "horizon", "h_request"} and h_max is not None:
            try:
                if float(value) > float(h_max):
                    blocked.append(f"{key}={value}: exceeds h_max={h_max}")
                    continue
            except (TypeError, ValueError):
                blocked.append(f"{key}={value}: invalid horizon")
                continue
        if k in {"tabpfn", "tabpfn_enabled", "use_tabpfn"} and value and not tabpfn_ok:
            blocked.append(f"{key}: TabPFN disabled (licence)")
            continue
        allowed[key] = value

    return {
        "allowed_patch": allowed,
        "blocked": blocked,
        "overrode": len(blocked) > 0,
        "original_keys": list(patch.keys()),
    }
