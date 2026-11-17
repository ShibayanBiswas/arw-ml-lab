# Phase oneshot-c157 — OPS.DEPLOY.ORDERING

## Built
- `labcore/ops/deploy_ordering_contract.py` — **ST-OPS-04** offline contract: Render `autoDeployTrigger: "off"` (no `checksPass`); `deploy.yml` ordering `migrate → build → deploy → smoke` with `supabase db push --remote`; artefact **`OPS.DEPLOY.ORDERING`**, seed **42**.
- `tests/unit/test_ops_deploy_ordering_contract.py` — repo blueprint checks + negative render/workflow fixtures.
- `docs/STRESS_TEST.md` — **ST-OPS-04** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_deploy_ordering_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 6 passed in 3.94s ==============================
```

## Notes
- Closes **ST-OPS-04** (Critical) offline — next STRESS row after **ST-OPS-07** (c156) that was `fixed` without kit tests; hosted Contabo/Render deploy prove stays Phase 8.2.
- Distinct from oneshot-c156 **OPS.PREDICTION.RETENTION** (**ST-OPS-07**), oneshot-c155 **OPS.LAB_BEAT** (**ST-OPS-05**).
- `tests/unit/test_import_allowlist.py`: map `opentelemetry` → `opentelemetry-sdk` (already pinned in `api.txt`).
- Seed **42**; no Contabo / NVIDIA / TradingLab / Actions billing.

## Self-check (CURSOR_PROMPT §000)
- [x] Contract reads real `render.yaml` and `.github/workflows/deploy.yml`; no fabricated deploy state.
- [x] Import allowlist green.
- [x] Rule 70: stdlib-only in new `labcore` module.

**Ship commit:** `c82f337`