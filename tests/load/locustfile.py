"""Locust load skeleton (ARCHITECTURE §26 / Phase 7).

Run locally (not CI by default):
  locust -f tests/load/locustfile.py --host https://arw-ml-lab.vercel.app
"""

from __future__ import annotations

from locust import HttpUser, between, task


class LabFrontendUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def login_page(self) -> None:
        self.client.get("/login", name="GET /login")

    @task(1)
    def home(self) -> None:
        self.client.get("/", name="GET /")
