"""lab-api rate limits — SEC-11 / §46.3 (slowapi).

Defaults: 120/minute per IP globally; ``/healthz`` capped at 60/minute
(uptime probes share the IP budget carefully).
"""

from __future__ import annotations

from typing import Any

ARTEFACT_ID = "SEC.RATE.LIMIT"
STRESS_ID = "ST-OPS-09"

DEFAULT_LIMIT = "120/minute"
HEALTHZ_LIMIT = "60/minute"


def rate_limit_manifest() -> dict[str, Any]:
    return {
        "id": ARTEFACT_ID,
        "stress": STRESS_ID,
        "library": "slowapi",
        "key_func": "get_remote_address",
        "default_limits": [DEFAULT_LIMIT],
        "route_limits": {"GET /healthz": HEALTHZ_LIMIT},
        "exceeded_status": 429,
    }


def assert_rate_limit_wired_in_main(main_src: str) -> dict[str, object]:
    if "Limiter(" not in main_src or "slowapi" not in main_src:
        raise AssertionError("slowapi Limiter missing from main.py")
    if DEFAULT_LIMIT not in main_src:
        raise AssertionError(f"default_limits must include {DEFAULT_LIMIT}")
    if HEALTHZ_LIMIT not in main_src and f'"{HEALTHZ_LIMIT}"' not in main_src:
        raise AssertionError(f"/healthz must use {HEALTHZ_LIMIT}")
    if "RateLimitExceeded" not in main_src or "429" not in main_src:
        raise AssertionError("429 handler for RateLimitExceeded required")
    return rate_limit_manifest()
