# Phase oneshot-c178 — REP.T.BUNDLE

## Built
- `labcore/reports/reproduction_bundle.py` — offline artefact **`REP.T.BUNDLE`** for ST-UX-02 (zip: config, data sha256, notebook, core pins, stub script; **Asia/Kolkata** in manifest).
- `backend/app/routers/reports.py` — `POST /api/v1/reports/bundle`.
- `frontend/.../ReproductionBundlePanel.tsx` — Templates download; `runReportsBundle` in `api.ts`.
- `tests/unit/test_rep_t_bundle_export.py`, `test_reports_bundle_api.py`, `test_fe_reports_bundle_wb.py`.
- `docs/STRESS_TEST.md` — **ST-UX-02** offline row notes **REP.T.BUNDLE**.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_rep_t_bundle_export.py tests\unit\test_reports_bundle_api.py tests\unit\test_fe_reports_bundle_wb.py tests\unit\test_import_allowlist.py -v --tb=short
======================== 8 passed, 1 warning in 35.97s =========================
```

## Notes
- Distinct from oneshot-c177 **REP.T.LEADERBOARD**; c178 closes the ST-UX-02 offline reproduction zip slice after **REP.T.NOTEBOOK** (c141/c21).
- `data_sha256` hashes canonical run config (not raw dataset bytes); user supplies `data_sha256` on API when known.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Zip contains all six contract paths; notebook nbformat-validates.
- [x] Manifest and API response record **Asia/Kolkata**.
- [x] Core pins pulled from `worker-light.lock.txt` when present.
- [x] Import allowlist green.
- [x] Rule 70: stdlib zip/json + existing `build_reproduction_notebook` only.

**Ship commit:** `880bae2`