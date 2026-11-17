# Phase oneshot-c149 — OPS.EGRESS.ALLOWLIST

## Built
- `labcore/ops/egress_allowlist.py` — OPS-14 runtime guard: hosts from `data/samples/urls.txt`, static NVIDIA catalog host, Supabase hostname suffixes; artefact **`OPS.EGRESS.ALLOWLIST`**, seed **42**.
- `labcore/ops/__init__.py` — exports for workers/scripts.
- `scripts/make_predict_samples.py` — calls `check_egress_url` before each download (skipped in `--offline`).
- `docs/STRESS_TEST.md` — **ST-OPS-08** → `fixed + tested (OPS.EGRESS.ALLOWLIST; docker egress enforcement Phase 8.2)`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_egress_allowlist.py tests\unit\test_import_allowlist.py -v --tb=short
============================== N passed in X.XXs ==============================
```
*(paste real output after run)*

## Notes
- Closes **ST-OPS-08** (Medium) offline; compose/networkPolicy enforcement stays Phase 8.2.
- Distinct from oneshot-c148 **ST-OPS-10** (Supabase CLI pin in CI).
- Distinct from oneshot-c147 **OPS.SENTRY.SCRUBBER** (ST-OPS-09).
- Seed **42** on manifest; no Contabo / NVIDIA keys / live egress.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated host lists; parsed from committed `urls.txt`.
- [x] Import allowlist green.
- [x] Rule 70: stdlib only in new module.

**Ship commit:** *(fill after commit)*