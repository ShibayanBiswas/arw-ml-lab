"""OPS.EGRESS.NFT — oneshot-c229."""

from labcore.ops.egress_nft_contract import assert_egress_nft_renderer


def test_egress_nft_renderer() -> None:
    m = assert_egress_nft_renderer()
    assert m["id"] == "OPS.EGRESS.NFT"
    assert m["hosts_n"] >= 1
