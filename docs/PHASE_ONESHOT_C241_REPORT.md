# Phase oneshot-c241 — insights router uses resilient_chat

## Built
- `POST /api/v1/insights/run` provider path calls `resilient_chat` (circuit + numbers-only on timeout/error).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ai_insights.py tests\unit\test_ai_resilient_chat.py -q --tb=line
......                                                                   [100%]
EXIT:0
```
