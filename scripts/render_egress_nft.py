"""CLI for labcore.ops.egress_nft — Contabo OPS-14 (oneshot-c229).

Usage: python scripts/render_egress_nft.py > /tmp/lab-egress.nft
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from labcore.ops.egress_nft import render_nft  # noqa: E402


def main() -> int:
    sys.stdout.write(render_nft())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
