# Phase oneshot-c221 — OPS.BACKUP.SCRIPT

## Built
- `scripts/backup_contabo.sh` — Redis BGSAVE + volume tar, encrypted config/`.env`, rclone sync for `models/` + `datasets/`, off-site copy, 7-day local retention (DEPLOY_CONTABO §10).
- `labcore/ops/backup_script_contract.py` — offline token contract.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_backup_script.py -q --tb=line
.                                                                        [100%]
EXIT:0
```

## Hosted
Cron install (`30 3 * * *`) and restore drill still **blocked** on Contabo host secrets.
