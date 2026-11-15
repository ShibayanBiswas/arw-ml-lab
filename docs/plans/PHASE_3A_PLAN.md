# Phase 3A — Prediction Studio thin + deploy sync

Approved plan: `phase_3a_predict_thin_883f9517`.

## Locked decisions

1. **Thin 3A:** DS3 end-to-end first — train → feature contract → template CSV → PV core → batch score; custom form from contract. Full §45 (Playwright, 1M chunks, DS12/22/18/33, all PV codes, sequential lookback) → **3A-cont**.
2. **Never refit** at predict time; saved pipeline + contract only (ADR-0012 / ADR-0013).
3. **Reuse kit:** prediction migrations, pgTAP, `data/samples/predict/`, `tests/unit/test_predict_samples.py`.
4. **Deploy:** sole `arw-ml-lab` (ADR-0011); push + Vercel READY + STOP.

## Workstreams

1. `labcore/predict/validate.py` + `template.py`; persist `feature_contract` + champion pipeline → `MODEL_STORE` on train.
2. API: template, sample-row, batch validate+score (JSON + upload + DS3 sample), formula-safe CSV.
3. Frontend: Predict mode chooser, `BatchPredictPanel`, `CustomPredictForm`.
4. Unit ACs, ADR-0013, report, PROGRESS, commit, push, READY.

## Acceptance (thin)

- [x] `test_predict_samples.py` green
- [x] DS3: template → predict sample → 0 blocking PVs → scored
- [x] PV04/05/06/08 unit tests
- [x] Single vs batch parity 1e-9 on 30 rows
- [x] Custom form from contract (UI)
- [ ] CI green; Vercel `arw-ml-lab` READY only; STOP
