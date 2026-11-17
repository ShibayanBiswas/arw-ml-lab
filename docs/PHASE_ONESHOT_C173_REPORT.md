# Phase oneshot-c173 — MI.TARGET.LEAKAGE

## Built
- `labcore/integrity/target_leakage_policy.py` — **MI-15** near-perfect predictor and post-outcome thresholds aligned with Intake D6.
- `labcore/integrity/target_leakage_contract.py` — offline artefact **`MI.TARGET.LEAKAGE`** for ST-ML-02 (stump leak, post-outcome name, Intake exclusion).
- `tests/unit/test_mi_target_leakage_contract.py` — detector fixtures, merged intake exclusion, manifest, negative monkeypatch.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.TARGET.LEAKAGE** MI-15.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_target_leakage_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 8 passed in 42.04s ==============================
```

## Notes
- Distinct from oneshot-c172 **MI.HIGH.CARD** (MI-10); c173 is Intake leakage suspects / pre-training exclusion only offline.
- Wraps existing `labcore.intake.d6_leakage.detect_leakage` and `run_intake`; no duplicate heuristics.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Near-perfect stump column flagged with `near_perfect_predictor`.
- [x] Post-outcome column name flagged with `post_outcome_name`.
- [x] Exact target duplicate excluded in merged Intake (`leakage_suspect` / `duplicate`).
- [x] Benign noise column not flagged critical.
- [x] Import allowlist green.
- [x] Rule 70: sklearn stump checks in D6 only; contract orchestrates Intake.

**Ship commit:** `8509076`