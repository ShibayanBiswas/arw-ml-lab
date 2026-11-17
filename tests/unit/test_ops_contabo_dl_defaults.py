"""OPS.CONTABO.DL_DEFAULTS — oneshot-c208."""

from labcore.ops.contabo_dl_defaults import assert_contabo_dl_defaults_contract


def test_contabo_dl_defaults() -> None:
    m = assert_contabo_dl_defaults_contract()
    assert m["id"] == "OPS.CONTABO.DL_DEFAULTS"
    assert m["batch_cap"] == 256
    assert m["max_rows"] == 2_000_000
