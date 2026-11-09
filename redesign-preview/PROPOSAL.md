# Promoaty (برومواتي) — Full Redesign Proposal · Phase 1 (for Mario's review)

Date: 9 Nov 2026 (Cairo) · Live site: https://kobon.is-a.si · Repo: ye7iaaaaa/ye7ia-site
Status: **proposal + mockups only. Nothing has been pushed to `main`, so nothing on the live site has changed.**
Mockups: branch `redesign`, folder `redesign-preview/` (index.html = home, partners.html = For Brands).
Screenshots: `/workspace/redesign-preview/shots/` (home-desktop, home-mobile, partners-desktop, partners-mobile).

---

## 0. What went wrong with the current site (honest diagnosis)

| Problem | Why it feels "patched together" |
|---|---|
| No visual identity | Generic teal, system fonts, no logo mark, no illustrations: it looks like a template. |
| Brands we have no deal with (iHerb, Namshi) | Store pages implied a relationship that doesn't exist, which hurts trust with both shoppers and brands. |
| Partners page = text + banner packages | It read like a price list, not a pitch. There's no story, process, rules, or clear CTA. |
| About page = generic paragraphs | No positioning, no principles, no "why us". |
| Home = list of empty states | "Offers coming soon" repeated with nothing that builds value while we have no offers. |

**Core strategy for the redesign:** while we have no partner brands yet, the site has to sell **the standard** (official-only offers, transparent terms, seasonal planning) and **the team** (performance marketers), not a catalogue of codes we don't have. That's honest and it's also the strongest pitch to brands.

---

## 1. Benchmark study (what the leaders do and what we copy)

> Method: fetched and screenshotted each site from the box on 9 Nov 2026 (reference shots in `/workspace/outreach/refshots/`). RetailMeNot showed a Cloudflare bot check and Cuponation.ae refused the connection, so for those two I used the page text and well-known patterns.

### 1.1 Almowafir (almowafir.com), the MENA coupon leader
- **Hero:** big rotating brand banner (e.g. "SHEIN 15%") beside a 3×3 logo grid of top stores. Category icon row (circle icons) right under the hero.
- **Coupon card:** a **terms table** (code, %, valid on, countries, min spend, max discount, expiry) on every offer. This is their single best UX pattern.
- **Trust:** physical offices (Dubai JLT + Riyadh), support emails, phone number, app-store ratings, real user reviews with dates.
- **SEO:** a very long Arabic article on the home page plus a 10+ question FAQ. They target "افضل موقع يعطيك كود خصم".
- **Retention:** app, Chrome extension ("مكتشف الأكواد"), loyalty/cashback club, AI gift-finder bot, newsletter.
- **Look:** white plus mint/teal accent, rounded cards, dense layout. Functional but busy.
- **Copy:** benefit-led MSA ("وفّر المال"), repetitive keyword stuffing.
- **Copy for us:** terms table on cards, category icon row, store info blocks (shipping, payment, returns), a strong FAQ, contact and address transparency. **Avoid:** density, keyword stuffing, "100% guaranteed" claims.

### 1.2 Yajny (yajny.com), the cashback leader in SA/EG
- Opens with a **region picker modal** (Global / Egypt / Saudi / UAE / Kuwait) with flags. Content is fully localised per country.
- Green brand, friendly rounded type, seasonal hero banners (back to school).
- Cashback explained in a 3-step "how it works" (shop, cashback confirmed, withdraw).
- **Copy for us:** a country selector that really filters (in the header, not a blocking modal), a 3-step "how it works", seasonal hero.

### 1.3 RetailMeNot (US)
- H1: "The Best Coupons, Promo Codes & Cash Back Offers". Sections: Cash Back at Stores We Love, curated **gift guide**, "What to buy in November", "3 Ways to Save" (cash back, app, extension), FAQ.
- **Labels sponsored placements as "Sponsored"**, which is good, transparent monetisation. There's also an editorial blog with "pro shopping tips".
- **Copy for us:** "Sponsored" labelling, a monthly "what to buy this month" editorial, curated gift guides for Ramadan/Eid.

### 1.4 Honey (PayPal)
- Single-message hero ("Love deals? You came to the right place"), one CTA, social proof (reviews count, members). Then "How it works" in 3 steps and a "Droplist" price-tracker feature.
- **Copy for us:** radical focus, with one promise and one CTA per section. A watchlist or "notify me" concept, for us via Telegram.

### 1.5 Cuponation (UAE/global)
- Store pages with offer list + store FAQ + "about the store"; strong category/season hubs; editorial "Spar-Tipps". (Site blocked our fetcher; pattern from known structure.)
- **Copy for us:** store page template = offers → how to use → store facts → FAQ.

### 1.6 impact.com (partnership platform, for our For Brands and About pages)
- Hero: "Find partners that **match your ambition**" (two-tone headline, accent colour on the key words), full-bleed imagery, logo strip, sticky header with "Request a demo" pill CTA.
- Sections by audience (Brands / Creators / Publishers), each with 3 bullet benefits; **big metric callouts** (400%, 90%, 1,700% ROAS); case studies; testimonials with name + title.
- Copy is confident and outcome-led ("Partner with anyone. Track everything. Pay for results.").
- **Copy for us:** the "Pay for results" framing, two-tone headlines, an audience-split layout, a case-study format **once we have real results** (no fake metrics).

### 1.7 Awin (affiliate network)
- Violet gradient hero with orange-red CTA and a **product UI mock (dashboard)** floating under the hero. Logo wall "Trusted by 30,000+ brands". Three plan cards (Access / Accelerate / Advanced). FAQ "What is affiliate marketing? Is it right for my business?"
- **Copy for us:** the illustrated dashboard visual (we draw ours in SVG), plan/model cards (CPS / CPA / Hybrid / Direct), an educational FAQ for brands new to affiliate.

### 1.8 Stripe (landing-page craft reference)
- Huge confident headline, with the second sentence in a muted colour. Animated gradient ribbon, generous whitespace, thin grid lines, a logo strip directly under the hero, a "Contact sales" + "Sign in" pair.
- **Copy for us:** typographic hierarchy (big headline, muted sub), whitespace, subtle gradients, crisp 1px borders, restrained palette with one hero colour.

### Summary of patterns we adopt
1. Two-tone, outcome-led headlines (Stripe, impact).
2. An illustrated product visual in the hero, drawn in SVG (Awin): a phone + verified offer for shoppers, and a campaign dashboard for brands.
3. A full terms table on every offer card (Almowafir).
4. Category icon row + seasonal hubs + a country selector (Almowafir, Yajny, Cuponation).
5. 3-step "how it works" (Honey, Yajny, RetailMeNot).
6. Model/plan cards + an educational FAQ for brands (Awin).
7. "Sponsored" labels + a visible commission disclosure (RetailMeNot).
8. **No fake social proof.** Every leader shows proof, but ours must be real, so until we have it we show **principles and process** instead of numbers.

---

## 2. Brand identity

**Name:** keep **برومواتي / Promoaty** on kobon.is-a.si (the domain itself means "coupon", which is good for memory).

**Positioning line:**
- AR: «عروض رسمية فقط، يديرها فريق مسوّقين محترفين.»
- EN: "Official offers only, run by professional marketers."

**Logo idea (built in the mockup as SVG):** a **coupon ticket** with side notches (die-cut), coral fill, and a white **percent sign** inside it. The two dots of the % double as the "o"s of Promoaty in the wordmark later. The wordmark is Arabic «برومواتي» in Readex Pro Bold, with a small Latin "PROMOATY" tracked caps below it. It works as a favicon (just the ticket) and as an app icon.

**Colour palette**

| Token | Hex | Use |
|---|---|---|
| Ink (primary dark) | `#0E1330` | text, dark sections, footer |
| Coral (brand) | `#FF5A36` | CTAs, logo, key highlights |
| Mint (trust) | `#14B8A6` | "verified/official" badges, success |
| Saffron (energy) | `#FFC233` | highlights, seasonal accents, underline marker |
| Violet (B2B/tech) | `#6D5BFF` | partner/brand visuals, dashboards |
| Cream (background) | `#FFF9F3` | page background (warmer and more premium than pure white) |
| Line | `#ECE6DE` | 1px borders |

Each accent has a 50-tint (`#FFF0EB`, `#E7F8F5`, `#FFF6DD`, `#EFEDFF`) for icon tiles.

**Typography (free, open-licence Google Fonts, to be self-hosted in phase 2)**
- Display: **Readex Pro** (600/700). It's a modern geometric Arabic+Latin family designed as a pair, so headlines look consistent in both scripts.
- Body: **IBM Plex Sans Arabic** (400/500/600). It's very readable and its Latin matches IBM Plex Sans for the English site.
- Scale: H1 clamp(2.2→3.9rem), H2 clamp(1.7→2.6rem), body 17px / line-height 1.7 (Arabic needs extra leading).

**Illustration style:** flat geometric vector, **inline SVG only** (no stock photos, nothing paid). Rounded shapes, soft drop shadows, the 4 accent colours on cream, and recurring motifs (ticket with notches, % coin, shopping bag, check badge, sparkles, growth curve). Every illustration is under ~5 KB and recolourable with CSS.

**Voice and tone:** Modern Standard Arabic (the site serves the Gulf and Egypt). It should be short, confident and honest: no "100% guaranteed", no fake urgency. English is the same tone, plain and outcome-led.

**UI language:** 20px card radius, 999px pills, 1px warm borders, generous spacing, max two CTAs per section, a sticky blurred header.

---

## 3. Site map (new)

```
/                         Home (shoppers)
/stores/                  All stores (only stores with real info; NO iHerb, NO Namshi)
/stores/<slug>/           Store page (offers → how to use → store facts → FAQ)
/categories/ + /<slug>/   Fashion, Beauty, Electronics, Travel, Home, Groceries & Food
/seasons/ + /<slug>/      White Friday, 11.11, Ramadan, Eid al-Fitr, Eid al-Adha, Back to School, National Days
/countries/ + /<cc>/      SA, AE, KW, QA, BH, OM, EG
/how-it-works/            How Promoaty works + the 4-step verification standard (merges /how-we-verify/)
/partners/                For Brands (single B2B page; /brands/, /advertise/, /marketers/ → 301 here)
/about/                   About the team
/contact/                 Contact (shoppers + brands, separated)
/blog/ (phase 3)          Buying guides, "what to buy this month"
/privacy/ /terms/ /affiliate-disclosure/
/en/...                   Full English mirror
```

**Removal plan for iHerb and Namshi (phase 2, on approval):**
- Delete their entries from `data/coupons.json`.
- Delete `stores/iherb/`, `stores/namshi/`, `en/stores/iherb/`, `en/stores/namshi/`.
- Remove every mention in the home, stores index, the fashion and beauty category pages, and all 7 AR + 7 EN country pages. That's 28 files today including the data file and sitemap, all regenerated by `build.py`.
- Remove the 4 URLs from `sitemap.xml`.
- Old URLs should return the 404 page (a "no relationship" store shouldn't redirect), or we can add a meta-refresh to /stores/ if you prefer.

**Partner rule (hard):** no brand logo, name or "partner" wording anywhere until there is a signed or approved programme. Store pages only exist for stores where we have at least an approved affiliate programme.

---

## 4. Page-by-page spec (purpose · layout · copy AR + EN · visuals)

### 4.1 Home `/` (built as the hi-fi mockup)

**Purpose:** in about 5 seconds, explain what Promoaty is, why it's different (official-only), and give shoppers a reason to come back (seasons + alerts), with a clear path for brands.

| # | Section | Layout | Arabic copy | English copy | Visual |
|---|---|---|---|---|---|
| 1 | Announcement bar | Thin ink bar | منصة جديدة بمعايير صارمة: **عروض رسمية فقط**. أولى العروض الحصرية قريبًا، اشترك ليصلك كل جديد. | A new platform with strict standards: **official offers only**. Our first exclusive deals are coming soon; subscribe to hear first. | — |
| 2 | Header | Logo · nav (الرئيسية، المتاجر، الفئات، المواسم، كيف نعمل، للبراندات، من نحن) · country pill · EN · coral "شراكة معنا" | — | Home, Stores, Categories, Seasons, How it works, For Brands, About · "Partner with us" | Ticket logo |
| 3 | Hero | 2 columns: copy and search on the right, illustration on the left | Eyebrow: دليل عروض يديره فريق مسوّقين محترفين · H1: **وفّر بذكاء، بعروض رسمية فقط.** · Sub: يجمع لك برومواتي العروض التي تطلقها المتاجر نفسها في السعودية والخليج ومصر. يظهر مع كل عرض مصدره وشروطه وتاريخ آخر مراجعة، بلا أكواد وهمية ولا وقت ضائع. · Search: ابحث عن متجر أو فئة… · Chips: أزياء، جمال وعناية، إلكترونيات، سفر، مقاضي · Ticks: مصدر كل عرض واضح · تاريخ آخر مراجعة · 7 دول | Eyebrow: A deals guide run by professional marketers · H1: **Shop smart, with official offers only.** · Sub: Promoaty collects the offers stores launch themselves across Saudi Arabia, the Gulf and Egypt. Every offer shows its source, terms and last-checked date: no fake codes, no wasted time. | SVG: phone showing a −30% official offer, a "مصدر رسمي · روجع اليوم" badge, a VIP ticket, a shopping bag, a ر.س coin, sparkles |
| 4 | Promise strip | Dark rounded bar, 4 items | عروض رسمية فقط · تاريخ مراجعة ظاهر · 7 أسواق · عربي وإنجليزي | Official offers only · Visible check date · 7 markets · Arabic & English | Line icons |
| 5 | Why Promoaty | Centered heading + 3 cards | H2: ليس مجرد موقع كوبونات. **دليل تسوّق تثق به.** · Sub: تمتلئ معظم مواقع الكوبونات بأكواد منتهية. نحن نفعل العكس: عروض أقل عددًا، لكن كل عرض منها حقيقي ومشروح بالتفصيل. · Cards: **سياسة «الرسمي فقط»**: لا ننشر أي كود إلا إذا جاء من المتجر نفسه أو من برنامج شراكة رسمي. · **الشروط كاملة أمامك**: الحد الأدنى للطلب، وأقصى خصم، والدول، وتاريخ الانتهاء. · **تقويم المواسم**: نجهّز صفحة لكل موسم قبل موعده. | H2: Not just another coupon site. **A shopping guide you can trust.** · Sub: Most coupon sites are full of expired codes. We do the opposite: fewer offers, each one real and fully explained. · Cards: **"Official-only" policy** · **Every term up front** · **Season calendar** | Icon tiles in 50-tints |
| 6 | How it works | 3 illustrated steps | ١ ابحث عن متجرك · ٢ اقرأ الشروط وانسخ · ٣ اشترِ ووفّر | 1 Find your store · 2 Read the terms & copy · 3 Shop & save | 3 SVG scenes (search bar, ticket, bag with check) |
| 7 | The Promoaty standard | Left: 4-step list · right: example offer cards | H2: 4 مراحل يمرّ بها كل عرض قبل نشره · المصدر، الشروط، التجربة، المتابعة | Every offer passes 4 checks before it's published: Source, Terms, Test, Monitor | Ticket-style coupon cards with a terms row (min spend / max discount / last checked), badges "مصدر رسمي" and "متبقٍ 5 أيام", clearly labelled «مثال توضيحي» |
| 8 | Categories | 6 tiles | تسوّق حسب اهتمامك · أزياء، جمال وعناية، إلكترونيات، سفر، المنزل، البقالة والطعام | Shop by interest | Custom SVG icon per category |
| 9 | Season calendar | 4 gradient cards | استعد للموسم قبل أن يبدأ · الجمعة البيضاء (قائم الآن) · عروض 11.11 · رمضان · عيد الفطر | Get ready before the season starts | Gradient cards with big glyphs (star, 11, crescent, gift) |
| 10 | Countries | Flag pills | عروض مخصّصة لبلدك: اختر بلدك لترى العروض الصالحة فيه فقط، بعملته وطرق الشحن إليه. | Offers for your country | Flag SVGs (no emoji dependency) |
| 11 | Brand band | Dark card, copy + growth chart | لديك علامة تجارية؟ دعنا ننمّي مبيعاتك، وادفع مقابل النتائج. · CTA: اكتشف الشراكة + partners@kobon.is-a.si | Own a brand? Let us grow your sales, and pay for results. | SVG growth curve |
| 12 | Newsletter / alerts | Saffron block | اعرف العرض قبل الجميع: رسالة واحدة أسبوعيًا بأهم العروض الرسمية. | Hear about offers first: one weekly email. | — |
| 13 | FAQ | Accordion | ما هو برومواتي؟ · لماذا لا توجد عروض كثيرة بعد؟ · هل يحصل برومواتي على عمولة؟ · الكود لم يعمل، ماذا أفعل؟ | What is Promoaty? · Why aren't there many offers yet? · Does Promoaty earn commission? · A code didn't work? | — |
| 14 | Footer | 5 columns + disclosure | دليل عروض رسمية للخليج ومصر. قد نحصل على عمولة عند الشراء عبر روابطنا، دون أي تكلفة إضافية عليك. | Official deals guide for the Gulf & Egypt. We may earn a commission at no extra cost to you. | Logo |

### 4.2 For Brands `/partners/` (built as the hi-fi mockup)

**Purpose:** convince a brand or affiliate manager in under a minute that we're a serious, brand-safe performance team, and get them to book a call or send the form. **No logos and no fake numbers.**

| # | Section | Arabic copy | English copy | Visual |
|---|---|---|---|---|
| 1 | Hero (dark, violet/coral glow) | Eyebrow: للبراندات والمتاجر الإلكترونية · H1: **نحوّل عروضك إلى مبيعات، وتدفع مقابل النتائج.** · Sub: برومواتي فريق متخصص في التسويق بالأداء والعمولة، ومنصة عروض موجّهة للمتسوقين في الخليج ومصر. نبني لعلامتك حضورًا موثوقًا ونقيس كل ريال يُنفق. · CTAs: احجز مكالمة تعارف / ملف الشراكة (PDF) · Facts: الدفع على النتيجة (CPS · CPA · هجين) · 7 أسواق · بلغتين | Eyebrow: For brands & online stores · H1: **We turn your offers into sales, and you pay for results.** · Sub: Promoaty is a performance & affiliate marketing team and a deals platform for shoppers in the Gulf and Egypt. We build a trusted presence for your brand and measure every riyal spent. · CTAs: Book an intro call / Partnership deck (PDF) | SVG campaign dashboard ("Campaign · White Friday", attributed-sales curve), "channels" card, "brand-safe, official codes only" badge |
| 2 | Founding Partners | **برنامج الشركاء المؤسسين**: نختار عددًا محدودًا من العلامات التجارية لتكون أول شركائنا: ظهور مميز على الصفحة الرئيسية وصفحات المواسم، وخطة حملة مخصّصة، وتقارير أسبوعية مباشرة من الفريق. · CTA: قدّم علامتك | **Founding Partner Programme**: a limited number of brands get premium placement on the home and season pages, a custom campaign plan and weekly reports straight from the team. | Gold star seal |
| 3 | What we offer (6 services) | منظومة تسويق بالأداء متكاملة: منصة العروض · محتوى وسيو · قنوات التواصل (تيليجرام، إكس، النشرة) · صنّاع المحتوى · حملات المواسم · تقارير شفافة, each with 3 ✓ bullets | A complete performance-marketing system: Deals platform · Content & SEO (incl. showing up in AI answers) · Owned channels · Creators · Seasonal campaigns · Transparent reporting | Icon tiles |
| 4 | Collaboration models | اختر النموذج الذي يناسب أهدافك: **CPS** عمولة على المبيعات (الأنسب) · **CPA** تكلفة لكل إجراء · **هجين** رسوم ظهور + عمولة · **مباشر** أو عبر شبكتك | Choose your model: CPS · CPA · Hybrid · Direct or via your network | Model cards, CPS highlighted in ink |
| 5 | Process timeline | من أول مكالمة إلى أول تقرير: مكالمة تعارف (اليوم الأول) · خطة مكتوبة (خلال 3 أيام) · الإطلاق (الأسبوع الأول) · تقرير وتحسين (كل أسبوع) | From first call to first report: Intro call → Written plan (3 days) → Launch (week 1) → Weekly report & optimise | Dashed coral timeline |
| 6 | Brand-safety rules | قواعد نلتزم بها مع كل شريك: أكوادك الرسمية فقط · لا مزايدة على اسم علامتك دون إذن · لا عدّ تنازلي وهمي · نتبع سياسات شبكتك · تقارير من مصدر التتبع نفسه · مراجعة المحتوى قبل نشره عند الطلب | Rules we keep with every partner: official codes only · no brand-term bidding without written permission · no fake urgency · we follow your network's policies · reports from the tracking source itself · content review on request | ✓ rule tiles |
| 7 | Contact + FAQ | أخبرنا عن علامتك، ونعود إليك خلال يوم عمل. · Form: الاسم، العلامة التجارية، البريد الإلكتروني للعمل، الموقع، الأسواق المستهدفة، النموذج المفضّل، الهدف · FAQ: هل هناك تكلفة لبدء الشراكة؟ / هل تعملون عبر شبكات التسويق بالعمولة؟ | Tell us about your brand; we reply within one business day. | Dark section, white form card |

*The form is static in the mockup. In phase 2 it can post to a free form backend (e.g. a mailto fallback, or Formspree's free tier) or link to email, pending your choice. partners@kobon.is-a.si only works once the Zoho mailbox and DNS records are done.*

### 4.3 About `/about/` (copy ready, to be built in phase 2)

**Purpose:** show who we are and what we stand for. It's for brands doing due diligence and for shoppers asking "is this legit?".

Layout: hero, then the story, then 4 principles, then "how we work" (team skills), then numbers (only real ones, hidden until we have them), then a CTA.

- **Hero.** AR: «نحن فريق من المسوّقين، بنينا برومواتي لأننا تعبنا من الأكواد الوهمية.» EN: "We're a team of marketers. We built Promoaty because we were tired of fake codes."
- **Story.** AR: «عملنا لسنوات في التسويق بالأداء والعمولة مع متاجر إلكترونية في الخليج ومصر، ورأينا المشكلة من الجهتين: متسوّق يضيع وقته في أكواد لا تعمل، وعلامات تجارية تخسر ثقة عملائها بسبب مواقع تنشر أي شيء. برومواتي هو الحل الذي أردناه: منصة عروض بمعيار واضح، يديرها فريق يعرف كيف تُبنى الحملات وتُقاس.»
  EN: "We spent years in performance and affiliate marketing with online stores across the Gulf and Egypt, and saw the problem from both sides: shoppers wasting time on codes that don't work, and brands losing customer trust to sites that publish anything. Promoaty is the answer we wanted: a deals platform with a clear standard, run by a team that knows how campaigns are built and measured."
  *(Mario: please confirm the team's real experience and years so the copy is accurate.)*
- **Principles (4 cards with icons):**
  - الرسمي فقط / Official only
  - الشفافية في العمولة / Transparent about commission
  - احترام وقتك / Respect your time
  - سلامة العلامة التجارية / Brand safety
- **How we work (skills grid):**
  - التسويق بالعمولة / Affiliate
  - السيو والمحتوى العربي / SEO & Arabic content
  - إدارة القنوات / Channels
  - تحليل الأداء / Analytics
  - إدارة حملات المواسم / Seasonal campaign management
- **Visual:** an abstract SVG "team table" scene (laptops, a chart, a coupon), with no faces, so no stock people.
- **CTA band:** للبراندات: لنعمل معًا / للمتسوقين: اشترك في التنبيهات.

### 4.4 How it works `/how-it-works/` (copy ready)

**Purpose:** explain the user journey and the verification standard (this merges the current /how-we-verify/).

Sections:
1. The 3-step journey (same as on the home page, but bigger).
2. "معيار برومواتي": the 4 stages in detail, each with an example.
3. How to read an offer card: an annotated SVG of the ticket with arrows to the source, terms, last check and expiry.
4. How we earn money (disclosure). AR: «عندما تشتري عبر روابطنا قد يدفع لنا المتجر عمولة. لا يغيّر ذلك سعرك، ولا يؤثر على ترتيب العروض إلا في الأماكن المعلَّمة بكلمة "مُموَّل".» EN: "When you buy through our links the store may pay us a commission. It never changes your price, and it never affects ranking except in spots labelled 'Sponsored'."
5. Report a broken code (CTA).

### 4.5 Contact `/contact/` (copy ready)

**Purpose:** two clear paths, so brand leads don't get lost among shopper questions.

- Two big cards:
  - للمتسوقين: «سؤال عن عرض أو كود لا يعمل؟» with a short form or email.
  - للبراندات والوكالات: «شراكة أو حملة؟» linking to /partners/#contact and partners@.
- Response time: «نرد خلال يوم عمل».
- Social/Telegram channel links once they exist.
- Visual: an SVG envelope + ticket.

---

## 5. SEO and performance

- **Keep what works:** static HTML from `build.py`, canonical + hreflang (ar-SA / en / x-default), sitemap, JSON-LD (Organization, WebSite+SearchAction, BreadcrumbList, FAQPage). Old ye7ia.is-a.si redirects stay untouched.
- **Fonts:** self-host Readex Pro + IBM Plex Sans Arabic as **WOFF2 subsets** (Arabic + Basic Latin, 2–3 weights). Use `font-display:swap` and preload one weight. Target under 120 KB of fonts total. The mockup uses Google Fonts only for the preview.
- **Images:** all illustrations are inline SVG (zero requests). OG images are generated per page as PNG from SVG templates (store, season, partners).
- **Budget:** under 60 KB of HTML+CSS per page (gzip), **no JS framework**, and under 3 KB of JS for the accordion, copy-code and country filter. Targets: LCP under 1.5 s on 4G, CLS ≈ 0, Lighthouse 95+.
- **Content SEO:**
  - Season hubs published 4–6 weeks early (Ramadan 2027, White Friday 2027).
  - Category guides («دليل شراء…»).
  - A monthly «ماذا تشتري في <شهر>» post.
  - FAQs per page.
  - No keyword stuffing.
  - Titles follow «كود خصم <متجر> <شهر سنة>» only on store pages where we really have codes.
- **E-E-A-T:** a real About page, the disclosure page, the verification standard, last-checked dates, and a named contact. Brands and Google both read these.
- **AI-answer visibility (2026):** clean FAQ schema, concise factual blocks per store (shipping, returns, payment), and llms.txt/robots allowing major AI crawlers. impact.com highlights this as the new battleground.
- **Accessibility:** contrast AA, focus states, `lang`/`dir` set per page, real `<button>`s, `prefers-reduced-motion`.
- **Analytics (free, privacy-friendly):** Cloudflare Web Analytics or GoatCounter, so we get real traffic numbers to show brands. This needs your OK.

---

## 6. Bold ideas (for your review; none are built or committed)

1. **"Official Only" seal + public standard.** A visible ✓ مصدر رسمي badge, and a public page that explains the 4-step check. This makes our weakness (few offers) into our brand.
2. **Founding Partner Programme.** The first ~10 brands get premium placement, a custom plan and weekly reports. It creates urgency for brands without needing fake stats. *(Terms need your approval.)*
3. **Season Radar.** A live countdown calendar for White Friday, 11.11, Ramadan, Eid and national days per country, plus "remind me" via Telegram/email. It captures traffic before the season.
4. **Telegram deals channel + bot alerts.** "Notify me when <store> has an official offer." This is our Honey-Droplist equivalent at zero cost, and channel size is also a proof metric for affiliate networks (ArabClicks requires 500 Telegram subs for approval-gated offers).
5. **Store "fact cards".** Shipping, returns, payment methods (Tabby/Tamara/COD) and delivery time per country. This is useful even when there's no code, and it's great for SEO and AI answers.
6. **Partnership deck page + PDF.** A beautiful one-pager deck generated from the same HTML (print CSS) that we attach in outreach emails, so brands see a pro media kit.
7. **"Code didn't work?" button with a public fix log.** Shows a "last fixed" timestamp per store. It builds trust and it's something competitors hide.
8. **Monthly Arabic shopping report.** «ماذا تشتري في ديسمبر» / Ramadan buying guide. It gives us PR and backlink bait, and content partners can share it.
9. **Creator kit.** A /creators/ page later: micro-influencers in the Gulf get their own tracked code via Promoaty. This positions us as a mini-network (the impact.com model, local).
10. **Bilingual mirrored design with a country switcher in the header.** Prices are shown in the local currency, and filters are remembered (localStorage), like Yajny but without a blocking modal.

---

## 7. Phase 2 plan (after your approval)

1. Apply the design system to `build.py` templates: a new `assets/style.css`, a header/footer partial, and an SVG sprite. All pages are regenerated, AR + EN.
2. Remove iHerb & Namshi completely (section 3).
3. Build the About, How it works and Contact pages per section 4, then the store, category, season and country templates in the new style.
4. Self-host fonts, write per-page OG images, and run a Lighthouse check.
5. Preview on the `redesign` branch, then merge to `main` only after your OK. Only that merge changes the live site.

**Open questions for Mario**
- Team facts for the About page: years of experience, past results we're allowed to mention?
- Approve the Founding Partner Programme wording?
- Contact form backend: email link only, or a free form service?
- Keep the Arabic name «برومواتي», or switch the display name to match the domain (e.g. «كوبون»)?
