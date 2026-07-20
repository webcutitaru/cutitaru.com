# cutitaru.com

Trilingual static site (RO / EN / RU) with PHP contact handling and Hestia VPS deploy.

## Build

From the project root:

```bash
# Optional: generate WebP portraits (requires Pillow)
python3 scripts/optimize_images.py

# Generate HTML, sitemap, robots.txt, llms.txt
python3 scripts/generate-site.py
```

Source of truth for page content:

- `scripts/generate-site.py` — home, service pages, SEO files
- `scripts/site_extensions.py` — shared head, legal pages, icons, JSON-LD
- `content/legal/{ro,en,ru}/*.body.html` — legal page bodies

## Local preview

Serve the folder with PHP (MAMP, `php -S`, etc.). Copy `.env.example` to `.env` and set:

- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — contact + visit notifications
- `CONTACT_CSRF_SECRET` — HMAC secret for the contact form

PHP must be able to write under `data/` (`submissions.jsonl`, `contact_rate.json`, `visit_notify_rate.json`).

## Deploy (Hestia VPS)

From the project root (after generating HTML locally if needed):

```bash
# SSH key auth (preferred)
./scripts/hestia-deploy.sh

# Or password auth
SSHPASS='…' ./scripts/hestia-deploy.sh
```

Defaults: `root@85.121.178.244` → `/home/admin/web/cutitaru.com/public_html`. Override with `DEPLOY_HOST` / `DEPLOY_PATH` / `DEPLOY_OWNER`.

`.env` is **not** in Git — create it on the server with production secrets. Runtime data under `data/` is preserved on deploy.

## Contact form security

- `contact_token.php` (GET) returns `{ts, token}` signed with `CONTACT_CSRF_SECRET`
- `contact.php` validates CSRF (1-hour window), rate-limits 5 submissions/hour/IP, and enforces max lengths (name 200, message 5000)
