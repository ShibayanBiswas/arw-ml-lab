# Phase oneshot-c200 — AI.NUMBERS.ONLY

## Built
- `labcore/ai/numbers_only.py` — FACTS-only fallback + circuit breaker (3 fails / 5 min).
- `insights_run` uses numbers-only when `prefer_mock`, key missing, restricted workspace, or provider error.
- `tests/unit/test_ai_numbers_only.py`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ai_numbers_only.py -v --tb=line
============================== 3 passed in … ==============================
```
(combined with uptime: 5 passed in 1.36s)

## Deviations
None. Live NVIDIA path still blocked without `NVIDIA_API_KEY`.

## TODOs
Hosted prove: unset key → panel shows numbers-only within 10 s.
