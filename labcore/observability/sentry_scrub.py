"""Pure Sentry event scrubbing for before_send (OPS-12 / SEC-11 / ST-OPS-09)."""

from __future__ import annotations

import copy
import re
from typing import Any

REDACTED = "[REDACTED]"

_SENSITIVE_HEADER_NAMES = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "api-key",
        "x-supabase-api-key",
        "x-sentry-auth",
    }
)

_SENSITIVE_KEY_PARTS = frozenset(
    {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "bearer",
        "dsn",
        "private_key",
        "service_role",
        "jwt",
        "nvidia_api_key",
        "supabase",
        "pan",
        "aadhaar",
    }
)

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_BEARER_RE = re.compile(r"Bearer\s+\S+", re.IGNORECASE)
_JWTISH_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")


def _key_is_sensitive(key: str) -> bool:
    lower = key.lower().replace("-", "_")
    return any(part in lower for part in _SENSITIVE_KEY_PARTS)


def scrub_string(value: str) -> str:
    out = _BEARER_RE.sub(f"Bearer {REDACTED}", value)
    out = _JWTISH_RE.sub(REDACTED, out)
    out = _EMAIL_RE.sub(f"{REDACTED}@example.invalid", out)
    return out


def scrub_value(value: Any) -> Any:
    if isinstance(value, dict):
        return scrub_mapping(value)
    if isinstance(value, list):
        return [scrub_value(v) for v in value]
    if isinstance(value, str):
        return scrub_string(value)
    return value


def scrub_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, val in mapping.items():
        if _key_is_sensitive(key):
            out[key] = REDACTED
        else:
            out[key] = scrub_value(val)
    return out


def scrub_event(event: dict[str, Any]) -> dict[str, Any]:
    """Return a scrubbed copy of a Sentry event dict (before_send hook body)."""
    cleaned = copy.deepcopy(event)
    req = cleaned.get("request")
    if isinstance(req, dict):
        headers = req.get("headers")
        if isinstance(headers, dict):
            req["headers"] = {
                k: (REDACTED if k.lower() in _SENSITIVE_HEADER_NAMES else scrub_value(v))
                for k, v in headers.items()
            }
        if "cookies" in req:
            req["cookies"] = REDACTED
        if "data" in req:
            req["data"] = scrub_value(req["data"])
    user = cleaned.get("user")
    if isinstance(user, dict):
        cleaned["user"] = scrub_mapping(user)
    for section in ("extra", "contexts", "breadcrumbs"):
        block = cleaned.get(section)
        if isinstance(block, dict):
            cleaned[section] = scrub_mapping(block)
        elif section == "breadcrumbs" and isinstance(block, list):
            cleaned["breadcrumbs"] = [
                scrub_mapping(b) if isinstance(b, dict) else scrub_value(b) for b in block
            ]
    return cleaned