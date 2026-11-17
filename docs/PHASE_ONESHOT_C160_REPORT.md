# Phase oneshot-c160 — OPS.GPU.WORKER

## Built
- `labcore/ops/gpu_worker_contract.py` — **ST-OPS-11** / DEPLOY_CONTABO §12 offline contract: `LAB_GPU_WORKER=false` on `worker-train`, §12 documents HTTP 422, experiments router maps `assert_gpu_allowed` → 422, registry lists GPU-only keys; artefact **`OPS.GPU.WORKER`**, seed **42**.
- `tests/unit/test_ops_gpu_worker_contract.py` — contract negatives + API train/tune 422 for `seq.xlstm` without `LAB_GPU_WORKER`.
- `docs/STRESS_TEST.md` — **ST-OPS-11** → `fixed + tested`; v2.3 note links §12 GPU refusal.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_gpu_worker_contract.py tests\unit\test_import_allowlist.py -v --tb=short
======================== 8 passed, 1 warning in 40.20s ========================
```

## Notes
- Distinct from oneshot-c158 (**OPS.OTEL.STUB** / **MI.HOLDOUT.REUSE** / **SEC.FEATURE_CONTRACT.IDENTIFIER**).
- Distinct from oneshot-c157 **OPS.DEPLOY.ORDERING**, c156 **OPS.PREDICTION.RETENTION**, c155 **OPS.LAB_BEAT**.
- Hosted GPU worker registration (second VPS / WireGuard) stays Phase 8.2; this slice is offline refusal only.
- Seed **42**; no Contabo / NVIDIA / TradingLab.

## Self-check (CURSOR_PROMPT §000)
- [x] HTTP 422 responses from real FastAPI TestClient runs; no fabricated status codes.
- [x] Import allowlist green.
- [x] Rule 70: contract module is stdlib + existing registry/guards only.

**Ship commit:** _(filled after commit)_