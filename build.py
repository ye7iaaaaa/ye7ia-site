#!/usr/bin/env python3
"""
Kobon (كوبون) — kobon.is-a.si — dependency-free static site generator.
Reads data/*.json, writes the whole site (AR at /, EN at /en/) to the repo root.
Run: python3 build.py
"""
from __future__ import annotations

import html
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DOMAIN = "https://kobon.is-a.si"
CNAME_HOST = "kobon.is-a.si"
NAME = {"ar": "كوبون", "en": "Kobon"}
EMAIL = "partners@kobon.is-a.si"
YEAR = 2026
TODAY = date.today().isoformat()
ASSET_V = "3"

COUNTRIES = [
    ("sa", "السعودية", "Saudi Arabia", "ر.س", "SAR"),
    ("ae", "الإمارات", "UAE", "د.إ", "AED"),
    ("kw", "الكويت", "Kuwait", "د.ك", "KWD"),
    ("qa", "قطر", "Qatar", "ر.ق", "QAR"),
    ("bh", "البحرين", "Bahrain", "د.ب", "BHD"),
    ("om", "عُمان", "Oman", "ر.ع", "OMR"),
    ("eg", "مصر", "Egypt", "ج.م", "EGP"),
]

FLAGS = {
    "sa": '<rect width="30" height="30" fill="#006C35"/><rect x="8" y="14" width="14" height="2" fill="#fff"/>',
    "ae": '<rect width="30" height="10" fill="#00732F"/><rect y="10" width="30" height="10" fill="#fff"/><rect y="20" width="30" height="10" fill="#000"/><rect width="9" height="30" fill="#FF0000"/>',
    "kw": '<rect width="30" height="10" fill="#007A3D"/><rect y="10" width="30" height="10" fill="#fff"/><rect y="20" width="30" height="10" fill="#CE1126"/><path d="M0 0l9 10v10L0 30z" fill="#000"/>',
    "qa": '<rect width="30" height="30" fill="#8A1538"/><path d="M0 0h10l3 2-3 2 3 2-3 2 3 2-3 2 3 2-3 2 3 2-3 2 3 2-3 2 3 2-3 2 3 2H0z" fill="#fff"/>',
    "bh": '<rect width="30" height="30" fill="#CE1126"/><path d="M0 0h10l3 3-3 3 3 3-3 3 3 3-3 3 3 3-3 3 3 3-3 3H0z" fill="#fff"/>',
    "om": '<rect width="30" height="10" fill="#fff"/><rect y="10" width="30" height="10" fill="#DB161B"/><rect y="20" width="30" height="10" fill="#008000"/><rect width="10" height="30" fill="#DB161B"/>',
    "eg": '<rect width="30" height="10" fill="#CE1126"/><rect y="10" width="30" height="10" fill="#fff"/><rect y="20" width="30" height="10" fill="#000"/><circle cx="15" cy="15" r="2.5" fill="#C09300"/>',
}

CAT_ICON = {
    "fashion": '<circle cx="28" cy="28" r="28" fill="#FFF0EB"/><path d="M20 18l8 5 8-5 6 6-4 4v14H18V28l-4-4z" fill="#FF5A36"/>',
    "beauty": '<circle cx="28" cy="28" r="28" fill="#EFEDFF"/><rect x="23" y="22" width="10" height="20" rx="3" fill="#6D5BFF"/><rect x="25" y="14" width="6" height="9" rx="2" fill="#0E1330"/>',
    "electronics": '<circle cx="28" cy="28" r="28" fill="#E7F8F5"/><rect x="20" y="13" width="16" height="30" rx="4" fill="#14B8A6"/><rect x="23" y="17" width="10" height="20" rx="1" fill="#fff"/>',
    "travel": '<circle cx="28" cy="28" r="28" fill="#FFF6DD"/><path d="M14 31l28-10-3 7-12 3-5 9-3-1 2-7-6 1z" fill="#E0A100"/>',
    "home": '<circle cx="28" cy="28" r="28" fill="#FFF0EB"/><path d="M15 29l13-11 13 11v12H15z" fill="#FF5A36"/><rect x="24" y="32" width="8" height="9" fill="#fff"/>',
    "food": '<circle cx="28" cy="28" r="28" fill="#E7F8F5"/><path d="M16 20h4l4 16h14l3-11H22" fill="none" stroke="#14B8A6" stroke-width="3.4" stroke-linejoin="round"/><circle cx="26" cy="41" r="2.6" fill="#0E1330"/><circle cx="37" cy="41" r="2.6" fill="#0E1330"/>',
}

SEASON_STYLE = {
    "white-friday": ("linear-gradient(135deg,#0E1330,#2C2F73)", '<path d="M12 2l2.6 6.6L21 9.3l-5 4.4 1.5 6.8L12 17l-5.5 3.5L8 13.7 3 9.3l6.4-.7z"/>'),
    "11-11": ("linear-gradient(135deg,#FF5A36,#FF8A3D)", '<rect x="5" y="3" width="3" height="18"/><rect x="11" y="3" width="3" height="18"/>'),
    "ramadan": ("linear-gradient(135deg,#0B8577,#14B8A6)", '<path d="M15 3a9 9 0 1 0 6 15A8 8 0 0 1 15 3z"/>'),
    "eid-al-fitr": ("linear-gradient(135deg,#6D5BFF,#9B8CFF)", '<rect x="4" y="9" width="16" height="12" rx="1"/><rect x="3" y="6" width="18" height="4"/>'),
    "founding-day": ("linear-gradient(135deg,#8A5B00,#E0A100)", '<path d="M4 21V5l8-3 8 3v16z"/>'),
    "saudi-national-day": ("linear-gradient(135deg,#006C35,#14B8A6)", '<path d="M5 3v18M5 4h13l-3 4 3 4H5"/>'),
}

LOGO_SVG = '<svg width="{s}" height="{s}" viewBox="0 0 48 48" aria-hidden="true"><path d="M8 6h32a4 4 0 0 1 4 4v9a5 5 0 0 0 0 10v9a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-9a5 5 0 0 0 0-10v-9a4 4 0 0 1 4-4z" fill="#FF5A36"/><circle cx="18" cy="18" r="4.2" fill="#fff"/><circle cx="30" cy="30" r="4.2" fill="#fff"/><path d="M31 14 17 34" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/></svg>'

CHECK = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="m9 12 2 2 4-4"/></svg>'

AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
MONTHS_AR = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def t(lang: str, ar: str, en: str) -> str:
    return ar if lang == "ar" else en


def L(lang: str, path: str) -> str:
    """Root-relative URL for a path in the given language tree."""
    return path if lang == "ar" else ("/en" + path)


def abs_url(lang: str, path: str) -> str:
    return DOMAIN + L(lang, path)


def load(name: str):
    with (DATA / name).open(encoding="utf-8") as f:
        return json.load(f)


def write(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def out_path(lang: str, path: str) -> str:
    base = "" if lang == "ar" else "en/"
    inner = path.strip("/")
    return base + (inner + "/" if inner else "") + "index.html"


def month_label(lang: str, iso: str) -> str:
    y, m = int(iso[:4]), int(iso[5:7])
    return f"{MONTHS_AR[m-1]} {y}" if lang == "ar" else f"{MONTHS_EN[m-1]} {y}"


def day_label(lang: str, iso: str) -> str:
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return f"{d} {MONTHS_AR[m-1]} {y}" if lang == "ar" else f"{d} {MONTHS_EN[m-1]} {y}"


def season_status(s: dict) -> str:
    if s["start"] <= TODAY < s["end"]:
        return "live"
    if TODAY < s["start"]:
        return "soon"
    return "past"


def flag(slug: str, size: int = 30, cls: str = "flag") -> str:
    return f'<svg class="{cls}" style="width:{size}px;height:{size}px" viewBox="0 0 30 30" aria-hidden="true">{FLAGS[slug]}</svg>'


def cat_icon(slug: str, size: int = 56) -> str:
    return f'<svg width="{size}" height="{size}" viewBox="0 0 56 56" aria-hidden="true">{CAT_ICON.get(slug, CAT_ICON["home"])}</svg>'


def jsonld(obj) -> str:
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def org_ld() -> dict:
    return {
        "@type": "Organization",
        "@id": DOMAIN + "/#org",
        "name": NAME["ar"],
        "alternateName": NAME["en"],
        "url": DOMAIN + "/",
        "logo": DOMAIN + "/assets/icon-512.png",
        "email": EMAIL,
        "description": "عروض رسمية فقط من متاجر الخليج ومصر، يديرها فريق تسويق بالعمولة. Official offers only, run by an affiliate marketing team.",
        "areaServed": ["SA", "AE", "KW", "QA", "BH", "OM", "EG"],
        "contactPoint": [{"@type": "ContactPoint", "contactType": "partnerships", "email": EMAIL, "availableLanguage": ["ar", "en"]}],
    }


def breadcrumb_ld(lang: str, crumbs: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(lang, p)} for i, (n, p) in enumerate(crumbs)
        ],
    }


def faq_ld(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in items
        ],
    }


def faq_html(items: list[tuple[str, str]], open_first: bool = True, dark: bool = False) -> str:
    out = []
    st = ' style="background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.12)"' if dark else ""
    sst = ' style="color:#fff"' if dark else ""
    pst = ' style="color:#C9CCE6"' if dark else ""
    for i, (q, a) in enumerate(items):
        op = " open" if (open_first and i == 0) else ""
        out.append(f"<details{op}{st}><summary{sst}>{esc(q)}</summary><p{pst}>{a}</p></details>")
    return "\n".join(out)


import re as _re


def strip_tags(s: str) -> str:
    return _re.sub(r"<[^>]+>", "", s)


NAV = [
    ("home", "/", "الرئيسية", "Home"),
    ("stores", "/stores/", "المتاجر", "Stores"),
    ("categories", "/categories/", "الفئات", "Categories"),
    ("seasons", "/seasons/", "المواسم", "Seasons"),
    ("how", "/how-it-works/", "كيف نعمل", "How it works"),
    ("partners", "/partners/", "للبراندات", "For Brands"),
    ("about", "/about/", "من نحن", "About"),
]


def head(lang: str, path: str, title: str, desc: str, ld: list[dict] | None = None, og_image: str = "/assets/og-default.png") -> str:
    canon = abs_url(lang, path)
    ar_url = abs_url("ar", path)
    en_url = abs_url("en", path)
    graph = [org_ld(), {
        "@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/", "name": NAME["ar"], "alternateName": NAME["en"],
        "inLanguage": ["ar", "en"], "publisher": {"@id": DOMAIN + "/#org"},
        "potentialAction": {"@type": "SearchAction", "target": DOMAIN + "/stores/?q={search_term_string}", "query-input": "required name=search_term_string"},
    }, {
        "@type": "WebPage", "@id": canon + "#webpage", "url": canon, "name": title, "description": desc,
        "inLanguage": "ar" if lang == "ar" else "en", "isPartOf": {"@id": DOMAIN + "/#website"},
    }]
    blocks = [jsonld({"@context": "https://schema.org", "@graph": graph})] + [jsonld(o) for o in (ld or [])]
    site = NAME[lang]
    return f"""<!DOCTYPE html>
<html lang="{'ar' if lang == 'ar' else 'en'}" dir="{'rtl' if lang == 'ar' else 'ltr'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{esc(canon)}">
<link rel="alternate" hreflang="ar" href="{esc(ar_url)}">
<link rel="alternate" hreflang="en" href="{esc(en_url)}">
<link rel="alternate" hreflang="x-default" href="{esc(ar_url)}">
<meta name="theme-color" content="#0E1330">
<link rel="preload" href="/assets/fonts/readex-pro-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/plex-arabic-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" sizes="180x180">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(site)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canon)}">
<meta property="og:image" content="{esc(DOMAIN + og_image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{'ar_AR' if lang == 'ar' else 'en_US'}">
<meta property="og:locale:alternate" content="{'en_US' if lang == 'ar' else 'ar_AR'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(DOMAIN + og_image)}">
{chr(10).join(blocks)}
</head>
<body>
<a class="skip" href="#main">{t(lang, 'تخطَّ إلى المحتوى', 'Skip to content')}</a>
"""


def logo(lang: str, size: int = 44) -> str:
    small = "KOBON" if lang == "ar" else "كوبون"
    return f'{LOGO_SVG.format(s=size)}<span>{NAME[lang]}<small>{small}</small></span>'


def header(lang: str, path: str, active: str, cta: tuple[str, str] | None = None, announce: bool = True) -> str:
    other = "en" if lang == "ar" else "ar"
    switch = L(other, path)
    nav = "".join(
        f'<a{" class=\"active\" aria-current=\"page\"" if key == active else ""} href="{L(lang, p)}">{t(lang, ar, en)}</a>' for key, p, ar, en in NAV
    )
    cta_label, cta_href = cta or (t(lang, "شراكة معنا", "Partner with us"), L(lang, "/partners/#contact"))
    ann = ""
    if announce:
        ann = '<div class="announce">' + t(
            lang,
            "منصة جديدة بمعايير صارمة: <b>عروض رسمية فقط</b>. أولى العروض الحصرية قريبًا، اشترك ليصلك كل جديد.",
            "A new platform with strict standards: <b>official offers only</b>. Our first exclusive deals are coming soon. Subscribe to hear first.",
        ) + "</div>\n"
    return f"""{ann}<header class="header"><div class="wrap">
  <a class="logo" href="{L(lang, '/')}" aria-label="{esc(NAME[lang])}">{logo(lang)}</a>
  <nav class="nav" aria-label="{t(lang, 'القائمة الرئيسية', 'Main')}">{nav}</nav>
  <div class="header-actions">
    <a class="pill" href="{L(lang, '/countries/')}">{flag('sa', 20)}{t(lang, 'الدول', 'Countries')}</a>
    <a class="pill lang" href="{switch}" hreflang="{other}" lang="{other}">{t(lang, 'EN', 'العربية')}</a>
    <a class="btn btn-primary" href="{cta_href}">{esc(cta_label)}</a>
    <details class="menu"><summary aria-label="{t(lang, 'فتح القائمة', 'Open menu')}"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0E1330" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>
      <div class="panel">{nav}<a href="{L(lang, '/countries/')}">{t(lang, 'الدول', 'Countries')}</a><a href="{L(lang, '/contact/')}">{t(lang, 'تواصل معنا', 'Contact')}</a><a href="{switch}" hreflang="{other}" lang="{other}">{t(lang, 'English', 'العربية')}</a><a class="btn btn-primary" href="{cta_href}">{esc(cta_label)}</a></div>
    </details>
  </div>
</div></header>
"""


def footer(lang: str, path: str, flush: bool = False) -> str:
    other = "en" if lang == "ar" else "ar"
    def li(p, ar, en):
        return f'<li><a href="{L(lang, p)}">{t(lang, ar, en)}</a></li>'
    style = ' style="margin-top:0"' if flush else ""
    return f"""<footer class="footer"{style}><div class="wrap">
  <div class="cols">
    <div><a class="logo" href="{L(lang, '/')}">{logo(lang, 40)}</a><p class="disclosure">{t(lang, 'دليل عروض رسمية للخليج ومصر، يديره فريق تسويق بالعمولة. قد نحصل على عمولة عند الشراء عبر روابطنا، دون أي تكلفة إضافية عليك.', 'An official-deals guide for the Gulf and Egypt, run by an affiliate marketing team. We may earn a commission when you buy through our links, at no extra cost to you.')}</p></div>
    <div><h4>{t(lang, 'تسوّق', 'Shop')}</h4><ul>{li('/stores/', 'المتاجر', 'Stores')}{li('/categories/', 'الفئات', 'Categories')}{li('/seasons/', 'المواسم', 'Seasons')}{li('/countries/', 'الدول', 'Countries')}</ul></div>
    <div><h4>{NAME[lang]}</h4><ul>{li('/about/', 'من نحن', 'About us')}{li('/how-it-works/', 'كيف نعمل', 'How it works')}{li('/how-it-works/#standard', 'معيار التحقق', 'Our standard')}{li('/contact/', 'تواصل معنا', 'Contact')}</ul></div>
    <div><h4>{t(lang, 'للبراندات', 'For brands')}</h4><ul>{li('/partners/', 'الشراكات', 'Partnerships')}{li('/partners/#models', 'نماذج التعاون', 'Collaboration models')}{li('/partners/#founding', 'الشركاء المؤسسون', 'Founding partners')}<li><a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
    <div><h4>{t(lang, 'قانوني', 'Legal')}</h4><ul>{li('/privacy/', 'الخصوصية', 'Privacy')}{li('/terms/', 'الشروط', 'Terms')}{li('/affiliate-disclosure/', 'الإفصاح عن العمولة', 'Affiliate disclosure')}</ul></div>
  </div>
  <div class="legal"><span>© {YEAR} {NAME[lang]} · kobon.is-a.si</span><span><a href="{L('ar', path)}" lang="ar" hreflang="ar">العربية</a> · <a href="{L('en', path)}" lang="en" hreflang="en">English</a></span></div>
</div></footer>
<script src="/assets/app.js?v={ASSET_V}" defer></script>
</body></html>
"""


def page_hero(lang: str, crumbs: list[tuple[str, str]], eyebrow: str, h1: str, lead: str, art: str = "", dark: bool = False, extra: str = "") -> str:
    cr = " / ".join(
        (f'<a href="{L(lang, p)}">{esc(n)}</a>' if i < len(crumbs) - 1 else f'<span aria-current="page">{esc(n)}</span>') for i, (n, p) in enumerate(crumbs)
    )
    ecls = "eyebrow light" if dark else "eyebrow"
    solo = "" if art else " solo"
    return f"""<section class="page-hero{' dark' if dark else ''}"><div class="wrap{solo}">
  <div class="copy"><nav class="crumbs" aria-label="{t(lang, 'مسار الصفحة', 'Breadcrumb')}">{cr}</nav><span class="{ecls}">{eyebrow}</span><h1>{h1}</h1><p class="lead">{lead}</p>{extra}</div>
  {art}
</div></section>
"""


def render(lang: str, path: str, title: str, desc: str, body: str, active: str = "", ld: list[dict] | None = None,
           crumbs: list[tuple[str, str]] | None = None, cta=None, flush_footer: bool = False, announce: bool = True) -> None:
    lds = list(ld or [])
    if crumbs:
        lds.append(breadcrumb_ld(lang, crumbs))
    html_out = head(lang, path, title, desc, lds) + header(lang, path, active, cta, announce) + f'<main id="main">\n{body}\n</main>\n' + footer(lang, path, flush_footer)
    write(out_path(lang, path), html_out)
    PAGES.append(path if lang == "ar" else None)


PAGES: list = []
SITEMAP: list[str] = []


def section_head(eyebrow: str, h2: str, p: str = "", cls: str = "") -> str:
    pp = f"<p>{p}</p>" if p else ""
    return f'<div class="section-head"><span class="eyebrow {cls}">{eyebrow}</span><h2>{h2}</h2>{pp}</div>'


def empty_block(lang: str, title: str, text: str, actions: str, icon: str = "") -> str:
    ic = icon or f'<svg class="big-ic" viewBox="0 0 96 96" aria-hidden="true"><circle cx="48" cy="48" r="48" fill="#FFF0EB"/><path d="M26 30h44a4 4 0 0 1 4 4v8a6 6 0 0 0 0 12v8a4 4 0 0 1-4 4H26a4 4 0 0 1-4-4v-8a6 6 0 0 0 0-12v-8a4 4 0 0 1 4-4z" fill="#FF5A36"/><path d="M58 32v32" stroke="#fff" stroke-dasharray="3 4" stroke-width="2"/><circle cx="38" cy="42" r="3" fill="#fff"/><circle cx="46" cy="54" r="3" fill="#fff"/><path d="M47 40 37 56" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/></svg>'
    return f'<div class="empty">{ic}<div style="display:grid;gap:.6rem"><h3 style="font-size:1.35rem">{title}</h3><p>{text}</p><div class="actions">{actions}</div></div></div>'


def hero_svg(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    coin = a("ر.س", "SAR")
    return f'''<svg viewBox="0 0 560 500" role="img" aria-label="{a('رسم توضيحي: جوال عليه عرض رسمي موثّق وأكياس تسوق', 'Illustration: a phone showing a verified official offer, with shopping bags')}">
      <defs>
        <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6D5BFF"/><stop offset="1" stop-color="#FF5A36"/></linearGradient>
        <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#F4EEE7"/></linearGradient>
        <filter id="sh" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#0E1330" flood-opacity=".22"/></filter>
      </defs>
      <circle cx="290" cy="250" r="210" fill="url(#g1)" opacity=".12"/>
      <circle cx="290" cy="250" r="150" fill="none" stroke="#0E1330" stroke-opacity=".08" stroke-dasharray="4 10" stroke-width="2"/>
      <g filter="url(#sh)"><rect x="190" y="40" width="200" height="410" rx="34" fill="#0E1330"/><rect x="202" y="54" width="176" height="382" rx="24" fill="url(#g2)"/><rect x="262" y="62" width="56" height="10" rx="5" fill="#0E1330"/></g>
      <rect x="216" y="92" width="110" height="10" rx="5" fill="#0E1330" opacity=".85"/>
      <rect x="216" y="110" width="80" height="8" rx="4" fill="#7A7F9A" opacity=".5"/>
      <rect x="216" y="134" width="148" height="88" rx="16" fill="#FF5A36"/>
      <text x="350" y="178" font-family="Readex Pro" font-weight="700" font-size="30" fill="#fff" text-anchor="end">&#8206;-30%</text>
      <text x="350" y="204" font-family="IBM Plex Sans Arabic" font-size="12" fill="#fff" text-anchor="end" opacity=".9">{a('عرض رسمي من المتجر', 'Official store offer')}</text>
      <rect x="216" y="236" width="148" height="52" rx="14" fill="#fff" stroke="#ECE6DE"/>
      <circle cx="342" cy="262" r="12" fill="#E7F8F5"/><path d="m336 262 4 4 8-8" stroke="#14B8A6" stroke-width="3" fill="none" stroke-linecap="round"/>
      <rect x="236" y="254" width="80" height="8" rx="4" fill="#0E1330" opacity=".75"/><rect x="256" y="268" width="60" height="6" rx="3" fill="#7A7F9A" opacity=".5"/>
      <rect x="216" y="300" width="148" height="52" rx="14" fill="#fff" stroke="#ECE6DE"/>
      <circle cx="342" cy="326" r="12" fill="#FFF6DD"/><path d="M342 319v8m0 4v1" stroke="#E0A100" stroke-width="3" stroke-linecap="round"/>
      <rect x="236" y="318" width="80" height="8" rx="4" fill="#0E1330" opacity=".75"/><rect x="256" y="332" width="60" height="6" rx="3" fill="#7A7F9A" opacity=".5"/>
      <rect x="216" y="372" width="148" height="40" rx="20" fill="#0E1330"/>
      <text x="290" y="397" font-family="Readex Pro" font-weight="600" font-size="13" fill="#fff" text-anchor="middle">{a('اذهب للمتجر ←', 'Go to store →')}</text>
      <g filter="url(#sh)" transform="rotate(-8 110 150)">
        <path d="M40 110h130a10 10 0 0 1 10 10v18a12 12 0 0 0 0 24v18a10 10 0 0 1-10 10H40a10 10 0 0 1-10-10v-18a12 12 0 0 0 0-24v-18a10 10 0 0 1 10-10z" fill="#FFC233"/>
        <line x1="128" y1="116" x2="128" y2="184" stroke="#0E1330" stroke-opacity=".3" stroke-dasharray="5 5" stroke-width="2"/>
        <text x="80" y="156" font-family="Readex Pro" font-weight="700" font-size="26" fill="#0E1330" text-anchor="middle">%</text>
        <text x="154" y="148" font-family="Readex Pro" font-weight="700" font-size="13" fill="#0E1330" text-anchor="middle">VIP</text>
        <text x="154" y="166" font-family="IBM Plex Sans Arabic" font-size="10" fill="#0E1330" text-anchor="middle">{a('حصري', 'Exclusive')}</text>
      </g>
      <g filter="url(#sh)">
        <rect x="380" y="120" width="160" height="62" rx="18" fill="#fff"/>
        <circle cx="512" cy="151" r="16" fill="#14B8A6"/><path d="m505 151 5 5 9-9" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/>
        <text x="486" y="146" font-family="Readex Pro" font-weight="600" font-size="13" fill="#0E1330" text-anchor="end">{a('مصدر رسمي', 'Official source')}</text>
        <text x="486" y="166" font-family="IBM Plex Sans Arabic" font-size="11" fill="#7A7F9A" text-anchor="end">{a('روجع اليوم', 'Checked today')}</text>
      </g>
      <g filter="url(#sh)">
        <path d="M410 300h96l10 130a12 12 0 0 1-12 13h-92a12 12 0 0 1-12-13z" fill="#14B8A6"/>
        <path d="M432 300v-14a26 26 0 0 1 52 0v14" fill="none" stroke="#0E1330" stroke-width="6" stroke-linecap="round"/>
        <circle cx="458" cy="370" r="22" fill="#fff" opacity=".9"/>
        <text x="458" y="378" font-family="Readex Pro" font-weight="700" font-size="20" fill="#14B8A6" text-anchor="middle">%</text>
      </g>
      <g filter="url(#sh)"><circle cx="110" cy="360" r="40" fill="#6D5BFF"/><circle cx="110" cy="360" r="30" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="2"/><text x="110" y="369" font-family="Readex Pro" font-weight="700" font-size="{24 if lang == 'ar' else 18}" fill="#fff" text-anchor="middle">{coin}</text></g>
      <path d="M520 60l6 14 14 6-14 6-6 14-6-14-14-6 14-6z" fill="#FFC233"/>
      <path d="M60 250l4 9 9 4-9 4-4 9-4-9-9-4 9-4z" fill="#FF5A36"/>
      <circle cx="160" cy="460" r="6" fill="#14B8A6"/><circle cx="520" cy="250" r="5" fill="#6D5BFF"/>
    </svg>'''


def strip_html(lang: str) -> str:
    items = [
        (CHECK.format(s=24, c="#FFC233"), t(lang, "عروض رسمية فقط", "Official offers only"), t(lang, "من المتجر أو شريكه المعتمد", "From the store or its approved partner")),
        ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#14B8A6" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>', t(lang, "تاريخ مراجعة ظاهر", "Visible check date"), t(lang, "على كل عرض", "On every offer")),
        ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2"><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/><circle cx="12" cy="12" r="9"/></svg>', t(lang, "7 أسواق", "7 markets"), t(lang, "الخليج ومصر", "The Gulf and Egypt")),
        ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#A99FFF" stroke-width="2"><path d="M4 5h16v11H8l-4 4z"/></svg>', t(lang, "عربي وإنجليزي", "Arabic & English"), t(lang, "بلغة واضحة وبسيطة", "In clear, simple language")),
    ]
    return '<div class="wrap"><div class="strip">' + "".join(
        f'<div><span class="ic">{ic}</span><span><b>{b}</b><small>{s}</small></span></div>' for ic, b, s in items
    ) + "</div></div>"


def why_cards(lang: str) -> str:
    return f'''<div class="grid-3">
      <article class="card"><span class="ic bg-coral">{CHECK.format(s=30, c="#FF5A36")}</span><h3>{t(lang, 'سياسة «الرسمي فقط»', 'An “official-only” policy')}</h3><p>{t(lang, 'لا ننشر أي كود إلا إذا جاء من المتجر نفسه أو من برنامج شراكة رسمي. وإذا لم نتأكد، لا ننشره.', 'We only publish a code if it comes from the store itself or an official partner programme. If we can’t confirm it, we don’t post it.')}</p></article>
      <article class="card"><span class="ic bg-mint"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#14B8A6" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8 9h8M8 13h8M8 17h5"/></svg></span><h3>{t(lang, 'الشروط كاملة أمامك', 'Every term up front')}</h3><p>{t(lang, 'الحد الأدنى للطلب، وأقصى خصم، والدول، وتاريخ الانتهاء. كلها في بطاقة واحدة واضحة قبل أن تنسخ الكود.', 'Minimum order, maximum discount, countries and expiry date, all on one clear card before you copy the code.')}</p></article>
      <article class="card"><span class="ic bg-saffron"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#E0A100" stroke-width="2"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg></span><h3>{t(lang, 'تقويم المواسم', 'A season calendar')}</h3><p>{t(lang, 'الجمعة البيضاء و11.11 ورمضان والعيد. نجهّز صفحة لكل موسم قبل موعده، لتخطط لمشترياتك مبكرًا.', 'White Friday, 11.11, Ramadan and Eid. We prepare a page for every season before it starts, so you can plan your shopping early.')}</p></article>
    </div>'''


def steps_html(lang: str) -> str:
    return f'''<div class="steps">
      <div class="step"><div class="art bg-violet"><svg width="200" height="140" viewBox="0 0 200 140" aria-hidden="true"><rect x="20" y="40" width="160" height="44" rx="22" fill="#fff"/><circle cx="154" cy="62" r="10" fill="none" stroke="#6D5BFF" stroke-width="4"/><path d="m161 69 8 8" stroke="#6D5BFF" stroke-width="4" stroke-linecap="round"/><rect x="40" y="56" width="90" height="12" rx="6" fill="#0E1330" opacity=".2"/><rect x="40" y="96" width="50" height="22" rx="11" fill="#fff"/><rect x="96" y="96" width="64" height="22" rx="11" fill="#6D5BFF" opacity=".25"/></svg></div>
        <span class="num">1</span><h3>{t(lang, 'ابحث عن متجرك', 'Find your store')}</h3><p>{t(lang, 'اختر المتجر أو الفئة، أو افتح صفحة الموسم.', 'Pick a store or category, or open a season page.')}</p></div>
      <div class="step"><div class="art bg-coral"><svg width="200" height="140" viewBox="0 0 200 140" aria-hidden="true"><path d="M30 30h140a8 8 0 0 1 8 8v20a12 12 0 0 0 0 24v20a8 8 0 0 1-8 8H30a8 8 0 0 1-8-8V82a12 12 0 0 0 0-24V38a8 8 0 0 1 8-8z" fill="#fff"/><line x1="130" y1="36" x2="130" y2="104" stroke="#FF5A36" stroke-dasharray="5 5" stroke-width="2"/><text x="154" y="78" font-family="Readex Pro" font-weight="700" font-size="22" fill="#FF5A36" text-anchor="middle">%</text><rect x="44" y="52" width="70" height="10" rx="5" fill="#0E1330" opacity=".7"/><rect x="44" y="70" width="50" height="8" rx="4" fill="#0E1330" opacity=".25"/><rect x="44" y="84" width="60" height="8" rx="4" fill="#0E1330" opacity=".25"/></svg></div>
        <span class="num">2</span><h3>{t(lang, 'اقرأ الشروط وانسخ', 'Read the terms & copy')}</h3><p>{t(lang, 'في كل بطاقة الشروط وتاريخ المراجعة ومصدر العرض.', 'Every card shows the terms, the last-checked date and the offer’s source.')}</p></div>
      <div class="step"><div class="art bg-mint"><svg width="200" height="140" viewBox="0 0 200 140" aria-hidden="true"><path d="M60 46h80l8 70a8 8 0 0 1-8 9H60a8 8 0 0 1-8-9z" fill="#14B8A6"/><path d="M78 46V38a22 22 0 0 1 44 0v8" fill="none" stroke="#0E1330" stroke-width="5" stroke-linecap="round"/><circle cx="100" cy="86" r="18" fill="#fff"/><path d="m91 86 6 6 12-12" stroke="#14B8A6" stroke-width="4" fill="none" stroke-linecap="round"/></svg></div>
        <span class="num">3</span><h3>{t(lang, 'اشترِ ووفّر', 'Shop & save')}</h3><p>{t(lang, 'ننقلك إلى موقع المتجر الرسمي، وتطبّق الكود في صفحة الدفع.', 'We take you to the store’s official site, and you apply the code at checkout.')}</p></div>
    </div>'''


STANDARD = [
    ("المصدر", "Source", "نتأكد أن العرض صادر عن المتجر أو عن برنامج شراكة معتمد.", "We confirm the offer comes from the store or an approved partner programme."),
    ("الشروط", "Terms", "نوثّق الحد الأدنى وأقصى خصم والدول والاستثناءات.", "We record the minimum spend, maximum discount, countries and exclusions."),
    ("التجربة", "Test", "نجرّب الكود على سلة حقيقية متى أمكن ذلك.", "We test the code on a real basket whenever possible."),
    ("المتابعة", "Monitor", "يُحذف العرض المنتهي، ويبقى تاريخ آخر مراجعة ظاهرًا.", "Expired offers are removed, and the last-checked date stays visible."),
]


def standard_list(lang: str) -> str:
    return '<div class="vlist">' + "".join(
        f'<div class="vitem"><span class="n">{i+1}</span><div><h3>{t(lang, a, b)}</h3><p>{t(lang, c, d)}</p></div></div>' for i, (a, b, c, d) in enumerate(STANDARD)
    ) + "</div>"


def sample_tickets(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    return f'''<div style="display:grid;gap:1.2rem">
      <p style="color:var(--muted);font-size:.9rem;text-align:center"><span class="tag-ex">{a('مثال توضيحي', 'Illustrative example')}</span> {a('شكل بطاقة العرض، وليس عرضًا حقيقيًا', 'How an offer card looks. This is not a real offer.')}</p>
      <div class="ticket" aria-label="{a('مثال توضيحي لبطاقة عرض', 'Illustrative offer card')}">
        <div class="main">
          <div style="display:flex;gap:.5rem;flex-wrap:wrap"><span class="badge ok">✓ {a('مصدر رسمي', 'Official source')}</span><span class="badge warn">{a('متبقٍ 5 أيام', '5 days left')}</span></div>
          <h3>{a('خصم 20% على الطلب الأول', '20% off your first order')}</h3>
          <p style="color:var(--ink-soft);font-size:.92rem">{a('اسم المتجر · أزياء · السعودية والإمارات', 'Store name · Fashion · Saudi Arabia & UAE')}</p>
          <div class="meta"><span>{a('الحد الأدنى', 'Min. spend')}<b>{a('150 ر.س', 'SAR 150')}</b></span><span>{a('أقصى خصم', 'Max. discount')}<b>{a('100 ر.س', 'SAR 100')}</b></span><span>{a('آخر مراجعة', 'Last checked')}<b>{a('اليوم', 'Today')}</b></span></div>
        </div>
        <div class="side"><div><b>20%</b><div style="font-size:.9rem;margin-top:.4rem">{a('اكشف الكود', 'Reveal code')}</div></div></div>
      </div>
      <div class="ticket" style="transform:scale(.94);opacity:.75">
        <div class="main"><div><span class="badge ok">✓ {a('مصدر رسمي', 'Official source')}</span></div><h3>{a('شحن مجاني فوق 99 ر.س', 'Free shipping over SAR 99')}</h3><div class="meta"><span>{a('الدول', 'Countries')}<b>{a('الخليج', 'GCC')}</b></span><span>{a('النوع', 'Type')}<b>{a('عرض', 'Deal')}</b></span><span>{a('آخر مراجعة', 'Last checked')}<b>{a('أمس', 'Yesterday')}</b></span></div></div>
        <div class="side" style="background:var(--mint)"><div><b style="font-size:1.4rem">{a('شحن<br>مجاني', 'Free<br>ship')}</b></div></div>
      </div>
    </div>'''


def cats_html(lang: str, cats: list[dict]) -> str:
    return '<div class="cats">' + "".join(
        f'<a class="cat" href="{L(lang, "/categories/" + c["slug"] + "/")}">{cat_icon(c["slug"])}{esc(c["name_" + lang])}<small>{esc(c["short_" + lang])}</small></a>' for c in cats
    ) + "</div>"


def season_card(lang: str, s: dict) -> str:
    bg, glyph = SEASON_STYLE.get(s["slug"], SEASON_STYLE["white-friday"])
    st = season_status(s)
    if st == "live":
        tag = t(lang, "● قائم الآن", "● Live now")
    else:
        tag = month_label(lang, s["start"])
    return f'<a class="season" href="{L(lang, "/seasons/" + s["slug"] + "/")}" style="background:{bg}"><span class="tag">{tag}</span><div><h3>{esc(s["name_" + lang])}</h3><div class="date">{esc(s["note_" + lang])}</div></div><svg width="140" height="140" viewBox="0 0 24 24" fill="#fff" aria-hidden="true">{glyph}</svg></a>'


def countries_html(lang: str) -> str:
    return '<div class="countries">' + "".join(
        f'<a class="country" href="{L(lang, "/countries/" + c[0] + "/")}">{flag(c[0])}{c[1] if lang == "ar" else c[2]}</a>' for c in COUNTRIES
    ) + "</div>"


def band_html(lang: str) -> str:
    return f'''<section class="wrap">
  <div class="band">
    <div style="display:grid;gap:1rem">
      <span class="eyebrow light">{t(lang, 'للبراندات والمتاجر', 'For brands & stores')}</span>
      <h2>{t(lang, 'لديك علامة تجارية؟ دعنا ننمّي مبيعاتك، وادفع مقابل النتائج.', 'Own a brand? Let us grow your sales, and pay for results.')}</h2>
      <p>{t(lang, 'نحن فريق متخصص في التسويق بالأداء والعمولة. نحوّل عروضك الرسمية إلى حملات تحقق مبيعات قابلة للقياس، عبر موقعنا وقنواتنا في الخليج ومصر.', 'We’re a team specialised in performance and affiliate marketing. We turn your official offers into campaigns with measurable sales, through our site and channels across the Gulf and Egypt.')}</p>
      <div class="actions"><a class="btn btn-primary" href="{L(lang, '/partners/')}">{t(lang, 'اكتشف الشراكة ←', 'Explore partnerships →')}</a><a class="btn btn-outline-light mail" href="mailto:{EMAIL}">{EMAIL}</a></div>
    </div>
    <svg viewBox="0 0 320 240" aria-hidden="true">
      <rect x="10" y="20" width="300" height="200" rx="22" fill="#fff" opacity=".06"/>
      <rect x="30" y="40" width="120" height="12" rx="6" fill="#fff" opacity=".5"/>
      <rect x="30" y="60" width="70" height="8" rx="4" fill="#fff" opacity=".25"/>
      <path d="M30 190 C80 180 90 150 130 150 S190 120 220 100 S270 70 290 50" fill="none" stroke="#FFC233" stroke-width="5" stroke-linecap="round"/>
      <path d="M30 190 C80 180 90 150 130 150 S190 120 220 100 S270 70 290 50 V200 H30z" fill="#FFC233" opacity=".12"/>
      <circle cx="290" cy="50" r="8" fill="#FFC233"/><circle cx="290" cy="50" r="16" fill="#FFC233" opacity=".25"/>
      <g opacity=".5"><rect x="30" y="204" width="40" height="6" rx="3" fill="#fff"/><rect x="100" y="204" width="40" height="6" rx="3" fill="#fff"/><rect x="170" y="204" width="40" height="6" rx="3" fill="#fff"/><rect x="240" y="204" width="40" height="6" rx="3" fill="#fff"/></g>
    </svg>
  </div>
</section>'''


def news_html(lang: str) -> str:
    subj = t(lang, "اشتراك في تنبيهات العروض", "Subscribe to offer alerts")
    return f'''<section class="section" id="alerts">
  <div class="wrap news">
    <div><h2>{t(lang, 'اعرف العرض قبل الجميع', 'Hear about offers first')}</h2><p style="margin-top:.6rem">{t(lang, 'رسالة واحدة أسبوعيًا بأهم العروض الرسمية، دون إزعاج، ويمكنك إلغاء الاشتراك في أي وقت.', 'One weekly email with the best official offers. No spam, and you can unsubscribe any time.')}</p></div>
    <form class="js-mailto" data-to="{EMAIL}" data-subject="{esc(subj)}" action="mailto:{EMAIL}" method="get" enctype="text/plain">
      <label class="sr" for="news-email" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">{t(lang, 'بريدك الإلكتروني', 'Your email')}</label>
      <input type="hidden" name="subject" value="{esc(subj)}">
      <input id="news-email" name="body" type="email" required placeholder="{t(lang, 'بريدك الإلكتروني', 'Your email')}" autocomplete="email" dir="ltr">
      <button class="btn" style="background:var(--ink);color:#fff">{t(lang, 'اشترك', 'Subscribe')}</button>
    </form>
  </div>
</section>'''


HOME_FAQ = {
    "ar": [
        ("ما هو كوبون؟", "«كوبون» دليل عروض وأكواد خصم للسعودية والخليج ومصر، يديره فريق تسويق بالعمولة بخبرة في الخليج ومصر. لا ننشر إلا العروض الصادرة عن مصادر رسمية."),
        ("لماذا لا توجد عروض كثيرة بعد؟", "لأننا لا ننشر أي كود لا نعرف مصدره. تُضاف العروض فور تفعيل الشراكات الرسمية مع المتاجر."),
        ("هل يحصل كوبون على عمولة؟", "قد نحصل على عمولة من المتجر عندما تشتري عبر رابط شراكة، دون أي تكلفة إضافية عليك. ونوضح ذلك في صفحة الإفصاح عن العمولة."),
        ("الكود لم يعمل، ماذا أفعل؟", "راجع الشروط في بطاقة العرض، وإن استمرت المشكلة راسلنا من صفحة التواصل وسنراجعه في يوم العمل نفسه."),
    ],
    "en": [
        ("What is Kobon?", "Kobon is a deals and discount-code guide for Saudi Arabia, the Gulf and Egypt, run by an affiliate marketing team with experience across the Gulf and Egypt. We only publish offers from official sources."),
        ("Why aren’t there many offers yet?", "Because we never publish a code we can’t trace to its source. Offers are added as soon as official partnerships with stores go live."),
        ("Does Kobon earn a commission?", "We may earn a commission from the store when you buy through a partner link, at no extra cost to you. Our affiliate disclosure page explains this."),
        ("A code didn’t work. What should I do?", "Check the terms on the offer card. If it still doesn’t work, message us from the contact page and we’ll review it the same business day."),
    ],
}


def build_home(lang: str, cats: list[dict], seasons: list[dict]) -> None:
    a = lambda ar, en: t(lang, ar, en)
    chips = "".join(f'<a class="chip" href="{L(lang, "/categories/" + c["slug"] + "/")}">{esc(c["name_" + lang])}</a>' for c in cats[:5])
    cal = [s for s in seasons if s["slug"] in ("white-friday", "11-11", "ramadan", "eid-al-fitr")]
    cal.sort(key=lambda s: s["start"])
    body = f'''<section class="hero">
  <div class="blob" style="width:420px;height:420px;background:#FFC233;top:-120px;inset-inline-end:-80px"></div>
  <div class="blob" style="width:360px;height:360px;background:#14B8A6;bottom:-160px;inset-inline-start:30%;opacity:.25"></div>
  <div class="wrap">
    <div class="hero-copy">
      <span class="eyebrow">✦ {a('دليل عروض يديره فريق مسوّقين محترفين', 'A deals guide run by professional marketers')}</span>
      <h1>{a('وفّر بذكاء،<br>بعروض <span class="hl-u">رسمية فقط</span>.', 'Shop smart,<br>with <span class="hl-u">official offers only</span>.')}</h1>
      <p class="lead">{a('يجمع لك «كوبون» العروض التي تطلقها المتاجر نفسها في السعودية والخليج ومصر. يظهر مع كل عرض مصدره وشروطه وتاريخ آخر مراجعة، بلا أكواد وهمية ولا وقت ضائع.', 'Kobon collects the offers stores launch themselves across Saudi Arabia, the Gulf and Egypt. Every offer shows its source, terms and last-checked date: no fake codes, no wasted time.')}</p>
      <form class="search" action="{L(lang, '/stores/')}" method="get" role="search">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7A7F9A" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input name="q" aria-label="{a('ابحث عن متجر أو فئة', 'Search for a store or category')}" placeholder="{a('ابحث عن متجر أو فئة… مثل: أزياء، إلكترونيات', 'Search a store or category… e.g. fashion, electronics')}">
        <button class="btn btn-primary"><span>{a('ابحث', 'Search')}</span> {a('←', '→')}</button>
      </form>
      <div class="chips">{chips}</div>
      <div class="trust-row"><span><i class="tick">✓</i>{a('مصدر كل عرض واضح', 'Clear source for every offer')}</span><span><i class="tick">✓</i>{a('تاريخ آخر مراجعة', 'Last-checked date')}</span><span><i class="tick">✓</i>{a('7 دول', '7 countries')}</span></div>
    </div>
    {hero_svg(lang)}
  </div>
</section>
{strip_html(lang)}
<section class="section">
  <div class="wrap">
    {section_head(a('لماذا كوبون؟', 'Why Kobon?'), a('ليس مجرد موقع كوبونات.<br><span class="hl">دليل تسوّق تثق به.</span>', 'Not just another coupon site.<br><span class="hl">A shopping guide you can trust.</span>'), a('تمتلئ معظم مواقع الكوبونات بأكواد منتهية. نحن نفعل العكس: عروض أقل عددًا، لكن كل عرض منها حقيقي ومشروح بالتفصيل.', 'Most coupon sites are full of expired codes. We do the opposite: fewer offers, but every one is real and fully explained.'), 'mint')}
    {why_cards(lang)}
  </div>
</section>
<section class="section" id="how" style="background:#fff;border-block:1px solid var(--line)">
  <div class="wrap">
    {section_head(a('كيف يعمل', 'How it works'), a('3 خطوات بلا تعقيد', 'Three simple steps'))}
    {steps_html(lang)}
  </div>
</section>
<section class="section">
  <div class="wrap verify">
    <div style="display:grid;gap:1.2rem">
      <span class="eyebrow mint">{a('معيار كوبون', 'The Kobon standard')}</span>
      <h2>{a('4 مراحل يمرّ بها<br>كل عرض قبل نشره', 'Every offer passes<br>4 checks before it’s published')}</h2>
      {standard_list(lang)}
      <a class="link" href="{L(lang, '/how-it-works/#standard')}">{a('اقرأ المعيار كاملًا ←', 'Read the full standard →')}</a>
    </div>
    {sample_tickets(lang)}
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    {section_head(a('الفئات', 'Categories'), a('تسوّق حسب اهتمامك', 'Shop by interest'))}
    {cats_html(lang, cats)}
  </div>
</section>
<section class="section" style="background:#fff;border-block:1px solid var(--line)">
  <div class="wrap">
    {section_head(a('تقويم المواسم', 'Season calendar'), a('استعد للموسم قبل أن يبدأ', 'Get ready before the season starts'), a('صفحة خاصة لكل موسم كبير، فيها المواعيد المتوقعة ونصائح الشراء، والعروض الرسمية فور صدورها.', 'A dedicated page for every big season, with expected dates, buying tips and the official offers as soon as they’re released.'))}
    <div class="seasons">{"".join(season_card(lang, s) for s in cal)}</div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {section_head(a('الأسواق', 'Markets'), a('عروض مخصّصة لبلدك', 'Offers for your country'), a('اختر بلدك لترى العروض الصالحة فيه فقط، بعملته وطرق الشحن إليه.', 'Choose your country to see only the offers valid there, in its currency and with its shipping options.'), 'mint')}
    {countries_html(lang)}
  </div>
</section>
{band_html(lang)}
{news_html(lang)}
<section class="section" style="padding-top:0">
  <div class="wrap">
    {section_head(a('أسئلة شائعة', 'FAQ'), a('لديك سؤال؟', 'Got a question?'))}
    <div class="faq">{faq_html(HOME_FAQ[lang])}</div>
  </div>
</section>'''
    title = a("كوبون | عروض وأكواد خصم رسمية فقط من متاجر الخليج ومصر", "Kobon | Official discount codes & deals only, for the Gulf and Egypt")
    desc = a("«كوبون» دليل عروض وأكواد خصم رسمية فقط للسعودية والإمارات والكويت وقطر والبحرين وعُمان ومصر. مع كل عرض مصدره وشروطه وتاريخ آخر مراجعة.",
             "Kobon is an official-only deals and discount-code guide for Saudi Arabia, the UAE, Kuwait, Qatar, Bahrain, Oman and Egypt. Every offer shows its source, terms and last-checked date.")
    render(lang, "/", title, desc, body, "home", [faq_ld(HOME_FAQ[lang])])


def dashboard_svg(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    return f'''<svg viewBox="0 0 520 440" role="img" aria-label="{a('لوحة أداء توضيحية لحملة', 'Illustrative campaign performance dashboard')}">
      <defs><filter id="s2" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="20" stdDeviation="20" flood-color="#000" flood-opacity=".35"/></filter>
      <linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF5A36" stop-opacity=".45"/><stop offset="1" stop-color="#FF5A36" stop-opacity="0"/></linearGradient></defs>
      <g filter="url(#s2)">
        <rect x="30" y="40" width="430" height="300" rx="26" fill="#fff"/>
        <rect x="30" y="40" width="430" height="52" rx="26" fill="#F6F2EC"/><rect x="30" y="66" width="430" height="26" fill="#F6F2EC"/>
        <circle cx="430" cy="66" r="7" fill="#FF5A36"/><circle cx="410" cy="66" r="7" fill="#FFC233"/><circle cx="390" cy="66" r="7" fill="#14B8A6"/>
        <text x="60" y="72" font-family="Readex Pro" font-weight="600" font-size="14" fill="#0E1330">Campaign · White Friday</text>
        <text x="430" y="130" font-family="IBM Plex Sans Arabic" font-size="13" fill="#7A7F9A" text-anchor="end">{a('المبيعات المنسوبة', 'Attributed sales')}</text>
        <rect x="300" y="142" width="130" height="16" rx="8" fill="#0E1330" opacity=".85"/>
        <rect x="372" y="168" width="58" height="18" rx="9" fill="#E7F8F5"/><text x="401" y="181" font-family="Readex Pro" font-size="11" font-weight="600" fill="#0B8577" text-anchor="middle">{a('▲ نمو', '▲ Growth')}</text>
        <path d="M60 300 C110 290 130 250 180 255 S250 210 290 205 S360 160 430 140 V310 H60z" fill="url(#ar)"/>
        <path d="M60 300 C110 290 130 250 180 255 S250 210 290 205 S360 160 430 140" fill="none" stroke="#FF5A36" stroke-width="4" stroke-linecap="round"/>
        <g fill="#0E1330" opacity=".08"><rect x="60" y="220" width="370" height="1"/><rect x="60" y="260" width="370" height="1"/><rect x="60" y="300" width="370" height="1"/></g>
        <rect x="60" y="120" width="90" height="10" rx="5" fill="#0E1330" opacity=".15"/><rect x="60" y="138" width="60" height="22" rx="8" fill="#6D5BFF" opacity=".18"/>
      </g>
      <g filter="url(#s2)">
        <rect x="0" y="270" width="190" height="130" rx="22" fill="#FFC233"/>
        <text x="170" y="308" font-family="IBM Plex Sans Arabic" font-size="13" fill="#0E1330" text-anchor="end">{a('قنوات الحملة', 'Campaign channels')}</text>
        <rect x="24" y="324" width="140" height="10" rx="5" fill="#0E1330" opacity=".85"/><rect x="64" y="344" width="100" height="10" rx="5" fill="#0E1330" opacity=".55"/><rect x="104" y="364" width="60" height="10" rx="5" fill="#0E1330" opacity=".3"/>
      </g>
      <g filter="url(#s2)">
        <rect x="350" y="0" width="160" height="70" rx="20" fill="#14B8A6"/>
        <circle cx="482" cy="35" r="16" fill="#fff"/><path d="m475 35 5 5 9-9" stroke="#14B8A6" stroke-width="3" fill="none" stroke-linecap="round"/>
        <text x="456" y="31" font-family="Readex Pro" font-weight="600" font-size="13" fill="#fff" text-anchor="end">{a('علامة آمنة', 'Brand-safe')}</text>
        <text x="456" y="50" font-family="IBM Plex Sans Arabic" font-size="11" fill="#fff" text-anchor="end" opacity=".9">{a('أكواد رسمية فقط', 'Official codes only')}</text>
      </g>
      <path d="M500 400l6 14 14 6-14 6-6 14-6-14-14-6 14-6z" fill="#FFC233"/>
    </svg>'''


SERVICES = [
    ("bg-coral", "#FF5A36", '<path d="M4 7h16v4a2 2 0 0 0 0 4v4H4v-4a2 2 0 0 0 0-4z"/>',
     ("منصة العروض", "Deals platform"), ("صفحة متجر احترافية لعلامتك، وظهور في الفئات والمواسم والدول.", "A professional store page for your brand, featured across categories, seasons and countries."),
     [("صفحة متجر بالعربي والإنجليزي", "Store page in Arabic and English"), ("عروض حصرية بكود خاص", "Exclusive offers with a dedicated code"), ("تحسين لمحركات البحث", "Search-engine optimised")]),
    ("bg-violet", "#6D5BFF", '<path d="M4 19V5M4 19h16M8 15l3-4 3 2 5-6"/>',
     ("محتوى وسيو", "Content & SEO"), ("محتوى عربي يجيب على أسئلة المتسوق ويقوده إلى الشراء.", "Arabic content that answers shoppers’ questions and leads them to buy."),
     [("أدلة شراء ومقارنات", "Buying guides and comparisons"), ("صفحات مواسم مبكرة", "Season pages published early"), ("حضور في إجابات الذكاء الاصطناعي", "Visibility in AI answers")]),
    ("bg-mint", "#14B8A6", '<path d="M21 4 3 11l7 2 2 7z"/>',
     ("قنوات التواصل", "Owned channels"), ("نشر عروضك عبر قنواتنا على تيليجرام وإكس والنشرة البريدية.", "Your offers shared through our Telegram, X and newsletter channels."),
     [("تنبيهات فورية للعروض", "Instant offer alerts"), ("حملات موسمية مجدولة", "Scheduled seasonal campaigns"), ("روابط وأكواد قابلة للتتبع", "Trackable links and codes")]),
    ("bg-saffron", "#E0A100", '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 19c0-3 3-5 6-5s6 2 6 5M15 19c0-2 1.5-4 4-4"/>',
     ("صنّاع المحتوى", "Creators"), ("ننسّق مع مؤثرين مناسبين لجمهورك، بأكواد خاصة لكل منهم.", "We coordinate creators who fit your audience, each with their own code."),
     [("اختيار حسب الجمهور لا المتابعين", "Chosen for audience fit, not follower count"), ("كود مستقل لقياس كل مؤثر", "A separate code to measure each creator"), ("دفع على المبيعات", "Paid on sales")]),
    ("bg-coral", "#FF5A36", '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/>',
     ("حملات المواسم", "Seasonal campaigns"), ("خطة جاهزة للجمعة البيضاء ورمضان والعيد والعودة للمدارس.", "Ready-made plans for White Friday, Ramadan, Eid and back to school."),
     [("تقويم حملات سنوي", "An annual campaign calendar"), ("صفحات هبوط موسمية", "Seasonal landing pages"), ("تنبيهات قبل الموسم", "Pre-season alerts")]),
    ("bg-violet", "#6D5BFF", '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
     ("تقارير شفافة", "Transparent reporting"), ("تقرير دوري بالنقرات والطلبات والمبيعات، ونقاط التحسين التالية.", "Regular reports on clicks, orders and sales, plus what we’ll improve next."),
     [("أرقام من شبكة التتبع نفسها", "Numbers from the tracking network itself"), ("مقارنة بين القنوات", "Channel-by-channel comparison"), ("توصيات عملية", "Practical recommendations")]),
]

MODELS = [
    ("CPS", "CPS", "عمولة على المبيعات", "Commission on sales", "تدفع نسبة من كل طلب مكتمل فقط. النموذج الأنسب لمعظم المتاجر.", "You pay a share of completed orders only. The best fit for most stores."),
    ("CPA", "CPA", "تكلفة لكل إجراء", "Cost per action", "مقابل محدد لكل تسجيل أو تحميل تطبيق أو عميل جديد.", "A fixed fee per sign-up, app install or new customer."),
    ("هجين", "Hybrid", "رسوم ظهور + عمولة", "Placement fee + commission", "ظهور مضمون في المواسم الكبرى، مع عمولة على النتائج.", "Guaranteed visibility in the big seasons, plus commission on results."),
    ("مباشر", "Direct", "أو عبر شبكتك", "Or via your network", "نعمل بعقد مباشر أو عبر شبكة التسويق بالعمولة التي تستخدمها.", "We work on a direct contract or through the affiliate network you already use."),
]

TIMELINE = [
    ("اليوم الأول", "Day one", "مكالمة تعارف", "Intro call", "نفهم منتجك وجمهورك وأهدافك وقيودك.", "We learn your product, audience, goals and constraints."),
    ("خلال 3 أيام", "Within 3 days", "خطة مكتوبة", "Written plan", "القنوات والعروض والتقويم ومؤشرات النجاح.", "Channels, offers, calendar and success metrics."),
    ("الأسبوع الأول", "Week one", "الإطلاق", "Launch", "صفحة متجرك وأكوادك وروابط التتبع جاهزة.", "Your store page, codes and tracking links go live."),
    ("كل أسبوع", "Every week", "تقرير وتحسين", "Report & optimise", "أرقام واضحة، وما سنغيّره في الأسبوع التالي.", "Clear numbers, and what we’ll change next week."),
]

RULES = [
    ("ننشر أكوادك الرسمية فقط، ولا نسرّب أي كود خاص.", "We publish your official codes only and never leak a private code."),
    ("لا نزايد على اسم علامتك في الإعلانات دون إذن مكتوب.", "No bidding on your brand name in ads without written permission."),
    ("لا عدّ تنازلي وهمي ولا ادعاءات مبالغ فيها.", "No fake countdowns and no exaggerated claims."),
    ("نتبع سياسات شبكتك وقواعد كل سوق.", "We follow your network’s policies and each market’s rules."),
    ("تقارير من مصدر التتبع نفسه، لا أرقام من عندنا.", "Reports come from the tracking source itself, not numbers we make up."),
    ("مراجعة أي محتوى عن علامتك قبل نشره عند الطلب.", "Any content about your brand can be reviewed before it goes live."),
]

PARTNER_FAQ = {
    "ar": [
        ("هل هناك تكلفة لبدء الشراكة؟", "في نموذج العمولة لا توجد رسوم ثابتة. تدفع فقط عند تحقق المبيعات."),
        ("هل تعملون عبر شبكات التسويق بالعمولة؟", "نعم، أو بعقد مباشر، حسب ما يناسبك."),
        ("ما هو برنامج الشركاء المؤسسين؟", "نختار عددًا محدودًا من العلامات التجارية لتكون أول شركائنا، مع ظهور مميز وخطة حملة مخصّصة وتقارير أسبوعية من الفريق."),
        ("هل تعرضون علامات تجارية لا تتعاملون معها؟", "لا. لا نعرض اسم أو شعار أي علامة كشريك إلا بعد اتفاق رسمي أو موافقة على برنامجها."),
    ],
    "en": [
        ("Is there a cost to start?", "On the commission model there are no fixed fees. You only pay when sales happen."),
        ("Do you work through affiliate networks?", "Yes, or on a direct contract, whichever suits you."),
        ("What is the Founding Partner Programme?", "We pick a limited number of brands to be our first partners, with premium placement, a custom campaign plan and weekly reports from the team."),
        ("Do you list brands you don’t work with?", "No. We never show a brand’s name or logo as a partner without a formal agreement or an approved programme."),
    ],
}


def partner_form(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    subj = a("طلب شراكة - كوبون", "Partnership request - Kobon")
    markets = [a("السعودية", "Saudi Arabia"), a("الإمارات", "UAE"), a("الخليج كله", "All GCC"), a("مصر", "Egypt"), a("الخليج ومصر", "GCC & Egypt")]
    models = [a("عمولة على المبيعات (CPS)", "Commission on sales (CPS)"), "CPA", a("هجين", "Hybrid"), a("لم نحدد بعد", "Not decided yet")]
    opt = lambda xs: "".join(f"<option>{esc(x)}</option>" for x in xs)
    return f'''<form class="contact-card js-mailto" data-to="{EMAIL}" data-subject="{esc(subj)}" action="mailto:{EMAIL}" method="get" enctype="text/plain" style="color:var(--ink)">
      <h3 style="font-size:1.4rem">{a('طلب شراكة', 'Partnership request')}</h3>
      <input type="hidden" name="subject" value="{esc(subj)}">
      <div class="row2"><label class="field">{a('الاسم', 'Name')}<input name="{a('الاسم', 'Name')}" required placeholder="{a('اسمك الكامل', 'Your full name')}" autocomplete="name"></label><label class="field">{a('العلامة التجارية', 'Brand')}<input name="{a('العلامة التجارية', 'Brand')}" required placeholder="{a('اسم المتجر', 'Store name')}" autocomplete="organization"></label></div>
      <div class="row2"><label class="field">{a('البريد الإلكتروني للعمل', 'Work email')}<input name="{a('البريد', 'Email')}" type="email" required placeholder="name@brand.com" dir="ltr" autocomplete="email"></label><label class="field">{a('الموقع الإلكتروني', 'Website')}<input name="{a('الموقع', 'Website')}" placeholder="brand.com" dir="ltr" autocomplete="url"></label></div>
      <div class="row2"><label class="field">{a('الأسواق المستهدفة', 'Target markets')}<select name="{a('الأسواق', 'Markets')}">{opt(markets)}</select></label><label class="field">{a('النموذج المفضّل', 'Preferred model')}<select name="{a('النموذج', 'Model')}">{opt(models)}</select></label></div>
      <label class="field">{a('ما هدفك الأساسي؟', 'What’s your main goal?')}<textarea name="{a('الهدف', 'Goal')}" rows="3" placeholder="{a('مثل: عملاء جدد في السعودية خلال موسم الجمعة البيضاء', 'e.g. new customers in Saudi Arabia during White Friday')}"></textarea></label>
      <button class="btn btn-primary" style="justify-content:center">{a('أرسل الطلب ←', 'Send request →')}</button>
      <small style="color:var(--muted)">{a('يفتح الزر بريدك الإلكتروني برسالة جاهزة إلى', 'The button opens your email app with a ready message to')} <a class="mail" href="mailto:{EMAIL}?subject={esc(subj)}">{EMAIL}</a>. {a('نستخدم بياناتك للرد على طلبك فقط.', 'We only use your details to reply to you.')}</small>
    </form>'''


def build_partners(lang: str) -> None:
    a = lambda ar, en: t(lang, ar, en)
    svcs = "".join(
        f'<article class="svc"><span class="ic {bg}" style="width:56px;height:56px;border-radius:16px;display:grid;place-items:center"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" aria-hidden="true">{ic}</svg></span><h3>{t(lang, *h)}</h3><p style="color:var(--ink-soft)">{t(lang, *p)}</p><ul>{"".join("<li>" + t(lang, *x) + "</li>" for x in lis)}</ul></article>'
        for bg, c, ic, h, p, lis in SERVICES
    )
    models = "".join(
        f'<div class="model{" feat" if i == 0 else ""}"><span class="k">{t(lang, k1, k2)}</span><h3>{t(lang, h1, h2)}</h3><p>{t(lang, p1, p2)}</p></div>' for i, (k1, k2, h1, h2, p1, p2) in enumerate(MODELS)
    )
    tl = "".join(
        f'<div class="tl"><span class="dot">{i+1}</span><small>{t(lang, s1, s2)}</small><h3>{t(lang, h1, h2)}</h3><p>{t(lang, p1, p2)}</p></div>' for i, (s1, s2, h1, h2, p1, p2) in enumerate(TIMELINE)
    )
    rules = "".join(f'<div class="rule"><span class="x">✓</span>{t(lang, r1, r2)}</div>' for r1, r2 in RULES)
    body = f'''<section class="p-hero">
  <div class="wrap">
    <div style="display:grid;gap:1.4rem;justify-items:start">
      <nav class="crumbs" aria-label="{a('مسار الصفحة', 'Breadcrumb')}" style="color:#B7BBD6"><a href="{L(lang, '/')}">{a('الرئيسية', 'Home')}</a> / <span aria-current="page">{a('للبراندات', 'For Brands')}</span></nav>
      <span class="eyebrow light">✦ {a('للبراندات والمتاجر الإلكترونية', 'For brands & online stores')}</span>
      <h1>{a('نحوّل عروضك<br>إلى <span style="color:var(--saffron)">مبيعات</span>،<br>وتدفع مقابل النتائج.', 'We turn your offers<br>into <span style="color:var(--saffron)">sales</span>,<br>and you pay for results.')}</h1>
      <p class="lead">{a('«كوبون» فريق متخصص في التسويق بالأداء والعمولة، ومنصة عروض موجّهة للمتسوقين في الخليج ومصر. نبني لعلامتك حضورًا موثوقًا ونقيس كل ريال يُنفق.', 'Kobon is a performance and affiliate marketing team and a deals platform for shoppers in the Gulf and Egypt. We build a trusted presence for your brand and measure every riyal spent.')}</p>
      <div class="actions"><a class="btn btn-primary" href="#contact">{a('احجز مكالمة تعارف ←', 'Book an intro call →')}</a><a class="btn btn-outline-light" href="#founding">{a('برنامج الشركاء المؤسسين', 'Founding Partner Programme')}</a></div>
      <div class="facts"><span><b>{a('الدفع على النتيجة', 'Pay for results')}</b>CPS · CPA · {a('هجين', 'Hybrid')}</span><span><b>{a('7 أسواق', '7 markets')}</b>{a('الخليج ومصر', 'The Gulf and Egypt')}</span><span><b>{a('بلغتين', 'Two languages')}</b>{a('عربي وإنجليزي', 'Arabic & English')}</span></div>
    </div>
    {dashboard_svg(lang)}
  </div>
</section>
<section class="wrap founding" id="founding">
  <div class="box">
    <svg class="seal" viewBox="0 0 88 88" aria-hidden="true"><circle cx="44" cy="44" r="42" fill="#FFF6DD"/><circle cx="44" cy="44" r="34" fill="none" stroke="#E0A100" stroke-width="2" stroke-dasharray="3 5"/><path d="M44 22l6 13 14 2-10 10 2 14-12-7-12 7 2-14-10-10 14-2z" fill="#FFC233" stroke="#E0A100" stroke-width="1.5"/></svg>
    <div><h2 style="font-size:1.4rem">{a('برنامج الشركاء المؤسسين', 'Founding Partner Programme')}</h2><p>{a('نختار عددًا محدودًا من العلامات التجارية لتكون أول شركائنا: ظهور مميز على الصفحة الرئيسية وصفحات المواسم، وخطة حملة مخصّصة، وتقارير أسبوعية مباشرة من الفريق.', 'A limited number of brands become our first partners, with premium placement on the home and season pages, a custom campaign plan and weekly reports straight from the team.')}</p></div>
    <a class="btn btn-primary" href="#contact">{a('قدّم علامتك', 'Apply with your brand')}</a>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {section_head(a('ماذا نقدّم', 'What we offer'), a('منظومة تسويق بالأداء متكاملة', 'A complete performance-marketing system'), a('لسنا موقع كوبونات فقط. نحن فريق ينفّذ حملتك عبر أكثر من قناة، ويحاسَب على النتائج.', 'We’re not just a coupon site. We’re a team that runs your campaign across several channels and is accountable for results.'))}
    <div class="services">{svcs}</div>
  </div>
</section>
<section class="section" id="models" style="background:#fff;border-block:1px solid var(--line)">
  <div class="wrap">
    {section_head(a('نماذج التعاون', 'Collaboration models'), a('اختر النموذج الذي يناسب أهدافك', 'Choose the model that fits your goals'), '', 'mint')}
    <div class="models">{models}</div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {section_head(a('خطوات الشراكة', 'How we start'), a('من أول مكالمة إلى أول تقرير', 'From first call to first report'))}
    <div class="timeline">{tl}</div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap split">
    <div style="display:grid;gap:1.2rem">
      <span class="eyebrow mint">{a('سلامة علامتك أولًا', 'Brand safety first')}</span>
      <h2>{a('قواعد نلتزم بها<br>مع كل شريك', 'Rules we keep<br>with every partner')}</h2>
      <p class="lead">{a('سمعة علامتك أهم من أي حملة. لذلك نعمل بقواعد واضحة ومكتوبة في كل اتفاق.', 'Your brand’s reputation matters more than any campaign, so every agreement comes with clear, written rules.')}</p>
    </div>
    <div class="rules">{rules}</div>
  </div>
</section>
<section class="section" id="contact" style="background:var(--ink);color:#fff">
  <div class="wrap split">
    <div style="display:grid;gap:1.2rem">
      <span class="eyebrow light">{a('لنبدأ', 'Let’s talk')}</span>
      <h2>{a('أخبرنا عن علامتك،<br>ونعود إليك خلال يوم عمل.', 'Tell us about your brand.<br>We reply within one business day.')}</h2>
      <p style="color:#C9CCE6;font-size:1.1rem">{a('أو راسلنا مباشرة على', 'Or email us directly at')} <a class="mail" style="color:#fff" href="mailto:{EMAIL}">{EMAIL}</a></p>
      <div class="faq" style="margin:1rem 0 0;max-width:none">{faq_html(PARTNER_FAQ[lang], True, True)}</div>
    </div>
    {partner_form(lang)}
  </div>
</section>'''
    title = a("للبراندات والمتاجر: تسويق بالعمولة والأداء في الخليج ومصر | كوبون", "For Brands: affiliate & performance marketing in the Gulf and Egypt | Kobon")
    desc = a("«كوبون» فريق تسويق بالعمولة والأداء بخبرة في الخليج ومصر. نحوّل عروضك الرسمية إلى مبيعات، وتدفع مقابل النتائج: CPS وCPA وهجين، مع قواعد صارمة لسلامة علامتك.",
             "Kobon is an affiliate and performance marketing team with experience across the Gulf and Egypt. We turn your official offers into sales, and you pay for results: CPS, CPA or hybrid, with strict brand-safety rules.")
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("للبراندات", "For Brands"), "/partners/")]
    ld = [faq_ld(PARTNER_FAQ[lang]), {"@context": "https://schema.org", "@type": "Service", "name": a("التسويق بالعمولة والأداء للعلامات التجارية", "Affiliate & performance marketing for brands"),
          "provider": {"@type": "Organization", "name": NAME[lang], "url": DOMAIN + "/"}, "areaServed": ["SA", "AE", "KW", "QA", "BH", "OM", "EG"], "serviceType": "Affiliate marketing"}]
    render(lang, "/partners/", title, desc, body, "partners", ld, crumbs, cta=(a("احجز مكالمة", "Book a call"), "#contact"), flush_footer=True, announce=False)


def team_svg(lang: str) -> str:
    return f'''<svg class="art" viewBox="0 0 420 320" role="img" aria-label="{t(lang, 'رسم توضيحي: طاولة عمل الفريق بحواسيب ورسم بياني وكوبون', 'Illustration: the team’s desk with laptops, a chart and a coupon')}">
  <defs><filter id="s3" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#0E1330" flood-opacity=".18"/></filter></defs>
  <circle cx="210" cy="160" r="150" fill="#FFF0EB"/>
  <rect x="40" y="220" width="340" height="18" rx="9" fill="#0E1330"/>
  <g filter="url(#s3)"><rect x="70" y="110" width="150" height="100" rx="12" fill="#0E1330"/><rect x="80" y="120" width="130" height="80" rx="6" fill="#fff"/>
  <path d="M90 185 C110 180 120 160 140 162 S175 140 200 132" fill="none" stroke="#FF5A36" stroke-width="4" stroke-linecap="round"/><rect x="90" y="130" width="50" height="8" rx="4" fill="#0E1330" opacity=".2"/></g>
  <rect x="55" y="208" width="180" height="12" rx="6" fill="#2C2F73"/>
  <g filter="url(#s3)"><rect x="240" y="96" width="120" height="114" rx="12" fill="#6D5BFF"/><rect x="254" y="112" width="70" height="10" rx="5" fill="#fff" opacity=".85"/><rect x="254" y="132" width="92" height="8" rx="4" fill="#fff" opacity=".4"/><rect x="254" y="148" width="80" height="8" rx="4" fill="#fff" opacity=".4"/>
  <rect x="254" y="170" width="40" height="26" rx="6" fill="#FFC233"/><rect x="300" y="160" width="40" height="36" rx="6" fill="#14B8A6"/></g>
  <g filter="url(#s3)" transform="rotate(8 330 60)"><path d="M280 40h90a8 8 0 0 1 8 8v10a10 10 0 0 0 0 20v10a8 8 0 0 1-8 8h-90a8 8 0 0 1-8-8V78a10 10 0 0 0 0-20V48a8 8 0 0 1 8-8z" fill="#FF5A36"/><text x="325" y="76" font-family="Readex Pro" font-weight="700" font-size="22" fill="#fff" text-anchor="middle">%</text></g>
  <g filter="url(#s3)"><circle cx="90" cy="70" r="30" fill="#14B8A6"/><path d="m77 70 9 9 17-17" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/></g>
  <path d="M190 40l5 12 12 5-12 5-5 12-5-12-12-5 12-5z" fill="#FFC233"/>
</svg>'''


def build_about(lang: str) -> None:
    a = lambda ar, en: t(lang, ar, en)
    principles = [
        ("bg-coral", "#FF5A36", ("الرسمي فقط", "Official only"), ("لا ننشر عرضًا إلا من المتجر نفسه أو من برنامج شراكة معتمد.", "We only publish offers from the store itself or an approved partner programme.")),
        ("bg-mint", "#14B8A6", ("الشفافية في العمولة", "Transparent about commission"), ("نقول بوضوح متى قد نحصل على عمولة، ولا يغيّر ذلك سعرك.", "We say clearly when we may earn a commission. It never changes your price.")),
        ("bg-saffron", "#E0A100", ("احترام وقتك", "Respect your time"), ("عروض أقل، لكن كل عرض مشروح بشروطه وتاريخ مراجعته.", "Fewer offers, each one explained with its terms and last-checked date.")),
        ("bg-violet", "#6D5BFF", ("سلامة العلامة التجارية", "Brand safety"), ("لا مزايدة على أسماء العلامات، ولا أكواد مسرّبة، ولا ادعاءات مبالغ فيها.", "No brand-name bidding, no leaked codes and no exaggerated claims.")),
    ]
    pr = "".join(f'<article class="card"><span class="ic {bg}">{CHECK.format(s=30, c=c)}</span><h3>{t(lang, *h)}</h3><p>{t(lang, *p)}</p></article>' for bg, c, h, p in principles)
    skills = [
        ("التسويق بالعمولة", "Affiliate marketing", "إدارة برامج العمولة مع المتاجر والشبكات، وروابط وأكواد قابلة للتتبع.", "Running commission programmes with stores and networks, with trackable links and codes."),
        ("السيو والمحتوى العربي", "SEO & Arabic content", "صفحات وأدلة شراء تجيب على أسئلة المتسوق في الخليج ومصر.", "Pages and buying guides that answer shoppers’ questions in the Gulf and Egypt."),
        ("إدارة القنوات", "Channels", "تيليجرام وإكس والنشرة البريدية، بجدول نشر واضح.", "Telegram, X and the newsletter, on a clear publishing schedule."),
        ("تحليل الأداء", "Analytics", "قياس النقرات والطلبات والمبيعات من مصدر التتبع نفسه.", "Measuring clicks, orders and sales from the tracking source itself."),
        ("إدارة حملات المواسم", "Seasonal campaigns", "خطط مبكرة للجمعة البيضاء ورمضان والعيد والأيام الوطنية.", "Early plans for White Friday, Ramadan, Eid and national days."),
        ("علاقات الشركاء", "Partner relations", "تواصل مباشر وتقارير أسبوعية لكل علامة نعمل معها.", "Direct contact and weekly reports for every brand we work with."),
    ]
    sk = "".join(f'<div class="vitem"><span class="n">{i+1}</span><div><h3>{t(lang, h1, h2)}</h3><p>{t(lang, p1, p2)}</p></div></div>' for i, (h1, h2, p1, p2) in enumerate(skills))
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("من نحن", "About"), "/about/")]
    body = page_hero(lang, crumbs, a("من نحن", "About us"),
                     a("نحن فريق من المسوّقين، بنينا «كوبون» لأننا تعبنا من <span class=\"hl\">الأكواد الوهمية</span>.", "We’re a team of marketers. We built Kobon because we were tired of <span class=\"hl\">fake codes</span>."),
                     a("فريق تسويق بالعمولة بخبرة في الخليج ومصر.", "An affiliate marketing team with experience across the Gulf and Egypt."), team_svg(lang)) + f'''
<section class="section">
  <div class="wrap split">
    <div style="display:grid;gap:1.2rem"><span class="eyebrow mint">{a('قصتنا', 'Our story')}</span><h2>{a('رأينا المشكلة من الجهتين', 'We saw the problem from both sides')}</h2></div>
    <div class="prose" style="margin:0">
      <p>{a('نحن فريق تسويق بالعمولة بخبرة في الخليج ومصر. عملنا في التسويق بالأداء مع متاجر إلكترونية، ورأينا المشكلة من الجهتين: متسوّق يضيع وقته في أكواد لا تعمل، وعلامات تجارية تخسر ثقة عملائها بسبب مواقع تنشر أي شيء.', 'We’re an affiliate marketing team with experience across the Gulf and Egypt. Working in performance marketing with online stores, we saw the problem from both sides: shoppers wasting time on codes that don’t work, and brands losing customer trust to sites that publish anything.')}</p>
      <p>{a('«كوبون» هو الحل الذي أردناه: منصة عروض بمعيار واضح، يديرها فريق يعرف كيف تُبنى الحملات وتُقاس.', 'Kobon is the answer we wanted: a deals platform with a clear standard, run by a team that knows how campaigns are built and measured.')}</p>
    </div>
  </div>
</section>
<section class="section" style="background:#fff;border-block:1px solid var(--line)">
  <div class="wrap">
    {section_head(a('مبادئنا', 'Our principles'), a('أربعة مبادئ لا نتنازل عنها', 'Four principles we don’t compromise on'))}
    <div class="grid-4">{pr}</div>
  </div>
</section>
<section class="section">
  <div class="wrap verify">
    <div style="display:grid;gap:1.2rem"><span class="eyebrow">{a('كيف نعمل', 'How we work')}</span><h2>{a('مهارات الفريق', 'What the team does')}</h2><p class="lead">{a('كل عرض وكل حملة تمرّ على أشخاص يعرفون التسويق بالأداء من الداخل.', 'Every offer and every campaign goes through people who know performance marketing from the inside.')}</p></div>
    <div class="vlist">{sk}</div>
  </div>
</section>
<section class="wrap two">
  <div class="path-card dark"><span class="eyebrow light">{a('للبراندات', 'For brands')}</span><h2 style="font-size:1.7rem">{a('لنعمل معًا', 'Let’s work together')}</h2><p>{a('عمولة على المبيعات، وقواعد واضحة لسلامة علامتك، وتقارير أسبوعية.', 'Commission on sales, clear brand-safety rules and weekly reports.')}</p><div class="actions"><a class="btn btn-primary" href="{L(lang, '/partners/')}">{a('اكتشف الشراكة ←', 'Explore partnerships →')}</a></div></div>
  <div class="path-card"><span class="eyebrow mint">{a('للمتسوقين', 'For shoppers')}</span><h2 style="font-size:1.7rem">{a('اشترك في التنبيهات', 'Get offer alerts')}</h2><p>{a('رسالة واحدة أسبوعيًا بأهم العروض الرسمية فور صدورها.', 'One weekly email with the best official offers as soon as they’re out.')}</p><div class="actions"><a class="btn btn-ghost" href="{L(lang, '/#alerts')}">{a('اشترك', 'Subscribe')}</a></div></div>
</section>'''
    render(lang, "/about/", a("من نحن: فريق تسويق بالعمولة بخبرة في الخليج ومصر | كوبون", "About us: an affiliate marketing team for the Gulf and Egypt | Kobon"),
           a("تعرّف على فريق «كوبون»: فريق تسويق بالعمولة بخبرة في الخليج ومصر، ومبادئنا: الرسمي فقط، والشفافية في العمولة، واحترام وقتك، وسلامة العلامة التجارية.",
             "Meet the Kobon team: an affiliate marketing team with experience across the Gulf and Egypt, and our principles: official only, transparent commission, respect for your time and brand safety."),
           body, "about", [{"@context": "https://schema.org", "@type": "AboutPage", "name": a("من نحن", "About us"), "url": abs_url(lang, "/about/")}], crumbs)


def offer_card_svg(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    return f'''<div style="display:grid;gap:1.2rem">
  <div class="ticket">
    <div class="main">
      <div style="display:flex;gap:.5rem;flex-wrap:wrap"><span class="badge ok">✓ {a('مصدر رسمي', 'Official source')}</span><span class="badge warn">{a('متبقٍ 5 أيام', '5 days left')}</span></div>
      <h3>{a('خصم 20% على الطلب الأول', '20% off your first order')}</h3>
      <p style="color:var(--ink-soft);font-size:.92rem">{a('اسم المتجر · أزياء · السعودية والإمارات', 'Store name · Fashion · Saudi Arabia & UAE')}</p>
      <div class="meta"><span>{a('الحد الأدنى', 'Min. spend')}<b>{a('150 ر.س', 'SAR 150')}</b></span><span>{a('أقصى خصم', 'Max. discount')}<b>{a('100 ر.س', 'SAR 100')}</b></span><span>{a('آخر مراجعة', 'Last checked')}<b>{a('اليوم', 'Today')}</b></span></div>
    </div>
    <div class="side"><div><b>20%</b><div style="font-size:.9rem;margin-top:.4rem">{a('اكشف الكود', 'Reveal code')}</div></div></div>
  </div>
  <p class="note" style="text-align:center"><span class="tag-ex">{a('مثال توضيحي', 'Illustrative example')}</span> {a('وليس عرضًا حقيقيًا', 'Not a real offer')}</p>
  <ol class="anno">
    <li><span class="n">1</span><span>{a('<b>مصدر رسمي</b>: العرض صادر عن المتجر أو برنامج شراكة معتمد.', '<b>Official source</b>: the offer comes from the store or an approved programme.')}</span></li>
    <li><span class="n">2</span><span>{a('<b>المدة المتبقية</b>: تاريخ الانتهاء كما أعلنه المتجر.', '<b>Time left</b>: the expiry date the store announced.')}</span></li>
    <li><span class="n">3</span><span>{a('<b>الشروط</b>: الحد الأدنى وأقصى خصم والدول.', '<b>Terms</b>: minimum spend, maximum discount and countries.')}</span></li>
    <li><span class="n">4</span><span>{a('<b>آخر مراجعة</b>: متى تحقق الفريق من العرض آخر مرة.', '<b>Last checked</b>: when the team last verified the offer.')}</span></li>
  </ol>
</div>'''


def build_how(lang: str) -> None:
    a = lambda ar, en: t(lang, ar, en)
    examples = [
        ("مثال: كود من صفحة العروض الرسمية للمتجر، أو من لوحة شبكة التسويق بالعمولة التي يستخدمها.", "Example: a code from the store’s official offers page, or from the dashboard of its affiliate network."),
        ("مثال: «الحد الأدنى 150 ر.س، أقصى خصم 100 ر.س، لا يشمل الإلكترونيات».", "Example: “Minimum SAR 150, maximum discount SAR 100, electronics excluded.”"),
        ("مثال: نضيف منتجًا للسلة ونتأكد أن الخصم يظهر قبل الدفع.", "Example: we add a product to the basket and check the discount appears before payment."),
        ("مثال: إذا أوقف المتجر العرض نحذفه، ونحدّث تاريخ المراجعة في كل مرة.", "Example: if the store ends the offer we remove it, and we update the check date every time."),
    ]
    std = "".join(
        f'<div class="vitem"><span class="n">{i+1}</span><div><h3>{t(lang, s[0], s[1])}</h3><p>{t(lang, s[2], s[3])}</p><p class="note" style="margin-top:.3rem">{t(lang, *examples[i])}</p></div></div>' for i, s in enumerate(STANDARD)
    )
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("كيف نعمل", "How it works"), "/how-it-works/")]
    body = page_hero(lang, crumbs, a("كيف نعمل", "How it works"), a("كيف يعمل «كوبون»،<br>ولماذا تثق <span class=\"hl\">بكل عرض</span>.", "How Kobon works,<br>and why you can trust <span class=\"hl\">every offer</span>."),
                     a("ثلاث خطوات للمتسوق، وأربع مراحل يمرّ بها كل عرض قبل نشره. هذا هو معيارنا، ونطبّقه على كل متجر.", "Three steps for shoppers, and four checks every offer passes before it’s published. This is our standard, and we apply it to every store.")) + f'''
<section class="section">
  <div class="wrap">
    {section_head(a('رحلة المتسوق', 'The shopper journey'), a('3 خطوات بلا تعقيد', 'Three simple steps'))}
    {steps_html(lang)}
  </div>
</section>
<section class="section" id="standard" style="background:#fff;border-block:1px solid var(--line)">
  <div class="wrap verify">
    <div style="display:grid;gap:1.2rem"><span class="eyebrow mint">{a('معيار كوبون', 'The Kobon standard')}</span><h2>{a('4 مراحل يمرّ بها<br>كل عرض قبل نشره', 'Every offer passes<br>4 checks before it’s published')}</h2><p class="lead">{a('إذا لم يجتز العرض المراحل الأربع، لا يُنشر.', 'If an offer doesn’t pass all four, it isn’t published.')}</p></div>
    <div class="vlist">{std}</div>
  </div>
</section>
<section class="section">
  <div class="wrap verify">
    <div style="display:grid;gap:1.2rem"><span class="eyebrow">{a('اقرأ البطاقة', 'Read the card')}</span><h2>{a('كيف تقرأ بطاقة العرض', 'How to read an offer card')}</h2><p class="lead">{a('كل ما تحتاجه لتقرر في بطاقة واحدة: المصدر والشروط والمدة وتاريخ آخر مراجعة.', 'Everything you need to decide is on one card: the source, terms, time left and last-checked date.')}</p></div>
    {offer_card_svg(lang)}
  </div>
</section>
<section class="section" id="commission" style="padding-top:0">
  <div class="wrap two">
    <div class="path-card"><span class="eyebrow mint">{a('كيف نربح', 'How we earn money')}</span><h2 style="font-size:1.6rem">{a('الإفصاح عن العمولة', 'Commission disclosure')}</h2><p>{a('عندما تشتري عبر روابطنا قد يدفع لنا المتجر عمولة. لا يغيّر ذلك سعرك، ولا يؤثر على ترتيب العروض إلا في الأماكن المعلَّمة بكلمة «مُموَّل».', 'When you buy through our links the store may pay us a commission. It never changes your price, and it never affects ranking except in spots labelled “Sponsored”.')}</p><div class="actions"><a class="link" href="{L(lang, '/affiliate-disclosure/')}">{a('صفحة الإفصاح الكاملة ←', 'Full disclosure →')}</a></div></div>
    <div class="path-card dark"><span class="eyebrow light">{a('الكود لا يعمل؟', 'Code not working?')}</span><h2 style="font-size:1.6rem">{a('أبلغنا عن كود لا يعمل', 'Report a broken code')}</h2><p>{a('أرسل لنا اسم المتجر والكود، ونراجعه في يوم العمل نفسه.', 'Send us the store name and the code, and we’ll review it the same business day.')}</p><div class="actions"><a class="btn btn-primary" href="mailto:{EMAIL}?subject={esc(a('كود لا يعمل', 'Broken code'))}">{a('أبلغنا', 'Report it')}</a></div></div>
  </div>
</section>'''
    faq = [(a("هل تضمنون أن كل كود يعمل؟", "Do you guarantee every code works?"), a("لا يمكن لأحد أن يضمن ذلك، لأن الشروط تختلف حسب السلة والدولة والحساب. لكننا ننشر الشروط كاملة ونحدّث تاريخ المراجعة.", "No one can, because terms vary by basket, country and account. But we publish the full terms and keep the check date up to date."))]
    render(lang, "/how-it-works/", a("كيف نعمل ومعيار التحقق من العروض | كوبون", "How it works & our verification standard | Kobon"),
           a("كيف يعمل «كوبون»: ثلاث خطوات للمتسوق، وأربع مراحل تحقق لكل عرض (المصدر، الشروط، التجربة، المتابعة)، وكيف نربح بشفافية.",
             "How Kobon works: three steps for shoppers, four verification checks for every offer (source, terms, test, monitor), and how we earn money transparently."),
           body, "how", [faq_ld(faq)], crumbs)


def build_contact(lang: str) -> None:
    a = lambda ar, en: t(lang, ar, en)
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("تواصل معنا", "Contact"), "/contact/")]
    env = '''<svg class="art" viewBox="0 0 360 280" role="img" aria-label="ENV"><defs><filter id="s4" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#0E1330" flood-opacity=".2"/></filter></defs>
<circle cx="180" cy="140" r="130" fill="#EFEDFF"/>
<g filter="url(#s4)"><rect x="60" y="80" width="240" height="160" rx="18" fill="#fff"/><path d="M60 98l120 80 120-80" fill="none" stroke="#6D5BFF" stroke-width="6" stroke-linejoin="round"/></g>
<g filter="url(#s4)" transform="rotate(-10 120 70)"><path d="M70 40h100a8 8 0 0 1 8 8v12a10 10 0 0 0 0 20v12a8 8 0 0 1-8 8H70a8 8 0 0 1-8-8V80a10 10 0 0 0 0-20V48a8 8 0 0 1 8-8z" fill="#FF5A36"/><text x="120" y="80" font-family="Readex Pro" font-weight="700" font-size="24" fill="#fff" text-anchor="middle">%</text></g>
<g filter="url(#s4)"><circle cx="290" cy="80" r="26" fill="#14B8A6"/><path d="m279 80 8 8 14-14" stroke="#fff" stroke-width="4.5" fill="none" stroke-linecap="round"/></g></svg>'''.replace('aria-label="ENV"', f'aria-label="{a("رسم توضيحي: ظرف بريد وكوبون", "Illustration: an envelope and a coupon")}"')
    body = page_hero(lang, crumbs, a("تواصل معنا", "Contact"), a("كيف نساعدك؟", "How can we help?"),
                     a("طريقان واضحان حتى لا يضيع طلبك: واحد للمتسوقين وواحد للبراندات والوكالات. نرد خلال يوم عمل.", "Two clear paths so nothing gets lost: one for shoppers and one for brands and agencies. We reply within one business day."), env) + f'''
<section class="section">
  <div class="wrap two">
    <div class="path-card"><span class="eyebrow mint">{a('للمتسوقين', 'For shoppers')}</span><h2 style="font-size:1.7rem">{a('سؤال عن عرض أو كود لا يعمل؟', 'A question about an offer, or a code that didn’t work?')}</h2><p>{a('أرسل لنا اسم المتجر والكود والدولة، وسنراجعه في يوم العمل نفسه.', 'Send us the store name, the code and your country, and we’ll review it the same business day.')}</p><div class="actions"><a class="btn btn-primary" href="mailto:{EMAIL}?subject={esc(a('سؤال متسوق', 'Shopper question'))}">{a('راسلنا', 'Email us')}</a></div><p class="note">{a('البريد:', 'Email:')} <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></p></div>
    <div class="path-card dark"><span class="eyebrow light">{a('للبراندات والوكالات', 'For brands & agencies')}</span><h2 style="font-size:1.7rem">{a('شراكة أو حملة؟', 'A partnership or a campaign?')}</h2><p>{a('أخبرنا عن علامتك وأسواقك وهدفك، ونعود إليك خلال يوم عمل بخطوات واضحة.', 'Tell us about your brand, markets and goal, and we’ll come back within one business day with clear next steps.')}</p><div class="actions"><a class="btn btn-primary" href="{L(lang, '/partners/#contact')}">{a('طلب شراكة ←', 'Partnership request →')}</a><a class="btn btn-outline-light mail" href="mailto:{EMAIL}">{EMAIL}</a></div></div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap facts-grid">
    <div class="fact"><small>{a('وقت الرد', 'Response time')}</small><b>{a('خلال يوم عمل', 'Within one business day')}</b></div>
    <div class="fact"><small>{a('اللغات', 'Languages')}</small><b>{a('العربية والإنجليزية', 'Arabic & English')}</b></div>
    <div class="fact"><small>{a('الأسواق', 'Markets')}</small><b>{a('الخليج ومصر', 'The Gulf and Egypt')}</b></div>
  </div>
</section>'''
    ld = [{"@context": "https://schema.org", "@type": "ContactPage", "name": a("تواصل معنا", "Contact"), "url": abs_url(lang, "/contact/")}]
    render(lang, "/contact/", a("تواصل معنا | كوبون", "Contact us | Kobon"),
           a("تواصل مع «كوبون»: للمتسوقين بخصوص عرض أو كود، وللبراندات والوكالات بخصوص الشراكات والحملات. نرد خلال يوم عمل على partners@kobon.is-a.si.",
             "Contact Kobon: shoppers with a question about an offer or code, and brands or agencies about partnerships and campaigns. We reply within one business day at partners@kobon.is-a.si."),
           body, "", ld, crumbs)


LEGAL = {
    "privacy": {
        "ar": ("الخصوصية وملفات تعريف الارتباط", "سياسة الخصوصية وملفات تعريف الارتباط في «كوبون».", """
<p>الموقع صفحات ثابتة. لا نطلب إنشاء حساب للتصفح، ولا نبيع بياناتك.</p>
<h2>ملفات تعريف الارتباط</h2>
<p>لا نضع حاليًا ملفات تعريف ارتباط للتتبع أو للإعلانات من أطراف ثالثة. إذا أضفنا لاحقًا أداة قياس، فسنوضح نوعها والغرض منها هنا قبل تفعيلها.</p>
<h2>النماذج والبريد</h2>
<p>نموذج الشراكة ونموذج التنبيهات لا يرسلان بياناتك إلى خادم. يفتحان تطبيق البريد لديك برسالة جاهزة، وأنت من يقرر إرسالها. نستخدم ما تصلنا به من بيانات للرد عليك فقط.</p>
<h2>روابط المتاجر</h2>
<p>قد تكون بعض الروابط روابط عمولة. عند الضغط عليها تنتقل إلى متجر خارجي له سياسة خصوصية خاصة به. راجع <a href="/affiliate-disclosure/">الإفصاح عن العمولة</a> و<a href="/terms/">الشروط</a>.</p>
<h2>التواصل</h2>
<p>للاستفسارات: <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></p>"""),
        "en": ("Privacy & cookies", "Kobon’s privacy and cookies policy.", """
<p>This is a static website. You don’t need an account to browse, and we don’t sell your data.</p>
<h2>Cookies</h2>
<p>We don’t currently set any tracking or third-party advertising cookies. If we add a measurement tool later, we’ll explain its type and purpose here before turning it on.</p>
<h2>Forms and email</h2>
<p>The partnership and alerts forms don’t send your data to a server. They open your email app with a ready message, and you decide whether to send it. We only use what you send us to reply to you.</p>
<h2>Store links</h2>
<p>Some links may be affiliate links. Clicking them takes you to an external store with its own privacy policy. See the <a href="/en/affiliate-disclosure/">affiliate disclosure</a> and <a href="/en/terms/">terms</a>.</p>
<h2>Contact</h2>
<p>Questions: <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></p>"""),
    },
    "terms": {
        "ar": ("الشروط", "شروط استخدام موقع «كوبون».", """
<p>باستخدامك موقع «كوبون» فأنت توافق على هذه الشروط. يقدّم الموقع معلومات عن العروض وأكواد الخصم بشكل مستقل، ولا يبيع المنتجات مباشرة.</p>
<h2>صلاحية العروض</h2>
<p>نراجع العروض وفق <a href="/how-it-works/#standard">معيار كوبون</a> ونحدّث تواريخ المراجعة، لكن لا يمكن ضمان أن يعمل كل كود لكل مستخدم في كل وقت. تختلف الشروط حسب السلة والدولة والحساب. قرار الشراء مسؤوليتك.</p>
<h2>العمولة</h2>
<p>قد تكون بعض الروابط روابط عمولة، وقد نحصل على عمولة دون أي تكلفة إضافية عليك. التفاصيل في <a href="/affiliate-disclosure/">الإفصاح عن العمولة</a>.</p>
<h2>العلامات التجارية</h2>
<p>أسماء المتاجر والعلامات ملك لأصحابها. لا نعرض أي علامة كشريك إلا بعد اتفاق رسمي أو موافقة على برنامجها.</p>
<h2>إخلاء المسؤولية</h2>
<p>يُقدَّم الموقع «كما هو». لا نتحمّل مسؤولية سياسات المتاجر الخارجية أو انتهاء عروضها.</p>
<h2>التواصل</h2>
<p><a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></p>"""),
        "en": ("Terms", "Terms of use for Kobon.", """
<p>By using Kobon you agree to these terms. The site provides independent information about offers and discount codes and doesn’t sell products directly.</p>
<h2>Offer validity</h2>
<p>We review offers under <a href="/en/how-it-works/#standard">the Kobon standard</a> and keep check dates current, but no one can guarantee every code works for every shopper at all times. Terms vary by basket, country and account. Buying is your decision.</p>
<h2>Commission</h2>
<p>Some links may be affiliate links, and we may earn a commission at no extra cost to you. See the <a href="/en/affiliate-disclosure/">affiliate disclosure</a>.</p>
<h2>Trademarks</h2>
<p>Store and brand names belong to their owners. We never show a brand as a partner without a formal agreement or an approved programme.</p>
<h2>Disclaimer</h2>
<p>The site is provided “as is”. We aren’t responsible for third-party store policies or offers that end.</p>
<h2>Contact</h2>
<p><a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></p>"""),
    },
    "affiliate-disclosure": {
        "ar": ("الإفصاح عن العمولة", "كيف يربح «كوبون»: الإفصاح عن روابط التسويق بالعمولة.", """
<p>عندما تشتري عبر روابطنا قد يدفع لنا المتجر عمولة. لا يغيّر ذلك سعرك، ولا يؤثر على ترتيب العروض إلا في الأماكن المعلَّمة بكلمة «مُموَّل».</p>
<p>هذه العمولة هي ما يغطي تشغيل الموقع وعمل الفريق. اختيار المتجر وقرار الشراء لك وحدك.</p>
<p>لا نبالغ في وصف الخصومات، ولا نعرض أرقام توفير أو إحصاءات وهمية.</p>
<p>راجع أيضًا <a href="/terms/">الشروط</a> و<a href="/privacy/">الخصوصية</a>.</p>"""),
        "en": ("Affiliate disclosure", "How Kobon earns money: our affiliate link disclosure.", """
<p>When you buy through our links the store may pay us a commission. It never changes your price, and it never affects ranking except in spots labelled “Sponsored”.</p>
<p>That commission pays for running the site and the team’s work. Choosing a store and deciding to buy is entirely up to you.</p>
<p>We don’t exaggerate discounts, and we never show made-up savings figures or statistics.</p>
<p>See also our <a href="/en/terms/">terms</a> and <a href="/en/privacy/">privacy</a> pages.</p>"""),
    },
}


def build_legal(lang: str, slug: str) -> None:
    h1, desc, inner = LEGAL[slug][lang]
    inner = inner.replace("{EMAIL}", EMAIL)
    crumbs = [(t(lang, "الرئيسية", "Home"), "/"), (h1, f"/{slug}/")]
    body = page_hero(lang, crumbs, t(lang, "قانوني", "Legal"), esc(h1), esc(desc)) + f'<section class="section"><div class="wrap"><article class="prose">{inner}<p class="note">{t(lang, "آخر تحديث:", "Last updated:")} {day_label(lang, TODAY)}</p></article></div></section>'
    render(lang, f"/{slug}/", f"{h1} | {NAME[lang]}", desc, body, "", None, crumbs)


def brand_cta_actions(lang: str) -> str:
    return f'<a class="btn btn-primary" href="{L(lang, "/#alerts")}">{t(lang, "اشترك في التنبيهات", "Get offer alerts")}</a><a class="btn btn-ghost" href="{L(lang, "/partners/")}">{t(lang, "أنت علامة تجارية؟", "Are you a brand?")}</a>'


def store_card(lang: str, s: dict, cats_by: dict) -> str:
    c = cats_by.get(s["category"], {})
    hay = " ".join([s["name_ar"], s["name_en"], c.get("name_ar", ""), c.get("name_en", "")]).lower()
    return f'<a class="card" data-search="{esc(hay)}" href="{L(lang, "/stores/" + s["slug"] + "/")}">{cat_icon(s["category"])}<h3>{esc(s["name_" + lang])}</h3><p>{esc(s["description_" + lang])}</p></a>'


def build_stores(lang: str, stores: list[dict], cats: list[dict]) -> None:
    a = lambda ar, en: t(lang, ar, en)
    cats_by = {c["slug"]: c for c in cats}
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("المتاجر", "Stores"), "/stores/")]
    cards = "".join(store_card(lang, s, cats_by) for s in stores)
    cat_cards = "".join(
        f'<a class="cat" data-search="{esc((c["name_ar"] + " " + c["name_en"] + " " + c["short_ar"] + " " + c["short_en"]).lower())}" href="{L(lang, "/categories/" + c["slug"] + "/")}">{cat_icon(c["slug"])}{esc(c["name_" + lang])}<small>{esc(c["short_" + lang])}</small></a>' for c in cats
    )
    empty = "" if stores else empty_block(lang, a("أولى المتاجر الرسمية قريبًا", "Our first official stores are coming soon"),
        a("لا نعرض أي متجر إلا بعد اعتماد برنامج شراكة رسمي معه، حتى تكون كل العروض هنا من مصدرها. اشترك ليصلك أول عرض فور نشره.", "We only list a store once an official partner programme with it is approved, so every offer here comes from its source. Subscribe to hear about the first offer as soon as it’s live."),
        brand_cta_actions(lang))
    search = f'''<form class="search" role="search" onsubmit="return false" style="margin-top:.4rem"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7A7F9A" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="site-q" name="q" aria-label="{a('ابحث عن متجر أو فئة', 'Search a store or category')}" placeholder="{a('ابحث عن متجر أو فئة…', 'Search a store or category…')}"></form>'''
    body = page_hero(lang, crumbs, a("المتاجر", "Stores"), a("متاجر بعروض <span class=\"hl\">رسمية فقط</span>", "Stores with <span class=\"hl\">official offers only</span>"),
                     a("كل متجر هنا له برنامج شراكة رسمي معتمد، وكل عرض فيه مصدره وشروطه وتاريخ آخر مراجعة.", "Every store here has an approved official partner programme, and every offer shows its source, terms and last-checked date."), "", extra=search) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:2.5rem">
  <p id="search-empty" class="note" hidden data-msg="{a('لا توجد نتائج مطابقة بعد. جرّب فئة أخرى.', 'No matches yet. Try another category.')}"></p>
  {('<div class="store-grid" id="store-grid">' + cards + '</div>') if stores else empty}
  <div style="display:grid;gap:1.2rem"><h2 style="font-size:1.6rem">{a('تصفّح حسب الفئة', 'Browse by category')}</h2><div class="cats" id="cat-grid">{cat_cards}</div></div>
</div></section>'''
    render(lang, "/stores/", a("المتاجر: عروض رسمية فقط | كوبون", "Stores: official offers only | Kobon"),
           a("متاجر الخليج ومصر على «كوبون»: نعرض المتجر فقط بعد اعتماد برنامج شراكة رسمي، مع مصدر وشروط كل عرض.", "Gulf and Egypt stores on Kobon: we only list a store after an official partner programme is approved, with the source and terms of every offer."),
           body, "stores", None, crumbs)
    for s in stores:
        build_store(lang, s, cats_by)


def build_store(lang: str, s: dict, cats_by: dict) -> None:
    a = lambda ar, en: t(lang, ar, en)
    c = cats_by.get(s["category"], {})
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("المتاجر", "Stores"), "/stores/"), (s["name_" + lang], f"/stores/{s['slug']}/")]
    offers = []
    for o in s.get("coupons", []):
        offers.append(f'''<div class="ticket"><div class="main"><div><span class="badge ok">✓ {a('مصدر رسمي', 'Official source')}</span></div><h3>{esc(o['title_' + lang])}</h3>
<div class="meta"><span>{a('الحد الأدنى', 'Min. spend')}<b>{esc(o.get('min_' + lang, '—'))}</b></span><span>{a('أقصى خصم', 'Max. discount')}<b>{esc(o.get('max_' + lang, '—'))}</b></span><span>{a('آخر مراجعة', 'Last checked')}<b>{esc(o.get('verified_date', ''))}</b></span></div></div>
<div class="side"><div><b>{esc(o.get('discount', '%'))}</b><button class="btn btn-light" data-copy data-code="{esc(o['code'])}" data-done="{a('تم النسخ', 'Copied')}">{esc(o['code'])}</button></div></div></div>''')
    body = page_hero(lang, crumbs, esc(c.get("name_" + lang, "")), esc(s["name_" + lang]), esc(s["description_" + lang]), cat_icon(s["category"], 160)) + \
        f'<section class="section"><div class="wrap" style="display:grid;gap:1.5rem">{"".join(offers) or empty_block(lang, a("لا توجد عروض نشطة الآن", "No active offers right now"), a("نضيف العروض الرسمية فور صدورها.", "We add official offers as soon as they’re released."), brand_cta_actions(lang))}</div></section>'
    render(lang, f"/stores/{s['slug']}/", f"{s['name_' + lang]} | {NAME[lang]}", s["description_" + lang], body, "stores", None, crumbs)


def build_categories(lang: str, cats: list[dict], stores: list[dict]) -> None:
    a = lambda ar, en: t(lang, ar, en)
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("الفئات", "Categories"), "/categories/")]
    body = page_hero(lang, crumbs, a("الفئات", "Categories"), a("تسوّق حسب اهتمامك", "Shop by interest"),
                     a("ست فئات تغطي أهم ما يشتريه المتسوق في الخليج ومصر. في كل فئة نعرض العروض الرسمية فقط.", "Six categories covering what shoppers in the Gulf and Egypt buy most. In each one we show official offers only.")) + \
        f'<section class="section"><div class="wrap">{cats_html(lang, cats)}</div></section>'
    render(lang, "/categories/", a("فئات العروض | كوبون", "Offer categories | Kobon"),
           a("تصفّح عروض «كوبون» الرسمية حسب الفئة: أزياء، جمال وعناية، إلكترونيات، سفر، المنزل، البقالة والطعام.", "Browse Kobon’s official offers by category: fashion, beauty, electronics, travel, home, and groceries & food."),
           body, "categories", None, crumbs)
    for c in cats:
        cs = [s for s in stores if s["category"] == c["slug"]]
        cr = crumbs + [(c["name_" + lang], f"/categories/{c['slug']}/")]
        others = "".join(f'<a href="{L(lang, "/categories/" + o["slug"] + "/")}">{esc(o["name_" + lang])}</a>' for o in cats if o["slug"] != c["slug"])
        tips = "".join(f"<li>{esc(x)}</li>" for x in c["tips_" + lang])
        content = ('<div class="store-grid">' + "".join(store_card(lang, s, {c["slug"]: c}) for s in cs) + "</div>") if cs else empty_block(
            lang, a("العروض الرسمية لهذه الفئة قريبًا", "Official offers for this category are coming soon"),
            a("ننشر عروض هذه الفئة فور اعتماد برامج الشراكة الرسمية مع متاجرها. اشترك ليصلك أول عرض.", "We’ll publish offers here as soon as official partner programmes with stores in this category are approved. Subscribe to hear first."),
            brand_cta_actions(lang), f'<svg class="big-ic" viewBox="0 0 56 56" aria-hidden="true">{CAT_ICON[c["slug"]]}</svg>')
        body = page_hero(lang, cr, a("فئة", "Category"), esc(c["name_" + lang]), esc(c["description_" + lang]), cat_icon(c["slug"], 180).replace("<svg ", '<svg class="art" ', 1)) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:2.5rem">
  {content}
  <div class="split" style="align-items:start"><div style="display:grid;gap:1rem"><span class="eyebrow mint">{a('نصائح شراء', 'Buying tips')}</span><h2 style="font-size:1.6rem">{a('قبل أن تشتري', 'Before you buy')}</h2></div><ul class="prose" style="margin:0">{tips}</ul></div>
  <div style="display:grid;gap:1rem"><h2 style="font-size:1.3rem">{a('فئات أخرى', 'Other categories')}</h2><div class="tiles">{others}</div></div>
</div></section>'''
        render(lang, f"/categories/{c['slug']}/", f"{c['name_' + lang]}: {a('عروض رسمية', 'official offers')} | {NAME[lang]}", c["description_" + lang], body, "categories", None, cr)


def build_countries(lang: str, stores: list[dict], seasons: list[dict]) -> None:
    a = lambda ar, en: t(lang, ar, en)
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("الدول", "Countries"), "/countries/")]
    body = page_hero(lang, crumbs, a("الأسواق", "Markets"), a("عروض مخصّصة لبلدك", "Offers for your country"),
                     a("اختر بلدك لترى العروض الصالحة فيه فقط، بعملته وطرق الشحن إليه.", "Choose your country to see only the offers valid there, in its currency and with its shipping options.")) + \
        f'<section class="section"><div class="wrap">{countries_html(lang)}</div></section>'
    render(lang, "/countries/", a("العروض حسب الدولة | كوبون", "Offers by country | Kobon"),
           a("عروض رسمية للسعودية والإمارات والكويت وقطر والبحرين وعُمان ومصر على «كوبون».", "Official offers for Saudi Arabia, the UAE, Kuwait, Qatar, Bahrain, Oman and Egypt on Kobon."),
           body, "", None, crumbs)
    for slug, n_ar, n_en, cur_ar, cur_en in COUNTRIES:
        name = n_ar if lang == "ar" else n_en
        cr = crumbs + [(name, f"/countries/{slug}/")]
        cs = [s for s in stores if slug in s.get("countries", [])]
        others = "".join(f'<a href="{L(lang, "/countries/" + o[0] + "/")}">{o[1] if lang == "ar" else o[2]}</a>' for o in COUNTRIES if o[0] != slug)
        content = ('<div class="store-grid">' + "".join(store_card(lang, s, {}) for s in cs) + "</div>") if cs else empty_block(
            lang, a(f"العروض الرسمية في {name} قريبًا", f"Official offers in {name} are coming soon"),
            a(f"نعرض في {name} فقط العروض الصالحة فيها، بعملتها ({cur_ar}) وطرق الشحن إليها. اشترك ليصلك أول عرض.", f"In {name} we only show offers valid there, in its currency ({cur_en}) and with its shipping options. Subscribe to hear first."),
            brand_cta_actions(lang), flag(slug, 96, "flag big-ic"))
        upcoming = [s for s in seasons if season_status(s) != "past" and (not s.get("countries") or slug in s["countries"])]
        upcoming.sort(key=lambda s: s["start"])
        body = page_hero(lang, cr, a("دولة", "Country"), a(f"عروض رسمية في {name}", f"Official offers in {name}"),
                         a(f"دليلك لعروض المتاجر الرسمية في {name}: مصدر كل عرض وشروطه وتاريخ آخر مراجعة، بالعملة المحلية ({cur_ar}).", f"Your guide to official store offers in {name}: every offer’s source, terms and last-checked date, in the local currency ({cur_en})."),
                         flag(slug, 180, "flag art")) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:2.5rem">
  {content}
  <div style="display:grid;gap:1.2rem"><h2 style="font-size:1.6rem">{a('المواسم القادمة', 'Upcoming seasons')}</h2><div class="seasons">{"".join(season_card(lang, s) for s in upcoming[:4])}</div></div>
  <div style="display:grid;gap:1rem"><h2 style="font-size:1.3rem">{a('دول أخرى', 'Other countries')}</h2><div class="tiles">{others}</div></div>
</div></section>'''
        render(lang, f"/countries/{slug}/", a(f"عروض وأكواد خصم رسمية في {name} | كوبون", f"Official deals and discount codes in {name} | Kobon"),
               a(f"عروض رسمية فقط في {name}: مصدر كل عرض وشروطه وتاريخ آخر مراجعة على «كوبون».", f"Official-only offers in {name}: every offer’s source, terms and last-checked date on Kobon."), body, "", None, cr)


def build_seasons(lang: str, seasons: list[dict]) -> None:
    a = lambda ar, en: t(lang, ar, en)
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("المواسم", "Seasons"), "/seasons/")]
    order = sorted(seasons, key=lambda s: ({"live": 0, "soon": 1, "past": 2}[season_status(s)], s["start"]))
    body = page_hero(lang, crumbs, a("تقويم المواسم", "Season calendar"), a("استعد للموسم <span class=\"hl\">قبل أن يبدأ</span>", "Get ready <span class=\"hl\">before the season starts</span>"),
                     a("صفحة خاصة لكل موسم كبير، فيها المواعيد المتوقعة ونصائح الشراء، والعروض الرسمية فور صدورها.", "A dedicated page for every big season, with expected dates, buying tips and the official offers as soon as they’re released.")) + \
        f'<section class="section"><div class="wrap"><div class="seasons">{"".join(season_card(lang, s) for s in order)}</div><p class="note" style="margin-top:1.5rem;text-align:center">{a("التواريخ تقديرية وقد تختلف حسب الدولة والمتجر، والمواسم الهجرية حسب رؤية الهلال.", "Dates are estimates and can vary by country and store. Hijri seasons depend on the moon sighting.")}</p></div></section>'
    render(lang, "/seasons/", a("تقويم مواسم التخفيضات في الخليج ومصر | كوبون", "Sale season calendar for the Gulf and Egypt | Kobon"),
           a("مواعيد الجمعة البيضاء و11.11 ورمضان وعيد الفطر ويوم التأسيس واليوم الوطني، مع نصائح الشراء والعروض الرسمية فور صدورها.", "Dates for White Friday, 11.11, Ramadan, Eid al-Fitr, Founding Day and National Day, with buying tips and official offers as soon as they’re out."),
           body, "seasons", None, crumbs)
    for s in seasons:
        st = season_status(s)
        cr = crumbs + [(s["name_" + lang], f"/seasons/{s['slug']}/")]
        badge = {"live": f'<span class="status">● {a("قائم الآن", "Live now")}</span>', "soon": f'<span class="status soon">{a("قريبًا", "Coming up")}</span>', "past": f'<span class="status off">{a("انتهى هذا العام، ونجهّز للموسم القادم", "Over for this year. We’re preparing for the next one")}</span>'}[st]
        tips = "".join(f"<li>{esc(x)}</li>" for x in s["tips_" + lang])
        bg, glyph = SEASON_STYLE.get(s["slug"], SEASON_STYLE["white-friday"])
        c1, c2 = _re.findall(r"#[0-9A-Fa-f]{6}", bg)[:2]
        art = f'<svg class="art" viewBox="0 0 200 200" aria-hidden="true" style="max-width:260px"><defs><linearGradient id="sg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs><rect width="200" height="200" rx="40" fill="url(#sg)"/><g transform="translate(40 40) scale(5)" fill="#fff" opacity=".9">{glyph}</g></svg>'
        facts = f'''<div class="facts-grid">
  <div class="fact"><small>{a('يبدأ', 'Starts')}</small><b>{day_label(lang, s['start'])}</b></div>
  <div class="fact"><small>{a('ينتهي تقريبًا', 'Ends around')}</small><b>{day_label(lang, s['end_display'])}</b></div>
  <div class="fact"><small>{a('الأسواق', 'Markets')}</small><b>{esc(s['markets_' + lang])}</b></div>
</div>'''
        content = empty_block(lang, a("العروض الرسمية لهذا الموسم تُنشر فور صدورها", "Official offers for this season are published as soon as they’re out"),
                              a("لا ننشر توقعات أو أكوادًا غير مؤكدة. اشترك ليصلك كل عرض رسمي لهذا الموسم.", "We don’t post guesses or unconfirmed codes. Subscribe to get every official offer for this season."), brand_cta_actions(lang))
        body = page_hero(lang, cr, a("موسم", "Season"), esc(s["name_" + lang]), esc(s["blurb_" + lang]), art, extra=badge) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:2.5rem">
  {facts}
  {content}
  <div class="split" style="align-items:start"><div style="display:grid;gap:1rem"><span class="eyebrow mint">{a('نصائح الموسم', 'Season tips')}</span><h2 style="font-size:1.6rem">{a('كيف تستعد', 'How to get ready')}</h2></div><ul class="prose" style="margin:0">{tips}</ul></div>
</div></section>'''
        ev = {"@context": "https://schema.org", "@type": "Event", "name": s["name_" + lang], "startDate": s["start"], "endDate": s["end_display"],
              "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode", "eventStatus": "https://schema.org/EventScheduled",
              "location": {"@type": "VirtualLocation", "url": abs_url(lang, f"/seasons/{s['slug']}/")}, "description": s["blurb_" + lang],
              "organizer": {"@type": "Organization", "name": NAME[lang], "url": DOMAIN + "/"}}
        render(lang, f"/seasons/{s['slug']}/", a(f"{s['name_ar']}: المواعيد والعروض الرسمية | كوبون", f"{s['name_en']}: dates and official offers | Kobon"),
               s["blurb_" + lang], body, "seasons", [ev], cr)


REDIRECTS = {
    # old path -> new path (same language tree)
    "/brands/": "/partners/",
    "/advertise/": "/partners/",
    "/marketers/": "/partners/",
    "/how-we-verify/": "/how-it-works/",
    "/stores/iherb/": "/",
    "/stores/namshi/": "/",
}


def build_redirects() -> None:
    for lang in ("ar", "en"):
        for old, new in REDIRECTS.items():
            target = L(lang, new)
            msg = t(lang, "جارٍ التحويل…", "Redirecting…")
            write(out_path(lang, old), f"""<!DOCTYPE html>
<html lang="{'ar' if lang == 'ar' else 'en'}" dir="{'rtl' if lang == 'ar' else 'ltr'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{msg} | {NAME[lang]}</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{DOMAIN + target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace({json.dumps(target)} + location.hash);</script>
</head>
<body><p><a href="{target}">{msg}</a></p></body>
</html>
""")


def build_404() -> None:
    body = f'''<section class="page-hero"><div class="wrap">
  <div class="copy"><span class="eyebrow">404</span><h1>الصفحة غير موجودة<br><span class="hl" lang="en" style="font-size:.6em">Page not found</span></h1>
  <p class="lead">ربما نُقلت الصفحة أو لم تعد موجودة. ابدأ من الرئيسية أو ابحث عن متجر.</p>
  <div style="display:flex;gap:.8rem;flex-wrap:wrap"><a class="btn btn-primary" href="/">العودة للرئيسية</a><a class="btn btn-ghost" href="/en/" lang="en">English home</a></div></div>
  <svg class="art" viewBox="0 0 48 48" aria-hidden="true" style="max-width:220px">{LOGO_SVG.split('>', 1)[1].rsplit('</svg>', 1)[0]}</svg>
</div></section>'''
    out = head("ar", "/", "الصفحة غير موجودة | كوبون", "الصفحة المطلوبة غير موجودة.").replace(
        '<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">')
    write("404.html", out + header("ar", "/", "") + f'<main id="main">{body}</main>' + footer("ar", "/"))


def build_sitemap(paths: list[str]) -> None:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p in paths:
        for lang in ("ar", "en"):
            lines.append("  <url>")
            lines.append(f"    <loc>{abs_url(lang, p)}</loc>")
            lines.append(f"    <lastmod>{TODAY}</lastmod>")
            lines.append(f'    <xhtml:link rel="alternate" hreflang="ar" href="{abs_url("ar", p)}"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{abs_url("en", p)}"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_url("ar", p)}"/>')
            lines.append("  </url>")
    lines.append("</urlset>")
    write("sitemap.xml", "\n".join(lines) + "\n")


def build_misc() -> None:
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    write("CNAME", CNAME_HOST + "\n")
    write("_config.yml", "# GitHub Pages: publish only the generated site\nexclude:\n  - build.py\n  - data\n  - README.md\n  - CHANGELOG.md\n  - tools\n")
    write("llms.txt", f"""# {NAME['en']} ({NAME['ar']})

> Official-only deals and discount-code guide for Saudi Arabia, the UAE, Kuwait, Qatar, Bahrain, Oman and Egypt, run by an affiliate marketing team with experience across the Gulf and Egypt.

- Home (Arabic): {DOMAIN}/
- Home (English): {DOMAIN}/en/
- For brands: {DOMAIN}/en/partners/
- How it works and verification standard: {DOMAIN}/en/how-it-works/
- About: {DOMAIN}/en/about/
- Contact: {EMAIL}
""")


def clean() -> None:
    for name in ("stores", "categories", "countries", "seasons", "en", "about", "how-we-verify", "how-it-works", "privacy",
                 "affiliate-disclosure", "marketers", "partners", "contact", "terms", "brands", "advertise"):
        p = ROOT / name
        if p.is_dir():
            shutil.rmtree(p)
    for name in ("index.html", "404.html", "sitemap.xml", "robots.txt", "CNAME", "llms.txt"):
        p = ROOT / name
        if p.is_file():
            p.unlink()


def main() -> None:
    cats = load("categories.json")
    seasons = load("seasons.json")
    stores = [s for s in load("coupons.json") if not s.get("example")]
    clean()
    for lang in ("ar", "en"):
        build_home(lang, cats, seasons)
        build_partners(lang)
        build_about(lang)
        build_how(lang)
        build_contact(lang)
        for slug in LEGAL:
            build_legal(lang, slug)
        build_stores(lang, stores, cats)
        build_categories(lang, cats, stores)
        build_countries(lang, stores, seasons)
        build_seasons(lang, seasons)
    build_redirects()
    build_404()
    build_misc()
    paths = [p for p in PAGES if p]
    build_sitemap(paths)
    print(f"Built {len(paths)} pages x 2 languages, {len(REDIRECTS) * 2} redirects.")


if __name__ == "__main__":
    main()
