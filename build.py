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
ASSET_V = "4"

COUNTRIES = [
    ("sa", "السعودية", "Saudi Arabia", "ر.س", "SAR"),
    ("ae", "الإمارات", "UAE", "د.إ", "AED"),
    ("kw", "الكويت", "Kuwait", "د.ك", "KWD"),
    ("qa", "قطر", "Qatar", "ر.ق", "QAR"),
    ("bh", "البحرين", "Bahrain", "د.ب", "BHD"),
    ("om", "عُمان", "Oman", "ر.ع", "OMR"),
    ("eg", "مصر", "Egypt", "ج.م", "EGP"),
    ("global", "المتاجر العالمية", "International stores", "عملة المتجر", "store currency"),
]

FLAGS = {
    "sa": '<rect width="30" height="30" fill="#006C35"/><rect x="8" y="14" width="14" height="2" fill="#fff"/>',
    "ae": '<rect width="30" height="10" fill="#00732F"/><rect y="10" width="30" height="10" fill="#fff"/><rect y="20" width="30" height="10" fill="#000"/><rect width="9" height="30" fill="#FF0000"/>',
    "kw": '<rect width="30" height="10" fill="#007A3D"/><rect y="10" width="30" height="10" fill="#fff"/><rect y="20" width="30" height="10" fill="#CE1126"/><path d="M0 0l9 10v10L0 30z" fill="#000"/>',
    "qa": '<rect width="30" height="30" fill="#8A1538"/><path d="M0 0h10l3 2-3 2 3 2-3 2 3 2-3 2 3 2-3 2 3 2-3 2 3 2-3 2 3 2-3 2 3 2H0z" fill="#fff"/>',
    "bh": '<rect width="30" height="30" fill="#CE1126"/><path d="M0 0h10l3 3-3 3 3 3-3 3 3 3-3 3 3 3-3 3 3 3-3 3H0z" fill="#fff"/>',
    "om": '<rect width="30" height="10" fill="#fff"/><rect y="10" width="30" height="10" fill="#DB161B"/><rect y="20" width="30" height="10" fill="#008000"/><rect width="10" height="30" fill="#DB161B"/>',
    "global": '<rect width="30" height="30" fill="#6D5BFF"/><circle cx="15" cy="15" r="9" fill="none" stroke="#fff" stroke-width="1.8"/><path d="M6 15h18M15 6c3 3 3 15 0 18M15 6c-3 3-3 15 0 18" fill="none" stroke="#fff" stroke-width="1.5"/>',
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
        "description": "كوبونات وعروض رسمية من المتاجر الخليجية والعالمية، يديرها فريق متخصص في التسويق بالعمولة. Official coupons and deals from Gulf and international stores, run by an affiliate marketing team.",
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


CSP = ("default-src 'self'; script-src 'self' https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data:; font-src 'self'; connect-src 'self' https://cloudflareinsights.com; "
       "base-uri 'self'; form-action 'self' mailto:; object-src 'none'; upgrade-insecure-requests")
CF_BEACON_TOKEN = "b9eed0a7d3194a7d95be8f4a9be48102"
BEACON = ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
          'data-cf-beacon=\'{"token": "' + CF_BEACON_TOKEN + '"}\'></script>') if CF_BEACON_TOKEN else ""


NAV = [
    ("home", "/", "الرئيسية", "Home"),
    ("stores", "/stores/", "المتاجر", "Stores"),
    ("categories", "/categories/", "الفئات", "Categories"),
    ("guides", "/guides/", "الأدلة", "Guides"),
    ("how", "/how-it-works/", "كيف يعمل", "How it works"),
    ("partners", "/partners/", "الشراكات", "For Brands"),
    ("about", "/about/", "من نحن", "About"),
]


def head(lang: str, path: str, title: str, desc: str, ld: list[dict] | None = None, og_image: str = "/assets/og-default.png", noindex: bool = False, og_type: str = "website") -> str:
    canon = abs_url(lang, path)
    ar_url = abs_url("ar", path)
    en_url = abs_url("en", path)
    graph = [org_ld(), {
        "@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/", "name": NAME["ar"], "alternateName": NAME["en"],
        "inLanguage": ["ar", "en"], "publisher": {"@id": DOMAIN + "/#org"},
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
<meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-image-preview:large'}">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
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
<meta property="og:type" content="{og_type}">
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
    cta_label, cta_href = cta or (t(lang, "انضم كشريك", "Become a partner"), L(lang, "/partners/#contact"))
    ann = ""
    if announce:
        ann = '<div class="announce">' + t(
            lang,
            "<b>عروض رسمية فقط</b> من المتاجر الخليجية والعالمية. اشترك ليصلك أول عرض فور نشره.",
            "<b>Official offers only</b>, from Gulf and international stores. Subscribe to get the first one.",
        ) + "</div>\n"
    return f"""{ann}<header class="header"><div class="wrap">
  <a class="logo" href="{L(lang, '/')}">{logo(lang)}</a>
  <nav class="nav" aria-label="{t(lang, 'القائمة الرئيسية', 'Main')}">{nav}</nav>
  <div class="header-actions">
    <a class="pill" href="{L(lang, '/countries/')}">{flag('global', 20)}{t(lang, 'الأسواق', 'Markets')}</a>
    <a class="pill lang" href="{switch}" hreflang="{other}" lang="{other}">{t(lang, 'EN', 'العربية')}</a>
    <a class="btn btn-primary" href="{cta_href}">{esc(cta_label)}</a>
    <details class="menu"><summary aria-label="{t(lang, 'فتح القائمة', 'Open menu')}"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0E1330" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>
      <div class="panel">{nav}<a href="{L(lang, '/countries/')}">{t(lang, 'الأسواق', 'Markets')}</a><a href="{L(lang, '/contact/')}">{t(lang, 'تواصل معنا', 'Contact')}</a><a href="{switch}" hreflang="{other}" lang="{other}">{t(lang, 'English', 'العربية')}</a><a class="btn btn-primary" href="{cta_href}">{esc(cta_label)}</a></div>
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
    <div><a class="logo" href="{L(lang, '/')}">{logo(lang, 40)}</a><p class="disclosure">{t(lang, 'كوبونات وعروض رسمية من المتاجر الخليجية والعالمية. قد نحصل على عمولة عند الشراء عبر روابطنا، دون أي تكلفة إضافية عليك.', 'Official coupons and deals from Gulf and international stores. We may earn a commission when you buy through our links, at no extra cost to you.')}</p></div>
    <div><h2 class="fh">{t(lang, 'تسوّق', 'Shop')}</h2><ul>{li('/guides/', 'أدلة التسوق', 'Shopping guides')}{li('/stores/', 'المتاجر', 'Stores')}{li('/categories/', 'الفئات', 'Categories')}{li('/seasons/', 'المواسم', 'Seasons')}{li('/countries/', 'الأسواق', 'Markets')}</ul></div>
    <div><h2 class="fh">{NAME[lang]}</h2><ul>{li('/about/', 'من نحن', 'About us')}{li('/how-it-works/', 'كيف يعمل', 'How it works')}{li('/how-it-works/#standard', 'معيار كوبون', 'The Kobon standard')}{li('/contact/', 'تواصل معنا', 'Contact')}</ul></div>
    <div><h2 class="fh">{t(lang, 'الشراكات', 'Partners')}</h2><ul>{li('/partners/', 'للعلامات التجارية', 'For brands')}{li('/partners/#models', 'نماذج التعاون', 'Collaboration models')}{li('/partners/#founding', 'الشركاء المؤسسون', 'Founding partners')}<li><a href="/media-kit.pdf">{t(lang, 'الملف التعريفي (PDF)', 'Media kit (PDF)')}</a></li><li><a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
    <div><h2 class="fh">{t(lang, 'قانوني', 'Legal')}</h2><ul>{li('/privacy/', 'الخصوصية', 'Privacy')}{li('/terms/', 'الشروط', 'Terms')}{li('/affiliate-disclosure/', 'الإفصاح عن العمولة', 'Commission disclosure')}</ul></div>
  </div>
  <div class="legal"><span>© {YEAR} {NAME[lang]} · kobon.is-a.si</span><span><a href="{L('ar', path)}" lang="ar" hreflang="ar">العربية</a> · <a href="{L('en', path)}" lang="en" hreflang="en">English</a></span></div>
</div></footer>
<script src="/assets/app.js?v={ASSET_V}" defer></script>
{BEACON}
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
           crumbs: list[tuple[str, str]] | None = None, cta=None, flush_footer: bool = False, announce: bool = True,
           noindex: bool = False, og_type: str = "website") -> None:
    lds = list(ld or [])
    if crumbs:
        lds.append(breadcrumb_ld(lang, crumbs))
    html_out = head(lang, path, title, desc, lds, noindex=noindex, og_type=og_type) + header(lang, path, active, cta, announce) + f'<main id="main">\n{body}\n</main>\n' + footer(lang, path, flush_footer)
    write(out_path(lang, path), html_out)
    PAGES.append(path if (lang == "ar" and not noindex) else None)
    if noindex and lang == "ar":
        NOINDEXED.append(path)


PAGES: list = []
SITEMAP: list[str] = []
NOINDEXED: list[str] = []


def section_head(eyebrow: str, h2: str, p: str = "", cls: str = "") -> str:
    pp = f"<p>{p}</p>" if p else ""
    return f'<div class="section-head"><span class="eyebrow {cls}">{eyebrow}</span><h2>{h2}</h2>{pp}</div>'


def empty_block(lang: str, title: str, text: str, actions: str, icon: str = "") -> str:
    ic = icon or f'<svg class="big-ic" viewBox="0 0 96 96" aria-hidden="true"><circle cx="48" cy="48" r="48" fill="#FFF0EB"/><path d="M26 30h44a4 4 0 0 1 4 4v8a6 6 0 0 0 0 12v8a4 4 0 0 1-4 4H26a4 4 0 0 1-4-4v-8a6 6 0 0 0 0-12v-8a4 4 0 0 1 4-4z" fill="#FF5A36"/><path d="M58 32v32" stroke="#fff" stroke-dasharray="3 4" stroke-width="2"/><circle cx="38" cy="42" r="3" fill="#fff"/><circle cx="46" cy="54" r="3" fill="#fff"/><path d="M47 40 37 56" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/></svg>'
    return f'<div class="empty">{ic}<div style="display:grid;gap:.6rem"><h2 style="font-size:1.35rem">{title}</h2><p>{text}</p><div class="actions">{actions}</div></div></div>'


def hero_svg(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    coin = a("ر.س", "SAR")
    return f'''<svg class="hero-art" viewBox="0 0 560 500" role="img" aria-label="{a('رسم توضيحي: جوال يعرض عرضًا رسميًا تم التحقق منه', 'Illustration: a phone showing a verified official offer')}">
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
      <text x="290" y="397" font-family="Readex Pro" font-weight="600" font-size="13" fill="#fff" text-anchor="middle">{a('انتقل إلى المتجر ←', 'Go to store →')}</text>
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
        <text x="486" y="166" font-family="IBM Plex Sans Arabic" font-size="11" fill="#7A7F9A" text-anchor="end">{a('تم التحقق اليوم', 'Checked today')}</text>
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
        (CHECK.format(s=24, c="#FFC233"), t(lang, "عروض رسمية فقط", "Official offers only"), t(lang, "من المتجر أو برنامج شريك معتمد", "From the store or an approved programme")),
        ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#14B8A6" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>', t(lang, "تاريخ آخر تحقق", "Last-checked date"), t(lang, "ظاهر على كل عرض", "Shown on every offer")),
        ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2"><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/><circle cx="12" cy="12" r="9"/></svg>', t(lang, "الخليج ومصر والعالم", "Gulf, Egypt & global"), t(lang, "دول الخليج ومصر والمتاجر العالمية", "GCC markets, Egypt and international stores")),
        ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#A99FFF" stroke-width="2"><path d="M4 5h16v11H8l-4 4z"/></svg>', t(lang, "بالعربية والإنجليزية", "Arabic & English"), t(lang, "محتوى واضح بلغتين", "Clear in both languages")),
    ]
    return '<div class="wrap"><div class="strip">' + "".join(
        f'<div><span class="ic">{ic}</span><span><b>{b}</b><small>{s}</small></span></div>' for ic, b, s in items
    ) + "</div></div>"


def why_cards(lang: str) -> str:
    return f'''<div class="grid-3">
      <article class="card"><span class="ic bg-coral">{CHECK.format(s=30, c="#FF5A36")}</span><h3>{t(lang, 'من المصدر مباشرة', 'Straight from the source')}</h3><p>{t(lang, 'لا ننشر كوبونًا إلا إذا أصدره المتجر نفسه أو برنامج شريك معتمد.', 'We only publish a coupon issued by the store itself or an approved partner programme.')}</p></article>
      <article class="card"><span class="ic bg-mint"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#14B8A6" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8 9h8M8 13h8M8 17h5"/></svg></span><h3>{t(lang, 'الشروط قبل الكود', 'Terms before the code')}</h3><p>{t(lang, 'الحد الأدنى للشراء، والحد الأقصى للخصم، والدول المشمولة، وتاريخ الانتهاء في بطاقة واحدة.', 'Minimum spend, maximum discount, eligible countries and expiry, all on one card.')}</p></article>
      <article class="card"><span class="ic bg-saffron"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#E0A100" stroke-width="2"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg></span><h3>{t(lang, 'جاهزون لكل موسم', 'Ready for every season')}</h3><p>{t(lang, 'صفحات الجمعة البيضاء و11.11 ورمضان والعيد جاهزة قبل موعدها.', 'White Friday, 11.11, Ramadan and Eid pages go live before the season starts.')}</p></article>
    </div>'''


def steps_html(lang: str) -> str:
    return f'''<div class="steps">
      <div class="step"><div class="art bg-violet"><svg width="200" height="140" viewBox="0 0 200 140" aria-hidden="true"><rect x="20" y="40" width="160" height="44" rx="22" fill="#fff"/><circle cx="154" cy="62" r="10" fill="none" stroke="#6D5BFF" stroke-width="4"/><path d="m161 69 8 8" stroke="#6D5BFF" stroke-width="4" stroke-linecap="round"/><rect x="40" y="56" width="90" height="12" rx="6" fill="#0E1330" opacity=".2"/><rect x="40" y="96" width="50" height="22" rx="11" fill="#fff"/><rect x="96" y="96" width="64" height="22" rx="11" fill="#6D5BFF" opacity=".25"/></svg></div>
        <span class="num">1</span><h3>{t(lang, 'اختر المتجر', 'Pick a store')}</h3><p>{t(lang, 'ابحث بالاسم، أو تصفّح الفئات والمواسم.', 'Search by name, or browse categories and seasons.')}</p></div>
      <div class="step"><div class="art bg-coral"><svg width="200" height="140" viewBox="0 0 200 140" aria-hidden="true"><path d="M30 30h140a8 8 0 0 1 8 8v20a12 12 0 0 0 0 24v20a8 8 0 0 1-8 8H30a8 8 0 0 1-8-8V82a12 12 0 0 0 0-24V38a8 8 0 0 1 8-8z" fill="#fff"/><line x1="130" y1="36" x2="130" y2="104" stroke="#FF5A36" stroke-dasharray="5 5" stroke-width="2"/><text x="154" y="78" font-family="Readex Pro" font-weight="700" font-size="22" fill="#FF5A36" text-anchor="middle">%</text><rect x="44" y="52" width="70" height="10" rx="5" fill="#0E1330" opacity=".7"/><rect x="44" y="70" width="50" height="8" rx="4" fill="#0E1330" opacity=".25"/><rect x="44" y="84" width="60" height="8" rx="4" fill="#0E1330" opacity=".25"/></svg></div>
        <span class="num">2</span><h3>{t(lang, 'اقرأ الشروط وانسخ الكود', 'Check the terms, copy the code')}</h3><p>{t(lang, 'كل ما يلزمك قبل الشراء في بطاقة العرض.', 'Everything you need to know is on the offer card.')}</p></div>
      <div class="step"><div class="art bg-mint"><svg width="200" height="140" viewBox="0 0 200 140" aria-hidden="true"><path d="M60 46h80l8 70a8 8 0 0 1-8 9H60a8 8 0 0 1-8-9z" fill="#14B8A6"/><path d="M78 46V38a22 22 0 0 1 44 0v8" fill="none" stroke="#0E1330" stroke-width="5" stroke-linecap="round"/><circle cx="100" cy="86" r="18" fill="#fff"/><path d="m91 86 6 6 12-12" stroke="#14B8A6" stroke-width="4" fill="none" stroke-linecap="round"/></svg></div>
        <span class="num">3</span><h3>{t(lang, 'أكمل الشراء', 'Check out and save')}</h3><p>{t(lang, 'الصق الكود في صفحة الدفع على موقع المتجر الرسمي.', 'Paste the code at checkout on the store’s official site.')}</p></div>
    </div>'''


STANDARD = [
    ("المصدر", "Source", "نتحقق أن العرض صادر عن المتجر أو برنامج شريك معتمد.", "We confirm the offer comes from the store or an approved partner programme."),
    ("الشروط", "Terms", "نوثّق الحد الأدنى للشراء والحد الأقصى للخصم والدول والاستثناءات.", "We record minimum spend, maximum discount, countries and exclusions."),
    ("التجربة", "Test", "نجرّب الكود على سلة حقيقية كلما أمكن.", "We try the code on a real basket whenever we can."),
    ("المتابعة", "Monitor", "نحذف العرض المنتهي ونحدّث تاريخ آخر تحقق.", "We remove expired offers and update the last-checked date."),
]


def standard_list(lang: str) -> str:
    return '<div class="vlist">' + "".join(
        f'<div class="vitem"><span class="n">{i+1}</span><div><h3>{t(lang, a, b)}</h3><p>{t(lang, c, d)}</p></div></div>' for i, (a, b, c, d) in enumerate(STANDARD)
    ) + "</div>"


def sample_tickets(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    return f'''<div style="display:grid;gap:1.2rem">
      <p style="color:var(--muted);font-size:.9rem;text-align:center"><span class="tag-ex">{a('مثال توضيحي', 'Illustrative example')}</span> {a('هكذا تبدو بطاقة العرض، وهي ليست عرضًا حقيقيًا', 'This is how an offer card looks. It isn’t a live offer.')}</p>
      <div class="ticket" aria-label="{a('مثال توضيحي لبطاقة عرض', 'Illustrative offer card')}">
        <div class="main">
          <div style="display:flex;gap:.5rem;flex-wrap:wrap"><span class="badge ok">✓ {a('مصدر رسمي', 'Official source')}</span><span class="badge warn">{a('ينتهي خلال 5 أيام', 'Ends in 5 days')}</span></div>
          <h3>{a('خصم 20% على الطلب الأول', '20% off your first order')}</h3>
          <p style="color:var(--ink-soft);font-size:.92rem">{a('متجر أزياء · السعودية والإمارات', 'Fashion store · Saudi Arabia & UAE')}</p>
          <div class="meta"><span>{a('الحد الأدنى للشراء', 'Min. spend')}<b>{a('150 ر.س', 'SAR 150')}</b></span><span>{a('الحد الأقصى للخصم', 'Max. discount')}<b>{a('100 ر.س', 'SAR 100')}</b></span><span>{a('آخر تحقق', 'Last checked')}<b>{a('اليوم', 'Today')}</b></span></div>
        </div>
        <div class="side"><div><b>20%</b><div style="font-size:.9rem;margin-top:.4rem">{a('اعرض الكود', 'Show code')}</div></div></div>
      </div>
      <div class="ticket" style="transform:scale(.94);opacity:.75">
        <div class="main"><div><span class="badge ok">✓ {a('مصدر رسمي', 'Official source')}</span></div><h3>{a('شحن مجاني فوق 99 ر.س', 'Free shipping over SAR 99')}</h3><div class="meta"><span>{a('الدول', 'Countries')}<b>{a('الخليج', 'GCC')}</b></span><span>{a('النوع', 'Type')}<b>{a('عرض', 'Deal')}</b></span><span>{a('آخر تحقق', 'Last checked')}<b>{a('أمس', 'Yesterday')}</b></span></div></div>
        <div class="side" style="background:var(--mint)"><div><b style="font-size:1.4rem">{a('شحن<br>مجاني', 'Free<br>ship')}</b></div></div>
      </div>
    </div>'''


def cats_html(lang: str, cats: list[dict]) -> str:
    return '<div class="cats">' + "".join(
        f'<a class="cat" href="{L(lang, "/categories/" + c["slug"] + "/")}">{cat_icon(c["slug"])}{esc(c["name_" + lang])}<small>{esc(c["short_" + lang])}</small></a>' for c in cats
    ) + "</div>"


def season_tag(lang: str, s: dict, page: bool = False) -> str:
    st = season_status(s)
    if page:
        labels = {"soon": t(lang, f"يبدأ نحو {day_label(lang, s['start'])}. استعد مبكرًا بالنصائح أدناه.", f"Starts around {day_label(lang, s['start'])}. Get ready early with the tips below."),
                  "live": t(lang, "الموسم جارٍ الآن. لم ننشر عروضًا رسمية بعد، فخطّط لمشترياتك بالنصائح أدناه.", "The season is under way. No official offers published yet, so plan with the tips below."),
                  "past": t(lang, "انتهى لهذا العام. خطّط للموسم القادم مبكرًا.", "Over for this year. Plan early for the next one.")}
        cls = {"soon": "status soon", "live": "status", "past": "status off"}
        base = "status"
    else:
        labels = {"soon": month_label(lang, s["start"]), "live": t(lang, "● الموسم جارٍ · خطّط الآن", "● Under way · plan now"),
                  "past": t(lang, "انتهى لهذا العام", "Over for this year")}
        cls = {"soon": "tag", "live": "tag", "past": "tag"}
        base = "tag"
    data = (f' data-season-start="{s["start"]}" data-season-end="{s["end"]}" data-l-soon="{esc(labels["soon"])}" data-l-live="{esc(labels["live"])}"'
            f' data-l-past="{esc(labels["past"])}" data-c-soon="{cls["soon"]}" data-c-live="{cls["live"]}" data-c-past="{cls["past"]}"')
    return f'<span class="{cls[st]}"{data}>{esc(labels[st])}</span>'


def season_card(lang: str, s: dict) -> str:
    bg, glyph = SEASON_STYLE.get(s["slug"], SEASON_STYLE["white-friday"])
    return f'<a class="season" href="{L(lang, "/seasons/" + s["slug"] + "/")}" style="background:{bg}">{season_tag(lang, s)}<div><h3>{esc(s["name_" + lang])}</h3><div class="date">{esc(s["note_" + lang])}</div></div><svg width="140" height="140" viewBox="0 0 24 24" fill="#fff" aria-hidden="true">{glyph}</svg></a>'


def countries_html(lang: str) -> str:
    return '<div class="countries">' + "".join(
        f'<a class="country" href="{L(lang, "/countries/" + c[0] + "/")}">{flag(c[0])}{c[1] if lang == "ar" else c[2]}</a>' for c in COUNTRIES
    ) + "</div>"


def band_html(lang: str) -> str:
    return f'''<section class="wrap">
  <div class="band">
    <div style="display:grid;gap:1rem">
      <span class="eyebrow light">{t(lang, 'للعلامات التجارية', 'For brands')}</span>
      <h2>{t(lang, 'علامتك أمام متسوقين جاهزين للشراء.', 'Put your brand in front of ready-to-buy shoppers.')}</h2>
      <p>{t(lang, 'فريق تسويق بالعمولة يحوّل عروضك الرسمية إلى مبيعات في الخليج والأسواق العالمية، وتدفع مقابل النتائج.', 'An affiliate marketing team that turns your official offers into sales across the Gulf and international markets. You pay for results.')}</p>
      <div class="actions"><a class="btn btn-primary" href="{L(lang, '/partners/')}">{t(lang, 'اعرف المزيد ←', 'Learn more →')}</a><a class="btn btn-outline-light mail" href="mailto:{EMAIL}">{EMAIL}</a></div>
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
    <div><h2>{t(lang, 'كن أول من يعرف', 'Be the first to know')}</h2><p style="margin-top:.6rem">{t(lang, 'رسالة أسبوعية واحدة بأفضل العروض الرسمية. يمكنك إلغاء الاشتراك متى شئت.', 'One weekly email with the best official offers. Unsubscribe any time.')}</p></div>
    <form class="js-mailto" data-to="{EMAIL}" data-subject="{esc(subj)}" method="get">
      <label class="sr" for="news-email" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">{t(lang, 'بريدك الإلكتروني', 'Your email')}</label>
      <input type="hidden" name="subject" value="{esc(subj)}">
      <input id="news-email" name="body" type="email" required placeholder="{t(lang, 'بريدك الإلكتروني', 'Your email')}" autocomplete="email" dir="ltr">
      <button class="btn" style="background:var(--ink);color:#fff">{t(lang, 'اشترك', 'Subscribe')}</button>
    </form>
  </div>
</section>'''


HOME_FAQ = {
    "ar": [
        ("ما هو كوبون؟", "دليل كوبونات وعروض رسمية للمتسوقين في الخليج، يشمل المتاجر المحلية والعالمية، ويديره فريق متخصص في التسويق بالعمولة."),
        ("لماذا العروض قليلة حاليًا؟", "لأننا لا ننشر أي كود خصم مجهول المصدر. نضيف العروض فور اعتماد برامج الشركاء الرسمية مع المتاجر."),
        ("هل تشمل العروض المتاجر العالمية؟", "نعم. نعرض عروض المتاجر العالمية التي تشحن إلى الخليج وإلى دول العالم، مع توضيح الدول المشمولة في كل عرض."),
        ("هل يحصل كوبون على عمولة؟", "قد يدفع لنا المتجر عمولة عند الشراء عبر روابطنا، دون أي تكلفة إضافية عليك ودون أن يتغير السعر."),
        ("ماذا أفعل إذا لم يعمل الكود؟", "راجع شروط العرض أولًا، ثم أبلغنا من صفحة التواصل وسنراجعه خلال يوم عمل."),
    ],
    "en": [
        ("What is Kobon?", "Kobon is a guide to official coupons and deals for shoppers in the Gulf, covering both local and international stores. It’s run by a team that specialises in affiliate marketing."),
        ("Why are there so few offers right now?", "Because we never publish a code we can’t trace to its source. Offers go live as soon as official partner programmes with stores are approved."),
        ("Do you cover international stores?", "Yes. We list offers from international stores that ship to the Gulf and worldwide, and every offer shows which countries it covers."),
        ("Does Kobon earn a commission?", "A store may pay us a commission when you buy through our links. It costs you nothing extra and never changes the price."),
        ("What if a code doesn’t work?", "Check the offer’s terms first. If it still fails, let us know from the contact page and we’ll look into it within one business day."),
    ],
}


def build_home(lang: str, cats: list[dict], seasons: list[dict]) -> None:
    a = lambda ar, en: t(lang, ar, en)
    chips = "".join(f'<a class="chip" href="{L(lang, "/guides/" + g["slug"] + "/")}">{esc(g["chip_" + lang])}</a>' for g in HOME_CHIPS)
    cal = [s for s in seasons if season_status(s) != "past"]
    cal.sort(key=lambda s: s["start"])
    featured = ["white-friday-2026", "global-shipping-customs", "verify-coupon-code", "tabby-tamara-bnpl", "ramadan-2027-shopping", "online-returns-saudi"]
    gcards = "".join(guide_card(lang, _g(s)) for s in featured)
    body = f'''<section class="hero">
  <div class="blob" style="width:420px;height:420px;background:#FFC233;top:-120px;inset-inline-end:-80px"></div>
  <div class="blob" style="width:360px;height:360px;background:#14B8A6;bottom:-160px;inset-inline-start:30%;opacity:.25"></div>
  <div class="wrap">
    <div class="hero-copy">
      <span class="eyebrow">✦ {a('كوبونات رسمية · الخليج والعالم', 'Official coupons · Gulf & worldwide')}</span>
      <h1>{a('وفّر بثقة.<br>عروض <span class="hl-u">رسمية فقط</span>.', 'Save with confidence.<br><span class="hl-u">Official offers</span> only.')}</h1>
      <p class="lead">{a('كوبونات وعروض من المتاجر الخليجية والعالمية، مع مصدر كل عرض وشروطه وتاريخ آخر تحقق، وأدلة عملية تساعدك قبل الشراء.', 'Coupons and deals from Gulf and international stores, each with its source, terms and last-checked date, plus practical guides to help before you buy.')}</p>
      <form class="search" action="{L(lang, '/guides/')}" method="get" role="search">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#5E6380" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input name="q" type="search" aria-label="{a('ابحث في أدلة التسوق', 'Search shopping guides')}" placeholder="{a('ابحث: الجمارك، تابي، الجمعة البيضاء…', 'Search: customs, Tabby, White Friday…')}">
        <button class="btn btn-primary"><span>{a('ابحث', 'Search')}</span> {a('←', '→')}</button>
      </form>
      <div class="chips">{chips}</div>
      <div class="trust-row"><span><i class="tick">✓</i>{a('من المتجر مباشرة', 'Straight from the store')}</span><span><i class="tick">✓</i>{a('الشروط كاملة', 'Full terms')}</span><span><i class="tick">✓</i>{a('مصادر رسمية', 'Official sources')}</span></div>
    </div>
    {hero_svg(lang)}
  </div>
</section>
{strip_html(lang)}
<section class="section" id="guides">
  <div class="wrap">
    {section_head(a('أدلة التسوق', 'Shopping guides'), a('اعرف قبل أن <span class="hl">تشتري</span>', 'Know before <span class="hl">you buy</span>'), a('مواعيد المواسم، والجمارك، والتقسيط، وحقوق الإرجاع. من مصادرها الرسمية.', 'Sale dates, customs, instalments and return rights, from official sources.'), 'mint')}
    <div class="guide-grid">{gcards}</div>
    <div class="section-cta"><a class="btn btn-ghost" href="{L(lang, '/guides/')}">{a('كل الأدلة ←', 'All guides →')}</a></div>
  </div>
</section>
<section class="section home-why" style="background:#fff;border-block:1px solid var(--line)">
  <div class="wrap">
    {section_head(a('لماذا كوبون', 'Why Kobon'), a('أكواد أقل. <span class="hl">ثقة أكبر.</span>', 'Fewer codes. <span class="hl">More trust.</span>'), a('كل عرض ننشره له مصدر معروف وشروط واضحة.', 'Every offer we publish has a known source and clear terms.'))}
    {why_cards(lang)}
    <div class="section-cta"><a class="link" href="{L(lang, '/how-it-works/')}">{a('كيف نتحقق من العروض ←', 'How we check offers →')}</a></div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {section_head(a('المواسم', 'Seasons'), a('خطّط قبل الموسم', 'Plan ahead of every sale'), a('المواعيد المتوقعة ونصائح الشراء، والعروض الرسمية فور صدورها.', 'Expected dates, buying tips and official offers the moment they drop.'))}
    <div class="seasons scroll">{"".join(season_card(lang, s) for s in cal[:4])}</div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    {section_head(a('الأسواق', 'Markets'), a('الخليج ومصر والمتاجر العالمية', 'The Gulf, Egypt and international stores'), a('اختر بلدك أو المتاجر العالمية لترى ما يناسبك.', 'Pick your country, or international stores, to see what applies to you.'), 'mint')}
    {countries_html(lang)}
  </div>
</section>
{band_html(lang)}
{news_html(lang)}
<section class="section home-faq" style="padding-top:0">
  <div class="wrap">
    {section_head(a('الأسئلة الشائعة', 'FAQ'), a('إجابات سريعة', 'Quick answers'))}
    <div class="faq">{faq_html(HOME_FAQ[lang])}</div>
  </div>
</section>'''
    title = a("كوبون | كوبونات رسمية وأدلة تسوق للخليج والمتاجر العالمية", "Kobon | Official coupons and shopping guides for the Gulf and beyond")
    desc = a("كوبونات وأكواد خصم رسمية فقط من المتاجر الخليجية والعالمية، مع شروط كل عرض وتاريخ آخر تحقق، وأدلة عن المواسم والجمارك والتقسيط وحقوق الإرجاع.",
             "Official-only coupons and discount codes from Gulf and international stores, with full terms and last-checked dates, plus guides to sales, customs, BNPL and return rights.")
    render(lang, "/", title, desc, body, "home", [faq_ld(HOME_FAQ[lang])])


HOME_CHIPS = [
    {"slug": "white-friday-2026", "chip_ar": "الجمعة البيضاء", "chip_en": "White Friday"},
    {"slug": "global-shipping-customs", "chip_ar": "الجمارك", "chip_en": "Customs"},
    {"slug": "tabby-tamara-bnpl", "chip_ar": "تابي وتمارا", "chip_en": "Tabby & Tamara"},
    {"slug": "ramadan-2027-shopping", "chip_ar": "رمضان 2027", "chip_en": "Ramadan 2027"},
    {"slug": "online-returns-saudi", "chip_ar": "حق الإرجاع", "chip_en": "Returns"},
]


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
        <text x="430" y="130" font-family="IBM Plex Sans Arabic" font-size="13" fill="#7A7F9A" text-anchor="end">{a('المبيعات المحققة', 'Attributed sales')}</text>
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
     ("صفحة متجر احترافية", "A professional store page"), ("صفحة لعلامتك بالعربية والإنجليزية تظهر في الفئات والمواسم والأسواق.", "A bilingual page for your brand, featured across categories, seasons and markets."),
     [("كود خصم حصري لكوبون", "A Kobon-exclusive discount code"), ("صفحة متوافقة مع محركات البحث", "Built for search"), ("شروط واضحة لكل عرض", "Clear terms on every offer")]),
    ("bg-violet", "#6D5BFF", '<path d="M4 19V5M4 19h16M8 15l3-4 3 2 5-6"/>',
     ("المحتوى والسيو", "Content & SEO"), ("محتوى عربي وإنجليزي يجيب عن أسئلة المتسوق ويقوده إلى الشراء.", "Arabic and English content that answers shoppers’ questions and leads to checkout."),
     [("أدلة شراء ومقارنات", "Buying guides and comparisons"), ("صفحات مواسم تُنشر مبكرًا", "Season pages published early"), ("ظهور في البحث وإجابات الذكاء الاصطناعي", "Visibility in search and AI answers")]),
    ("bg-mint", "#14B8A6", '<path d="M4 6h16v12H4z"/><path d="m4 7 8 6 8-6"/>',
     ("البريد والتنبيهات", "Email & alerts"), ("نوصل عروضك إلى المشتركين في التوقيت المناسب.", "We get your offers to subscribers at the right moment."),
     [("نشرة أسبوعية بأفضل العروض", "A weekly best-offers email"), ("تنبيهات موسمية", "Seasonal alerts"), ("روابط قابلة للتتبع", "Fully trackable links")]),
    ("bg-saffron", "#E0A100", '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 19c0-3 3-5 6-5s6 2 6 5M15 19c0-2 1.5-4 4-4"/>',
     ("صنّاع المحتوى", "Creators"), ("نختار مؤثرين يناسبون جمهورك، ولكل منهم كود خصم خاص.", "We match creators to your audience, each with their own discount code."),
     [("اختيار حسب الجمهور لا عدد المتابعين", "Chosen for audience fit, not follower count"), ("كود مستقل لقياس أداء كل مؤثر", "One code per creator for clean tracking"), ("الدفع مقابل المبيعات", "Paid on sales")]),
    ("bg-coral", "#FF5A36", '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/>',
     ("حملات المواسم", "Seasonal campaigns"), ("خطة جاهزة للجمعة البيضاء و11.11 ورمضان والعيد والأيام الوطنية.", "Ready-made plans for White Friday, 11.11, Ramadan, Eid and national days."),
     [("تقويم حملات سنوي", "An annual campaign calendar"), ("صفحات هبوط موسمية", "Seasonal landing pages"), ("تنبيهات قبل الموسم", "Pre-season alerts")]),
    ("bg-violet", "#6D5BFF", '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
     ("تقارير شفافة", "Transparent reporting"), ("تقرير دوري بالنقرات والطلبات والمبيعات وخطوات التحسين.", "Regular reports on clicks, orders and sales, with clear next steps."),
     [("أرقام من منصة التتبع نفسها", "Numbers from the tracking platform itself"), ("مقارنة أداء القنوات", "Channel-by-channel comparison"), ("توصيات عملية", "Actionable recommendations")]),
]

MODELS = [
    ("CPS", "CPS", "عمولة على المبيعات", "Commission on sales", "نسبة من كل طلب مكتمل فقط. الأنسب لمعظم المتاجر.", "A share of completed orders only. The right fit for most stores."),
    ("CPA", "CPA", "مقابل كل إجراء", "Cost per action", "مبلغ محدد لكل تسجيل أو تثبيت تطبيق أو عميل جديد.", "A fixed fee per sign-up, app install or new customer."),
    ("هجين", "Hybrid", "رسوم ظهور وعمولة", "Placement + commission", "ظهور مضمون في المواسم الكبرى، مع عمولة على المبيعات.", "Guaranteed visibility in peak seasons, plus commission on sales."),
    ("مباشر", "Direct", "أو عبر شبكتك", "Or via your network", "بعقد مباشر أو عبر شبكة التسويق بالعمولة التي تعتمدها.", "On a direct contract, or through the affiliate network you already use."),
]

TIMELINE = [
    ("اليوم الأول", "Day one", "مكالمة تعارف", "Intro call", "نتعرّف على منتجك وجمهورك وأهدافك.", "We learn your product, audience and goals."),
    ("خلال 3 أيام", "Within 3 days", "خطة مكتوبة", "Written plan", "القنوات والعروض والجدول الزمني ومؤشرات النجاح.", "Channels, offers, timeline and success metrics."),
    ("الأسبوع الأول", "Week one", "الإطلاق", "Launch", "صفحتك وأكوادك وروابط التتبع جاهزة.", "Your page, codes and tracking links go live."),
    ("أسبوعيًا", "Every week", "تقرير وتحسين", "Report & optimise", "أرقام واضحة وخطوات الأسبوع التالي.", "Clear numbers and next week’s plan."),
]

RULES = [
    ("ننشر أكوادك الرسمية فقط، ولا نسرّب أي كود خاص.", "We publish your official codes only and never leak private ones."),
    ("لا نستخدم اسم علامتك في الإعلانات المدفوعة دون إذن مكتوب.", "No paid ads on your brand name without written permission."),
    ("لا عدّ تنازلي وهمي ولا ادعاءات مبالغ فيها.", "No fake countdowns, no inflated claims."),
    ("نلتزم بسياسات شبكتك وأنظمة كل سوق.", "We follow your network’s policies and each market’s regulations."),
    ("التقارير من منصة التتبع نفسها.", "Reports come straight from the tracking platform."),
    ("نراجع معك أي محتوى عن علامتك قبل نشره عند الطلب.", "Content about your brand can be reviewed before it goes live."),
]

PARTNER_FAQ = {
    "ar": [
        ("هل توجد تكلفة لبدء الشراكة؟", "في نموذج العمولة لا توجد رسوم ثابتة؛ تدفع فقط عند تحقق المبيعات."),
        ("هل تعملون عبر شبكات التسويق بالعمولة؟", "نعم، أو بعقد مباشر، حسب ما يناسبك."),
        ("هل تعملون مع المتاجر العالمية؟", "نعم. نعمل مع المتاجر الخليجية والعالمية التي تشحن إلى الخليج أو إلى دول العالم."),
        ("هل تعرضون علامات تجارية لا تتعاملون معها؟", "لا. لا يظهر اسم أي علامة أو شعارها كشريك إلا بعد اتفاق رسمي."),
    ],
    "en": [
        ("Is there a cost to get started?", "Not on the commission model. There are no fixed fees; you only pay when sales come in."),
        ("Do you work through affiliate networks?", "Yes, or on a direct contract, whichever suits you."),
        ("Do you work with international stores?", "Yes. We work with Gulf and international stores that ship to the region or worldwide."),
        ("Do you feature brands you don’t work with?", "No. A brand’s name or logo only appears as a partner after a formal agreement."),
    ],
}


def partner_form(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    subj = a("طلب شراكة - كوبون", "Partnership request - Kobon")
    markets = [a("السعودية", "Saudi Arabia"), a("الإمارات", "UAE"), a("دول الخليج كلها", "All GCC markets"), a("الأسواق العالمية", "International markets"), a("الخليج والأسواق العالمية", "GCC + international")]
    models = [a("عمولة على المبيعات (CPS)", "Commission on sales (CPS)"), "CPA", a("هجين", "Hybrid"), a("لم نحدد بعد", "Not decided yet")]
    opt = lambda xs: "".join(f"<option>{esc(x)}</option>" for x in xs)
    return f'''<form class="contact-card js-mailto" data-to="{EMAIL}" data-subject="{esc(subj)}" method="get" style="color:var(--ink)">
      <h3 style="font-size:1.4rem">{a('طلب شراكة', 'Partnership request')}</h3>
      <input type="hidden" name="subject" value="{esc(subj)}">
      <div class="row2"><label class="field">{a('الاسم', 'Name')}<input name="{a('الاسم', 'Name')}" required placeholder="{a('اسمك الكامل', 'Your full name')}" autocomplete="name"></label><label class="field">{a('العلامة التجارية', 'Brand')}<input name="{a('العلامة التجارية', 'Brand')}" required placeholder="{a('اسم المتجر', 'Store name')}" autocomplete="organization"></label></div>
      <div class="row2"><label class="field">{a('البريد الإلكتروني للعمل', 'Work email')}<input name="{a('البريد', 'Email')}" type="email" required placeholder="name@brand.com" dir="ltr" autocomplete="email"></label><label class="field">{a('الموقع الإلكتروني', 'Website')}<input name="{a('الموقع', 'Website')}" placeholder="brand.com" dir="ltr" autocomplete="url"></label></div>
      <div class="row2"><label class="field">{a('الأسواق المستهدفة', 'Target markets')}<select name="{a('الأسواق', 'Markets')}">{opt(markets)}</select></label><label class="field">{a('النموذج المفضّل', 'Preferred model')}<select name="{a('النموذج', 'Model')}">{opt(models)}</select></label></div>
      <label class="field">{a('هدفك الرئيسي', 'Main goal')}<textarea name="{a('الهدف', 'Goal')}" rows="3" placeholder="{a('مثال: عملاء جدد في السعودية خلال الجمعة البيضاء', 'e.g. new customers in Saudi Arabia over White Friday')}"></textarea></label>
      <button class="btn btn-primary" style="justify-content:center">{a('أرسل الطلب ←', 'Send request →')}</button>
      <small style="color:var(--muted)">{a('يفتح الزر تطبيق البريد برسالة جاهزة إلى', 'This opens your email app with a ready-to-send message to')} <a class="mail" href="mailto:{EMAIL}?subject={esc(subj)}">{EMAIL}</a>. {a('نستخدم بياناتك للرد عليك فقط.', 'We only use your details to reply to you.')}</small>
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
      <nav class="crumbs" aria-label="{a('مسار الصفحة', 'Breadcrumb')}" style="color:#B7BBD6"><a href="{L(lang, '/')}">{a('الرئيسية', 'Home')}</a> / <span aria-current="page">{a('الشراكات', 'For Brands')}</span></nav>
      <span class="eyebrow light">✦ {a('للعلامات التجارية والمتاجر', 'For brands & online stores')}</span>
      <h1>{a('مبيعات قابلة للقياس.<br>تدفع مقابل <span style="color:var(--saffron)">النتائج</span>.', 'Measurable sales.<br>You pay for <span style="color:var(--saffron)">results</span>.')}</h1>
      <p class="lead">{a('كوبون فريق متخصص في التسويق بالعمولة والأداء، ومنصة عروض رسمية للمتسوقين في الخليج والأسواق العالمية.', 'Kobon is a performance and affiliate marketing team with an official-offers platform for shoppers in the Gulf and international markets.')}</p>
      <div class="actions"><a class="btn btn-primary" href="#contact">{a('احجز مكالمة تعارف ←', 'Book an intro call →')}</a><a class="btn btn-outline-light" href="/media-kit.pdf">{a('الملف التعريفي (PDF)', 'Media kit (PDF)')}</a></div>
      <div class="facts"><span><b>{a('الدفع مقابل النتائج', 'Pay for results')}</b>CPS · CPA · {a('هجين', 'Hybrid')}</span><span><b>{a('الخليج ومصر والعالم', 'Gulf, Egypt & global')}</b>{a('أسواق خليجية ومصر وأسواق عالمية', 'GCC, Egypt + international')}</span><span><b>{a('بلغتين', 'Bilingual')}</b>{a('العربية والإنجليزية', 'Arabic & English')}</span></div>
    </div>
    {dashboard_svg(lang)}
  </div>
</section>
<section class="wrap founding" id="founding">
  <div class="box">
    <svg class="seal" viewBox="0 0 88 88" aria-hidden="true"><circle cx="44" cy="44" r="42" fill="#FFF6DD"/><circle cx="44" cy="44" r="34" fill="none" stroke="#E0A100" stroke-width="2" stroke-dasharray="3 5"/><path d="M44 22l6 13 14 2-10 10 2 14-12-7-12 7 2-14-10-10 14-2z" fill="#FFC233" stroke="#E0A100" stroke-width="1.5"/></svg>
    <div><h2 style="font-size:1.4rem">{a('برنامج الشركاء المؤسسين', 'Founding Partner Programme')}</h2><p>{a('مقاعد محدودة لأول العلامات التجارية: ظهور مميز في الصفحة الرئيسية وصفحات المواسم، وخطة حملة مخصصة، وتقرير أسبوعي من الفريق.', 'A limited number of places for our first brands: premium placement on the home and season pages, a tailored campaign plan and a weekly report from the team.')}</p></div>
    <a class="btn btn-primary" href="#contact">{a('قدّم علامتك', 'Apply now')}</a>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {section_head(a('خدماتنا', 'What we do'), a('كل ما تحتاجه حملتك في فريق واحد', 'Everything your campaign needs, in one team'), a('نخطّط وننفّذ ونقيس، ونُحاسَب على النتيجة.', 'We plan, launch and measure, and we’re accountable for results.'))}
    <div class="services">{svcs}</div>
  </div>
</section>
<section class="section" id="models" style="background:#fff;border-block:1px solid var(--line)">
  <div class="wrap">
    {section_head(a('نماذج التعاون', 'Collaboration models'), a('اختر النموذج المناسب لأهدافك', 'Pick the model that fits your goals'), '', 'mint')}
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
      <span class="eyebrow mint">{a('سلامة علامتك', 'Brand safety')}</span>
      <h2>{a('التزامات مكتوبة<br>مع كل شريك', 'Written commitments<br>with every partner')}</h2>
      <p class="lead">{a('سمعة علامتك تأتي أولًا، لذلك نعمل وفق قواعد واضحة في كل اتفاق.', 'Your reputation comes first, so every agreement runs on clear rules.')}</p>
    </div>
    <div class="rules">{rules}</div>
  </div>
</section>
<section class="section" id="contact" style="background:var(--ink);color:#fff">
  <div class="wrap split">
    <div style="display:grid;gap:1.2rem">
      <span class="eyebrow light">{a('تواصل معنا', 'Get in touch')}</span>
      <h2>{a('حدّثنا عن علامتك.<br>نرد خلال يوم عمل.', 'Tell us about your brand.<br>We reply within one business day.')}</h2>
      <p style="color:#C9CCE6;font-size:1.1rem">{a('أو راسلنا مباشرة على', 'Or email us directly at')} <a class="mail" style="color:#fff" href="mailto:{EMAIL}">{EMAIL}</a></p>
      <div class="faq" style="margin:1rem 0 0;max-width:none">{faq_html(PARTNER_FAQ[lang], True, True)}</div>
    </div>
    {partner_form(lang)}
  </div>
</section>'''
    title = a("للعلامات التجارية: تسويق بالعمولة في الخليج والأسواق العالمية | كوبون", "For Brands: affiliate marketing across the Gulf and global markets | Kobon")
    desc = a("كوبون فريق متخصص في التسويق بالعمولة والأداء في الخليج والأسواق العالمية. نحوّل عروضك الرسمية إلى مبيعات، وتدفع مقابل النتائج: CPS أو CPA أو نموذج هجين.",
             "Kobon is an affiliate and performance marketing team for the Gulf and global markets. We turn your official offers into sales, and you pay for results: CPS, CPA or hybrid.")
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("الشراكات", "For Brands"), "/partners/")]
    ld = [faq_ld(PARTNER_FAQ[lang]), {"@context": "https://schema.org", "@type": "Service", "name": a("التسويق بالعمولة والأداء للعلامات التجارية", "Affiliate & performance marketing for brands"),
          "provider": {"@type": "Organization", "name": NAME[lang], "url": DOMAIN + "/"}, "areaServed": ["SA", "AE", "KW", "QA", "BH", "OM", "Worldwide"], "serviceType": "Affiliate marketing"}]
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
        ("bg-coral", "#FF5A36", ("الرسمي فقط", "Official only"), ("لا ننشر عرضًا إلا إذا أصدره المتجر أو برنامج شريك معتمد.", "We only publish offers issued by the store or an approved partner programme.")),
        ("bg-mint", "#14B8A6", ("الشفافية في العمولة", "Open about commission"), ("نوضّح متى قد نحصل على عمولة، ولا يتغير سعرك.", "We tell you when we may earn a commission. Your price never changes.")),
        ("bg-saffron", "#E0A100", ("احترام وقتك", "Your time matters"), ("عروض أقل، ولكل عرض شروطه وتاريخ آخر تحقق.", "Fewer offers, each with its terms and last-checked date.")),
        ("bg-violet", "#6D5BFF", ("سلامة العلامة التجارية", "Brand safety"), ("لا إعلانات على أسماء العلامات، ولا أكواد مسرّبة، ولا ادعاءات مبالغ فيها.", "No brand-name bidding, no leaked codes, no inflated claims.")),
    ]
    pr = "".join(f'<article class="card"><span class="ic {bg}">{CHECK.format(s=30, c=c)}</span><h3>{t(lang, *h)}</h3><p>{t(lang, *p)}</p></article>' for bg, c, h, p in principles)
    skills = [
        ("التسويق بالعمولة", "Affiliate marketing", "إدارة برامج العمولة مع المتاجر والشبكات بروابط وأكواد قابلة للتتبع.", "Running commission programmes with stores and networks, with trackable links and codes."),
        ("السيو والمحتوى", "SEO & content", "صفحات وأدلة شراء بالعربية والإنجليزية تجيب عن أسئلة المتسوق.", "Arabic and English pages and buying guides that answer shoppers’ questions."),
        ("البريد والتنبيهات", "Email & alerts", "نشرة أسبوعية وتنبيهات موسمية بجدول واضح.", "A weekly email and seasonal alerts on a clear schedule."),
        ("تحليل الأداء", "Analytics", "قياس النقرات والطلبات والمبيعات من منصة التتبع نفسها.", "Clicks, orders and sales measured from the tracking platform itself."),
        ("إدارة حملات المواسم", "Seasonal campaigns", "خطط مبكرة للجمعة البيضاء ورمضان والعيد والأيام الوطنية.", "Early plans for White Friday, Ramadan, Eid and national days."),
        ("علاقات الشركاء", "Partner relations", "تواصل مباشر وتقارير أسبوعية لكل علامة نعمل معها.", "Direct contact and weekly reports for every brand we work with."),
    ]
    sk = "".join(f'<div class="vitem"><span class="n">{i+1}</span><div><h3>{t(lang, h1, h2)}</h3><p>{t(lang, p1, p2)}</p></div></div>' for i, (h1, h2, p1, p2) in enumerate(skills))
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("من نحن", "About"), "/about/")]
    body = page_hero(lang, crumbs, a("من نحن", "About us"),
                     a("فريق تسويق بالعمولة،<br>بمعيار <span class=\"hl\">العروض الرسمية</span>.", "Affiliate marketers<br>with an <span class=\"hl\">official-only</span> standard."),
                     a("نعمل مع المتاجر في الخليج والأسواق العالمية، وننشر فقط ما نستطيع التحقق منه.", "We work with stores across the Gulf and global markets, and only publish what we can verify."), team_svg(lang)) + f'''
<section class="section">
  <div class="wrap split">
    <div style="display:grid;gap:1.2rem"><span class="eyebrow mint">{a('قصتنا', 'Our story')}</span><h2>{a('لماذا أنشأنا كوبون', 'Why we built Kobon')}</h2></div>
    <div class="prose" style="margin:0">
      <p>{a('نحن فريق متخصص في التسويق بالعمولة، بخبرة في الخليج والأسواق العالمية. عملنا مع المتاجر الإلكترونية ورأينا المشكلة من الجهتين: متسوق يضيع وقته في أكواد لا تعمل، وعلامات تجارية تفقد ثقة عملائها بسبب مواقع تنشر أي شيء.', 'We’re an affiliate marketing team with experience across the Gulf and international markets. Working with online stores, we saw the problem from both sides: shoppers losing time on codes that don’t work, and brands losing trust to sites that will publish anything.')}</p>
      <p>{a('كوبون هو ما أردناه: عروض رسمية بمعيار واضح، يديرها فريق يعرف كيف تُبنى الحملات وتُقاس.', 'Kobon is our answer: official offers held to a clear standard, run by people who know how campaigns are built and measured.')}</p>
    </div>
  </div>
</section>
<section class="section" style="background:#fff;border-block:1px solid var(--line)">
  <div class="wrap">
    {section_head(a('مبادئنا', 'Our principles'), a('أربعة مبادئ ثابتة', 'Four principles we hold to'))}
    <div class="grid-4">{pr}</div>
  </div>
</section>
<section class="section">
  <div class="wrap verify">
    <div style="display:grid;gap:1.2rem"><span class="eyebrow">{a('كيف نعمل', 'How we work')}</span><h2>{a('ما يتقنه فريقنا', 'What the team does')}</h2><p class="lead">{a('كل عرض وكل حملة يمرّان على فريق متخصص في التسويق بالأداء.', 'Every offer and campaign is handled by performance-marketing specialists.')}</p></div>
    <div class="vlist">{sk}</div>
  </div>
</section>
<section class="wrap two">
  <div class="path-card dark"><span class="eyebrow light">{a('للعلامات التجارية', 'For brands')}</span><h2 style="font-size:1.7rem">{a('لنعمل معًا', 'Let’s work together')}</h2><p>{a('عمولة على المبيعات، وقواعد واضحة لسلامة علامتك، وتقارير أسبوعية.', 'Commission on sales, clear brand-safety rules and weekly reports.')}</p><div class="actions"><a class="btn btn-primary" href="{L(lang, '/partners/')}">{a('اعرف المزيد ←', 'Learn more →')}</a></div></div>
  <div class="path-card"><span class="eyebrow mint">{a('للمتسوقين', 'For shoppers')}</span><h2 style="font-size:1.7rem">{a('اشترك في التنبيهات', 'Get offer alerts')}</h2><p>{a('رسالة أسبوعية واحدة بأفضل العروض الرسمية.', 'One weekly email with the best official offers.')}</p><div class="actions"><a class="btn btn-ghost" href="{L(lang, '/#alerts')}">{a('اشترك', 'Subscribe')}</a></div></div>
</section>'''
    render(lang, "/about/", a("من نحن: فريق تسويق بالعمولة في الخليج والأسواق العالمية | كوبون", "About Kobon: an affiliate marketing team for the Gulf and beyond | Kobon"),
           a("تعرّف على فريق كوبون المتخصص في التسويق بالعمولة في الخليج والأسواق العالمية، ومبادئنا: العروض الرسمية فقط، والشفافية، واحترام وقتك، وسلامة العلامة التجارية.",
             "Meet the team behind Kobon, affiliate marketers working across the Gulf and global markets, and the principles we hold to: official offers only, transparency, your time and brand safety."),
           body, "about", [{"@context": "https://schema.org", "@type": "AboutPage", "name": a("من نحن", "About us"), "url": abs_url(lang, "/about/")}], crumbs)


def offer_card_svg(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    return f'''<div style="display:grid;gap:1.2rem">
  <div class="ticket">
    <div class="main">
      <div style="display:flex;gap:.5rem;flex-wrap:wrap"><span class="badge ok">✓ {a('مصدر رسمي', 'Official source')}</span><span class="badge warn">{a('ينتهي خلال 5 أيام', 'Ends in 5 days')}</span></div>
      <h3>{a('خصم 20% على الطلب الأول', '20% off your first order')}</h3>
      <p style="color:var(--ink-soft);font-size:.92rem">{a('متجر أزياء · السعودية والإمارات', 'Fashion store · Saudi Arabia & UAE')}</p>
      <div class="meta"><span>{a('الحد الأدنى للشراء', 'Min. spend')}<b>{a('150 ر.س', 'SAR 150')}</b></span><span>{a('الحد الأقصى للخصم', 'Max. discount')}<b>{a('100 ر.س', 'SAR 100')}</b></span><span>{a('آخر تحقق', 'Last checked')}<b>{a('اليوم', 'Today')}</b></span></div>
    </div>
    <div class="side"><div><b>20%</b><div style="font-size:.9rem;margin-top:.4rem">{a('اعرض الكود', 'Show code')}</div></div></div>
  </div>
  <p class="note" style="text-align:center"><span class="tag-ex">{a('مثال توضيحي', 'Illustrative example')}</span> {a('وليس عرضًا حقيقيًا', 'Not a real offer')}</p>
  <ol class="anno">
    <li><span class="n">1</span><span>{a('<b>مصدر رسمي</b>: العرض صادر عن المتجر أو برنامج شريك معتمد.', '<b>Official source</b>: the offer comes from the store or an approved programme.')}</span></li>
    <li><span class="n">2</span><span>{a('<b>المدة المتبقية</b>: تاريخ الانتهاء كما أعلنه المتجر.', '<b>Time left</b>: the expiry date the store announced.')}</span></li>
    <li><span class="n">3</span><span>{a('<b>الشروط</b>: الحد الأدنى للشراء والحد الأقصى للخصم والدول المشمولة.', '<b>Terms</b>: minimum spend, maximum discount and countries.')}</span></li>
    <li><span class="n">4</span><span>{a('<b>آخر تحقق</b>: آخر مرة راجع فيها الفريق العرض.', '<b>Last checked</b>: when the team last verified the offer.')}</span></li>
  </ol>
</div>'''


def build_how(lang: str) -> None:
    a = lambda ar, en: t(lang, ar, en)
    examples = [
        ("مثال: كود من صفحة العروض الرسمية للمتجر، أو من لوحة شبكة التسويق بالعمولة التي يستخدمها.", "Example: a code from the store’s official offers page, or from the dashboard of its affiliate network."),
        ("مثال: «الحد الأدنى 150 ر.س، أقصى خصم 100 ر.س، لا يشمل الإلكترونيات».", "Example: “Minimum SAR 150, maximum discount SAR 100, electronics excluded.”"),
        ("مثال: نضيف منتجًا للسلة ونتأكد أن الخصم يظهر قبل الدفع.", "Example: we add a product to the basket and check the discount appears before payment."),
        ("مثال: إذا أوقف المتجر العرض نحذفه فورًا، ونحدّث تاريخ آخر تحقق في كل مراجعة.", "Example: if the store ends the offer we take it down, and we update the last-checked date on every review."),
    ]
    std = "".join(
        f'<div class="vitem"><span class="n">{i+1}</span><div><h3>{t(lang, s[0], s[1])}</h3><p>{t(lang, s[2], s[3])}</p><p class="note" style="margin-top:.3rem">{t(lang, *examples[i])}</p></div></div>' for i, s in enumerate(STANDARD)
    )
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("كيف نعمل", "How it works"), "/how-it-works/")]
    body = page_hero(lang, crumbs, a("كيف نعمل", "How it works"), a("كيف يعمل كوبون،<br>ولماذا تثق <span class=\"hl\">بكل عرض</span>.", "How Kobon works,<br>and why you can trust <span class=\"hl\">every offer</span>."),
                     a("ثلاث خطوات للمتسوق، وأربع مراحل تحقق قبل نشر أي عرض، على كل متجر خليجي أو عالمي.", "Three steps for shoppers, and four checks before any offer goes live, for every store, local or international.")) + f'''
<section class="section">
  <div class="wrap">
    {section_head(a('رحلة المتسوق', 'The shopper journey'), a('ثلاث خطوات للتوفير', 'Three steps to save'))}
    {steps_html(lang)}
  </div>
</section>
<section class="section" id="standard" style="background:#fff;border-block:1px solid var(--line)">
  <div class="wrap verify">
    <div style="display:grid;gap:1.2rem"><span class="eyebrow mint">{a('معيار كوبون', 'The Kobon standard')}</span><h2>{a('أربع خطوات<br>قبل نشر أي عرض', 'Four checks<br>before any offer goes live')}</h2><p class="lead">{a('العرض الذي لا يجتاز الخطوات الأربع لا يُنشر.', 'An offer that fails any check doesn’t go live.')}</p></div>
    <div class="vlist">{std}</div>
  </div>
</section>
<section class="section">
  <div class="wrap verify">
    <div style="display:grid;gap:1.2rem"><span class="eyebrow">{a('اقرأ البطاقة', 'Read the card')}</span><h2>{a('كيف تقرأ بطاقة العرض', 'How to read an offer card')}</h2><p class="lead">{a('المصدر والشروط والمدة وتاريخ آخر تحقق في بطاقة واحدة.', 'Source, terms, time left and last-checked date, all on one card.')}</p></div>
    {offer_card_svg(lang)}
  </div>
</section>
<section class="section" id="commission" style="padding-top:0">
  <div class="wrap two">
    <div class="path-card"><span class="eyebrow mint">{a('كيف نربح', 'How we earn money')}</span><h2 style="font-size:1.6rem">{a('الإفصاح عن العمولة', 'Commission disclosure')}</h2><p>{a('قد يدفع لنا المتجر عمولة عند الشراء عبر روابطنا. لا يتغير سعرك، ولا تؤثر العمولة في ترتيب العروض إلا في المساحات المعلَّمة «مُموَّل».', 'A store may pay us a commission when you buy through our links. Your price stays the same, and commission never affects ranking outside spots marked “Sponsored”.')}</p><div class="actions"><a class="link" href="{L(lang, '/affiliate-disclosure/')}">{a('صفحة الإفصاح الكاملة ←', 'Full disclosure →')}</a></div></div>
    <div class="path-card dark"><span class="eyebrow light">{a('الكود لا يعمل؟', 'Code not working?')}</span><h2 style="font-size:1.6rem">{a('أبلغنا عن كود لا يعمل', 'Report a broken code')}</h2><p>{a('أرسل اسم المتجر والكود، وسنراجعه خلال يوم عمل.', 'Send us the store and the code, and we’ll check it within one business day.')}</p><div class="actions"><a class="btn btn-primary" href="mailto:{EMAIL}?subject={esc(a('كود لا يعمل', 'Broken code'))}">{a('أبلغنا', 'Report it')}</a></div></div>
  </div>
</section>'''
    faq = [(a("هل تضمنون أن كل كود يعمل؟", "Do you guarantee every code works?"), a("لا يمكن لأحد ضمان ذلك، فالشروط تختلف حسب السلة والدولة والحساب. لكننا ننشر الشروط كاملة ونحدّث تاريخ آخر تحقق.", "No one can, because terms vary by basket, country and account. What we do guarantee is full terms and an up-to-date last-checked date."))]
    render(lang, "/how-it-works/", a("كيف نعمل ومعيار التحقق من العروض | كوبون", "How it works & our verification standard | Kobon"),
           a("كيف يعمل كوبون: ثلاث خطوات للمتسوق، وأربع مراحل تحقق لكل عرض (المصدر، الشروط، التجربة، المتابعة)، وكيف نربح بشفافية.",
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
                     a("اختر الطريق المناسب لطلبك. نرد خلال يوم عمل.", "Choose the right path for your request. We reply within one business day."), env) + f'''
<section class="section">
  <div class="wrap two">
    <div class="path-card"><span class="eyebrow mint">{a('للمتسوقين', 'For shoppers')}</span><h2 style="font-size:1.7rem">{a('سؤال عن عرض أو كود؟', 'A question about an offer or code?')}</h2><p>{a('أرسل اسم المتجر والكود ودولتك، وسنراجعه خلال يوم عمل.', 'Send us the store, the code and your country, and we’ll check it within one business day.')}</p><div class="actions"><a class="btn btn-primary" href="mailto:{EMAIL}?subject={esc(a('سؤال متسوق', 'Shopper question'))}">{a('راسلنا', 'Email us')}</a></div><p class="note">{a('البريد:', 'Email:')} <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></p></div>
    <div class="path-card dark"><span class="eyebrow light">{a('للعلامات التجارية والوكالات', 'For brands & agencies')}</span><h2 style="font-size:1.7rem">{a('شراكة أو حملة؟', 'A partnership or a campaign?')}</h2><p>{a('حدّثنا عن علامتك وأسواقك وهدفك، ونعود إليك بخطوات واضحة خلال يوم عمل.', 'Tell us about your brand, markets and goals, and we’ll come back with clear next steps within one business day.')}</p><div class="actions"><a class="btn btn-primary" href="{L(lang, '/partners/#contact')}">{a('طلب شراكة ←', 'Partnership request →')}</a><a class="btn btn-outline-light mail" href="mailto:{EMAIL}">{EMAIL}</a></div></div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap facts-grid">
    <div class="fact"><small>{a('وقت الرد', 'Response time')}</small><b>{a('خلال يوم عمل', 'Within one business day')}</b></div>
    <div class="fact"><small>{a('اللغات', 'Languages')}</small><b>{a('العربية والإنجليزية', 'Arabic & English')}</b></div>
    <div class="fact"><small>{a('الأسواق', 'Markets')}</small><b>{a('الخليج والعالم', 'The Gulf & worldwide')}</b></div>
  </div>
</section>'''
    ld = [{"@context": "https://schema.org", "@type": "ContactPage", "name": a("تواصل معنا", "Contact"), "url": abs_url(lang, "/contact/")}]
    render(lang, "/contact/", a("تواصل معنا | كوبون", "Contact us | Kobon"),
           a("تواصل مع كوبون: للمتسوقين بخصوص عرض أو كود، وللعلامات التجارية والوكالات بخصوص الشراكات. نرد خلال يوم عمل على partners@kobon.is-a.si.",
             "Contact Kobon: shoppers with a question about an offer or code, and brands or agencies about partnerships and campaigns. We reply within one business day at partners@kobon.is-a.si."),
           body, "", ld, crumbs)


LEGAL = {
    "privacy": {
        "ar": ("الخصوصية وملفات تعريف الارتباط", "سياسة الخصوصية وملفات تعريف الارتباط في كوبون.", """
<p>الموقع صفحات ثابتة. لا نطلب إنشاء حساب للتصفح، ولا نبيع بياناتك.</p>
<h2>ملفات تعريف الارتباط</h2>
<p>لا نضع ملفات تعريف ارتباط للتتبع أو للإعلانات. نستخدم Cloudflare Web Analytics لقياس عدد الزيارات والصفحات الأكثر قراءة بشكل إجمالي، وهي أداة لا تستخدم ملفات تعريف الارتباط ولا تتتبعك عبر المواقع.</p>
<h2>النماذج والبريد</h2>
<p>نموذج الشراكة ونموذج التنبيهات لا يرسلان بياناتك إلى خادم. يفتحان تطبيق البريد لديك برسالة جاهزة، وأنت من يقرر إرسالها. نستخدم ما تصلنا به من بيانات للرد عليك فقط.</p>
<h2>روابط المتاجر</h2>
<p>قد تكون بعض الروابط روابط عمولة. عند الضغط عليها تنتقل إلى متجر خارجي له سياسة خصوصية خاصة به. راجع <a href="/affiliate-disclosure/">الإفصاح عن العمولة</a> و<a href="/terms/">الشروط</a>.</p>
<h2>التواصل</h2>
<p>للاستفسارات: <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></p>"""),
        "en": ("Privacy & cookies", "Kobon’s privacy and cookies policy.", """
<p>This is a static website. You don’t need an account to browse, and we don’t sell your data.</p>
<h2>Cookies</h2>
<p>We don’t set tracking or advertising cookies. We use Cloudflare Web Analytics to count visits and see which pages are read most, in aggregate. It doesn’t use cookies or track you across sites.</p>
<h2>Forms and email</h2>
<p>The partnership and alerts forms don’t send your data to a server. They open your email app with a ready message, and you decide whether to send it. We only use what you send us to reply to you.</p>
<h2>Store links</h2>
<p>Some links may be affiliate links. Clicking them takes you to an external store with its own privacy policy. See the <a href="/en/affiliate-disclosure/">affiliate disclosure</a> and <a href="/en/terms/">terms</a>.</p>
<h2>Contact</h2>
<p>Questions: <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a></p>"""),
    },
    "terms": {
        "ar": ("الشروط", "شروط استخدام موقع كوبون.", """
<p>باستخدامك موقع كوبون فأنت توافق على هذه الشروط. يقدّم الموقع معلومات عن العروض وأكواد الخصم بشكل مستقل، ولا يبيع المنتجات مباشرة.</p>
<h2>صلاحية العروض</h2>
<p>نراجع العروض وفق <a href="/how-it-works/#standard">معيار كوبون</a> ونحدّث تاريخ آخر تحقق، لكن لا يمكن ضمان أن يعمل كل كود لكل مستخدم في كل وقت. تختلف الشروط حسب السلة والدولة والحساب. قرار الشراء مسؤوليتك.</p>
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
<p>We review offers under <a href="/en/how-it-works/#standard">the Kobon standard</a> and keep last-checked dates current, but no one can guarantee every code works for every shopper at all times. Terms vary by basket, country and account. Buying is your decision.</p>
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
        "ar": ("الإفصاح عن العمولة", "كيف يربح كوبون: الإفصاح عن روابط التسويق بالعمولة.", """
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
    return f'<a class="btn btn-primary" href="{L(lang, "/#alerts")}">{t(lang, "اشترك في التنبيهات", "Get offer alerts")}</a><a class="btn btn-ghost" href="{L(lang, "/partners/")}">{t(lang, "للعلامات التجارية", "For brands")}</a>'


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
        a("نضيف المتجر بعد اعتماد برنامج شريك رسمي معه، لتكون كل العروض من مصدرها. اشترك ليصلك أول عرض فور نشره.", "We only list a store once an official partner programme with it is approved, so every offer here comes from its source. Subscribe to hear about the first offer as soon as it’s live."),
        brand_cta_actions(lang))
    search = f'''<form class="search js-filter" role="search" style="margin-top:.4rem"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#5E6380" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="site-q" name="q" aria-label="{a('ابحث عن متجر أو فئة', 'Search a store or category')}" placeholder="{a('ابحث عن متجر أو فئة…', 'Search a store or category…')}"></form>'''
    body = page_hero(lang, crumbs, a("المتاجر", "Stores"), a("متاجر بعروض <span class=\"hl\">رسمية فقط</span>", "Stores with <span class=\"hl\">official offers only</span>"),
                     a("متاجر خليجية وعالمية ببرامج شركاء رسمية، ولكل عرض مصدره وشروطه وتاريخ آخر تحقق.", "Gulf and international stores with official partner programmes. Every offer shows its source, terms and last-checked date."), "", extra=search) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:2.5rem">
  <p id="search-empty" class="note" hidden data-msg="{a('لا توجد نتائج مطابقة بعد. جرّب فئة أخرى.', 'No matches yet. Try another category.')}"></p>
  {('<div class="store-grid" id="store-grid">' + cards + '</div>') if stores else empty}
  <div style="display:grid;gap:1.2rem"><h2 style="font-size:1.6rem">{a('تصفّح حسب الفئة', 'Browse by category')}</h2><div class="cats" id="cat-grid">{cat_cards}</div></div>
</div></section>'''
    render(lang, "/stores/", a("المتاجر: كوبونات رسمية من متاجر الخليج والعالم | كوبون", "Stores: official coupons from Gulf and international stores | Kobon"),
           a("متاجر خليجية وعالمية على كوبون، نضيفها بعد اعتماد برنامج شريك رسمي، مع مصدر كل عرض وشروطه.", "Gulf and international stores on Kobon, listed only once an official partner programme is approved, with the source and terms of every offer."),
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
<div class="meta"><span>{a('الحد الأدنى للشراء', 'Min. spend')}<b>{esc(o.get('min_' + lang, '—'))}</b></span><span>{a('الحد الأقصى للخصم', 'Max. discount')}<b>{esc(o.get('max_' + lang, '—'))}</b></span><span>{a('آخر تحقق', 'Last checked')}<b>{esc(o.get('verified_date', ''))}</b></span></div></div>
<div class="side"><div><b>{esc(o.get('discount', '%'))}</b><button class="btn btn-light" data-copy data-code="{esc(o['code'])}" data-done="{a('تم النسخ', 'Copied')}">{esc(o['code'])}</button></div></div></div>''')
    body = page_hero(lang, crumbs, esc(c.get("name_" + lang, "")), esc(s["name_" + lang]), esc(s["description_" + lang]), cat_icon(s["category"], 160)) + \
        f'<section class="section"><div class="wrap" style="display:grid;gap:1.5rem">{"".join(offers) or empty_block(lang, a("لا توجد عروض نشطة الآن", "No active offers right now"), a("نضيف العروض الرسمية فور صدورها من المتجر.", "We add official offers as soon as the store releases them."), brand_cta_actions(lang))}</div></section>'
    render(lang, f"/stores/{s['slug']}/", f"{s['name_' + lang]} | {NAME[lang]}", s["description_" + lang], body, "stores", None, crumbs)


def build_categories(lang: str, cats: list[dict], stores: list[dict]) -> None:
    a = lambda ar, en: t(lang, ar, en)
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("الفئات", "Categories"), "/categories/")]
    body = page_hero(lang, crumbs, a("الفئات", "Categories"), a("تسوّق حسب اهتمامك", "Shop by interest"),
                     a("ست فئات تغطي أهم مشتريات المتسوق من المتاجر الخليجية والعالمية، بعروض رسمية فقط.", "Six categories covering what shoppers buy most from Gulf and international stores. Official offers only.")) + \
        f'<section class="section"><div class="wrap">{cats_html(lang, cats)}</div></section>'
    render(lang, "/categories/", a("فئات الكوبونات والعروض الرسمية | كوبون", "Coupon & deal categories | Kobon"),
           a("تصفّح كوبونات وعروض رسمية حسب الفئة: أزياء، جمال وعناية، إلكترونيات، سفر، المنزل، البقالة والطعام.", "Browse Kobon’s official offers by category: fashion, beauty, electronics, travel, home, and groceries & food."),
           body, "categories", None, crumbs, noindex=not stores)
    for c in cats:
        cs = [s for s in stores if s["category"] == c["slug"]]
        cr = crumbs + [(c["name_" + lang], f"/categories/{c['slug']}/")]
        others = "".join(f'<a href="{L(lang, "/categories/" + o["slug"] + "/")}">{esc(o["name_" + lang])}</a>' for o in cats if o["slug"] != c["slug"])
        tips = "".join(f"<li>{esc(x)}</li>" for x in c["tips_" + lang])
        content = ('<div class="store-grid">' + "".join(store_card(lang, s, {c["slug"]: c}) for s in cs) + "</div>") if cs else empty_block(
            lang, a("العروض الرسمية لهذه الفئة قريبًا", "Official offers for this category are coming soon"),
            a("ننشر عروض هذه الفئة فور اعتماد برامج الشركاء الرسمية مع متاجرها. اشترك ليصلك أول عرض.", "Offers appear here once official partner programmes with stores in this category are approved. Subscribe to hear first."),
            brand_cta_actions(lang), f'<svg class="big-ic" viewBox="0 0 56 56" aria-hidden="true">{CAT_ICON[c["slug"]]}</svg>')
        body = page_hero(lang, cr, a("فئة", "Category"), esc(c["name_" + lang]), esc(c["description_" + lang]), cat_icon(c["slug"], 180).replace("<svg ", '<svg class="art" ', 1)) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:2.5rem">
  {content}
  <div class="split" style="align-items:start"><div style="display:grid;gap:1rem"><span class="eyebrow mint">{a('نصائح شراء', 'Buying tips')}</span><h2 style="font-size:1.6rem">{a('قبل أن تشتري', 'Before you buy')}</h2></div><ul class="prose" style="margin:0">{tips}</ul></div>
  {related_guides_html(lang, CATEGORY_GUIDES.get(c["slug"], []))}
  <div style="display:grid;gap:1rem"><h2 style="font-size:1.3rem">{a('فئات أخرى', 'Other categories')}</h2><div class="tiles">{others}</div></div>
</div></section>'''
        render(lang, f"/categories/{c['slug']}/", f"{c['name_' + lang]}: {a('كوبونات وعروض رسمية', 'official coupons & deals')} | {NAME[lang]}", c["description_" + lang], body, "categories", None, cr, noindex=not cs)


def build_countries(lang: str, stores: list[dict], seasons: list[dict]) -> None:
    a = lambda ar, en: t(lang, ar, en)
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("الأسواق", "Markets"), "/countries/")]
    body = page_hero(lang, crumbs, a("الأسواق", "Markets"), a("من الخليج <span class=\"hl\">إلى العالم</span>", "From the Gulf <span class=\"hl\">to the world</span>"),
                     a("اختر بلدك أو المتاجر العالمية لترى العروض الصالحة لك فقط، بالعملة وطرق الشحن المناسبة.", "Pick your country, or international stores, to see only the offers that apply to you, with the right currency and shipping.")) + \
        f'<section class="section"><div class="wrap">{countries_html(lang)}</div></section>'
    render(lang, "/countries/", a("العروض حسب السوق: الخليج والمتاجر العالمية | كوبون", "Offers by market: the Gulf and international stores | Kobon"),
           a("عروض رسمية للسعودية والإمارات والكويت وقطر والبحرين وعُمان، ومن المتاجر العالمية التي تشحن إلى الخليج والعالم.", "Official offers for Saudi Arabia, the UAE, Kuwait, Qatar, Bahrain and Oman, plus international stores that ship to the Gulf and worldwide."),
           body, "", None, crumbs, noindex=not stores)
    for slug, n_ar, n_en, cur_ar, cur_en in COUNTRIES:
        name = n_ar if lang == "ar" else n_en
        g = slug == "global"
        cr = crumbs + [(name, f"/countries/{slug}/")]
        cs = [s for s in stores if slug in s.get("countries", [])]
        others = "".join(f'<a href="{L(lang, "/countries/" + o[0] + "/")}">{o[1] if lang == "ar" else o[2]}</a>' for o in COUNTRIES if o[0] != slug)
        if g:
            empty_t = a("عروض المتاجر العالمية قريبًا", "International store offers are coming soon")
            empty_p = a("نضيف عروض المتاجر العالمية فور اعتماد برامج الشركاء الرسمية، مع توضيح الدول التي تشحن إليها وعملة الدفع. اشترك ليصلك أول عرض.", "We add international store offers as soon as official partner programmes are approved, with the countries they ship to and the checkout currency. Subscribe to hear first.")
            h1 = a("عروض المتاجر العالمية", "International store offers")
            lead = a("كوبونات رسمية من متاجر عالمية تشحن إلى الخليج ودول العالم، مع الدول المشمولة وعملة الدفع وتاريخ آخر تحقق.", "Official coupons from international stores that ship to the Gulf and worldwide, with eligible countries, checkout currency and last-checked date.")
            title = a("كوبونات وعروض رسمية من المتاجر العالمية | كوبون", "Official coupons from international stores | Kobon")
            desc = a("كوبونات وأكواد خصم رسمية من متاجر عالمية تشحن إلى الخليج والعالم، مع شروط كل عرض وتاريخ آخر تحقق.", "Official coupons and discount codes from international stores that ship to the Gulf and worldwide, with full terms and a last-checked date.")
            other_h = a("الأسواق الخليجية", "Gulf markets")
        else:
            empty_t = a(f"العروض الرسمية في {name} قريبًا", f"Official offers in {name} are coming soon")
            empty_p = a(f"نعرض هنا العروض الصالحة في {name} فقط، بالعملة المحلية ({cur_ar}) وطرق الشحن المتاحة. اشترك ليصلك أول عرض.", f"This page will only list offers valid in {name}, priced in {cur_en} with local shipping options. Subscribe to hear first.")
            h1 = a(f"عروض رسمية في {name}", f"Official offers in {name}")
            lead = a(f"عروض المتاجر المحلية والعالمية الصالحة في {name}، بمصدرها وشروطها وتاريخ آخر تحقق، وبالعملة المحلية ({cur_ar}).", f"Local and international store offers valid in {name}, each with its source, terms and last-checked date, in {cur_en}.")
            title = a(f"كوبونات وأكواد خصم رسمية في {name} | كوبون", f"Official coupons and discount codes in {name} | Kobon")
            desc = a(f"كوبونات وعروض رسمية فقط في {name}، من المتاجر المحلية والعالمية، مع شروط كل عرض وتاريخ آخر تحقق.", f"Official-only coupons and deals in {name}, from local and international stores, with full terms and a last-checked date.")
            other_h = a("أسواق أخرى", "Other markets")
        content = ('<div class="store-grid">' + "".join(store_card(lang, s, {}) for s in cs) + "</div>") if cs else empty_block(
            lang, empty_t, empty_p, brand_cta_actions(lang), flag(slug, 96, "flag big-ic"))
        upcoming = [s for s in seasons if season_status(s) != "past" and (not s.get("countries") or (not g and slug in s["countries"]))]
        upcoming.sort(key=lambda s: s["start"])
        body = page_hero(lang, cr, a("السوق", "Market") if g else a("دولة", "Country"), h1, lead, flag(slug, 180, "flag art")) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:2.5rem">
  {content}
  {global_extra(lang) if g else ""}
  <div style="display:grid;gap:1.2rem"><h2 style="font-size:1.6rem">{a('المواسم القادمة', 'Upcoming seasons')}</h2><div class="seasons">{"".join(season_card(lang, s) for s in upcoming[:4])}</div></div>
  <div style="display:grid;gap:1rem"><h2 style="font-size:1.3rem">{other_h}</h2><div class="tiles">{others}</div></div>
</div></section>'''
        render(lang, f"/countries/{slug}/", title, desc, body, "", None, cr, noindex=not (cs or g))


def build_seasons(lang: str, seasons: list[dict]) -> None:
    a = lambda ar, en: t(lang, ar, en)
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("المواسم", "Seasons"), "/seasons/")]
    order = sorted(seasons, key=lambda s: ({"live": 0, "soon": 1, "past": 2}[season_status(s)], s["start"]))
    body = page_hero(lang, crumbs, a("تقويم المواسم", "Season calendar"), a("استعد للموسم <span class=\"hl\">قبل أن يبدأ</span>", "Get ready <span class=\"hl\">before the season starts</span>"),
                     a("لكل موسم كبير صفحة بمواعيده المتوقعة ونصائح الشراء، والعروض الرسمية فور صدورها.", "Every major season gets its own page: expected dates, buying tips and official offers the moment they drop.")) + \
        f'<section class="section"><div class="wrap"><h2 class="sr-only">{a("مواسم السنة", "This year’s seasons")}</h2><div class="seasons">{"".join(season_card(lang, s) for s in order)}</div><p class="note" style="margin-top:1.5rem;text-align:center">{a("التواريخ تقديرية وقد تختلف حسب الدولة والمتجر، والمواسم الهجرية حسب رؤية الهلال.", "Dates are estimates and can vary by country and store. Hijri seasons depend on the moon sighting.")}</p></div></section>'
    render(lang, "/seasons/", a("تقويم مواسم التخفيضات في الخليج والمتاجر العالمية | كوبون", "Sale season calendar for the Gulf and global stores | Kobon"),
           a("مواعيد الجمعة البيضاء و11.11 ورمضان وعيد الفطر ويوم التأسيس واليوم الوطني، مع نصائح الشراء والعروض الرسمية فور صدورها.", "Dates for White Friday, 11.11, Ramadan, Eid al-Fitr, Founding Day and National Day, with buying tips and official offers as soon as they’re out."),
           body, "seasons", None, crumbs, noindex=True)
    for s in seasons:
        st = season_status(s)
        cr = crumbs + [(s["name_" + lang], f"/seasons/{s['slug']}/")]
        badge = season_tag(lang, s, page=True)
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
                              a("لا ننشر توقعات ولا أكوادًا غير مؤكدة. اشترك ليصلك كل عرض رسمي لهذا الموسم.", "No guesses, no unconfirmed codes. Subscribe to get every official offer this season."), brand_cta_actions(lang))
        body = page_hero(lang, cr, a("موسم", "Season"), esc(s["name_" + lang]), esc(s["blurb_" + lang]), art, extra=badge) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:2.5rem">
  {facts}
  {content}
  <div class="split" style="align-items:start"><div style="display:grid;gap:1rem"><span class="eyebrow mint">{a('نصائح الموسم', 'Season tips')}</span><h2 style="font-size:1.6rem">{a('كيف تستعد', 'How to get ready')}</h2></div><ul class="prose" style="margin:0">{tips}</ul></div>
  {related_guides_html(lang, [SEASON_GUIDE[s["slug"]]] if s["slug"] in SEASON_GUIDE else [], a("الدليل الكامل لهذا الموسم", "The full guide for this season"))}
</div></section>'''
        render(lang, f"/seasons/{s['slug']}/", a(f"{s['name_ar']}: المواعيد والعروض الرسمية | كوبون", f"{s['name_en']}: dates and official offers | Kobon"),
               s["blurb_" + lang], body, "seasons", None, cr, noindex=True)


def global_extra(lang: str) -> str:
    a = lambda ar, en: t(lang, ar, en)
    return f'''<div class="split" style="align-items:start">
  <div style="display:grid;gap:1rem"><span class="eyebrow mint">{a('قبل الشراء من الخارج', 'Before you buy from abroad')}</span><h2 style="font-size:1.6rem">{a('احسب السعر النهائي، لا سعر المنتج', 'Work out the landed cost, not the sticker price')}</h2><p>{a('إعفاء الشحنة من الرسوم الجمركية لا يعني إعفاءها من ضريبة القيمة المضافة. هذه أهم الحدود في السعودية والإمارات:', 'A parcel exempt from customs duty isn’t exempt from VAT. The key thresholds in Saudi Arabia and the UAE:')}</p></div>
  <div class="prose"><table><thead><tr><th>{a('الدولة', 'Country')}</th><th>{a('إعفاء الرسوم الجمركية', 'Customs duty exemption')}</th><th>{a('ضريبة القيمة المضافة', 'VAT')}</th></tr></thead><tbody>
  <tr><td>{a('السعودية', 'Saudi Arabia')}</td><td>{a('المشتريات الشخصية أقل من 1,000 ريال (شاملة الشحن والتأمين)، مع رسم بيان 15 ريالًا', 'Personal purchases under SAR 1,000 incl. shipping and insurance; SAR 15 declaration fee')}</td><td>15%</td></tr>
  <tr><td>{a('الإمارات', 'UAE')}</td><td>{a('سلع التجارة الإلكترونية العابرة للحدود حتى 1,000 درهم في دبي، اعتبارًا من 3 أغسطس 2026، مع استثناءات', 'Cross-border e-commerce goods up to AED 1,000 in Dubai, from 3 August 2026, with exclusions')}</td><td>5%</td></tr>
  </tbody></table>
  <ul><li>{a('ابحث عن خيار «شامل الرسوم والضرائب» عند الدفع.', 'Look for a “duties and taxes included” option at checkout.')}</li><li>{a('لا تقسّم الطلب للبقاء تحت الحد.', 'Don’t split an order to stay under a threshold.')}</li><li>{a('اقرأ سياسة الإرجاع الدولية قبل الشراء.', 'Read the international return policy before you buy.')}</li></ul>
  <p class="note">{a('المصادر: هيئة الزكاة والضريبة والجمارك، وجمارك دبي. التفاصيل الكاملة في الدليل أدناه.', 'Sources: ZATCA and Dubai Customs. Full details in the guide below.')}</p></div>
</div>
{related_guides_html(lang, ["global-shipping-customs", "gcc-vat-prices", "11-11-gulf"], a("أدلة للتسوق من المتاجر العالمية", "Guides for shopping internationally"))}'''

GUIDES: list[dict] = []
GUIDES.append({
"slug": "white-friday-2026",
"updated": "2026-11-09",
"title_ar": "الجمعة البيضاء 2026 في السعودية والإمارات: المواعيد وكيف تستعد",
"title_en": "White Friday 2026 in Saudi Arabia and the UAE: dates and how to prepare",
"desc_ar": "متى تبدأ الجمعة البيضاء 2026؟ ما نعرفه عن مواعيد أمازون ونون، وكيف تجهّز قائمتك وتتحقق من الخصم وترخيصه قبل الشراء.",
"desc_en": "When does White Friday 2026 start? What we know about Amazon and noon dates, and how to prepare your list and check a discount before you buy.",
"tag_ar": "مواسم", "tag_en": "Seasons",
"sources": [
 ("https://sell.amazon.sa/deals-and-coupons", "Amazon.sa: White Friday deals for sellers (event timing)"),
 ("https://en.lanatime.com/lifestyle/shopping/amazon-uae-reveals-massive-white-friday-sale-dates-2025-11-19/", "Lana Time: Amazon UAE White Friday 2025 dates"),
 ("https://www.khaleejtimes.com/uae/black-white-yellow-green-friday-sales-explainer", "Khaleej Times: UAE Black, White, Yellow and Green Friday explained"),
 ("https://mc.gov.sa/Pages/dvs.aspx", "Saudi Ministry of Commerce: document verification service"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li>الجمعة السوداء هذا العام توافق <b>الجمعة 27 نوفمبر 2026</b>، والاثنين الإلكتروني (Cyber Monday) يوافق 30 نوفمبر.</li>
<li>حتى تاريخ كتابة هذا الدليل لم تعلن أمازون السعودية والإمارات ولا نون مواعيد 2026 الرسمية.</li>
<li>في 2025 امتدت تخفيضات أمازون الإمارات من 20 إلى 30 نوفمبر، وامتدت تخفيضات أمازون السعودية من 21 إلى 30 نوفمبر.</li>
<li>جهّز قائمتك وسجّل الأسعار الحالية من الآن، حتى تعرف قيمة الخصم الحقيقية عند بدء الموسم.</li>
</ul></div>

<h2>ما هي الجمعة البيضاء؟</h2>
<p>الجمعة البيضاء هي الاسم الذي تستخدمه متاجر كثيرة في الخليج لموسم «الجمعة السوداء» العالمي، الذي يأتي في الجمعة التالية لعيد الشكر الأمريكي. اختارت أمازون في المنطقة اسم «الجمعة البيضاء»، بينما تسمّي نون موسمها «الجمعة الصفراء»، وتستخدم متاجر أخرى أسماء وألوانًا مختلفة. المهم أن الموسم في الخليج لم يعد يومًا واحدًا، بل أصبح في السنوات الأخيرة أسبوعًا أو أكثر من العروض المتتالية.</p>

<h2>متى تبدأ الجمعة البيضاء 2026؟</h2>
<p>التاريخ الثابت الوحيد هو يوم الجمعة نفسه: 27 نوفمبر 2026. أما مواعيد المتاجر الكبرى فلم تُعلن بعد. تذكر أمازون السعودية في صفحتها المخصصة للبائعين أن الحدث سيكون في نهاية نوفمبر، وأن التواريخ النهائية تُعلن قرب موعده.</p>
<p>للاسترشاد فقط، هذه مواعيد العام الماضي كما نُشرت:</p>
<table><thead><tr><th>المتجر</th><th>موعد 2025</th></tr></thead><tbody>
<tr><td>أمازون الإمارات (الجمعة البيضاء)</td><td>20 – 30 نوفمبر</td></tr>
<tr><td>أمازون السعودية (الجمعة البيضاء)</td><td>21 – 30 نوفمبر، مع وصول مبكر لمشتركي برايم</td></tr>
<tr><td>نون (الجمعة الصفراء)</td><td>20 – 30 نوفمبر</td></tr>
</tbody></table>
<p>إذا تكرر النمط نفسه، فالأرجح أن تبدأ العروض الكبرى قبل الجمعة بنحو أسبوع وتنتهي مع نهاية الشهر. لكن هذا توقع وليس موعدًا رسميًا، وسنحدّث هذا الدليل فور إعلان المتاجر.</p>

<h2>جهّز قائمتك قبل الموسم</h2>
<p>أكثر ما يضيّع التوفير في هذا الموسم هو الشراء العشوائي. قبل أن تبدأ العروض:</p>
<ol>
<li><b>اكتب قائمة قصيرة</b> بما تحتاجه فعلًا، ورتّبها حسب الأولوية.</li>
<li><b>سجّل السعر الحالي</b> لكل منتج في أكثر من متجر، والتقط صورة للصفحة مع التاريخ. هذا مرجعك لمعرفة الخصم الحقيقي.</li>
<li><b>حدّد سقفًا للميزانية</b> قبل أن تبدأ، وخاصة إذا كنت تنوي الدفع بالتقسيط.</li>
<li><b>أضف المنتجات إلى قائمة الرغبات</b> في التطبيق، فبعض المتاجر ترسل تنبيهًا عند انخفاض السعر.</li>
<li><b>حدّث عنوانك وطريقة الدفع</b> في حسابك مسبقًا، لأن العروض المحدودة تنفد بسرعة.</li>
</ol>

<h2>كيف تعرف أن الخصم حقيقي؟</h2>
<p>نسبة الخصم المكتوبة لا تعني بالضرورة توفيرًا حقيقيًا. قارن السعر بعد الخصم بالسعر الذي سجّلته قبل الموسم، لا بالسعر «قبل الخصم» الذي يعرضه المتجر. وإذا وجدت المنتج نفسه أرخص في متجر آخر خارج الموسم، فالعرض ليس بالقوة التي يبدو عليها.</p>
<p>في السعودية، تتطلب التخفيضات ترخيصًا من وزارة التجارة، ويمكن التحقق من الترخيص بمسح الباركود الظاهر عليه، أو عبر خدمة التحقق من الوثائق في موقع الوزارة. هذه خطوة سريعة تحميك من «التخفيضات» غير النظامية.</p>

<h2>عروض البنوك والدفع</h2>
<p>تضيف البنوك عادة خصومات فورية أو استرداد نقدي عند الدفع ببطاقات معينة خلال الموسم، وكثير منها له حد أقصى لكل بطاقة أو لكل عميل. اقرأ الشروط قبل الدفع، وتأكد إن كان العرض البنكي يُجمع مع كود الخصم أم لا. وإذا كنت تفكر في التقسيط عبر تابي أو تمارا، فتحقق من أن الخصم البنكي لا يُستثنى منه هذا النوع من الدفع، واقرأ دليلنا عن الشراء الآن والدفع لاحقًا.</p>

<h2>التوصيل والإرجاع</h2>
<p>يرتفع ضغط الطلبات في نهاية نوفمبر، فتطول مدة التوصيل أحيانًا. إذا كنت تشتري هدية لموعد محدد، فاطلب مبكرًا. وقبل الدفع راجع سياسة الإرجاع، لأن بعض عروض الموسم تكون نهائية أو بشروط إرجاع مختلفة. في السعودية يمنح نظام التجارة الإلكترونية المستهلك حق فسخ العقد خلال سبعة أيام من استلام المنتج ما لم يستخدمه، مع استثناءات محددة. اقرأ دليلنا عن حق الإرجاع لمعرفة التفاصيل.</p>

<h2>كيف نتعامل مع الموسم في كوبون</h2>
<p>لن ننشر أي كود قبل أن يصدر من المتجر نفسه أو من برنامج شريك معتمد. عندما تبدأ العروض الرسمية، ستجد على كل عرض شروطه ومدته وتاريخ آخر تحقق. وإلى ذلك الحين، صفحة الموسم وهذا الدليل هما أفضل نقطة بداية لتخطيط مشترياتك.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li>Black Friday falls on <b>Friday 27 November 2026</b>. Cyber Monday is 30 November.</li>
<li>At the time of writing, neither Amazon (Saudi Arabia, UAE) nor noon had announced official 2026 dates.</li>
<li>In 2025, Amazon.ae ran White Friday from 20 to 30 November and Amazon.sa from 21 to 30 November.</li>
<li>Start a list and record today’s prices now, so you can judge real discounts when the sale opens.</li>
</ul></div>

<h2>What is White Friday?</h2>
<p>White Friday is the name many Gulf retailers give to Black Friday, the Friday after US Thanksgiving. Amazon uses “White Friday” across the region, noon calls its event “Yellow Friday”, and other stores pick their own colour. Whatever the label, it’s no longer a single day here. Over the past few years it has grown into a week or more of back-to-back promotions.</p>

<h2>When does White Friday 2026 start?</h2>
<p>The only fixed date is the Friday itself: 27 November 2026. Retailers haven’t confirmed their windows yet. Amazon.sa’s seller page says the event will take place towards the end of November, with final dates released closer to the time.</p>
<p>For reference only, here is how last year played out:</p>
<table><thead><tr><th>Retailer</th><th>2025 window</th></tr></thead><tbody>
<tr><td>Amazon.ae (White Friday)</td><td>20–30 November</td></tr>
<tr><td>Amazon.sa (White Friday)</td><td>21–30 November, with early access for Prime members</td></tr>
<tr><td>noon (Yellow Friday)</td><td>20–30 November</td></tr>
</tbody></table>
<p>If the pattern holds, expect the big deals to open about a week before the Friday and run to the end of the month. That’s an educated guess, not an announcement. We’ll update this guide as soon as the stores publish their dates.</p>

<h2>Build your list before the sale</h2>
<p>Impulse buying is what eats most of the savings. Before the deals start:</p>
<ol>
<li><b>Write a short list</b> of what you actually need, in order of priority.</li>
<li><b>Record today’s price</b> for each item at two or three stores, and screenshot the page with the date. That’s your benchmark.</li>
<li><b>Set a budget ceiling</b>, especially if you plan to pay in instalments.</li>
<li><b>Add items to your wish list</b> in each app. Some stores notify you when a price drops.</li>
<li><b>Update your address and payment card</b> in advance. Limited deals sell out fast.</li>
</ol>

<h2>Is the discount real?</h2>
<p>A big percentage on the tag isn’t proof of a big saving. Compare the sale price with the price you recorded before the season, not with the “was” price the store shows. If the same product was cheaper elsewhere a month ago, the deal is weaker than it looks.</p>
<p>In Saudi Arabia, sales need a licence from the Ministry of Commerce. You can check a licence by scanning the barcode printed on it, or through the Ministry’s document verification service. It takes seconds and protects you from unlicensed “sales”.</p>

<h2>Bank offers and payment</h2>
<p>Banks often add instant discounts or cashback on selected cards during the season, and many are capped per card or per customer. Read the terms before you pay, and check whether the bank offer stacks with a discount code. If you plan to split the payment with Tabby or Tamara, confirm the bank offer doesn’t exclude instalment payments. Our buy-now-pay-later guide covers the details.</p>

<h2>Delivery and returns</h2>
<p>Order volumes peak at the end of November, so delivery can take longer. If you’re buying a gift for a specific date, order early. Check the return policy before paying, since some sale items are final or have different return terms. In Saudi Arabia, the E-Commerce Law gives consumers seven days from delivery to cancel a purchase, provided the item hasn’t been used, with some exceptions. Our returns guide explains how it works.</p>

<h2>How Kobon handles the season</h2>
<p>We won’t publish any code until it comes from the store itself or an approved partner programme. When official offers go live, each one will show its terms, its validity and the date we last checked it. Until then, the season page and this guide are the best place to start planning.</p>
""",
})

GUIDES.append({
"slug": "11-11-gulf",
"updated": "2026-11-09",
"title_ar": "عروض 11.11 في الخليج: ما هو اليوم وكيف تستفيد منه",
"title_en": "11.11 in the Gulf: what Singles’ Day is and how to make the most of it",
"desc_ar": "من أين جاء موسم 11.11، ومتى تبدأ عروضه في الإمارات والسعودية، وكيف تقارنه بالجمعة البيضاء التي تليه بأسابيع.",
"desc_en": "Where 11.11 comes from, when Gulf retailers run it, and how to weigh it against White Friday a few weeks later.",
"tag_ar": "مواسم", "tag_en": "Seasons",
"sources": [
 ("https://gulfnews.com/business/retail/uae-retailers-unveil-massive-1111-singles-day-sales-with-up-to-80-off-1.500340496", "Gulf News: UAE retailers’ 11.11 sales"),
 ("https://whatsonsaudiarabia.com/2025/11/noon-11-11-sale-2025/", "What’s On Saudi Arabia: noon’s 11.11 sale 2025"),
 ("https://www.khaleejtimes.com/uae/1111-sale-dh1-deals-90-discounts-gifts", "Khaleej Times: 11.11 sale in the UAE"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li>يوافق 11.11 هذا العام <b>الأربعاء 11 نوفمبر 2026</b>.</li>
<li>بدأ اليوم في الصين بوصفه «يوم العزّاب»، ثم حوّلته علي بابا إلى أكبر موسم تسوق إلكتروني هناك، وانتقل إلى المتاجر في الخليج.</li>
<li>في 2025 امتدت عروض نون لموسم 11.11 من 7 إلى 12 نوفمبر في الإمارات والسعودية.</li>
<li>يأتي قبل الجمعة البيضاء بأسبوعين تقريبًا، فقارن قبل أن تشتري المنتجات الكبيرة.</li>
</ul></div>

<h2>من أين جاء 11.11؟</h2>
<p>اختيار التاريخ ليس صدفة: الرقم 1 يتكرر أربع مرات، فارتبط اليوم في الصين بالعزّاب. ومع الوقت حوّلت شركة علي بابا هذه المناسبة إلى مهرجان تسوق إلكتروني ضخم، ثم تبنته متاجر حول العالم. وفي الخليج أصبح 11.11 خلال السنوات الأخيرة من أبرز مواسم نوفمبر، ويعدّه كثير من المتسوقين بداية فعلية لموسم التخفيضات.</p>

<h2>كيف يجري 11.11 في الخليج؟</h2>
<p>لا يقتصر الموسم على يوم واحد غالبًا. في 2025 مثلًا، بدأت عروض نون في الإمارات والسعودية في 7 نوفمبر واستمرت حتى 12 نوفمبر، بحسب ما نشرته وسائل إعلام محلية. وتشارك متاجر أزياء وإلكترونيات وجمال بعروض خاصة بها، بعضها يبدأ عند منتصف الليل ويستمر 24 ساعة فقط، وبعضها يمتد أيامًا.</p>
<p>لأن مواعيد كل متجر تختلف، لا تعتمد على يوم 11 وحده. تابع تطبيقات المتاجر التي تهمك وفعّل إشعاراتها قبل الموعد بأيام.</p>

<h2>11.11 أم الجمعة البيضاء؟</h2>
<p>يأتي 11.11 قبل الجمعة البيضاء بنحو أسبوعين، فيبقى السؤال: هل أشتري الآن أم أنتظر؟ لا توجد إجابة واحدة، لكن هذه قواعد عملية:</p>
<ul>
<li><b>المشتريات الصغيرة والمتكررة</b> مثل منتجات العناية والملابس اليومية: إذا كان السعر جيدًا مقارنة بما سجّلته سابقًا، فلا داعي للانتظار.</li>
<li><b>الأجهزة الكبيرة والإلكترونيات</b>: سجّل سعر 11.11، ثم قارنه بعروض الجمعة البيضاء. وإذا اشتريت الآن، فاعرف سياسة الإرجاع وهل يتيح المتجر استرداد الفرق عند انخفاض السعر (وهذا نادر، فلا تفترضه).</li>
<li><b>المنتجات محدودة الكمية</b>: إذا كان المنتج مطلوبًا بكثرة، فقد ينفد قبل الجمعة البيضاء.</li>
</ul>

<h2>خطوات قبل الشراء</h2>
<ol>
<li><b>راجع السعر المرجعي</b>: قارن السعر بعد الخصم بالسعر قبل أسبوعين، لا بالسعر المشطوب فقط.</li>
<li><b>اقرأ شروط الكود</b>: الحد الأدنى للشراء، والحد الأقصى للخصم، والفئات المستثناة، وهل يعمل على المنتجات المخفّضة أصلًا.</li>
<li><b>احسب التكلفة النهائية</b>: الشحن، والضريبة، ورسوم الجمارك إن كان المتجر خارج بلدك.</li>
<li><b>تأكد من البائع</b> في الأسواق الإلكترونية: هل يبيع المتجر نفسه، أم بائع طرف ثالث بسياسة إرجاع مختلفة؟</li>
</ol>

<h2>المتاجر العالمية في 11.11</h2>
<p>تشارك متاجر عالمية كثيرة في 11.11، وبعضها يشحن إلى الخليج مباشرة. قبل أن تتحمس لخصم كبير من متجر في الخارج، احسب الشحن وضريبة القيمة المضافة والرسوم الجمركية عند الاستيراد، فقد تقلّل الفرق كثيرًا. اقرأ دليلنا عن الشحن والجمارك من المتاجر العالمية لمعرفة الحدود والإعفاءات في السعودية والإمارات.</p>

<h2>كيف نتعامل مع الموسم في كوبون</h2>
<p>ننشر عروض 11.11 الرسمية فقط، أي العروض التي يصدرها المتجر أو برنامج شريك معتمد، مع شروطها ومدتها وتاريخ آخر تحقق. لا نعيد نشر أكواد متداولة لا نعرف مصدرها، حتى لو بدت مغرية.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li>11.11 falls on <b>Wednesday 11 November 2026</b>.</li>
<li>It started in China as “Singles’ Day”. Alibaba turned it into the country’s biggest online shopping event, and Gulf retailers picked it up.</li>
<li>In 2025, noon ran its 11.11 sale from 7 to 12 November in the UAE and Saudi Arabia.</li>
<li>It lands about two weeks before White Friday, so compare before you buy anything big.</li>
</ul></div>

<h2>Where 11.11 comes from</h2>
<p>The date is no accident: four ones in a row came to stand for being single, and in China 11 November became Singles’ Day. Alibaba turned it into a huge online shopping festival, and retailers around the world followed. In the Gulf it has become one of November’s headline events, and for many shoppers it now marks the real start of sale season.</p>

<h2>How it runs in the Gulf</h2>
<p>It’s rarely just one day. In 2025, for example, noon’s 11.11 deals in the UAE and Saudi Arabia started on 7 November and ran until 12 November, according to local media. Fashion, electronics and beauty stores join in with their own promotions. Some open at midnight and last 24 hours; others stretch over several days.</p>
<p>Because every store sets its own timing, don’t plan around the 11th alone. Follow the apps you care about and turn on their notifications a few days ahead.</p>

<h2>11.11 or White Friday?</h2>
<p>With White Friday about two weeks later, the obvious question is whether to buy now or wait. There’s no single answer, but a few rules of thumb help:</p>
<ul>
<li><b>Small, repeat purchases</b> such as skincare or everyday clothing: if the price beats what you’ve seen before, there’s little reason to wait.</li>
<li><b>Big-ticket electronics and appliances</b>: note the 11.11 price and compare it with White Friday. If you buy now, know the return policy, and don’t assume the store will refund a later price drop. Few do.</li>
<li><b>Limited-stock items</b>: popular products can sell out before White Friday arrives.</li>
</ul>

<h2>Before you check out</h2>
<ol>
<li><b>Check the benchmark price.</b> Compare the sale price with what the item cost two weeks ago, not just the crossed-out price.</li>
<li><b>Read the code’s terms.</b> Minimum spend, maximum discount, excluded categories, and whether it works on items already on sale.</li>
<li><b>Work out the final cost.</b> Shipping, VAT, and customs if the store is abroad.</li>
<li><b>Check who the seller is</b> on marketplaces. A third-party seller may have a different return policy from the platform.</li>
</ol>

<h2>International stores on 11.11</h2>
<p>Plenty of international stores run 11.11 deals, and some ship straight to the Gulf. Before you jump on a big discount from abroad, add up shipping, import VAT and any customs duty, which can narrow the gap quickly. Our shipping and customs guide covers the thresholds in Saudi Arabia and the UAE.</p>

<h2>How Kobon handles 11.11</h2>
<p>We only publish official 11.11 offers, issued by the store or an approved partner programme, each with its terms, validity and last-checked date. We don’t repost codes that are doing the rounds unless we can trace them to the source, however tempting they look.</p>
""",
})

GUIDES.append({
"slug": "global-shipping-customs",
"updated": "2026-11-09",
"title_ar": "الشراء من المتاجر العالمية: الشحن والجمارك والضريبة في السعودية والإمارات",
"title_en": "Buying from international stores: shipping, customs and VAT in Saudi Arabia and the UAE",
"desc_ar": "متى تُعفى شحنتك من الرسوم الجمركية؟ ولماذا تدفع ضريبة القيمة المضافة حتى على الطلبات الصغيرة؟ دليل عملي لحساب السعر النهائي قبل الشراء من الخارج.",
"desc_en": "When is your parcel exempt from customs duty, and why does VAT still apply to small orders? A practical guide to the real cost of shopping abroad.",
"tag_ar": "المتاجر العالمية", "tag_en": "International stores",
"sources": [
 ("https://zatca.gov.sa/en/RulesRegulations/Taxes/Pages/customs-individual/e-stores-customers.aspx", "ZATCA: E-store customers (customs and VAT)"),
 ("https://zatca.gov.sa/en/MediaCenter/News/Pages/news-1282.aspx", "ZATCA: customs service fees, including the SAR 15 e-store fee"),
 ("https://www.dubaicustoms.gov.ae/en/PoliciesAndNotices/Notices/CN16_2026.pdf", "Dubai Customs: Customs Notice 16/2026 on cross-border e-commerce"),
 ("https://u.ae/en/information-and-services/finance-and-investment/taxation/clearing-the-customs-and-paying-customs-duty", "UAE Government portal: customs duty and tariff"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li><b>السعودية:</b> تُعفى المشتريات الشخصية من المتاجر الإلكترونية من الرسوم الجمركية إذا كانت قيمتها الإجمالية (البضاعة + الشحن + التأمين) أقل من 1,000 ريال، لكن ضريبة القيمة المضافة (15%) تبقى مستحقة، إضافة إلى رسم معالجة بيان جمركي قدره 15 ريالًا.</li>
<li><b>الإمارات:</b> أعلنت جمارك دبي إعفاء سلع التجارة الإلكترونية العابرة للحدود التي لا تتجاوز قيمتها 1,000 درهم من الرسوم الجمركية اعتبارًا من 3 أغسطس 2026، مع استثناءات. أما ضريبة القيمة المضافة (5%) فتُطبّق على الواردات.</li>
<li>الرسوم الجمركية الموحدة في دول الخليج 5% من القيمة شاملة الشحن والتأمين لمعظم السلع.</li>
<li>احسب السعر النهائي قبل الدفع، لا سعر المنتج وحده.</li>
</ul></div>

<h2>لماذا يختلف السعر النهائي عن سعر المنتج؟</h2>
<p>عندما تشتري من متجر خارج بلدك، تضاف إلى سعر المنتج تكاليف قد لا تظهر في صفحة الدفع: تكلفة الشحن الدولي، وضريبة القيمة المضافة على الاستيراد، والرسوم الجمركية إذا تجاوزت الشحنة حد الإعفاء، وأحيانًا رسوم تخليص تفرضها شركة الشحن. بعض المتاجر تحسب هذه المبالغ مسبقًا وتعرضها لك قبل الدفع، وبعضها يتركها لتدفعها عند التسليم. اسأل نفسك دائمًا: هل السعر المعروض «شامل الرسوم والضرائب» أم لا؟</p>

<h2>السعودية: حد 1,000 ريال</h2>
<p>توضح هيئة الزكاة والضريبة والجمارك أن المشتريات الشخصية من المتاجر الإلكترونية في الخارج تُعفى من الرسوم الجمركية بشرطين:</p>
<ol>
<li>أن تكون القيمة الإجمالية أقل من 1,000 ريال، وتشمل قيمة البضاعة وتكلفة الشحن والتأمين.</li>
<li>ألا تحتاج الشحنة إلى فسح من جهة أخرى.</li>
</ol>
<p>لكن الإعفاء يخص الرسوم الجمركية فقط. ضريبة القيمة المضافة تُحصّل في جميع الحالات بغض النظر عن قيمة الشحنة، إلا ما استثناه النظام، وتُحسب على قيمة البضاعة والشحن والتأمين والرسوم الجمركية ورسوم البيان الجمركي. كما أصدرت الهيئة قواعد رسوم الخدمات الجمركية التي تنص على رسم قدره 15 ريالًا لمعالجة البيان الجمركي لشحنات الأفراد الواردة عبر المتاجر الإلكترونية التي لا تتجاوز قيمتها 1,000 ريال.</p>
<p><b>مثال توضيحي:</b> منتج بسعر 800 ريال مع شحن 150 ريالًا. القيمة الإجمالية 950 ريالًا، أي أقل من الحد، فلا رسوم جمركية. لكن ستدفع ضريبة القيمة المضافة 15% على المبلغ الخاضع للضريبة (بما فيه رسم البيان)، أي نحو 145 ريالًا، فيصبح الإجمالي قرابة 1,110 ريالات. ولو كان الشحن 250 ريالًا لتجاوزت القيمة 1,000 ريال وأصبحت الرسوم الجمركية مستحقة أيضًا.</p>
<p>انتبه: بعض المنتجات تحتاج إلى موافقة جهات أخرى مهما كانت قيمتها، مثل مستحضرات التجميل والمكملات الغذائية والأدوية وبعض الأجهزة اللاسلكية. وقد تتأخر هذه الشحنات أو تُرفض إذا لم تستوفِ المتطلبات.</p>

<h2>الإمارات: حد 1,000 درهم</h2>
<p>الرسوم الجمركية في الإمارات، كما في بقية دول مجلس التعاون، 5% من قيمة السلع شاملة الشحن والتأمين، مع نسب مختلفة لسلع مثل التبغ والكحول. وفي 2026 أصدرت جمارك دبي إعلانًا جمركيًا بإعفاء سلع التجارة الإلكترونية العابرة للحدود التي لا تتجاوز قيمتها 1,000 درهم من الرسوم الجمركية، ويسري اعتبارًا من 3 أغسطس 2026. ولا يشمل الإعفاء التبغ ومشتقاته وأجهزة التدخين الإلكترونية وسوائل النيكوتين والمشروبات الكحولية.</p>
<p>أما ضريبة القيمة المضافة في الإمارات فنسبتها 5%، وتُطبّق على السلع المستوردة. لذلك فإن إعفاء الرسوم الجمركية لا يعني أن الطلب معفى من كل التكاليف.</p>

<h2>بقية دول الخليج</h2>
<p>تطبّق دول مجلس التعاون تعرفة جمركية موحدة بنسبة 5% لمعظم السلع المستوردة من خارج الاتحاد الجمركي، لكن حدود الإعفاء للطلبات الصغيرة وإجراءات التخليص تختلف من دولة إلى أخرى. كما تختلف ضريبة القيمة المضافة: 10% في البحرين و5% في عُمان، بينما لم تطبّقها الكويت وقطر حتى الآن. قبل الطلب، راجع موقع الجمارك في بلدك أو اسأل شركة الشحن عن التكاليف المتوقعة.</p>

<h2>نصائح عملية قبل الشراء من الخارج</h2>
<ul>
<li><b>ابحث عن خيار «شامل الرسوم»</b> عند الدفع، فهو يجنّبك المفاجآت عند التسليم.</li>
<li><b>لا تقسّم الطلب</b> للبقاء تحت حد الإعفاء؛ قد تُعامل الطلبات المجزأة كشحنة واحدة.</li>
<li><b>احتفظ بالفاتورة</b> وإيصال الضريبة الذي تقدّمه شركة الشحن.</li>
<li><b>اقرأ سياسة الإرجاع الدولية</b>: إعادة منتج إلى الخارج قد تكون مكلفة، وقد لا تُسترد الضرائب المدفوعة بسهولة.</li>
<li><b>قارن مع المتجر المحلي</b>: أحيانًا يبيع الموزع المحلي المنتج نفسه بسعر قريب مع ضمان محلي وإرجاع أسهل.</li>
</ul>

<p class="note">هذا الدليل للتوعية العامة وليس استشارة جمركية أو ضريبية. الأنظمة والحدود تتغير، والمرجع النهائي هو موقع الجهة الرسمية في بلدك.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li><b>Saudi Arabia:</b> personal online purchases are exempt from customs duty when the total value (goods + shipping + insurance) is under SAR 1,000. VAT at 15% still applies, plus a SAR 15 customs declaration fee.</li>
<li><b>UAE:</b> Dubai Customs exempts eligible cross-border e-commerce goods worth up to AED 1,000 from customs duty from 3 August 2026, with exclusions. Import VAT at 5% still applies.</li>
<li>The common GCC customs duty is 5% of the value including shipping and insurance, for most goods.</li>
<li>Work out the landed cost before you pay, not just the item price.</li>
</ul></div>

<h2>Why the final price isn’t the sticker price</h2>
<p>Order from a store abroad and several costs can land on top of the item price: international shipping, import VAT, customs duty above the exemption threshold, and sometimes a clearance fee from the courier. Some stores calculate all of this at checkout. Others leave it for you to pay on delivery. The question to ask every time is simple: is this price “duties and taxes included” or not?</p>

<h2>Saudi Arabia: the SAR 1,000 line</h2>
<p>The Zakat, Tax and Customs Authority (ZATCA) says personal purchases from overseas online stores are exempt from customs duty when two conditions are met:</p>
<ol>
<li>The total value is below SAR 1,000, counting the goods, shipping and insurance.</li>
<li>The shipment doesn’t need clearance approval from another authority.</li>
</ol>
<p>That exemption covers duty only. VAT is collected regardless of the shipment’s value, except where the VAT rules say otherwise, and it’s calculated on the goods, shipping, insurance, customs duty and declaration fees. ZATCA’s customs fee rules also set a SAR 15 declaration processing fee for individuals’ e-store shipments worth up to SAR 1,000.</p>
<p><b>Worked example:</b> an SAR 800 item with SAR 150 shipping comes to SAR 950, under the line, so no duty. You’ll still pay 15% VAT on the taxable amount, including the declaration fee: roughly SAR 145, for a total of about SAR 1,110. If shipping were SAR 250, the total would cross SAR 1,000 and customs duty would apply too.</p>
<p>Some products need approval from another regulator whatever their value, including cosmetics, supplements, medicines and some wireless devices. These can be delayed or refused if the paperwork isn’t in order.</p>

<h2>UAE: the AED 1,000 line</h2>
<p>Customs duty in the UAE, as across the GCC, is 5% of the goods’ value including shipping and insurance, with higher rates for items such as tobacco and alcohol. In 2026, Dubai Customs issued a notice exempting cross-border e-commerce goods worth no more than AED 1,000 from customs duty, effective 3 August 2026. The exemption doesn’t cover tobacco, e-cigarettes and accessories, nicotine liquids or alcoholic drinks.</p>
<p>The UAE’s VAT rate is 5% and it applies to imported goods. A duty-free parcel isn’t a cost-free parcel.</p>

<h2>The rest of the Gulf</h2>
<p>GCC states share a common external tariff of 5% on most goods imported from outside the customs union, but low-value exemptions and clearance procedures differ by country. VAT differs too: 10% in Bahrain and 5% in Oman, while Kuwait and Qatar haven’t introduced it. Before ordering, check your national customs website or ask the courier what to expect.</p>

<h2>Practical tips</h2>
<ul>
<li><b>Look for a “duties included” option</b> at checkout to avoid surprises on the doorstep.</li>
<li><b>Don’t split an order</b> to stay under a threshold. Split shipments can be treated as one.</li>
<li><b>Keep the invoice</b> and the VAT receipt the courier gives you.</li>
<li><b>Read the international return policy.</b> Sending something back abroad can be expensive, and taxes already paid aren’t always easy to recover.</li>
<li><b>Compare with local retailers.</b> A local distributor sometimes sells the same item for a similar price, with a local warranty and easier returns.</li>
</ul>

<p class="note">This guide is general information, not customs or tax advice. Rules and thresholds change, and the official authority in your country has the final word.</p>
""",
})

GUIDES.append({
"slug": "verify-coupon-code",
"updated": "2026-11-09",
"title_ar": "كيف تتأكد أن كود الخصم حقيقي قبل أن تستخدمه",
"title_en": "How to tell whether a discount code is real before you use it",
"desc_ar": "خطوات عملية لمعرفة مصدر الكود وشروطه وصلاحيته، وعلامات الأكواد المزيفة والمنتهية، وما تفعله إذا لم يعمل الكود في صفحة الدفع.",
"desc_en": "Practical steps to check a code’s source, terms and validity, spot fake or expired codes, and what to do when a code fails at checkout.",
"tag_ar": "أساسيات", "tag_en": "Basics",
"sources": [
 ("https://mc.gov.sa/Pages/dvs.aspx", "Saudi Ministry of Commerce: document verification service"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li>الكود الموثوق له مصدر واضح: المتجر نفسه، أو برنامج شريك معتمد، أو حملة رسمية معلنة.</li>
<li>اقرأ الشروط قبل النسخ: الحد الأدنى للشراء، والحد الأقصى للخصم، والفئات والدول المشمولة، وتاريخ الانتهاء.</li>
<li>لا تُدخل بياناتك في صفحة خارجية «لكشف الكود». الكود يُستخدم في صفحة الدفع على موقع المتجر الرسمي فقط.</li>
<li>إذا لم يعمل الكود، فالسبب غالبًا في الشروط لا في الكود نفسه.</li>
</ul></div>

<h2>لماذا تفشل أكواد كثيرة؟</h2>
<p>أكواد الخصم تنتشر بسرعة: تُنسخ من موقع إلى آخر، وتُشارك في المجموعات، وتبقى منشورة بعد انتهائها بأشهر. كما أن بعض الأكواد شخصية أصلًا، أي صادرة لعميل واحد أو للطلب الأول فقط، ثم تتسرّب للعامة فيوقفها المتجر. والنتيجة أنك تجرّب كودًا بعد آخر في صفحة الدفع دون فائدة. الحل ليس تجربة المزيد، بل التحقق من المصدر والشروط قبل البدء.</p>

<h2>الخطوة 1: من أين جاء الكود؟</h2>
<p>ابدأ بالمصدر، فهو أهم مؤشر على صحة الكود:</p>
<ul>
<li><b>المتجر نفسه:</b> صفحة العروض في الموقع أو التطبيق، أو رسالة رسمية من المتجر إلى بريدك.</li>
<li><b>برنامج شريك معتمد:</b> مواقع ومؤثرون يعملون مع المتجر باتفاق رسمي، ويحصلون على أكواد مخصصة لجمهورهم.</li>
<li><b>البنوك وشركات الدفع:</b> حملات مشتركة مع المتاجر، تظهر عادة في تطبيق البنك وموقع المتجر معًا.</li>
</ul>
<p>إذا لم تستطع ربط الكود بأي من هذه المصادر، فاعتبره غير مؤكد. في كوبون لا ننشر إلا الأكواد التي نعرف مصدرها.</p>

<h2>الخطوة 2: اقرأ الشروط كاملة</h2>
<p>أغلب حالات «الكود لا يعمل» سببها شرط لم ينتبه له المتسوق. قبل النسخ تحقق من:</p>
<ol>
<li><b>الحد الأدنى للشراء:</b> هل تجاوزت سلتك المبلغ المطلوب بعد احتساب الخصومات الأخرى؟</li>
<li><b>الحد الأقصى للخصم:</b> كود «20%» قد يكون بحد أقصى 50 ريالًا، فلا يمنحك 20% على طلب كبير.</li>
<li><b>الفئات والماركات المستثناة:</b> كثير من الأكواد لا تشمل الإلكترونيات أو بعض الماركات أو المنتجات المخفّضة أصلًا.</li>
<li><b>الدولة:</b> كود صادر للسعودية قد لا يعمل في الإمارات، والعكس.</li>
<li><b>نوع العميل:</b> بعض الأكواد للعملاء الجدد أو للطلب الأول فقط، أو لمستخدمي التطبيق دون الموقع.</li>
<li><b>تاريخ الانتهاء:</b> وبعض الأكواد تنتهي عند نفاد عدد مرات الاستخدام قبل تاريخها المعلن.</li>
</ol>

<h2>الخطوة 3: علامات التحذير</h2>
<p>احذر الكود أو الموقع إذا لاحظت شيئًا من هذا:</p>
<ul>
<li>خصم كبير بشكل غير منطقي على منتجات لا يخفّضها المتجر عادة.</li>
<li>طلب تحميل تطبيق غير معروف أو إدخال رقم جوالك أو بيانات بطاقتك «لكشف الكود».</li>
<li>رابط يأخذك إلى موقع يشبه المتجر لكن عنوانه مختلف، ولو بحرف واحد.</li>
<li>عدّ تنازلي يضغط عليك للشراء فورًا دون أي شروط مكتوبة.</li>
<li>غياب أي تاريخ أو شرط أو جهة مسؤولة عن العرض.</li>
</ul>
<p>القاعدة البسيطة: الكود يُكتب في خانة الكوبون في صفحة الدفع على موقع المتجر الرسمي، ولا يحتاج إلى أي بيانات إضافية منك.</p>

<h2>الخطوة 4: جرّب الكود بأمان</h2>
<p>أضف المنتجات إلى السلة، ثم أدخل الكود قبل تأكيد الدفع، وتأكد أن الخصم ظهر فعلًا في ملخص الطلب بالمبلغ المتوقع. إذا ظهر خصم أقل مما توقعت، فراجع الحد الأقصى للخصم. وإذا ظهرت رسالة خطأ، فاقرأها جيدًا؛ المتاجر عادة توضح السبب: «الكود منتهٍ»، أو «لا يشمل هذه المنتجات»، أو «لم تصل إلى الحد الأدنى».</p>

<h2>ماذا تفعل إذا لم يعمل الكود؟</h2>
<ol>
<li>تحقق من كتابة الكود بالأحرف الصحيحة ودون مسافات زائدة.</li>
<li>راجع الشروط مرة أخرى، خاصة الدولة والحد الأدنى والفئات.</li>
<li>جرّب في التطبيق إذا كنت تستخدم الموقع، أو العكس، إذا كانت الشروط تذكر ذلك.</li>
<li>إذا كان الكود من كوبون، فأبلغنا من صفحة التواصل مع اسم المتجر والكود ودولتك، وسنراجعه خلال يوم عمل.</li>
</ol>

<h2>خصم المتجر أم كود الخصم؟</h2>
<p>أحيانًا يكون السعر المخفّض المعروض في صفحة المنتج أفضل من أي كود، وكثير من المتاجر لا تسمح بجمع الكود مع التخفيض. قارن الخيارين: السعر بعد التخفيض وحده، والسعر الأصلي بعد الكود. واختر الأقل بعد احتساب الشحن.</p>

<p>وإذا كنت في السعودية وتريد التأكد من أن «التخفيضات» المعلنة نظامية، فوزارة التجارة تتيح التحقق من تراخيص التخفيضات عبر خدمة التحقق من الوثائق في موقعها.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li>A trustworthy code has a clear source: the store itself, an approved partner programme, or an announced official campaign.</li>
<li>Read the terms before you copy it: minimum spend, maximum discount, eligible categories and countries, expiry.</li>
<li>Never hand over personal details on a third-party page to “unlock” a code. Codes go in the checkout on the store’s official site, nowhere else.</li>
<li>When a code fails, the reason is usually in the terms, not the code.</li>
</ul></div>

<h2>Why so many codes fail</h2>
<p>Discount codes travel fast. They’re copied from site to site, shared in group chats, and left online months after they expire. Some were personal to begin with, issued to one customer or for a first order only, and the store shut them down once they leaked. The result is a checkout session spent pasting code after code. The fix isn’t trying more codes. It’s checking the source and terms before you start.</p>

<h2>Step 1: Where did it come from?</h2>
<p>The source tells you more than anything else:</p>
<ul>
<li><b>The store itself:</b> the offers page on its site or app, or an official email from the store.</li>
<li><b>An approved partner:</b> sites and creators who work with the store under a formal agreement and get codes for their audience.</li>
<li><b>Banks and payment providers:</b> joint campaigns, usually announced in both the bank’s app and the store’s site.</li>
</ul>
<p>If you can’t trace a code to any of these, treat it as unconfirmed. At Kobon we only publish codes whose source we know.</p>

<h2>Step 2: Read every term</h2>
<p>Most “this code doesn’t work” moments come down to a condition nobody noticed. Before copying, check:</p>
<ol>
<li><b>Minimum spend.</b> Does your basket clear the threshold after other discounts?</li>
<li><b>Maximum discount.</b> A “20% off” code capped at SAR 50 won’t give you 20% on a big order.</li>
<li><b>Excluded categories and brands.</b> Many codes skip electronics, certain brands or items already on sale.</li>
<li><b>Country.</b> A code issued for Saudi Arabia may not work in the UAE, and vice versa.</li>
<li><b>Customer type.</b> Some codes are for new customers, first orders, or app users only.</li>
<li><b>Expiry.</b> Some codes also stop working once a usage limit is reached, before the stated end date.</li>
</ol>

<h2>Step 3: Red flags</h2>
<p>Be wary of a code, or a site, if you see any of these:</p>
<ul>
<li>A discount that’s implausibly large on products the store rarely discounts.</li>
<li>A request to install an unknown app, or enter your phone number or card details, to “reveal” the code.</li>
<li>A link to a site that looks like the store but has a different address, even by one letter.</li>
<li>A countdown pushing you to buy now with no written terms at all.</li>
<li>No date, no conditions and no named company behind the offer.</li>
</ul>
<p>The simple rule: a code goes into the coupon box at checkout on the store’s official site. It never needs anything else from you.</p>

<h2>Step 4: Test it safely</h2>
<p>Add items to your basket, enter the code before you confirm payment, and make sure the discount actually appears in the order summary for the amount you expected. If it’s smaller, check the maximum discount. If you get an error, read it. Stores usually say why: the code has expired, doesn’t cover these items, or the minimum hasn’t been met.</p>

<h2>When a code doesn’t work</h2>
<ol>
<li>Check the spelling and remove any stray spaces.</li>
<li>Re-read the terms, especially country, minimum spend and categories.</li>
<li>Try the app instead of the website, or the other way round, if the terms mention it.</li>
<li>If the code came from Kobon, tell us via the contact page with the store, the code and your country. We’ll check it within one business day.</li>
</ol>

<h2>Sale price or code?</h2>
<p>Sometimes the reduced price on the product page beats any code, and many stores won’t let you combine the two. Compare both: the sale price on its own, and the full price with the code applied. Pick whichever is lower once shipping is included.</p>

<p>In Saudi Arabia, if you want to confirm an advertised sale is licensed, the Ministry of Commerce lets you check discount licences through its document verification service.</p>
""",
})

GUIDES.append({
"slug": "tabby-tamara-bnpl",
"updated": "2026-11-09",
"title_ar": "اشترِ الآن وادفع لاحقًا: كيف يعمل تابي وتمارا وما الذي يجب أن تعرفه",
"title_en": "Buy now, pay later: how Tabby and Tamara work, and what to watch for",
"desc_ar": "شرح مبسط لخدمات التقسيط تابي وتمارا في السعودية والإمارات: عدد الدفعات، والرسوم، وما يحدث عند التأخر في السداد، ومتى يكون التقسيط قرارًا جيدًا.",
"desc_en": "A plain guide to Tabby and Tamara in Saudi Arabia and the UAE: instalments, fees, what happens if you pay late, and when splitting a payment makes sense.",
"tag_ar": "الدفع", "tag_en": "Payments",
"sources": [
 ("https://tabby.sa/en-SA/pay-in-4", "Tabby Saudi Arabia: Pay in 4"),
 ("https://tabby.ai/en-AE/pay-in-4", "Tabby UAE: Pay in 4"),
 ("https://tabby.sa/en-SA/newsroom/no-late-fees", "Tabby: removal of late fees in Saudi Arabia (December 2023)"),
 ("https://cdn.tamara.co/static/faq-en.html", "Tamara: FAQs"),
 ("https://tamarapay.zendesk.com/hc/en-us/articles/21035456957970-What-are-processing-fees", "Tamara Help Center: processing fees"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li>تابي وتمارا خدمتان تتيحان تقسيم ثمن المشتريات على دفعات، تُدفع الأولى عند الشراء والباقي شهريًا.</li>
<li>تقدّم الشركتان خدماتهما على أنها بلا فوائد ومتوافقة مع أحكام الشريعة، لكن قد تُطبّق رسوم معالجة في بعض الخطط، وتظهر عند الدفع.</li>
<li>تختلف عواقب التأخر حسب الدولة والخطة، وقد يؤثر التأخر المتكرر في سجلك الائتماني.</li>
<li>التقسيط أداة لتنظيم الدفع، وليس سببًا لشراء ما لا تحتاجه.</li>
</ul></div>

<h2>كيف تعمل الخدمة؟</h2>
<p>عند الدفع في متجر يدعم الخدمة تختار تابي أو تمارا كطريقة دفع، ثم تسجّل برقم جوالك وهويتك وتربط بطاقة. تتم الموافقة عادة خلال لحظات، وتدفع الدفعة الأولى فورًا، ثم تُخصم بقية الدفعات من بطاقتك في المواعيد المحددة. يحصل المتجر على المبلغ كاملًا من شركة التقسيط، وتدفع الشركة للمتجر مقابل الخدمة، وهذا مصدر دخلها الأساسي.</p>

<h2>تابي</h2>
<p>تذكر تابي في موقعها السعودي أنك تستطيع تقسيم مشترياتك على 3 أو 4 دفعات شهرية، عبر الإنترنت أو في المتاجر، مع دفع الدفعة الأولى عند الشراء والبقية في اليوم نفسه من كل شهر. ووفقًا لصفحة الأسئلة الشائعة، لا رسوم ولا فوائد عند التقسيم على 3 دفعات، وقد تُطبّق رسوم معالجة بنسبة 1% عند التقسيم على 4، وتظهر الرسوم في جدول الدفع قبل التأكيد.</p>
<p>في ديسمبر 2023 أعلنت تابي إلغاء رسوم التأخير على خدمة الدفع على 4 دفعات في السعودية. لكن الحساب يتوقف عن قبول مشتريات جديدة إذا تأخرت دفعة، وقد يُبلَّغ عن التأخر المتكرر لشركات المعلومات الائتمانية. أما في الإمارات، فتذكر تابي أن العملاء قد يتحملون رسوم تحصيل عند التأخر. لذلك راجع شروط بلدك تحديدًا قبل الاستخدام.</p>

<h2>تمارا</h2>
<p>تتيح تمارا تقسيم المشتريات على عدة دفعات، وتقدّم نفسها على أنها بلا رسوم تأخير ومتوافقة مع الشريعة. وتوضح في مركز المساعدة أن رسوم معالجة قد تُطبّق على خطط الدفع، تغطي تكاليف معالجة الطلب والتحقق من الهوية والتحقق الائتماني، وتظهر بوضوح في صفحة الدفع وتُوزّع على الدفعات. ويشترط لاستخدامها أن تكون فوق 18 عامًا ولديك رقم جوال وهوية وبطاقة صالحة في السعودية أو الإمارات أو الكويت، مع اختلاف التوفر حسب المتجر.</p>
<p>وتختلف الخطط المتاحة (عدد الدفعات والحد الأدنى والأقصى للمبلغ) من متجر إلى آخر، فاقرأ ما يظهر لك عند الدفع.</p>

<h2>الإرجاع والاسترداد</h2>
<p>عند إرجاع منتج اشتريته بالتقسيط، تطلب الإرجاع من المتجر وفق سياسته، ثم يُبلغ المتجر شركة التقسيط فتُحدّث خطة الدفع وتُعيد المبلغ المستحق. انتبه إلى أن رسوم المعالجة قد لا تكون قابلة للاسترداد، وأن بعض المتاجر لا تعيد المبلغ إلا عبر خدمة التقسيط نفسها.</p>

<h2>هل يجتمع التقسيط مع كود الخصم؟</h2>
<p>غالبًا نعم، لأن الكود يُطبّق على قيمة السلة قبل اختيار طريقة الدفع. لكن العروض البنكية مسألة أخرى: كثير من الخصومات الفورية مشروطة بالدفع ببطاقة بنك معين، وقد لا تنطبق إذا اخترت التقسيط. اقرأ شروط العرض البنكي قبل أن تختار.</p>

<h2>متى يكون التقسيط قرارًا جيدًا؟</h2>
<ul>
<li>عندما تشتري شيئًا تحتاجه فعلًا وكنت ستشتريه في كل الأحوال.</li>
<li>عندما تعرف أن الدفعات القادمة تدخل في ميزانيتك الشهرية دون ضغط.</li>
<li>عندما تكون الخطة بلا رسوم، أو تكون الرسوم واضحة وتقبلها.</li>
</ul>
<h2>ومتى تتجنبه؟</h2>
<ul>
<li>إذا كان التقسيط هو ما يجعلك تشتري منتجًا لا تحتاجه.</li>
<li>إذا كان لديك أكثر من خطة مفتوحة وصعب عليك تتبّع مواعيدها.</li>
<li>إذا كان دخلك غير مستقر في الأشهر القادمة.</li>
</ul>
<p>نصيحة عملية: سجّل مواعيد الدفعات في تقويمك، وتأكد أن البطاقة المربوطة فيها رصيد كافٍ قبل كل موعد.</p>

<p class="note">المعلومات من الصفحات الرسمية لتابي وتمارا وقت كتابة الدليل، وقد تتغير الشروط والرسوم. راجع ما يظهر لك في صفحة الدفع قبل التأكيد. كوبون غير مرتبط بأي من الشركتين.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li>Tabby and Tamara let you split a purchase into instalments: the first at checkout, the rest monthly.</li>
<li>Both describe their plans as interest-free and Sharia-compliant, but some plans carry a processing fee, shown at checkout.</li>
<li>What happens if you pay late depends on the country and the plan, and repeated late payments can hurt your credit record.</li>
<li>Instalments are a way to spread a payment, not a reason to buy something you don’t need.</li>
</ul></div>

<h2>How it works</h2>
<p>At a participating store you choose Tabby or Tamara at checkout, sign up with your phone number and ID, and link a card. Approval usually takes moments. You pay the first instalment straight away and the rest are taken from your card on schedule. The store receives the full amount from the provider and pays the provider a fee, which is how these services mainly make money.</p>

<h2>Tabby</h2>
<p>Tabby’s Saudi site says you can split purchases into 3 or 4 monthly payments, online or in store. The first is collected at purchase and the rest on the same day each month. According to its FAQ, splitting in 3 carries no fees or interest, while splitting in 4 may carry a 1% processing fee, shown in your payment schedule before you confirm.</p>
<p>In December 2023, Tabby removed late fees on Pay in 4 in Saudi Arabia. Miss a payment and your account is paused for new purchases, and repeated late payments may be reported to credit bureaus. In the UAE, Tabby says customers may be charged collection fees for missed payments. Check the terms for your country specifically.</p>

<h2>Tamara</h2>
<p>Tamara lets you split purchases into several payments and describes itself as having no late fees and being Sharia-compliant. Its help centre explains that a processing fee may apply to payment plans, covering order processing, ID verification and credit checks. The fee is shown at checkout and spread across your payments. You need to be over 18, with a valid phone number, ID and payment card in Saudi Arabia, the UAE or Kuwait, and availability varies by store.</p>
<p>Plan options such as the number of payments and the minimum and maximum amounts vary between stores, so read what checkout shows you.</p>

<h2>Returns and refunds</h2>
<p>To return something bought in instalments, request the return from the store under its normal policy. The store notifies the provider, which updates your plan and refunds what’s due. Processing fees may not be refundable, and some stores will only refund through the instalment provider.</p>

<h2>Does it work with discount codes?</h2>
<p>Usually, yes. The code applies to your basket before you pick a payment method. Bank offers are different: many instant discounts require paying with a particular bank’s card and may not apply if you choose instalments. Read the bank offer’s terms first.</p>

<h2>When instalments make sense</h2>
<ul>
<li>You’re buying something you need and would have bought anyway.</li>
<li>The upcoming payments fit comfortably in your monthly budget.</li>
<li>The plan is fee-free, or the fee is clear and acceptable to you.</li>
</ul>
<h2>When to skip them</h2>
<ul>
<li>The instalments are the only reason you’re buying.</li>
<li>You already have several open plans and struggle to track due dates.</li>
<li>Your income over the next few months is uncertain.</li>
</ul>
<p>A practical habit: put each due date in your calendar, and make sure the linked card has funds before every payment.</p>

<p class="note">Information is from Tabby’s and Tamara’s official pages at the time of writing. Terms and fees can change, so check what checkout shows you before confirming. Kobon isn’t affiliated with either company.</p>
""",
})

GUIDES.append({
"slug": "online-returns-saudi",
"updated": "2026-11-09",
"title_ar": "حقك في الإرجاع والإلغاء عند الشراء أونلاين في السعودية",
"title_en": "Your right to return or cancel an online purchase in Saudi Arabia",
"desc_ar": "ما يقوله نظام التجارة الإلكترونية السعودي عن مهلة الأيام السبعة، والحالات المستثناة، وحقك إذا تأخر التوصيل أكثر من 15 يومًا.",
"desc_en": "What Saudi Arabia’s E-Commerce Law says about the seven-day window, the exceptions, and your rights if delivery is more than 15 days late.",
"tag_ar": "حقوق المتسوق", "tag_en": "Shopper rights",
"sources": [
 ("https://misa.gov.sa/app/uploads/2025/07/E-Commerce-Law.pdf", "Saudi E-Commerce Law (English translation, MISA)"),
 ("https://mc.gov.sa/en/mediacenter/News/Pages/10-07-19-01.aspx", "Ministry of Commerce: services provided online are covered by the E-Commerce Law"),
 ("https://mc.gov.sa/en/guides/Documents/CustomerGuide.pdf", "Ministry of Commerce: Guide to Consumer Rights and Responsibilities"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li>يحق لك فسخ عقد الشراء الإلكتروني خلال <b>7 أيام</b> من تاريخ استلام المنتج، بشرط ألا تكون استخدمته أو انتفعت به.</li>
<li>تتحمل أنت تكلفة الإرجاع في هذه الحالة ما لم يُتفق على غير ذلك.</li>
<li>هناك استثناءات، منها المنتجات المصنوعة حسب الطلب، والكتب والمجلات، وخدمات السكن والنقل والإعاشة.</li>
<li>إذا تأخر التسليم أكثر من <b>15 يومًا</b> من تاريخ العقد أو الموعد المتفق عليه، يحق لك الفسخ واسترداد ما دفعته، ما لم يكن التأخير لقوة قاهرة.</li>
</ul></div>

<h2>ما النظام الذي يحميك؟</h2>
<p>يُنظم الشراء من المتاجر الإلكترونية في السعودية نظامُ التجارة الإلكترونية ولائحته التنفيذية. ويشمل النظام المتاجر داخل المملكة، وكذلك من يقدّم منتجات أو خدمات للمستهلكين في المملكة من خارجها بطريقة تتيح لهم الوصول إليها. أي أن المتجر الذي يستهدفك بموقعه وخدماته داخل السعودية معنيّ بهذه الأحكام.</p>

<h2>مهلة الأيام السبعة</h2>
<p>تنص المادة الثالثة عشرة من النظام على أن للمستهلك فسخ العقد خلال سبعة أيام من تاريخ استلام المنتج، أو من تاريخ التعاقد على الخدمة، بشرط ألا يكون قد استخدم المنتج أو استفاد من الخدمة. وفي هذه الحالة يتحمل المستهلك تكاليف الفسخ، ما لم يتفق الطرفان على خلاف ذلك.</p>
<p>هذا هو الحد الأدنى الذي يضمنه النظام. كثير من المتاجر تقدّم سياسة أكرم، مثل 14 أو 30 يومًا للإرجاع، أو إرجاعًا مجانيًا. اقرأ سياسة المتجر، فإن كانت أفضل لك فهي التي تُطبّق.</p>

<h2>الحالات المستثناة</h2>
<p>لا يحق الفسخ خلال المهلة في حالات حددها النظام، منها:</p>
<ul>
<li>المنتج المصنوع أو المخصص بناءً على طلبك، إلا إذا كان معيبًا أو مخالفًا للمواصفات المتفق عليها.</li>
<li>أشرطة الفيديو والأسطوانات وبرامج الحاسب إذا فُتحت أو استُخدمت.</li>
<li>الصحف والمجلات والكتب والمطبوعات.</li>
<li>العيب الناتج عن سوء استخدام المستهلك.</li>
<li>خدمات السكن والنقل والإعاشة.</li>
<li>البرامج التي تُحمّل من الإنترنت، إلا إذا كانت معيبة أو لا يمكن تحميلها أو مخالفة للمواصفات.</li>
</ul>
<p>وتضيف اللائحة التنفيذية حالات أخرى بحسب طبيعة المنتج، مثل المنتجات التي يُحتمل أن تتلف خلال مدة الفسخ، والمنتجات التي لا يمكن إعادة بيعها لأسباب صحية. لذلك قد لا تتمكن من إرجاع منتجات عناية شخصية فُتحت.</p>

<h2>إذا تأخر التوصيل</h2>
<p>تمنحك المادة الرابعة عشرة حقًا منفصلًا: إذا تأخر المتجر في التسليم أكثر من 15 يومًا من تاريخ إبرام العقد أو من الموعد المتفق عليه، يحق لك فسخ العقد واسترداد ما دفعته، إضافة إلى أي تكاليف ترتبت على التأخير، ما لم يكن التأخير بسبب قوة قاهرة. كما يلزم النظام المتجر بإبلاغك بأي تأخير متوقع يؤثر في التسليم.</p>
<p>انتبه: إذا وافقت على موعد تسليم أبعد عند الشراء، يُحسب التأخير من ذلك الموعد.</p>

<h2>المنتج المعيب أو المختلف</h2>
<p>مهلة الأيام السبعة لا تلغي حقوقك في الضمان. إذا وصلك منتج معيب أو مختلف عن الوصف، فهذه حالة مختلفة عن «غيّرت رأيي»، ويجب ألا تتحمل تكلفتها. وثّق المشكلة بالصور فور الاستلام، وتواصل مع المتجر كتابيًا.</p>

<h2>خطوات عملية للإرجاع</h2>
<ol>
<li><b>احتفظ بالفاتورة الإلكترونية</b>، فهي تثبت تاريخ الشراء والسعر وشروط التسليم.</li>
<li><b>لا تستخدم المنتج</b> إذا كنت تفكر في إرجاعه، واحتفظ بالتغليف الأصلي.</li>
<li><b>اطلب الإرجاع كتابيًا</b> عبر حسابك في المتجر أو البريد، واحفظ رقم الطلب والمراسلات.</li>
<li><b>صوّر المنتج</b> عند الاستلام وعند الإرجاع.</li>
<li><b>تابع الاسترداد</b>: إذا دفعت بالتقسيط، فتأكد أن شركة التقسيط حدّثت خطتك.</li>
</ol>

<h2>إذا رفض المتجر</h2>
<p>ابدأ بخدمة العملاء واطلب التصعيد كتابيًا. وإذا لم تُحل المشكلة، يمكنك تقديم بلاغ لوزارة التجارة عبر قنواتها الرسمية، مع إرفاق الفاتورة والمراسلات.</p>

<h2>ماذا عن المتاجر العالمية؟</h2>
<p>إذا كان المتجر في الخارج، فقد تكون إعادة المنتج مكلفة، وقد لا تُسترد الضرائب والرسوم المدفوعة عند الاستيراد بسهولة. اقرأ سياسة الإرجاع الدولية قبل الشراء، وراجع دليلنا عن الشحن والجمارك.</p>

<p class="note">هذا الدليل للتوعية وليس استشارة قانونية. النص العربي للنظام هو المرجع المعتمد.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li>You can cancel an online purchase within <b>7 days</b> of receiving the product, provided you haven’t used it.</li>
<li>You pay the cost of returning it in that case, unless agreed otherwise.</li>
<li>There are exceptions, including made-to-order items, books and magazines, and accommodation, transport and catering services.</li>
<li>If delivery is more than <b>15 days</b> late against the contract date or agreed date, you can cancel and get your money back, unless the delay is due to force majeure.</li>
</ul></div>

<h2>Which law protects you?</h2>
<p>Online shopping in Saudi Arabia is governed by the E-Commerce Law and its Implementing Regulations. The law covers stores based in the Kingdom and also businesses abroad that offer products or services to consumers in the Kingdom in a way that lets them buy. In other words, a store that targets you in Saudi Arabia is bound by these rules.</p>

<h2>The seven-day window</h2>
<p>Article 13 lets a consumer rescind the contract within seven days of receiving the product, or of the service contract date, provided they haven’t used the product or benefited from the service. In that case the consumer bears the cost of cancelling, unless the parties agree otherwise.</p>
<p>That’s the legal minimum. Many stores go further, with 14- or 30-day returns or free return shipping. Read the store’s policy: if it’s better for you, it’s the one that applies.</p>

<h2>What’s excluded</h2>
<p>The law lists cases where the seven-day right doesn’t apply, including:</p>
<ul>
<li>Items customised or made to your order, unless they’re defective or don’t match the agreed specification.</li>
<li>Video tapes, records, CDs or software that have been opened or used.</li>
<li>Newspapers, magazines, books and other publications.</li>
<li>Defects caused by the consumer’s mishandling.</li>
<li>Accommodation, transport and catering services.</li>
<li>Downloadable software, unless it’s faulty, can’t be downloaded or doesn’t match the specification.</li>
</ul>
<p>The Implementing Regulations add cases based on the nature of the product, such as goods likely to deteriorate during the cancellation period and goods that can’t be resold for health reasons. So opened personal-care items may not be returnable.</p>

<h2>When delivery is late</h2>
<p>Article 14 gives you a separate right. If the store delays delivery by more than 15 days from the contract date or the agreed date, you can rescind the contract and recover what you paid, plus any costs the delay caused, unless the delay is due to force majeure. The store must also tell you about any expected delay that materially affects delivery.</p>
<p>Note that if you accepted a later delivery date when ordering, the 15 days count from that date.</p>

<h2>Defective or not as described</h2>
<p>The seven-day window doesn’t replace your warranty rights. A faulty item, or one that doesn’t match its description, is a different case from changing your mind, and you shouldn’t bear the cost. Photograph the problem as soon as it arrives and contact the store in writing.</p>

<h2>Practical steps</h2>
<ol>
<li><b>Keep the e-invoice.</b> It proves the purchase date, price and delivery terms.</li>
<li><b>Don’t use the item</b> if you might return it, and keep the original packaging.</li>
<li><b>Request the return in writing</b> through your account or by email, and keep the order number and messages.</li>
<li><b>Photograph the item</b> on arrival and when you send it back.</li>
<li><b>Follow up on the refund.</b> If you paid in instalments, make sure the provider has updated your plan.</li>
</ol>

<h2>If the store refuses</h2>
<p>Start with customer service and ask for escalation in writing. If that doesn’t resolve it, you can file a complaint with the Ministry of Commerce through its official channels, attaching the invoice and your correspondence.</p>

<h2>International stores</h2>
<p>If the store is abroad, sending items back can be expensive, and import taxes and fees may be hard to recover. Read the international return policy before you buy, and see our shipping and customs guide.</p>

<p class="note">This guide is general information, not legal advice. The Arabic text of the law is the authoritative version.</p>
""",
})

GUIDES.append({
"slug": "ramadan-2027-shopping",
"updated": "2026-11-09",
"title_ar": "خطة تسوّق رمضان 2027: المواعيد المتوقعة وكيف تستعد مبكرًا",
"title_en": "Planning your Ramadan 2027 shopping: expected dates and how to start early",
"desc_ar": "متى يبدأ رمضان 2027 فلكيًا، ومتى تتوقع عيد الفطر، وكيف تقسّم مشترياتك بين المقاضي والهدايا والملابس دون ضغط اللحظة الأخيرة.",
"desc_en": "When Ramadan 2027 is expected to start, when Eid al-Fitr may fall, and how to split groceries, gifts and Eid clothes without a last-minute rush.",
"tag_ar": "مواسم", "tag_en": "Seasons",
"sources": [
 ("https://gulfnews.com/uae/ramadan/when-is-ramadan-2027-the-expected-date-moon-sighting-and-eid-explained-1.500630523", "Gulf News: Ramadan 2027 expected date and Eid explained"),
 ("https://mc.gov.sa/ar/mediacenter/News/Pages/09-02-26-01.aspx", "وزارة التجارة: تراخيص موسم تخفيضات رمضان (فبراير 2026)"),
 ("https://mc.gov.sa/Pages/dvs.aspx", "Saudi Ministry of Commerce: document verification service"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li>تشير الحسابات الفلكية إلى أن رمضان 1448 هـ يبدأ نحو <b>الاثنين 8 فبراير 2027</b>، والموعد الرسمي يُعلن بعد تحري الهلال.</li>
<li>يُتوقع عيد الفطر في <b>9 أو 10 مارس 2027</b> بحسب تمام الشهر.</li>
<li>ابدأ المقاضي قبل الشهر بأسبوعين، واطلب ملابس العيد والهدايا قبل العشر الأواخر.</li>
<li>في السعودية، تحقق من ترخيص التخفيضات قبل الشراء.</li>
</ul></div>

<h2>متى يبدأ رمضان 2027؟</h2>
<p>وفق الحسابات الفلكية التي نشرتها وسائل إعلام خليجية، يُتوقع أن يبدأ رمضان يوم الاثنين 8 فبراير 2027. لكن بداية الشهر في دول الخليج تُعلن رسميًا بعد تحري الهلال، فقد يختلف الموعد بيوم. وإذا كان الشهر 29 يومًا فالعيد الثلاثاء 9 مارس، وإن أتم ثلاثين فالعيد الأربعاء 10 مارس.</p>
<p>هذه المواعيد كافية للتخطيط. لا تنتظر الإعلان الرسمي لتبدأ، فأفضل العروض والأسعار المستقرة تكون عادةً قبل الزحام.</p>

<h2>المرحلة الأولى: قبل رمضان بأسبوعين إلى ثلاثة</h2>
<p>هذا وقت المقاضي الأساسية التي لا تتلف بسرعة: الأرز والسكر والزيوت والتمور والبقوليات والمعلبات ومستلزمات المطبخ. في هذه الفترة تبدأ متاجر البقالة وتطبيقات التوصيل عروض «استعد لرمضان» عادة.</p>
<ul>
<li><b>اكتب قائمة حسب عدد أفراد الأسرة</b> وعدد الأيام، بدل الشراء بالكميات الكبيرة دون حساب.</li>
<li><b>قارن سعر الوحدة</b> (لكل كيلو أو لتر)، لا سعر العبوة فقط؛ العبوة الكبيرة ليست دائمًا الأرخص.</li>
<li><b>انتبه لتاريخ الصلاحية</b> في عروض الكميات.</li>
<li><b>استخدم أكواد الطلب الأول</b> في تطبيقات البقالة إن كنت عميلًا جديدًا، واقرأ حدها الأدنى ورسوم التوصيل.</li>
</ul>

<h2>المرحلة الثانية: الأسبوعان الأولان من رمضان</h2>
<p>ركّز على المشتريات المنزلية والأجهزة التي تحتاجها خلال الشهر، وعلى الهدايا إن كنت تريد إرسالها مبكرًا. كثير من المتاجر تطلق عروضها الكبرى في بداية الشهر، فقارن الأسعار بما سجّلته قبل رمضان.</p>
<p>وفي السعودية تصدر وزارة التجارة تراخيص التخفيضات الموسمية؛ ففي فبراير 2026 مثلًا أعلنت الوزارة إصدار 1,987 ترخيصًا لموسم تخفيضات رمضان. يمكنك التحقق من أي ترخيص بمسح الباركود الظاهر عليه أو عبر خدمة التحقق من الوثائق في موقع الوزارة.</p>

<h2>المرحلة الثالثة: قبل العشر الأواخر</h2>
<p>هذه أهم نقطة في الخطة: <b>اطلب ملابس العيد والهدايا قبل العشر الأواخر</b>. ضغط الطلبات على المتاجر وشركات الشحن يرتفع كثيرًا في الأيام الأخيرة، وقد يتأخر التوصيل أو تنفد المقاسات. وإذا كنت تشتري من متجر عالمي، فأضف وقتًا إضافيًا للشحن الدولي والتخليص الجمركي.</p>
<ul>
<li>تحقق من «آخر موعد للطلب للتوصيل قبل العيد» الذي تعلنه بعض المتاجر.</li>
<li>راجع سياسة الاستبدال للملابس والهدايا، خاصة إن كنت لا تعرف المقاس بدقة.</li>
<li>تجنب الاعتماد على التوصيل في آخر يومين.</li>
</ul>

<h2>ميزانية الشهر</h2>
<p>رمضان والعيد معًا من أعلى مواسم الإنفاق في العام. قسّم ميزانيتك إلى ثلاثة بنود: المقاضي، والبيت والهدايا، والعيد. وإذا قررت استخدام التقسيط، فاحسب أن دفعاته ستمتد إلى ما بعد العيد، واقرأ دليلنا عن تابي وتمارا قبل أن تقرر.</p>

<h2>نصائح سريعة لتوفير أكثر</h2>
<ul>
<li>اشترك في تنبيهات المتاجر التي تتسوق منها فعلًا، لا في كل المتاجر.</li>
<li>اجمع طلباتك من المتجر الواحد لتصل إلى حد الشحن المجاني.</li>
<li>قارن العرض البنكي مع كود الخصم، واختر ما يعطيك سعرًا نهائيًا أقل.</li>
<li>لا تشترِ بسبب العدّ التنازلي؛ اشترِ لأن المنتج في قائمتك وسعره جيد.</li>
</ul>

<h2>كيف نتعامل مع الموسم في كوبون</h2>
<p>سنضيف عروض رمضان الرسمية فور صدورها من المتاجر أو برامج الشركاء المعتمدة، مع شروط كل عرض وتاريخ آخر تحقق. وسنحدّث هذا الدليل بالموعد الرسمي فور إعلانه.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li>Astronomical calculations put the start of Ramadan 1448 AH at about <b>Monday 8 February 2027</b>. The official date is announced after the moon sighting.</li>
<li>Eid al-Fitr is expected on <b>9 or 10 March 2027</b>, depending on the length of the month.</li>
<li>Start grocery shopping two weeks before Ramadan, and order Eid clothes and gifts before the last ten nights.</li>
<li>In Saudi Arabia, check that a sale is licensed before you buy.</li>
</ul></div>

<h2>When does Ramadan 2027 start?</h2>
<p>Based on astronomical calculations reported by Gulf media, Ramadan is expected to begin on Monday 8 February 2027. Gulf countries announce the start officially after the moon sighting, so it can move by a day. If the month runs 29 days, Eid falls on Tuesday 9 March; if it runs 30, on Wednesday 10 March.</p>
<p>That’s enough to plan with. Don’t wait for the announcement to get started: the steadiest prices and best deals usually come before the rush.</p>

<h2>Phase one: two to three weeks before Ramadan</h2>
<p>This is the time for staples that keep well: rice, sugar, oil, dates, pulses, tinned goods and kitchen basics. Grocery stores and delivery apps typically launch their “get ready for Ramadan” promotions around now.</p>
<ul>
<li><b>Plan by household size</b> and number of days, rather than buying in bulk without a plan.</li>
<li><b>Compare unit prices</b> per kilo or litre, not pack prices. The big pack isn’t always cheaper.</li>
<li><b>Check expiry dates</b> on multi-buy offers.</li>
<li><b>Use first-order codes</b> on grocery apps if you’re a new customer, and check the minimum order and delivery fee.</li>
</ul>

<h2>Phase two: the first two weeks of Ramadan</h2>
<p>Turn to household items and appliances you’ll need during the month, and to gifts if you want to send them early. Many stores run their biggest promotions at the start of the month, so compare against the prices you noted beforehand.</p>
<p>In Saudi Arabia, the Ministry of Commerce licenses seasonal sales. In February 2026, for example, it announced 1,987 licences for the Ramadan sale season. You can check any licence by scanning its barcode or through the Ministry’s document verification service.</p>

<h2>Phase three: before the last ten nights</h2>
<p>This is the part of the plan that matters most: <b>order Eid clothes and gifts before the last ten nights</b>. Stores and couriers get very busy in the final days, deliveries slip and sizes sell out. If you’re ordering from an international store, add extra time for shipping and customs clearance.</p>
<ul>
<li>Look for a “last order date for delivery before Eid”, which some stores publish.</li>
<li>Check the exchange policy for clothes and gifts, especially if you’re unsure of sizes.</li>
<li>Don’t count on delivery in the last two days.</li>
</ul>

<h2>Budgeting for the month</h2>
<p>Ramadan and Eid together are among the biggest spending periods of the year. Split your budget three ways: groceries, home and gifts, and Eid. If you use instalments, remember the payments will run past Eid, and read our Tabby and Tamara guide before deciding.</p>

<h2>Quick ways to save more</h2>
<ul>
<li>Subscribe to alerts from the stores you actually use, not every store.</li>
<li>Combine orders from one store to reach free delivery.</li>
<li>Compare the bank offer with the discount code and pick whichever gives the lower final price.</li>
<li>Don’t buy because of a countdown. Buy because the item is on your list and the price is right.</li>
</ul>

<h2>How Kobon handles the season</h2>
<p>We’ll add official Ramadan offers as soon as stores or approved partner programmes release them, each with its terms and last-checked date. We’ll also update this guide with the official start date once it’s announced.</p>
""",
})

GUIDES.append({
"slug": "gcc-vat-prices",
"updated": "2026-11-09",
"title_ar": "ضريبة القيمة المضافة في الخليج: كيف تؤثر على السعر الذي تدفعه",
"title_en": "VAT in the Gulf: how it affects the price you pay",
"desc_ar": "نسب ضريبة القيمة المضافة في السعودية والإمارات والبحرين وعُمان، ولماذا لا تُطبّق في الكويت وقطر، وكيف تحسب أثرها على الخصم والطلبات من الخارج.",
"desc_en": "VAT rates in Saudi Arabia, the UAE, Bahrain and Oman, why Kuwait and Qatar don’t charge it, and how it affects discounts and orders from abroad.",
"tag_ar": "أساسيات", "tag_en": "Basics",
"sources": [
 ("https://zatca.gov.sa/en/RulesRegulations/Taxes/Pages/customs-individual/e-stores-customers.aspx", "ZATCA: E-store customers (VAT on imports)"),
 ("https://www.pwc.com/m1/en/tax/documents/2026/gcc-indirect-tax-news-roundup-quarter-one-2026.pdf", "PwC: GCC indirect tax news roundup, Q1 2026"),
 ("https://u.ae/en/information-and-services/finance-and-investment/taxation/clearing-the-customs-and-paying-customs-duty", "UAE Government portal: customs duty and tariff"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li>نسب ضريبة القيمة المضافة الأساسية: <b>السعودية 15%</b>، <b>البحرين 10%</b>، <b>الإمارات 5%</b>، <b>عُمان 5%</b>.</li>
<li>لم تطبّق <b>الكويت وقطر</b> ضريبة القيمة المضافة حتى الآن.</li>
<li>الضريبة تُطبّق على الواردات أيضًا، حتى عندما تُعفى الشحنة من الرسوم الجمركية.</li>
<li>خصم الكود يُحسب عادة على السعر شامل الضريبة، فاقرأ ملخص الطلب لتعرف المبلغ النهائي.</li>
</ul></div>

<h2>ما هي ضريبة القيمة المضافة؟</h2>
<p>ضريبة القيمة المضافة ضريبة على الاستهلاك، تُفرض على معظم السلع والخدمات في كل مرحلة من مراحل البيع، ويتحملها المستهلك في النهاية ضمن السعر الذي يدفعه. اتفقت دول مجلس التعاون على إطار موحد لها، لكن كل دولة قررت توقيت تطبيقها ونسبتها، ولهذا تختلف الأسعار النهائية للمنتج نفسه من دولة خليجية إلى أخرى.</p>

<h2>النسب في دول الخليج</h2>
<table><thead><tr><th>الدولة</th><th>النسبة الأساسية</th></tr></thead><tbody>
<tr><td>السعودية</td><td>15%</td></tr>
<tr><td>البحرين</td><td>10%</td></tr>
<tr><td>الإمارات</td><td>5%</td></tr>
<tr><td>عُمان</td><td>5%</td></tr>
<tr><td>الكويت</td><td>غير مطبّقة</td></tr>
<tr><td>قطر</td><td>غير مطبّقة</td></tr>
</tbody></table>
<p>هذه هي النسب الأساسية. بعض السلع والخدمات لها معاملة خاصة، كالإعفاء أو النسبة الصفرية، بحسب نظام كل دولة. والنسب قد تتغير بقرارات حكومية، فراجع الجهة الضريبية في بلدك عند الحاجة.</p>

<h2>هل السعر المعروض شامل الضريبة؟</h2>
<p>في المتاجر التي تبيع للمستهلكين داخل الدولة، يُعرض السعر عادة شاملًا الضريبة. لكن في المتاجر العالمية قد يظهر السعر دون ضريبة الاستيراد، وتُضاف الضريبة لاحقًا عند الدفع أو عند التسليم. اقرأ ملخص الطلب قبل الدفع، وابحث عن عبارة «شامل الضريبة» أو «الضرائب والرسوم مشمولة».</p>

<h2>الضريبة على الطلبات من الخارج</h2>
<p>هذه النقطة يغفل عنها كثيرون: إعفاء الشحنة من الرسوم الجمركية لا يعني إعفاءها من ضريبة القيمة المضافة. في السعودية مثلًا، توضح هيئة الزكاة والضريبة والجمارك أن ضريبة القيمة المضافة تُحصّل على الواردات بغض النظر عن قيمة الشحنة، إلا ما استثناه النظام، وتُحسب على قيمة البضاعة والشحن والتأمين والرسوم. وكذلك في الإمارات تُطبّق الضريبة على السلع المستوردة. لذلك أضف الضريبة دائمًا عند مقارنة متجر عالمي بمتجر محلي.</p>

<h2>كيف تتعامل الضريبة مع كود الخصم؟</h2>
<p>الطريقة الشائعة أن يُخصم الكود من سعر المنتج، ثم تُحسب الضريبة على المبلغ بعد الخصم، فيظهر السعر النهائي أقل بالنسبة نفسها تقريبًا. لكن طريقة العرض تختلف من متجر إلى آخر. المهم أن تنظر إلى «الإجمالي المستحق» في ملخص الطلب، لا إلى نسبة الخصم المكتوبة.</p>
<p><b>مثال توضيحي في السعودية:</b> منتج سعره 230 ريالًا شامل الضريبة. كود خصم 10% يخفّضه إلى 207 ريالات شامل الضريبة. الخصم الفعلي الذي وفّرته 23 ريالًا، منها جزء كان سيذهب ضريبة.</p>

<h2>هل الشراء من دولة خليجية أخرى أرخص؟</h2>
<p>قد يبدو المنتج أرخص في متجر بدولة ذات ضريبة أقل، لكن الطلب عبر الحدود قد يخضع لضريبة الدولة التي تستلم فيها، إضافة إلى الشحن وإجراءات التخليص. في أغلب الحالات، الأبسط والأوضح أن تشتري من نسخة المتجر المخصصة لبلدك، لأن السعر والضمان وسياسة الإرجاع مصممة لها.</p>

<h2>نصائح عملية</h2>
<ul>
<li><b>قارن الأسعار النهائية</b> شاملة الضريبة والشحن، لا الأسعار قبلها.</li>
<li><b>اطلب فاتورة ضريبية</b> واحتفظ بها، فهي مهمة للضمان والإرجاع.</li>
<li><b>انتبه للسعر «قبل الضريبة»</b> في بعض المتاجر الموجهة للشركات.</li>
<li><b>في الطلبات الدولية</b>، اختر الدفع المسبق للرسوم والضرائب إن توفر، لتعرف التكلفة كاملة قبل الشراء.</li>
</ul>

<p class="note">هذا الدليل للتوعية العامة وليس استشارة ضريبية. المرجع النهائي هو الجهة الضريبية الرسمية في بلدك.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li>Standard VAT rates: <b>Saudi Arabia 15%</b>, <b>Bahrain 10%</b>, <b>UAE 5%</b>, <b>Oman 5%</b>.</li>
<li><b>Kuwait and Qatar</b> haven’t introduced VAT.</li>
<li>VAT applies to imports too, even when a parcel is exempt from customs duty.</li>
<li>Code discounts are usually shown against VAT-inclusive prices, so check the order summary for the real total.</li>
</ul></div>

<h2>What VAT is</h2>
<p>Value added tax is a consumption tax charged on most goods and services at each stage of sale, and ultimately paid by the shopper as part of the price. GCC states agreed a common framework, but each country chose its own timing and rate, which is why the same product can end up costing different amounts across the Gulf.</p>

<h2>Rates across the Gulf</h2>
<table><thead><tr><th>Country</th><th>Standard rate</th></tr></thead><tbody>
<tr><td>Saudi Arabia</td><td>15%</td></tr>
<tr><td>Bahrain</td><td>10%</td></tr>
<tr><td>UAE</td><td>5%</td></tr>
<tr><td>Oman</td><td>5%</td></tr>
<tr><td>Kuwait</td><td>Not introduced</td></tr>
<tr><td>Qatar</td><td>Not introduced</td></tr>
</tbody></table>
<p>These are standard rates. Some goods and services are exempt or zero-rated under each country’s rules, and rates can change by government decision, so check your national tax authority if it matters.</p>

<h2>Is the price VAT-inclusive?</h2>
<p>Stores selling to consumers inside a country normally show prices including VAT. International stores may show a price without import VAT, adding it at checkout or on delivery. Check the order summary before you pay and look for “VAT included” or “duties and taxes included”.</p>

<h2>VAT on orders from abroad</h2>
<p>This is the bit people miss: a parcel exempt from customs duty isn’t exempt from VAT. In Saudi Arabia, ZATCA says VAT is collected on imports regardless of the shipment’s value, except where the VAT rules exclude it, and is calculated on the goods, shipping, insurance and fees. The UAE likewise charges VAT on imported goods. Always add VAT when comparing an international store with a local one.</p>

<h2>How VAT interacts with a discount code</h2>
<p>Typically the code comes off the item price and VAT is calculated on the discounted amount, so the final price drops by roughly the same percentage. Stores display this differently, though. What matters is the “total due” in the order summary, not the percentage on the code.</p>
<p><b>Example in Saudi Arabia:</b> an item costs SAR 230 including VAT. A 10% code brings it to SAR 207 including VAT. You save SAR 23 in total, part of which would have gone to tax.</p>

<h2>Is it cheaper to buy from another Gulf country?</h2>
<p>A product can look cheaper on a store in a lower-VAT country, but a cross-border order may be taxed in the country where you receive it, on top of shipping and clearance. In most cases it’s simpler and clearer to buy from the store’s version for your own country, where the price, warranty and returns are designed for you.</p>

<h2>Practical tips</h2>
<ul>
<li><b>Compare final prices</b> including VAT and shipping, not pre-tax prices.</li>
<li><b>Ask for a tax invoice</b> and keep it. You’ll need it for warranty claims and returns.</li>
<li><b>Watch for pre-VAT prices</b> on stores aimed at businesses.</li>
<li><b>On international orders</b>, prepay duties and taxes when offered, so you know the full cost up front.</li>
</ul>

<p class="note">This guide is general information, not tax advice. Your national tax authority has the final word.</p>
""",
})

GUIDES.append({
"slug": "fake-discounts",
"updated": "2026-11-09",
"title_ar": "كيف تكشف الخصم الوهمي: السعر المرجعي والعدّ التنازلي وحيل أخرى",
"title_en": "How to spot a fake discount: reference prices, countdowns and other tricks",
"desc_ar": "علامات تدل على أن الخصم أقل مما يبدو، وطريقة بسيطة لمعرفة السعر الحقيقي، وكيف تتحقق من ترخيص التخفيضات في السعودية.",
"desc_en": "Signs a discount is smaller than it looks, a simple way to find the real price, and how to check a sale licence in Saudi Arabia.",
"tag_ar": "أساسيات", "tag_en": "Basics",
"sources": [
 ("https://mc.gov.sa/Pages/dvs.aspx", "Saudi Ministry of Commerce: document verification service"),
 ("https://mc.gov.sa/en/mediacenter/News/Pages/19-09-23-01.aspx", "Ministry of Commerce: verifying promotions by scanning the barcode"),
 ("https://mc.gov.sa/en/guides/Documents/CustomerGuide.pdf", "Ministry of Commerce: Guide to Consumer Rights and Responsibilities"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li>نسبة الخصم تُقاس على «السعر قبل الخصم»، وهذا السعر قد يكون مرتفعًا أصلًا.</li>
<li>أفضل مرجع هو السعر الذي سجّلته بنفسك قبل الموسم، أو سعر المنتج نفسه في متاجر أخرى.</li>
<li>العدّ التنازلي و«بقيت قطعتان» أدوات ضغط، وليست دليلًا على عرض جيد.</li>
<li>في السعودية يمكنك التحقق من ترخيص التخفيضات بمسح الباركود أو عبر موقع وزارة التجارة.</li>
</ul></div>

<h2>كيف يبدو الخصم أكبر مما هو؟</h2>
<p>كل خصم يُحسب من سعر مرجعي. إذا كان هذا السعر مبالغًا فيه، تبدو النسبة كبيرة بينما السعر النهائي عادي. لهذا قد ترى «خصم 60%» على منتج يُباع طوال العام بالسعر نفسه تقريبًا بعد الخصم. ليس كل خصم كبير وهميًا، لكن النسبة وحدها لا تكفي للحكم.</p>

<h2>الحيل الأكثر شيوعًا</h2>
<ul>
<li><b>رفع السعر قبل الموسم:</b> يرتفع السعر قبل التخفيضات بأسابيع، ثم «ينخفض» إلى ما كان عليه.</li>
<li><b>سعر مرجعي لم يُبع به المنتج فعلًا:</b> سعر مشطوب لا يعكس ما دفعه الناس في الواقع.</li>
<li><b>«خصم يصل إلى»:</b> النسبة القصوى تنطبق على عدد قليل من المنتجات، والباقي بخصم أقل بكثير.</li>
<li><b>العدّ التنازلي المتجدد:</b> عدّاد ينتهي ثم يبدأ من جديد عند تحديث الصفحة.</li>
<li><b>«بقيت قطعة واحدة»:</b> رسائل ندرة تدفعك للشراء دون مقارنة.</li>
<li><b>الخصم على الحزمة:</b> «اشترِ 3 وادفع 2» مفيد فقط إذا كنت تحتاج الثلاثة.</li>
<li><b>رسوم تظهر في النهاية:</b> سعر منخفض في الصفحة، ثم شحن ورسوم خدمة في صفحة الدفع.</li>
</ul>

<h2>طريقة بسيطة لمعرفة السعر الحقيقي</h2>
<ol>
<li><b>سجّل السعر قبل الموسم:</b> صورة للصفحة مع التاريخ تكفي. هذا أقوى مرجع لديك.</li>
<li><b>قارن بين متجرين أو ثلاثة</b> للمنتج نفسه بالمواصفات نفسها، وانتبه لاختلاف الطراز أو السعة أو النسخة الإقليمية.</li>
<li><b>احسب السعر النهائي</b> بعد الشحن والرسوم والضريبة، لا السعر في صفحة المنتج.</li>
<li><b>اسأل نفسك:</b> لو لم يكن هناك خصم، هل كنت سأشتري هذا المنتج بهذا السعر؟</li>
</ol>

<h2>التحقق من ترخيص التخفيضات في السعودية</h2>
<p>تنظم وزارة التجارة في السعودية التخفيضات، وتتطلب ترخيصًا لها. وقد أتاحت الوزارة التحقق من العروض بمسح الباركود الظاهر على الترخيص بكاميرا الجوال، لمعرفة نوع التخفيض ونسبته ومدته وبيانات المنشأة. كما يمكنك التحقق عبر خدمة التحقق من الوثائق في موقع الوزارة. إذا لم تجد ترخيصًا لتخفيضات معلنة في متجر، أو وجدت بياناته مختلفة عما يُعرض، فهذه علامة تستحق الانتباه.</p>

<h2>العروض البنكية والاسترداد النقدي</h2>
<p>الاسترداد النقدي ليس خصمًا فوريًا؛ يُضاف لاحقًا، وغالبًا بحد أقصى وشروط. احسبه كتوفير فقط إذا كنت متأكدًا من استيفاء الشروط. وكذلك النقاط وبطاقات الهدايا: قيمتها حقيقية فقط إذا كنت ستستخدمها فعلًا.</p>

<h2>إذا شعرت أن العرض مضلل</h2>
<p>احتفظ بصور للصفحة قبل الموسم وأثناءه، وتواصل مع المتجر. وفي السعودية يمكنك الإبلاغ عن المخالفات لوزارة التجارة عبر قنواتها الرسمية. وفي كل الأحوال، أفضل حماية هي ألا تشتري تحت الضغط.</p>

<h2>معيارنا في كوبون</h2>
<p>لا ننشر عدًّا تنازليًا وهميًا، ولا نبالغ في وصف الخصومات، ولا نعرض أرقام توفير غير حقيقية. لكل عرض ننشره مصدر رسمي وشروط مكتوبة وتاريخ آخر تحقق، حتى تحكم بنفسك.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li>A discount percentage is measured against a “was” price, and that price may have been high to begin with.</li>
<li>The best benchmark is a price you recorded yourself before the sale, or the same item at other stores.</li>
<li>Countdowns and “only 2 left” are pressure tactics, not proof of a good deal.</li>
<li>In Saudi Arabia you can check a sale licence by scanning its barcode or on the Ministry of Commerce website.</li>
</ul></div>

<h2>How a discount can look bigger than it is</h2>
<p>Every discount is calculated from a reference price. Inflate that price and the percentage looks impressive while the final price is ordinary. That’s how you get “60% off” on something that sells for about the same all year. Not every big discount is fake, but the percentage alone tells you very little.</p>

<h2>The most common tricks</h2>
<ul>
<li><b>Pre-sale price rises:</b> the price climbs a few weeks before the sale, then “drops” back to where it was.</li>
<li><b>A “was” price nobody paid:</b> a crossed-out figure that doesn’t reflect what the item actually sold for.</li>
<li><b>“Up to” discounts:</b> the headline percentage covers a handful of items; the rest get far less.</li>
<li><b>Resetting countdowns:</b> a timer that runs out, then starts again when you reload.</li>
<li><b>“Only one left”:</b> scarcity messages that rush you past comparison.</li>
<li><b>Bundle deals:</b> “buy 3, pay for 2” only helps if you need all three.</li>
<li><b>Fees at the end:</b> a low price on the page, then shipping and service fees at checkout.</li>
</ul>

<h2>A simple way to find the real price</h2>
<ol>
<li><b>Record the price before the sale.</b> A dated screenshot is enough, and it’s the strongest benchmark you’ll have.</li>
<li><b>Compare two or three stores</b> for the exact same item and spec. Watch for different models, storage sizes or regional versions.</li>
<li><b>Work out the final price</b> after shipping, fees and VAT, not the price on the product page.</li>
<li><b>Ask yourself:</b> without the discount, would I buy this at this price?</li>
</ol>

<h2>Checking a sale licence in Saudi Arabia</h2>
<p>Saudi Arabia’s Ministry of Commerce regulates sales and requires a licence for them. It lets shoppers verify promotions by scanning the barcode on the licence with a phone camera, showing the discount type, percentage, duration and business details. You can also check through the Ministry’s document verification service. If a store advertises a sale without a licence, or the licence details don’t match what’s on offer, take note.</p>

<h2>Bank offers and cashback</h2>
<p>Cashback isn’t an instant discount. It arrives later, usually with a cap and conditions, so count it as a saving only if you’re sure you’ll meet them. The same goes for points and gift cards: they’re worth something only if you’ll actually use them.</p>

<h2>If an offer feels misleading</h2>
<p>Keep screenshots from before and during the sale, and contact the store. In Saudi Arabia you can report violations to the Ministry of Commerce through its official channels. Either way, the best protection is not buying under pressure.</p>

<h2>Our standard at Kobon</h2>
<p>No fake countdowns, no exaggerated discounts and no made-up savings figures. Every offer we publish has an official source, written terms and a last-checked date, so you can judge it for yourself.</p>
""",
})

GUIDES.append({
"slug": "gulf-national-days-sales",
"updated": "2026-11-09",
"title_ar": "الأيام الوطنية في الخليج وتخفيضاتها: تقويم سنوي للمتسوق",
"title_en": "Gulf national days and their sales: a shopper’s calendar",
"desc_ar": "مواعيد الأيام الوطنية في دول الخليج الست ويوم التأسيس السعودي، وما تتوقعه من عروض في كل مناسبة، وكيف تخطط لها.",
"desc_en": "National day dates for all six Gulf states plus Saudi Founding Day, what kind of offers to expect, and how to plan around them.",
"tag_ar": "مواسم", "tag_en": "Seasons",
"sources": [
 ("https://decree.om/2025/rd20250015/", "Oman: Royal Decree 15/2025 on official holidays (National Day 20–21 November)"),
 ("https://cm.gov.qa/en/Pages/official_holidays.aspx", "Qatar Council of Ministers: official holidays"),
 ("https://protocol.dfat.gov.au/Public/NationalDays", "Australian DFAT protocol: national days list"),
 ("https://mc.gov.sa/Pages/dvs.aspx", "Saudi Ministry of Commerce: document verification service"),
],
"body_ar": """
<div class="keybox"><h2>باختصار</h2><ul>
<li>لكل دولة خليجية يوم وطني تصاحبه عادةً عروض محلية من المتاجر.</li>
<li>المواعيد ثابتة بالتقويم الميلادي، فيسهل التخطيط لها مسبقًا.</li>
<li>كثير من العروض تحمل أرقامًا مرتبطة بالمناسبة، مثل رقم اليوم أو سنة التأسيس.</li>
<li>تأكد أن العرض صالح في بلدك؛ عروض اليوم الوطني غالبًا محلية.</li>
</ul></div>

<h2>التقويم</h2>
<table><thead><tr><th>المناسبة</th><th>الموعد</th></tr></thead><tbody>
<tr><td>اليوم الوطني العُماني</td><td>20 نوفمبر (عطلة 20 و21 نوفمبر)</td></tr>
<tr><td>عيد الاتحاد في الإمارات</td><td>2 ديسمبر</td></tr>
<tr><td>اليوم الوطني البحريني</td><td>16 ديسمبر</td></tr>
<tr><td>اليوم الوطني القطري</td><td>18 ديسمبر</td></tr>
<tr><td>يوم التأسيس السعودي</td><td>22 فبراير</td></tr>
<tr><td>العيد الوطني الكويتي ويوم التحرير</td><td>25 و26 فبراير</td></tr>
<tr><td>اليوم الوطني السعودي</td><td>23 سبتمبر</td></tr>
</tbody></table>
<p>قد تختلف أيام العطلة الرسمية عن يوم المناسبة نفسه في بعض السنوات، بحسب ما تعلنه كل دولة.</p>

<h2>ماذا تتوقع من العروض؟</h2>
<p>عروض الأيام الوطنية تختلف عن المواسم العالمية مثل الجمعة البيضاء. هي في الغالب:</p>
<ul>
<li><b>محلية:</b> تستهدف المتسوقين في الدولة صاحبة المناسبة، وقد لا تعمل في الدول الأخرى.</li>
<li><b>رمزية في الأرقام:</b> كثير من المتاجر في السعودية تستخدم أرقامًا مثل 93 أو 94 في اليوم الوطني (رقم الذكرى)، أو 1727 في يوم التأسيس، كأكواد أو نسب أو أسعار.</li>
<li><b>قصيرة:</b> بعضها يوم أو يومين فقط، وبعضها يبدأ قبل المناسبة بأيام.</li>
<li><b>متنوعة الفئات:</b> من الأزياء والإلكترونيات إلى المطاعم والسفر الداخلي.</li>
</ul>

<h2>نوفمبر وديسمبر: موسم مزدحم</h2>
<p>تتقاطع في نهاية العام عدة مناسبات: 11.11، والجمعة البيضاء، واليوم الوطني العُماني، ثم عيد الاتحاد في الإمارات، واليوم الوطني في البحرين وقطر. هذا يعني أن العروض متتالية، فلا داعي للاستعجال. إذا فاتك عرض في 11.11 فقد تجد ما يشبهه في الجمعة البيضاء أو في عروض اليوم الوطني لبلدك. سجّل الأسعار وقارن بين المناسبات.</p>

<h2>فبراير: يوم التأسيس والعيد الوطني الكويتي ورمضان</h2>
<p>في 2027 يأتي يوم التأسيس السعودي (22 فبراير) والعيد الوطني الكويتي (25 فبراير) خلال شهر رمضان المتوقع أن يبدأ نحو 8 فبراير. لذلك قد تتداخل عروض المناسبات الوطنية مع عروض رمضان. خطط لمشترياتك على هذا الأساس، واقرأ دليلنا عن خطة تسوق رمضان 2027.</p>

<h2>سبتمبر: اليوم الوطني السعودي</h2>
<p>يوافق 23 سبتمبر ذكرى توحيد المملكة، وهو من أكبر مواسم العروض المحلية في السعودية. كثير من المتاجر تبدأ عروضها قبل اليوم بأسبوع تقريبًا، وتأتي معه عادة عروض العودة إلى المدارس في الفترة نفسها.</p>

<h2>نصائح قبل الشراء</h2>
<ol>
<li><b>تأكد من الدولة</b> المشمولة بالعرض، خاصة إذا كنت تتسوق من تطبيق يخدم أكثر من دولة.</li>
<li><b>اقرأ الحد الأقصى للخصم</b>؛ الأكواد الرمزية قد تكون بحد أقصى منخفض.</li>
<li><b>تحقق من الترخيص</b> في السعودية عبر مسح الباركود أو خدمة التحقق من الوثائق لدى وزارة التجارة.</li>
<li><b>احذر الحسابات المقلّدة</b> التي تنشر «أكواد اليوم الوطني» في وسائل التواصل؛ الكود الحقيقي يأتي من المتجر أو شريكه المعتمد.</li>
</ol>

<h2>كيف نتعامل مع هذه المواسم في كوبون</h2>
<p>نضيف عروض الأيام الوطنية الرسمية لكل دولة في صفحة السوق الخاصة بها، مع توضيح الدول التي يصلح فيها العرض وتاريخ آخر تحقق. ولا ننشر أكوادًا متداولة دون مصدر.</p>
""",
"body_en": """
<div class="keybox"><h2>The short version</h2><ul>
<li>Each Gulf state has a national day, and local retailers usually mark it with offers.</li>
<li>The dates are fixed in the Gregorian calendar, which makes them easy to plan for.</li>
<li>Many offers use numbers tied to the occasion, such as the anniversary year or founding year.</li>
<li>Check that an offer is valid where you live. National day deals are usually local.</li>
</ul></div>

<h2>The calendar</h2>
<table><thead><tr><th>Occasion</th><th>Date</th></tr></thead><tbody>
<tr><td>Oman National Day</td><td>20 November (holiday on 20 and 21 November)</td></tr>
<tr><td>UAE National Day (Eid Al Etihad)</td><td>2 December</td></tr>
<tr><td>Bahrain National Day</td><td>16 December</td></tr>
<tr><td>Qatar National Day</td><td>18 December</td></tr>
<tr><td>Saudi Founding Day</td><td>22 February</td></tr>
<tr><td>Kuwait National Day and Liberation Day</td><td>25 and 26 February</td></tr>
<tr><td>Saudi National Day</td><td>23 September</td></tr>
</tbody></table>
<p>In some years the official public holiday differs from the day itself, depending on what each government announces.</p>

<h2>What kind of offers to expect</h2>
<p>National day promotions work differently from global events like White Friday. They tend to be:</p>
<ul>
<li><b>Local:</b> aimed at shoppers in that country, and often not valid elsewhere.</li>
<li><b>Symbolic:</b> many Saudi retailers use the anniversary number on National Day (93, 94 and so on) or 1727 on Founding Day, as codes, percentages or prices.</li>
<li><b>Short:</b> some last a day or two; others start a few days early.</li>
<li><b>Broad:</b> from fashion and electronics to restaurants and domestic travel.</li>
</ul>

<h2>November and December: a crowded stretch</h2>
<p>The end of the year stacks several occasions: 11.11, White Friday, Oman’s National Day, then UAE National Day, and Bahrain’s and Qatar’s national days. Deals come one after another, so there’s no need to rush. Miss something on 11.11 and you may find similar on White Friday or your own national day. Keep a note of prices and compare across events.</p>

<h2>February: Founding Day, Kuwait’s National Day and Ramadan</h2>
<p>In 2027, Saudi Founding Day (22 February) and Kuwait’s National Day (25 February) fall during Ramadan, which is expected to start around 8 February. National day promotions may overlap with Ramadan offers, so plan with both in mind. Our Ramadan 2027 guide has the details.</p>

<h2>September: Saudi National Day</h2>
<p>23 September marks the unification of the Kingdom and is one of Saudi Arabia’s biggest local sale moments. Many stores start about a week early, and it often overlaps with back-to-school promotions.</p>

<h2>Before you buy</h2>
<ol>
<li><b>Check the country</b> the offer covers, especially in apps that serve several markets.</li>
<li><b>Read the maximum discount.</b> Symbolic codes can carry low caps.</li>
<li><b>Verify the licence</b> in Saudi Arabia by scanning the barcode or using the Ministry of Commerce verification service.</li>
<li><b>Beware of copycat accounts</b> posting “national day codes” on social media. Real codes come from the store or its approved partners.</li>
</ol>

<h2>How Kobon handles these seasons</h2>
<p>We add official national day offers to each country’s market page, showing where the offer is valid and when we last checked it. We don’t post codes doing the rounds without a source.</p>
""",
})

GFAQ = {
"white-friday-2026": (
 [("هل الجمعة البيضاء أرخص من 11.11؟", "ليس بالضرورة. بعض المنتجات تنخفض أكثر في 11.11، وبعضها في الجمعة البيضاء. سجّل سعر المنتج في المناسبتين وقارن، ولا تفترض أن الموسم الأكبر هو الأرخص دائمًا."),
  ("هل يحتاج الحصول على عروض أمازون إلى اشتراك برايم؟", "معظم العروض متاحة للجميع، لكن أمازون منحت مشتركي برايم في السعودية وصولًا مبكرًا في 2025، وتخصص لهم بعض العروض. قرّر الاشتراك بناءً على استخدامك طوال العام، لا من أجل يوم واحد."),
  ("هل أشتري الآن أم أنتظر؟", "إذا كان المنتج في قائمتك وسعره الحالي جيد مقارنة بما سجّلته، وتحتاجه قبل نهاية الشهر، فالانتظار ليس ضروريًا. أما المشتريات الكبيرة غير العاجلة، فالأفضل أن تنتظر وتقارن.")],
 [("Is White Friday cheaper than 11.11?", "Not necessarily. Some products drop further on 11.11, others on White Friday. Note the price at both and compare. Don’t assume the bigger event is always cheaper."),
  ("Do I need Prime for Amazon’s deals?", "Most deals are open to everyone, but Amazon gave Prime members in Saudi Arabia early access in 2025 and reserves some deals for them. Decide on Prime based on how you use it all year, not for one sale.")]),
"11-11-gulf": (
 [("هل عروض 11.11 تقتصر على يوم 11 نوفمبر؟", "لا. كثير من المتاجر تبدأ قبله بأيام وتنتهي بعده، كما فعلت نون في 2025 عندما امتدت عروضها من 7 إلى 12 نوفمبر. تابع المتاجر التي تهمك بدل انتظار اليوم نفسه."),
  ("هل تعمل أكواد 11.11 على المنتجات المخفّضة؟", "يعتمد ذلك على شروط كل كود. كثير من المتاجر لا تسمح بجمع الكود مع التخفيض، وبعضها يسمح بذلك في الموسم تحديدًا. اقرأ الشروط، ثم قارن السعر النهائي في الحالتين."),
  ("هل يحق لي إرجاع منتج اشتريته في 11.11؟", "تنطبق سياسة الإرجاع المعتادة إلا إذا ذكر المتجر غير ذلك صراحة، وبعض عروض الموسم تكون نهائية. وفي السعودية يمنحك نظام التجارة الإلكترونية سبعة أيام من الاستلام لفسخ العقد إذا لم تستخدم المنتج، مع استثناءات."),
  ("كيف أعرف أن متجرًا عالميًا يشحن إلى بلدي؟", "ابحث عن قائمة الدول في صفحة الشحن، أو غيّر الدولة في أعلى الموقع وأضف المنتج إلى السلة لترى تكلفة الشحن الفعلية قبل الدفع.")],
 [("Does 11.11 only run on 11 November?", "No. Many stores start a few days before and finish after, as noon did in 2025 with deals from 7 to 12 November. Follow the stores you care about rather than waiting for the day itself."),
  ("Do 11.11 codes work on sale items?", "It depends on each code’s terms. Many stores don’t allow a code on top of a sale price; some make an exception for the event. Read the terms, then compare the final price both ways."),
  ("Can I return something bought on 11.11?", "The normal return policy applies unless the store says otherwise, and some event deals are final sale. In Saudi Arabia, the E-Commerce Law gives you seven days from delivery to cancel if the item is unused, with exceptions.")]),
"global-shipping-customs": (
 [("من يدفع الضريبة والرسوم: أنا أم المتجر؟", "يعتمد على المتجر. بعضها يحصّلها منك عند الدفع ويتولى التخليص، وبعضها يترك لشركة الشحن تحصيلها عند التسليم. اقرأ صفحة الشحن، وابحث عن عبارة «شامل الرسوم»."),
  ("هل يمكن أن تُحتجز شحنتي في الجمارك؟", "قد تتأخر الشحنة إذا كانت المعلومات ناقصة أو غير دقيقة، أو إذا احتاج المنتج إلى فسح من جهة أخرى. احرص على أن يكون اسمك وعنوانك ورقم جوالك صحيحة في الطلب.")],
 [("Who pays the tax and fees, me or the store?", "It depends on the store. Some collect them at checkout and handle clearance; others leave the courier to collect on delivery. Check the shipping page and look for “duties included”.")]),
"verify-coupon-code": (
 [("هل الأكواد الموجودة في مواقع الكوبونات آمنة؟", "الكود نفسه لا يضرك، لكنه قد يكون منتهيًا أو غير صالح. الخطر الحقيقي في المواقع التي تطلب بياناتك أو تحميل تطبيقات. استخدم الكود فقط في صفحة الدفع على موقع المتجر الرسمي.")],
 []),
"tabby-tamara-bnpl": (
 [("هل استخدام التقسيط يؤثر على سجلي الائتماني؟", "قد يؤثر التأخر المتكرر في السداد، إذ تذكر الشركتان أن التأخر قد يُبلّغ لشركات المعلومات الائتمانية. أما السداد في المواعيد فهو جزء طبيعي من الاستخدام."),
  ("هل يمكنني سداد المبلغ كاملًا قبل موعده؟", "تتيح الخدمتان عادةً سداد الدفعات المتبقية مبكرًا من التطبيق. راجع التطبيق لمعرفة الخيارات المتاحة لخطتك."),
  ("لماذا رُفض طلب التقسيط؟", "تذكر تمارا أسبابًا منها: بطاقة غير مفعلة للشراء الإلكتروني، أو التزامات متأخرة، أو قيمة شراء تتجاوز الحد المسموح. جرّب مبلغًا أقل أو بطاقة أخرى، أو ادفع بطريقة مختلفة.")],
 [("Can I pay off early?", "Both services generally let you settle remaining payments early in the app. Check the app for your plan’s options.")]),
"online-returns-saudi": (
 [("هل يحق للمتجر رفض الإرجاع إذا فتحت العلبة فقط؟", "يشترط النظام ألا تكون استخدمت المنتج أو انتفعت به. فتح العلبة لفحص المنتج ليس استخدامًا في الغالب، لكن بعض المنتجات الصحية أو الشخصية لا تُرجع بعد فتحها لأسباب صحية. احتفظ بكل شيء كما وصلك قدر الإمكان."),
  ("كم يستغرق استرداد المبلغ؟", "لا يحدد النظام مدة محددة لإعادة المبلغ، فراجع سياسة المتجر، وتابع الطلب كتابيًا إذا تأخر.")],
 []),
"ramadan-2027-shopping": (
 [("هل عروض رمضان أفضل في بدايته أم في نهايته؟", "يختلف ذلك حسب الفئة. المقاضي غالبًا قبل الشهر وفي بدايته، والأزياء والهدايا تتكثف عروضها مع اقتراب العيد. لكن التوصيل في الأيام الأخيرة أبطأ، فلا تؤجل ما تحتاجه للعيد."),
  ("كيف أتجنب الشراء الزائد؟", "حدّد الكميات قبل التسوق بحسب عدد أفراد الأسرة والأيام، والتزم بالقائمة، وتجاهل عروض الكميات الكبيرة إذا لم تكن تحتاجها."),
  ("هل أشتري ملابس العيد من متجر عالمي؟", "ممكن، لكن احسب الشحن الدولي والتخليص، واطلب قبل وقت كافٍ، وتأكد من سياسة الإرجاع إن لم يناسبك المقاس.")],
 []),
"gcc-vat-prices": (
 [("هل أدفع ضريبة على رسوم الشحن؟", "في الواردات، تحسب الضريبة على قيمة البضاعة شاملة الشحن والتأمين والرسوم، كما توضح هيئة الزكاة والضريبة والجمارك في السعودية. وفي الطلبات المحلية، تُعامل رسوم التوصيل عادة كجزء من قيمة التوريد."),
  ("هل يحق لي طلب فاتورة ضريبية؟", "نعم، والمتاجر المسجلة في الضريبة تصدر فواتير تتضمن الضريبة. احتفظ بها، فهي تثبت السعر الذي دفعته وتفيدك في الضمان والإرجاع."),
  ("هل الضريبة تُسترد عند الإرجاع؟", "عند إرجاع منتج محلي يُعاد لك المبلغ كاملًا شاملًا الضريبة عادة. أما ضريبة الاستيراد على طلبات الخارج فقد لا تُسترد بسهولة، فاقرأ سياسة المتجر.")],
 [("Do I pay VAT on shipping?", "On imports, VAT is calculated on the goods including shipping, insurance and fees, as ZATCA explains for Saudi Arabia. On local orders, delivery charges are normally treated as part of the supply.")]),
"fake-discounts": (
 [("هل الخصم الكبير دائمًا مشبوه؟", "لا. بعض المتاجر تصفّي مخزونًا أو تطلق منتجًا بخصم حقيقي كبير. المهم أن تقارن السعر النهائي بمرجع تثق به، لا أن ترفض كل خصم كبير."),
  ("هل أدوات تتبع الأسعار مفيدة؟", "يمكن أن تساعدك على رؤية تاريخ السعر، لكن تحقق من أنها تتبع المتجر نفسه والمنتج نفسه في بلدك. وأبسط أداة هي صورة للصفحة مع التاريخ."),
  ("ماذا لو انخفض السعر بعد شرائي بأيام؟", "بعض المتاجر تعيد الفرق، وأغلبها لا تفعل. اسأل خدمة العملاء، وإن كانت مهلة الإرجاع ما زالت سارية والمنتج لم يُستخدم، فقد يكون الإرجاع وإعادة الشراء خيارًا.")],
 [("Is a big discount always suspicious?", "No. Stores clear stock or launch products with genuinely deep discounts. The point is to compare the final price with a benchmark you trust, not to reject every big number."),
  ("What if the price drops after I buy?", "A few stores refund the difference; most don’t. Ask customer service, and if you’re still inside the return window with an unused item, returning and rebuying may be an option.")]),
"gulf-national-days-sales": (
 [("هل عروض اليوم الوطني متاحة للمقيمين أيضًا؟", "نعم، العروض موجهة للمتسوقين داخل الدولة عمومًا، مواطنين ومقيمين، ما لم تذكر الشروط غير ذلك صراحة."),
  ("هل تبدأ العروض في اليوم نفسه؟", "كثير منها يبدأ قبل المناسبة بأيام، وخاصة في اليوم الوطني السعودي. فعّل تنبيهات المتاجر التي تتسوق منها قبل الموعد بأسبوع."),
  ("هل أكواد اليوم الوطني تعمل في المتاجر العالمية؟", "غالبًا لا، لأنها حملات محلية. لكن بعض المتاجر العالمية التي لها نسخة خليجية قد تشارك بعروض لسوق بعينه، فتحقق من الدولة المشمولة."),
  ("لماذا تختلف أيام العطلة عن يوم المناسبة؟", "تعلن كل دولة عطلاتها الرسمية بحسب أيام الأسبوع وقراراتها، فقد تُنقل العطلة أو تُمدّد في بعض السنوات.")],
 [("Are national day offers open to residents?", "Yes. They’re generally aimed at everyone shopping in the country, citizens and residents alike, unless the terms say otherwise."),
  ("Do the deals start on the day itself?", "Many start a few days early, especially for Saudi National Day. Turn on alerts from your usual stores a week ahead.")]),
}
def _add(slug, ar=(), en=()):
    GFAQ[slug][0].extend(ar); GFAQ[slug][1].extend(en)
_add("11-11-gulf", ar=[("هل تختلف عروض 11.11 بين السعودية والإمارات؟", "نعم في الغالب. المتجر نفسه قد يطرح عروضًا وأكوادًا مختلفة لكل دولة، بأسعار وعملات ومنتجات مختلفة. تأكد أنك تتصفح نسخة المتجر الخاصة ببلدك قبل نسخ أي كود.")])
_add("ramadan-2027-shopping", ar=[("متى يُعلن موعد رمضان رسميًا؟", "تعلن الجهات المختصة في كل دولة بداية الشهر بعد تحري الهلال مساء التاسع والعشرين من شعبان. حتى ذلك الحين، استخدم الموعد الفلكي المتوقع للتخطيط.")],
 en=[("Are Ramadan deals better at the start or the end?", "It depends on the category. Groceries are usually best before and early in the month; fashion and gifts ramp up towards Eid. Deliveries slow down in the final days, though, so don’t leave Eid essentials late."),
     ("How do I avoid overbuying?", "Set quantities before you shop, based on household size and days, stick to the list, and ignore bulk offers you don’t need."),
     ("When is Ramadan officially announced?", "Each country’s authorities announce the start after the moon sighting on the evening of 29 Sha’ban. Until then, plan with the expected astronomical date.")])
_add("gcc-vat-prices", ar=[("لماذا يختلف سعر المنتج نفسه بين دولتين خليجيتين؟", "تختلف نسبة الضريبة، وتكاليف الاستيراد والتوزيع، وسياسات التسعير لكل متجر في كل سوق. لذلك لا تكفي مقارنة السعر قبل الضريبة لمعرفة الأرخص.")],
 en=[("Can I ask for a tax invoice?", "Yes. VAT-registered stores issue invoices showing the VAT. Keep them as proof of what you paid, for warranty claims and returns."),
     ("Is VAT refunded when I return something?", "For a local return you’re normally refunded the full amount including VAT. Import VAT on overseas orders can be harder to recover, so check the store’s policy.")])
_add("fake-discounts", ar=[("كيف أتعامل مع «خصم يصل إلى 70%»؟", "اعتبر الرقم سقفًا لا وعدًا. ادخل إلى المنتجات التي تهمك وانظر إلى خصم كل منها، فغالبًا تكون النسبة القصوى على عدد محدود من المنتجات.")],
 en=[("Are price-tracking tools useful?", "They can show a price history, but make sure they track the same store, the same product and your country. The simplest tool is still a dated screenshot.")])
_add("gulf-national-days-sales", ar=[("ما الفرق بين يوم التأسيس واليوم الوطني في السعودية؟", "يوم التأسيس في 22 فبراير يستذكر تأسيس الدولة السعودية الأولى، أما اليوم الوطني في 23 سبتمبر فيوافق ذكرى توحيد المملكة. ولكل منهما عروضه الخاصة.")],
 en=[("Do national day codes work on international stores?", "Usually not, since they’re local campaigns. International stores with a Gulf version sometimes join in for a specific market, so check which country the offer covers."),
     ("What’s the difference between Saudi Founding Day and National Day?", "Founding Day on 22 February commemorates the founding of the first Saudi state, while National Day on 23 September marks the unification of the Kingdom. Each has its own promotions.")])
_add("fake-discounts", ar=[("هل «السعر قبل الخصم» يعني أن المنتج بيع به فعلًا؟", "ليس دائمًا. قد يكون السعر الذي يوصي به المصنع، أو سعرًا مرتفعًا لفترة قصيرة. لذلك لا تعتمد عليه وحده، وارجع إلى السعر الذي سجّلته بنفسك أو إلى أسعار المتاجر الأخرى للمنتج نفسه."),
                           ("هل الشراء من التطبيق أرخص من الموقع؟", "أحيانًا تخصص المتاجر عروضًا أو أكوادًا للتطبيق فقط. قارن السعر النهائي في الاثنين قبل الدفع، ولا تفترض أن أحدهما أرخص دائمًا.")])
_add("gulf-national-days-sales", ar=[("كيف أجهّز نفسي لعروض اليوم الوطني؟", "اكتب قائمة قصيرة بما تحتاجه، وسجّل الأسعار قبل المناسبة بأسبوعين، وفعّل تنبيهات المتاجر التي تتسوق منها فعلًا، ثم قارن السعر بعد الخصم بما سجّلته قبل أن تشتري.")])
_add("gcc-vat-prices", ar=[("هل تطبّق الكويت وقطر ضرائب أخرى على الواردات؟", "لم تطبّق الدولتان ضريبة القيمة المضافة، لكن الرسوم الجمركية الخليجية الموحدة تبقى قائمة على السلع المستوردة من خارج الاتحاد الجمركي، مع حدود إعفاء وإجراءات تختلف حسب كل دولة.")])


SEASON_GUIDE = {"white-friday": "white-friday-2026", "11-11": "11-11-gulf", "ramadan": "ramadan-2027-shopping", "eid-al-fitr": "ramadan-2027-shopping",
                "founding-day": "gulf-national-days-sales", "saudi-national-day": "gulf-national-days-sales"}
CATEGORY_GUIDES = {"fashion": ["verify-coupon-code", "online-returns-saudi"], "beauty": ["global-shipping-customs", "fake-discounts"],
                   "electronics": ["fake-discounts", "tabby-tamara-bnpl"], "travel": ["verify-coupon-code", "gcc-vat-prices"],
                   "home": ["tabby-tamara-bnpl", "online-returns-saudi"], "food": ["ramadan-2027-shopping", "verify-coupon-code"]}
GBY = {}


def _g(slug: str) -> dict:
    if not GBY:
        GBY.update({g["slug"]: g for g in GUIDES})
    return GBY[slug]


def guide_words(g: dict, lang: str) -> int:
    faq = GFAQ.get(g["slug"], ([], []))[0 if lang == "ar" else 1]
    return len(strip_tags(g["body_" + lang]).split()) + sum(len((q + " " + x).split()) for q, x in faq)


def guide_card(lang: str, g: dict, search: bool = False) -> str:
    ds = f' data-search="{esc((g["title_" + lang] + " " + g["desc_" + lang] + " " + g["tag_" + lang] + " " + g["title_en"]).lower())}"' if search else ""
    mins = max(3, round(guide_words(g, lang) / 200))
    rt = t(lang, f"{mins} دقائق قراءة", f"{mins} min read")
    return (f'<a class="guide-card" href="{L(lang, "/guides/" + g["slug"] + "/")}"{ds}><span class="gtag">{esc(g["tag_" + lang])}</span>'
            f'<h3>{esc(g["title_" + lang])}</h3><p>{esc(g["desc_" + lang])}</p><span class="note">{rt}</span><span class="more">{t(lang, "اقرأ الدليل ←", "Read the guide →")}</span></a>')


def related_guides_html(lang: str, slugs: list[str], title: str = "") -> str:
    cards = "".join(guide_card(lang, _g(s)) for s in slugs if s in {g["slug"] for g in GUIDES})
    if not cards:
        return ""
    h = title or t(lang, "أدلة ذات صلة", "Related guides")
    return f'<div style="display:grid;gap:1.2rem"><h2 style="font-size:1.4rem">{h}</h2><div class="guide-grid">{cards}</div></div>'


def build_guides(lang: str) -> None:
    a = lambda ar, en: t(lang, ar, en)
    crumbs = [(a("الرئيسية", "Home"), "/"), (a("أدلة التسوق", "Shopping guides"), "/guides/")]
    search = f'''<form class="search js-filter" role="search" style="margin-top:.4rem"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#5E6380" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="site-q" name="q" type="search" aria-label="{a('ابحث في الأدلة', 'Search the guides')}" placeholder="{a('ابحث في الأدلة: الجمارك، تابي، الجمعة البيضاء…', 'Search guides: customs, Tabby, White Friday…')}"></form>'''
    cards = "".join(guide_card(lang, g, True) for g in GUIDES)
    body = page_hero(lang, crumbs, a("أدلة التسوق", "Shopping guides"), a("أدلة عملية <span class=\"hl\">قبل أن تشتري</span>", "Practical guides <span class=\"hl\">before you buy</span>"),
                     a("مواعيد المواسم، والشحن والجمارك، والدفع بالتقسيط، وحقوقك عند الإرجاع. معلومات من مصادرها الرسمية، بلغة واضحة.", "Sale dates, shipping and customs, instalment payments and your return rights. Facts from official sources, in plain language."), "", extra=search) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:1.5rem">
  <p id="search-empty" class="note" hidden data-msg="{a('لا يوجد دليل يطابق بحثك. جرّب كلمة أخرى.', 'No guide matches your search. Try another word.')}"></p>
  <h2 class="sr-only">{a("كل الأدلة", "All guides")}</h2>
  <div class="guide-grid">{cards}</div>
</div></section>'''
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": a("أدلة التسوق", "Shopping guides"), "url": abs_url(lang, "/guides/"),
           "hasPart": [{"@type": "Article", "headline": g["title_" + lang], "url": abs_url(lang, f"/guides/{g['slug']}/")} for g in GUIDES]}]
    render(lang, "/guides/", a("أدلة التسوق: مواسم، جمارك، تقسيط، وإرجاع | كوبون", "Shopping guides: sales, customs, BNPL and returns | Kobon"),
           a("أدلة عملية للمتسوق في الخليج: مواعيد الجمعة البيضاء و11.11 ورمضان، والشحن والجمارك من المتاجر العالمية، وتابي وتمارا، وحق الإرجاع، وكشف الخصم الوهمي.",
             "Practical guides for Gulf shoppers: White Friday, 11.11 and Ramadan dates, shipping and customs from international stores, Tabby and Tamara, return rights and spotting fake discounts."),
           body, "guides", ld, crumbs)
    for g in GUIDES:
        path = f"/guides/{g['slug']}/"
        cr = crumbs + [(g["title_" + lang], path)]
        faq = GFAQ.get(g["slug"], ([], []))[0 if lang == "ar" else 1]
        faq_sec = f'<h2>{a("أسئلة شائعة", "Common questions")}</h2><div class="faq">{faq_html(faq)}</div>' if faq else ""
        src = "".join(f'<li><a href="{esc(u)}" rel="noopener nofollow" target="_blank">{esc(n)}</a></li>' for u, n in g["sources"])
        src_sec = f'<h2>{a("المصادر", "Sources")}</h2><ul class="sources">{src}</ul>' if src else ""
        mins = max(3, round(guide_words(g, lang) / 200))
        meta = f'<div class="gmeta"><span>{a("آخر تحديث:", "Updated:")} {day_label(lang, g["updated"])}</span><span>{a(f"{mins} دقائق قراءة", f"{mins} min read")}</span><span>{a("إعداد فريق كوبون", "By the Kobon team")}</span></div>'
        others = [x["slug"] for x in GUIDES if x["slug"] != g["slug"]]
        idx = [x["slug"] for x in GUIDES].index(g["slug"])
        rel = [others[(idx + k) % len(others)] for k in range(3)]
        aside = f'''<aside class="guide-aside">
  <div class="card"><span class="eyebrow mint">{a("معيار كوبون", "The Kobon standard")}</span><p>{a("لا ننشر إلا العروض الصادرة من المتجر أو برنامج شريك معتمد، مع شروطها وتاريخ آخر تحقق.", "We only publish offers issued by the store or an approved partner programme, with full terms and a last-checked date.")}</p><a class="link" href="{L(lang, '/how-it-works/#standard')}">{a("كيف نتحقق ←", "How we check →")}</a></div>
  <div class="card"><b>{a("كن أول من يعرف", "Be the first to know")}</b><p>{a("رسالة أسبوعية واحدة بأفضل العروض الرسمية.", "One weekly email with the best official offers.")}</p><a class="btn btn-primary" href="{L(lang, '/#alerts')}">{a("اشترك", "Subscribe")}</a></div>
</aside>'''
        body = page_hero(lang, cr, esc(g["tag_" + lang]), esc(g["title_" + lang]), esc(g["desc_" + lang]), "", extra=meta) + f'''
<section class="section"><div class="wrap" style="display:grid;gap:3rem">
  <div class="guide-layout"><article class="prose">{g["body_" + lang]}{faq_sec}{src_sec}<p class="note">{a("قد نحصل على عمولة عند الشراء عبر روابط شركائنا، دون أي تكلفة إضافية عليك. لا يؤثر ذلك في محتوى الأدلة.", "We may earn a commission when you buy through partner links, at no extra cost to you. It doesn’t influence our guides.")}</p></article>{aside}</div>
  {related_guides_html(lang, rel, a("أدلة أخرى", "More guides"))}
</div></section>'''
        art = {"@context": "https://schema.org", "@type": "Article", "headline": g["title_" + lang], "description": g["desc_" + lang],
               "inLanguage": lang, "datePublished": g["updated"], "dateModified": g["updated"], "wordCount": guide_words(g, lang),
               "mainEntityOfPage": abs_url(lang, path), "url": abs_url(lang, path), "image": DOMAIN + "/assets/og-default.png",
               "author": {"@type": "Organization", "name": NAME[lang], "url": DOMAIN + "/"}, "publisher": {"@id": DOMAIN + "/#org"},
               "citation": [u for u, _ in g["sources"]]}
        lds = [art] + ([faq_ld(faq)] if faq else [])
        render(lang, path, f'{g["title_" + lang]} | {NAME[lang]}', g["desc_" + lang], body, "guides", lds, cr, og_type="article")



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
  <p class="lead">ربما تغيّر الرابط أو حُذفت الصفحة. يمكنك العودة إلى الرئيسية أو تصفّح المتاجر.</p>
  <p class="note" lang="en" dir="ltr">The link may have changed or the page was removed.</p>
  <div style="display:flex;gap:.8rem;flex-wrap:wrap"><a class="btn btn-primary" href="/">العودة إلى الرئيسية</a><a class="btn btn-ghost" href="/stores/">تصفّح المتاجر</a><a class="btn btn-ghost" href="/en/" lang="en">English home</a></div></div>
  <svg class="art" viewBox="0 0 48 48" aria-hidden="true" style="max-width:220px">{LOGO_SVG.split('>', 1)[1].rsplit('</svg>', 1)[0]}</svg>
</div></section>'''
    out = head("ar", "/", "الصفحة غير موجودة | كوبون", "الصفحة التي تبحث عنها غير موجودة. Page not found.", noindex=True)
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

> Official-only coupons and discount codes from Gulf and international stores, for shoppers in Saudi Arabia, the UAE, Kuwait, Qatar, Bahrain, Oman and beyond. Run by an affiliate marketing team.

- International stores: {DOMAIN}/en/countries/global/
- Shopping guides: {DOMAIN}/en/guides/
- Media kit (PDF): {DOMAIN}/media-kit.pdf

- Home (Arabic): {DOMAIN}/
- Home (English): {DOMAIN}/en/
- For brands: {DOMAIN}/en/partners/
- How it works and verification standard: {DOMAIN}/en/how-it-works/
- About: {DOMAIN}/en/about/
- Contact: {EMAIL}
""")


def clean() -> None:
    for name in ("stores", "categories", "countries", "seasons", "guides", "en", "about", "how-we-verify", "how-it-works", "privacy",
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
        build_guides(lang)
    build_redirects()
    build_404()
    build_misc()
    paths = [p for p in PAGES if p]
    build_sitemap(paths)
    print(f"Built {len(paths)} indexed pages x 2 languages, {len(NOINDEXED)} noindex pages x 2, {len(REDIRECTS) * 2} redirects.")


if __name__ == "__main__":
    main()
