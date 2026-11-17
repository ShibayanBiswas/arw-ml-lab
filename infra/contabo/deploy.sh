#!/usr/bin/env bash
# deploy.sh <new_tag>: pull, start, health-check, roll back on failure.
set -euo pipefail
cd /opt/arw-ml-lab
NEW="$1"; touch .deploy.env
PREV="$(grep -E '^IMAGE_TAG=' .deploy.env | cut -d= -f2 || true)"
C="docker compose --env-file .env --env-file .deploy.env -f docker-compose.prod.yml"
printf 'IMAGE_TAG=%s\nPREV_IMAGE_TAG=%s\nGHCR_OWNER=shibayanbiswas\n' "$NEW" "$PREV" > .deploy.env
$C pull --quiet
$C up -d --remove-orphans
for i in $(seq 1 30); do
  if $C exec -T lab-api python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz',timeout=3).status==200 else 1)"; then
    echo "healthy: $NEW"; docker image prune -af --filter "until=168h" >/dev/null || true; exit 0
  fi
  sleep 5
done
echo "UNHEALTHY: rolling back to ${PREV:-<none>}" >&2
$C logs --tail 200 lab-api >&2 || true
if [ -n "$PREV" ]; then
  printf 'IMAGE_TAG=%s\nPREV_IMAGE_TAG=%s\nGHCR_OWNER=shibayanbiswas\n' "$PREV" "$PREV" > .deploy.env
  $C up -d --remove-orphans
fi
exit 1
