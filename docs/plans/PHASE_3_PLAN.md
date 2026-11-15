# Phase 3 — Explain + Predict + UQ thin + deploy sync

Approved plan: `deploy_fix_phase_3_c63ae057` (Workstream A = 2C hygiene; Workstream B = Phase 3 thin).

## Locked decisions

1. **Thin before full §17/§21/§22/§25:** TreeSHAP additivity, PDP=mean ICE, MAPIE split conformal (reg 88–92% @90%, APS ≥89%), CalibratedClassifierCV ECE drop, feature contract + predict_single/batch (never refit). Full catalogues → 3-cont / 3A.
2. **Libraries only (rule 70):** `shap`, `sklearn.inspection`, `mapie`, `sklearn.calibration` / `FrozenEstimator`, `jsonschema` for contracts.
3. **Sole Vercel project:** `arw-ml-lab` only (ADR-0011).
4. **Deploy sync (ADR-0006):** push `origin/main`, confirm Vercel READY.

## Acceptance (thin)

- [ ] TreeSHAP |Σφ + E[f] − f(x)| < 1e-6  
- [ ] PDP equals mean ICE  
- [ ] Split-conformal 90% coverage in 88–92% on DS12 subsample  
- [ ] APS coverage ≥ 89%  
- [ ] Calibration reduces ECE  
- [ ] Feature contract validates schema; no identifier values  
- [ ] Commit + push + arw-ml-lab READY only  
