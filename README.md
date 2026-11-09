# كوبون / Kobon — kobon.is-a.si

Static, dependency-free site: Arabic (RTL) at `/`, English at `/en/`. Deployed by GitHub Pages from `main`.

## Build

```bash
python3 build.py
```

`build.py` reads `data/*.json` and regenerates every page, the redirects, `sitemap.xml`, `robots.txt`, `llms.txt` and `CNAME`.

- `data/categories.json` — categories (names, short labels, descriptions, buying tips)
- `data/seasons.json` — season calendar (static dates; Hijri dates are estimates)
- `data/coupons.json` — stores and offers. **Empty on purpose.** Only add a store after an official partner programme is approved. See `data/store-template.json` and `data/ONBOARDING.md`.

## Rules

- Official offers only. No brand name or logo is shown as a partner without a formal agreement.
- No invented numbers, testimonials or fake urgency.
- Contact: partners@kobon.is-a.si

## Design system

Tokens and components live in `assets/style.css` (ink #0E1330, coral #FF5A36, mint #14B8A6, saffron #FFC233, violet #6D5BFF, cream #FFF9F3).
Fonts are self-hosted WOFF2 subsets in `assets/fonts/` (Readex Pro, IBM Plex Sans Arabic; SIL OFL 1.1, licences included). No third-party requests.
