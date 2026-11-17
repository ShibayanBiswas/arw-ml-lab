# Phase oneshot-c228 — holdout audit UUID guard

## Built
- `persist_holdout_audit_row` skips insert when `workspace_id` is not a UUID (avoids Postgres cast errors for local `offline`).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_holdout_reuse.py::test_persist_holdout_audit_row_with_mock_executor -q --tb=short
.                                                                        [100%]
EXIT:0
```
