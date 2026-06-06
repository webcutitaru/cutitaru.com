#!/usr/bin/env python3
"""Generate trilingual cutitaru.com static pages (RO / EN / RU)."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://cutitaru.com"

LANGS = {
    "ro": {
        "code": "ro-MD",
        "prefix": "",
        "home": "/",
        "privacy": "/politica-confidentialitate.html",
        "cookies": "/politica-cookies.html",
        "terms": "/termeni-si-conditii.html",
        "design": "/design-web-moldova.html",
        "shopify": "/magazin-online-shopify-moldova.html",
        "ads": "/reclame-google-facebook-moldova.html",
    },
    "en": {
        "code": "en",
        "prefix": "/en",
        "home": "/en/",
        "privacy": "/en/privacy-policy.html",
        "cookies": "/en/cookies-policy.html",
        "terms": "/en/terms-of-service.html",
        "design": "/en/web-design-moldova.html",
        "shopify": "/en/shopify-store-moldova.html",
        "ads": "/en/google-facebook-ads-moldova.html",
    },
    "ru": {
        "code": "ru-MD",
        "prefix": "/ru",
        "home": "/ru/",
        "privacy": "/ru/politika-konfidencialnosti.html",
        "cookies": "/ru/politika-cookies.html",
        "terms": "/ru/usloviya-ispolzovaniya.html",
        "design": "/ru/veb-dizayn-moldova.html",
        "shopify": "/ru/internet-magazin-shopify-moldova.html",
        "ads": "/ru/reklama-google-facebook-moldova.html",
    },
}

SAME_AS = [
    "https://www.instagram.com/cut1taru/",
    "https://www.facebook.com/cutitaru.adrian",
    "https://www.linkedin.com/in/cutitaru-adrian/",
]


def asset_prefix(lang: str) -> str:
    return "../" if lang in ("en", "ru") else ""


LEGAL_FILES = {
    "privacy": {
        "ro": "politica-confidentialitate.html",
        "en": "privacy-policy.html",
        "ru": "politika-konfidencialnosti.html",
    },
    "cookies": {
        "ro": "politica-cookies.html",
        "en": "cookies-policy.html",
        "ru": "politika-cookies.html",
    },
    "terms": {
        "ro": "termeni-si-conditii.html",
        "en": "terms-of-service.html",
        "ru": "usloviya-ispolzovaniya.html",
    },
}


def page_rel_path(lang: str, page_key: str) -> str:
    if page_key == "home":
        return "index.html" if lang == "ro" else f"{lang}/index.html"
    if page_key in LEGAL_FILES:
        fname = LEGAL_FILES[page_key][lang]
        return fname if lang == "ro" else f"{lang}/{fname}"
    if page_key in ("design", "shopify", "ads"):
        fname = SERVICE_PAGES[page_key][lang]["file"]
        return fname if lang == "ro" else f"{lang}/{fname}"
    return page_rel_path(lang, "home")


def lang_href(from_lang: str, to_lang: str, page_key: str) -> str:
    target = page_rel_path(to_lang, page_key)
    if from_lang == "ro":
        return target
    if to_lang == from_lang:
        return target.split("/")[-1]
    return "../" + target


def portrait_url(lang: str) -> str:
    """Document-relative URL for preload/img tags."""
    name = "portrait.webp" if (ROOT / "css" / "portrait.webp").exists() else "portrait.png"
    return f"{asset_prefix(lang)}css/{name}"


def hero_image_var() -> str:
    """URL for --hero-image; resolved from css/styles.css (where var() is consumed)."""
    if (ROOT / "css" / "portrait.webp").exists():
        return "portrait.webp"
    return "portrait.png"


def portrait_abs() -> str:
    name = "portrait.webp" if (ROOT / "css" / "portrait.webp").exists() else "portrait.png"
    return SITE + f"/css/{name}"


FA_TO_ICON = {
    "fa-pen-nib": "pen-nib",
    "fa-laptop-code": "laptop-code",
    "fa-bullseye": "bullseye",
    "fa-chart-line": "chart-line",
    "fa-brands fa-shopify": "shopify",
    "fa-rectangle-ad": "rectangle-ad",
}


def service_icon_name(fa_class: str) -> str:
    return FA_TO_ICON.get(fa_class, fa_class.replace("fa-brands fa-", "").replace("fa-", ""))


def about_section_image(ap: str) -> str:
    webp = ROOT / "css" / "portrait_about_section.webp"
    alt = "Adrian Cutitaru — cutitaru"
    if webp.exists():
        return f"""            <picture>
              <source srcset="{ap}css/portrait_about_section.webp" type="image/webp" />
              <img src="{ap}css/portrait_about_section.png" alt="{alt}" width="1200" height="1600" loading="lazy" decoding="async" />
            </picture>"""
    return f"""            <img src="{ap}css/portrait_about_section.png" alt="{alt}" width="1200" height="1600" loading="lazy" decoding="async" />"""


LANG_UI = {
    "ro": {"code": "RO", "name": "Română", "region": "Moldova", "aria": "Limbi"},
    "en": {"code": "EN", "name": "English", "region": "International", "aria": "Language"},
    "ru": {"code": "RU", "name": "Русский", "region": "Молдова", "aria": "Язык"},
}


def json_ld_home(lang: str, faq: list[tuple[str, str]]) -> str:
    descs = {
        "ro": "Design web, magazine Shopify și reclame Google/Facebook pentru branduri locale și internaționale.",
        "en": "Web design, Shopify stores, and Google/Facebook ads for local and international brands.",
        "ru": "Веб-дизайн, магазины Shopify и реклама Google/Facebook для локальных и международных брендов.",
    }
    area_served = [
        {"@type": "Country", "name": "Moldova"},
        {"@type": "Place", "name": "International"},
    ]
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "name": "cutitaru",
                "url": SITE + LANGS[lang]["home"],
                "inLanguage": LANGS[lang]["code"],
            },
            {
                "@type": "Person",
                "@id": SITE + "/#person",
                "name": "Adrian Cutitaru",
                "jobTitle": "Web Designer & Developer",
                "url": SITE + "/",
                "image": portrait_abs(),
                "sameAs": SAME_AS,
                "knowsAbout": ["Web Design", "Branding", "Shopify", "Google Ads", "Facebook Ads"],
                "areaServed": area_served,
            },
            {
                "@type": "ProfessionalService",
                "@id": SITE + "/#business",
                "name": "cutitaru",
                "description": descs[lang],
                "url": SITE + "/",
                "provider": {"@id": SITE + "/#person"},
                "areaServed": area_served,
                "serviceType": ["Web Design", "E-commerce", "Digital Advertising"],
                "availableLanguage": ["Romanian", "English", "Russian"],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a},
                    }
                    for q, a in faq
                ],
            },
        ],
    }
    return f'    <script type="application/ld+json">{json.dumps(graph, ensure_ascii=False)}</script>'


# --- Content dictionaries (abbreviated keys) ---
HOME = {
    "ro": {
        "title": "cutitaru — design web, Shopify și reclame online",
        "desc": "Design web, magazine Shopify și promovare Google/Facebook pentru branduri locale și internaționale. Site-uri rapide, clare, ușor de găsit.",
        "skip": "Sari la conținut",
        "nav": [("Despre", "#about"), ("Servicii", "#services"), ("Parteneri", "#partners"), ("Contact", "#contact")],
        "hero_eyebrow": "Cutitaru Signature",
        "hero_h1": "Hai să construim ceva care contează.",
        "hero_lead": "Design și dezvoltare web pentru branduri care vor claritate online — site-uri, magazine Shopify și promovare, oriunde ești tu.",
        "hero_cta": "Începe un proiect",
        "about_eyebrow": "Despre",
        "about_h2": "Construit cu grijă, susținut după lansare",
        "about_p1": "Combin design vizual cu dezvoltare web — structură clară, interfață ușor de folosit, cod curat. Nu o pagină frumoasă de moment: ceva care vorbește clar publicului tău și rezistă în timp.",
        "about_p2": "Lucrez remote cu clienți din Moldova, Europa și din alte piețe. Fiecare proiect începe cu ascultare; când e live, rămân disponibil pentru ajustări și ce urmează.",
        "services_eyebrow": "Servicii",
        "services_h2": "Tot ce ai nevoie ca să arăți bine și să crești online",
        "services_lead": "Te ajut pas cu pas: cum arăți, apoi site-ul, apoi cum te găsesc clienții — și setez totul ca să vezi ce funcționează.",
        "features": [
            ("Livrare clară, pas cu pas", "Etape definite, progres constant, fără surprize la final."),
            ("Aspect unitar peste tot", "Aceeași identitate pe site, social media și materiale."),
            ("Rezultate pe care le vezi", "Performanță, contacte și claritate — nu doar „pixel perfect”."),
        ],
        "campaigns_eyebrow": "Campanii",
        "campaigns_h2": "Reclame Facebook, Instagram și Google care merg cu site-ul tău",
        "campaigns_p": "Când cineva dă click pe reclamă, pagina unde ajunge trebuie să fie un pas natural — nu o surpriză. Conectez campaniile la site ca mesajul să rămână clar și să vezi ce aduce rezultate.",
        "campaigns_li": [
            ("Reclame și pagini care se potrivesc", "Același mesaj de la reclamă la site — oamenii știu că sunt locul potrivit."),
            ("Setup clar, ușor de crescut", "Campanii și audiențe organizate, fără buget irosit."),
            ("Măsurăm ce contează", "Lead-uri, vânzări sau apeluri — nu doar click-uri."),
            ("Îmbunătățiri cu sens", "Teste mici, planificate — știi ce merită păstrat."),
        ],
        "partners_eyebrow": "Încredere",
        "partners_h2": "Parteneri și colaborări",
        "partners_lead": "Branduri și studiouri cu care am lucrat — același standard de calitate și claritate.",
        "work_eyebrow": "Cum lucrez",
        "work_h2": "De la idee la site care merge",
        "work_lead": "Fiecare proiect urmează pași clari: descoperire, structură, design, implementare și lansare — cu feedback regulat la fiecare etapă.",
        "work_cards": [
            ("Descoperire și structură", "Discutăm obiectivele, publicul și conținutul. Propun sitemap și flux clar înainte de design."),
            ("Design și prototip", "Machete vizuale, tipografie și culori — revizuim împreună până e clar ce transmite site-ul."),
            ("Implementare și testare", "Cod curat, mobil, formular contact și SEO de bază. Testăm viteza și traseele importante."),
            ("Lansare și urmărire", "Publicăm, verificăm analytics și rămân disponibil pentru ajustări și campanii ulterioare."),
        ],
        "faq_eyebrow": "Întrebări",
        "faq_h2": "Întrebări frecvente",
        "faq": [
            ("Ce servicii oferă cutitaru?", "Design web, identitate vizuală, magazine Shopify, formulare și tracking pentru lead-uri, dashboard-uri simple și reclame Google/Facebook — totul legat ca să funcționeze împreună."),
            ("Lucrezi doar local sau și internațional?", "Remote, cu clienți din Moldova și din alte țări. Proces clar, comunicare în română, engleză sau rusă."),
            ("Cât costă un site web?", "Depinde de complexitate — un site de prezentare, un magazin Shopify sau campanii de ads au scope diferit. Scrie-mi câteva detalii și îți răspund cu întrebări clare și o estimare onestă."),
            ("Construiești magazine online Shopify?", "Da. Magazine ușor de navigat, checkout simplu, produse organizate — gata de vânzări local sau pe piețe externe."),
            ("Te ocupi de reclame Google și Facebook?", "Da. Setez și optimizez campanii legate de site-ul tău, cu rapoarte clare — nu doar click-uri sau like-uri."),
            ("Cât durează un proiect?", "Depinde de complexitate — scope-ul, conținutul, integrările și feedback-ul determină durata. Discutăm transparent la început, după ce înțeleg brief-ul."),
        ],
        "contact_eyebrow": "Contact",
        "contact_h2": "Hai să construim ceva durabil",
        "contact_lead": "Spune-mi câteva detalii despre proiect — răspund cu întrebări clare și o estimare onestă.",
        "form_name": "Nume",
        "form_email": "Email",
        "form_phone": "Telefon (opțional)",
        "form_city": "Oraș (opțional)",
        "form_message": "Mesaj",
        "form_send": "Trimite",
        "footer_cta_p": "Ai un brief sau doar o idee? Scrie-mi câteva rânduri.",
        "footer_cta_btn": "Contactează-mă",
        "footer_blurb": "Design și implementare web pentru branduri care vor claritate, viteză și consistență vizuală.",
        "footer_explore": "Explorează",
        "footer_services": "Design web · Magazine Shopify · Reclame online",
        "footer_rights": "Toate drepturile rezervate.",
        "footer_privacy": "Confidențialitate",
        "footer_terms": "Termeni",
        "footer_cookies": "Cookie",
        "back_top": "Sus ↑",
        "cookie_label": "Cookie-uri și analiză pe acest site",
        "cookie_text": "Folosim cookie-uri și tehnologii similare, inclusiv Microsoft Clarity, pentru a înțelege cum e folosit site-ul. Acceptarea ascunde acest banner. Vezi",
        "cookie_link": "Politica de cookie",
        "cookie_accept": "Accept",
        "toast_ok": "Mesajul a fost trimis.\nMulțumesc — revin în curând.",
        "toast_err": "Ceva n-a mers bine. Încearcă din nou sau scrie-mi direct pe email.",
        "toast_close": "Închide notificarea",
        "toast_btn": "OK",
        "val_name": "Introdu numele.",
        "val_email": "Introdu emailul.",
        "val_email_bad": "Emailul nu pare valid.",
        "val_message": "Scrie un scurt mesaj.",
        "services": [
            ("fa-pen-nib", "Logo, culori și identitate", "Aspect unitar: logo, culori, fonturi și reguli simple — pe site, social media și print.", None, "branding"),
            ("fa-laptop-code", "Site-uri și landing page-uri", "Site-uri clare și rapide, ușor de contactat. Merge bine pe telefon, apare pe Google.", "design", "design"),
            ("fa-bullseye", "Mai multe solicitări și vânzări", "Formulare, butoane clare și trasee simple — vezi de unde vin contactele.", None, "leads"),
            ("fa-chart-line", "Rapoarte și mai puțină muncă manuală", "Dashboard-uri și legături cu CRM, foi de calcul, email — mai puțin copy-paste.", None, "reports"),
            ("fa-brands fa-shopify", "Magazine online (Shopify)", "Magazine ușor de folosit: produse organizate, checkout simplu, pregătite de creștere.", "shopify", "shopify"),
            ("fa-rectangle-ad", "Reclame Facebook, Instagram și Google", "Campanii testate și ajustate după rezultate reale — nu doar like-uri.", "ads", "ads"),
        ],
        "talk": "Hai să vorbim",
        "work_cta": "Hai să vorbim",
        "carousel_prev": "Derulează serviciile la stânga",
        "carousel_next": "Derulează serviciile la dreapta",
        "carousel_region": "Oferte servicii",
        "return_to": "/",
    },
    "en": {
        "title": "cutitaru — web design, Shopify & online ads",
        "desc": "Web design, Shopify stores, and Google/Facebook promotion for local and international brands. Fast, clear sites that are easy to find.",
        "skip": "Skip to main content",
        "nav": [("About", "#about"), ("Services", "#services"), ("Partners", "#partners"), ("Contact", "#contact")],
        "hero_eyebrow": "Cutitaru Signature",
        "hero_h1": "Let's build something that matters.",
        "hero_lead": "Web design and development for brands that want clarity online — websites, Shopify stores, and promotion, wherever you are.",
        "hero_cta": "Start a project",
        "about_eyebrow": "About",
        "about_h2": "Built with care, supported after launch",
        "about_p1": "I combine visual design with web development — clear structure, easy-to-use interface, clean code. Not a one-off pretty page: something that speaks clearly to your audience and holds up over time.",
        "about_p2": "I work remotely with clients in Moldova, across Europe, and internationally. Every project starts with listening; when it's live, I stay available for tweaks and what comes next.",
        "services_eyebrow": "Services",
        "services_h2": "Everything you need to look good and grow online",
        "services_lead": "I help you step by step: how you look, then your website, then getting people to reach out — and I set things up so you can see what's working.",
        "features": [
            ("Clear delivery, step by step", "Defined milestones, steady progress, no end-of-project surprises."),
            ("Consistent look everywhere", "Same identity on your site, social media, and materials."),
            ("Results you can see", "Performance, leads, and clarity — not just \"pixel perfect.\""),
        ],
        "campaigns_eyebrow": "Campaigns",
        "campaigns_h2": "Facebook, Instagram & Google ads that work with your site",
        "campaigns_p": "When someone clicks your ad, the page they land on should feel like a natural next step — not a surprise. I connect your campaigns to your website so the message stays clear and you can see what's actually bringing in results.",
        "campaigns_li": [
            ("Ads and pages that match", "Same look and message from the ad to your site, so people know they're in the right place."),
            ("Clear setup you can grow", "Organized campaigns and audiences so your budget goes where it should, without overlap or wasted spend."),
            ("Track what matters", "Set up so you see real leads, sales, or calls — not just clicks and impressions."),
            ("Improve with purpose", "Small, planned tests instead of random tweaks — so you know what's worth keeping."),
        ],
        "partners_eyebrow": "Trust",
        "partners_h2": "Partners & collaborations",
        "partners_lead": "Brands and studios I've worked with — the same bar for quality and clarity.",
        "work_eyebrow": "How I work",
        "work_h2": "From idea to a site that works",
        "work_lead": "Every project follows clear steps: discovery, structure, design, build, and launch — with regular feedback at each stage.",
        "work_cards": [
            ("Discovery & structure", "We align on goals, audience, and content. I propose a sitemap and clear user flow before design starts."),
            ("Design & prototype", "Visual layouts, typography, and color — we review together until the site’s message is clear."),
            ("Build & testing", "Clean code, mobile-first, contact form, and basic SEO. We test speed and key user paths."),
            ("Launch & follow-up", "Go live, verify analytics, and I stay available for tweaks and follow-on campaigns."),
        ],
        "faq_eyebrow": "FAQ",
        "faq_h2": "Frequently asked questions",
        "faq": [
            ("What services does cutitaru offer?", "Web design, visual identity, Shopify stores, lead forms and tracking, simple dashboards, and Google/Facebook ads — all connected to work together."),
            ("Do you work locally or internationally?", "Remotely, with clients in Moldova and other countries. Clear process, communication in Romanian, English, or Russian."),
            ("How much does a website cost?", "It depends on scope — a presentation site, Shopify store, or ad campaigns differ. Send a few details and I'll reply with clear questions and an honest estimate."),
            ("Do you build Shopify online stores?", "Yes. Easy-to-browse stores, smooth checkout, organized products — ready for local sales or international markets."),
            ("Do you manage Google and Facebook ads?", "Yes. I set up and optimize campaigns tied to your site, with clear reports — not just clicks or likes."),
            ("How long does a project take?", "It depends on complexity — scope, content, integrations, and feedback all affect the timeline. We're transparent about it upfront once I understand your brief."),
        ],
        "contact_eyebrow": "Contact",
        "contact_h2": "Let's build something that lasts",
        "contact_lead": "Share a few details about your project — I'll reply with focused questions and an honest estimate.",
        "form_name": "Name",
        "form_email": "Email",
        "form_phone": "Phone (optional)",
        "form_city": "City (optional)",
        "form_message": "Message",
        "form_send": "Send",
        "footer_cta_p": "Have a brief or just an idea? Tell me in a few lines.",
        "footer_cta_btn": "Contact me",
        "footer_blurb": "Design and web implementation for brands that want clarity, speed, and visual consistency.",
        "footer_explore": "Explore",
        "footer_services": "Web design · Shopify stores · Online ads",
        "footer_rights": "All rights reserved.",
        "footer_privacy": "Privacy",
        "footer_terms": "Terms",
        "footer_cookies": "Cookies",
        "back_top": "Back to top ↑",
        "cookie_label": "Cookies and analytics on this site",
        "cookie_text": "We use cookies and similar technologies, including Microsoft Clarity, to understand how this site is used. Accepting hides this banner. See the",
        "cookie_link": "Cookie policy",
        "cookie_accept": "Accept",
        "toast_ok": "Your message was sent.\nThank you — I'll get back to you shortly.",
        "toast_err": "Something went wrong. Please try again or email me directly.",
        "toast_close": "Close notification",
        "toast_btn": "OK",
        "val_name": "Please enter your name.",
        "val_email": "Please enter your email.",
        "val_email_bad": "That email doesn't look valid.",
        "val_message": "Please enter a short message.",
        "services": [
            ("fa-pen-nib", "Logo, colors & brand look", "A consistent look: logo direction, colors, fonts, and simple rules — on your site, social media, and print.", None, "branding"),
            ("fa-laptop-code", "Websites & landing pages", "Clear, fast websites that make it easy to get in touch. Works well on phones and Google.", "design", "design"),
            ("fa-bullseye", "Get more inquiries & sales", "Contact forms, clear buttons, and simple paths — see where leads come from.", None, "leads"),
            ("fa-chart-line", "Reports & less manual work", "Dashboards and connections to CRM, spreadsheets, email — less copy-paste.", None, "reports"),
            ("fa-brands fa-shopify", "Online stores (Shopify)", "Easy-to-use shops: organized products, smooth checkout, ready to grow.", "shopify", "shopify"),
            ("fa-rectangle-ad", "Facebook, Instagram & Google ads", "Campaigns tested and adjusted based on real results — not just likes.", "ads", "ads"),
        ],
        "talk": "Let's talk",
        "work_cta": "Let's talk",
        "carousel_prev": "Scroll services left",
        "carousel_next": "Scroll services right",
        "carousel_region": "Service offerings",
        "return_to": "/en/",
    },
    "ru": {
        "title": "cutitaru — веб-дизайн, Shopify и онлайн-реклама",
        "desc": "Веб-дизайн, Shopify и реклама Google/Facebook для локальных и международных брендов. Быстрые, понятные сайты.",
        "skip": "Перейти к содержанию",
        "nav": [("О нас", "#about"), ("Услуги", "#services"), ("Партнёры", "#partners"), ("Контакт", "#contact")],
        "hero_eyebrow": "Cutitaru Signature",
        "hero_h1": "Давайте создадим что-то важное.",
        "hero_lead": "Веб-дизайн и разработка для брендов, которым нужна ясность онлайн — сайты, Shopify и продвижение, где бы вы ни были.",
        "hero_cta": "Начать проект",
        "about_eyebrow": "О нас",
        "about_h2": "С заботой о деталях, поддержка после запуска",
        "about_p1": "Сочетаю визуальный дизайн с веб-разработкой — чёткая структура, удобный интерфейс, чистый код. Не разовая красивая страница, а то, что понятно аудитории и работает долго.",
        "about_p2": "Работаю удалённо с клиентами из Молдовы, Европы и других рынков. Каждый проект начинается с диалога; после запуска остаюсь на связи для доработок.",
        "services_eyebrow": "Услуги",
        "services_h2": "Всё, чтобы выглядеть профессионально и расти онлайн",
        "services_lead": "Помогаю шаг за шагом: как вы выглядите, затем сайт, затем как клиенты находят вас — и настраиваю всё, чтобы видеть, что работает.",
        "features": [
            ("Чёткая поэтапная работа", "Этапы, постоянный прогресс, без сюрпризов в конце."),
            ("Единый стиль везде", "Одна идентичность на сайте, в соцсетях и материалах."),
            ("Результаты, которые видны", "Скорость, заявки и ясность — не только «pixel perfect»."),
        ],
        "campaigns_eyebrow": "Реклама",
        "campaigns_h2": "Реклама Facebook, Instagram и Google, которая работает с вашим сайтом",
        "campaigns_p": "Когда человек кликает по рекламе, страница должна быть естественным шагом — не сюрпризом. Связываю кампании с сайтом, чтобы сообщение было ясным и вы видели реальные результаты.",
        "campaigns_li": [
            ("Реклама и страницы совпадают", "Одинаковый вид и сообщение от рекламы до сайта."),
            ("Понятная настройка для роста", "Организованные кампании и аудитории — без лишних трат."),
            ("Отслеживаем важное", "Заявки, продажи, звонки — не только клики."),
            ("Улучшаем осмысленно", "Небольшие запланированные тесты — знаете, что оставить."),
        ],
        "partners_eyebrow": "Доверие",
        "partners_h2": "Партнёры и сотрудничество",
        "partners_lead": "Бренды и студии, с которыми работал — тот же стандарт качества и ясности.",
        "work_eyebrow": "Как работаю",
        "work_h2": "От идеи до работающего сайта",
        "work_lead": "Каждый проект идёт по чётким этапам: исследование, структура, дизайн, разработка и запуск — с регулярной обратной связью на каждом шаге.",
        "work_cards": [
            ("Исследование и структура", "Обсуждаем цели, аудиторию и контент. Предлагаю карту сайта и понятный путь пользователя до дизайна."),
            ("Дизайн и прототип", "Макеты, типографика и цвета — согласовываем, пока сообщение сайта не станет ясным."),
            ("Разработка и тестирование", "Чистый код, мобильная версия, форма связи и базовое SEO. Проверяем скорость и ключевые сценарии."),
            ("Запуск и сопровождение", "Публикуем, настраиваем аналитику и остаюсь на связи для доработок и рекламных кампаний."),
        ],
        "faq_eyebrow": "Вопросы",
        "faq_h2": "Частые вопросы",
        "faq": [
            ("Какие услуги предлагает cutitaru?", "Веб-дизайн, визуальная идентичность, магазины Shopify, формы и отслеживание заявок, простые дашборды и реклама Google/Facebook — всё связано вместе."),
            ("Работаете только локально или и международно?", "Удалённо, с клиентами из Молдовы и других стран. Чёткий процесс, общение на румынском, английском или русском."),
            ("Сколько стоит сайт?", "Зависит от объёма — сайт-визитка, Shopify или реклама. Напишите детали — отвечу с вопросами и честной оценкой."),
            ("Делаете магазины Shopify?", "Да. Удобные магазины, простой checkout, организованные товары — для локальных продаж или зарубежных рынков."),
            ("Занимаетесь рекламой Google и Facebook?", "Да. Настраиваю и оптимизирую кампании, связанные с сайтом, с понятными отчётами."),
            ("Сколько длится проект?", "Зависит от сложности — объём, контент, интеграции и обратная связь определяют сроки. Обсудим прозрачно в начале, когда пойму ваш бриф."),
        ],
        "contact_eyebrow": "Контакт",
        "contact_h2": "Давайте построим что-то надёжное",
        "contact_lead": "Расскажите о проекте — отвечу с вопросами и честной оценкой.",
        "form_name": "Имя",
        "form_email": "Email",
        "form_phone": "Телефон (необяз.)",
        "form_city": "Город (необяз.)",
        "form_message": "Сообщение",
        "form_send": "Отправить",
        "footer_cta_p": "Есть идея или бриф? Напишите несколько строк.",
        "footer_cta_btn": "Связаться",
        "footer_blurb": "Дизайн и веб-разработка для брендов, которым нужны ясность, скорость и визуальная согласованность.",
        "footer_explore": "Разделы",
        "footer_services": "Веб-дизайн · Shopify · Онлайн-реклама",
        "footer_rights": "Все права защищены.",
        "footer_privacy": "Конфиденциальность",
        "footer_terms": "Условия",
        "footer_cookies": "Cookie",
        "back_top": "Наверх ↑",
        "cookie_label": "Cookie и аналитика на этом сайте",
        "cookie_text": "Мы используем cookie и Microsoft Clarity для понимания использования сайта. Принятие скрывает баннер. См.",
        "cookie_link": "Политику cookie",
        "cookie_accept": "Принять",
        "toast_ok": "Сообщение отправлено.\nСпасибо — скоро отвечу.",
        "toast_err": "Что-то пошло не так. Попробуйте снова или напишите на email.",
        "toast_close": "Закрыть",
        "toast_btn": "OK",
        "val_name": "Введите имя.",
        "val_email": "Введите email.",
        "val_email_bad": "Email выглядит неверно.",
        "val_message": "Напишите короткое сообщение.",
        "services": [
            ("fa-pen-nib", "Логотип, цвета и стиль", "Единый образ: логотип, цвета, шрифты и простые правила — на сайте и в соцсетях.", None, "branding"),
            ("fa-laptop-code", "Сайты и landing page", "Понятные быстрые сайты, удобно связаться. Хорошо на телефоне и в Google.", "design", "design"),
            ("fa-bullseye", "Больше заявок и продаж", "Формы, кнопки и простые пути — видно, откуда заявки.", None, "leads"),
            ("fa-chart-line", "Отчёты и меньше ручной работы", "Дашборды и связи с CRM, таблицами, email.", None, "reports"),
            ("fa-brands fa-shopify", "Интернет-магазины (Shopify)", "Удобные магазины: товары, checkout, готовы к росту.", "shopify", "shopify"),
            ("fa-rectangle-ad", "Реклама Facebook, Instagram, Google", "Кампании по реальным результатам — не только лайки.", "ads", "ads"),
        ],
        "talk": "Обсудим",
        "work_cta": "Обсудим",
        "carousel_prev": "Прокрутить услуги влево",
        "carousel_next": "Прокрутить услуги вправо",
        "carousel_region": "Услуги",
        "return_to": "/ru/",
    },
}

SERVICE_LINKS = {
    "ro": {"design": "design-web-moldova.html", "shopify": "magazin-online-shopify-moldova.html", "ads": "reclame-google-facebook-moldova.html"},
    "en": {"design": "web-design-moldova.html", "shopify": "shopify-store-moldova.html", "ads": "google-facebook-ads-moldova.html"},
    "ru": {"design": "veb-dizayn-moldova.html", "shopify": "internet-magazin-shopify-moldova.html", "ads": "reklama-google-facebook-moldova.html"},
}


def service_href(lang: str, key: str | None, ap: str) -> str:
    if not key:
        return "#contact"
    fname = SERVICE_LINKS[lang][key]
    if lang == "ro":
        return fname
    return fname


PARTNERS_ROW1 = [
    {"name": "LikeHome", "url": "https://www.likehome.md", "file": "likehome-logo.png", "w": 260, "h": 118, "img_class": "partners-marquee__logo--rounded"},
    {"name": "Aquamarine", "url": "https://aquamarine.md", "file": "aquamarine-logo.webp", "w": 243, "h": 40},
    {"name": "Instant Convert Pro", "url": "https://convert.cutitaru.com/", "file": "instant convert pro logo.png", "w": 200, "h": 64},
    {"name": "Perfect Media Pro", "url": "https://www.perfectmedia.pro/", "file": "perfect media pro logo.webp", "w": 200, "h": 64},
    {"name": "OLY Studio", "url": "https://www.oly-studio.com/", "file": "oly studio logo.webp", "w": 200, "h": 64},
]

PARTNERS_ROW2 = [
    {"name": "English Please", "url": "https://www.englishplease.net/", "file": "english please logo.webp", "w": 240, "h": 80},
    {"name": "Select Transfer", "url": "https://selecttransferncc.com/", "file": "select transfer logo.webp", "w": 220, "h": 72},
    {"name": "Crigo Group", "url": "https://crigogroup.com/", "file": "crigo group logo.webp", "w": 200, "h": 64},
    {"name": "Lyfeni", "url": "https://lyfeni.com/", "file": "lyfeni london logo.webp", "w": 200, "h": 64},
    {"name": "Sew the Trend", "url": "https://www.sewthetrend.com/", "file": "logo sew the trend.avif", "w": 200, "h": 64},
    {"name": "Prime Rent", "url": None, "file": "prime rent logo.webp", "w": 200, "h": 64},
]


def _partner_logo_item(ap: str, partner: dict, *, duplicate: bool = False) -> str:
    src = f"{ap}assets/partners/{quote(partner['file'])}"
    img_class = partner.get("img_class", "")
    class_attr = f' class="{img_class}"' if img_class else ""
    img = (
        f'<img src="{src}" alt="{partner["name"]}" width="{partner["w"]}" height="{partner["h"]}" '
        f'loading="lazy" decoding="async"{class_attr} />'
    )
    hidden = ' aria-hidden="true"' if duplicate else ""
    if partner.get("url"):
        inner = (
            f'<a href="{partner["url"]}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="{partner["name"]}" tabindex="{"-1" if duplicate else "0"}">{img}</a>'
        )
    else:
        inner = f'<span class="partners-marquee__mark">{img}</span>'
    return f'                <div class="partners-marquee__item"{hidden}>{inner}</div>'


def _partner_marquee_row(ap: str, row_num: int, partners: list[dict]) -> str:
    items = "\n".join(_partner_logo_item(ap, p) for p in partners)
    dup_items = "\n".join(_partner_logo_item(ap, p, duplicate=True) for p in partners)
    return f"""            <div class="partners-marquee__row partners-marquee__row--{row_num}">
              <div class="partners-marquee__viewport">
                <div class="partners-marquee__track">
{items}
{dup_items}
                </div>
              </div>
            </div>"""


def partners_block(ap: str) -> str:
    row1 = _partner_marquee_row(ap, 1, PARTNERS_ROW1)
    row2 = _partner_marquee_row(ap, 2, PARTNERS_ROW2)
    return f"""          <div class="partners-marquee" aria-label="Partner logos">
{row1}
{row2}
          </div>"""


def build_home(lang: str, ext) -> str:
    c = HOME[lang]
    ap = asset_prefix(lang)
    path = LANGS[lang]["home"]
    cfg = LANGS[lang]

    nav = "\n".join(
        f'              <li><a href="{href}">{label}</a></li>' for label, href in c["nav"]
    )

    service_cards = []
    for fa_class, title, body, link_key, _ in c["services"]:
        icon_name = service_icon_name(fa_class)
        if link_key:
            title_html = f'<h3><a class="service-card__title-link" href="{service_href(lang, link_key, ap)}">{title}</a></h3>'
        else:
            title_html = f"<h3>{title}</h3>"
        service_cards.append(f"""            <article class="service-card">
              <div class="service-card__icon" aria-hidden="true">{ext.icon(icon_name)}</div>
              {title_html}
              <p>{body}</p>
              <a class="service-card__link" href="#contact">{c["talk"]}</a>
            </article>""")
    services_html = "\n".join(service_cards)

    features = []
    for strong, span in c["features"]:
        features.append(f"""            <div class="feature-mini" role="listitem">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" /></svg>
              <div><strong>{strong}</strong><span>{span}</span></div>
            </div>""")
    features_html = "\n".join(features)

    campaigns_li = "\n".join(
        f"            <li><strong>{s}</strong> — {d}</li>" for s, d in c["campaigns_li"]
    )

    work_cards = "\n".join(
        f"""            <article class="portfolio-card">
              <h3>{t}</h3><p>{b}</p><a href="#contact">{c["work_cta"]}</a>
            </article>"""
        for t, b in c["work_cards"]
    )

    faq_items = []
    for i, (q, a) in enumerate(c["faq"]):
        faq_items.append(f"""            <details class="faq-item">
              <summary>{q}</summary>
              <p>{a}</p>
            </details>""")
    faq_html = "\n".join(faq_items)

    footer_nav = "\n".join(
        f'                <li><a href="{href}">{label}</a></li>' for label, href in c["nav"] if href != "#home"
    )

    sl = SERVICE_LINKS[lang]
    if lang == "ro":
        svc_footer = f'<p class="footer-services"><a href="{sl["design"]}">{c["footer_services"].split(" · ")[0]}</a> · <a href="{sl["shopify"]}">{c["footer_services"].split(" · ")[1]}</a> · <a href="{sl["ads"]}">{c["footer_services"].split(" · ")[2]}</a></p>'
    else:
        svc_footer = f'<p class="footer-services"><a href="{sl["design"]}">{c["footer_services"].split(" · ")[0]}</a> · <a href="{sl["shopify"]}">{c["footer_services"].split(" · ")[1]}</a> · <a href="{sl["ads"]}">{c["footer_services"].split(" · ")[2]}</a></p>'

    contact_action = f"{ap}contact.php" if ap else "contact.php"
    csrf_action = f"{ap}contact_token.php" if ap else "contact_token.php"
    about_img = about_section_image(ap)

    return f"""{ext.head_common(lang, c["title"], c["desc"], path, "home", preload_portrait=True)}
{json_ld_home(lang, c["faq"])}
  </head>
  <body
    data-lang="{lang}"
    data-val-name="{c["val_name"]}"
    data-val-email="{c["val_email"]}"
    data-val-email-bad="{c["val_email_bad"]}"
    data-val-message="{c["val_message"]}"
  >
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
          <a class="nav-brand" href="#home">
            <img class="nav-brand__img" src="{ap}cutitaru-logo.png" alt="cutitaru" width="160" height="48" decoding="async" />
          </a>
          {ext.lang_switcher_html(lang, "home")}
        </div>
        <svg class="scroll-progress-ring" aria-hidden="true" focusable="false">
          <path id="scroll-progress-path" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" pathLength="100" d="" />
        </svg>
      </div>
    </header>
    <main id="main">
      <section id="home" class="hero" aria-labelledby="hero-eyebrow hero-title">
        <div class="hero__bg" style="--hero-image: url('{hero_image_var()}')" aria-hidden="true"></div>
        <div class="hero__inner container">
          <p id="hero-eyebrow" class="hero__eyebrow">{c["hero_eyebrow"]}</p>
          <h1 id="hero-title" class="hero__title">{c["hero_h1"]}</h1>
          <p class="hero__lead">{c["hero_lead"]}</p>
          <a class="btn btn--hero" href="#contact">{c["hero_cta"]}</a>
        </div>
      </section>
      <section id="about" class="section section--white" aria-labelledby="about-title">
        <div class="container about-grid">
          <div class="about__media">
{about_img}
          </div>
          <div class="about__body">
            <p class="section__eyebrow">{c["about_eyebrow"]}</p>
            <h2 class="section__title" id="about-title">{c["about_h2"]}</h2>
            <hr class="title-rule" />
            <p>{c["about_p1"]}</p>
            <p>{c["about_p2"]}</p>
          </div>
        </div>
      </section>
      <section id="services" class="section section--muted" aria-labelledby="services-title">
        <div class="container">
          <div class="services-head">
            <p class="section__eyebrow">{c["services_eyebrow"]}</p>
            <h2 class="section__title" id="services-title">{c["services_h2"]}</h2>
            <hr class="title-rule title-rule--center" />
            <p class="section__lead">{c["services_lead"]}</p>
          </div>
          <div class="services-carousel" data-services-carousel>
            <button type="button" class="services-carousel__btn services-carousel__btn--prev" data-services-scroll="prev" aria-controls="services-scroll-viewport" aria-label="{c["carousel_prev"]}">{ext.icon("chevron-left")}</button>
            <div class="services-carousel__viewport" id="services-scroll-viewport" tabindex="0" role="region" aria-label="{c["carousel_region"]}">
              <div class="services-grid">
{services_html}
              </div>
            </div>
            <button type="button" class="services-carousel__btn services-carousel__btn--next" data-services-scroll="next" aria-controls="services-scroll-viewport" aria-label="{c["carousel_next"]}">{ext.icon("chevron-right")}</button>
          </div>
          <div class="features-bar" role="list">
{features_html}
          </div>
        </div>
      </section>
      <section class="statement" aria-labelledby="statement-title">
        <div class="container statement-grid">
          <div>
            <p class="section__eyebrow statement__eyebrow">{c["campaigns_eyebrow"]}</p>
            <h2 id="statement-title">{c["campaigns_h2"]}</h2>
            <p>{c["campaigns_p"]}</p>
          </div>
          <ul class="statement-list">
{campaigns_li}
          </ul>
        </div>
      </section>
      <section id="partners" class="section section--white partners" aria-labelledby="partners-title">
        <div class="container partners-static">
          <p class="section__eyebrow">{c["partners_eyebrow"]}</p>
          <h2 class="section__title" id="partners-title">{c["partners_h2"]}</h2>
          <hr class="title-rule title-rule--center" />
          <p class="section__lead">{c["partners_lead"]}</p>
{partners_block(ap)}
        </div>
      </section>
      <section id="work" class="section section--muted" aria-labelledby="work-title">
        <div class="container">
          <p class="section__eyebrow">{c["work_eyebrow"]}</p>
          <h2 class="section__title" id="work-title">{c["work_h2"]}</h2>
          <hr class="title-rule title-rule--center" />
          <p class="section__lead">{c["work_lead"]}</p>
          <div class="portfolio-grid">
{work_cards}
          </div>
        </div>
      </section>
      <section id="faq" class="section section--white faq-section" aria-labelledby="faq-title">
        <div class="container container--narrow">
          <p class="section__eyebrow">{c["faq_eyebrow"]}</p>
          <h2 class="section__title" id="faq-title">{c["faq_h2"]}</h2>
          <hr class="title-rule title-rule--center" />
          <div class="faq-list">
{faq_html}
          </div>
        </div>
      </section>
      <section id="contact" class="section section--white contact-wrap" aria-labelledby="contact-title">
        <div class="container">
          <p class="section__eyebrow">{c["contact_eyebrow"]}</p>
          <h2 class="section__title" id="contact-title">{c["contact_h2"]}</h2>
          <hr class="title-rule title-rule--center" />
          <p class="section__lead">{c["contact_lead"]}</p>
          <form class="contact-form" data-contact-form action="{contact_action}" method="post" novalidate data-csrf-url="{csrf_action}">
            <input type="hidden" name="return_to" value="{c["return_to"]}" />
            <input type="hidden" name="csrf_ts" id="csrf_ts" value="" />
            <input type="hidden" name="csrf_token" id="csrf_token" value="" />
            <input class="hp-field" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" />
            <div class="form-row"><label for="name">{c["form_name"]}</label><input id="name" name="name" type="text" autocomplete="name" required aria-describedby="err-name" /><p class="form-error" id="err-name" data-err-for="name" role="alert"></p></div>
            <div class="form-row"><label for="email">{c["form_email"]}</label><input id="email" name="email" type="email" autocomplete="email" required aria-describedby="err-email" /><p class="form-error" id="err-email" data-err-for="email" role="alert"></p></div>
            <div class="form-row"><label for="phone">{c["form_phone"]}</label><input id="phone" name="phone" type="tel" autocomplete="tel" aria-describedby="err-phone" /><p class="form-error" id="err-phone" data-err-for="phone" role="alert"></p></div>
            <div class="form-row"><label for="city">{c["form_city"]}</label><input id="city" name="city" type="text" autocomplete="address-level2" aria-describedby="err-city" /><p class="form-error" id="err-city" data-err-for="city" role="alert"></p></div>
            <div class="form-row"><label for="message">{c["form_message"]}</label><textarea id="message" name="message" required aria-describedby="err-message"></textarea><p class="form-error" id="err-message" data-err-for="message" role="alert"></p></div>
            <div class="form-actions"><button class="btn btn--primary" type="submit">{c["form_send"]}</button></div>
          </form>
        </div>
      </section>
    </main>
    <footer class="site-footer" role="contentinfo">
      <div class="footer-cta"><div class="container"><p>{c["footer_cta_p"]}</p><a class="btn btn--primary" href="#contact">{c["footer_cta_btn"]}</a></div></div>
      <div class="footer-main">
        <div class="container">
          <div class="footer-grid">
            <div>
              <a class="footer-brand" href="#home"><img class="footer-brand__img" src="{ap}cutitaru-logo.png" alt="cutitaru" width="160" height="48" decoding="async" /></a>
              <p style="margin:0;max-width:16rem">{c["footer_blurb"]}</p>
              {svc_footer}
            </div>
            <div class="footer-col"><h4>{c["footer_explore"]}</h4><ul>{footer_nav}</ul></div>
            <div class="footer-aside">
              <div class="social" aria-label="Social">
                <a href="https://www.instagram.com/cut1taru/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">{ext.icon("instagram")}</a>
                <a href="https://www.facebook.com/cutitaru.adrian" target="_blank" rel="noopener noreferrer" aria-label="Facebook">{ext.icon("facebook")}</a>
                <a href="https://www.linkedin.com/in/cutitaru-adrian/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">{ext.icon("linkedin")}</a>
              </div>
            </div>
          </div>
          <div class="footer-bottom">
            <span>© <span id="y"></span> CUTITARU.signature. {c["footer_rights"]}</span>
            <div class="footer-legal">
              <a href="{ap}{cfg["privacy"].lstrip("/") if lang=="ro" else cfg["privacy"].split("/")[-1]}">{c["footer_privacy"]}</a>
              <a href="{ap}{cfg["terms"].lstrip("/") if lang=="ro" else cfg["terms"].split("/")[-1]}">{c["footer_terms"]}</a>
              <a href="{ap}{cfg["cookies"].lstrip("/") if lang=="ro" else cfg["cookies"].split("/")[-1]}">{c["footer_cookies"]}</a>
            </div>
            <button type="button" class="back-top">{c["back_top"]}</button>
          </div>
        </div>
      </div>
    </footer>
    <div class="contact-toast" data-contact-toast data-ok-message="{c["toast_ok"]}" data-err-message="{c["toast_err"]}" hidden aria-hidden="true">
      <button type="button" class="contact-toast__backdrop" data-contact-toast-dismiss tabindex="-1" aria-label="{c["toast_close"]}"></button>
      <div class="contact-toast__frame" role="dialog" aria-modal="true" aria-labelledby="contact-toast-title">
        <div class="contact-toast__surface">
          <p id="contact-toast-title" class="contact-toast__title"></p>
          <button type="button" class="btn btn--primary contact-toast__btn" data-contact-toast-close>{c["toast_btn"]}</button>
        </div>
      </div>
    </div>
    <div id="cookie-banner" class="cookie-banner" role="region" aria-label="{c["cookie_label"]}" hidden>
      <div class="container cookie-banner__inner">
        <p class="cookie-banner__text">{c["cookie_text"]} <a href="{ap}{'politica-cookies.html' if lang=='ro' else 'cookies-policy.html' if lang=='en' else 'politika-cookies.html'}">{c["cookie_link"]}</a>.</p>
        <div class="cookie-banner__actions">
          <a class="cookie-banner__link" href="{ap}{'politica-cookies.html' if lang=='ro' else 'cookies-policy.html' if lang=='en' else 'politika-cookies.html'}">{c["cookie_link"]}</a>
          <button type="button" class="btn btn--primary cookie-banner__accept">{c["cookie_accept"]}</button>
        </div>
      </div>
    </div>
    <script>document.getElementById("y").textContent = new Date().getFullYear();</script>
    <script src="{ap}js/main.js" defer></script>
  </body>
</html>
"""


def write_homepages(ext):
    (ROOT / "index.html").write_text(build_home("ro", ext), encoding="utf-8")
    (ROOT / "en" / "index.html").write_text(build_home("en", ext), encoding="utf-8")
    (ROOT / "ru" / "index.html").write_text(build_home("ru", ext), encoding="utf-8")
    print("Homepages written")


SERVICE_PAGES = {
    "design": {
        "ro": {
            "file": "design-web-moldova.html",
            "title": "Creare site web Moldova — design modern | cutitaru",
            "desc": "Site-uri de prezentare și landing page-uri pentru business-uri din Moldova. Mobile-first, SEO inclus, livrare clară.",
            "h1": "Creare site web în Moldova",
            "lead": "cutitaru construiește site-uri de prezentare pentru afaceri din Chișinău și Republica Moldova. Fiecare site e rapid, optimizat mobil și pregătit pentru Google.",
            "sections": [
                ("Ce include un site web cutitaru?", "Design clar, structură ușor de navigat, formulare de contact, optimizare mobil, setări SEO de bază și integrare cu analytics."),
                ("Pentru cine e potrivit?", "IMM-uri, freelanceri, startup-uri și branduri locale care vor un site profesional, ușor de înțeles și de actualizat."),
                ("Cât durează?", "Un landing page simplu: câteva săptămâni. Un site complet cu mai multe pagini: de obicei 4–8 săptămâni, în funcție de conținut."),
                ("Cum decurge procesul?", "Începem cu un call scurt și un brief. Propun structura paginilor, apoi design, implementare, testare și lansare — cu revizuiri la fiecare etapă."),
                ("Pot actualiza conținutul singur?", "Da, pentru texte și imagini simple. Pentru schimbări majore de structură sau design, rămân disponibil."),
                ("Site-ul va apărea pe Google?", "Fiecare site include SEO de bază: titluri, meta-descrieri, structură clară și viteză bună — fundament pentru indexare."),
            ],
            "cta": "Solicită o ofertă",
            "home": "Acasă",
        },
        "en": {
            "file": "web-design-moldova.html",
            "title": "Web design Moldova — modern sites | cutitaru",
            "desc": "Presentation websites and landing pages for businesses in Moldova. Mobile-first, SEO included, clear delivery.",
            "h1": "Web design in Moldova",
            "lead": "cutitaru builds presentation websites for businesses in Chișinău and Moldova. Every site is fast, mobile-optimized, and ready for Google.",
            "sections": [
                ("What's included?", "Clear design, easy navigation, contact forms, mobile optimization, basic SEO setup, and analytics integration."),
                ("Who is it for?", "SMBs, freelancers, startups, and local brands that want a professional, easy-to-understand site."),
                ("How long does it take?", "A simple landing page: a few weeks. A full multi-page site: usually 4–8 weeks, depending on content."),
                ("How does the process work?", "We start with a short call and brief. I propose page structure, then design, build, testing, and launch — with reviews at each stage."),
                ("Can I update content myself?", "Yes, for simple text and image changes. For major structure or design changes, I stay available."),
                ("Will the site show up on Google?", "Every site includes basic SEO: titles, meta descriptions, clear structure, and good speed — a solid foundation for indexing."),
            ],
            "cta": "Get a quote",
            "home": "Home",
        },
        "ru": {
            "file": "veb-dizayn-moldova.html",
            "title": "Создание сайта Молдова — веб-дизайн | cutitaru",
            "desc": "Сайты-визитки и landing page для бизнеса в Молдове. Mobile-first, SEO, чёткая сдача проекта.",
            "h1": "Создание сайта в Молдове",
            "lead": "cutitaru создаёт сайты для бизнеса в Кишинёве и Молдове. Быстрые, адаптированные под мобильные и готовые к Google.",
            "sections": [
                ("Что входит?", "Понятный дизайн, навигация, формы связи, мобильная оптимизация, базовое SEO и аналитика."),
                ("Для кого?", "Малый бизнес, фрилансеры, стартапы и локальные бренды."),
                ("Сроки?", "Простой landing — несколько недель. Полный сайт — обычно 4–8 недель."),
                ("Как проходит процесс?", "Начинаем с короткого созвона и брифа. Предлагаю структуру страниц, затем дизайн, разработку, тестирование и запуск — с согласованием на каждом этапе."),
                ("Смогу ли обновлять контент сам?", "Да, для простых текстов и изображений. При серьёзных изменениях структуры или дизайна остаюсь на связи."),
                ("Будет ли сайт в Google?", "Каждый сайт включает базовое SEO: заголовки, meta-описания, чёткая структура и хорошая скорость — основа для индексации."),
            ],
            "cta": "Запросить предложение",
            "home": "Главная",
        },
    },
    "shopify": {
        "ro": {
            "file": "magazin-online-shopify-moldova.html",
            "title": "Magazin online Shopify Moldova | cutitaru",
            "desc": "Construiesc magazine Shopify ușor de folosit — produse, checkout, plăți. Pentru vânzări online în Moldova.",
            "h1": "Magazin online Shopify în Moldova",
            "lead": "Construiesc magazine Shopify ușor de navigat și de administrat — produse organizate, checkout simplu, pregătite pentru vânzări locale sau export.",
            "sections": [
                ("Ce include?", "Structură catalog, pagini produs clare, checkout optimizat, alegere theme și apps potrivite, training de bază."),
                ("Pentru cine?", "Branduri care vând produse fizice sau digitale și vor o platformă stabilă, fără complicații tehnice."),
                ("Cât durează?", "Magazin mediu: de obicei 4–8 săptămâni, în funcție de numărul de produse și integrări."),
                ("Cum decurge procesul?", "Planificăm catalogul, designul paginilor și checkout-ul. Implementez, testez plățile și livrarea, apoi lansăm cu training scurt."),
                ("Pot vinde în străinătate?", "Da — Shopify suportă piețe multiple, valute și livrări internaționale. Setăm totul pas cu pas."),
                ("Ce se întâmplă după lansare?", "Rămân disponibil pentru ajustări, produse noi și integrări — plus recomandări pentru reclame dacă ai nevoie."),
            ],
            "cta": "Solicită o ofertă",
            "home": "Acasă",
        },
        "en": {
            "file": "shopify-store-moldova.html",
            "title": "Shopify store Moldova | cutitaru",
            "desc": "Easy-to-use Shopify stores for businesses in Moldova — products, checkout, payments.",
            "h1": "Shopify online store in Moldova",
            "lead": "I build Shopify stores that are easy to browse and manage — organized products, smooth checkout, ready for local or export sales.",
            "sections": [
                ("What's included?", "Catalog structure, clear product pages, optimized checkout, theme and app selection, basic training."),
                ("Who is it for?", "Brands selling physical or digital products who want a stable platform without technical hassle."),
                ("How long?", "A medium store: usually 4–8 weeks, depending on products and integrations."),
                ("How does the process work?", "We plan the catalog, page design, and checkout. I build, test payments and shipping, then launch with a short training session."),
                ("Can I sell internationally?", "Yes — Shopify supports multiple markets, currencies, and international shipping. We set it up step by step."),
                ("What happens after launch?", "I stay available for tweaks, new products, and integrations — plus ad recommendations if you need them."),
            ],
            "cta": "Get a quote",
            "home": "Home",
        },
        "ru": {
            "file": "internet-magazin-shopify-moldova.html",
            "title": "Интернет-магазин Shopify Молдова | cutitaru",
            "desc": "Магазины Shopify для бизнеса в Молдове — товары, checkout, оплата.",
            "h1": "Интернет-магазин Shopify в Молдове",
            "lead": "Создаю магазины Shopify для клиентов из Молдовы и международных рынков — удобные для покупателей, с организованным каталогом, простым checkout и готовностью к экспорту.",
            "sections": [
                ("Что входит?", "Структура каталога, страницы товаров, checkout, выбор темы и приложений, базовое обучение."),
                ("Для кого?", "Бренды с физическими или цифровыми товарами — локальные и международные."),
                ("Сроки?", "Средний магазин — обычно 4–8 недель."),
                ("Как проходит процесс?", "Планируем каталог, дизайн страниц и checkout. Разрабатываю, тестирую оплату и доставку, затем запуск с кратким обучением."),
                ("Можно продавать за рубеж?", "Да — Shopify поддерживает несколько рынков, валют и международную доставку. Настраиваем поэтапно."),
                ("Что после запуска?", "Остаюсь на связи для доработок, новых товаров и интеграций — и рекомендаций по рекламе при необходимости."),
            ],
            "cta": "Запросить предложение",
            "home": "Главная",
        },
    },
    "ads": {
        "ro": {
            "file": "reclame-google-facebook-moldova.html",
            "title": "Reclame Google și Facebook Moldova | cutitaru",
            "desc": "Campanii Google Ads și Meta Ads pentru afaceri din Moldova, legate de site-ul tău. Setup, testare, rapoarte clare.",
            "h1": "Reclame Google și Facebook în Moldova",
            "lead": "Setez și optimizez campanii Google Ads și Meta (Facebook, Instagram) legate de site-ul tău — ca bugetul să meargă spre lead-uri și vânzări reale.",
            "sections": [
                ("Ce include?", "Structură campanii, audiențe, creativ aliniat cu site-ul, tracking conversii, rapoarte simple."),
                ("Pentru cine?", "Afaceri din Moldova care au deja un site sau magazin și vor trafic plătit cu măsurare clară."),
                ("Cum funcționează?", "Pornim cu obiective clare, testăm, ajustăm — fără schimbări la întâmplare."),
                ("Cum decurge procesul?", "Analizăm site-ul și obiectivele, setăm tracking, lansăm campanii pilot, apoi optimizăm pe baza datelor reale."),
                ("Lucrezi doar în Moldova?", "Campaniile pot ținti Moldova sau piețe externe — audiențe, limbă și creativ aliniate cu publicul tău."),
                ("Cât costă managementul?", "Depinde de buget și platforme. Discutăm transparent înainte de start — fără contracte pe termen lung obligatorii."),
            ],
            "cta": "Solicită o ofertă",
            "home": "Acasă",
        },
        "en": {
            "file": "google-facebook-ads-moldova.html",
            "title": "Google & Facebook ads Moldova | cutitaru",
            "desc": "Google Ads and Meta campaigns for businesses in Moldova. Setup, testing, clear reports tied to your site.",
            "h1": "Google & Facebook ads in Moldova",
            "lead": "I set up and optimize Google Ads and Meta (Facebook, Instagram) campaigns tied to your website — so budget goes toward real leads and sales.",
            "sections": [
                ("What's included?", "Campaign structure, audiences, creatives aligned with your site, conversion tracking, simple reports."),
                ("Who is it for?", "Businesses in Moldova with a site or store who want paid traffic with clear measurement."),
                ("How does it work?", "Clear goals first, then test and adjust — no random changes."),
                ("How does the process work?", "We review your site and goals, set up tracking, launch pilot campaigns, then optimize based on real data."),
                ("Do you only target Moldova?", "Campaigns can target Moldova or international markets — audiences, language, and creatives matched to your audience."),
                ("What does management cost?", "Depends on budget and platforms. We discuss transparently before starting — no mandatory long-term contracts."),
            ],
            "cta": "Get a quote",
            "home": "Home",
        },
        "ru": {
            "file": "reklama-google-facebook-moldova.html",
            "title": "Реклама Google и Facebook Молдова | cutitaru",
            "desc": "Кампании Google Ads и Meta для бизнеса в Молдове, связанные с вашим сайтом.",
            "h1": "Реклама Google и Facebook в Молдове",
            "lead": "Настраиваю и оптимизирую Google Ads и Meta (Facebook, Instagram), связанные с сайтом — бюджет идёт на реальные заявки и продажи.",
            "sections": [
                ("Что входит?", "Структура кампаний, аудитории, креативы, отслеживание конверсий, отчёты."),
                ("Для кого?", "Бизнес в Молдове с сайтом или магазином, которому нужен платный трафик с измерением."),
                ("Как работает?", "Чёткие цели, тесты, корректировки — без хаотичных изменений."),
                ("Как проходит процесс?", "Анализируем сайт и цели, настраиваем tracking, запускаем пилотные кампании, затем оптимизируем по данным."),
                ("Только Молдова?", "Кампании могут таргетировать Молдову или международные рынки — аудитории, язык и креативы под вашу аудиторию."),
                ("Сколько стоит ведение?", "Зависит от бюджета и платформ. Обсуждаем прозрачно до старта — без обязательных долгосрочных контрактов."),
            ],
            "cta": "Запросить предложение",
            "home": "Главная",
        },
    },
}


def build_service_page(lang: str, key: str, ext) -> str:
    p = SERVICE_PAGES[key][lang]
    c = HOME[lang]
    ap = asset_prefix(lang)
    cfg = LANGS[lang]
    home = ext.home_doc_href(lang)
    contact = f"{home}#contact"

    path = "/" + p["file"] if lang == "ro" else f"/{lang}/" + p["file"]
    sections_html = "\n".join(
        f'          <h2>{h}</h2>\n          <p>{b}</p>' for h, b in p["sections"]
    )

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
    legal_priv = ext.legal_doc_href(lang, "privacy")
    legal_terms = ext.legal_doc_href(lang, "terms")
    legal_cookies = ext.legal_doc_href(lang, "cookies")

    return f"""{ext.head_common(lang, p["title"], p["desc"], path, key, preload_portrait=False)}
{ext.json_ld_service(lang, key)}
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
          {ext.lang_switcher_html(lang, key)}
        </div>
        <svg class="scroll-progress-ring" aria-hidden="true" focusable="false">
          <path id="scroll-progress-path" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" pathLength="100" d="" />
        </svg>
      </div>
    </header>
    <main id="main" class="section section--white legal-page">
      <div class="container container--narrow">
        <p class="section__eyebrow"><a href="{home}">{p["home"]}</a></p>
        <h1 class="section__title">{p["h1"]}</h1>
        <hr class="title-rule" />
        <p class="section__lead">{p["lead"]}</p>
{sections_html}
        <p style="margin-top:2rem"><a class="btn btn--primary" href="{contact}">{p["cta"]}</a></p>
      </div>
    </main>
    <footer class="site-footer" role="contentinfo">
      <div class="footer-cta"><div class="container"><p>{c["footer_cta_p"]}</p><a class="btn btn--primary" href="{contact}">{c["footer_cta_btn"]}</a></div></div>
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
                <a href="https://www.instagram.com/cut1taru/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">{ext.icon("instagram")}</a>
                <a href="https://www.facebook.com/cutitaru.adrian" target="_blank" rel="noopener noreferrer" aria-label="Facebook">{ext.icon("facebook")}</a>
                <a href="https://www.linkedin.com/in/cutitaru-adrian/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">{ext.icon("linkedin")}</a>
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
    <script src="{ap}js/main.js" defer></script>
  </body>
</html>
"""


def write_service_pages(ext):
    for key in SERVICE_PAGES:
        for lang in ("ro", "en", "ru"):
            p = SERVICE_PAGES[key][lang]
            dest = ROOT / p["file"] if lang == "ro" else ROOT / lang / p["file"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(build_service_page(lang, key, ext), encoding="utf-8")
    print("Service pages written")


def write_legal_pages(ext):
    for page_key in LEGAL_FILES:
        for lang in ("ro", "en", "ru"):
            fname = LEGAL_FILES[page_key][lang]
            dest = ROOT / fname if lang == "ro" else ROOT / lang / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(ext.build_legal_page(lang, page_key), encoding="utf-8")
    print("Legal pages written")


def write_seo_files():
    from datetime import date

    lastmod = date.today().isoformat()
    urls = ["/", "/en/", "/ru/"]
    for key in SERVICE_PAGES:
        for lang in ("ro", "en", "ru"):
            f = SERVICE_PAGES[key][lang]["file"]
            urls.append(f"/{f}" if lang == "ro" else f"/{lang}/{f}")
    for lang in LANGS:
        for page in ("privacy", "cookies", "terms"):
            urls.append(LANGS[lang][page])

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for u in urls:
        sitemap.append(
            f"  <url><loc>{SITE}{u}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq></url>"
        )
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")

    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n\nSitemap: https://cutitaru.com/sitemap.xml\n",
        encoding="utf-8",
    )

    (ROOT / "llms.txt").write_text(
        f"""# cutitaru

> Web design, Shopify stores, and Google/Facebook ads for businesses in Moldova and internationally. Remote — Chișinău and worldwide. Languages: Romanian, English, Russian.

## Services (RO)
- [Design web Moldova]({SITE}/design-web-moldova.html): Site-uri de prezentare, landing pages, SEO inclus.
- [Shopify Moldova]({SITE}/magazin-online-shopify-moldova.html): Magazine online complete.
- [Reclame Google/Facebook]({SITE}/reclame-google-facebook-moldova.html): Campanii plătite cu tracking.

## Services (EN)
- [Web design Moldova]({SITE}/en/web-design-moldova.html): Presentation websites, landing pages, SEO included.
- [Shopify store Moldova]({SITE}/en/shopify-store-moldova.html): Full online stores.
- [Google & Facebook ads]({SITE}/en/google-facebook-ads-moldova.html): Paid campaigns with tracking.

## Services (RU)
- [Веб-дизайн Молдова]({SITE}/ru/veb-dizayn-moldova.html): Сайты-визитки, landing page, SEO.
- [Shopify Молдова]({SITE}/ru/internet-magazin-shopify-moldova.html): Интернет-магазины.
- [Реклама Google/Facebook]({SITE}/ru/reklama-google-facebook-moldova.html): Платные кампании с отслеживанием.

## Pages
- [Acasă RO]({SITE}/): Servicii, FAQ, contact.
- [Home EN]({SITE}/en/): English version.
- [Главная RU]({SITE}/ru/): Русская версия.

## Contact
- Form: {SITE}/#contact
- Instagram: @cut1taru | LinkedIn: Cutitaru Adrian
""",
        encoding="utf-8",
    )
    print("SEO files written")


import site_extensions as ext
import sys


def main():
    ext.bind(sys.modules[__name__])
    write_homepages(ext)
    write_service_pages(ext)
    write_legal_pages(ext)
    write_seo_files()


if __name__ == "__main__":
    main()
