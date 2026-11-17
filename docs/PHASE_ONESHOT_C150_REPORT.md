# Phase oneshot-c150 — SEC.UPLOAD.GUARD

## Built
- `labcore/security/upload_guard.py` — SEC-05: XLSX zip ratio/size guard (PV01), `defuse_stdlib()` before openpyxl writes; artefact **`SEC.UPLOAD.GUARD`**, seed **42**.
- `labcore/predict/validate.py` — `check_zip_bomb` / `load_predict_table` delegate to `inspect_xlsx_archive`.
- `labcore/data/readers.py`, `backend/app/routers/predict.py`, `labcore/predict/template.py` — ingest + batch upload + template XLSX wired to the guard.
- `docs/STRESS_TEST.md` — **ST-SEC-05** → `fixed + tested (SEC.UPLOAD.GUARD; Parquet caps Phase 3A)`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec05_upload_guard.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 8 passed in 11.52s ==============================
(Optional regression: `test_sec07_cors_bearer.py` — 5 passed with bundle above.)
```

## Notes
- Closes **ST-SEC-05** (High) offline; distinct from oneshot-c149 **OPS.EGRESS.ALLOWLIST** (ST-OPS-08).
- Parquet row-group / column-count limits remain Phase 3A per ARCHITECTURE SEC-05 table.
- Seed **42**; no Contabo / live uploads.

## Self-check (CURSOR_PROMPT §000)
- [x] Zip-bomb thresholds match §45.3 PV01 (ratio 100, 500 MB uncompressed).
- [x] Import allowlist green.
- [x] Rule 70: defusedxml + calamine already pinned in `ml-core.txt`.

**Ship commit:** *(fill after commit)*