# Phase 1A — AI Dataset Intake / Auto-Setup (§33)

Approved plan source: `phase_1a_intake_d480a96f`.

## Locked decisions

1. TradingLab labels: propose derived financial targets as JSON builders only (Phase 5); never propose raw Close as target.
2. HorizonGuard: thin `labcore/intake/horizon.py` (§20 caps); full TS slider stays Phase 4.
3. Libraries: `exchange-calendars`, `rapidfuzz` in requirements + §44; MI/PSI/KS via sklearn/scipy; ACF via statsmodels.
4. Persistence: in-memory proposal store for API/tests; migration + RLS for hosted.
5. After ingest/sample: enqueue `lab.intake.run` so Intake Review has a proposal.
6. LLM adjudicator deferred to Phase 6; rule-based proposals only.

## Workstreams

A. Migration + RLS — intake detail tables, `parent_version_id`  
B. `labcore/intake/` — D1–D8, weights, validator, pipeline  
C. API §33.12 + Celery + confirm 422  
D. Intake Review UI  
E. Golden tests + synthetic leak  
F. Report, PROGRESS, commit, STOP

## AC summary

Golden §33.14 on DS3/12/18/22/24/27/28/30; synthetic leakage; ambiguous dates; versioning diff/rename/breaking; hard-exclude 422; intake timing soft-record if >45s.
