# Phase oneshot-c224 — OPS.ACTIONS.NODE

## Built
- Bumped workflow actions off Node-20-era majors:
  - `actions/checkout@v6`, `actions/setup-node@v6`, `actions/setup-python@v6`
  - `pnpm/action-setup@v6`
  - `docker/setup-buildx-action@v4`, `docker/login-action@v4`, `docker/build-push-action@v7`
- Contract `labcore/ops/actions_node_runtime_contract.py` fails CI if banned majors return.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_actions_node.py -q --tb=short
.                                                                        [100%]
EXIT:0
```

## Note
Hosted CI still blocked on Actions billing; pin bump verified offline only.
