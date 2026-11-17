#!/usr/bin/env bash
# Hosted smoke: healthz → load DS1 sample → run EDA (AUTH_TEST_BYPASS staging only).
# Usage (Contabo v2.3): LAB_API_URL=https://<LAB_API_HOSTNAME> bash scripts/smoke_hosted.sh
# Legacy Render: LAB_API_URL=https://lab-api.onrender.com bash scripts/smoke_hosted.sh
set -euo pipefail

API="${LAB_API_URL:?LAB_API_URL required}"
API="${API%/}"

HDR=(-H "Authorization: Bearer test" -H "X-Test-Role: scientist" \
  -H "X-Test-User-Id: 00000000-0000-0000-0000-000000000099" \
  -H "X-Test-Workspace-Id: 00000000-0000-0000-0000-000000000010" \
  -H "Content-Type: application/json")

echo "== healthz =="
curl -fsS "$API/healthz" | tee /tmp/lab_healthz.json
echo

echo "== load DS1 =="
JOB=$(curl -fsS -X POST "${HDR[@]}" "$API/api/v1/datasets/samples/DS1/load")
echo "$JOB"
JOB_ID=$(python -c "import json,sys; print(json.load(sys.stdin)['job_id'])" <<<"$JOB")

for i in $(seq 1 60); do
  ST=$(curl -fsS "${HDR[@]}" "$API/api/v1/jobs/$JOB_ID")
  STATUS=$(python -c "import json,sys; print(json.load(sys.stdin)['status'])" <<<"$ST")
  echo "ingest status=$STATUS"
  if [ "$STATUS" = "done" ]; then
    DS_ID=$(python -c "import json,sys; print(json.load(sys.stdin)['result']['dataset_id'])" <<<"$ST")
    break
  fi
  if [ "$STATUS" = "error" ]; then
    echo "$ST"
    exit 1
  fi
  sleep 2
done

echo "== eda $DS_ID =="
EDA=$(curl -fsS -X POST "${HDR[@]}" "$API/api/v1/eda/$DS_ID/run")
echo "$EDA"
EDA_JOB=$(python -c "import json,sys; print(json.load(sys.stdin)['job_id'])" <<<"$EDA")

for i in $(seq 1 90); do
  ST=$(curl -fsS "${HDR[@]}" "$API/api/v1/jobs/$EDA_JOB")
  STATUS=$(python -c "import json,sys; print(json.load(sys.stdin)['status'])" <<<"$ST")
  echo "eda status=$STATUS"
  if [ "$STATUS" = "done" ]; then
    python -c "import json,sys; r=json.load(sys.stdin); assert r['result']['n_artefacts']>=19; print('eda artefacts', r['result']['n_artefacts'])" <<<"$ST"
    echo "SMOKE OK"
    exit 0
  fi
  if [ "$STATUS" = "error" ]; then
    echo "$ST"
    exit 1
  fi
  sleep 3
done
echo "EDA timeout"
exit 1
