"""SEC.AUTH.BYPASS — oneshot-c218."""

from labcore.security.auth_bypass_guard import assert_auth_bypass_contract


def test_auth_bypass_false_in_prod_docs() -> None:
    m = assert_auth_bypass_contract()
    assert m["id"] == "SEC.AUTH.BYPASS"
