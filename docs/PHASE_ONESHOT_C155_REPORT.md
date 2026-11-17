# Phase oneshot-c155 — OPS.LAB_BEAT

## Built
- `labcore/ops/lab_beat_contract.py` — **ST-OPS-05** contract: hourly `lab-beat` on Render (`render.yaml` cron + `dockerCommand`) and Contabo (`docker-compose.prod.yml` loop + `sleep 3600`); `expired_prediction_jobs()` in hardening migration; artefact **`OPS.LAB_BEAT`**, seed **42**.
- `tests/unit/test_ops_lab_beat_contract.py` — repo blueprint checks + negative compose fixture.
- `docs/STRESS_TEST.md` — **ST-OPS-05** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_lab_beat_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 6 passed in 3.72s ==============================
```

## Notes
- Closes **ST-OPS-05** (High) offline — next partial STRESS row after **ST-OPS-03** (typical c154 lane).
- Distinct from oneshot-c153 **OPS.CI.SUPABASE_CLI** (**ST-OPS-10**).
- Distinct from oneshot-c152 **SEC.MODEL.LOAD** (**ST-SEC-06**).
- Maintenance implementation remains `backend/worker/maintenance.py` (c101/c108/c110); this oneshot adds enforceable deployment manifests only.
- Seed **42**; no Contabo SSH / live cron prove (Phase 8.2).

## Self-check (CURSOR_PROMPT §000)
- [x] Pins read from real `render.yaml` / `docker-compose.prod.yml` / migration; no fabricated deploy output.
- [x] Import allowlist green.
- [x] Rule 70: stdlib `re` only in new module.

**Ship commit:** `06f2ecd`