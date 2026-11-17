# Phase oneshot-c153 — OPS.CI.SUPABASE_CLI

## Built
- `labcore/ops/ci_supabase_cli_pin.py` — **ST-OPS-10** contract: `PINNED_SUPABASE_CLI_VERSION` (`3.1.0`), workflow scanner + `assert_workflows_pin_supabase_cli`; artefact **`OPS.CI.SUPABASE_CLI`**, seed **42**.
- `tests/unit/test_ops_ci_supabase_cli_pin.py` — pins in `ci.yml` and `deploy.yml`; rejects `latest` on a temp workflow.
- `docs/STRESS_TEST.md` — **ST-OPS-10** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_ci_supabase_cli_pin.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 5 passed in 3.52s ==============================
```

## Notes
- Closes **ST-OPS-10** (Low) offline — the only row still marked `open` in STRESS_TEST after c151.
- Distinct from oneshot-c152 **SEC.MODEL.LOAD** lane (**ST-SEC-06**, High model deserialisation policy).
- Distinct from oneshot-c151 **SEC.CORS.BEARER** (**ST-SEC-07**).
- Workflows already pinned `3.1.0`; this oneshot adds an enforceable pytest contract (no live `supabase` CLI on the runner).
- Seed **42**; no Contabo / NVIDIA / live deploy.

## Self-check (CURSOR_PROMPT §000)
- [x] Pin version read from real workflow files; no fabricated CI output.
- [x] Import allowlist green.
- [x] Rule 70: stdlib `re` only in new module.

**Ship commit:** `505df46`