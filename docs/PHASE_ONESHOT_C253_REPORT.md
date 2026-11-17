# Phase oneshot-c253 — BatchPredictPanel classification columns UI

## Built
- `BatchPredictPanel` shows `classification_columns` from the score response (`PRED.BATCH.CLF.COLS`).
- `api.ts` types include `classification_columns`.

## Tests
Offline UI wiring only (no new pytest). Prior clf column unit test remains green from c252.

## Contabo
Still blocked — `CONTABO_HOST` missing.
