#!/usr/bin/env python3
"""
ye7ia coupon site — dependency-free static site generator.
Reads data/coupons.json + data/categories.json, writes HTML to site root.
Run: python3 build.py
"""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ASSETS_SRC = ROOT / "assets"
SITE_NAME_AR = "يحيى كوبونات"
SITE_NAME_EN = "ye7ia Coupons"
DOMAIN = "https://ye7ia.is-a.si"
CONTACT_EMAIL = "partners@ye7ia.is-a.si"
YEAR = 2026
TODAY = date.today().isoformat()

COUNTRIES = [
    {"slug": "sa", "name_ar": "السعودية", "name_en": "Saudi Arabia", "flag": "🇸🇦"},
    {"slug": "ae", "name_ar": "الإمارات", "name_en": "United Arab Emirates", "flag": "🇦🇪"},
    {"slug": "kw", "name_ar": "الكويت", "name_en": "Kuwait", "flag": "🇰🇼"},
    {"slug": "qa", "name_ar": "قطر", "name_en": "Qatar", "flag": "🇶🇦"},
    {"slug": "bh", "name_ar": "البحرين", "name_en": "Bahrain", "flag": "🇧🇭"},
    {"slug": "om", "name_ar": "عُمان", "name_en": "Oman", "flag": "🇴🇲"},
]

# Loaded from data/seasons.json in main() — includes start/end for live chips.
SEASONS: list[dict] = []

REQUIRED_STORE_FIELDS = (
    "slug",
    "name_ar",
    "name_en",
    "category",
    "countries",
    "description_ar",
    "description_en",
)
REQUIRED_COUPON_FIELDS = (
    "code",
    "title_ar",
    "title_en",
    "verified_date",
    "expires",
    "affiliate_url",
)

STATIC_PAGES = [
    "about",
    "how-we-verify",
    "privacy",
    "affiliate-disclosure",
    "marketers",
    "partners",
    "contact",
    "terms",
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


def load_seasons() -> list[dict]:
    """Season metadata + start/end windows from data/seasons.json (end date exclusive)."""
    return load_json(DATA / "seasons.json")


def season_is_live(season: dict, today: str | None = None) -> bool:
    """True when today is in [start, end). Missing dates => not live (no chip)."""
    day = today or TODAY
    start = (season.get("start") or "")[:10]
    end = (season.get("end") or "")[:10]
    if not start or not end:
        return False
    return start <= day < end


def live_seasons(seasons: list[dict] | None = None) -> list[dict]:
    return [s for s in (seasons if seasons is not None else SEASONS) if season_is_live(s)]


def featured_live_season(seasons: list[dict] | None = None) -> dict | None:
    """Prefer White Friday while live; otherwise first live season."""
    live = live_seasons(seasons)
    for s in live:
        if s.get("slug") == "white-friday":
            return s
    return live[0] if live else None


PLACEHOLDER_CODES = {"REALCODE", "YOURCODE", "CODEHERE", "EXAMPLE", "TESTCODE"}
PLACEHOLDER_HOST_MARKERS = ("example.com", "example.org", "localhost")


def _is_https_url(url: str) -> bool:
    if not isinstance(url, str) or not url:
        return False
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    return parsed.scheme == "https" and bool(parsed.hostname)


def _is_iso_date(value: str) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _url_is_placeholder(url: str) -> bool:
    low = (url or "").lower()
    return any(m in low for m in PLACEHOLDER_HOST_MARKERS)


def validate_stores(stores: list[dict]) -> None:
    """Fail the build if non-example stores/coupons miss fields, use bad URLs/dates, or placeholders."""
    errors: list[str] = []
    for store in stores:
        slug = store.get("slug") or "<missing-slug>"
        if store.get("example"):
            continue
        for field in REQUIRED_STORE_FIELDS:
            val = store.get(field)
            if val is None or val == "" or val == []:
                errors.append(f"store '{slug}': missing required field '{field}'")
        for url_field in ("website", "affiliate_url"):
            val = store.get(url_field)
            if val in (None, ""):
                continue
            if not _is_https_url(val):
                errors.append(f"store '{slug}': '{url_field}' must be an https:// URL")
            elif _url_is_placeholder(val):
                errors.append(f"store '{slug}': '{url_field}' still uses a placeholder host")
        if "coupons" not in store or not isinstance(store.get("coupons"), list):
            errors.append(f"store '{slug}': missing coupons list")
            continue
        for idx, coupon in enumerate(store.get("coupons") or []):
            if coupon.get("example"):
                continue
            label = f"store '{slug}' coupon[{idx}]"
            for field in REQUIRED_COUPON_FIELDS:
                val = coupon.get(field)
                if val is None or val == "":
                    errors.append(f"{label}: missing required field '{field}'")
            code = (coupon.get("code") or "").strip().upper()
            if code in PLACEHOLDER_CODES:
                errors.append(f"{label}: placeholder code '{coupon.get('code')}' is not allowed")
            for date_field in ("verified_date", "expires"):
                val = coupon.get(date_field)
                if val in (None, ""):
                    continue
                if not _is_iso_date(val):
                    errors.append(f"{label}: '{date_field}' must be ISO YYYY-MM-DD")
            aff = coupon.get("affiliate_url")
            if aff not in (None, ""):
                if not _is_https_url(aff):
                    errors.append(f"{label}: 'affiliate_url' must be an https:// URL")
                elif _url_is_placeholder(aff):
                    errors.append(f"{label}: 'affiliate_url' still uses a placeholder host")
            src = coupon.get("source_url")
            if src not in (None, ""):
                if not _is_https_url(src):
                    errors.append(f"{label}: 'source_url' must be an https:// URL")
                elif _url_is_placeholder(src):
                    errors.append(f"{label}: 'source_url' still uses a placeholder host")
    if errors:
        msg = "Coupon data validation failed:\n  - " + "\n  - ".join(errors)
        raise SystemExit(msg)


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
<link rel="shortcut icon" href="{esc(asset_prefix(lang, depth) + "favicon.ico")}">
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
    featured = featured_live_season()
    season_chip = ""
    if featured:
        fname = featured["name_ar"] if lang == "ar" else featured["name_en"]
        start = esc((featured.get("start") or "")[:10])
        end = esc((featured.get("end") or "")[:10])
        aria = esc(t(lang, f"موسم حي: {fname}", f"Live season: {fname}"))
        season_chip = (
            f'<a class="nav-season-chip" href="{esc(loc + "seasons/" + featured["slug"] + "/")}" '
            f'aria-label="{aria}" '
            f'data-season-start="{start}" data-season-end="{end}">'
            f'{esc(fname)}</a>'
        )
    return f"""<a class="skip-link" href="#main">{esc(skip)}</a>
<header class="site-header">
  <div class="container header-inner">
    <a class="logo" href="{esc(loc + "index.html")}"><span>ye7ia</span> {esc(brand_tail)}</a>
    <nav class="nav" aria-label="Main">
      <a href="{esc(loc + "index.html")}">{esc(home)}</a>
      <a href="{esc(loc + "stores/")}">{esc(stores)}</a>
      <a href="{esc(loc + "categories/")}">{esc(cats)}</a>
      <a href="{esc(loc + "seasons/")}">{esc(seasons)}</a>
      {season_chip}
      <a href="{esc(loc + "marketers/")}">{esc(marketers)}</a>
      <a class="lang-switch" href="{esc(switch_href)}" hreflang="{other_lang(lang)}">{esc(switch_label)}</a>
    </nav>
  </div>
</header>
"""



def render_footer(lang: str, depth: int) -> str:
    root = asset_prefix(lang, depth)
    loc = lang_prefix(depth)
    mail = CONTACT_EMAIL
    if lang == "ar":
        links = [
            ("about/", "من نحن"),
            ("how-we-verify/", "كيف نتحقق من الأكواد"),
            ("privacy/", "الخصوصية"),
            ("terms/", "الشروط"),
            ("affiliate-disclosure/", "الإفصاح عن العمولات"),
            ("marketers/", "للمسوقين"),
            ("partners/", "شركاء وإعلان"),
            ("contact/", "تواصل"),
            ("countries/sa/", "السعودية"),
            ("countries/ae/", "الإمارات"),
            ("countries/kw/", "الكويت"),
            ("countries/qa/", "قطر"),
            ("countries/bh/", "البحرين"),
            ("countries/om/", "عُمان"),
        ]
        note = "موقع أكواد خصم مستقل. قد نحصل على عمولة عند استخدام بعض الروابط دون أي تكلفة إضافية عليك."
        brand = SITE_NAME_AR
        links_label = "روابط"
        biz_title = "للمتاجر والشركاء"
        biz_text = "عرض متجرك، كود حصري، أو بانر إعلاني — تواصل للتسعير."
        biz_cta = "تواصل معنا"
        biz_more = "باقات الشراكة"
    else:
        links = [
            ("about/", "About"),
            ("how-we-verify/", "How we verify"),
            ("privacy/", "Privacy"),
            ("terms/", "Terms"),
            ("affiliate-disclosure/", "Affiliate disclosure"),
            ("marketers/", "For marketers"),
            ("partners/", "Partners & advertise"),
            ("contact/", "Contact"),
            ("countries/sa/", "Saudi Arabia"),
            ("countries/ae/", "UAE"),
            ("countries/kw/", "Kuwait"),
            ("countries/qa/", "Qatar"),
            ("countries/bh/", "Bahrain"),
            ("countries/om/", "Oman"),
        ]
        note = "Independent coupon site. We may earn a commission when you use some links, at no extra cost to you."
        brand = SITE_NAME_EN
        links_label = "Links"
        biz_title = "For stores & partners"
        biz_text = "Feature your store, an exclusive code, or a banner — contact for pricing."
        biz_cta = "Contact us"
        biz_more = "Partnership packages"
    items = "\n".join(
        f'      <li><a href="{esc(loc + href)}">{esc(label)}</a></li>' for href, label in links
    )
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <p class="footer-heading">{esc(brand)}</p>
        <p class="muted" style="color:#94a3b8">{esc(note)}</p>
      </div>
      <div>
        <p class="footer-heading">{esc(links_label)}</p>
        <ul>
{items}
        </ul>
      </div>
      <div class="footer-biz">
        <p class="footer-heading">{esc(biz_title)}</p>
        <p class="muted" style="color:#94a3b8">{esc(biz_text)}</p>
        <p><a class="btn" href="{esc(loc + "contact/")}">{esc(biz_cta)}</a>
        <a class="btn btn-secondary" href="{esc(loc + "partners/")}">{esc(biz_more)}</a></p>
        <p class="muted" style="color:#94a3b8;margin-top:0.6rem"><a href="mailto:{esc(mail)}">{esc(mail)}</a></p>
      </div>
    </div>
    <p class="footer-note">© {YEAR} ye7ia.is-a.si</p>
  </div>
</footer>
<div id="cookie-banner" class="cookie-banner" hidden role="dialog" aria-live="polite" aria-label="cookies">
  <div class="cookie-banner-inner">
    <p>{esc(t(lang, "نستخدم تخزيناً محلياً بسيطاً لتفضيلات الصفحة (مثل نسخ الكود). راجع سياسة الخصوصية.", "We use simple local storage for page preferences (such as copying a code). See our privacy policy."))} <a href="{esc(loc + "privacy/")}">{esc(t(lang, "الخصوصية", "Privacy"))}</a></p>
    <button type="button" class="btn" id="cookie-accept">{esc(t(lang, "حسناً", "OK"))}</button>
  </div>
</div>
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
    search_blob = " ".join(
        [
            store.get("name_ar") or "",
            store.get("name_en") or "",
            store.get("slug") or "",
            store.get("description_ar") or "",
            store.get("description_en") or "",
            cat_name,
        ]
    ).lower()
    return f"""<article class="card store-card" data-store-card data-search="{esc(search_blob)}">
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


def webpage_jsonld(lang: str, title: str, description: str, canonical_path: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": DOMAIN + canonical_path,
        "inLanguage": "ar-SA" if lang == "ar" else "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": SITE_NAME_AR if lang == "ar" else SITE_NAME_EN,
            "url": DOMAIN + "/",
        },
    }


def org_contactpoint_jsonld(lang: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": SITE_NAME_AR if lang == "ar" else SITE_NAME_EN,
        "url": DOMAIN + "/",
        "logo": DOMAIN + "/assets/icon-512.png",
        "email": CONTACT_EMAIL,
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "sales",
            "email": CONTACT_EMAIL,
            "availableLanguage": ["ar", "en"],
            "url": page_url(lang, "contact"),
        },
    }


def contactpage_jsonld(lang: str, title: str, description: str, canonical_path: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": title,
        "description": description,
        "url": DOMAIN + canonical_path,
        "inLanguage": "ar-SA" if lang == "ar" else "en",
        "mainEntity": org_contactpoint_jsonld(lang),
    }


def collection_page_jsonld(
    lang: str,
    title: str,
    description: str,
    canonical_path: str,
    list_items: list[tuple[str, str]] | None = None,
) -> dict:
    """CollectionPage; optional ItemList of real existing page URLs only (never invented deals)."""
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": description,
        "url": DOMAIN + canonical_path,
        "inLanguage": "ar-SA" if lang == "ar" else "en",
    }
    if list_items:
        data["mainEntity"] = {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": name,
                    "url": url,
                }
                for i, (name, url) in enumerate(list_items)
            ],
        }
    return data


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
    blocks = list(jsonld or [])
    if not any(isinstance(b, dict) and b.get("@type") in ("WebPage", "ContactPage") for b in blocks):
        blocks.insert(0, webpage_jsonld(lang, title, description, canonical_path))
    return (
        render_head(lang, title, description, canonical_path, depth, blocks)
        + render_header(lang, depth, canonical_path)
        + body
        + render_footer(lang, depth)
    )



def empty_state_block(lang: str, depth: int, message: str) -> str:
    """Soft empty UX with real CTAs (browse categories + partners)."""
    loc = lang_prefix(depth)
    cats_label = t(lang, "تصفّح التصنيفات", "Browse categories")
    partners_label = t(lang, "للمتاجر والشركاء", "For stores & partners")
    return (
        f'<div class="empty-state">'
        f'<p class="muted">{esc(message)}</p>'
        f'<div class="empty-state-actions">'
        f'<a class="btn" href="{esc(loc + "categories/")}">{esc(cats_label)}</a>'
        f'<a class="btn btn-secondary" href="{esc(loc + "partners/")}">{esc(partners_label)}</a>'
        f'</div></div>'
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
        season_label_generic = "عرض موسمي: تصفّح أكواد الجمعة البيضاء ورمضان واليوم الوطني"
        top_stores, today_label = "أبرز المتاجر", "أكواد محدثة"
        cats_label, countries_label = "تصفح حسب التصنيف", "حسب الدولة"
        empty_stores = "ما فيه متاجر معروضة حالياً."
        empty_codes = "ما فيه أكواد معروضة حالياً."
        canon = "/"
    else:
        title = f"Saudi Discount Codes {YEAR} | {SITE_NAME_EN}"
        desc = "Discount codes and coupons for stores in Saudi Arabia and the GCC. Copy a code and shop."
        h1 = f"Trusted discount codes for Saudi shoppers {YEAR}"
        lead = "Save on popular stores. We focus on Saudi Arabia first, then the wider GCC."
        season_label_generic = "Seasonal: browse White Friday, Ramadan, and National Day codes"
        top_stores, today_label = "Top stores", "Recently verified codes"
        cats_label, countries_label = "Browse by category", "By country"
        empty_stores = "No stores listed yet."
        empty_codes = "No codes to show right now."
        canon = "/en/"

    if stores:
        store_cards = "\n".join(store_card(lang, s, categories, depth) for s in stores)
        stores_block = f'<div class="grid">{store_cards}</div>'
    else:
        stores_block = empty_state_block(lang, depth, empty_stores)

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
    if lang == "ar":
        biz_h = "متجر أو علامة تجارية؟"
        biz_p = "أبرز متجرك، انشر كوداً حصرياً، أو احجز بانر — تواصل للتسعير."
        biz_contact = "تواصل معنا"
        biz_partners = "باقات الشراكة والإعلان"
    else:
        biz_h = "Store or brand?"
        biz_p = "Feature your store, publish an exclusive code, or book a banner — contact for pricing."
        biz_contact = "Contact us"
        biz_partners = "Partnership & advertising packages"
    featured = featured_live_season()
    if featured and featured.get("slug") == "white-friday":
        season_href = f"seasons/{featured['slug']}/"
        season_label = t(
            lang,
            "الجمعة البيضاء: تصفّح أكواد الخصم الموسمية",
            "White Friday: browse seasonal discount codes",
        )
        season_start = (featured.get("start") or "")[:10]
        season_end = (featured.get("end") or "")[:10]
    elif featured:
        fname = featured["name_ar"] if lang == "ar" else featured["name_en"]
        season_href = f"seasons/{featured['slug']}/"
        season_label = t(lang, f"موسم نشط: {fname}", f"Live season: {fname}")
        season_start = (featured.get("start") or "")[:10]
        season_end = (featured.get("end") or "")[:10]
    else:
        season_href = "seasons/"
        season_label = season_label_generic
        season_start = ""
        season_end = ""
    season_attrs = ""
    if season_start and season_end and featured:
        fname = featured["name_ar"] if lang == "ar" else featured["name_en"]
        banner_aria = esc(t(lang, f"موسم حي: {fname}", f"Live season: {fname}"))
        season_attrs = (
            f' aria-label="{banner_aria}"'
            f' data-season-start="{esc(season_start)}" data-season-end="{esc(season_end)}"'
        )
    body = f"""<section class="hero"><div class="container">
  <h1>{esc(h1)}</h1>
  <p>{esc(lead)}</p>
</div></section>
<main id="main" class="container">
  <a class="season-banner" href="{esc(season_href)}"{season_attrs}>{esc(season_label)} →</a>
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
  <section class="section business-cta">
    <div class="business-cta-inner">
      <h2>{esc(biz_h)}</h2>
      <p>{esc(biz_p)}</p>
      <p>
        <a class="btn" href="contact/">{esc(biz_contact)}</a>
        <a class="btn btn-secondary" href="partners/">{esc(biz_partners)}</a>
      </p>
    </div>
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
    org = org_contactpoint_jsonld(lang)
    org["description"] = desc
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
        search_label = "ابحث عن متجر"
        search_ph = "اسم المتجر…"
        no_match = "ما لقينا متاجر مطابقة."
        home_label, stores_label = "الرئيسية", "المتاجر"
    else:
        title, desc, canon, h1 = (
            f"All stores | Saudi discount codes {YEAR}",
            "List of discount-code stores for Saudi Arabia and the GCC.",
            "/en/stores/",
            "All stores",
        )
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), ("Stores", None)])
        search_label = "Search stores"
        search_ph = "Store name…"
        no_match = "No matching stores."
        home_label, stores_label = "Home", "Stores"
    empty_yet = t(
        lang,
        "ما فيه متاجر معروضة حالياً.",
        "No stores listed yet.",
    )
    cards = "\n".join(store_card(lang, s, categories, depth) for s in stores) if stores else ""
    # Always render #store-grid (empty message lives inside) so client search (?q=) works with zero stores.
    empty_initial = "" if stores else empty_yet
    empty_hidden = "hidden" if stores else ""
    empty = (
        f'<p id="store-search-empty" class="muted empty-state" {empty_hidden}>'
        f"{esc(empty_initial or no_match)}</p>"
    )
    grid = f'<div class="grid" id="store-grid">{cards}{empty}</div>'
    search = f"""<form class="store-search" role="search" action="" method="get">
  <label class="store-search-label" for="store-q">{esc(search_label)}</label>
  <input id="store-q" name="q" type="search" enterkeyhint="search" autocomplete="off"
    placeholder="{esc(search_ph)}" data-no-match="{esc(no_match)}" data-empty-yet="{esc(empty_yet)}">
</form>"""
    body = f"""{bc}<main id="main" class="container"><h1>{esc(h1)}</h1>{search}{grid}</main>"""
    jsonld = [
        breadcrumb_jsonld(
            [
                (home_label, page_url(lang)),
                (stores_label, page_url(lang, "stores")),
            ]
        )
    ]
    write(out_dir / "stores" / "index.html", wrap_page(lang, depth, title, desc, canon, body, jsonld))


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
    if filtered:
        cards = "\n".join(store_card(lang, s, categories, depth) for s in filtered)
        content = f'<div class="grid grid-spaced">{cards}</div>'
    else:
        content = empty_state_block(
            lang,
            depth,
            t(lang, "ما فيه متاجر في هذا التصنيف حالياً.", "No stores in this category yet."),
        )
    body = f"""{bc}<main id="main" class="container"><h1>{esc(cat.get("icon",""))} {esc(name)}</h1><p>{esc(desc)}</p>{content}</main>"""
    home_label = "الرئيسية" if lang == "ar" else "Home"
    cats_label = "التصنيفات" if lang == "ar" else "Categories"
    jsonld = [
        breadcrumb_jsonld(
            [
                (home_label, page_url(lang)),
                (cats_label, page_url(lang, "categories")),
                (name, DOMAIN + canon),
            ]
        )
    ]
    write(out_dir / "categories" / cat["slug"] / "index.html", wrap_page(lang, depth, title, desc, canon, body, jsonld))


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
    if filtered:
        cards = "\n".join(store_card(lang, s, categories, depth) for s in filtered)
        content = f'<div class="grid grid-spaced">{cards}</div>'
    else:
        content = empty_state_block(
            lang,
            depth,
            t(lang, "ما فيه متاجر لهذه الدولة حالياً.", "No stores for this country yet."),
        )
    body = f"""{bc}<main id="main" class="container"><h1>{esc(country["flag"])} {esc(h1)}</h1>{content}</main>"""
    home_label = "الرئيسية" if lang == "ar" else "Home"
    countries_label = "الدول" if lang == "ar" else "Countries"
    jsonld = [
        breadcrumb_jsonld(
            [
                (home_label, page_url(lang)),
                (countries_label, page_url(lang, "countries")),
                (name, DOMAIN + canon),
            ]
        )
    ]
    write(out_dir / "countries" / country["slug"] / "index.html", wrap_page(lang, depth, title, desc, canon, body, jsonld))


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


def build_season(
    lang: str,
    season: dict,
    stores: list[dict],
    categories: list[dict],
    out_dir: Path,
    depth: int,
) -> None:
    loc = lang_prefix(depth)
    name = season["name_ar"] if lang == "ar" else season["name_en"]
    blurb = season["blurb_ar"] if lang == "ar" else season["blurb_en"]
    flat = sort_coupons(all_coupons_flat(public_stores(stores)))[:12]
    if lang == "ar":
        title, canon = f"أكواد خصم {name} السعودية {YEAR}", f"/seasons/{season['slug']}/"
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), ("المواسم", f"{loc}seasons/"), (name, None)])
        home_label, seasons_label, related_h = "الرئيسية", "المواسم", "تصفّح حسب التصنيف"
    else:
        title, canon = f"{name} discount codes Saudi Arabia {YEAR}", f"/en/seasons/{season['slug']}/"
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), ("Seasons", f"{loc}seasons/"), (name, None)])
        home_label, seasons_label, related_h = "Home", "Seasons", "Browse by category"
    note = t(
        lang,
        "صفحة موسمية دائمة — نحدّث الأكواد من ملف البيانات عند اقتراب الموسم.",
        "Evergreen seasonal page — we update codes in the data file as the season approaches.",
    )
    if flat:
        cards = "\n".join(coupon_card(lang, c, c.get("_store"), depth) for c in flat)
        grid = f'<div class="grid grid-spaced">{cards}</div>'
    else:
        grid = empty_state_block(
            lang,
            depth,
            t(lang, "ما فيه أكواد لهذا الموسم حالياً.", "No codes for this season yet."),
        )
    related_items = []
    list_items: list[tuple[str, str]] = []
    for c in categories:
        cname = c["name_ar"] if lang == "ar" else c["name_en"]
        href = f"{loc}categories/{c['slug']}/"
        icon = c.get("icon", "")
        label = f"{icon} {cname}".strip() if icon else cname
        related_items.append(
            f'<li><a class="related-cat-link" href="{esc(href)}">{esc(label)}</a></li>'
        )
        list_items.append((cname, page_url(lang, "categories", c["slug"])))
    related = ""
    if related_items:
        related = (
            f'<section class="section related-categories" aria-labelledby="season-related-heading">'
            f'<div class="section-head"><h2 id="season-related-heading">{esc(related_h)}</h2></div>'
            f'<ul class="related-cat-list">{"".join(related_items)}</ul></section>'
        )
    body = f"""{bc}<main id="main" class="container">
  <h1>{esc(name)}</h1>
  <p>{esc(blurb)}</p>
  <p class="muted">{esc(note)}</p>
  {grid}
  {related}
</main>"""
    jsonld = [
        breadcrumb_jsonld(
            [
                (home_label, page_url(lang)),
                (seasons_label, page_url(lang, "seasons")),
                (name, page_url(lang, "seasons", season["slug"])),
            ]
        ),
        collection_page_jsonld(lang, title, blurb, canon, list_items or None),
    ]
    write(
        out_dir / "seasons" / season["slug"] / "index.html",
        wrap_page(lang, depth, title, blurb, canon, body, jsonld),
    )



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
    featured = featured_live_season()
    live_badge = t(lang, "مباشر الآن", "Live now")
    # Feature live seasons first (White Friday preferred via featured_live_season order).
    ordered = sorted(
        SEASONS,
        key=lambda s: (
            0 if featured and s.get("slug") == featured.get("slug") else 1,
            0 if season_is_live(s) else 1,
        ),
    )
    cards = []
    for s in ordered:
        name = s["name_ar"] if lang == "ar" else s["name_en"]
        blurb = s["blurb_ar"] if lang == "ar" else s["blurb_en"]
        badge = ""
        if season_is_live(s):
            badge = f'<span class="chip chip-live">{esc(live_badge)}</span>'
        cards.append(
            f'<article class="card"><a href="{esc(s["slug"])}/"><h3>{esc(name)} {badge}</h3><p>{esc(blurb)}</p></a></article>'
        )
    body = f"""{bc}<main id="main" class="container"><h1>{esc(h1)}</h1><div class="grid">{"".join(cards)}</div></main>"""
    home_label = "الرئيسية" if lang == "ar" else "Home"
    seasons_label = "المواسم" if lang == "ar" else "Seasons"
    list_items = [
        (
            (s["name_ar"] if lang == "ar" else s["name_en"]),
            page_url(lang, "seasons", s["slug"]),
        )
        for s in ordered
    ]
    jsonld = [
        breadcrumb_jsonld(
            [
                (home_label, page_url(lang)),
                (seasons_label, page_url(lang, "seasons")),
            ]
        ),
        collection_page_jsonld(lang, title, desc, canon, list_items),
    ]
    write(out_dir / "seasons" / "index.html", wrap_page(lang, depth, title, desc, canon, body, jsonld))


def static_content(page: str, lang: str) -> tuple[str, str, str]:
    mail = CONTACT_EMAIL
    if page == "about":
        if lang == "ar":
            return (
                f"من نحن | {SITE_NAME_AR}",
                "موقع أكواد خصم يركز على المتسوقين في السعودية ثم دول الخليج.",
                f"""<h1>من نحن</h1>
<p><strong>{SITE_NAME_AR}</strong> موقع مستقل لتجميع أكواد الخصم والكوبونات، موجّه أولاً للمتسوقين في السعودية، ثم باقي دول الخليج، وللمسوقين اللي يدورون مصادر موثوقة للكوبونات.</p>
<p>ما نبيع منتجات — نساعدكم توصلون لكود خصم وتستخدمونه عند المتجر مباشرة.</p>
<p>المحتوى يُدار يدوياً: نضيف المتاجر والأكواد بعد مراجعتها. شوف صفحة <a href="../how-we-verify/">كيف نتحقق من الأكواد</a>.</p>
<p>للمتاجر والشركاء: <a href="../partners/">باقات الشراكة</a> أو <a href="../contact/">تواصل معنا</a>.</p>""",
            )
        return (
            f"About | {SITE_NAME_EN}",
            "An independent coupon site focused on Saudi shoppers, then the GCC.",
            f"""<h1>About</h1>
<p><strong>{SITE_NAME_EN}</strong> is an independent discount-code site aimed first at shoppers in Saudi Arabia, then the wider GCC, and at marketers looking for reliable coupon sources.</p>
<p>We do not sell products — we help you find a code and use it at the store.</p>
<p>Content is managed manually. See <a href="../how-we-verify/">how we verify codes</a>.</p>
<p>For stores and partners: <a href="../partners/">partnership packages</a> or <a href="../contact/">contact us</a>.</p>""",
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
                "سياسة الخصوصية وملفات تعريف الارتباط لموقع أكواد الخصم.",
                f"""<h1>الخصوصية وملفات تعريف الارتباط</h1>
<p>الموقع صفحات ثابتة. ما نطلب إنشاء حساب للتصفح، وما نبيع بياناتك.</p>
<h2>ملفات تعريف الارتباط (Cookies)</h2>
<p>قد يستخدم المتصفح تخزيناً محلياً بسيطاً لوظائف الصفحة (مثل نسخ الكود). حالياً ما نضع ملفات تعريف ارتباط تتبّع أو إعلانات طرف ثالث.</p>
<p>لو أُضيف لاحقاً تحليلات أو أدوات قياس، سنوضّح أنواع الكوكيز والغرض منها هنا قبل التفعيل.</p>
<h2>روابط العمولة</h2>
<p>قد تُستخدم روابط عمولة؛ عند الضغط عليها تنتقل لمتجر خارجي بسياسته الخاصة لجمع البيانات. راجع أيضاً <a href="../affiliate-disclosure/">الإفصاح عن العمولات</a> و<a href="../terms/">الشروط</a>.</p>
<h2>التواصل</h2>
<p>للاستفسارات: <a href="mailto:{mail}">{mail}</a> — أو صفحة <a href="../contact/">تواصل</a>.</p>""",
            )
        return (
            f"Privacy | {SITE_NAME_EN}",
            "Privacy and cookies policy for the coupon site.",
            f"""<h1>Privacy & cookies</h1>
<p>This site is static. You do not need an account to browse, and we do not sell your data.</p>
<h2>Cookies</h2>
<p>Your browser may use simple local storage for page features (for example copying a code). We do not currently set tracking or third-party advertising cookies.</p>
<p>If analytics or measurement tools are added later, we will disclose cookie types and purposes here before enabling them.</p>
<h2>Affiliate links</h2>
<p>We may use affiliate links; clicking them takes you to a third-party store with its own data policy. See also our <a href="../affiliate-disclosure/">affiliate disclosure</a> and <a href="../terms/">terms</a>.</p>
<h2>Contact</h2>
<p>Questions: <a href="mailto:{mail}">{mail}</a> — or the <a href="../contact/">contact</a> page.</p>""",
        )
    if page == "affiliate-disclosure":
        if lang == "ar":
            return (
                f"الإفصاح عن العمولات | {SITE_NAME_AR}",
                "إفصاح عن روابط التسويق بالعمولة في موقع أكواد الخصم.",
                """<h1>الإفصاح عن العمولات</h1>
<p>بعض الروابط في هذا الموقع روابط تسويق بالعمولة. إذا اشتريت عبرها، قد نحصل على عمولة بدون ما تدفع زيادة.</p>
<p>هذا يساعدنا نغطي تشغيل الموقع. اختيار المتجر والشراء قرارك أنت.</p>
<p>ما نبالغ في وصف الخصم، وما نعرض إحصائيات وهمية.</p>
<p>للتفاصيل القانونية الأوسع شوف <a href="../terms/">الشروط</a> و<a href="../privacy/">الخصوصية</a>.</p>""",
            )
        return (
            f"Affiliate disclosure | {SITE_NAME_EN}",
            "Affiliate link disclosure for the coupon site.",
            """<h1>Affiliate disclosure</h1>
<p>Some links on this site are affiliate links. If you buy through them, we may earn a commission at no extra cost to you.</p>
<p>That helps keep the site running. Choosing a store and buying is your decision.</p>
<p>We do not invent fake savings stats.</p>
<p>For broader legal detail see our <a href="../terms/">terms</a> and <a href="../privacy/">privacy</a> pages.</p>""",
        )
    if page == "marketers":
        if lang == "ar":
            return (
                f"للمسوقين | {SITE_NAME_AR}",
                "صفحة للمسوقين بالعمولة والناشرين المهتمين بأكواد الخصم في السعودية والخليج.",
                f"""<h1>للمسوقين والناشرين</h1>
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
<p>لإضافة متجر، عرض كود حصري، أو باقات الإعلان: راجع <a href="../partners/">شركاء وإعلان</a> أو راسلنا على <a href="mailto:{mail}">{mail}</a> عبر صفحة <a href="../contact/">تواصل</a>.</p>
<p class="muted">ملاحظة: القائمة أعلاه أسماء شبكات معروفة وليست إعلان مدفوع.</p>""",
            )
        return (
            f"For marketers | {SITE_NAME_EN}",
            "For affiliate marketers and publishers interested in GCC discount codes.",
            f"""<h1>For marketers & publishers</h1>
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
<p>To add a store, offer an exclusive code, or discuss advertising packages: see <a href="../partners/">Partners &amp; advertise</a> or email <a href="mailto:{mail}">{mail}</a> via the <a href="../contact/">contact</a> page.</p>
<p class="muted">Network names above are well-known options, not paid placements.</p>""",
        )
    if page == "partners":
        if lang == "ar":
            return (
                f"شركاء وإعلان | {SITE_NAME_AR}",
                "باقات الشراكة والإعلان للمتاجر والعلامات: تميّز، كود حصري، بانر — تواصل للتسعير.",
                f"""<h1>شركاء وإعلان</h1>
<p>نستقبل طلبات المتاجر والعلامات اللي تبي تظهر لجمهور مهتم بأكواد الخصم في السعودية والخليج. التواصل عبر البريد فقط: <a href="mailto:{mail}">{mail}</a>.</p>
<h2>الباقات</h2>
<div class="packages">
<article class="package-card">
<h3>تميّز المتجر (Featured)</h3>
<p>إبراز متجرك في الصفحة الرئيسية وصفحات التصنيف ذات الصلة، مع وصف واضح وروابط تسوّق.</p>
<p class="package-price"><a href="../contact/">تواصل للتسعير</a></p>
</article>
<article class="package-card">
<h3>كود حصري (Exclusive code)</h3>
<p>نشر كود خاص بالموقع مع تمييز واضح وتاريخ تحقق، مناسب للحملات الموسمية أو الإطلاقات.</p>
<p class="package-price"><a href="../contact/">تواصل للتسعير</a></p>
</article>
<article class="package-card">
<h3>بانر (Banner)</h3>
<p>مساحة بانر تحريرية على صفحات مختارة (رئيسية / مواسم / تصنيفات) حسب الاتفاق.</p>
<p class="package-price"><a href="../contact/">تواصل للتسعير</a></p>
</article>
</div>
<h2>الوسائط (Media kit)</h2>
<ul>
<li>الجمهور المستهدف: متسوقون في السعودية أولاً، ثم دول الخليج.</li>
<li>اللغات: عربي (لهجة سعودية واضحة) + إنجليزي.</li>
<li>المحتوى: صفحات متاجر، تصنيفات، دول، ومواسم (الجمعة البيضاء، رمضان، وغيرها).</li>
<li>الشكل: موقع ثابت سريع، مناسب للجوال، مع بيانات منظمة لمحركات البحث.</li>
<li>ما نقدّم أرقاماً وهمية عن الزيارات أو نسب التحويل — نشارك تفاصيل حقيقية عند الحاجة بعد التواصل.</li>
</ul>
<p><a class="btn" href="../contact/">تواصل معنا</a> <a class="btn btn-secondary" href="../marketers/">صفحة المسوقين</a></p>""",
            )
        return (
            f"Partners & advertise | {SITE_NAME_EN}",
            "Partnership and advertising packages for stores and brands — contact for pricing.",
            f"""<h1>Partners &amp; advertise</h1>
<p>We welcome stores and brands that want to reach shoppers looking for discount codes in Saudi Arabia and the GCC. Email only: <a href="mailto:{mail}">{mail}</a>.</p>
<h2>Packages</h2>
<div class="packages">
<article class="package-card">
<h3>Featured store</h3>
<p>Highlight your store on the home page and relevant category pages, with a clear description and shopping links.</p>
<p class="package-price"><a href="../contact/">Contact for pricing</a></p>
</article>
<article class="package-card">
<h3>Exclusive code</h3>
<p>Publish a site-exclusive code with clear labeling and a verified date — useful for seasonal campaigns or launches.</p>
<p class="package-price"><a href="../contact/">Contact for pricing</a></p>
</article>
<article class="package-card">
<h3>Banner</h3>
<p>Editorial banner placements on selected pages (home / seasons / categories) by agreement.</p>
<p class="package-price"><a href="../contact/">Contact for pricing</a></p>
</article>
</div>
<h2>Media kit</h2>
<ul>
<li>Audience focus: shoppers in Saudi Arabia first, then the wider GCC.</li>
<li>Languages: Arabic (clear Saudi tone) + English.</li>
<li>Inventory: store, category, country, and seasonal pages (White Friday, Ramadan, and more).</li>
<li>Format: fast static site, mobile-friendly, with structured data for search.</li>
<li>We do not publish invented traffic or conversion figures — real details can be shared after you reach out.</li>
</ul>
<p><a class="btn" href="../contact/">Contact us</a> <a class="btn btn-secondary" href="../marketers/">Marketers page</a></p>""",
        )
    if page == "contact":
        if lang == "ar":
            return (
                f"تواصل | {SITE_NAME_AR}",
                "تواصل مع يحيى كوبونات للشراكات والإعلان وأكواد الخصم.",
                f"""<h1>تواصل معنا</h1>
<p>للاستفسارات عن الشراكة، الإعلان، أو إضافة متجر/كود:</p>
<p><a class="btn" href="mailto:{mail}">{mail}</a></p>
<ul>
<li>اذكر اسم المتجر أو العلامة.</li>
<li>وضّح نوع الطلب: تميّز / كود حصري / بانر / غير ذلك.</li>
<li>أرفق أي تفاصيل مفيدة عن الحملة أو الفترة المطلوبة.</li>
</ul>
<p>نراجع الرسائل يدوياً ونرد في أقرب فرصة. شوف أيضاً <a href="../partners/">باقات الشراكة</a> و<a href="../marketers/">صفحة المسوقين</a>.</p>
<p class="muted">التواصل حالياً عبر البريد الإلكتروني فقط.</p>""",
            )
        return (
            f"Contact | {SITE_NAME_EN}",
            "Contact ye7ia Coupons for partnerships, advertising, and discount codes.",
            f"""<h1>Contact us</h1>
<p>For partnership, advertising, or adding a store/code:</p>
<p><a class="btn" href="mailto:{mail}">{mail}</a></p>
<ul>
<li>Include the store or brand name.</li>
<li>Say what you need: Featured / Exclusive code / Banner / other.</li>
<li>Add any useful campaign or timing details.</li>
</ul>
<p>We review messages manually and reply as soon as we can. See also <a href="../partners/">partnership packages</a> and the <a href="../marketers/">marketers</a> page.</p>
<p class="muted">Contact is by email only for now.</p>""",
        )
    if page == "terms":
        if lang == "ar":
            return (
                f"الشروط | {SITE_NAME_AR}",
                "شروط الاستخدام: صلاحية الأكواد، العمولات، وملفات تعريف الارتباط.",
                f"""<h1>الشروط</h1>
<p>باستخدامك موقع <strong>ye7ia.is-a.si</strong> فأنت توافق على هذه الشروط. الموقع يقدّم معلومات عن أكواد خصم بشكل مستقل ولا يبيع المنتجات مباشرة.</p>
<h2>صلاحية الأكواد</h2>
<p>نراجع الأكواد قدر الإمكان ونحدّث تواريخ التحقق، لكن ما نضمن إن كل كود يشتغل لكل مستخدم في كل وقت. الشروط تختلف حسب السلة، الدولة، الحساب، والعروض لدى المتجر. قرار الشراء واستخدام الكود مسؤوليتك.</p>
<h2>الإفصاح عن العمولات</h2>
<p>بعض الروابط روابط تسويق بالعمولة؛ قد نحصل على عمولة إذا اشتريت عبرها بدون تكلفة إضافية عليك. التفاصيل في <a href="../affiliate-disclosure/">الإفصاح عن العمولات</a>.</p>
<h2>ملفات تعريف الارتباط</h2>
<p>راجع <a href="../privacy/">سياسة الخصوصية وملفات تعريف الارتباط</a> لمعرفة ما نستخدمه حالياً وما سنفصح عنه إذا أُضيفت أدوات قياس لاحقاً.</p>
<h2>المحتوى والملكية</h2>
<p>أسماء المتاجر والعلامات ملك لأصحابها. المحتوى التحريري على الموقع لنا ما لم يُذكر غير ذلك. يُمنع نسخ المحتوى بشكل مضلّل أو إعادة نشر أكواد حصرية دون إذن.</p>
<h2>إخلاء المسؤولية</h2>
<p>الموقع يُقدَّم «كما هو». لا نتحمّل مسؤولية أخطاء العرض، انتهاء العروض، أو سياسات المتاجر الخارجية.</p>
<h2>التواصل</h2>
<p><a href="mailto:{mail}">{mail}</a> — <a href="../contact/">صفحة التواصل</a>.</p>""",
            )
        return (
            f"Terms | {SITE_NAME_EN}",
            "Terms of use: code validity, commissions, and cookies.",
            f"""<h1>Terms</h1>
<p>By using <strong>ye7ia.is-a.si</strong> you agree to these terms. The site provides independent discount-code information and does not sell products directly.</p>
<h2>Code validity</h2>
<p>We review codes where possible and update verification dates, but we do not guarantee that every code will work for every shopper at every time. Terms vary by cart, country, account, and the merchant’s own offers. Purchasing and using a code is your responsibility.</p>
<h2>Commission disclosure</h2>
<p>Some links are affiliate links; we may earn a commission if you buy through them, at no extra cost to you. See the <a href="../affiliate-disclosure/">affiliate disclosure</a>.</p>
<h2>Cookies</h2>
<p>See our <a href="../privacy/">privacy &amp; cookies policy</a> for what we use today and what we will disclose if measurement tools are added later.</p>
<h2>Content &amp; ownership</h2>
<p>Store and brand names belong to their owners. Editorial content on this site is ours unless stated otherwise. Do not copy content misleadingly or republish exclusive codes without permission.</p>
<h2>Disclaimer</h2>
<p>The site is provided “as is”. We are not liable for display errors, expired offers, or third-party store policies.</p>
<h2>Contact</h2>
<p><a href="mailto:{mail}">{mail}</a> — <a href="../contact/">contact page</a>.</p>""",
        )
    raise ValueError(page)



def build_static_page(lang: str, page: str, out_dir: Path, depth: int) -> None:
    title, desc, inner = static_content(page, lang)
    loc = lang_prefix(depth)
    short = title.split("|")[0].strip()
    if lang == "ar":
        canon = f"/{page}/"
        bc = render_breadcrumbs([("الرئيسية", f"{loc}index.html"), (short, None)])
        home_label = "الرئيسية"
    else:
        canon = f"/en/{page}/"
        bc = render_breadcrumbs([("Home", f"{loc}index.html"), (short, None)])
        home_label = "Home"
    body = f"""{bc}<main id="main" class="container"><article class="prose">{inner}</article></main>"""
    jsonld: list[dict] = [
        breadcrumb_jsonld(
            [
                (home_label, page_url(lang)),
                (short, DOMAIN + canon),
            ]
        )
    ]
    if page in ("partners", "contact"):
        jsonld.append(contactpage_jsonld(lang, title, desc, canon))
        jsonld.append(org_contactpoint_jsonld(lang))
    write(out_dir / page / "index.html", wrap_page(lang, depth, title, desc, canon, body, jsonld))


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
    # Browsers request /favicon.ico at site root
    ico_src = ASSETS_SRC / "favicon.ico"
    if ico_src.is_file():
        shutil.copy2(ico_src, out_dir / "favicon.ico")
        print("  copied /favicon.ico")


def build_redirects(out_dir: Path) -> None:
    """/brands/ and /advertise/ → /partners/ (AR + EN), meta refresh + canonical."""
    targets = (
        (out_dir / "brands", "/partners/", "ar", "شركاء وإعلان"),
        (out_dir / "advertise", "/partners/", "ar", "شركاء وإعلان"),
        (out_dir / "en" / "brands", "/en/partners/", "en", "Partners & advertise"),
        (out_dir / "en" / "advertise", "/en/partners/", "en", "Partners & advertise"),
    )
    for dest_dir, target_path, lang, label in targets:
        ensure_dir(dest_dir)
        canon = DOMAIN + target_path
        html_lang = "ar" if lang == "ar" else "en"
        dir_attr = "rtl" if lang == "ar" else "ltr"
        msg = "جاري التحويل…" if lang == "ar" else "Redirecting…"
        content = f"""<!DOCTYPE html>
<html lang="{html_lang}" dir="{dir_attr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(msg)} | {esc(label)}</title>
<meta http-equiv="refresh" content="0;url={esc(target_path)}">
<link rel="canonical" href="{esc(canon)}">
<meta name="robots" content="noindex, follow">
</head>
<body>
<p><a href="{esc(target_path)}">{esc(label)}</a></p>
</body>
</html>
"""
        write(dest_dir / "index.html", content)


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
        build_season(lang, s, visible, categories, out_dir, item_depth)
    for p in STATIC_PAGES:
        build_static_page(lang, p, out_dir, list_depth)


def clean_generated(out_dir: Path) -> None:
    for name in (
        "stores", "categories", "countries", "seasons", "en",
        "about", "how-we-verify", "privacy", "affiliate-disclosure", "marketers",
        "partners", "contact", "terms", "brands", "advertise",
    ):
        p = out_dir / name
        if p.is_dir():
            shutil.rmtree(p)
            print(f"  cleaned {name}/")
    for name in ("index.html", "404.html", "robots.txt", "sitemap.xml", "CNAME", "favicon.ico"):
        p = out_dir / name
        if p.is_file():
            p.unlink()


def main() -> None:
    global SEASONS
    print("Building ye7ia coupon site…")
    stores = load_json(DATA / "coupons.json")
    categories = load_json(DATA / "categories.json")
    SEASONS = load_seasons()
    validate_stores(stores)
    out = ROOT
    clean_generated(out)
    copy_assets(out)
    build_cname(out)
    build_robots(out)
    build_404(out)
    build_lang_tree("ar", stores, categories, out)
    ensure_dir(out / "en")
    build_lang_tree("en", stores, categories, out / "en")
    build_redirects(out)
    build_sitemap(out, stores, categories)
    print("Done.")


if __name__ == "__main__":
    main()
