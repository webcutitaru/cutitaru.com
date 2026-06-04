#!/bin/sh
# Copiere whitelist în public_html (.env rămâne doar pe server, nu din Git)

DEPLOYPATH="${DEPLOYPATH:-/home/awxisina/public_html/}"
HTACCESS_PATHS="data/.htaccess"
DEPLOY_DIRS="assets css data includes js"

if [ ! -d "$DEPLOYPATH" ]; then
  echo "ERROR: DEPLOYPATH missing: $DEPLOYPATH" >&2
  exit 1
fi

chmod 755 "$DEPLOYPATH" 2>/dev/null || true

copy_htaccess() {
  src="$1"
  dest="$2"
  if [ -f "$src" ]; then
    mkdir -p "$(dirname "$dest")"
    /bin/cp -f "$src" "$dest"
    /bin/chmod 644 "$dest"
  fi
}

for rel in $HTACCESS_PATHS; do
  copy_htaccess "$rel" "$DEPLOYPATH$rel"
done

for dir in $DEPLOY_DIRS; do
  if [ -d "$dir" ]; then
    /bin/cp -R "$dir" "$DEPLOYPATH" 2>/dev/null || true
  fi
done

for f in ./*.php; do
  [ -f "$f" ] || continue
  /bin/cp -f "$f" "$DEPLOYPATH" 2>/dev/null || true
done

for f in ./*.html cutitaru-logo.png; do
  [ -f "$f" ] || continue
  /bin/cp -f "$f" "$DEPLOYPATH" 2>/dev/null || true
done

for rel in $HTACCESS_PATHS; do
  copy_htaccess "$rel" "$DEPLOYPATH$rel"
done

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) cutitaru-deploy" > "$DEPLOYPATH.deploy-marker"
chmod 644 "$DEPLOYPATH.deploy-marker"
