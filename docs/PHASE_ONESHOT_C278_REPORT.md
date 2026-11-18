# Phase oneshot-c278 — Tune log context + Playwright journey gates

## Built
- Tune Celery task binds/clears JSON log context (parity with train/predict).
- `tests/e2e/test_playwright_journeys.py`: DoD shells gated on `PLAYWRIGHT_E2E=1`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_playwright_journeys.py -q --tb=line
sssss                                                                    [100%]
# skip without PLAYWRIGHT_E2E=1 (expected)
```

## Contabo
Still blocked — `CONTABO_HOST` missing; Actions billing still kills CI in ~2s.
Hosted DS1 EDA prove, Deploy green, rollback, backup cron, and final prune wait on Blocked table.
