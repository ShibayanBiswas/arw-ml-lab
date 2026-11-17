# Phase oneshot-c185 — OPS.CONTABO.LIMITS

## Built
- `labcore/ops/contabo_limits_contract.py` — offline artefact **`OPS.CONTABO.LIMITS`**: worker-train `--concurrency 1`, `LAB_GPU_WORKER=false`, mem_limit, redis unpublished, only Caddy publishes ports, DEPLOY_CONTABO §12 markers.
- `tests/unit/test_ops_contabo_limits.py`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_contabo_limits.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 2 passed in 0.53s ==============================
```

## Notes
- Seed **42**. Hosted Contabo prove still blocked (no CONTABO_HOST / Actions billing).

## Self-check (CURSOR_PROMPT §000)
- [x] Compose matches DEPLOY_CONTABO §5 one-heavy-job budget.
- [x] Redis not exposed; Caddy-only ports.
- [x] Import allowlist green (PyYAML already pinned).
