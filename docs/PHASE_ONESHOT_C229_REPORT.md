# Phase oneshot-c229 — OPS.EGRESS.NFT

## Built
- `labcore/ops/egress_nft.py` renders an nftables drop-by-default egress table with `# ALLOW_HOST` lines from the OPS-14 allow-list.
- `scripts/render_egress_nft.py` CLI for Contabo apply-time use.
- ST-OPS-08 updated.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_egress_nft.py -q --tb=short
.                                                                        [100%]
EXIT:0
```

## Hosted
`nft -f` on the VPS still **blocked** (no CONTABO_HOST).
