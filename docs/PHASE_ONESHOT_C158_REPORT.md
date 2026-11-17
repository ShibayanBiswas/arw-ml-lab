# Phase oneshot-c158 — Phase 8.2 hardening (offline)

## Built
- `labcore/observability/otel_stub.py` + `backend/app/observability.py` — **ST-OPS-09** OTel stub: pin contract, optional `OTEL_ENABLED` / `OTEL_EXPORTER_OTLP_ENDPOINT` / `OTEL_SERVICE_NAME`, console exporter offline; artefact **`OPS.OTEL.STUB`**, seed **42**.
- `labcore/integrity/holdout_reuse.py` + `labcore/train/run.py` — **ST-ML-04** / MI-16 hold-out reuse counter + `test.evaluation` audit row; artefact **`MI.HOLDOUT.REUSE`**.
- `labcore/predict/identifier_ban_contract.py` — **SEC-09** / §45.2 kit scan + ban on stored identifier values; artefact **`SEC.FEATURE_CONTRACT.IDENTIFIER`**.
- `docs/STRESS_TEST.md` — **ST-OPS-09**, **ST-ML-04** → `fixed + tested` (offline portions).
- `pyproject.toml` dev extra — OTel pins for local pytest parity with `api.txt`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_otel_stub.py tests\unit\test_mi_holdout_reuse.py tests\unit\test_sec09_feature_contract_identifier_ban.py tests\unit\test_import_allowlist.py -v --tb=short
======================= 12 passed, 4 warnings in 54.64s =======================
```

## Notes
- Distinct from oneshot-c157 (next STRESS open/partial item — not Contabo).
- Distinct from oneshot-c156 **OPS.PREDICTION.RETENTION** (**ST-OPS-07**), c155 **OPS.LAB_BEAT**, c147 Sentry scrubber only.
- OTLP HTTP exporter + Postgres-persisted reuse counts stay hosted Phase 8.2.
- Seed **42**; no Contabo / NVIDIA / TradingLab.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; holdout counts from in-process registry + real `run_supervised_cv` run.
- [x] Import allowlist green (`opentelemetry` → `opentelemetry-sdk`).
- [x] Rule 70: OTel instrumentation uses pinned libraries only (lazy import).

**Ship commit:** _(pending)_