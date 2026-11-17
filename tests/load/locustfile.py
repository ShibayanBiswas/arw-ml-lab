"""Locust public API load scenario (ARCHITECTURE §28 / Phase 7).

Secrets-free: ``GET /healthz`` and public ``GET /api/v1/catalog/*`` only.

Run locally (lab-api on :8000):
  locust -f tests/load/locustfile.py --host http://127.0.0.1:8000

Headless smoke:
  locust -f tests/load/locustfile.py --host http://127.0.0.1:8000 \\
    --headless -u 5 -r 5 -t 10s --only-summary
"""

from __future__ import annotations

from locust import HttpUser, between, task

LOAD_SCENARIO_ID = "LOAD.P.HEALTHZ_CATALOG"


class LabApiPublicUser(HttpUser):
    """Read-only health probes + catalogue browsing (no Authorization header)."""

    wait_time = between(0.2, 1.0)

    @task(5)
    def healthz(self) -> None:
        with self.client.get("/healthz", name="GET /healthz", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"status {resp.status_code}")
                return
            try:
                body = resp.json()
            except Exception:
                resp.failure("non-json")
                return
            if body.get("seed") != 42:
                resp.failure(f"unexpected seed {body.get('seed')!r}")
            else:
                resp.success()

    @task(3)
    def catalog_algorithms(self) -> None:
        self.client.get(
            "/api/v1/catalog/algorithms",
            name="GET /api/v1/catalog/algorithms",
        )

    @task(2)
    def catalog_metrics(self) -> None:
        self.client.get(
            "/api/v1/catalog/metrics",
            name="GET /api/v1/catalog/metrics",
        )

    @task(1)
    def catalog_root(self) -> None:
        self.client.get("/api/v1/catalog", name="GET /api/v1/catalog")