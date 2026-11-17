# Phase oneshot-c237 — AI.NVIDIA.TIMEOUT

## Built
- `NvidiaAIClient` httpx timeout lowered from 60s → **8.0s** so provider failures can fall back to numbers-only within the §39.13 10s AC.
- Contract `AI.NVIDIA.TIMEOUT`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ai_nvidia_timeout.py tests\unit\test_ai_numbers_only.py -q --tb=line
.....                                                                    [100%]
EXIT:0
```
