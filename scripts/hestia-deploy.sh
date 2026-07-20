#!/usr/bin/env bash
# Deploy whitelist to Hestia VPS public_html (.env stays only on the server)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DEPLOY_HOST="${DEPLOY_HOST:-root@85.121.178.244}"
DEPLOY_PATH="${DEPLOY_PATH:-/home/admin/web/cutitaru.com/public_html}"
DEPLOY_OWNER="${DEPLOY_OWNER:-admin:www-data}"

if [ -n "${SSHPASS:-}" ]; then
  RSYNC_RSH='sshpass -e ssh -T -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no'
  ssh_cmd() {
    sshpass -e ssh -T -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no "$@"
  }
else
  RSYNC_RSH='ssh -o StrictHostKeyChecking=accept-new'
  ssh_cmd() { ssh -o StrictHostKeyChecking=accept-new "$@"; }
fi

REMOTE="${DEPLOY_HOST}:${DEPLOY_PATH}"

echo "Deploy → ${REMOTE}"

rsync_dir() {
  local src="$1"
  local dest="$2"
  shift 2
  rsync -avz --delete -e "$RSYNC_RSH" --exclude '.DS_Store' "$@" "$src" "$dest"
}

rsync_dir ./assets/ "${REMOTE}/assets/"
rsync_dir ./css/ "${REMOTE}/css/"
rsync_dir ./js/ "${REMOTE}/js/"
rsync_dir ./includes/ "${REMOTE}/includes/"
rsync_dir ./en/ "${REMOTE}/en/"
rsync_dir ./ru/ "${REMOTE}/ru/"

rsync -avz -e "$RSYNC_RSH" \
  --exclude '.env' \
  --exclude '.env.*' \
  --exclude 'submissions.jsonl' \
  --exclude 'contact_rate.json' \
  --exclude 'visit_notify_rate.json' \
  --exclude '.DS_Store' \
  ./data/ "${REMOTE}/data/"

# Root files only (no directory recursion)
rsync -avz -e "$RSYNC_RSH" \
  --include '*.php' \
  --include '*.html' \
  --include 'cutitaru-logo.png' \
  --include 'robots.txt' \
  --include 'sitemap.xml' \
  --include 'llms.txt' \
  --exclude '*' \
  ./ "${REMOTE}/"

MARKER="$(date -u +%Y-%m-%dT%H:%M:%SZ) cutitaru-hestia-deploy"
ssh_cmd "$DEPLOY_HOST" "rm -rf '$DEPLOY_PATH/.git' '$DEPLOY_PATH/content' '$DEPLOY_PATH/scripts' '$DEPLOY_PATH/.cursor' 2>/dev/null || true; chown -R '$DEPLOY_OWNER' '$DEPLOY_PATH'; find '$DEPLOY_PATH' -type d -exec chmod 755 {} +; find '$DEPLOY_PATH' -type f -exec chmod 644 {} +; chmod 640 '$DEPLOY_PATH/.env' 2>/dev/null || true; printf '%s\n' '$MARKER' > '$DEPLOY_PATH/.deploy-marker'; chown '$DEPLOY_OWNER' '$DEPLOY_PATH/.deploy-marker'; chmod 644 '$DEPLOY_PATH/.deploy-marker'"

echo "Deploy done: $MARKER"
