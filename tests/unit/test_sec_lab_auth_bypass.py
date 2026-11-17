"""SEC.LAB_AUTH.BYPASS — oneshot-c220."""

from labcore.security.lab_auth_bypass_guard import assert_lab_auth_bypass_contract


def test_lab_auth_bypass_false_in_prod_docs() -> None:
    m = assert_lab_auth_bypass_contract()
    assert m["id"] == "SEC.LAB_AUTH.BYPASS"
