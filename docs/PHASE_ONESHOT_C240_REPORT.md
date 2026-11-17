# Phase oneshot-c240 — AI.RESILIENT.CHAT

## Built
- `labcore/ai/resilient.py` — `resilient_chat()` wraps provider calls with process-local circuit breaker; TimeoutError/other failures → numbers-only within 10s.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ai_resilient_chat.py -q --tb=short
..                                                                       [100%]
EXIT:0
```
