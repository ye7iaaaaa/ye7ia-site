#!/usr/bin/env python3
"""
ye7ia coupon site — dependency-free static site generator.
Reads data/coupons.json + data/categories.json, writes HTML to site root.
Run: python3 build.py
"""
from __future__ import annotations

import html
import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ASSETS_SRC = ROOT / "assets"
SITE_NAME_AR = "يحيى كوبونات"
SITE_NAME_EN = "ye7ia Coupons"
DOMAIN = "https://ye7ia.is-a.si"
YEAR = 2026
TODAY = date.today().isoformat()

COUNTRIES = [
    {"slug": "sa", "name_ar": "السعودية", "name_en": "Saudi Arabia", "flag": "🇸🇦"},
    {"slug": "ae", "name_ar": "الإمارات", "name_en": "United Arab Emirates", "flag": "🇦🇪"},
    {"slug": "kw", "name_ar": "الكويت", "name_en": "Kuwait", "flag": "🇰🇼"},
]

SEASONS = [
    {
        "slug": "white-friday",
        "name_ar": "الجمعة البيضاء",
        "name_en": "White Friday",
        "blurb_ar": "تجميعة أكواد خصم وعروض الجمعة البيضاء للمتسوقين في السعودية والخليج.",
        "blurb_en": "White Friday discount codes and deals for shoppers in Saudi Arabia and the GCC.",
    },
    {
        "slug": "ramadan",
        "name_ar": "رمضان",
        "name_en": "Ramadan",
        "blurb_ar": "أكواد خصم وعروض رمضان — وفر وأنت تتسوق للمستلزمات والهدايا.",
        "blurb_en": "Ramadan discount codes — save while shopping for essentials and gifts.",
    },
    {
        "slug": "11-11",
        "name_ar": "عروض ١١.١١",
        "name_en": "11.11 Sale",
        "blurb_ar": "أكواد خصم عروض ١١.١١ من أشهر المتاجر في المنطقة.",
        "blurb_en": "11.11 sale discount codes from popular stores in the region.",
    },
    {
        "slug": "saudi-national-day",
        "name_ar": "اليوم الوطني السعودي",
        "name_en": "Saudi National Day",
        "blurb_ar": "عروض وأكواد خصم بمناسبة اليوم الوطني السعودي.",
        "blurb_en": "Deals and discount codes for Saudi National Day.",
    },
    {
        "slug": "founding-day",
        "name_ar": "يوم التأسيس",
        "name_en": "Founding Day",
        "blurb_ar": "أكواد خصم وعروض يوم التأسيس في السعودية.",
        "blurb_en": "Founding Day discount codes and offers in Saudi Arabia.",
    },
]

STATIC_PAGES = [
    "about",
    "how-we-verify",
    "privacy",
    "affiliate-disclosure",
    "marketers",
]


def esc(s: Any) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}")


def asset_prefix(lang: str, depth: int) -> str:
    """Relative path from a page (depth within language tree) up to site root."""
    levels = depth if lang == "ar" else depth + 1
    return "" if levels == 0 else "../" * levels


def lang_prefix(depth: int) -> str:
    """Relative path from a page up to its language home."""
    return "" if depth == 0 else "../" * depth


def page_url(lang: str, *parts: str) -> str:
    clean = [p.strip("/") for p in parts if p]
    if lang == "en":
        path = "/" + "/".join(["en"] + clean) + "/"
    elif not clean:
        path = "/"
    else:
        path = "/" + "/".join(clean) + "/"
    return DOMAIN + path



def other_lang(lang: str) -> str:
    return "en" if lang == "ar" else "ar"


def public_stores(stores: list[dict]) -> list[dict]:
    """Stores marked example stay in data/ but are hidden from public pages/sitemap."""
    return [s for s in stores if not s.get("example")]


def alternate_path(lang: str, canonical_path: str) -> str:
    """Absolute site path for the same page in the other language."""
    if lang == "ar":
        return "/en/" if canonical_path == "/" else "/en" + canonical_path
    rest = canonical_path[3:] if canonical_path.startswith("/en") else canonical_path
    return rest if rest else "/"


def t(lang: str, ar: str, en: str) -> str:
    return ar if lang == "ar" else en


def is_verified_today(d: str) -> bool:
    return (d or "")[:10] == TODAY


def days_until(expires: str) -> int | None:
    if not expires:
        return None
    try:
        return (date.fromisoformat(expires[:10]) - date.today()).days
    except ValueError:
        return None


def cat_by_slug(categories: list[dict], slug: str) -> dict | None:
    for c in categories:
        if c["slug"] == slug:
            return c
    return None


def country_by_slug(slug: str) -> dict | None:
    for c in COUNTRIES:
        if c["slug"] == slug:
            return c
    return None


def all_coupons_flat(stores: list[dict]) -> list[dict]:
    rows = []
    for store in stores:
        for c in store.get("coupons") or []:
            row = dict(c)
            row["_store"] = store
            rows.append(row)
    return rows


def sort_coupons(coupons: list[dict]) -> list[dict]:
    def key(c: dict) -> tuple:
        verified = c.get("verified_date") or ""
        exclusive = 0 if c.get("exclusive") else 1
        return (-int(verified.replace("-", "") or 0), exclusive)

    return sorted(coupons, key=key)


def render_head(
    lang: str,
    title: str,
    description: str,
    canonical_path: str,
    depth: int,
    extra_jsonld: list[dict] | None = None,
) -> str:
    dir_attr = "rtl" if lang == "ar" else "ltr"
    html_lang = "ar" if lang == "ar" else "en"
    css = asset_prefix(lang, depth) + "assets/style.css"
    canon = DOMAIN + canonical_path
    if lang == "ar":
        hreflang_ar = canon
        hreflang_en = DOMAIN + ("/en/" if canonical_path == "/" else "/en" + canonical_path)
    else:
        hreflang_en = canon
        rest = canonical_path[3:] if canonical_path.startswith("/en") else canonical_path
        if not rest:
            rest = "/"
        hreflang_ar = DOMAIN + rest

    blocks = []
    if extra_jsonld:
        for obj in extra_jsonld:
            blocks.append(
                '<script type="application/ld+json">'
                + json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
                + "</script>"
            )
    return f"""<!DOCTYPE html>
<html lang="{html_lang}" dir="{dir_attr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canon)}">
<link rel="alternate" hreflang="ar-SA" href="{esc(hreflang_ar)}">
<link rel="alternate" hreflang="en" href="{esc(hreflang_en)}">
<link rel="alternate" hreflang="x-default" href="{esc(hreflang_ar)}">
<meta name="theme-color" content="#0d9488">
<link rel="icon" href="{esc(asset_prefix(lang, depth) + "assets/favicon.svg")}" type="image/svg+xml">
<link rel="icon" href="{esc(asset_prefix(lang, depth) + "assets/favicon-32.png")}" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{esc(asset_prefix(lang, depth) + "assets/apple-touch-icon.png")}" sizes="180x180">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canon)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(SITE_NAME_AR if lang == "ar" else SITE_NAME_EN)}">
<meta property="og:locale" content="{"ar_SA" if lang == "ar" else "en_US"}">
<meta property="og:locale:alternate" content="{"en_US" if lang == "ar" else "ar_SA"}">
<meta property="og:image" content="{esc(DOMAIN + "/assets/og-default.png")}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{esc(DOMAIN + "/assets/og-default.png")}">
<link rel="stylesheet" href="{esc(css)}">
{chr(10).join(blocks)}
</head>
<body>
"""


def render_header(lang: str, depth: int, canonical_path: str = "/") -> str:
    root = asset_prefix(lang, depth)
    loc = lang_prefix(depth)
    switch_href = alternate_path(lang, canonical_path)
    if lang == "ar":
        switch_label = "English"
        brand_tail = "كوبونات"
        nav = ("الرئيسية", "المتاجر", "التصنيفات", "المواسم", "للمسوقين")
    else:
        switch_label = "العربية"
        brand_tail = "Coupons"
        nav = ("Home", "Stores", "Categories", "Seasons", "Marketers")
    home, stores, cats, seasons, marketers = nav
    skip = t(lang, "تخطّي إلى المحتوى", "Skip to content")
    return f"""<a class="skip-link" href="#main">{esc(skip)}</a>
<header class="site-header">
  <div class="container header-inner">
    <a class="logo" href="{esc(loc + "index.html")}"><span>ye7ia</span> {esc(brand_tail)}</a>
    <nav class="nav" aria-label="Main">
      <a href="{esc(loc + "index.html")}">{esc(home)}</a>
      <a href="{esc(loc + "stores/")}">{esc(stores)}</a>
      <a href="{esc(loc + "categories/")}">{esc(cats)}</a>
      <a href="{esc(loc + "seasons/")}">{esc(seasons)}</a>
      <a href="{esc(loc + "marketers/")}">{esc(marketers)}</a>
      <a class="lang-switch" href="{esc(switch_href)}" hreflang="{other_lang(lang)}">{esc(switch_label)}</a>
    </nav>
  </div>
</header>
"""



def render_footer(lang: str, depth: int) -> str:
    root = asset_prefix(lang, depth)
    loc = lang_prefix(depth)
    if lang == "ar":
        links = [
            ("about/", "من نحن"),
            ("how-we-verify/", "كيف نتحقق من الأكواد"),
            ("privacy/", "الخصوصية"),
            ("affiliate-disclosure/", "الإفصاح عن العمولات"),
            ("marketers/", "للمسوقين"),
            ("countries/sa/", "السعودية"),
            ("countries/ae/", "الإمارات"),
            ("countries/kw/", "الكويت"),
        ]
        note = "موقع أكواد خصم مستقل. قد نحصل على عمولة عند استخدام بعض الروابط دون أي تكلفة إضافية عليك."
        brand = SITE_NAME_AR
        links_label = "روابط"
    else:
        links = [
            ("about/", "About"),
            ("how-we-verify/", "How we verify"),
            ("privacy/", "Privacy"),
            ("affiliate-disclosure/", "Affiliate disclosure"),
            ("marketers/", "For marketers"),
            ("countries/sa/", "Saudi Arabia"),
            ("countries/ae/", "UAE"),
            ("countries/kw/", "Kuwait"),
        ]
        note = "Independent coupon site. We may earn a commission when you use some links, at no extra cost to you."
        brand = SITE_NAME_EN
        links_label = "Links"
    items = "\n".join(
        f'      <li><a href="{esc(loc + href)}">{esc(label)}</a></li>' for href, label in links
    )
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>{esc(brand)}</h4>
        <p class="muted" style="color:#94a3b8">{esc(note)}</p>
      </div>
      <div>
        <h4>{esc(links_label)}</h4>
        <ul>
{items}
        </ul>
      </div>
    </div>
    <p class="footer-note">© {YEAR} ye7ia.is-a.si</p>
  </div>
</footer>
<script src="{esc(root + "assets/app.js")}" defer></script>
</body>
</html>
"""


def render_breadcrumbs(crumbs: list[tuple[str, str | None]]) -> str:
    parts = []
    for i, (label, href) in enumerate(crumbs):
        if href is None or i == len(crumbs) - 1:
            parts.append(f"<span>{esc(label)}</span>")
        else:
            parts.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        if i < len(crumbs) - 1:
            parts.append('<span aria-hidden="true">/</span>')
    return '<nav class="breadcrumbs container" aria-label="Breadcrumb">' + " ".join(parts) + "</nav>\n"


def badge_html(lang: str, coupon: dict) -> str:
    bits = []
    if coupon.get("example"):
        bits.append(f'<span class="badge badge-example">{esc(t(lang, "مثال تجريبي", "EXAMPLE"))}</span>')
    if is_verified_today(coupon.get("verified_date") or ""):
        bits.append(f'<span class="badge badge-verified">{esc(t(lang, "متحقق اليوم", "Verified today"))}</span>')
    elif coupon.get("verified_date"):
        bits.append(
            f'<span class="badge badge-verified">{esc(t(lang, "متحقق", "Verified"))} {esc(coupon["verified_date"][:10])}</span>'
        )
    if coupon.get("exclusive"):
        bits.append(f'<span class="badge badge-exclusive">{esc(t(lang, "حصري", "Exclusive"))}</span>')
    days = days_until(coupon.get("expires") or "")
    if coupon.get("expires"):
        if days is not None and days < 0:
            label = t(lang, "منتهي", "Expired")
        elif days is not None and days <= 7:
            label = t(lang, f"ينتهي خلال {days} يوم", f"Expires in {days}d")
        else:
            label = t(lang, f"ينتهي {coupon['expires'][:10]}", f"Expires {coupon['expires'][:10]}")
        bits.append(f'<span class="badge badge-expires">{esc(label)}</span>')
    return '<div class="badges">' + "".join(bits) + "</div>"


def coupon_card(lang: str, coupon: dict, store: dict | None = None, depth: int = 0) -> str:
    title = coupon.get("title_ar") if lang == "ar" else coupon.get("title_en")
    store_line = ""
    if store:
        sname = store["name_ar"] if lang == "ar" else store["name_en"]
        loc = lang_prefix(depth)
        store_line = f'<p class="muted"><a href="{esc(loc)}stores/{esc(store["slug"])}/">{esc(sname)}</a></p>'
    label_copy = t(lang, "نسخ الكود", "Copy code")
    label_done = t(lang, "تم النسخ!", "Copied!")
    label_shop = t(lang, "تسوّق الآن", "Shop now")
    shop_url = coupon.get("affiliate_url") or "#"
    verified_line = ""
    vd = (coupon.get("verified_date") or "")[:10]
    if vd:
        verified_line = (
            f'<p class="muted coupon-verified">{esc(t(lang, f"آخر تحقق: {vd}", f"Last verified: {vd}"))}</p>'
        )
    shop_btn = ""
    if shop_url and shop_url != "#":
        shop_btn = (
            f'<a class="btn btn-secondary" href="{esc(shop_url)}" target="_blank" '
            f'rel="noopener noreferrer sponsored">{esc(label_shop)}</a>'
        )
    return f"""<article class="coupon">
  <div class="coupon-top">
    <div>
      <p class="discount-pill">{esc(coupon.get("discount") or "")}</p>
      {badge_html(lang, coupon)}
    </div>
  </div>
  <h3 class="coupon-title">{esc(title)}</h3>
  {store_line}
  {verified_line}
  <div class="coupon-actions">
    <div class="code-box" aria-label="code">{esc(coupon.get("code") or "")}</div>
    <button type="button" class="btn"
      data-copy
      data-code="{esc(coupon.get("code") or "")}"
      data-label-copy="{esc(label_copy)}"
      data-label-done="{esc(label_done)}">{esc(label_copy)}</button>
    {shop_btn}
  </div>
</article>
"""


def store_card(lang: str, store: dict, categories: list[dict], depth: int) -> str:
    loc = lang_prefix(depth)
    name = store["name_ar"] if lang == "ar" else store["name_en"]
    desc = store["description_ar"] if lang == "ar" else store["description_en"]
    cat = cat_by_slug(categories, store.get("category") or "")
    cat_name = (cat["name_ar"] if lang == "ar" else cat["name_en"]) if cat else ""
    n = len(store.get("coupons") or [])
    example = f'<span class="chip">{esc(t(lang, "مثال", "EXAMPLE"))}</span>' if store.get("example") else ""
    href = f'{loc}stores/{store["slug"]}/'
    short = desc if len(desc) <= 120 else desc[:120] + "…"
    return f"""<article class="card store-card">
  <a href="{esc(href)}">
    <h3>{esc(name)}</h3>
    <p>{esc(short)}</p>
    <div class="store-meta">
      {example}
      <span class="chip">{esc(cat_name)}</span>
      <span class="chip">{esc(t(lang, f"{n} أكواد", f"{n} codes"))}</span>
    </div>
  </a>
</article>
"""


def breadcrumb_jsonld(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ],
    }


def faq_jsonld(faq: list[dict], lang: str) -> dict | None:
    entities = []
    for item in faq or []:
        q = item.get("q_ar") if lang == "ar" else item.get("q_en")
        a = item.get("a_ar") if lang == "ar" else item.get("a_en")
        if q and a:
            entities.append(
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            )
    if not entities:
        return None
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}


def itemlist_offers_jsonld(lang: str, store: dict) -> dict:
    elements = []
    for i, c in enumerate(store.get("coupons") or [], start=1):
        title = c.get("title_ar") if lang == "ar" else c.get("title_en")
        item: dict[str, Any] = {
            "@type": "Offer",
            "name": title,
            "description": title,
            "url": c.get("affiliate_url") or page_url(lang, "stores", store["slug"]),
            "priceCurrency": "SAR",
            "availability": "https://schema.org/InStock",
        }
        if c.get("expires"):
            item["validThrough"] = c["expires"][:10]
        elements.append({"@type": "ListItem", "position": i, "item": item})
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": t(lang, f"أكواد خصم {store['name_ar']}", f"Discount codes for {store['name_en']}"),
        "itemListElement": elements,
    }


def faq_section(lang: str, faq: list[dict]) -> str:
    if not faq:
        return ""
    parts = [f'<section class="section faq"><h2>{esc(t(lang, "أسئلة شائعة", "FAQ"))}</h2>']
    for item in faq:
        q = item.get("q_ar") if lang == "ar" else item.get("q_en")
        a = item.get("a_ar") if lang == "ar" else item.get("a_en")
        parts.append(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>")
    parts.append("</section>")
    return "\n".join(parts)


def wrap_page(
    lang: str,
    depth: int,
    title: str,
    description: str,
    canonical_path: str,
    body: str,
    jsonld: list[dict] | None = None,
) -> str:
    return (
        render_head(lang, title, description, canonical_path, depth, jsonld)
        + render_header(lang, depth, canonical_path)
        + body
        + render_footer(lang, depth)
    )


def build_home(lang: str, stores: list[dict], categories: list[dict], out_dir: Path, depth: int) -> None:
    stores = public_stores(stores)
    flat = sort_coupons(all_coupons_flat(stores))
    today_codes = [c for c in flat if is_verified_today(c.get("verified_date") or "")][:8] or flat[:6]
    if lang == "ar":
        title = f"أكواد خصم السعودية {YEAR} | {SITE_NAME_AR}"
        desc = "أكواد خصم وكوبونات للمتاجر في السعودية والخليج. انسخ الكود وتسوّق. نحدّث الأكواد باستمرار."
        h1 = f"أكواد خصم موثوقة للمتسوقين في السعودية {YEAR}"
        lead = "وفّر على مشترياتك من أشهر المتاجر. ركّزنا أولاً على السعودية، وبعدين باقي دول الخليج."
        season_label = "عرض موسمي: تصفّح أكواد الجمعة البيضاء ورمضان واليوم الوطني"
        top_stores, today_label = "أبرز المتاجر", "أكواد محدثة"
        cats_label, countries_label = "تصفح حسب التصنيف", "حسب الدولة"
        empty_stores = "ما فيه متاجر بعد — قريب نضيف أكواد حقيقية."
        empty_codes = "ما فيه أكواد معروضة حالياً."
        canon = "/"
    else:
        title = f"Saudi Discount Codes {YEAR} | {SITE_NAME_EN}"
        desc = "Discount codes and coupons for stores in Saudi Arabia and the GCC. Copy a code and shop."
        h1 = f"Trusted discount codes for Saudi shoppers {YEAR}"
        lead = "Save on popular stores. We focus on Saudi Arabia first, then the wider GCC."
        season_label = "Seasonal: browse White Friday, Ramadan, and National Day codes"
        top_stores, today_label = "Top stores", "Recently verified codes"
        cats_label, countries_label = "Browse by category", "By country"
        empty_stores = "No stores yet — real codes will appear here soon."
        empty_codes = "No codes to show right now."
        canon = "/en/"

    if stores:
        store_cards = "\n".join(store_card(lang, s, categories, depth) for s in stores)
        stores_block = f'<div class="grid">{store_cards}</div>'
    else:
        stores_block = f'<p class="muted empty-state">{esc(empty_stores)}</p>'

    if today_codes:
        coupon_cards = "\n".join(coupon_card(lang, c, c.get("_store"), depth) for c in today_codes)
        coupons_block = f'<div class="grid">{coupon_cards}</div>'
    else:
        coupons_block = f'<p class="muted empty-state">{esc(empty_codes)}</p>'

    cat_cards = []
    for c in categories:
        name = c["name_ar"] if lang == "ar" else c["name_en"]
        d = c["description_ar"] if lang == "ar" else c["description_en"]
        cat_cards.append(
            f'<article class="card"><a href="categories/{esc(c["slug"])}/"><h3>{esc(c.get("icon",""))} {esc(name)}</h3><p>{esc(d)}</p></a></article>'
        )
    country_cards = [
        f'<article class="card"><a href="countries/{esc(c["slug"])}/"><h3>{esc(c["flag"])} {esc(c["name_ar"] if lang == "ar" else c["name_en"])}</h3></a></article>'
        for c in COUNTRIES
    ]
    body = f"""<section class="hero"><div class="container">
  <h1>{esc(h1)}</h1>
  <p>{esc(lead)}</p>
</div></section>
<main id="main" class="container">
  <a class="season-banner" href="seasons/">{esc(season_label)} →</a>
  <section class="section">
    <div class="section-head"><h2>{esc(top_stores)}</h2></div>
    {stores_block}
  </section>
  <section class="section">
    <div class="section-head"><h2>{esc(today_label)}</h2></div>
    {coupons_block}
  </section>
  <section class="section">
    <div class="section-head"><h2>{esc(cats_label)}</h2></div>
    <div class="grid">{"".join(cat_cards)}</div>
  </section>
  <section class="section">
    <div class="section-head"><h2>{esc(countries_label)}</h2></div>
    <div class="grid">{"".join(country_cards)}</div>
  </section>
</main>
"""
    search_path = "/stores/?q={search_term_string}" if lang == "ar" else "/en/stores/?q={search_term_string}"
    web = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME_AR if lang == "ar" else SITE_NAME_EN,
        "url": page_url(lang),
        "inLanguage": "ar-SA" if lang == "ar" else "en",
        "description": desc,
        "potentialAction": {
            "@type": "SearchAction",
            "target": {"@type": "EntryPoint", "urlTemplate": DOMAIN + search_path},
            "query-input": "required name=search_term_string",
        },
    }
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": SITE_NAME_AR if lang == "ar" else SITE_NAME_EN,
        "url": DOMAIN + "/",
        "logo": DOMAIN + "/assets/icon-512.png",
        "description": desc,
    }
    write(out_dir / "index.html", wrap_page(lang, depth, title, desc, canon, body, [web, org]))



def build_store(lang: str, store: dict, stores: list[dict], categories: list[dict], out_dir: Path, depth: int) -> None:
    loc = lang_prefix(depth)
    name = store["name_ar"] if lang == "ar" else store["name_en"]
    desc = store["description_ar"] if lang == "ar" else store["description_en"]
    if lang == "ar":
        title = f"كود خصم {name} السعودية {YEAR}"
        meta = f"أكواد خصم {name} في السعودية {YEAR}. انسخ الكود وتسوّق مباشرة."
        canon = f"/stores/{store['slug']}/"
        home_label, stores_label = "الرئيسية", "المتاجر"
    else:
        title = f"{name} Discount Code Saudi Arabia {YEAR}"
        meta = f"{name} discount codes for Saudi Arabia {YEAR}. Copy a code and shop."
        canon = f"/en/stores/{store['slug']}/"
        home_label, stores_label = "Home", "Stores"

    bc = render_breadcrumbs(
        [
            (home_label, f"{loc}index.html"),
            (stores_label, f"{loc}stores/"),
            (name, None),
        ]
    )
    example = ""
    if store.get("example"):
        example = f'<div class="example-banner">{esc(t(lang, "هذه صفحة متجر تجريبي — استبدل البيانات قبل النشر.", "This is an EXAMPLE store page — replace data before publishing."))}</div>'

    coupons_html = "\n".join(coupon_card(lang, c) for c in sort_coupons(store.get("coupons") or []))
    empty = f'<p class="muted">{esc(t(lang, "لا توجد أكواد حالياً.", "No codes yet."))}</p>'
    faq_html = faq_section(lang, store.get("faq") or [])

    cat = cat_by_slug(categories, store.get("category") or "")
    cat_line = ""
    if cat:
        cname = cat["name_ar"] if lang == "ar" else cat["name_en"]
        cat_line = f'<p class="muted"><a href="{esc(loc)}categories/{esc(cat["slug"])}/">{esc(cname)}</a></p>'

    countries_bits = []
    for cs in store.get("countries") or []:
        co = country_by_slug(cs)
        if co:
            n = co["name_ar"] if lang == "ar" else co["name_en"]
            countries_bits.append(
                f'<a class="chip" href="{esc(loc)}countries/{esc(cs)}/">{esc(co["flag"] + " " + n)}</a>'
            )

    cat_slug = store.get("category") or ""
    pub = public_stores(stores)
    peers = [s for s in pub if s.get("slug") != store.get("slug") and s.get("category") == cat_slug]
    if not peers:
        peers = [s for s in pub if s.get("slug") != store.get("slug")]
    peers = peers[:4]
    related_html = ""
    if peers:
        related_cards = "\n".join(store_card(lang, s, categories, depth) for s in peers)
        related_title = t(lang, "متاجر مشابهة", "Related stores")
        related_html = f"""  <section class="section related-stores">
    <div class="section-head"><h2>{esc(related_title)}</h2></div>
    <div class="grid">{related_cards}</div>
  </section>"""

    body = f"""{bc}
<main id="main" class="container">
  <h1>{esc(t(lang, f"كود خصم {name}", f"{name} discount codes"))}</h1>
  {example}
  <p>{esc(desc)}</p>
  {cat_line}
  <div class="store-meta" style="margin:1rem 0">{"".join(countries_bits)}</div>
  <section class="section">
    <div class="section-head"><h2>{esc(t(lang, "الأكواد المتاحة", "Available codes"))}</h2></div>
    <div class="grid">{coupons_html or empty}</div>
  </section>
  {faq_html}
{related_html}
</main>
"""
    jsonld: list[dict] = [
        breadcrumb_jsonld(
            [
                (home_label, page_url(lang)),
                (stores_label, page_url(lang, "stores")),
                (name, page_url(lang, "stores", store["slug"])),
            ]
        ),
        itemlist_offers_jsonld(lang, store),
    ]
    faq_ld = faq_jsonld(store.get("faq") or [], lang)
    if faq_ld:
        jsonld.append(faq_ld)
    write(out_dir / "stores" / store["slug"] / "index.html", wrap_page(lang, depth, title, meta, canon, body, jsonld))


def build_stores_index(lang: str, stores: list[dict], categories: list[dict], out_dir: Path, depth: int) -> None:
    stores = public_stores(stores)
    loc = lang_prefix(depth)
    if lang == "ar":
        title, desc, canon, h1 = (
            f"جميع المتاجر | أكواد خصم السعودية {YEAR}",
            "قائمة متاجر أكواد الخصم في السعودية والخليج.",
            "/stores/",
            "جميع المتاجر",
        )
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), ("المتاجر", None)])
    else:
        title, desc, canon, h1 = (
            f"All stores | Saudi discount codes {YEAR}",
            "List of discount-code stores for Saudi Arabia and the GCC.",
            "/en/stores/",
            "All stores",
        )
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), ("Stores", None)])
    if stores:
        cards = "\n".join(store_card(lang, s, categories, depth) for s in stores)
        grid = f'<div class="grid">{cards}</div>'
    else:
        grid = f'<p class="muted empty-state">{esc(t(lang, "ما فيه متاجر بعد — قريب نضيف أكواد حقيقية.", "No stores yet — real codes will appear here soon."))}</p>'
    body = f"""{bc}<main id="main" class="container"><h1>{esc(h1)}</h1>{grid}</main>"""
    write(out_dir / "stores" / "index.html", wrap_page(lang, depth, title, desc, canon, body))


def build_category(lang: str, cat: dict, stores: list[dict], categories: list[dict], out_dir: Path, depth: int) -> None:
    loc = lang_prefix(depth)
    name = cat["name_ar"] if lang == "ar" else cat["name_en"]
    desc = cat["description_ar"] if lang == "ar" else cat["description_en"]
    filtered = [s for s in public_stores(stores) if s.get("category") == cat["slug"]]
    if lang == "ar":
        title, canon = f"أكواد خصم {name} السعودية {YEAR}", f"/categories/{cat['slug']}/"
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), ("التصنيفات", f"{loc}categories/"), (name, None)])
    else:
        title, canon = f"{name} discount codes Saudi Arabia {YEAR}", f"/en/categories/{cat['slug']}/"
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), ("Categories", f"{loc}categories/"), (name, None)])
    cards = "\n".join(store_card(lang, s, categories, depth) for s in filtered) or (
        f'<p class="muted">{esc(t(lang, "لا متاجر في هذا التصنيف بعد.", "No stores in this category yet."))}</p>'
    )
    body = f"""{bc}<main id="main" class="container"><h1>{esc(cat.get("icon",""))} {esc(name)}</h1><p>{esc(desc)}</p><div class="grid" style="margin-top:1.2rem">{cards}</div></main>"""
    write(out_dir / "categories" / cat["slug"] / "index.html", wrap_page(lang, depth, title, desc, canon, body))


def build_categories_index(lang: str, categories: list[dict], out_dir: Path, depth: int) -> None:
    loc = lang_prefix(depth)
    if lang == "ar":
        title, desc, canon, h1 = (
            f"التصنيفات | أكواد خصم السعودية {YEAR}",
            "تصفح أكواد الخصم حسب التصنيف.",
            "/categories/",
            "التصنيفات",
        )
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), ("التصنيفات", None)])
    else:
        title, desc, canon, h1 = (
            f"Categories | Saudi discount codes {YEAR}",
            "Browse discount codes by category.",
            "/en/categories/",
            "Categories",
        )
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), ("Categories", None)])
    cards = []
    for c in categories:
        name = c["name_ar"] if lang == "ar" else c["name_en"]
        d = c["description_ar"] if lang == "ar" else c["description_en"]
        cards.append(
            f'<article class="card"><a href="{esc(c["slug"])}/"><h3>{esc(c.get("icon",""))} {esc(name)}</h3><p>{esc(d)}</p></a></article>'
        )
    body = f"""{bc}<main id="main" class="container"><h1>{esc(h1)}</h1><div class="grid">{"".join(cards)}</div></main>"""
    write(out_dir / "categories" / "index.html", wrap_page(lang, depth, title, desc, canon, body))


def build_country(lang: str, country: dict, stores: list[dict], categories: list[dict], out_dir: Path, depth: int) -> None:
    loc = lang_prefix(depth)
    name = country["name_ar"] if lang == "ar" else country["name_en"]
    filtered = [s for s in public_stores(stores) if country["slug"] in (s.get("countries") or [])]
    if lang == "ar":
        title = f"أكواد خصم {name} {YEAR}"
        desc = f"أكواد خصم وكوبونات للمتسوقين في {name}."
        canon = f"/countries/{country['slug']}/"
        h1 = f"أكواد خصم {name}"
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), ("الدول", f"{loc}countries/"), (name, None)])
    else:
        title = f"{name} discount codes {YEAR}"
        desc = f"Discount codes and coupons for shoppers in {name}."
        canon = f"/en/countries/{country['slug']}/"
        h1 = f"{name} discount codes"
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), ("Countries", f"{loc}countries/"), (name, None)])
    cards = "\n".join(store_card(lang, s, categories, depth) for s in filtered) or (
        f'<p class="muted">{esc(t(lang, "لا متاجر لهذه الدولة بعد.", "No stores for this country yet."))}</p>'
    )
    body = f"""{bc}<main id="main" class="container"><h1>{esc(country["flag"])} {esc(h1)}</h1><div class="grid" style="margin-top:1.2rem">{cards}</div></main>"""
    write(out_dir / "countries" / country["slug"] / "index.html", wrap_page(lang, depth, title, desc, canon, body))


def build_countries_index(lang: str, out_dir: Path, depth: int) -> None:
    loc = lang_prefix(depth)
    if lang == "ar":
        title, desc, canon, h1 = (
            f"الدول | أكواد خصم الخليج {YEAR}",
            "أكواد خصم حسب الدولة: السعودية، الإمارات، الكويت.",
            "/countries/",
            "حسب الدولة",
        )
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), ("الدول", None)])
    else:
        title, desc, canon, h1 = (
            f"Countries | GCC discount codes {YEAR}",
            "Discount codes by country: Saudi Arabia, UAE, Kuwait.",
            "/en/countries/",
            "By country",
        )
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), ("Countries", None)])
    cards = [
        f'<article class="card"><a href="{esc(c["slug"])}/"><h3>{esc(c["flag"])} {esc(c["name_ar"] if lang == "ar" else c["name_en"])}</h3></a></article>'
        for c in COUNTRIES
    ]
    body = f"""{bc}<main id="main" class="container"><h1>{esc(h1)}</h1><div class="grid">{"".join(cards)}</div></main>"""
    write(out_dir / "countries" / "index.html", wrap_page(lang, depth, title, desc, canon, body))


def build_season(lang: str, season: dict, stores: list[dict], out_dir: Path, depth: int) -> None:
    loc = lang_prefix(depth)
    name = season["name_ar"] if lang == "ar" else season["name_en"]
    blurb = season["blurb_ar"] if lang == "ar" else season["blurb_en"]
    flat = sort_coupons(all_coupons_flat(public_stores(stores)))[:12]
    if lang == "ar":
        title, canon = f"أكواد خصم {name} السعودية {YEAR}", f"/seasons/{season['slug']}/"
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), ("المواسم", f"{loc}seasons/"), (name, None)])
    else:
        title, canon = f"{name} discount codes Saudi Arabia {YEAR}", f"/en/seasons/{season['slug']}/"
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), ("Seasons", f"{loc}seasons/"), (name, None)])
    note = t(
        lang,
        "صفحة موسمية دائمة — نحدّث الأكواد من ملف البيانات عند اقتراب الموسم.",
        "Evergreen seasonal page — we update codes in the data file as the season approaches.",
    )
    if flat:
        cards = "\n".join(coupon_card(lang, c, c.get("_store"), depth) for c in flat)
        grid = f'<div class="grid" style="margin-top:1.2rem">{cards}</div>'
    else:
        grid = (
            f'<p class="muted empty-state" style="margin-top:1.2rem">'
            f'{esc(t(lang, "ما فيه أكواد لهذا الموسم حالياً.", "No codes for this season yet."))}</p>'
        )
    body = f"""{bc}<main id="main" class="container">
  <h1>{esc(name)}</h1>
  <p>{esc(blurb)}</p>
  <p class="muted">{esc(note)}</p>
  {grid}
</main>"""
    write(out_dir / "seasons" / season["slug"] / "index.html", wrap_page(lang, depth, title, blurb, canon, body))



def build_seasons_index(lang: str, out_dir: Path, depth: int) -> None:
    loc = lang_prefix(depth)
    if lang == "ar":
        title, desc, canon, h1 = (
            f"المواسم والعروض | أكواد خصم السعودية {YEAR}",
            "صفحات موسمية: الجمعة البيضاء، رمضان، ١١.١١، اليوم الوطني، يوم التأسيس.",
            "/seasons/",
            "المواسم والعروض",
        )
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), ("المواسم", None)])
    else:
        title, desc, canon, h1 = (
            f"Seasons & sales | Saudi discount codes {YEAR}",
            "Seasonal pages: White Friday, Ramadan, 11.11, National Day, Founding Day.",
            "/en/seasons/",
            "Seasons & sales",
        )
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), ("Seasons", None)])
    cards = []
    for s in SEASONS:
        name = s["name_ar"] if lang == "ar" else s["name_en"]
        blurb = s["blurb_ar"] if lang == "ar" else s["blurb_en"]
        cards.append(
            f'<article class="card"><a href="{esc(s["slug"])}/"><h3>{esc(name)}</h3><p>{esc(blurb)}</p></a></article>'
        )
    body = f"""{bc}<main id="main" class="container"><h1>{esc(h1)}</h1><div class="grid">{"".join(cards)}</div></main>"""
    write(out_dir / "seasons" / "index.html", wrap_page(lang, depth, title, desc, canon, body))


def static_content(page: str, lang: str) -> tuple[str, str, str]:
    if page == "about":
        if lang == "ar":
            return (
                f"من نحن | {SITE_NAME_AR}",
                "موقع أكواد خصم يركز على المتسوقين في السعودية ثم دول الخليج.",
                f"""<h1>من نحن</h1>
<p><strong>{SITE_NAME_AR}</strong> موقع مستقل لتجميع أكواد الخصم والكوبونات، موجّه أولاً للمتسوقين في السعودية، ثم باقي دول الخليج، وللمسوقين اللي يدورون مصادر موثوقة للكوبونات.</p>
<p>ما نبيع منتجات — نساعدكم توصلون لكود خصم وتستخدمونه عند المتجر مباشرة.</p>
<p>المحتوى يُدار يدوياً: نضيف المتاجر والأكواد بعد مراجعتها. شوف صفحة <a href="../how-we-verify/">كيف نتحقق من الأكواد</a>.</p>""",
            )
        return (
            f"About | {SITE_NAME_EN}",
            "An independent coupon site focused on Saudi shoppers, then the GCC.",
            f"""<h1>About</h1>
<p><strong>{SITE_NAME_EN}</strong> is an independent discount-code site aimed first at shoppers in Saudi Arabia, then the wider GCC, and at marketers looking for reliable coupon sources.</p>
<p>We do not sell products — we help you find a code and use it at the store.</p>
<p>Content is managed manually. See <a href="../how-we-verify/">how we verify codes</a>.</p>""",
        )
    if page == "how-we-verify":
        if lang == "ar":
            return (
                f"كيف نتحقق من الأكواد | {SITE_NAME_AR}",
                "طريقة التحقق من أكواد الخصم قبل نشرها على الموقع.",
                """<h1>كيف نتحقق من الأكواد</h1>
<ol>
<li>نجمع الأكواد من شبكات التسويق بالعمولة أو من المتجر نفسه.</li>
<li>نراجع تاريخ الانتهاء والشروط الظاهرة.</li>
<li>نحدّث تاريخ «متحقق» عند إعادة الفحص.</li>
<li>الأكواد المنتهية تُزال أو تُعلَّم بوضوح.</li>
</ol>
<p>ما نضمن إن كل كود يشتغل لكل مستخدم — الشروط تختلف حسب السلة والدولة والحساب. لو لقيت كود ما اشتغل، أخبرنا.</p>
<p>صفحات الأمثلة في الموقع معلّمة صراحةً بكلمة «مثال تجريبي».</p>""",
            )
        return (
            f"How we verify | {SITE_NAME_EN}",
            "How we check discount codes before publishing them.",
            """<h1>How we verify codes</h1>
<ol>
<li>We collect codes from affiliate networks or the store itself.</li>
<li>We review expiry dates and visible terms.</li>
<li>We update the “verified” date when we re-check.</li>
<li>Expired codes are removed or clearly marked.</li>
</ol>
<p>We cannot guarantee every code works for every shopper — terms vary by cart, country, and account.</p>
<p>Example pages on this site are clearly labeled EXAMPLE.</p>""",
        )
    if page == "privacy":
        if lang == "ar":
            return (
                f"الخصوصية | {SITE_NAME_AR}",
                "سياسة الخصوصية لموقع أكواد الخصم.",
                """<h1>الخصوصية</h1>
<p>الموقع صفحات ثابتة. ما نطلب إنشاء حساب للتصفح.</p>
<p>قد تُستخدم روابط عمولة؛ عند الضغط عليها تنتقل لمتجر خارجي بسياسته الخاصة.</p>
<p>لو أُضيف لاحقاً تحليلات أو أدوات قياس، سنوضّحها هنا.</p>
<p>للتواصل: عبر النطاق <strong>ye7ia.is-a.si</strong>.</p>""",
            )
        return (
            f"Privacy | {SITE_NAME_EN}",
            "Privacy policy for the coupon site.",
            """<h1>Privacy</h1>
<p>This site is static. You do not need an account to browse.</p>
<p>We may use affiliate links; clicking them takes you to a third-party store with its own policy.</p>
<p>If analytics are added later, we will disclose them here.</p>
<p>Contact via <strong>ye7ia.is-a.si</strong>.</p>""",
        )
    if page == "affiliate-disclosure":
        if lang == "ar":
            return (
                f"الإفصاح عن العمولات | {SITE_NAME_AR}",
                "إفصاح عن روابط التسويق بالعمولة في موقع أكواد الخصم.",
                """<h1>الإفصاح عن العمولات</h1>
<p>بعض الروابط في هذا الموقع روابط تسويق بالعمولة. إذا اشتريت عبرها، قد نحصل على عمولة بدون ما تدفع زيادة.</p>
<p>هذا يساعدنا نغطي تشغيل الموقع. اختيار المتجر والشراء قرارك أنت.</p>
<p>ما نبالغ في وصف الخصم، وما نعرض إحصائيات وهمية.</p>""",
            )
        return (
            f"Affiliate disclosure | {SITE_NAME_EN}",
            "Affiliate link disclosure for the coupon site.",
            """<h1>Affiliate disclosure</h1>
<p>Some links on this site are affiliate links. If you buy through them, we may earn a commission at no extra cost to you.</p>
<p>That helps keep the site running. Choosing a store and buying is your decision.</p>
<p>We do not invent fake savings stats.</p>""",
        )
    if page == "marketers":
        if lang == "ar":
            return (
                f"للمسوقين | {SITE_NAME_AR}",
                "صفحة للمسوقين بالعمولة والناشرين المهتمين بأكواد الخصم في السعودية والخليج.",
                """<h1>للمسوقين والناشرين</h1>
<p>إذا كنت مسوّق بالعمولة أو عندك موقع/قناة وتدور مصادر أكواد خصم تستهدف السعودية والخليج، هالصفحة لك.</p>
<h2>ليش الموقع؟</h2>
<ul>
<li>تركيز لغوي وسعودي واضح (عربي أولاً + إنجليزي).</li>
<li>صفحات متاجر وتصنيفات ودول ومواسم جاهزة لمحركات البحث.</li>
<li>بيانات منظمة (JSON) يسهل تحديثها يومياً.</li>
</ul>
<h2>شبكات مقترحة للانضمام</h2>
<ul>
<li>Admitad</li>
<li>ArabClicks</li>
<li>Boostiny</li>
<li>Awin / Impact / Amazon Associates (حسب المتجر)</li>
</ul>
<p>تواصل لإضافة متجرك أو عرض كود حصري عبر النطاق ye7ia.is-a.si.</p>
<p class="muted">ملاحظة: القائمة أعلاه أسماء شبكات معروفة وليست إعلان مدفوع.</p>""",
            )
        return (
            f"For marketers | {SITE_NAME_EN}",
            "For affiliate marketers and publishers interested in GCC discount codes.",
            """<h1>For marketers & publishers</h1>
<p>If you are an affiliate marketer or publisher looking for Saudi/GCC coupon inventory, this page is for you.</p>
<h2>Why this site</h2>
<ul>
<li>Clear Saudi-first Arabic + English structure.</li>
<li>Store, category, country, and seasonal pages built for search.</li>
<li>JSON-driven data that is easy to update daily.</li>
</ul>
<h2>Suggested networks</h2>
<ul>
<li>Admitad</li>
<li>ArabClicks</li>
<li>Boostiny</li>
<li>Awin / Impact / Amazon Associates (depending on the merchant)</li>
</ul>
<p>Contact via ye7ia.is-a.si to add a store or offer an exclusive code.</p>
<p class="muted">Network names above are well-known options, not paid placements.</p>""",
        )
    raise ValueError(page)


def build_static_page(lang: str, page: str, out_dir: Path, depth: int) -> None:
    title, desc, inner = static_content(page, lang)
    loc = lang_prefix(depth)
    if lang == "ar":
        canon = f"/{page}/"
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), (title.split("|")[0].strip(), None)])
    else:
        canon = f"/en/{page}/"
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), (title.split("|")[0].strip(), None)])
    body = f"""{bc}<main id="main" class="container"><article class="prose">{inner}</article></main>"""
    write(out_dir / page / "index.html", wrap_page(lang, depth, title, desc, canon, body))


def build_404(out_dir: Path) -> None:
    title = "الصفحة غير موجودة | 404"
    desc = "الصفحة المطلوبة غير موجودة."
    body = """<main id="main" class="container not-found">
  <h1>404</h1>
  <p>الصفحة غير موجودة / Page not found</p>
  <p><a class="btn" href="/">العودة للرئيسية</a>
  <a class="btn btn-secondary" href="/en/">English home</a></p>
</main>
"""
    write(
        out_dir / "404.html",
        render_head("ar", title, desc, "/404.html", 0, None)
        + render_header("ar", 0, "/")
        + body
        + render_footer("ar", 0),
    )


def build_robots(out_dir: Path) -> None:
    write(out_dir / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")


def build_cname(out_dir: Path) -> None:
    write(out_dir / "CNAME", "ye7ia.is-a.si\n")


def build_sitemap(out_dir: Path, stores: list[dict], categories: list[dict]) -> None:
    stores = public_stores(stores)
    urls: list[str] = []

    def add(path: str) -> None:
        path = path.replace("//", "/")
        if not path.endswith("/"):
            path += "/"
        urls.append(path)

    add("/")
    add("/en/")
    for prefix in ("", "/en"):
        for p in STATIC_PAGES:
            add(f"{prefix}/{p}")
        add(f"{prefix}/stores")
        add(f"{prefix}/categories")
        add(f"{prefix}/countries")
        add(f"{prefix}/seasons")
        for s in stores:
            add(f"{prefix}/stores/{s['slug']}")
        for c in categories:
            add(f"{prefix}/categories/{c['slug']}")
        for c in COUNTRIES:
            add(f"{prefix}/countries/{c['slug']}")
        for s in SEASONS:
            add(f"{prefix}/seasons/{s['slug']}")

    clean, seen = [], set()
    for u in urls:
        u = u.replace("//", "/")
        if u not in seen:
            seen.add(u)
            clean.append(u)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in clean:
        lines += ["  <url>", f"    <loc>{esc(DOMAIN + u)}</loc>", f"    <lastmod>{TODAY}</lastmod>", "  </url>"]
    lines.append("</urlset>")
    write(out_dir / "sitemap.xml", "\n".join(lines) + "\n")


def copy_assets(out_dir: Path) -> None:
    dest = out_dir / "assets"
    ensure_dir(dest)
    for name in (
        "style.css",
        "app.js",
        "og-default.svg",
        "og-default.png",
        "favicon.svg",
        "favicon.ico",
        "favicon-32.png",
        "apple-touch-icon.png",
        "icon-512.png",
    ):
        src = ASSETS_SRC / name
        dst = dest / name
        if not src.is_file():
            print(f"  skip missing assets/{name}")
            continue
        if src.resolve() == dst.resolve():
            print(f"  assets/{name} already in place")
            continue
        shutil.copy2(src, dst)
        print(f"  copied assets/{name}")


def build_lang_tree(lang: str, stores: list[dict], categories: list[dict], out_dir: Path) -> None:
    home_depth, list_depth, item_depth = 0, 1, 2
    visible = public_stores(stores)
    build_home(lang, visible, categories, out_dir, home_depth)
    build_stores_index(lang, visible, categories, out_dir, list_depth)
    for s in visible:
        build_store(lang, s, visible, categories, out_dir, item_depth)
    build_categories_index(lang, categories, out_dir, list_depth)
    for c in categories:
        build_category(lang, c, visible, categories, out_dir, item_depth)
    build_countries_index(lang, out_dir, list_depth)
    for c in COUNTRIES:
        build_country(lang, c, visible, categories, out_dir, item_depth)
    build_seasons_index(lang, out_dir, list_depth)
    for s in SEASONS:
        build_season(lang, s, visible, out_dir, item_depth)
    for p in STATIC_PAGES:
        build_static_page(lang, p, out_dir, list_depth)


def clean_generated(out_dir: Path) -> None:
    for name in (
        "stores", "categories", "countries", "seasons", "en",
        "about", "how-we-verify", "privacy", "affiliate-disclosure", "marketers",
    ):
        p = out_dir / name
        if p.is_dir():
            shutil.rmtree(p)
            print(f"  cleaned {name}/")
    for name in ("index.html", "404.html", "robots.txt", "sitemap.xml", "CNAME"):
        p = out_dir / name
        if p.is_file():
            p.unlink()


def main() -> None:
    print("Building ye7ia coupon site…")
    stores = load_json(DATA / "coupons.json")
    categories = load_json(DATA / "categories.json")
    out = ROOT
    clean_generated(out)
    copy_assets(out)
    build_cname(out)
    build_robots(out)
    build_404(out)
    build_lang_tree("ar", stores, categories, out)
    ensure_dir(out / "en")
    build_lang_tree("en", stores, categories, out / "en")
    build_sitemap(out, stores, categories)
    print("Done.")


if __name__ == "__main__":
    main()
