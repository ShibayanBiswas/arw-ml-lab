# Phase oneshot-c199 — OPS.UPTIME.EXTERNAL

## Built
- `labcore/ops/uptime_monitor.py` — DEPLOY_CONTABO §11 + deploy.yml `/healthz` smoke contract.
- `tests/unit/test_ops_uptime_monitor.py`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_uptime_monitor.py -v --tb=line
============================== 2 passed in 0.43s ==============================
```

## Deviations
`hosted_configured=false` until external monitor account is created (Blocked — needs Shibayan account).

## TODOs
Register healthchecks.io / UptimeRobot on `https://<LAB_API_HOSTNAME>/healthz`.
