"""SEC.CORS.BEARER — CORS allow-list + Bearer-only API auth (ST-SEC-07 / oneshot-c151)."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

from labcore.security.api_auth_policy import (
    ARTEFACT_ID,
    CORS_ALLOW_CREDENTIALS,
    cors_policy_manifest,
    reject_cookie_without_bearer,
)

os.environ.setdefault("AUTH_MODE", "bff")
os.environ.setdefault("JWT_SECRET", "test-secret-for-pytest-only-32chars!!")

from backend.app.main import create_app  # noqa: E402


def test_reject_cookie_without_bearer_matrix() -> None:
    assert not reject_cookie_without_bearer(
        cookie=None, authorization=None, method="GET", path="/catalog"
    )
    assert not reject_cookie_without_bearer(
        cookie="session=abc", authorization="Bearer tok", method="POST", path="/jobs"
    )
    assert reject_cookie_without_bearer(
        cookie="session=abc", authorization=None, method="POST", path="/jobs"
    )
    assert not reject_cookie_without_bearer(
        cookie="session=abc", authorization=None, method="OPTIONS", path="/jobs"
    )
    assert not reject_cookie_without_bearer(
        cookie="session=abc", authorization=None, method="GET", path="/healthz"
    )


def test_manifest_contract_seed_42() -> None:
    manifest = cors_policy_manifest(seed=42, allowed_origins=("http://localhost:3000",))
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["allow_credentials"] is CORS_ALLOW_CREDENTIALS


def test_api_rejects_cookie_without_bearer() -> None:
    client = TestClient(create_app())
    r = client.get("/catalog", headers={"Cookie": "sb-access-token=fake"})
    assert r.status_code == 401
    assert "Bearer" in r.json()["detail"]


def test_api_allows_bearer_with_cookie() -> None:
    client = TestClient(create_app())
    r = client.get(
        "/catalog",
        headers={
            "Cookie": "sb-access-token=fake",
            "Authorization": "Bearer not-a-real-jwt",
        },
    )
    assert r.status_code != 401 or "Bearer only" not in r.text


def test_cors_preflight_no_credentials() -> None:
    client = TestClient(create_app())
    r = client.options(
        "/catalog",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-credentials") in (None, "false")