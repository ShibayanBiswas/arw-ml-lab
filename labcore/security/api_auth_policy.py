"""lab-api CORS + Bearer-only auth policy (ARCHITECTURE §46.3 SEC-07 / ST-SEC-07).

Browsers must not treat ``lab-api`` as a cookie-authenticated origin: CORS disables
credentials and mutating requests with a ``Cookie`` header but no ``Authorization:
Bearer`` are rejected so CSRF against session cookies cannot apply to the API.
"""

from __future__ import annotations

ARTEFACT_ID = "SEC.CORS.BEARER"

CORS_ALLOW_CREDENTIALS = False
CORS_ALLOWED_METHODS: tuple[str, ...] = (
    "GET",
    "POST",
    "PATCH",
    "PUT",
    "DELETE",
    "OPTIONS",
)
CORS_ALLOWED_HEADERS: tuple[str, ...] = (
    "Authorization",
    "Content-Type",
    "Idempotency-Key",
    "X-Workspace-Id",
)

COOKIE_EXEMPT_PATHS = frozenset({"/healthz", "/openapi.json", "/docs", "/redoc"})


def has_bearer_authorization(authorization: str | None) -> bool:
    if not authorization:
        return False
    return authorization.strip().lower().startswith("bearer ")


def has_cookie_header(cookie: str | None) -> bool:
    return bool(cookie and cookie.strip())


def reject_cookie_without_bearer(
    *,
    cookie: str | None,
    authorization: str | None,
    method: str,
    path: str,
) -> bool:
    """Return True when the request must be rejected (cookie present, no Bearer)."""
    if method.upper() == "OPTIONS":
        return False
    if path in COOKIE_EXEMPT_PATHS or path.startswith("/docs"):
        return False
    if not has_cookie_header(cookie):
        return False
    return not has_bearer_authorization(authorization)


def cors_policy_manifest(*, seed: int, allowed_origins: tuple[str, ...]) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "allow_credentials": CORS_ALLOW_CREDENTIALS,
        "allowed_methods": list(CORS_ALLOWED_METHODS),
        "allowed_headers": list(CORS_ALLOWED_HEADERS),
        "allowed_origins_n": len(allowed_origins),
        "cookie_exempt_paths": sorted(COOKIE_EXEMPT_PATHS),
    }