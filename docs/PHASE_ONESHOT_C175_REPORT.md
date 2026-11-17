# Phase oneshot-c175 — MI.MULTICOLLINEARITY

## Built
- `labcore/integrity/multicollinearity_policy.py` — **MI-14** VIF / correlation thresholds aligned with EDA table.
- `labcore/integrity/multicollinearity_contract.py` — offline artefact **`MI.MULTICOLLINEARITY`** for ST-ML-02 (collinear VIF, `EDA.T.VIF`, `vif.high` insights).
- `tests/unit/test_mi_multicollinearity_contract.py` — fixture checks, manifest, negative monkeypatch.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.MULTICOLLINEARITY** MI-14.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_multicollinearity_contract.py tests\unit\test_import_allowlist.py -v --tb=short
======================= 4 passed, 16 warnings in 34.53s ========================
```

## Notes
- Distinct from oneshot-c174 **MI.MULTI.TARGET** (MI-13); c175 is VIF / multicollinearity only offline.
- Wraps statsmodels `variance_inflation_factor`, `table_vif`, and `run_eda_rules`; no duplicate VIF math in the contract.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Collinear fixture |r(x1,x2)| ≥ 0.9 and VIF high on dependent numerics only.
- [x] `EDA.T.VIF` flags x1 or x2 `high`, x3 not high.
- [x] Insights emit `vif.high` for collinear columns.
- [x] Import allowlist green.
- [x] Rule 70: statsmodels VIF + existing EDA/insights paths only.

**Ship commit:** `92e191a`