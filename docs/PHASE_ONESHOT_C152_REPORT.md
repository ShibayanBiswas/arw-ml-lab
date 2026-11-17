# Phase oneshot-c152 — SEC.MODEL.LOAD

## Built
- `labcore/security/model_load_policy.py` — **SEC-06** policy: lab-store path/key checks, sha256 verification, sklearn via **skops** only, `torch.load(weights_only=True)`; rejects user uploads and pickle/joblib suffixes; artefact **`SEC.MODEL.LOAD`**, seed **42**.
- `labcore/security/__init__.py` — exports model-load helpers.
- `docs/STRESS_TEST.md` — **ST-SEC-06** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec06_model_load.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 7 passed in 53.29s ==============================
```

## Notes
- Closes **ST-SEC-06** (High) offline; prediction worker registry URI + signed fetch wiring remains Phase 3A.
- Distinct from oneshot-c151 **SEC.CORS.BEARER** (ST-SEC-07) and oneshot-c150 **SEC.UPLOAD.GUARD** (ST-SEC-05).
- Seed **42**; no Contabo / live model store.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated hashes; skops round-trip + torch state dict from real saves.
- [x] Import allowlist green.
- [x] Rule 70: skops/torch/sklearn pins unchanged.

**Ship commit:** `0958a48`