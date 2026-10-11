# دليل التتبع والقياس — موقع MKN ARABIA

كل زيارة وكل نقرة وكل طلب على الموقع مربوط بمصدره (UTM / الحملة الإعلانية)، ويُرسل إلى Google Analytics 4 ومنصات الإعلانات.
**الملف المسؤول:** `assets/js/tracking.js`

---

## 1) التفعيل: ضع المعرّفات

افتح `assets/js/tracking.js` واملأ `CONFIG` في أعلى الملف:

| الحقل | من أين تحصل عليه | مثال |
|---|---|---|
| `GTM_ID` | Google Tag Manager ← Container ID | `GTM-XXXXXXX` |
| `GA4_ID` | GA4 ← Admin ← Data streams ← Measurement ID | `G-XXXXXXXXXX` |
| `GOOGLE_ADS_ID` | Google Ads ← Goals ← Conversions ← Tag setup | `AW-123456789` |
| `GOOGLE_ADS_LEAD_LABEL` / `GOOGLE_ADS_WHATSAPP_LABEL` | تسمية كل تحويل في Google Ads | `AbC-D_efG` |
| `META_PIXEL_ID` | Meta Events Manager ← Data sources | `123456789012345` |
| `TIKTOK_PIXEL_ID` | TikTok Ads ← Events ← Web events | `CXXXXXXXXXXXXXXX` |

**طريقتان للعمل (اختر واحدة):**
- **مع GTM (موصى به):** ضع `GTM_ID` فقط. يدفع الموقع كل الأحداث إلى `dataLayer`، وتُضاف وسوم GA4 و Meta و TikTok و Google Ads من داخل GTM دون تعديل الكود.
- **بدون GTM:** اترك `GTM_ID` فارغًا وضع `GA4_ID` والبكسلات. يحمّلها الموقع مباشرة ويرسل لها الأحداث.

> لا يُحمَّل أي سكربت تتبع حتى تُملأ المعرّفات.

---

## 2) كيف يُحفظ مصدر الزيارة

- عند دخول الزائر برابط فيه `utm_*` أو `gclid` / `fbclid` / `ttclid`، يُحفظ المصدر على جهازه لمدة **90 يومًا**.
- **آخر تفاعل (Last touch):** آخر حملة جاء منها الزائر، ويُرسل مع كل حدث.
- **أول تفاعل (First touch):** أول مصدر عرّفه على الموقع، ويُرسل كـ `first_source / first_medium / first_campaign`.
- بدون UTM يُستنتج المصدر تلقائيًا: Google → `organic`، إنستغرام وفيسبوك → `social`، أي موقع آخر → `referral`.
- يبقى المصدر محفوظًا عند التنقل بين الصفحات، فيُنسب الطلب في صفحة التواصل إلى الحملة الأصلية.

### رسائل واتساب تحمل المصدر
كل رسالة واتساب من الموقع (الأزرار، طلبات عروض الأسعار، النموذج) تنتهي بسطر مرجعي مثل:

```
— مرجع: facebook / paid_social / ksa-leadgen-2026-11 / reel-01 · /pricing.html
```

فيعرف الفريق من أي حملة وأي إعلان وأي صفحة جاء كل عميل، حتى بدون فتح Analytics.

---

## 3) الأحداث المرسلة

كل حدث يحمل أيضًا: `utm_source, utm_medium, utm_campaign, utm_term, utm_content, gclid, fbclid, ttclid, landing_page, first_source, first_medium, first_campaign, page_path`.

| الحدث | متى يُرسل | معاملات إضافية | Meta | TikTok | Google Ads |
|---|---|---|---|---|---|
| `generate_lead` | إرسال نموذج التواصل | `department, market, budget_range, timing` | Lead | SubmitForm | تحويل الطلب |
| `quote_request` | زر "اطلب عرض سعر" لأي باقة أو حل | `package_id` (مثل `D04-GROWTH` أو `X03`)، `department` | Lead | SubmitForm | تحويل الطلب |
| `whatsapp_click` | أي نقرة على واتساب | `link_location` (header / floating_button / packages …) | Contact | Contact | تحويل واتساب |
| `email_click` | نقرة على البريد | `link_location` | Contact | Contact | — |
| `social_click` | إنستغرام / لينكدإن | `platform` | — | — | — |
| `cta_click` | أي زر أو بطاقة أخرى | `link_text, link_url, link_location` | — | — | — |
| `select_content` | فتح تبويب قسم في صفحة الباقات | `item_id` (d01–d08) | — | — | — |
| `view_case` | ظهور حالة عمل على الشاشة | `case_id` | — | — | — |
| `form_start` | أول تفاعل مع النموذج | `form_id` | — | — | — |
| `faq_open` | فتح سؤال شائع | `question` | — | — | — |
| `scroll_depth` | تمرير 25/50/75/90% | `percent_scrolled` | — | — | — |

> لا تُرسل أي بيانات شخصية (الاسم أو الهاتف أو البريد) إلى Analytics أو المنصات؛ هذه البيانات تذهب في رسالة واتساب فقط.

---

## 4) إعداد GA4 (مرة واحدة)

1. **Key events (التحويلات):** في GA4 ← Admin ← Events، علّم `generate_lead` و `quote_request` و `whatsapp_click` كـ Key events.
2. **Custom dimensions:** في Admin ← Custom definitions ← Create، أنشئ بنطاق **Event**:
   `package_id`, `department`, `link_location`, `market`, `budget_range`, `case_id`, `landing_page`, `first_source`, `first_medium`, `first_campaign`
   وبنطاق **User**: `first_source`, `first_medium`, `first_campaign`.
3. **التقارير:** المصدر والوسيط والحملة تظهر تلقائيًا في Acquisition من معاملات UTM.
4. **الربط:** اربط GA4 بـ Google Ads (Admin ← Product links) لاستيراد التحويلات.

## 5) إعداد GTM (إذا اخترته)

- **المتغيرات:** أنشئ Data Layer Variables لكل معامل في الجدول أعلاه.
- **المشغلات:** Custom Event لكل حدث (`generate_lead`، `quote_request`، `whatsapp_click`، إلخ).
- **الوسوم:** GA4 Configuration بالـ Measurement ID، ووسم GA4 Event لكل حدث مع تمرير المعاملات، ووسوم Meta Pixel و TikTok Pixel و Google Ads Conversion حسب جدول المطابقة أعلاه.

---

## 6) تسمية روابط الحملات (UTM)

استخدم الأداة الداخلية: **`/utm.html`** (غير مرتبطة بالقائمة ومحجوبة عن محركات البحث).

| المعامل | القاعدة | أمثلة |
|---|---|---|
| `utm_source` | المنصة | `facebook`، `instagram`، `google`، `tiktok`، `snapchat`، `linkedin`، `whatsapp`، `email`، `qr` |
| `utm_medium` | نوع القناة | `paid_social`، `cpc`، `display`، `paid_video`، `social`، `messaging`، `email`، `offline` |
| `utm_campaign` | السوق-الهدف-السنة-الشهر | `ksa-leadgen-2026-11`، `uae-brand-2026-12` |
| `utm_content` | الإعلان أو التصميم | `reel-01`، `carousel-pricing`، `static-offer-b` |
| `utm_term` | الكلمة المفتاحية أو الجمهور | `marketing-agency-riyadh`، `lookalike-1pct` |

**القواعد:** أحرف إنجليزية صغيرة، وشرطات بدل المسافات، ونفس الاسم دائمًا لنفس الحملة.
**في إعلانات Meta و TikTok** يمكن استخدام المتغيرات الديناميكية في URL parameters:
`utm_source=facebook&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}`

---

## 7) التحقق بعد التفعيل

- GA4 ← Admin ← **DebugView** (أو إضافة Google Tag Assistant): افتح الموقع برابط فيه UTM واضغط زر واتساب، فيجب أن يظهر `whatsapp_click` ومعه المصدر.
- Meta Events Manager ← **Test events**، و TikTok ← **Test events**.
- من الكونسول في المتصفح: `MKN.attribution()` يعرض المصدر المحفوظ، و `dataLayer` يعرض كل الأحداث.

## 8) الخصوصية

صفحة `privacy.html` تشرح استخدام أدوات القياس. إذا استهدفتم زوارًا من أوروبا أو أسواق تشترط الموافقة المسبقة، أضيفوا لافتة موافقة (Consent Mode) قبل تفعيل البكسلات.
