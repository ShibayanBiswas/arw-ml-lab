#!/usr/bin/env bash
# Nightly Contabo host backup — DEPLOY_CONTABO §10 (oneshot-c221).
# Install on the VPS as deploy:  crontab -e
#   30 3 * * * /opt/arw-ml-lab/scripts/backup_contabo.sh >>/opt/arw-ml-lab/backups/cron.log 2>&1
# Requires: docker compose stack up, REDIS_PASSWORD in /opt/arw-ml-lab/.env, optional rclone remote.
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/arw-ml-lab}"
COMPOSE_FILE="${COMPOSE_FILE:-$APP_DIR/docker-compose.prod.yml}"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/backups}"
STAMP="$(date -u +%F)"
KEEP_DAYS="${KEEP_DAYS:-7}"

cd "$APP_DIR"
# shellcheck disable=SC1091
set -a
# Load secrets without printing them
source "$APP_DIR/.env"
set +a

mkdir -p "$BACKUP_DIR"

# Redis RDB snapshot then archive the named volume bind (compose volume redis_data).
docker compose -f "$COMPOSE_FILE" exec -T redis \
  redis-cli -a "$REDIS_PASSWORD" BGSAVE >/dev/null
sleep 2
docker run --rm \
  -v "${COMPOSE_PROJECT_NAME:-arw-ml-lab}_redis_data:/data:ro" \
  -v "$BACKUP_DIR:/out" \
  alpine:3.20 \
  tar czf "/out/redis-${STAMP}.tgz" -C /data .

# Encrypt a copy of runtime config (age preferred; gpg --symmetric fallback).
CFG_TAR="$BACKUP_DIR/config-${STAMP}.tgz"
tar czf "$CFG_TAR" -C "$APP_DIR" \
  --exclude='.env' \
  docker-compose.prod.yml infra/caddy/Caddyfile 2>/dev/null || true
if command -v age >/dev/null 2>&1 && [[ -n "${BACKUP_AGE_RECIPIENT:-}" ]]; then
  age -r "$BACKUP_AGE_RECIPIENT" -o "${CFG_TAR}.age" "$CFG_TAR"
  shred -u "$CFG_TAR" 2>/dev/null || rm -f "$CFG_TAR"
elif command -v gpg >/dev/null 2>&1 && [[ -n "${BACKUP_GPG_RECIPIENT:-}" ]]; then
  gpg --batch --yes -e -r "$BACKUP_GPG_RECIPIENT" -o "${CFG_TAR}.gpg" "$CFG_TAR"
  shred -u "$CFG_TAR" 2>/dev/null || rm -f "$CFG_TAR"
fi

# Encrypted .env separately (never leave plaintext in backups/).
if command -v age >/dev/null 2>&1 && [[ -n "${BACKUP_AGE_RECIPIENT:-}" ]]; then
  age -r "$BACKUP_AGE_RECIPIENT" -o "$BACKUP_DIR/env-${STAMP}.env.age" "$APP_DIR/.env"
elif command -v gpg >/dev/null 2>&1 && [[ -n "${BACKUP_GPG_RECIPIENT:-}" ]]; then
  gpg --batch --yes -e -r "$BACKUP_GPG_RECIPIENT" -o "$BACKUP_DIR/env-${STAMP}.env.gpg" "$APP_DIR/.env"
fi

# Off-site: Supabase Storage mirrors (models/ datasets/) + local backups folder.
if command -v rclone >/dev/null 2>&1; then
  rclone sync "${RCLONE_MODELS_SRC:-supabase-s3:models}" "${RCLONE_MODELS_DST:-supabase-s3:backups/models}" --fast-list || true
  rclone sync "${RCLONE_DATASETS_SRC:-supabase-s3:datasets}" "${RCLONE_DATASETS_DST:-supabase-s3:backups/datasets}" --fast-list || true
  rclone copy "$BACKUP_DIR" "${RCLONE_OFFSITE:-supabase-s3:backups/contabo/}" --include "*-${STAMP}.*" || true
fi

# Local retention
find "$BACKUP_DIR" -type f -mtime +"$KEEP_DAYS" -name '*.tgz' -delete 2>/dev/null || true
find "$BACKUP_DIR" -type f -mtime +"$KEEP_DAYS" -name '*.age' -delete 2>/dev/null || true
find "$BACKUP_DIR" -type f -mtime +"$KEEP_DAYS" -name '*.gpg' -delete 2>/dev/null || true

echo "[backup_contabo] ok stamp=${STAMP}"
