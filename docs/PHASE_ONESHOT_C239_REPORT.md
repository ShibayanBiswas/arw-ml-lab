# Phase oneshot-c239 — OPS.LAB_API.HTTPS

## Built
- Contract that Contabo/DEPLOY docs require HTTPS for `LAB_API_URL` / `NEXT_PUBLIC_LAB_API_URL` (mixed-content defence).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_lab_api_https.py -q --tb=short
.                                                                        [100%]
EXIT:0
```
