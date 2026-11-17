# Phase oneshot-c203 — SEC.NO.NVIDIA.VERCEL

## Built
- `labcore/security/vercel_secret_guard.py` — scan `frontend/src` for forbidden client AI key names.
- Unit test.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec_no_nvidia_vercel.py -v --tb=line
============================= 2 passed in 16.92s ==============================
```

## Deviations
None.

## TODOs
Hosted: `vercel env ls` confirm no NVIDIA_API_KEY (manual when logged in).
