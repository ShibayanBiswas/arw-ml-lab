# Phase oneshot-c171 — MI.HORIZON.GUARD

## Built
- `labcore/integrity/horizon_guard_policy.py` — **MI-17** `horizon_request_allowed` / `horizon_reject_reasons` via canonical `compute_horizon_guard`.
- `labcore/integrity/horizon_guard_contract.py` — offline artefact **`MI.HORIZON.GUARD`** for ST-ML-02 (DS22 h_max=24, over-request reject, small-n cap).
- `tests/unit/test_mi_horizon_guard_contract.py` — fixture checks, manifest, negative monkeypatch.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.HORIZON.GUARD** MI-17.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_horizon_guard_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 6 passed in 17.52s ==============================
```

## Notes
- Distinct from oneshot-c170 **MI.CLASS.RESAMPLE** lane (MI-07 resampler never sees validation rows); c171 is forecast horizon only offline.
- API/worker 422 wiring already covered in `tests/unit/test_timeseries_api.py`; this kit is the ST-ML-02 MI-17 manifest.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] DS22 structural h_max=24 from real `compute_horizon_guard`.
- [x] h_request=100 rejected with `reject_reasons`; h=12 allowed.
- [x] n=40 respects n/4 cap and rejects above h_max.
- [x] Import allowlist green.
- [x] Rule 70: wraps existing `labcore.timeseries.horizon_guard` only.

**Ship commit:** _pending commit_