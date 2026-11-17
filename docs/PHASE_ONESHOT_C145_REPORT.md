# Phase oneshot-c145 — SEC.ZAP.BASELINE

## Built
- `tests/security/manifest.json` — artefact **`SEC.ZAP.BASELINE`**, seed **42**, documents both policy files.
- `tests/security/zap-baseline-lab-api.yaml` — ZAP context for unauthenticated **`GET /healthz`** and **`GET /api/v1/catalog*`** (no Bearer / secrets).
- `tests/security/zap-baseline.yaml` — public Vercel shell polish: tighter include path, exclude source maps, extra header rule thresholds.
- `tests/security/README.md` — Docker run lines for frontend + lab-api configs.
- Regression: `tests/unit/test_sec_zap_baseline_config.py` (+ import allowlist).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec_zap_baseline_config.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 4 passed in 3.63s ==============================
```

## Notes
- Distinct from oneshot-c144 **LOAD.P.HEALTHZ_CATALOG** (Locust `/healthz` + `/catalog`); c145 is OWASP ZAP policy only — no live scan in CI until hosts are up.
- Pairs with oneshot-c23 initial `zap-baseline.yaml`; c145 splits lab-api public surface and adds manifest + pytest contract.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated scan results; ZAP not executed here, structure validated only.
- [x] Manifest `seed: 42`.
- [x] Import allowlist green.

**Ship commit:** (this commit)