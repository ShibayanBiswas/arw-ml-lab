"""SEC.JWT.PARITY — oneshot-c212."""

from labcore.security.jwt_secret_parity import assert_jwt_parity_contract


def test_jwt_parity_contract() -> None:
    m = assert_jwt_parity_contract()
    assert m["id"] == "SEC.JWT.PARITY"
    assert m["hosted_verified"] is False
