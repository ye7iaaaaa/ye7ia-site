# Promoaty (برومواتي) — coupon site

موقع ثابت (Static) لأكواد الخصم والكوبونات، موجّه أولاً للسعودية ثم الخليج + صفحة للمسوقين.
العربي (نبرة سعودية، RTL) على `/` والإنجليزي على `/en/`.

## التشغيل محلياً

```bash
cd coupon-site
python3 build.py
```

ما فيش أي مكتبات خارجية. السكربت بيقرأ `data/` وبيولّد HTML في جذر المشروع (جاهز لـ GitHub Pages من الـ root).

بعد البناء افتح `index.html` أو ارفع المجلد كامل على الريبو `ye7iaaaaa/ye7ia-site` وفعّل Pages من الـ root (مش docs). ملف `CNAME` فيه `ye7ia.is-a.si`.

## إضافة متجر جديد

1. افتح `data/coupons.json`.
2. انسخ عنصر متجر موجود وغيّر الحقول:

```json
{
  "slug": "my-store",
  "name_ar": "اسم المتجر",
  "name_en": "Store Name",
  "category": "fashion",
  "countries": ["sa", "ae"],
  "description_ar": "وصف قصير بالعربي…",
  "description_en": "Short English description…",
  "example": false,
  "faq": [
    {
      "q_ar": "سؤال؟",
      "a_ar": "جواب.",
      "q_en": "Question?",
      "a_en": "Answer."
    }
  ],
  "coupons": [
    {
      "code": "SAVE10",
      "title_ar": "خصم ١٠٪",
      "title_en": "10% off",
      "discount": "10%",
      "verified_date": "2026-11-06",
      "expires": "2026-12-31",
      "exclusive": false,
      "affiliate_url": "https://…",
      "example": false
    }
  ]
}
```

3. `category` لازم يكون موجود في `data/categories.json` (`fashion`, `electronics`, `beauty`, `food`, `home`, `travel` أو أضف تصنيف جديد هناك).
4. امسح `"example": true` من المتجر والأكواد قبل ما تنشر حاجة حقيقية.
5. شغّل `python3 build.py` تاني.

## إضافة كود لمتجر موجود

- داخل نفس عنصر المتجر في `coupons.json`، ضيف عنصر في مصفوفة `coupons`.
- حدّث `verified_date` لما تتأكد إن الكود شغال.
- لو الكود حصري حط `"exclusive": true`.

## إضافة تصنيف

عدّل `data/categories.json` بنفس شكل العناصر الموجودة (`slug`, `name_ar`, `name_en`, `icon`, `description_ar`, `description_en`) وبعدين `python3 build.py`.

## الصفحات اللي بتتولّد

- رئيسية، متاجر، تصنيفات، دول (`sa` / `ae` / `kw`)
- مواسم دائمة: الجمعة البيضاء، رمضان، ١١.١١، اليوم الوطني، يوم التأسيس
- للمسوقين، من نحن، كيف نتحقق، الخصوصية، الإفصاح عن العمولات، 404
- كل ده بالعربي والإنجليزي + `sitemap.xml` و `robots.txt`

## ملاحظات مهمة

- المتاجر الحالية **أمثلة تجريبية** — غيّرها قبل الإطلاق.
- ما فيش أرقام توفير وهمية في القالب.
- زر «انسخ وتسوّق» بينسخ الكود وبيفتح رابط العمولة في تاب جديد (`assets/app.js`).
- ما تعملش push من هنا لو الـ GitHub auth بايظ؛ انقل الملفات للريبو بنفسك أو بعد إصلاح التوكن.

## هيكل سريع

```
coupon-site/
  build.py
  README.md
  CNAME
  data/coupons.json
  data/categories.json
  assets/style.css
  assets/app.js
  index.html          ← بعد البناء
  en/…                ← بعد البناء
  stores/… categories/… countries/… seasons/…
```
