"""OPS.LAB_API.HTTPS — oneshot-c239."""

from labcore.ops.lab_api_url_https_contract import assert_lab_api_https_docs


def test_deploy_docs_require_https_lab_api_url() -> None:
    m = assert_lab_api_https_docs()
    assert m["id"] == "OPS.LAB_API.HTTPS"
