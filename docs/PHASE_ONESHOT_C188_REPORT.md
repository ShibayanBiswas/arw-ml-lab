# Phase oneshot-c188 — OPS.FOLD.UPSERT

## Built
- `labcore/ops/fold_upsert.py` — ON CONFLICT SQL + in-memory upsert store keyed by `(run_id, fold, algorithm_key)`.
- `labcore/ops/fold_upsert_contract.py` — offline artefact **`OPS.FOLD.UPSERT`**.
- `supabase/migrations/20261117000000_cv_folds_upsert.sql` — `algorithm_key` + unique index.
- `tests/unit/test_ops_fold_upsert.py`.
- `docs/STRESS_TEST.md` — **ST-OPS-03** fold upserts marked tested offline.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_fold_upsert.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 2 passed (with allowlist) ==============================
```
Combined with soft-limit: 3 passed in 2.46s.

## Notes
- Seed **42**. Hosted `supabase db push` still blocked (no migrate secrets).

## Self-check
- [x] Retry upsert replaces metrics; second fold inserts.
- [x] Migration present with unique index name.
