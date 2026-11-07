# Onboarding: add the first real stores

Checklist for replacing example data with real GCC/Saudi stores. Examples stay in `coupons.json` with `"example": true` and stay hidden from public pages. The template defaults to `"example": true`.

## Required store fields (non-example)

| Field | Notes |
|-------|--------|
| `slug` | URL slug, unique, lowercase kebab-case |
| `name_ar` | Arabic display name |
| `name_en` | English display name |
| `category` | Must match a slug in `categories.json` |
| `countries` | Array of country slugs (`sa`, `ae`, `kw`, `qa`, `bh`, `om`) |
| `description_ar` | Short Arabic description |
| `description_en` | Short English description |
| `example` | Must be `false` or omitted for real stores |

Optional store fields: `website` (`https://…`), `affiliate_url` (`https://…`), `faq`.

## Required coupon fields (non-example)

| Field | Notes |
|-------|--------|
| `code` | Real coupon code — never invent; placeholders like `REALCODE` fail the build |
| `title_ar` | Arabic offer title |
| `title_en` | English offer title |
| `verified_date` | ISO date `YYYY-MM-DD` when last checked |
| `expires` | ISO date `YYYY-MM-DD` |
| `affiliate_url` | Tracking / checkout URL — must be `https://…` (not `example.com`) |

Optional coupon fields: `discount`, `exclusive` (boolean), `source_url` (`https://…` page where the code was verified, separate from `affiliate_url`).

## Steps

1. Copy `store-template.json` into `coupons.json` as a new array item (or edit a copy).
2. Fill every required field from the store’s official page / affiliate program. Do **not** invent codes, discounts, or stats.
3. Replace every `example.com` / `REALCODE` placeholder. Set `"example": false` (or remove `example`) on the store; omit `example` on real coupons.
4. Keep existing example stores with `"example": true` until you intentionally remove them.
5. Run `python3 build.py` — the build **fails** if any non-example store/coupon is missing required fields, uses non-`https` URLs, non-ISO dates, or placeholder values.
6. Spot-check the store page in AR + EN, then commit.

## Season windows

Live season chips/banners (e.g. White Friday) are controlled in `data/seasons.json` via `start` / `end` (ISO dates; end is exclusive). Build-time chips still respect those dates; the browser also hides chips/banners client-side after `end` without a rebuild.
