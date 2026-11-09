2026-11-07 04:10 Cairo — Validation hardening: _is_https_url via urllib.parse (https + non-empty hostname); _is_iso_date requires full ^\d{4}-\d{2}-\d{2}$ match before fromisoformat.
2026-11-07 03:00 Cairo — Batch 6: season related-categories a11y/list markup + chip/banner aria when client-hidden; category/country empty states with browse + partners CTAs (no coming-soon copy).
2026-11-07 02:10 Cairo — Batch 5: client-side season chip/banner hide via data-season-start/end; store no-results inside #store-grid; stricter build validation (https + ISO dates + reject REALCODE/example.com; optional source_url); template defaults example:true; season pages CollectionPage+ItemList of real category URLs + related category deep-links (no invented deals).
2026-11-07 01:10 Cairo — Batch 4: White Friday live chip/banner (data/seasons.json start/end auto-hide); store onboarding pack (store-template.json + ONBOARDING.md) + build validation for non-example coupons; stores #store-grid always present for ?q= empty state; home Organization ContactPoint email.
2026-11-07 00:15 Cairo — Batch 3: lightweight cookie consent; WCAG polish (footer headings, focus styles, reduced-motion); WebPage/Breadcrumb schema across pages; ContactPage+Organization ContactPoint on partners/contact; /favicon.ico at root; stores ?q= client filter (keeps SearchAction); Qatar/Bahrain/Oman country pages; /brands/+/advertise/ → /partners/ redirects; data/affiliate-programs.md from public official join requirements only.
# Changelog

## 2026-11-09 — Re-audit follow-ups
- /stores/ and /en/stores/ set to noindex (while no stores are listed) and removed from sitemap.
- Dubai AED 1,000 customs exemption checked against Customs Notice 16/2026 (effective 03/08/2026 confirmed); wording now notes it applies via e-commerce companies registered with Dubai Customs.

## 2026-11-09 — Audit fixes (indexing, a11y, facts, guides, analytics)
- Indexing: empty category/country/season pages and hubs set to noindex,follow and removed from sitemap; /countries/global/ kept indexed with sourced KSA/UAE threshold content.
- Accessibility: CTA coral #C93A17, darker muted/mint/label colours, 12px minimum, no heading-level gaps (footer h2, sr-only hub headings).
- Facts: "Gulf, Egypt & global" wording; plan-ahead season labels driven by start/end dates (app.js); SearchAction and Event schema removed; search boxes filter guides/stores client-side.
- Guides: /guides/ hub + 10 bilingual guides (Article + FAQPage schema, sources listed), linked from nav and home.
- Design: shorter mobile home (guides near top, sample offer cards removed); one-page bilingual /media-kit.pdf (no prices or traffic numbers) linked from /partners/.
- Meta CSP on all pages; cookieless Cloudflare Web Analytics beacon; privacy page updated. Forms remain mailto (JS-composed).

## 2026-11-09 — Copy rewrite (Gulf + global)

- Rewrote all Arabic and English copy (home, partners, about, how it works, contact, stores, categories, markets, seasons, 404, meta titles and descriptions) in concise MSA and native English, using one glossary: كوبون، كود خصم، عرض، متجر، شريك.
- Repositioned the site for the GCC (SA, AE, KW, QA, BH, OM) and international stores; added /countries/global/ and /en/countries/global/.
- Removed the Telegram/X channel claims; partner services now say email & alerts.

2026-11-09 Cairo — Full redesign and rebrand to كوبون / Kobon (matches kobon.is-a.si): new design system (coral ticket logo, Readex Pro + IBM Plex Sans Arabic self-hosted subsets), rebuilt home, For Brands (/partners/), About, How it works, Contact, legal, stores, categories, countries and seasons pages in AR + EN. iHerb and Namshi removed entirely (old URLs redirect home); no brand shown as a partner. Redirects: /brands/, /advertise/, /marketers/ → /partners/; /how-we-verify/ → /how-it-works/. Partnership and alerts forms are mailto partners@kobon.is-a.si.
2026-11-07 18:08 Cairo — Rebrand fixes: drop redundant aria-label on White Friday season chip/banner (visible text names the season; keep data-season-start/end); clarify iHerb/Namshi coupon terms on store pages (first-order + exclusions; Namshi app-only max 75 SAR/AED, min 100 AED equiv, AE/SA/KW/BH/EG phone) with official source links; confirm Namshi excluded from QA/OM country pages via store.countries filter.
2026-11-07 17:10 Cairo — Mario request: rebrand to برومواتي / Promoaty (no Yehia/ye7ia in visible text, titles, meta, schema; base URL is one DOMAIN config, CNAME unchanged until DOMAIN LIVE); compact country switcher (SA, AE, KW, QA, BH, OM, EG) + category nav under the header; Egypt country page; expires may be null when verified_date is ISO, cards show "last checked" + terms + official source link; real codes added: iHerb NEW20 and Namshi app first-order code "اولى" (official pages); new OG image.
2026-11-06 23:13 Cairo — Batch 2: Partners/Advertise, Contact, Terms pages; privacy cookies; packages without prices + media kit; business CTA on home/footer; marketers linked to real partners@ye7ia.is-a.si mailto (ImprovMX catch-all verified).
2026-11-06 23:10 Cairo — Batch 1 additions: hide example stores from home/sitemap (clean empty state; data kept); same-page language switch; favicon/apple-touch/og/twitter; contrast+skip-link+focus-visible; separate copy-code button + shop via target=_blank link; home Organization+SearchAction schema.
2026-11-06 22:04 Cairo — Related stores on store pages; Twitter/OG image + Organization schema.
