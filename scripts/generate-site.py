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
        "ro": "Design, site-uri (Shopify, Tilda sau cod custom) și reclame Google & Meta pentru afaceri din Moldova și din afară.",
        "en": "Design, websites (Shopify, Tilda, or custom code), and Google & Meta ads for businesses in Moldova and abroad.",
        "ru": "Дизайн, сайты (Shopify, Tilda или custom-код) и реклама Google & Meta для бизнеса в Молдове и за рубежом.",
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
        "title": "cutitaru — design, site-uri și reclame online",
        "desc": "Design, site-uri (Shopify, Tilda sau cod custom) și reclame Google & Meta pentru afaceri din Moldova și din afară.",
        "skip": "Sari la conținut",
        "nav": [("Despre", "#about"), ("Servicii", "#services"), ("Parteneri", "#partners"), ("Contact", "#contact")],
        "hero_eyebrow": "cutitaru",
        "hero_h1": "Design, site-uri și promovare — clare de la început.",
        "hero_lead": "Identitate vizuală, site-uri (Shopify, Tilda sau custom) și reclame Google & Meta — pentru afaceri din Moldova și din afară.",
        "hero_cta": "Solicită o estimare",
        "about_eyebrow": "Despre",
        "about_h2": "Un partener pe care îl poți urmări pe tot parcursul",
        "about_p1": "Fac design și site-uri care se înțeleg ușor — pe telefon și pe desktop. Scopul nu e o pagină „frumoasă o dată”, ci o prezență online pe care o poți folosi și actualiza.",
        "about_p2": "Lucrez remote, cu comunicare clară în română, engleză sau rusă. După lansare rămân disponibil pentru ajustări și pașii următori.",
        "services_eyebrow": "Servicii",
        "services_h2": "Trei direcții. Un singur standard.",
        "services_lead": "Alegem împreună ce ai nevoie acum — design, site sau promovare — fără liste lungi de „extra”.",
        "features": [],
        "campaigns_eyebrow": "Încredere",
        "campaigns_h2": "Cum rămâne proiectul sub control",
        "campaigns_p": "Lucrez transparent: știi ce urmează, ce primești și ce se măsoară.",
        "campaigns_li": [
            ("Brief clar, înainte de design", "Stabilim obiectivul, paginile și conținutul înainte să desenăm."),
            ("Livrare pe etape", "Vezi progresul, dai feedback, fără surprize la final."),
            ("După lansare, tot aici", "Ajustări, măsurare, următorul pas — fără să cauți pe altcineva."),
        ],
        "partners_eyebrow": "Colaborări",
        "partners_h2": "Parteneri și colaborări",
        "partners_lead": "Branduri și studiouri cu care am colaborat — același nivel de atenție la detalii.",
        "work_eyebrow": "Cum lucrez",
        "work_h2": "De la idee la rezultat, pe etape",
        "work_lead": "Lucrăm pe etape: vorbim, desenăm, construim, lansăm — și îmi spui părerea pe parcurs.",
        "work_cards": [
            ("Discuție & plan", "Obiective, public, tip de site sau campanie."),
            ("Design", "Aspect și structură — le revizuim împreună."),
            ("Implementare", "Construiesc, testez pe mobil, pregătesc lansarea."),
            ("Lansare & urmărire", "Publicăm, verificăm și rămân disponibil."),
        ],
        "faq_eyebrow": "Întrebări",
        "faq_h2": "Întrebări frecvente",
        "faq": [
            ("Ce servicii oferi?", "Design și identitate vizuală, creare site (Shopify, Tilda sau cod custom) și reclame Google & Meta."),
            ("Ce tipuri de site faci?", "Site de prezentare, landing page sau magazin online. Platforma o alegem după nevoie — nu după modă."),
            ("Lucrezi doar în Moldova?", "Lucrez remote, cu clienți din Moldova și din alte țări. Comunic în română, engleză sau rusă."),
            ("Cât costă un proiect?", "Depinde de ce ai nevoie. După câteva detalii, îți dau o estimare onestă."),
            ("Te ocupi și de reclame?", "Da. Setez și optimizez campanii Google & Meta legate de site-ul tău, cu rezultate pe care le poți urmări."),
            ("Cât durează?", "Un landing: de obicei 5–7 zile. Proiectele mai complexe le discutăm individual, în funcție de ce ai nevoie."),
        ],
        "contact_eyebrow": "Contact",
        "contact_h2": "Spune-mi pe scurt ce ai nevoie",
        "contact_lead": "Câteva rânduri despre proiect sunt suficiente. Răspund cu întrebări clare și o estimare.",
        "form_name": "Nume",
        "form_email": "Email",
        "form_phone": "Telefon (opțional)",
        "form_city": "Oraș (opțional)",
        "form_message": "Mesaj",
        "form_send": "Trimite",
        "footer_cta_p": "Ai un brief sau doar o idee? Scrie-mi.",
        "footer_cta_btn": "Contactează-mă",
        "footer_blurb": "Design, site-uri și promovare online pentru afaceri care vor o prezență clară și de încredere.",
        "footer_explore": "Explorează",
        "footer_services": "Design · Creare site · Reclame Google & Meta",
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
            ("fa-pen-nib", "Design & identitate", "Logo, culori, fonturi și un aspect unitar pe site, social și materiale.", None, "branding"),
            ("fa-laptop-code", "Creare site", "Site de prezentare, landing sau magazin — pe Shopify, Tilda sau cod custom, după ce ți se potrivește.", "design", "design"),
            ("fa-rectangle-ad", "Reclame Google & Meta", "Campanii pe Google, Facebook și Instagram, legate de site, cu rezultate pe care le poți urmări.", "ads", "ads"),
        ],
        "talk": "Scrie-mi",
        "work_cta": "Scrie-mi",
        "carousel_prev": "Derulează serviciile la stânga",
        "carousel_next": "Derulează serviciile la dreapta",
        "carousel_region": "Oferte servicii",
        "return_to": "/",
    },
    "en": {
        "title": "cutitaru — design, websites & online ads",
        "desc": "Design, websites (Shopify, Tilda, or custom code), and Google & Meta ads for businesses in Moldova and abroad.",
        "skip": "Skip to main content",
        "nav": [("About", "#about"), ("Services", "#services"), ("Partners", "#partners"), ("Contact", "#contact")],
        "hero_eyebrow": "cutitaru",
        "hero_h1": "Design, websites & promotion — clear from the start.",
        "hero_lead": "Visual identity, websites (Shopify, Tilda, or custom), and Google & Meta ads — for businesses in Moldova and abroad.",
        "hero_cta": "Request an estimate",
        "about_eyebrow": "About",
        "about_h2": "A partner you can follow through the whole project",
        "about_p1": "I design and build websites that are easy to understand — on phone and desktop. The goal isn’t a one-off pretty page, but an online presence you can use and update.",
        "about_p2": "I work remotely, with clear communication in Romanian, English, or Russian. After launch I stay available for tweaks and next steps.",
        "services_eyebrow": "Services",
        "services_h2": "Three directions. One standard.",
        "services_lead": "You choose what you need now — design, a website, or promotion — without long lists of extras.",
        "features": [],
        "campaigns_eyebrow": "Trust",
        "campaigns_h2": "How the project stays under control",
        "campaigns_p": "I work transparently: you know what’s next, what you get, and what gets measured.",
        "campaigns_li": [
            ("Clear brief before design", "Goal, pages, and content are set before I start designing."),
            ("Delivery in stages", "You see progress, give feedback, no surprises at the end."),
            ("After launch, still here", "Tweaks, measurement, next step — without hunting for someone new."),
        ],
        "partners_eyebrow": "Collaborations",
        "partners_h2": "Partners & collaborations",
        "partners_lead": "Brands and studios I’ve worked with — the same attention to detail.",
        "work_eyebrow": "How I work",
        "work_h2": "From idea to result, step by step",
        "work_lead": "Work happens in stages: talk, design, build, launch — and you share feedback along the way.",
        "work_cards": [
            ("Talk & plan", "Goals, audience, type of site or campaign."),
            ("Design", "Look and structure — reviewed together."),
            ("Build", "I build, test on mobile, prepare for launch."),
            ("Launch & follow-up", "Go live, check things, and I stay available."),
        ],
        "faq_eyebrow": "FAQ",
        "faq_h2": "Frequently asked questions",
        "faq": [
            ("What services do you offer?", "Visual identity and design, website builds (Shopify, Tilda, or custom code), and Google & Meta ads."),
            ("What kinds of sites do you build?", "Presentation sites, landing pages, or online stores. The platform is chosen based on need — not trends."),
            ("Do you only work in Moldova?", "I work remotely with clients in Moldova and other countries. I communicate in Romanian, English, or Russian."),
            ("How much does a project cost?", "It depends on what you need. After a few details, I’ll give you an honest estimate."),
            ("Do you handle ads as well?", "Yes. I set up and optimize Google & Meta campaigns tied to your site, with results you can track."),
            ("How long does it take?", "A landing page: usually 5–7 days. More complex projects are discussed individually, based on what you need."),
        ],
        "contact_eyebrow": "Contact",
        "contact_h2": "Tell me briefly what you need",
        "contact_lead": "A few lines about the project are enough. I’ll reply with clear questions and an estimate.",
        "form_name": "Name",
        "form_email": "Email",
        "form_phone": "Phone (optional)",
        "form_city": "City (optional)",
        "form_message": "Message",
        "form_send": "Send",
        "footer_cta_p": "Have a brief or just an idea? Write me.",
        "footer_cta_btn": "Contact me",
        "footer_blurb": "Design, websites, and online promotion for businesses that want a clear, trustworthy presence.",
        "footer_explore": "Explore",
        "footer_services": "Design · Websites · Google & Meta ads",
        "footer_rights": "All rights reserved.",
        "footer_privacy": "Privacy",
        "footer_terms": "Terms",
        "footer_cookies": "Cookies",
        "back_top": "Back to top ↑",
        "cookie_label": "Cookies and analytics on this site",
        "cookie_text": "This site uses cookies and similar technologies, including Microsoft Clarity, to understand how the site is used. Accepting hides this banner. See the",
        "cookie_link": "Cookie policy",
        "cookie_accept": "Accept",
        "toast_ok": "Your message was sent.\nThank you — I’ll get back to you shortly.",
        "toast_err": "Something went wrong. Please try again or email me directly.",
        "toast_close": "Close notification",
        "toast_btn": "OK",
        "val_name": "Please enter your name.",
        "val_email": "Please enter your email.",
        "val_email_bad": "That email doesn’t look valid.",
        "val_message": "Please enter a short message.",
        "services": [
            ("fa-pen-nib", "Design & identity", "Logo, colors, fonts, and a consistent look across site, social, and materials.", None, "branding"),
            ("fa-laptop-code", "Website builds", "Presentation site, landing, or store — on Shopify, Tilda, or custom code, based on what fits you.", "design", "design"),
            ("fa-rectangle-ad", "Google & Meta ads", "Campaigns on Google, Facebook, and Instagram, tied to your site, with results you can track.", "ads", "ads"),
        ],
        "talk": "Write me",
        "work_cta": "Write me",
        "carousel_prev": "Scroll services left",
        "carousel_next": "Scroll services right",
        "carousel_region": "Service offerings",
        "return_to": "/en/",
    },
    "ru": {
        "title": "cutitaru — дизайн, сайты и онлайн-реклама",
        "desc": "Дизайн, сайты (Shopify, Tilda или custom-код) и реклама Google & Meta для бизнеса в Молдове и за рубежом.",
        "skip": "Перейти к содержанию",
        "nav": [("Обо мне", "#about"), ("Услуги", "#services"), ("Партнёры", "#partners"), ("Контакт", "#contact")],
        "hero_eyebrow": "cutitaru",
        "hero_h1": "Дизайн, сайты и продвижение — понятно с самого начала.",
        "hero_lead": "Визуальная идентичность, сайты (Shopify, Tilda или custom) и реклама Google & Meta — для бизнеса в Молдове и за рубежом.",
        "hero_cta": "Запросить оценку",
        "about_eyebrow": "Обо мне",
        "about_h2": "Партнёр, с которым можно пройти весь проект",
        "about_p1": "Делаю дизайн и сайты, которые легко понять — на телефоне и на компьютере. Цель не «красивая страница один раз», а онлайн-присутствие, которым можно пользоваться и обновлять.",
        "about_p2": "Работаю удалённо, с понятной коммуникацией на румынском, английском или русском. После запуска остаюсь на связи для правок и следующих шагов.",
        "services_eyebrow": "Услуги",
        "services_h2": "Три направления. Один стандарт.",
        "services_lead": "Вместе выбираем, что нужно сейчас — дизайн, сайт или продвижение — без длинных списков «допов».",
        "features": [],
        "campaigns_eyebrow": "Доверие",
        "campaigns_h2": "Как проект остаётся под контролем",
        "campaigns_p": "Работаю прозрачно: вы знаете, что дальше, что получите и что измеряем.",
        "campaigns_li": [
            ("Чёткий бриф до дизайна", "Фиксируем цель, страницы и контент до того, как я начну рисовать."),
            ("Сдача по этапам", "Вы видите прогресс, даёте обратную связь — без сюрпризов в конце."),
            ("После запуска — тоже здесь", "Правки, измерение, следующий шаг — без поиска нового исполнителя."),
        ],
        "partners_eyebrow": "Сотрудничество",
        "partners_h2": "Партнёры и сотрудничество",
        "partners_lead": "Бренды и студии, с которыми я работал — то же внимание к деталям.",
        "work_eyebrow": "Как я работаю",
        "work_h2": "От идеи к результату — по этапам",
        "work_lead": "Работаем по этапам: говорим, рисуем, собираем, запускаем — и вы даёте обратную связь по ходу.",
        "work_cards": [
            ("Разговор и план", "Цели, аудитория, тип сайта или кампании."),
            ("Дизайн", "Внешний вид и структура — смотрим вместе."),
            ("Реализация", "Собираю, тестирую на мобильном, готовлю запуск."),
            ("Запуск и сопровождение", "Публикуем, проверяем — и я остаюсь на связи."),
        ],
        "faq_eyebrow": "Вопросы",
        "faq_h2": "Частые вопросы",
        "faq": [
            ("Какие услуги вы предлагаете?", "Дизайн и визуальная идентичность, создание сайта (Shopify, Tilda или custom-код) и реклама Google & Meta."),
            ("Какие сайты вы делаете?", "Сайт-визитку, лендинг или интернет-магазин. Платформу выбираем по задаче — не по моде."),
            ("Работаете только в Молдове?", "Работаю удалённо с клиентами из Молдовы и других стран. Общаюсь на румынском, английском или русском."),
            ("Сколько стоит проект?", "Зависит от задачи. После нескольких деталей дам честную оценку."),
            ("Занимаетесь ли рекламой?", "Да. Настраиваю и оптимизирую кампании Google & Meta, связанные с вашим сайтом, с результатами, которые можно отслеживать."),
            ("Сколько занимает по времени?", "Лендинг: обычно 5–7 дней. Более сложные проекты обсуждаем индивидуально, исходя из задачи."),
        ],
        "contact_eyebrow": "Контакт",
        "contact_h2": "Кратко напишите, что нужно",
        "contact_lead": "Нескольких строк о проекте достаточно. Отвечу с понятными вопросами и оценкой.",
        "form_name": "Имя",
        "form_email": "Email",
        "form_phone": "Телефон (необяз.)",
        "form_city": "Город (необяз.)",
        "form_message": "Сообщение",
        "form_send": "Отправить",
        "footer_cta_p": "Есть бриф или только идея? Напишите мне.",
        "footer_cta_btn": "Связаться",
        "footer_blurb": "Дизайн, сайты и онлайн-продвижение для бизнеса, которому нужно понятное и надёжное присутствие.",
        "footer_explore": "Разделы",
        "footer_services": "Дизайн · Создание сайта · Реклама Google & Meta",
        "footer_rights": "Все права защищены.",
        "footer_privacy": "Конфиденциальность",
        "footer_terms": "Условия",
        "footer_cookies": "Cookie",
        "back_top": "Наверх ↑",
        "cookie_label": "Cookie и аналитика на этом сайте",
        "cookie_text": "На сайте используются cookie и похожие технологии, включая Microsoft Clarity, чтобы понимать, как им пользуются. Принятие скрывает баннер. См.",
        "cookie_link": "Политику cookie",
        "cookie_accept": "Принять",
        "toast_ok": "Сообщение отправлено.\nСпасибо — скоро отвечу.",
        "toast_err": "Что-то пошло не так. Попробуйте снова или напишите мне на email.",
        "toast_close": "Закрыть",
        "toast_btn": "OK",
        "val_name": "Введите имя.",
        "val_email": "Введите email.",
        "val_email_bad": "Email выглядит неверно.",
        "val_message": "Напишите короткое сообщение.",
        "services": [
            ("fa-pen-nib", "Дизайн и идентичность", "Логотип, цвета, шрифты и единый вид на сайте, в соцсетях и материалах.", None, "branding"),
            ("fa-laptop-code", "Создание сайта", "Сайт-визитка, лендинг или магазин — на Shopify, Tilda или custom-коде, как вам подходит.", "design", "design"),
            ("fa-rectangle-ad", "Реклама Google & Meta", "Кампании в Google, Facebook и Instagram, связанные с сайтом, с результатами, которые можно отслеживать.", "ads", "ads"),
        ],
        "talk": "Написать",
        "work_cta": "Написать",
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


PARTNERS = [
    {"name": "LikeHome", "url": "https://www.likehome.md", "file": "likehome-logo.png", "w": 260, "h": 118, "img_class": "partners-wall__logo--rounded"},
    {"name": "Aquamarine", "url": "https://aquamarine.md", "file": "aquamarine-logo.webp", "w": 243, "h": 40},
    {"name": "Instant Convert Pro", "url": "https://convert.cutitaru.com/", "file": "instant convert pro logo.png", "w": 200, "h": 64},
    {"name": "Perfect Media Pro", "url": "https://www.perfectmedia.pro/", "file": "perfect media pro logo.webp", "w": 200, "h": 64},
    {"name": "OLY Studio", "url": "https://www.oly-studio.com/", "file": "oly studio logo.webp", "w": 200, "h": 64},
    {"name": "English Please", "url": "https://www.englishplease.net/", "file": "english please logo.webp", "w": 240, "h": 80},
    {"name": "Select Transfer", "url": "https://selecttransferncc.com/", "file": "select transfer logo.webp", "w": 220, "h": 72},
    {"name": "Crigo Group", "url": "https://crigogroup.com/", "file": "crigo group logo.webp", "w": 200, "h": 64},
    {"name": "Lyfeni", "url": "https://lyfeni.com/", "file": "lyfeni london logo.webp", "w": 200, "h": 64},
    {"name": "Sew the Trend", "url": "https://www.sewthetrend.com/", "file": "logo sew the trend.avif", "w": 200, "h": 64},
    {"name": "Prime Rent", "url": None, "file": "prime rent logo.webp", "w": 200, "h": 64},
]

PARTNERS_ARIA = {
    "ro": "Logo-uri parteneri",
    "en": "Partner logos",
    "ru": "Логотипы партнёров",
}


def _partner_logo_item(ap: str, partner: dict) -> str:
    src = f"{ap}assets/partners/{quote(partner['file'])}"
    img_class = partner.get("img_class", "")
    class_attr = f' class="{img_class}"' if img_class else ""
    img = (
        f'<img src="{src}" alt="{partner["name"]}" width="{partner["w"]}" height="{partner["h"]}" '
        f'loading="lazy" decoding="async"{class_attr} />'
    )
    if partner.get("url"):
        inner = (
            f'<a href="{partner["url"]}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="{partner["name"]}">{img}</a>'
        )
    else:
        inner = f'<span class="partners-wall__mark">{img}</span>'
    return f"""            <li class="partners-wall__item">
              {inner}
            </li>"""


def partners_block(ap: str, lang: str = "en") -> str:
    items = "\n".join(_partner_logo_item(ap, p) for p in PARTNERS)
    aria = PARTNERS_ARIA.get(lang, PARTNERS_ARIA["en"])
    return f"""          <ul class="partners-wall" aria-label="{aria}">
{items}
          </ul>"""


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
    footer_parts = c["footer_services"].split(" · ")
    svc_footer = (
        f'<p class="footer-services">'
        f'<a href="#contact">{footer_parts[0]}</a> · '
        f'<a href="{sl["design"]}">{footer_parts[1]}</a> · '
        f'<a href="{sl["ads"]}">{footer_parts[2]}</a></p>'
    )

    features_bar = (
        f"""          <div class="features-bar" role="list">
{features_html}
          </div>
"""
        if c["features"]
        else ""
    )

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
{features_bar}        </div>
      </section>
      <section id="trust" class="statement" aria-labelledby="statement-title">
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
{partners_block(ap, lang)}
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
    <script src="{ext.asset_url(ap, 'js/main.js')}" defer></script>
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
            "title": "Creare site web Moldova — landing & site business | cutitaru",
            "desc": "Fac site-uri de prezentare, landing-uri și magazine în Moldova — pe Shopify, Tilda sau cod custom. Rapid pe mobil, SEO de bază inclus.",
            "h1": "Creare site web în Moldova",
            "lead": "Construiesc site-uri clare pentru afaceri din Chișinău și Republica Moldova: prezentare, landing sau magazin — pe Shopify, Tilda sau cod custom, după ce ți se potrivește.",
            "sections": [
                ("Ce include?", "Design clar, structură ușor de navigat, formular de contact, optimizare mobil, SEO de bază și analytics."),
                ("Pentru cine e potrivit?", "IMM-uri, freelanceri, startup-uri și branduri locale care vor un site profesional, ușor de înțeles și de actualizat."),
                ("Cât durează?", "Un landing: de obicei 5–7 zile. Proiectele mai complexe le discutăm individual, în funcție de conținut și scope."),
                ("Cum decurge procesul?", "Începem cu un call scurt și un brief. Propun structura, apoi design, implementare, testare și lansare — cu revizuiri pe parcurs."),
                ("Pot actualiza conținutul singur?", "Da, pentru texte și imagini simple. Pentru schimbări majore de structură sau design, rămân disponibil."),
                ("Site-ul va apărea pe Google?", "Include SEO de bază: titluri, meta-descrieri, structură clară și viteză bună — fundament pentru indexare."),
            ],
            "cta": "Solicită o ofertă",
            "home": "Acasă",
        },
        "en": {
            "file": "web-design-moldova.html",
            "title": "Website design Moldova — landing & business sites | cutitaru",
            "desc": "I build presentation sites, landing pages, and stores in Moldova — on Shopify, Tilda, or custom code. Mobile-ready, basic SEO included.",
            "h1": "Website design in Moldova",
            "lead": "I build clear websites for businesses in Chișinău and Moldova: presentation, landing, or store — on Shopify, Tilda, or custom code, based on what fits you.",
            "sections": [
                ("What’s included?", "Clear design, easy navigation, contact form, mobile optimization, basic SEO, and analytics."),
                ("Who is it for?", "SMBs, freelancers, startups, and local brands that want a professional site that’s easy to understand and update."),
                ("How long does it take?", "A landing page: usually 5–7 days. More complex projects are discussed individually, based on content and scope."),
                ("How does the process work?", "A short call and brief first. I propose structure, then design, build, testing, and launch — with reviews along the way."),
                ("Can I update content myself?", "Yes, for simple text and image changes. For major structure or design changes, I stay available."),
                ("Will the site show up on Google?", "Basic SEO is included: titles, meta descriptions, clear structure, and solid speed — a foundation for indexing."),
            ],
            "cta": "Get a quote",
            "home": "Home",
        },
        "ru": {
            "file": "veb-dizayn-moldova.html",
            "title": "Создание сайта Молдова — лендинг и бизнес-сайт | cutitaru",
            "desc": "Делаю сайты-визитки, лендинги и магазины в Молдове — на Shopify, Tilda или custom-коде. Удобно на мобильном, базовое SEO включено.",
            "h1": "Создание сайта в Молдове",
            "lead": "Создаю понятные сайты для бизнеса в Кишинёве и Молдове: визитка, лендинг или магазин — на Shopify, Tilda или custom-коде, как вам подходит.",
            "sections": [
                ("Что входит?", "Понятный дизайн, удобная навигация, форма связи, мобильная оптимизация, базовое SEO и аналитика."),
                ("Для кого?", "Малый бизнес, фрилансеры, стартапы и локальные бренды, которым нужен профессиональный сайт — понятный и обновляемый."),
                ("Сколько по времени?", "Лендинг: обычно 5–7 дней. Более сложные проекты обсуждаем индивидуально — по контенту и объёму."),
                ("Как проходит процесс?", "Сначала короткий созвон и бриф. Предлагаю структуру, затем дизайн, сборку, тесты и запуск — с правками по ходу."),
                ("Смогу ли обновлять контент сам?", "Да, для простых текстов и изображений. При серьёзных изменениях структуры или дизайна остаюсь на связи."),
                ("Будет ли сайт в Google?", "Входит базовое SEO: заголовки, meta-описания, чёткая структура и хорошая скорость — основа для индексации."),
            ],
            "cta": "Запросить предложение",
            "home": "Главная",
        },
    },
    "shopify": {
        "ro": {
            "file": "magazin-online-shopify-moldova.html",
            "title": "Magazin online Shopify Moldova | cutitaru",
            "desc": "Construiesc magazine Shopify ușor de folosit pentru vânzări în Moldova și export — catalog, checkout, plăți.",
            "h1": "Magazin online Shopify în Moldova",
            "lead": "Construiesc magazine Shopify ușor de navigat și de administrat — produse organizate, checkout simplu, pregătite pentru vânzări locale sau export.",
            "sections": [
                ("Ce include?", "Structură catalog, pagini produs clare, checkout optimizat, alegere theme și apps potrivite, training de bază."),
                ("Pentru cine?", "Branduri care vând produse fizice sau digitale și vor o platformă stabilă, fără complicații tehnice."),
                ("Cât durează?", "Un magazin mediu: de obicei câteva săptămâni, în funcție de produse și integrări. Scope-ul mai mare îl discutăm individual."),
                ("Cum decurge procesul?", "Planific catalogul, designul paginilor și checkout-ul. Implementez, testez plățile și livrarea, apoi lansăm cu un training scurt."),
                ("Pot vinde în străinătate?", "Da — Shopify suportă piețe multiple, valute și livrări internaționale. Setez totul pas cu pas."),
                ("Ce se întâmplă după lansare?", "Rămân disponibil pentru ajustări, produse noi și integrări — plus recomandări pentru reclame dacă ai nevoie."),
            ],
            "cta": "Solicită o ofertă",
            "home": "Acasă",
        },
        "en": {
            "file": "shopify-store-moldova.html",
            "title": "Shopify store Moldova | cutitaru",
            "desc": "I build easy-to-use Shopify stores for sales in Moldova and abroad — catalog, checkout, payments.",
            "h1": "Shopify online store in Moldova",
            "lead": "I build Shopify stores that are easy to browse and manage — organized products, smooth checkout, ready for local or export sales.",
            "sections": [
                ("What’s included?", "Catalog structure, clear product pages, optimized checkout, theme and app selection, basic training."),
                ("Who is it for?", "Brands selling physical or digital products that want a stable platform without technical hassle."),
                ("How long?", "A mid-size store: usually a few weeks, depending on products and integrations. Larger scope is discussed individually."),
                ("How does the process work?", "I plan the catalog, page design, and checkout. Then I build, test payments and shipping, and launch with a short training session."),
                ("Can I sell internationally?", "Yes — Shopify supports multiple markets, currencies, and international shipping. I set it up step by step."),
                ("What happens after launch?", "I stay available for tweaks, new products, and integrations — plus ad recommendations if you need them."),
            ],
            "cta": "Get a quote",
            "home": "Home",
        },
        "ru": {
            "file": "internet-magazin-shopify-moldova.html",
            "title": "Интернет-магазин Shopify Молдова | cutitaru",
            "desc": "Создаю удобные магазины Shopify для продаж в Молдове и на экспорт — каталог, checkout, оплата.",
            "h1": "Интернет-магазин Shopify в Молдове",
            "lead": "Создаю магазины Shopify, удобные для покупателей и для вас — организованный каталог, простой checkout, готовность к локальным продажам или экспорту.",
            "sections": [
                ("Что входит?", "Структура каталога, понятные страницы товаров, оптимизированный checkout, подбор темы и приложений, базовое обучение."),
                ("Для кого?", "Бренды с физическими или цифровыми товарами, которым нужна стабильная платформа без лишней технической сложности."),
                ("Сроки?", "Средний магазин: обычно несколько недель — зависит от товаров и интеграций. Больший объём обсуждаем индивидуально."),
                ("Как проходит процесс?", "Планирую каталог, дизайн страниц и checkout. Затем собираю, тестирую оплату и доставку, запускаю с коротким обучением."),
                ("Можно продавать за рубеж?", "Да — Shopify поддерживает несколько рынков, валют и международную доставку. Настраиваю поэтапно."),
                ("Что после запуска?", "Остаюсь на связи для правок, новых товаров и интеграций — и рекомендаций по рекламе при необходимости."),
            ],
            "cta": "Запросить предложение",
            "home": "Главная",
        },
    },
    "ads": {
        "ro": {
            "file": "reclame-google-facebook-moldova.html",
            "title": "Reclame Google & Meta Moldova | cutitaru",
            "desc": "Setez campanii Google Ads și Meta (Facebook, Instagram) pentru afaceri din Moldova, legate de site — setup, testare, rapoarte clare.",
            "h1": "Reclame Google & Meta în Moldova",
            "lead": "Setez și optimizez campanii Google Ads și Meta (Facebook, Instagram) legate de site-ul tău — ca bugetul să meargă spre lead-uri și vânzări reale.",
            "sections": [
                ("Ce include?", "Structură campanii, audiențe, creativ aliniat cu site-ul, tracking conversii, rapoarte simple."),
                ("Pentru cine?", "Afaceri din Moldova care au deja un site sau magazin și vor trafic plătit cu măsurare clară."),
                ("Cum funcționează?", "Pornim de la obiective clare, testăm, ajustăm — fără schimbări la întâmplare."),
                ("Cum decurge procesul?", "Analizez site-ul și obiectivele, setez tracking, lansez campanii pilot, apoi optimizez pe baza datelor reale."),
                ("Lucrezi doar în Moldova?", "Campaniile pot ținti Moldova sau piețe externe — audiențe, limbă și creativ aliniate cu publicul tău."),
                ("Cât costă managementul?", "Depinde de buget și platforme. Discutăm transparent înainte de start — fără contracte pe termen lung obligatorii."),
            ],
            "cta": "Solicită o ofertă",
            "home": "Acasă",
        },
        "en": {
            "file": "google-facebook-ads-moldova.html",
            "title": "Google & Meta ads Moldova | cutitaru",
            "desc": "I set up Google Ads and Meta (Facebook, Instagram) campaigns for businesses in Moldova, tied to your site — setup, testing, clear reports.",
            "h1": "Google & Meta ads in Moldova",
            "lead": "I set up and optimize Google Ads and Meta (Facebook, Instagram) campaigns tied to your website — so budget goes toward real leads and sales.",
            "sections": [
                ("What’s included?", "Campaign structure, audiences, creatives aligned with your site, conversion tracking, simple reports."),
                ("Who is it for?", "Businesses in Moldova with a site or store that want paid traffic with clear measurement."),
                ("How does it work?", "Clear goals first, then test and adjust — no random changes."),
                ("How does the process work?", "I review your site and goals, set up tracking, launch pilot campaigns, then optimize based on real data."),
                ("Do you only target Moldova?", "Campaigns can target Moldova or international markets — audiences, language, and creatives matched to your audience."),
                ("What does management cost?", "Depends on budget and platforms. Discussed transparently before starting — no mandatory long-term contracts."),
            ],
            "cta": "Get a quote",
            "home": "Home",
        },
        "ru": {
            "file": "reklama-google-facebook-moldova.html",
            "title": "Реклама Google & Meta Молдова | cutitaru",
            "desc": "Настраиваю кампании Google Ads и Meta (Facebook, Instagram) для бизнеса в Молдове, связанные с сайтом — setup, тесты, понятные отчёты.",
            "h1": "Реклама Google & Meta в Молдове",
            "lead": "Настраиваю и оптимизирую Google Ads и Meta (Facebook, Instagram), связанные с вашим сайтом — чтобы бюджет шёл на реальные заявки и продажи.",
            "sections": [
                ("Что входит?", "Структура кампаний, аудитории, креативы под сайт, отслеживание конверсий, простые отчёты."),
                ("Для кого?", "Бизнес в Молдове с сайтом или магазином, которому нужен платный трафик с понятным измерением."),
                ("Как это работает?", "Сначала чёткие цели, затем тесты и корректировки — без хаотичных изменений."),
                ("Как проходит процесс?", "Смотрю сайт и цели, настраиваю tracking, запускаю пилотные кампании, затем оптимизирую по данным."),
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
    footer_parts = c["footer_services"].split(" · ")
    svc_footer = (
        f'<p class="footer-services">'
        f'<a href="{contact}">{footer_parts[0]}</a> · '
        f'<a href="{sl["design"]}">{footer_parts[1]}</a> · '
        f'<a href="{sl["ads"]}">{footer_parts[2]}</a></p>'
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
    <script src="{ext.asset_url(ap, 'js/main.js')}" defer></script>
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

> Design, websites (Shopify, Tilda, or custom), and Google & Meta ads for businesses in Moldova and internationally. Remote — Chișinău and worldwide. Languages: Romanian, English, Russian. Solo — Adrian Cutitaru.

## Services (RO)
- [Creare site Moldova]({SITE}/design-web-moldova.html): Prezentare, landing, magazin — Shopify, Tilda sau custom. SEO de bază.
- [Shopify Moldova]({SITE}/magazin-online-shopify-moldova.html): Magazine online Shopify.
- [Reclame Google & Meta]({SITE}/reclame-google-facebook-moldova.html): Campanii plătite cu tracking.

## Services (EN)
- [Website design Moldova]({SITE}/en/web-design-moldova.html): Presentation, landing, or store — Shopify, Tilda, or custom. Basic SEO.
- [Shopify store Moldova]({SITE}/en/shopify-store-moldova.html): Full Shopify online stores.
- [Google & Meta ads]({SITE}/en/google-facebook-ads-moldova.html): Paid campaigns with tracking.

## Services (RU)
- [Создание сайта Молдова]({SITE}/ru/veb-dizayn-moldova.html): Визитка, лендинг или магазин — Shopify, Tilda или custom. Базовое SEO.
- [Shopify Молдова]({SITE}/ru/internet-magazin-shopify-moldova.html): Интернет-магазины Shopify.
- [Реклама Google & Meta]({SITE}/ru/reklama-google-facebook-moldova.html): Платные кампании с отслеживанием.

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
