# Phase oneshot-c223 — OPS.DEPLOY.BACKUP_SCP

## Built
- `deploy.yml` scp of `scripts/backup_contabo.sh` → `/opt/arw-ml-lab/scripts/` (chmod 750) alongside compose/Caddy/deploy.sh.
- `DEPLOY_CONTABO.md` §10 names `backup_contabo.sh`.
- Contract `OPS.DEPLOY.BACKUP_SCP`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_backup_script.py tests\unit\test_ops_deploy_backup_scp.py -q --tb=line
..                                                                       [100%]
EXIT:0
```
