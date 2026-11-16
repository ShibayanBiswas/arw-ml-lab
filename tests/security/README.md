# Security scans (Phase 7)

| Tool | Status | How |
|---|---|---|
| OWASP ZAP baseline | config only | `tests/security/zap-baseline.yaml` — needs live host |
| axe-core | pending Playwright | ship with browser e2e |
| Locust | skeleton | `tests/load/locustfile.py` |

Hosted API smoke remains blocked until Render payment + secrets.
