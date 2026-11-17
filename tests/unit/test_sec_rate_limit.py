"""SEC.RATE.LIMIT — oneshot-c198."""

from pathlib import Path

from labcore.security.rate_limit_policy import (
    DEFAULT_LIMIT,
    HEALTHZ_LIMIT,
    assert_rate_limit_wired_in_main,
    rate_limit_manifest,
)


def test_rate_limit_manifest() -> None:
    m = rate_limit_manifest()
    assert m["default_limits"] == [DEFAULT_LIMIT]
    assert m["route_limits"]["GET /healthz"] == HEALTHZ_LIMIT
    assert m["exceeded_status"] == 429


def test_main_wires_slowapi() -> None:
    src = Path("backend/app/main.py").read_text(encoding="utf-8")
    out = assert_rate_limit_wired_in_main(src)
    assert out["library"] == "slowapi"
