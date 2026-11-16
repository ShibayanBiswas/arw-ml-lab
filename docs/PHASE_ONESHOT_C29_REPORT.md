# Phase oneshot-c29 — CLE.P deepen + ONNX/skops export

## Built
- CLE.P additions: `TOP_CONFUSIONS`, `CLASS_PRED_ERROR`, `SUPPORT_BARS`, `PRECISION_AT_K`, `CONFIDENCE_ERRORS`, `REPORT_HEATMAP`, `CM_COUNTS` / `CM_NORM` aliases (wired in `run_classification_eval`).
- REE.P: `ABS_RESID`, `ERROR_HIST`.
- `labcore/export/` — `skops_store` (sha256) + `onnx_export` (skl2onnx → onnxruntime parity).
- Pins: `skl2onnx==1.20.0`, `onnx==1.23.2`, `onnxruntime==1.23.0` in `ml-core.txt` + ARCHITECTURE §44 rows.
- API: `POST /api/v1/models/export-demo` (+ wire `preprocess` + `export_models` in `main.py`).

## Tests (real)
```
pytest tests/unit/test_export_onnx_skops.py \
  tests/unit/test_phase2_cont2_tune_cv.py::test_expanded_cle_plots_ds4 \
  tests/unit/test_phase2_cont2_tune_cv.py::test_expanded_ree_plots_ds12_fixture \
  tests/unit/test_import_allowlist.py -q
→ 5 passed
```

## Still deferred
- Anchors (`alibi` BSL) — optional-licence-review only.
- FS7/9–13/16–18 — TradingLab submodule empty.
- Full CLE.P 45 / REE.P 36 catalogues (more IDs remain).
- Lockfile regen for worker images (CI installs from `.txt` pins).

## Anchors / ONNX decision
Anchors stay off (rule 70 / BSL). ONNX is now first-class with parity test.
