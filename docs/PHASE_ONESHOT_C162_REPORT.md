# Phase oneshot-c162 — OPS.STORAGE.BACKUP

## Built
- `labcore/ops/storage_backup_contract.py` — **ST-OPS-06** / **OPS-13** offline contract: mirror buckets `models` + `datasets`, `DEPLOY_CONTABO.md` §10 rclone + restore drill, `docs/DEPLOY.md` pointer, storage migration + bootstrap `backups/` dir; artefact **`OPS.STORAGE.BACKUP`**, seed **42**.
- `tests/unit/test_ops_storage_backup_contract.py` — contract positives + negative fixtures.
- `docs/DEPLOY.md` — Storage backups (OPS-13 / ST-OPS-06) section.
- `docs/DEPLOY_CONTABO.md` §10 — explicit `models/` / `datasets/` Storage row (DB backup gap).
- `docs/STRESS_TEST.md` — **ST-OPS-06** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_storage_backup_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 7 passed in 3.38s ==============================
```

## Notes
- Distinct from oneshot-c161 (expected **ST-ML-02** remainder / integrity slice — not OPS).
- Distinct from oneshot-c160 **OPS.GPU.WORKER** (**ST-OPS-11**), c158 OTel/holdout/identifier, c157 deploy ordering.
- Live `rclone` cron + quarterly restore drill on VPS stay Phase 8.2.
- Seed **42**; no Contabo SSH / live backup prove.

## Self-check (CURSOR_PROMPT §000)
- [x] Checks read real repo files; no fabricated backup paths.
- [x] Import allowlist green.
- [x] Rule 70: stdlib + pathlib only in contract module.

**Ship commit:** `4361def`