"""Nested CV default — MI-03 / ST-ML-02 (ARCHITECTURE §46.1).

Nested CV is on by default when ``n_train < 2000`` unless the user overrides
``nested`` or chooses scheme ``nested``.
"""

from __future__ import annotations

from labcore.cv.schemes import nested_default

ARTEFACT_ID = "MI.NESTED.CV"
MI_RULE = "MI-03"
NESTED_CV_AUTO_THRESHOLD = 2000


def build_nested_cv_manifest(
    *,
    n_train: int,
    nested_enabled: bool,
    cv_scheme: str,
    nested_override: bool | None,
    seed: int = 42,
) -> dict[str, object]:
    auto = nested_default(n_train)
    return {
        "id": ARTEFACT_ID,
        "mi_rule": MI_RULE,
        "seed": seed,
        "n_train": n_train,
        "nested_enabled": nested_enabled,
        "cv_scheme": cv_scheme,
        "auto_default": auto,
        "auto_threshold": NESTED_CV_AUTO_THRESHOLD,
        "user_override": nested_override,
        "source": (
            "cv_scheme_nested"
            if cv_scheme == "nested"
            else ("user_override" if nested_override is not None else "mi03_auto")
        ),
    }