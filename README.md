# cutitaru.com

Trilingual static site (RO / EN / RU) with PHP contact handling and cPanel deploy.

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

## Deploy (cPanel)

Git push triggers `.cpanel.yml`, which runs `scripts/cpanel-deploy.sh`. The script:

1. Runs `python3 scripts/generate-site.py`
2. Copies whitelisted assets, HTML, PHP, and SEO files to `public_html`

`.env` is **not** in Git — create it on the server with production secrets.

## Contact form security

- `contact_token.php` (GET) returns `{ts, token}` signed with `CONTACT_CSRF_SECRET`
- `contact.php` validates CSRF (1-hour window), rate-limits 5 submissions/hour/IP, and enforces max lengths (name 200, message 5000)
