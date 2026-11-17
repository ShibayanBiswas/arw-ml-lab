"""OPS.EGRESS.NFT contract — oneshot-c229."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from labcore.ops.egress_nft import assert_egress_nft_ready


def assert_egress_nft_renderer() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[2] / "scripts" / "render_egress_nft.py"
    if not path.is_file():
        raise AssertionError("scripts/render_egress_nft.py missing")
    text = path.read_text(encoding="utf-8")
    if "render_nft" not in text:
        raise AssertionError("CLI must call render_nft")
    return assert_egress_nft_ready()
