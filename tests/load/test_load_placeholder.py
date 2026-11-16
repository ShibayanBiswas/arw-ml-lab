"""Load-test placeholder — Locust suite expands in Phase 7."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Locust load tests land in Phase 7")
def test_locust_suite_pending() -> None:
    raise AssertionError("pending Phase 7")
