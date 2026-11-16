# Phase oneshot-c15 — e2e httpx smoke + Locust skeleton

**Date:** 16 Nov 2026

## Built
- `tests/e2e/test_hosted_frontend_smoke.py` — GET `/login` and `/` against Vercel (`E2E_STRICT=1` in kit-checks).
- `tests/load/locustfile.py` — Locust frontend load skeleton (excluded from pytest recurse).
- Fix: ruff-format on FS15 assertion from c14.

## Notes
- Local SSL timeouts soft-skip unless `E2E_STRICT`.
- Playwright browser suite still pending; this is the thin Phase 7 gate.
