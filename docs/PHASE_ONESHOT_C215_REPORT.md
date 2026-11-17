# Phase oneshot-c215 — Caddy SSE encode skip

## Built
- `infra/caddy/Caddyfile`: `@notSse not path */events*` then `encode @notSse zstd gzip`.
- `OPS.SSE.PROGRESS` requires the encode skip + `flush_interval`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_sse_progress.py -q --tb=line
.                                                                        [100%]
```

## Deviations
None. Contabo host still missing.
