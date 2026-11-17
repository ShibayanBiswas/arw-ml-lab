# Security scans (Phase 7)

Artefact **`SEC.ZAP.BASELINE`** (`manifest.json`, seed 42).

| Tool | Status | How |
|---|---|---|
| OWASP ZAP baseline (Vercel shell) | config only | `zap-baseline.yaml` — public pages, excludes `/api/*` proxy |
| OWASP ZAP baseline (lab-api public) | config only | `zap-baseline-lab-api.yaml` — `GET /healthz` + `GET /api/v1/catalog*` |
| axe-core | pending Playwright | ship with browser e2e |
| Locust | public API scenario | `tests/load/locustfile.py` (`LOAD.P.HEALTHZ_CATALOG`) |

## Manual ZAP (Docker)

From repo root (PowerShell paths adjusted):

```text
docker run --rm -v ${PWD}/tests/security:/zap/wrk owasp/zap2docker-stable zap-baseline.py -t https://arw-ml-lab.vercel.app -c zap-baseline.yaml

docker run --rm -v ${PWD}/tests/security:/zap/wrk owasp/zap2docker-stable zap-baseline.py -t http://127.0.0.1:8000 -c zap-baseline-lab-api.yaml
```

Replace the `-t` host with `LAB_API_URL` when the API is deployed. ZAP is not run in CI until hosts are reachable; structure is guarded by `tests/unit/test_sec_zap_baseline_config.py`.

Hosted API smoke remains blocked until deploy secrets are set (Contabo path documented in `DEPLOY_CONTABO.md`).
