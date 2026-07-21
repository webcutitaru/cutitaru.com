"""Shared site generation helpers (head, SEO, legal pages, icons, JSON-LD)."""
from __future__ import annotations

import json
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _SCRIPTS.parent
_CONTENT = _ROOT / "content" / "legal"

# Bump when css/js change so browsers ignore nginx expires:max cache
ASSET_VERSION = "20260721c"

SITE: str = ""
LANGS: dict = {}
HOME: dict = {}
LEGAL_FILES: dict = {}
SERVICE_LINKS: dict = {}
SERVICE_PAGES: dict = {}
LANG_UI: dict = {}
asset_prefix = None  # type: ignore
portrait_url = None  # type: ignore
portrait_abs = None  # type: ignore
lang_href = None  # type: ignore


def asset_url(ap: str, path: str) -> str:
    return f"{ap}{path}?v={ASSET_VERSION}"


def bind(gen: object) -> None:
    """Wire references from generate-site module (call once before build)."""
    global SITE, LANGS, HOME, LEGAL_FILES, SERVICE_LINKS, SERVICE_PAGES, LANG_UI
    global asset_prefix, portrait_url, portrait_abs, lang_href
    SITE = gen.SITE
    LANGS = gen.LANGS
    HOME = gen.HOME
    LEGAL_FILES = gen.LEGAL_FILES
    SERVICE_LINKS = gen.SERVICE_LINKS
    SERVICE_PAGES = gen.SERVICE_PAGES
    LANG_UI = gen.LANG_UI
    asset_prefix = gen.asset_prefix
    portrait_url = gen.portrait_url
    portrait_abs = gen.portrait_abs
    lang_href = gen.lang_href


def _cls(class_: str) -> str:
    return f' class="{class_}"' if class_ else ""


def _svg_open(class_: str, view_box: str = "0 0 24 24", fill: str = "none") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}"'
        f' fill="{fill}"{_cls(class_)} aria-hidden="true" focusable="false">'
    )


ICONS: dict[str, str] = {
    "globe": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        '{attrs} aria-hidden="true" focusable="false">'
        '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>'
        '<path d="M2 12h20"/></svg>'
    ),
    "chevron-left": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        '{attrs} aria-hidden="true" focusable="false"><path d="m15 18-6-6 6-6"/></svg>'
    ),
    "chevron-right": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        '{attrs} aria-hidden="true" focusable="false"><path d="m9 18 6-6-6-6"/></svg>'
    ),
    "instagram": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" '
        '{attrs} aria-hidden="true" focusable="false">'
        '<path d="M7.8 2h8.4A5.8 5.8 0 0 1 22 7.8v8.4a5.8 5.8 0 0 1-5.8 5.8H7.8A5.8 5.8 0 0 1 2 16.2V7.8A5.8 5.8 0 0 1 7.8 2m-.2 2A3.6 3.6 0 0 0 4 7.6v8.8a3.6 3.6 0 0 0 3.6 3.6h8.8a3.6 3.6 0 0 0 3.6-3.6V7.6A3.6 3.6 0 0 0 16.4 4H7.6zm9.65 1.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5M12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10m0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6"/></svg>'
    ),
    "facebook": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" '
        '{attrs} aria-hidden="true" focusable="false">'
        '<path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>'
    ),
    "linkedin": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" '
        '{attrs} aria-hidden="true" focusable="false">'
        '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
    ),
    "pen-nib": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        '{attrs} aria-hidden="true" focusable="false">'
        '<path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/>'
        '<path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>'
    ),
    "laptop-code": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        '{attrs} aria-hidden="true" focusable="false">'
        '<path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45L4 16"/></svg>'
    ),
    "bullseye": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        '{attrs} aria-hidden="true" focusable="false">'
        '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
    ),
    "chart-line": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        '{attrs} aria-hidden="true" focusable="false"><path d="M3 3v18h18"/>'
        '<path d="m19 9-5 5-4-4-3 3"/></svg>'
    ),
    "shopify": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" '
        '{attrs} aria-hidden="true" focusable="false">'
        '<path d="M15.337 2.35c-.07-.004-.14-.01-.21-.01-.12 0-.24.01-.35.03-.01 0-.02 0-.03.01-.01 0-.02-.01-.03-.01-.11-.02-.23-.03-.35-.03-.07 0-.14.006-.21.01C9.813 2.7 6.5 5.5 6.5 9.2c0 3.2 2.4 5.9 5.6 6.5.4.1.8.1 1.2.1.4 0 .8 0 1.2-.1 3.2-.6 5.6-3.3 5.6-6.5 0-3.7-3.313-6.5-4.763-6.85zM12 14.5c-2.9 0-5.3-2.2-5.3-5.3S9.1 4 12 4s5.3 2.2 5.3 5.2-2.4 5.3-5.3 5.3z"/>'
        '<path d="M12 6.5c-1.6 0-2.9 1.3-2.9 2.9S10.4 12.3 12 12.3s2.9-1.3 2.9-2.9S13.6 6.5 12 6.5z"/></svg>'
    ),
    "rectangle-ad": (
        '{cls}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        '{attrs} aria-hidden="true" focusable="false">'
        '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 15h2l2-3 2 6 2-4h2"/></svg>'
    ),
}


def icon(name: str, class_: str = "") -> str:
    """Return inline SVG for a named icon with optional CSS class."""
    template = ICONS[name]
    attrs = f' class="{class_}"' if class_ else ""
    return template.format(cls="", attrs=attrs)


LEGAL_UPDATED = {
    "ro": "5 iunie 2026",
    "en": "5 June 2026",
    "ru": "5 июня 2026",
}

LEGAL_PAGE_META = {
    "privacy": {
        "ro": {
            "title": "Politica de confidențialitate — cutitaru",
            "desc": "Politica de confidențialitate cutitaru — cum sunt colectate și folosite datele personale pe acest site.",
            "h1": "Politica de confidențialitate",
        },
        "en": {
            "title": "Privacy policy — cutitaru",
            "desc": "Privacy policy for cutitaru — how personal data is collected and used on this site.",
            "h1": "Privacy policy",
        },
        "ru": {
            "title": "Политика конфиденциальности — cutitaru",
            "desc": "Политика конфиденциальности cutitaru — как собираются и используются персональные данные на этом сайте.",
            "h1": "Политика конфиденциальности",
        },
    },
    "cookies": {
        "ro": {
            "title": "Politica de cookie — cutitaru",
            "desc": "Politica de cookie cutitaru — Microsoft Clarity, preferințe locale și opțiunile tale.",
            "h1": "Politica de cookie",
        },
        "en": {
            "title": "Cookie policy — cutitaru",
            "desc": "Cookie policy for cutitaru — Microsoft Clarity, local preferences, and your choices.",
            "h1": "Cookie policy",
        },
        "ru": {
            "title": "Политика cookie — cutitaru",
            "desc": "Политика cookie cutitaru — Microsoft Clarity, локальные настройки и ваш выбор.",
            "h1": "Политика cookie",
        },
    },
    "terms": {
        "ro": {
            "title": "Termeni și condiții — cutitaru",
            "desc": "Termeni și condiții pentru utilizarea site-ului cutitaru.",
            "h1": "Termeni și condiții",
        },
        "en": {
            "title": "Terms of service — cutitaru",
            "desc": "Terms of service for using the cutitaru website.",
            "h1": "Terms of service",
        },
        "ru": {
            "title": "Условия использования — cutitaru",
            "desc": "Условия использования сайта cutitaru.",
            "h1": "Условия использования",
        },
    },
}


def hreflang_block(page_key: str, lang: str) -> str:
    canonical = LANGS[lang][page_key]
    lines = [f'    <link rel="canonical" href="{SITE}{canonical}" />']
    for key, cfg in LANGS.items():
        alt = cfg.get(page_key, cfg["home"])
        lines.append(
            f'    <link rel="alternate" hreflang="{cfg["code"]}" href="{SITE}{alt}" />'
        )
    lines.append(
        f'    <link rel="alternate" hreflang="x-default" href="{SITE}{LANGS["ro"][page_key]}" />'
    )
    return "\n".join(lines)


def og_block(lang: str, title: str, desc: str, path: str) -> str:
    locale = {"ro": "ro_MD", "en": "en_US", "ru": "ru_MD"}[lang]
    alternates = []
    for key, loc in (("ro", "ro_MD"), ("en", "en_US"), ("ru", "ru_MD")):
        if key != lang:
            alternates.append(f'    <meta property="og:locale:alternate" content="{loc}" />')
    alt_block = "\n".join(alternates)
    return f"""    <meta property="og:type" content="website" />
    <meta property="og:url" content="{SITE}{path}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{desc}" />
    <meta property="og:image" content="{portrait_abs()}" />
    <meta property="og:locale" content="{locale}" />
{alt_block}
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{desc}" />
    <meta name="geo.region" content="MD" />"""


def head_common(
    lang: str,
    title: str,
    desc: str,
    path: str,
    page_key: str = "home",
    preload_portrait: bool = True,
) -> str:
    ap = asset_prefix(lang)
    html_lang = {"ro": "ro-MD", "en": "en", "ru": "ru"}[lang]
    preload_line = (
        f'    <link rel="preload" href="{portrait_url(lang)}" as="image" />\n'
        if preload_portrait
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="{desc}" />
    <title>{title}</title>
{hreflang_block(page_key, lang)}
{og_block(lang, title, desc, path)}
    <link rel="icon" href="{ap}cutitaru-logo.png" type="image/png" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&amp;family=Playfair+Display:wght@400;600;700&amp;family=Roboto+Mono:wght@400;500&amp;display=swap"
      rel="stylesheet"
    />
{preload_line}    <link rel="stylesheet" href="{asset_url(ap, 'css/styles.css')}" />"""


def home_doc_href(lang: str) -> str:
    return "index.html"


def legal_doc_href(lang: str, page_key: str) -> str:
    return LEGAL_FILES[page_key][lang]


def service_doc_href(lang: str, key: str) -> str:
    return SERVICE_LINKS[lang][key]


def replace_legal_placeholders(body: str, lang: str) -> str:
    replacements = {
        "{{HOME}}": home_doc_href(lang),
        "{{CONTACT}}": f"{home_doc_href(lang)}#contact",
        "{{PRIVACY}}": legal_doc_href(lang, "privacy"),
        "{{COOKIES}}": legal_doc_href(lang, "cookies"),
        "{{TERMS}}": legal_doc_href(lang, "terms"),
        "{{UPDATED}}": LEGAL_UPDATED[lang],
    }
    for token, value in replacements.items():
        body = body.replace(token, value)
    return body


def load_legal_body(lang: str, page_key: str) -> str:
    path = _CONTENT / lang / f"{page_key}.body.html"
    return replace_legal_placeholders(path.read_text(encoding="utf-8"), lang)


def json_ld_service(lang: str, key: str) -> str:
    p = SERVICE_PAGES[key][lang]
    page_path = LANGS[lang][key]
    page_url = SITE + page_path
    home_url = SITE + LANGS[lang]["home"]
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Service",
                "name": p["h1"],
                "description": p["desc"],
                "url": page_url,
                "provider": {"@id": SITE + "/#person"},
                "areaServed": [
                    {"@type": "Country", "name": "Moldova"},
                    {"@type": "Place", "name": "International"},
                ],
            },
            {
                "@type": "WebPage",
                "name": p["title"],
                "description": p["desc"],
                "url": page_url,
                "inLanguage": LANGS[lang]["code"],
                "isPartOf": {"@type": "WebSite", "url": home_url},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": p["home"],
                        "item": home_url,
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": p["h1"],
                        "item": page_url,
                    },
                ],
            },
        ],
    }
    return f'    <script type="application/ld+json">{json.dumps(graph, ensure_ascii=False)}</script>'


def lang_switcher_html(active: str, page_key: str = "home") -> str:
    ui = LANG_UI[active]
    options = []
    for key in ("ro", "en", "ru"):
        L = LANG_UI[key]
        href = lang_href(active, key, page_key)
        cls = "lang-dropdown__option is-active" if key == active else "lang-dropdown__option"
        aria = ' aria-selected="true"' if key == active else ""
        options.append(
            f'            <li role="option"{aria}><a class="{cls}" href="{href}" hreflang="{LANGS[key]["code"]}">{L["code"]}</a></li>'
        )
    menu = "\n".join(options)
    return f"""          <div class="lang-dropdown" data-lang-dropdown>
            <button type="button" class="lang-dropdown__toggle" aria-expanded="false" aria-haspopup="listbox" aria-label="{ui["aria"]}">
              {icon("globe")}
            </button>
            <ul class="lang-dropdown__menu" role="listbox" hidden>
{menu}
            </ul>
          </div>"""


def build_legal_page(lang: str, page_key: str) -> str:
    c = HOME[lang]
    meta = LEGAL_PAGE_META[page_key][lang]
    ap = asset_prefix(lang)
    path = LANGS[lang][page_key]
    cfg = LANGS[lang]
    home = home_doc_href(lang)

    nav = "\n".join(
        f'              <li><a href="{home}{href}">{label}</a></li>'
        for label, href in c["nav"]
    )
    footer_nav = "\n".join(
        f'                <li><a href="{home}{href}">{label}</a></li>'
        for label, href in c["nav"]
        if href != "#home"
    )

    sl = SERVICE_LINKS[lang]
    svc_footer = (
        f'<p class="footer-services"><a href="{sl["design"]}">{c["footer_services"].split(" · ")[0]}</a> · '
        f'<a href="{sl["shopify"]}">{c["footer_services"].split(" · ")[1]}</a> · '
        f'<a href="{sl["ads"]}">{c["footer_services"].split(" · ")[2]}</a></p>'
    )

    legal_priv = legal_doc_href(lang, "privacy")
    legal_terms = legal_doc_href(lang, "terms")
    legal_cookies = legal_doc_href(lang, "cookies")
    body = load_legal_body(lang, page_key)

    return f"""{head_common(lang, meta["title"], meta["desc"], path, page_key, preload_portrait=False)}
  </head>
  <body data-lang="{lang}">
    <a class="skip-link" href="#main">{c["skip"]}</a>
    <header class="site-header" role="banner">
      <div class="container nav-shell">
        <div class="nav-inner">
          <button type="button" class="nav-toggle" data-nav-toggle aria-expanded="false" aria-controls="nav-primary" aria-label="Menu">
            <span class="nav-toggle__bar" aria-hidden="true"></span>
            <span class="nav-toggle__bar" aria-hidden="true"></span>
            <span class="nav-toggle__bar" aria-hidden="true"></span>
          </button>
          <nav class="nav-primary nav-links--left" id="nav-primary" aria-label="Primary">
            <ul class="nav-links">{nav}
            </ul>
          </nav>
          <a class="nav-brand" href="{home}#home">
            <img class="nav-brand__img" src="{ap}cutitaru-logo.png" alt="cutitaru" width="160" height="48" decoding="async" />
          </a>
          {lang_switcher_html(lang, page_key)}
        </div>
        <svg class="scroll-progress-ring" aria-hidden="true" focusable="false">
          <path id="scroll-progress-path" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" pathLength="100" d="" />
        </svg>
      </div>
    </header>
    <main id="main" class="legal-page">
      <div class="container">
        <h1>{meta["h1"]}</h1>
{body}
      </div>
    </main>
    <footer class="site-footer" role="contentinfo">
      <div class="footer-cta"><div class="container"><p>{c["footer_cta_p"]}</p><a class="btn btn--primary" href="{home}#contact">{c["footer_cta_btn"]}</a></div></div>
      <div class="footer-main">
        <div class="container">
          <div class="footer-grid">
            <div>
              <a class="footer-brand" href="{home}#home"><img class="footer-brand__img" src="{ap}cutitaru-logo.png" alt="cutitaru" width="160" height="48" decoding="async" /></a>
              <p style="margin:0;max-width:16rem">{c["footer_blurb"]}</p>
              {svc_footer}
            </div>
            <div class="footer-col"><h4>{c["footer_explore"]}</h4><ul>{footer_nav}</ul></div>
            <div class="footer-aside">
              <div class="social" aria-label="Social">
                <a href="https://www.instagram.com/cut1taru/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">{icon("instagram")}</a>
                <a href="https://www.facebook.com/cutitaru.adrian" target="_blank" rel="noopener noreferrer" aria-label="Facebook">{icon("facebook")}</a>
                <a href="https://www.linkedin.com/in/cutitaru-adrian/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">{icon("linkedin")}</a>
              </div>
            </div>
          </div>
          <div class="footer-bottom">
            <span>© <span id="y"></span> CUTITARU.signature. {c["footer_rights"]}</span>
            <div class="footer-legal">
              <a href="{legal_priv}">{c["footer_privacy"]}</a>
              <a href="{legal_terms}">{c["footer_terms"]}</a>
              <a href="{legal_cookies}">{c["footer_cookies"]}</a>
            </div>
            <button type="button" class="back-top">{c["back_top"]}</button>
          </div>
        </div>
      </div>
    </footer>
    <div id="cookie-banner" class="cookie-banner" role="region" aria-label="{c["cookie_label"]}" hidden>
      <div class="container cookie-banner__inner">
        <p class="cookie-banner__text">{c["cookie_text"]} <a href="{legal_cookies}">{c["cookie_link"]}</a>.</p>
        <div class="cookie-banner__actions">
          <a class="cookie-banner__link" href="{legal_cookies}">{c["cookie_link"]}</a>
          <button type="button" class="btn btn--primary cookie-banner__accept">{c["cookie_accept"]}</button>
        </div>
      </div>
    </div>
    <script>document.getElementById("y").textContent = new Date().getFullYear();</script>
    <script src="{asset_url(ap, 'js/main.js')}" defer></script>
  </body>
</html>
"""
