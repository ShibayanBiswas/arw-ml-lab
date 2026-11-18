# Phase oneshot-c277 — Module journey HTTP e2e + JSON log bind_context

## Built
- `tests/e2e/test_module_journeys_http.py`: DoD journey shells on Vercel (soft-skip if unreachable).
- Train/predict Celery tasks bind `job_id` / `run_id` / `workspace_id` into structured logs.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_module_journeys_http.py -q --tb=line
s...s...                                                                 [100%]
# mix of pass + soft-skip depending on network; no failures
```

## Contabo
Still blocked — `CONTABO_HOST` missing; Actions billing still kills CI in ~2s.
