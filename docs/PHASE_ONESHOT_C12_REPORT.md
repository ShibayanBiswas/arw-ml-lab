# Phase oneshot-c12 report — LIME + DiCE (§17)

**Date:** 16 Nov 2026  
**Commit:** (this commit)

## Built
- `labcore/explain/lime_tabular.py` — LimeTabularExplainer thin wrapper (`EXPLAIN.T.LIME`): weights, local fidelity R², stability Jaccard.
- `labcore/explain/dice_cf.py` — dice-ml `Dice` counterfactuals (`EXPLAIN.T.DICE`): CF table + mean pairwise L1 diversity.
- `POST /api/v1/explain/{model_id}` methods: `lime`, `dice` (plus existing shap/permutation).
- ExplainWorkbench UI: method select includes LIME + DiCE.
- Allowlist map `dice_ml` → `dice-ml`.
- Admin route wiring for AdminWorkbench (was missing from page.tsx).

## Tests (real)
```
.\.venv\Scripts\python -m pytest tests/unit/test_explain_lime_dice.py tests/unit/test_import_allowlist.py -q --tb=short
# .. passed (LIME + DiCE + allowlist)
```

## Deviations / TODOs
- LIME API path uses `num_samples=1000` (not 5000) for latency; unit test uses 800.
- Anchors remain off (alibi BSL licence).
- ONNX export / full SHAP plot matrix still open.
