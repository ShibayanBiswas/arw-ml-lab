"""SEC.CORS.ORIGINS — oneshot-c213."""

from labcore.security.cors_origins import PROD_ORIGIN, assert_cors_origins_contract


def test_cors_origins_contract() -> None:
    m = assert_cors_origins_contract()
    assert m["production_origin"] == PROD_ORIGIN
