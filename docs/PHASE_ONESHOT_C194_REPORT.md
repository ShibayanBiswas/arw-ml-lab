# Phase oneshot-c194 — TRAIN.REFIT.FULL API + FE wire

## Built
- `TrainConfig.refit_full` (default `True`) → `prepare_for_deployment` before champion registration in `run_supervised_cv`.
- `TrainBody.refit_full` / train Celery body → `TrainConfig`.
- TrainWorkbench checkbox `data-artefact="TRAIN.REFIT.FULL"` → `startTrain({ refit_full })`.
- `tests/unit/test_train_refit_full_wire.py`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_train_refit_full_wire.py -v --tb=line
============================= 2 passed in 18.63s ==============================
```

## Deviations
None. Contabo/Actions still blocked (see PROGRESS).

## TODOs
Hosted prove that registered model used refit-on-full when toggle on.
