# Phase oneshot-c227 — train API injects workspace_id for MI-16

## Built
- `POST /api/v1/experiments/train` adds `workspace_id` to the Celery payload so hold-out `audit_log` rows can reference the real workspace UUID (pairs with c225–c226).

## Tests
Covered by existing holdout unit tests + router payload shape (no new secret values).
