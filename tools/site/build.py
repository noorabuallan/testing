"""MKN ARABIA site generator.

python3 tools/site/build.py            → static site (repo root) + WordPress theme (wordpress/mkn-arabia)
MKN_TARGET=theme python3 tools/site/build.py → theme fragments only (used internally)
"""
import os, math, html, re, json, hashlib, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
THEME = os.environ.get("MKN_TARGET") == "theme"
THEME_DIR = os.path.join(OUT, "wordpress", "mkn-arabia")
THEME_PAGES = {}
e = html.escape

WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1s-.5-.1-.7.1-.8 1-.9 1.2-.3.2-.6.1a8 8 0 0 1-2.4-1.5 9 9 0 0 1-1.6-2c-.2-.3 0-.5.1-.6l.4-.5.3-.5v-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6a1.1 1.1 0 0 0-.8.4 3.4 3.4 0 0 0-1 2.5 5.9 5.9 0 0 0 1.2 3.1 13.4 13.4 0 0 0 5.2 4.6c.7.3 1.3.5 1.7.6a4.2 4.2 0 0 0 1.9.1 3.1 3.1 0 0 0 2-1.4 2.5 2.5 0 0 0 .2-1.4c-.1-.2-.3-.2-.6-.4ZM12 21.8a9.9 9.9 0 0 1-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.9 9.9 0 1 1 12 21.8Zm8.4-18.3A11.8 11.8 0 0 0 1.8 17.7L.1 24l6.4-1.7a11.8 11.8 0 0 0 5.6 1.4 11.8 11.8 0 0 0 8.3-20.2Z"/></svg>'

NAV = [("./", "الرئيسية"), ("services.html", "الخدمات"), ("pricing.html", "الباقات"), ("work.html", "أعمالنا"), ("insights.html", "المقالات"), ("about.html", "من نحن"), ("contact.html", "تواصل")]
BOOK = "https://calendar.app.google/kJDTjHQZmPZWF2Db7"
BOOK_EMBED = "https://calendar.google.com/calendar/appointments/schedules/AcZssZ0_SZA9tnwj_9R_n-ebdo2FBUuX28625sIGvoKApG3Fp1Li678AUdGqkuWumBv5LrElyA3ZuO0S?gv=true"
BOOK_A = f'href="{BOOK}" target="_blank" rel="noopener" data-book'
sys.path.insert(0, HERE)
from articles import ARTICLES
from testimonials import TESTIMONIALS, COUNTRIES

DEPTS = [
 dict(code="D01", axis="STRATEGY", t="الاستراتيجية والاستشارات وتخطيط النمو", short="الاستراتيجية وتخطيط النمو",
  lead="نحوّل سياق العمل والبيانات المتاحة إلى قرارات محددة: من نخدم، وما القيمة، وأين نركز، وكيف نقيس التقدم.",
  fit="المؤسسون والشركات التي تحتاج إلى ترتيب أولوياتها أو إعادة تموضعها أو التخطيط لمرحلة نمو جديدة.",
  prob="قد تتوزع الجهود بين قنوات كثيرة دون معرفة العميل الأهم أو العرض الأقوى أو موضع التعطل في الرحلة التجارية.",
  subs=[("تدقيق النمو الرقمي","GROWTH AUDIT","مراجعة 4 أصول رقمية، جلسة 60 دقيقة، تقرير حتى 12 صفحة، 10 أولويات مرتبة."),
        ("استراتيجية نمو رقمية","GROWTH STRATEGY","3 شرائح جمهور، 5 منافسين، 3 قنوات، رحلة واحدة، خارطة 90 يومًا، إطار 8 مؤشرات."),
        ("دراسة الجمهور والمنافسين","AUDIENCE &amp; MARKET","دراسة مكتبية لـ5 منافسين، 3 شرائح، 3 ملفات جمهور افتراضية، تقرير حتى 15 صفحة."),
        ("خارطة نمو وخطة حملة","GROWTH ROADMAP","خارطة 90 يومًا، حملة بهدف واحد، 3 مسارات تنفيذ، سجل مسؤوليات، 6 مؤشرات."),
        ("جلسة استشارة تجارية","GROWTH WORKSHOP","جلسة 90 دقيقة، تحضير موضوع واحد، ملخص حتى 3 صفحات، 5 خطوات تالية."),
        ("خطة دخول سوق","GO TO MARKET","5 منافسين، 3 شرائح، عرض قيمة، قنوات، سيناريو ميزانية، خارطة 90 يومًا.")],
  measure="قرارات معتمدة، أولويات تدخل حيز التنفيذ، وخط أساس واضح للمؤشرات نقيس عليه التقدم.",
  special_label="يُتفق عليه منفصلًا", special="البحوث الميدانية والعينات الممثلة والمقابلات الواسعة (عبر شريك متخصص)."),
 dict(code="D02", axis="CREATIVE", t="بناء العلامة التجارية والهوية والتصميم المؤسسي", short="العلامة والهوية",
  lead="نربط التموضع بالتعبير اللفظي والبصري، ثم نوثق قواعد الاستخدام والمخرجات التي يحتاجها الفريق فعليًا.",
  fit="الأعمال الجديدة والشركات التي تطور تموضعها أو تحتاج لغة بصرية ومؤسسية متسقة.",
  prob="قد يقدم العمل خدمة قوية لكن الهوية والرسائل والعروض لا تعكس مستواه أو تميزه.",
  subs=[("تموضع ورسائل العلامة","BRAND POSITIONING","جلسة اكتشاف، عرض قيمة، 3 أعمدة رسائل، نبرة تواصل، 5 نصوص تعريفية."),
        ("نظام الهوية البصرية","VISUAL IDENTITY","اتجاها تصميم، شعار بنسخه، ألوان وخطوط، دليل مختصر 12 صفحة، 3 تطبيقات."),
        ("دليل استخدام الهوية","BRAND GUIDELINES","دليل حتى 24 صفحة لقواعد الشعار والألوان والخطوط والصور، 6 أمثلة استعمال."),
        ("بروفايل شركة تحريري","CORPORATE PROFILE","هيكلة وكتابة عربية حتى 2500 كلمة، تصميم حتى 20 صفحة."),
        ("عرض تقديمي مؤسسي","CORPORATE DECK","تصميم 12 شريحة من نص جاهز، جداول ومخطط، PPTX وPDF."),
        ("تصميم عبوة وتطبيقات","PACKAGING","عبوة واحدة بمقاس واحد، نموذجا عرض، PDF جاهز بحسب قالب المورد."),
        ("تسمية علامة","BRAND NAMING","6 أسماء باتجاهين، تفسير، فحص مكتبي أولي للنطاقات والتشابه.")],
  measure="اعتماد النظام، اتساق التطبيقات، جاهزية ملفات الإنتاج، وسهولة استخدامها من الفريق.",
  special_label="يُتفق عليه منفصلًا", special="تسجيل العلامة، والفحص القانوني للأسماء، والطباعة والتصنيع."),
 dict(code="D03", axis="CREATIVE", t="المحتوى والإنتاج الإبداعي وإدارة التواصل الاجتماعي", short="المحتوى والإنتاج الإبداعي",
  lead="نبني خطة موضوعات ورسائل ثم نحولها إلى مواد محددة ونشر متفق عليه؛ يرتبط كل مخرج بمرحلة في رحلة العميل.",
  fit="العلامات التي تحتاج حضورًا منظمًا ومحتوى يشرح خدماتها ويقود إلى خطوة تجارية واضحة.",
  prob="النشر المتكرر قد يستهلك الوقت دون رسالة متسقة أو مواد كافية للاختبار والتحويل.",
  subs=[("خطة محتوى شهرية","CONTENT PLAN","4 محاور، تقويم 12 فكرة، 12 كابشن، 4 موجزات فيديو، جدول نشر."),
        ("تصميم منشور ثابت","STATIC POST","منشور 1080×1350 مع تكييف ستوري 1080×1920."),
        ("جدولة ونشر محتوى","PUBLISHING","نشر حتى 12 مادة على قناتين مع تكييف الكابشن وتقرير نشر."),
        ("تصميم كاروسيل","CAROUSEL","حتى 6 شرائح متسقة من نص جاهز."),
        ("مونتاج ريل","REEL EDITING","فيديو 15–45 ثانية بمقاس 9:16 وعناوين عربية."),
        ("تكييف فيديو قصير","SHORT VIDEO","تكييف فيديو معتمد حتى 30 ثانية، قص وعناوين."),
        ("تنويعات إبداعية للإعلان","AD CREATIVE VARIATIONS","3 تنويعات من فكرة معتمدة، 3 افتتاحيات و3 CTA."),
        ("إنتاج إبداعي بمساعدة AI","AI CREATIVE ASSETS","3 صور نهائية من مفهوم واحد مع مراجعة بشرية."),
        ("متابعة مجتمع محدودة","COMMUNITY SUPPORT","فرز حتى 150 محادثة أو تعليق شهريًا بقوالب معتمدة.")],
  measure="نشر منتظم في موعده، تفاعل من الجمهور المستهدف، ونقرات واستفسارات قابلة للتتبع.",
  special_label="يُتفق عليه منفصلًا", special="التصوير والممثلون والتعليق الصوتي والمؤثرون وترخيص الموسيقى."),
 dict(code="D04", axis="PERFORMANCE", t="الإعلانات المدفوعة وتحسين الأداء", short="الإعلانات المدفوعة",
  lead="نربط الهدف بالجمهور والعرض والمادة الإبداعية ومسار التحويل، ثم نراجع نتائج المنصة والنتائج التجارية كلًا بتعريفه.",
  fit="الشركات التي تمتلك عرضًا واضحًا وقدرة على استقبال الطلب وتريد اختبار الاستقطاب المدفوع.",
  prob="قد تجلب الحملات تواصلًا دون معرفة الجودة أو الحجز أو المبيعات الناتجة عنه.",
  subs=[("تدقيق حساب إعلاني","CAMPAIGN AUDIT","مراجعة حساب منصة واحدة لـ90 يومًا، 5 حملات، تقرير حتى 10 صفحات."),
        ("إعداد حملة وحساب","CAMPAIGN SETUP","منصة وهدف واحد، حتى حملتين و4 مجموعات و6 إعلانات، تحقق تتبع أساسي."),
        ("إدارة إعلانات منصة واحدة","PAID MEDIA MGMT","حتى 3 حملات و12 إعلانًا نشطًا، مراجعتا تحسين أسبوعيًا، إنفاق إعلاني حتى 3,000 دولار شهريًا."),
        ("خطة اختبار إبداعي","CREATIVE TEST PLAN","4 فرضيات، مصفوفة حتى 6 نسخ، معيار تقييم، دورة 30 يومًا."),
        ("مراجعة تحويل صفحة","CONVERSION REVIEW","مراجعة رسالة ونموذج وCTA، 10 توصيات مرتبة، 3 أحداث قياس مقترحة.")],
  measure="الإنفاق، الوصول، النقرات، التواصل أو التحويلات المثبتة، وجودة العملاء عند مشاركة بياناتهم المجهلة.",
  special_label="تخضع لسياسات المنصات", special="مراجعة الإعلانات واستقرار الحسابات؛ وإتمام البيع لدى فريقك."),
 dict(code="D05", axis="TECHNOLOGY", t="المواقع والمتاجر الإلكترونية", short="المواقع والمتاجر",
  lead="نرتب المحتوى والصفحات والتجربة، وننفذ الأساس التقني والتكاملات المتفق عليها ونختبر التسليم.",
  fit="الشركات التي تحتاج موقعًا مؤسسيًا أو صفحة تحويل أو متجرًا محدد النطاق.",
  prob="قد يوجد الموقع لكن المعلومات أو التنقل أو الحجز أو القياس لا تدعم قرار العميل.",
  subs=[("صفحة هبوط","LANDING PAGE","صفحة حتى 7 أقسام على WordPress، نموذج، متوافقة مع كل الأجهزة، 3 أحداث قياس."),
        ("موقع مؤسسي","CORPORATE WEBSITE","WordPress حتى 6 صفحات، نموذج تواصل، أساس SEO، 5 أحداث، تدريب 60 دقيقة."),
        ("تأسيس متجر محدود","COMMERCE SETUP","Shopify أو سلة أو زد: حتى 20 منتجًا و5 فئات، بوابة دفع وشحن، اختبار طلب."),
        ("ربط حجز قياسي","BOOKING INTEGRATION","ربط منصة حجز مثل Fresha في 3 مواضع، اختبار هاتف وحاسوب."),
        ("إضافة لغة ثانية","SECOND LANGUAGE","حتى 6 صفحات بلغة ثانية، اتجاه RTL عند الحاجة، فحص روابط."),
        ("نقل موقع WordPress","WEBSITE MIGRATION","موقع حتى 2GB، نسخة قاعدة وملفات، نقل إلى استضافة واحدة، خطة عودة."),
        ("صيانة موقع محدودة","MAINTENANCE","تحديثات ونسخة احتياطية شهرية، حتى 3 ساعات تغييرات محتوى.")],
  measure="قبول الصفحات والوظائف، إتمام الإجراء، سلامة التتبع، وأداء تقني يقاس على بيئة التسليم.",
  special_label="يُحدَّد بعد مراجعة المنصة", special="بوابات الدفع والشحن والاشتراكات والتطبيقات والقوالب المدفوعة."),
 dict(code="D06", axis="PERFORMANCE", t="الظهور في البحث والقياس والتحليلات", short="البحث والقياس",
  lead="نرتب أساس البحث والملف المحلي، ونحدد الأحداث والمؤشرات ومصادرها قبل تحويلها إلى تقرير قابل للاستخدام.",
  fit="الأعمال المحلية والمواقع التي تحتاج تحسين الاكتشاف أو تصحيح القياس أو ربط التقارير بالقرار.",
  prob="الترتيب أو التفاعل أو تقرير المنصة لا يوضح وحده لماذا يتغير الطلب أو أين تتعطل الرحلة.",
  subs=[("ظهور محلي وملف Google","LOCAL VISIBILITY","مراجعة الملف و5 خدمات، 4 تحديثات، ردود حتى 15 تقييمًا بقوالب معتمدة."),
        ("إعداد قياس وتحويلات","TRACKING SETUP","GA4 وGTM، حتى 5 أحداث، Pixel، روابط UTM، جدول تعريف واختبار."),
        ("تقرير أداء وقراءة إدارية","PERFORMANCE REPORT","تقرير حتى 10 صفحات من 3 مصادر، 10 مؤشرات، 5 توصيات."),
        ("تدقيق SEO","SEO AUDIT","حتى 30 رابطًا، مراجعة فهرسة وعناوين وروابط، 15 أولوية، خطة 90 يومًا."),
        ("تحسين SEO شهري","SEO MANAGEMENT","حتى 5 صفحات محسنة، 10 كلمات متابعة، موجزا محتوى، مراجعة تقنية."),
        ("لوحة تقارير محدودة","REPORTING DASHBOARD","حتى 3 مصادر و10 مؤشرات و3 صفحات، نسخة قابلة للتحديث."),
        ("دراسة تتبع خادمي","SERVER TRACKING","خريطة أحداث، مراجعة مصدرين، نموذج جدوى وخصوصية، خطة تنفيذ.")],
  measure="أحداث تتبع تعمل بدقة، بيانات مكتملة، ومؤشرات ظهور في Google وخرائطها نتابعها شهريًا.",
  special_label="تخضع لـGoogle", special="الفهرسة وترتيب النتائج وعمليات التحقق."),
 dict(code="D07", axis="TECHNOLOGY", t="إدارة علاقات العملاء والأتمتة وحلول الذكاء الاصطناعي التطبيقية", short="CRM والأتمتة وAI",
  lead="نبدأ بتوثيق الرحلة ومسؤولياتها، ثم ندرس ملاءمة الأداة والتكاملات قبل تنفيذ الأتمتة أو نموذج AI تجريبي.",
  fit="الأعمال التي تتكرر لديها المتابعة والتنسيق وتحتاج تنظيمًا أو تجربة تقنية محدودة يمكن اختبارها.",
  prob="تضيع معلومات العملاء بين القنوات، وتبقى المتابعة معتمدة على الذاكرة أو نقل البيانات يدويًا.",
  subs=[("توثيق رحلة وإجراءات متابعة","JOURNEY &amp; WORKFLOW","رحلة حتى 6 مراحل، 3 أدوار، 8 حالات متابعة، مصفوفة مسؤوليات."),
        ("دليل تواصل وقوالب متابعة","PLAYBOOK","حتى 25 قالبًا، 3 قنوات، قواعد تصعيد، 8 سيناريوهات اختبار."),
        ("تهيئة CRM محدودة","CRM SETUP","Pipeline حتى 6 مراحل، 10 حقول، استيراد حتى 500 سجل، تدريب 60 دقيقة."),
        ("أتمتة عملية واحدة","WORKFLOW AUTOMATION","Trigger واحد حتى 4 Actions بين نظامين، اختبار وتنبيه أخطاء."),
        ("متابعة أتمتة محدودة","AUTOMATION CARE","حتى عمليتين، مراجعة أسبوعية، 4 ساعات إصلاحات، تقرير شهري."),
        ("دراسة تطبيق AI","AI FEASIBILITY","حالة استخدام واحدة، مراجعة بيانات ومخاطر، مقارنة نهجين، خطة تكاليف."),
        ("نموذج AI تجريبي","AI WORKFLOW PILOT","تجربة بواجهة بسيطة ومزود واحد، حتى 20 حالة اختبار، تقرير قرار استمرار.")],
  measure="مسار متابعة موثق، حالات اختبار ناجحة، وتحويل سلس للحالات المعقدة إلى فريقك.",
  special_label="تُدفع للموردين بموافقتك", special="اشتراكات CRM وواجهات الرسائل وAPI ونماذج الذكاء الاصطناعي."),
 dict(code="D08", axis="TECHNOLOGY", t="البرمجيات والأنظمة المخصصة ومنتجات SaaS", short="الأنظمة المخصصة وSaaS",
  lead="نوثق المتطلبات ثم نبني نموذجًا محدودًا ونختبره. يأتي الانتقال إلى الإنتاج بعد اعتماد البنية والاستضافة والبيانات والأمن والدعم.",
  fit="الشركات التي لا تغطي الأدوات الجاهزة سير عملها وتستطيع تحديد مالك للعملية ونطاق تجريبي.",
  prob="تؤدي الأدوات المنفصلة أو الملفات المتعددة إلى تكرار الإدخال وصعوبة فهم التشغيل والصلاحيات.",
  subs=[("اكتشاف تقني ومتطلبات","TECH DISCOVERY","حتى 3 عمليات و3 أدوار، 15 قصة استخدام، نموذج 6 شاشات، خطة بنية وتقدير."),
        ("تطوير MVP محدود","CUSTOM MVP","تطبيق ويب، 3 أدوار، 6 شاشات، 3 كيانات بيانات، API، بيئة تجريبية."),
        ("تجربة تشغيل نظام قائم","SYSTEM PILOT","تهيئة نموذج لعملية واحدة، 5 شاشات، 50 سجل اختبار، خطة انتقال للإنتاج."),
        ("تكامل تقني محدود","API INTEGRATION","نظامان، حتى 3 Endpoints، آلية فشل وإعادة محاولة، 10 اختبارات."),
        ("تطوير وحدة إضافية","CUSTOM MODULE","حتى شاشتين وكيان بيانات وصلاحيتين و8 اختبارات قبول."),
        ("دعم وصيانة تقنية","SYSTEM SUPPORT","10 ساعات شهريًا، سجل طلبات، مراجعة شهرية."),
        ("دراسة نظام عقاري","REAL ESTATE DISCOVERY","خريطة عقار ووحدة ووسائط، 6 شاشات نموذج، دراسة تكامل موقع.")],
  measure="اجتياز معايير القبول، سلامة الأدوار والنسخ الاحتياطية، ثم مؤشرات استخدام متفق عليها بعد الإطلاق.",
  special_label="يُتفق عليه منفصلًا", special="الدفع والرسائل والاستضافة والأمن واختبارات الاختراق والربط المحاسبي."),
]

# Pricing tiers: (name_ar, name_en, price, unit, setup, goal, [(k,v)...])
TIERS = {
 "D01": [("تأسيس","FOUNDATION","350","مشروع","", "تشخيص الوضع وترتيب أولويات التحسين", [("المخرجات","حتى 4 أصول رقمية، تقرير 12 صفحة و10 أولويات"),("المدة","5–7 أيام عمل"),("الاجتماعات","جلسة 60 دقيقة")]),
         ("نمو","GROWTH","950","مشروع","", "خطة متكاملة لعلامة وسوق واحد", [("المخرجات","3 شرائح، 5 منافسين، رحلة، خارطة 90 يومًا، 8 مؤشرات، حتى 3 قنوات"),("المدة","10–15 يوم عمل"),("الاجتماعات","جلستان 60 دقيقة"),("التقرير","استراتيجية حتى 25 صفحة")]),
         ("توسع","SCALE","1,600","مرحلة دراسة","", "دخول سوق ومراجعة قرارات التنفيذ", [("المخرجات","خطة سوق واحدة وورشتا مراجعة إضافيتان 90 دقيقة"),("المدة","15–20 يوم عمل ثم مراجعتان خلال 60 يومًا"),("الاجتماعات","جلسة اكتشاف وورشتان"),("التقرير","خطة حتى 30 صفحة")])],
 "D02": [("تأسيس","FOUNDATION","1,200","مشروع","", "نظام بصري لعلامة واحدة", [("المخرجات","اتجاها تصميم، شعار، دليل 12 صفحة، 3 تطبيقات"),("المدة","15–20 يوم عمل"),("الاجتماعات","جلستا اتجاه واعتماد")]),
         ("نمو","GROWTH","1,800","مشروع","", "تموضع ورسائل مع هوية", [("المخرجات","إطار رسائل 12 صفحة، نظام بصري، 3 تطبيقات"),("المدة","20–25 يوم عمل"),("الاجتماعات","3 جلسات")]),
         ("توسع","SCALE","3,000","مشروع","", "تموضع وهوية وتواصل مؤسسي", [("المخرجات","دليل هوية 24 صفحة، 3 تطبيقات، بروفايل 20 صفحة"),("المدة","30–40 يوم عمل"),("الاجتماعات","4 جلسات")])],
 "D03": [("تأسيس","FOUNDATION","925","شهريًا","", "حضور شهري منتظم من المواد المتاحة", [("المخرجات","6 منشورات ومقطعا ريلز؛ 8 مواد أصلية"),("القنوات","قناتان"),("الاجتماعات","اجتماع 45 دقيقة"),("التعاقد","3 أشهر")]),
         ("نمو","GROWTH","1,850","شهريًا","", "توسيع الشرح والاختبار الإبداعي", [("المخرجات","9 منشورات، منشورا كاروسيل، 4 مقاطع ريلز؛ 15 مادة أصلية؛ تقويم 24 فكرة"),("القنوات","قناتان"),("الاجتماعات","اجتماعان 45 دقيقة"),("التعاقد","3 أشهر")]),
         ("توسع","SCALE","3,150","شهريًا","", "إنتاج منظم لحجم أكبر من الموضوعات", [("المخرجات","12 منشورًا، 4 منشورات كاروسيل، 6 مقاطع ريلز، 4 تكييفات فيديو؛ فرز 150 تواصلًا"),("القنوات","قناتان للنشر وقناة للفرز"),("الاجتماعات","اجتماعان 45 دقيقة"),("التعاقد","3 أشهر")])],
 "D04": [("تأسيس","FOUNDATION","400","شهريًا","+ 300 إعداد مستقل", "إدارة هدف استقطاب واضح", [("المخرجات","3 حملات، 6 مجموعات، 12 إعلانًا"),("القنوات","منصة واحدة"),("سقف الإنفاق الإعلاني","حتى 3,000 دولار شهريًا"),("التعاقد","3 أشهر")]),
         ("نمو","GROWTH","1,050","شهريًا","+ 600 إعداد مستقل", "تنسيق منصتين واختبار الرسائل", [("المخرجات","6 حملات، 12 مجموعة، 24 إعلانًا، 4 فرضيات اختبار"),("القنوات","منصتان"),("سقف الإنفاق الإعلاني","حتى 6,000 دولار شهريًا للمنصتين معًا"),("التعاقد","3 أشهر")]),
         ("توسع","SCALE","1,450","شهريًا","+ 1,150 إعداد مستقل", "تشغيل ثلاث منصات ضمن حدود معلنة", [("المخرجات","9 حملات، 18 مجموعة، 36 إعلانًا"),("القنوات","3 منصات بعد تثبيت التنفيذ"),("سقف الإنفاق الإعلاني","حتى 9,000 دولار شهريًا للمنصات الثلاث"),("التعاقد","3 أشهر")])],
 "D05": [("تأسيس","FOUNDATION","600","مشروع","", "وجهة رقمية لهدف واحد", [("المخرجات","صفحة 7 أقسام، نموذج، 3 أحداث قياس"),("النطاق","موقع واحد بلغة واحدة"),("المدة","7–10 أيام عمل")]),
         ("نمو","GROWTH","1,500","مشروع","", "موقع مؤسسي مرتب وقابل للقياس", [("المخرجات","6 صفحات، نموذج، 5 أحداث، تدريب 60 دقيقة"),("النطاق","موقع واحد بلغة واحدة"),("المدة","20–25 يوم عمل")]),
         ("توسع","SCALE","2,300","مشروع","", "موقع ثنائي اللغة مع مسار حجز", [("المخرجات","6 صفحات لكل لغة، ربط حجز قياسي"),("النطاق","موقع واحد بلغتين"),("المدة","25–35 يوم عمل")])],
 "D06": [("تأسيس","FOUNDATION","300","شهريًا","", "تثبيت الظهور المحلي لموقع واحد", [("المخرجات","4 تحديثات، 5 خدمات، حتى 15 رد تقييم"),("النطاق","ملف Google واحد"),("الاجتماعات","اجتماع 30 دقيقة"),("التعاقد","3 أشهر")]),
         ("نمو","GROWTH","825","شهريًا","+ 400 إعداد مستقل", "ربط الموقع والظهور المحلي", [("المخرجات","5 صفحات SEO، 10 كلمات، موجزا محتوى، 4 تحديثات محلية"),("النطاق","موقع واحد وملف واحد"),("التقرير","تقرير موحد شهري"),("التعاقد","3 أشهر")]),
         ("توسع","SCALE","1,025","شهريًا","+ 900 إعداد مستقل", "ظهور وقراءة إدارية من مصادر محددة", [("المخرجات","مخرجات النمو + تقرير 10 صفحات و10 مؤشرات"),("النطاق","موقع وملف وحتى 3 مصادر"),("الاجتماعات","اجتماعان 45 دقيقة"),("التعاقد","3 أشهر")])],
 "D07": [("تأسيس","FOUNDATION","900","مشروع","", "تنظيم رحلة المتابعة قبل شراء الأدوات", [("المخرجات","رحلة 6 مراحل و3 أدوار، 25 قالبًا، 8 اختبارات"),("القنوات","حتى 3 قنوات في دليل التواصل"),("المدة","10–15 يوم عمل")]),
         ("نمو","GROWTH","1,550","مشروع مشروط","", "تهيئة CRM وعملية متابعة واحدة", [("المخرجات","6 مراحل، 3 أدوار، 500 سجل، أتمتة 4 إجراءات"),("الأنظمة","أداة CRM ونظام متصل"),("المدة","20–30 يوم عمل بعد الجدوى")]),
         ("توسع","SCALE","2,200","مشروع مشروط","", "CRM وعمليتان مترابطتان", [("المخرجات","6 مراحل، 3 أدوار، 500 سجل؛ عمليتان حتى 4 إجراءات لكل منهما"),("الأنظمة","CRM ونظامان معتمدان"),("المدة","25–35 يوم عمل بعد الجدوى"),("الصيانة","متابعة اختيارية بعد التسليم")])],
 "D08": [("تأسيس","FOUNDATION","1,000","مرحلة دراسة","", "تحويل الحاجة إلى متطلبات قابلة للتسعير", [("المخرجات","3 عمليات، 3 أدوار، 15 قصة، 6 شاشات نموذج، 10 معايير"),("المدة","10–15 يوم عمل"),("التقرير","وثيقة نطاق وخطة بنية وتقدير")]),
         ("نمو","GROWTH","3,800","مرحلة تجريبية","+ 1,000 إعداد مستقل", "تقييم نموذج تقني قائم بعملية واحدة", [("المخرجات","3 أدوار، 5 شاشات، 50 سجلًا تجريبيًا"),("البيئة","بيئة اختبار واحدة"),("المدة","6–8 أسابيع بعد الاكتشاف")]),
         ("توسع","SCALE","6,000","مرحلة تطوير","+ 1,000 إعداد مستقل", "بناء MVP محدود لمتطلبات معتمدة", [("المخرجات","3 أدوار، 6 شاشات، 3 كيانات، API واحد"),("البيئة","تطبيق ويب وبيئة تجريبية"),("المدة","8–10 أسابيع بعد الاكتشاف"),("الدعم","دعم وصيانة اختيارية بعد التسليم")])],
}

BUNDLES = [
 ("X01","إطلاق علامة","BRAND LAUNCH","ربط الفكرة التجارية بهوية ووجهة تحويل ومحتوى إطلاق: تدقيق، تموضع، هوية و3 تطبيقات، صفحة هبوط 7 أقسام، تقويم و6 منشورات.",[("مشروع","3,150")],"30–40 يوم عمل"),
 ("X02","الأساس الرقمي","DIGITAL FOUNDATION","الهوية والموقع والحضور المحلي والنشر ضمن نطاق واحد: هوية، موقع 6 صفحات، 6 منشورات افتتاحية؛ شهريًا ملف محلي و4 تحديثات ونشر حتى 12 مادة على قناتين.",[("إعداد","2,900"),("شهريًا","+500")],"30–40 يوم عمل ثم دورة شهرية"),
 ("X03","نمو الأداء","PERFORMANCE GROWTH","وصل التدقيق وصفحة التحويل باختبار الإعلان: تدقيق، صفحة واحدة، إعداد منصة؛ شهريًا إدارة منصة و3 تنويعات إبداعية وتقرير.",[("إعداد","1,250"),("شهريًا","+575")],"15–20 يوم عمل ثم 3 أشهر"),
 ("X04","نمو التجارة","ECOMMERCE GROWTH","تأسيس التجربة والقياس وربط المنتج بالاستقطاب: متجر 20 منتجًا و5 فئات، قياس 5 أحداث، إعداد منصة؛ شهريًا 12 فكرة و6 منشورات ومقطعا ريلز وإدارة منصة.",[("إعداد","2,500"),("شهريًا","+1,125")],"25–35 يوم عمل ثم دورة شهرية"),
 ("X05","توليد طلب الشركات (B2B)","B2B DEMAND ENGINE","ربط التموضع بالمحتوى والمتابعة والاستقطاب: تموضع ورسائل، رحلة CRM محدود، إعداد إعلان؛ شهريًا خطة و6 منشورات ونشر وإدارة منصة.",[("إعداد","2,150"),("شهريًا","+1,100")],"25–35 يوم عمل ثم دورة شهرية"),
 ("X06","نمو أعمال الخدمات","SERVICE BUSINESS GROWTH","تنسيق المحتوى والبحث والإعلان ومسار الحجز: ربط حجز وقياس وإعداد إعلان؛ شهريًا 6 منشورات ومقطعا ريلز ونشر قناتين وإدارة منصة و4 تحديثات محلية وتقرير موحد.",[("إعداد","1,050"),("شهريًا","+1,600")],"15–20 يوم عمل ثم دورة شهرية"),
 ("X07","التقنية والأتمتة","TECHNOLOGY &amp; AUTOMATION","تنظيم العميل والعملية والتقرير: رحلة وCRM محدود وعملية 4 إجراءات ولوحة 10 مؤشرات؛ متابعة شهرية حتى عمليتين و4 ساعات إصلاحات.",[("إعداد","2,450"),("شهريًا","+300")],"25–35 يوم عمل بعد الجدوى"),
 ("X08","تحول رقمي مخصص","CUSTOM DIGITAL TRANSFORMATION","نقل الاحتياج من المتطلبات إلى MVP قابل للاختبار: اكتشاف كمرحلة مستقلة، ثم تطوير بعد قبول الدراسة، وصيانة اختيارية.",[("مراحل","7,000"),("صيانة شهريًا","+750")],"10–15 يوم اكتشاف ثم 8–10 أسابيع تطوير"),
]

def grid_lines(kind="a"):
    # construction lines inspired by the logo grid
    sets = {
      "a": [(8,0,8,100),(92,0,92,100),(0,22,100,22),(0,78,100,78),(8,0,92,100),(92,0,8,100),(50,0,50,100)],
      "b": [(14,0,14,100),(86,0,86,100),(0,30,100,30),(0,70,100,70),(14,0,86,100)],
      "c": [(30,0,30,100),(70,0,70,100),(0,50,100,50),(30,0,70,100),(70,0,30,100)],
    }[kind]
    ln = "".join(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}"/>' for a, b, c, d in sets)
    return f'<svg class="grid-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">{ln}</svg>'

def badge(extra="", img="assets/img/logo-white-sm.png"):
    txt = "MKN ARABIA · MARKETING AGENCY · "
    return f"""<div class="badge {extra}" aria-hidden="true">
  <svg viewBox="0 0 120 120"><defs><path id="bp{extra.replace(' ','')}" d="M60,60 m-46,0 a46,46 0 1,1 92,0 a46,46 0 1,1 -92,0"/></defs>
  <text direction="ltr"><textPath href="#bp{extra.replace(' ','')}" textLength="286" lengthAdjust="spacing">{txt}</textPath></text></svg>
  <img src="{img}" alt="" width="101" height="34">
</div>"""

def header(active, section=None):
    def attrs(h):
        if h == active: return ' class="active" aria-current="page"'
        if h == section: return ' class="active" aria-current="true"'
        return ""
    links = ""
    for h, t in NAV:
        links += f'<a href="{h}"{attrs(h)}>{t}</a>'
        if h == "work.html":  # testimonials live under «أعمالنا»; listed separately in the mobile menu only
            cur = ' aria-current="page"' if active == "testimonials.html" else ""
            links += f'<a href="testimonials.html" class="nav__m{" active" if cur else ""}"{cur}>آراء العملاء</a>'
    return f'''<header class="header">
  <div class="container"><div class="header__inner">
    <a href="./" class="logo" aria-label="MKN ARABIA — الرئيسية"><img src="assets/img/logo-white-sm.png" alt="MKN ARABIA" width="101" height="34"></a>
    <a {BOOK_A} class="btn btn--blue btn--sm header__book">احجز<span class="hb-x"> استشارة</span></a>
    <button type="button" class="nav-toggle" aria-label="فتح القائمة" aria-expanded="false" aria-controls="site-nav"><span></span><span></span><span></span></button>
    <nav class="nav" id="site-nav" aria-label="القائمة الرئيسية">
      {links}
      <a {BOOK_A} class="btn btn--blue btn--sm">احجز استشارة</a>
      <a href="#" data-wa class="btn btn--line btn--sm nav__wa">واتساب</a>
    </nav>
  </div></div>
</header>'''

def footer():
    dl = "".join(f'<li><a href="services/{SVC_SLUG_EARLY[d["code"].lower()]}.html"><span class="ltr">{d["code"]}</span> · {d["short"]}</a></li>' for d in DEPTS)
    return f'''<footer class="footer">
  <img class="footer__mark" src="assets/img/logo-white.png" alt="" width="620" height="210" loading="lazy">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        <a href="./" class="logo"><img src="assets/img/logo-white-sm.png" alt="MKN ARABIA" width="101" height="34"></a>
        <p>شريك استراتيجي لنمو الأعمال. نربط الاستراتيجية والإبداع والأداء والتقنية حول هدف تجاري واحد.</p>
        <p class="slogan">سوّق بالعربي، سوّق صح</p>
        {badge("footer-badge")}
      </div>
      <div><details class="fdepts"><summary class="fh">الخدمات</summary><ul>{dl}</ul></details></div>
      <div>
        <h2 class="fh">استكشف</h2>
        <ul>
          <li><a href="pricing.html">الباقات وعرض السعر</a></li>
          <li><a href="pricing.html#bundles">الحلول المتكاملة</a></li>
          <li><a href="work.html">أعمالنا</a></li>
          <li><a href="testimonials.html">آراء العملاء</a></li>
          <li><a href="insights.html">المقالات</a></li>
          <li><a href="markets.html">الأسواق: الخليج</a></li>
        </ul>
      </div>
      <div>
        <h2 class="fh">الشركة</h2>
        <ul>
          <li><a href="about.html">من نحن</a></li>
          <li><a href="about.html#method">منهجية العمل</a></li>
          <li><a href="contact.html">تواصل</a></li>
          <li><a href="privacy.html">سياسة الخصوصية</a></li>
        </ul>
      </div>
      <div>
        <h2 class="fh">تواصل</h2>
        <ul>
          <li><a {BOOK_A}>احجز استشارة مجانية</a></li>
          <li><a href="#" data-wa>واتساب · <span class="ltr">+20 114 055 2627</span></a></li>
          <li><a data-email href="mailto:contact@mknarabia.com">contact@mknarabia.com</a></li>
          <li><a href="https://instagram.com/mknarabia" target="_blank" rel="noopener">Instagram · <span class="ltr">@mknarabia</span></a></li>
          <li><a href="https://facebook.com/mknarabia" target="_blank" rel="noopener">Facebook · <span class="ltr">@mknarabia</span></a></li>
          <li><a href="https://linkedin.com/company/mknarabia" target="_blank" rel="noopener">LinkedIn · MKN ARABIA</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© <span data-year></span> MKN ARABIA · الأردن. جميع الحقوق محفوظة.</span>
      <span class="label">STRATEGY · CREATIVE · PERFORMANCE · TECHNOLOGY</span>
    </div>
  </div>
</footer>
<aside aria-label="تواصل سريع"><a class="wa-float" data-wa href="#" aria-label="تواصل عبر واتساب">{WA_SVG}</a></aside>'''

ROBOTS = {"utm.html": "\n<meta name=\"robots\" content=\"noindex, nofollow\">", "404.html": "\n<meta name=\"robots\" content=\"noindex\">"}
NO_CANON = {"404.html", "utm.html"}
def ver(p):  # cache-busting version string: changes whenever the file changes
    return hashlib.md5(open(os.path.join(OUT, p), "rb").read()).hexdigest()[:8]
AR_RE = re.compile(r"[؀-ۿ]")
def polish(doc):
    """Typography fixes on visible text only (never attributes, scripts or JSON-LD)."""
    head, sep, body = doc.partition("<body>")
    parts = re.split(r"(<script\b.*?</script>|<[^>]+>)", body, flags=re.S)
    for i in range(0, len(parts), 2):
        t = parts[i]
        t = t.replace("MKN ARABIA", "MKN&nbsp;ARABIA")          # keep the brand on one line
        t = re.sub(r" و (?=[A-Za-z])", " و", t)                 # attach «و» before Latin words
        parts[i] = t
    body = "".join(parts)
    # English-only mono labels are announced with an English voice
    body = re.sub(r'<span class="(label[^"]*)">([^<]*)</span>',
                  lambda m: f'<span class="{m.group(1)}"{"" if AR_RE.search(m.group(2)) else " lang=" + chr(34) + "en" + chr(34)}>{m.group(2)}</span>', body)
    return head + sep + body

def page(fname, title, desc, active, body, head_extra="", og_type="website", section=None):
    h = body.find(SWIPE_HINT)
    if h >= 0:
        body = body[:h + len(SWIPE_HINT)] + body[h + len(SWIPE_HINT):].replace(SWIPE_HINT, "")
    if THEME:
        THEME_PAGES[fname] = dict(title=title, desc=desc, body=body, og_type=og_type)
        return
    url = f"https://mknarabia.com/{'' if fname == 'index.html' else fname}"
    canon = "" if fname in NO_CANON else f'\n<meta property="og:url" content="{url}">\n<link rel="canonical" href="{url}">'
    doc = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:site_name" content="MKN ARABIA">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="ar_AR">
<meta property="og:image" content="https://mknarabia.com/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="MKN ARABIA — سوّق بالعربي، سوّق صح">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://mknarabia.com/assets/img/og-image.jpg">{canon}{ROBOTS.get(fname, '')}
<meta name="theme-color" content="#0d1114">
<link rel="icon" href="assets/img/favicon-48.png" type="image/png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<script src="assets/js/tracking.js?v={ver('assets/js/tracking.js')}" defer></script>
<link rel="preload" as="image" href="assets/img/brand/diffusion-dark.webp" type="image/webp" fetchpriority="high">
<link rel="preload" href="assets/fonts/ibm-plex-sans-arabic-400-arabic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/ibm-plex-sans-arabic-700-arabic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/fonts.css?v={ver('assets/css/fonts.css')}">
<link rel="stylesheet" href="assets/css/style.css?v={ver('assets/css/style.css')}">{head_extra}
</head>
<body>
<a class="skip-link" href="#main">تخطَّ إلى المحتوى الرئيسي</a>
{header(active, section)}
<main id="main" tabindex="-1">
{body}
</main>
{footer()}
<script src="assets/js/main.js?v={ver('assets/js/main.js')}" defer></script>
</body>
</html>
'''
    doc = polish(doc)
    if "/" in fname:  # nested page: make relative links point one level up
        doc = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/|data:)', r'\1="../', doc)
        doc = doc.replace('href=".././"', 'href="../"').replace("url(assets/", "url(../assets/")
    if fname == "404.html":  # served at any depth by ErrorDocument: use root-absolute URLs
        doc = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/|data:)', r'\1="/', doc)
        doc = doc.replace('href="/./"', 'href="/"').replace("url(assets/", "url(/assets/")
    os.makedirs(os.path.dirname(os.path.join(OUT, fname)), exist_ok=True)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(doc)

HERO_ACTIONS = f"""<div class="hero__actions page-hero__actions">
      <a {BOOK_A} class="btn btn--blue">احجز استشارة مجانية</a>
      <a href="#" data-wa class="btn btn--line">تحدث معنا عبر واتساب</a>
    </div>"""
def page_hero(label, h1, p, actions=False, extra="", chip=True):
    tail = HERO_ACTIONS if actions else ('<span class="chip"><span class="dot"></span>سوّق بالعربي، سوّق صح</span>' if chip else "")
    return f"""<section class="page-hero grain">
  {grid_lines("b")}
  <div class="container">
    <span class="label">{label}</span>
    <h1>{h1}</h1>
    <p>{p}</p>
    {extra}{tail}
  </div>
</section>"""

CTA = f"""<section class="cta grain">
  <div class="container cta__grid">
    <div class="glass cta__card reveal">
      <span class="label">LET'S BUILD WHAT'S NEXT</span>
      <h2>النمو يُبنى،<br>لا يُطارَد.</h2>
      <p>سواء كنت تحتاج إعادة تموضع العلامة، أو تحسين توليد العملاء، أو بناء متجر، أو ربط العمليات بنظام CRM، ابدأ بجلسة لتحديد نقطة الانطلاق الصحيحة.</p>
      <div class="hero__actions">
        <a {BOOK_A} class="btn btn--dark">احجز استشارة مجانية</a>
        <a href="#" data-wa class="btn btn--line">تحدث معنا عبر واتساب</a>
      </div>
      <p class="cta-note">30 دقيقة مع المؤسس عبر Google Meet · مجانية · دون أي التزام</p>
    </div>
    <div class="big-mono reveal">BUILD<span>.</span><br>SCALE<span>.</span><br>GROW<span>.</span></div>
  </div>
</section>"""

# ---------- orbit svg ----------
def orbit():
    # static, interleaved rings so labels never collide
    rings = [(70, [], 0), (125, ["BRANDING","POSITIONING","AUDIENCE","OFFER","JOURNEY","IDENTITY"], 0),
             (185, ["META ADS","CONTENT","GOOGLE ADS","REELS","TIKTOK ADS","AI CREATIVE","CAMPAIGNS","LEAD GEN"], 0),
             (245, ["WEBSITES","SEO","LOCAL SEO","CRM","AUTOMATION","DASHBOARDS","SHOPIFY · SALLA · ZID","AI SYSTEMS"], 22.5)]
    out = [f'<circle class="ring" cx="280" cy="280" r="{r}"/>' for r, _, _ in rings]
    for r, labels, off in rings:
        n = len(labels)
        for i, lab in enumerate(labels):
            a = math.radians(off + i * 360 / n - 90)
            x = 280 + r * math.cos(a); y = 280 + r * math.sin(a)
            out.append(f'<rect class="node" x="{x-2.5:.1f}" y="{y-2.5:.1f}" width="5" height="5"/><text class="tag" x="{x:.1f}" y="{y+15:.1f}" text-anchor="middle">{lab}</text>')
    return f'''<div class="orbit" aria-hidden="true"><svg viewBox="-50 -10 660 590">
{''.join(out)}
<circle class="pulse" cx="280" cy="280" r="50"/>
<circle class="core" cx="280" cy="280" r="50"/>
<text class="core-t" x="280" y="284" text-anchor="middle">النمو</text>
<text class="core-s" x="280" y="300" text-anchor="middle">GROWTH</text>
</svg></div>'''

AXES = [("01 · STRATEGY","الاستراتيجية","فهم السياق وتحديد الجمهور والتموضع والأولويات."),
        ("02 · CREATIVE","الإبداع","تحويل الاتجاه إلى هوية ورسائل ومحتوى وتجارب عرض."),
        ("03 · PERFORMANCE","الأداء","اختبار الاستقطاب وقراءة المؤشرات وتحسين رحلة التحويل."),
        ("04 · TECHNOLOGY","التقنية","تنظيم الوجهات والبيانات والمتابعة ودراسة الأنظمة المناسبة للعمل.")]

PROBLEMS = [("جهود تسويق متفرقة بلا اتجاه","نراجع كل ما تقوم به ونرتب الأولويات","خطة واضحة: من يفعل ماذا، وكيف نقيس"),
            ("عميلك لا يعرف لماذا يختارك","نصوغ رسالتك وهويتك","عرض قيمة واضح ودليل يستخدمه فريقك"),
            ("محتوى جميل لا يبيع","خطة محتوى وإنتاج","مواد تقود العميل من الاهتمام إلى الحجز"),
            ("تصرف على الإعلانات ولا تعرف العائد","إدارة الحملات والتتبع والاختبار","تقرير يفصل نتائج المنصة عن الحجوزات والمبيعات الفعلية"),
            ("العميل يضيع بين الروابط والصفحات","صفحة هبوط أو موقع أو ربط حجز","مسار واحد واضح من الإعلان إلى الحجز"),
            ("استفسارات تضيع في واتساب والدفاتر","ننظم المتابعة ثم نؤتمتها","مسار متابعة ومسؤول عن كل حالة"),
            ("أنظمة جاهزة لا تناسب طريقة عملك","دراسة تقنية للاحتياج","متطلبات واضحة ونموذج أولي تجربه")]

LOOP = [("التموضع","POSITIONING","يحدد الرسالة."),("الرسالة","MESSAGE","توجه المادة الإبداعية."),
        ("المادة الإبداعية","CREATIVE","تشرح العرض للجمهور."),("الإعلان","MEDIA","يقود إلى وجهة واضحة."),
        ("الوجهة","DESTINATION","صفحة أو موقع أو حجز."),("التجربة والمتابعة","FOLLOW-UP","تساعد على الخطوة التالية."),
        ("القياس","MEASURE","يوضح ما حدث وما يحتاج تعديلًا.")]

CASES = [
 ("les-senes","Les Sènes Spa","الجمال والعافية · شراكة مستمرة منذ نوفمبر 2023"),
 ("beautiful-shine","Beautiful Shine","الجمال والعافية · أغسطس 2025 – يوليو 2026"),
 ("cryo","CRYO Infinity Jeddah","العافية والاستشفاء · جدة · 2026"),
 ("bud-studio","BU’D Studio","العمارة والتصميم الداخلي · 2026"),
 ("sandouka","Sandouka Coffee","الأغذية والمشروبات · فلسطين · 2025"),
 ("osus","OSUS Events","فعاليات B2B · السعودية · 2026"),
 ("imperio","IMPERIO Events","الفعاليات والتجارب · السعودية · 2026"),
 ("mireva","Mireva Group / Mireva AI","التقنية والجمال · السعودية · 2025–2026"),
 ("restaurant-ops","MKN Restaurant Operations","منتج تقني من تطوير MKN ARABIA · 2026"),
 ("kyan","Kyan Real Estate","العقارات · فلسطين · شراكة منذ يوليو 2024"),
]

# ===================== HOME =====================
SVC_SLUG_EARLY = {"d01": "growth-strategy", "d02": "branding", "d03": "content", "d04": "paid-ads", "d05": "websites", "d06": "seo-geo", "d07": "crm-automation", "d08": "custom-software"}
axes_html = "".join(f'<div class="cell spot reveal"><span class="label">{a}</span><h3>{t}</h3><p>{d}</p></div>' for a, t, d in AXES)
dept_cells = "".join(f"""<a href="services/{SVC_SLUG_EARLY[d["code"].lower()]}.html" class="cell spot reveal"><span class="label" aria-hidden="true">{d["code"]} · {d["axis"]}</span><span class="go" aria-hidden="true">←</span><h3>{d["short"]}</h3><p>{d["fit"]}</p></a>""" for d in DEPTS)
PROB_HEAD = ("المشكلة", "ما نفعله", "ما تحصل عليه")
prob_rows = "".join(f'<tr><td data-label="{PROB_HEAD[0]}"><span class="label">0{i}</span>{a}</td><td data-label="{PROB_HEAD[1]}">{b}</td><td data-label="{PROB_HEAD[2]}">{c}</td></tr>' for i, (a, b, c) in enumerate(PROBLEMS, 1))
LOOP_FLOW = '<ol class="loop-flow">' + "".join(f"<li>{t}</li>" for t, _, _ in LOOP) + "</ol>"
windex = "".join(f'<a href="work.html#{cid}"><span class="n">{i:02d}</span><strong>{n}</strong><span class="s">{s_}</span></a>' for i, (cid, n, s_) in enumerate(CASES, 1))
MQ = ["STRATEGY","BRANDING","CONTENT","META ADS","GOOGLE ADS","TIKTOK ADS","WEBSITES","SALLA · ZID · SHOPIFY","LOCAL SEO","GA4 · GTM","CRM","AUTOMATION","AI SYSTEMS","SAAS"]
marquee = "".join(f"<span>{m}</span>" for m in MQ * 2)
PORTRAITS = [("portrait-1","الاستراتيجية","STRATEGY","سياق ورسالة قبل أي حملة"),
             ("portrait-2","الإبداع","CREATIVE","هوية ومحتوى يشرح العرض"),
             ("portrait-3","الأداء","PERFORMANCE","قياس يخدم القرار")]
portraits = "".join(f"""<figure class="portrait reveal" style="margin:0"><img src="assets/img/brand/{img}.webp" alt="" loading="lazy" width="552" height="470">
  <span class="ptag" aria-hidden="true"><b>{ar}</b><small>{en}</small></span>
  <figcaption class="pcap">{cap}</figcaption></figure>""" for img, ar, en, cap in PORTRAITS)

FOUNDER_QUOTE = "أؤمن أن التسويق يصبح أقوى عندما تتصل الاستراتيجية بالهوية والإبداع والأداء والتقنية، وعندما تستطيع الإدارة فهم ما يحدث وكيف تتخذ قرارها التالي."
FOUNDER_BIO = "يقود د. نور الدين أعمال MKN ARABIA في الاستراتيجية وإدارة المشاريع والنمو الرقمي، مع التركيز على تصميم أنظمة متكاملة تجمع المحتوى والإعلانات والمواقع والتحليلات واحتياجات التشغيل في أسواق الخليج والمنطقة."
SWIPE_HINT = '<p class="swipe-hint" aria-hidden="true">اسحب لعرض المزيد</p>'
import json as _json
_LOGOS = _json.load(open(os.path.join(OUT, "assets/img/clients/logos.json"), encoding="utf-8"))
def logo_tile(k, v, eager=False):
    w, h = v["size"]
    style = f' style="background:{v["bg"]}"' if v.get("tone") == "custom" else ""
    tone = " ltile--dark" if v.get("tone") == "dark" else (" ltile--custom" if v.get("tone") == "custom" else "")
    tone += " ltile--fill" if v.get("fit") == "fill" else ""
    clip = f' style="clip-path:{v["clip"]}"' if v.get("clip") else ""  # display-only mask; the approved file is unchanged
    load = ' loading="eager" fetchpriority="low" decoding="async"' if eager else ' loading="lazy"'
    return f'<span class="ltile{tone}"{style}><img src="assets/img/clients/{v.get("src", k + ".webp")}" alt="{v["label"]}" width="{w}" height="{h}"{load}{clip}></span>'
def _dup(r):  # visual clones for the seamless loop: hidden from assistive tech and from reduced motion
    r = r.replace(' loading="eager" fetchpriority="low" decoding="async"', ' loading="lazy"')
    return re.sub(r' alt="[^"]*"', ' alt=""', r.replace('<span class="ltile', '<span aria-hidden="true" class="dup ltile'))
def logos_rail(title="علامات تجارية عملنا معها", sub="عملاء في السعودية والإمارات والأردن وفلسطين ومصر."):
    if THEME: return f"[[logos_rail|{sub}]]"
    items = list(_LOGOS.items())
    half = (len(items) + 1) // 2
    r1 = "".join(logo_tile(k, v, eager=True) for k, v in items[:half])  # clipped by the rail, so lazy-loading would leave blank tiles
    r2 = "".join(logo_tile(k, v, eager=True) for k, v in items[half:])
    return f"""<section class="logos" aria-labelledby="h-logos">
  <div class="container logos__head"><span class="label">TRUSTED BY</span><h2 id="h-logos">{title}</h2><p class="muted">{sub}</p>
    <button type="button" class="motion-toggle">إيقاف الحركة</button></div>
  <div class="logo-rail"><div class="logo-track">{r1}{_dup(r1)}{_dup(r1)}</div></div>
  <div class="logo-rail logo-rail--rev"><div class="logo-track">{r2}{_dup(r2)}{_dup(r2)}</div></div>
</section>"""
def logos_static():
    if THEME: return "[[logo_wall]]"
    return '<div class="logo-wall">' + "".join(logo_tile(k, v) for k, v in _LOGOS.items()) + "</div>"

def founder_block(section_cls="section section--dark grain", heading="المؤسس.", photo="founder-bw"):
    return f"""<section class="{section_cls}" id="founder">
  {grid_lines("c")}
  <div class="container founder">
    <div class="founder__card founder__card--photo reveal">
      <img class="founder__photo" src="assets/img/brand/{photo}.webp" alt="د. نور الدين أبو علّان — المؤسس والرئيس التنفيذي لـ MKN ARABIA" width="640" height="714" loading="lazy">
      <div class="glass">
        <span class="label" style="color:var(--ink)">CEO &amp; FOUNDER</span>
        <h3>د. نور الدين أبو علّان</h3>
        <div class="en">DR. NOUREDDIN ABUALLAN</div>
      </div>
    </div>
    <div class="reveal">
      <span class="label">LEADERSHIP</span>
      <h2 style="font-size:clamp(28px,3.6vw,42px);margin-top:14px">{heading}</h2>
      <blockquote class="quote">{FOUNDER_QUOTE}</blockquote>
      <p style="font-size:17px">{FOUNDER_BIO}</p>
      <div class="hero__actions" style="margin-top:24px">
        <a {BOOK_A} class="btn btn--blue">احجز استشارة مجانية</a>
        <a href="about.html#method" class="btn {"btn--line" if "dark" in section_cls else "btn--ghost"}">تعرّف على طريقة عملنا</a>
      </div>
      <p class="founder__note">الاستشارة المجانية مع د. نور الدين مباشرة · <a href="https://www.linkedin.com/in/noureddinabuallan" target="_blank" rel="noopener">الملف الشخصي على LinkedIn</a></p>
    </div>
  </div>
</section>"""
FOUNDER_HOME = founder_block()

def insight_cards(items):
    return "".join(f"""<a href="insights/{a["slug"]}.html" class="cell spot reveal icard"><span class="label" aria-hidden="true">{a["topic"]}</span><span class="go" aria-hidden="true">←</span><h3>{a["title"]}</h3><p>{a["desc"]}</p><span class="more">اقرأ المقال · {ar_minutes(read_min(a))}</span></a>""" for a in items)
def ar_minutes(n):
    return {1: "دقيقة واحدة", 2: "دقيقتان"}.get(n, f"{n} دقائق" if n <= 10 else f"{n} دقيقة")
def read_min(a):
    words = len(re.sub(r"<[^>]+>", " ", a["lead"] + " ".join(" ".join(ps) for _, ps in a["sections"])).split())
    return max(1, round(words / 200))

# brand → client-logo file (only where the owner supplied a logo)
TLOGO = {"Les Sènes Spa": "les-senes", "OSUS Events": "osus", "Kyan Real Estate": "kyan", "Mireva Group": "mireva",
         "Aqua Software": "aqua", "Aqua Software — Egypt": "aqua", "Artimal Gifts": "artimal", "Bright Smile Dental": "bright-smile",
         "Islam Salon": "islam-salon", "Mix Grill / Grand Mix": "mix-grill", "Tabiq Lahem": "tabiq-lahem",
         "Ayoub Dental Clinic": "ayoub", "Fitness Times": "fitness-times", "E SPA Dubai": "e-spa",
         "مطعم أبناء الشيخ": "abnaa-alsheikh"}
def tavatar(brand):
    k = TLOGO.get(brand)
    if k:
        v = _LOGOS[k]
        tone = " tlogo--dark" if v.get("tone") == "dark" else ""
        tone += " tlogo--fill" if v.get("fit") == "fill" else ""
        bg = f' style="background:{v["bg"]}"' if v.get("tone") == "custom" else ""
        clip = f' style="clip-path:{v["clip"]}"' if v.get("clip") else ""
        return f'<span class="tlogo{tone}"{bg}><img src="assets/img/clients/{v.get("src", k + ".webp")}" alt="" loading="lazy" width="{v["size"][0]}" height="{v["size"][1]}"{clip}></span>'
    letter = html.unescape(brand).strip()[0]
    return f'<span class="tlogo tlogo--mono" aria-hidden="true">{letter}</span>'
def tcard(t, extra=""):
    ltr = ' dir="ltr"' if t["country"] == "uk" else ""
    cname = next(n for c, n, _ in COUNTRIES if c == t["country"])
    place = t["place"] or cname
    link = f'<a href="work.html#{t["case"]}" class="tlink">دراسة الحالة</a>' if t["case"] else ""
    en = '<span class="tlang">بالإنجليزية</span>' if ltr else ""
    return f"""<figure class="cell tcard reveal{extra}"><span class="tmark" aria-hidden="true">”</span><blockquote{ltr}>{t["text"]}</blockquote><figcaption>{tavatar(t["brand"])}<span class="tby"><b>{t["brand"]}</b><span>{place}</span></span>{en}{link}</figcaption></figure>"""
FEATURED = [t for t in TESTIMONIALS if t["featured"]]
N_BRANDS = len({re.sub(r"\s*—.*$", "", t["brand"]) for t in TESTIMONIALS})
BRANDS_N = "[[brands_count]]" if THEME else str(N_BRANDS)
TESTI_N = "[[testimonials_count]]" if THEME else str(len(TESTIMONIALS))
CASES_N = "[[cases_count]]" if THEME else str(len(CASES))
FEATURED_CARDS = "[[testimonials_featured]]" if THEME else "".join(tcard(t) for t in FEATURED)
TESTI_HOME = f"""<section class="section section--aura">
  <div class="container">
    <div class="heading heading--row">
      <div>
        <span class="label">CLIENT VOICES</span>
        <h2 id="h-voices">آراء العملاء.</h2>
        <p>تجارب أصحاب الأعمال الذين عملنا معهم في السعودية والإمارات والأردن وفلسطين ومصر، منشورة بموافقتهم.</p>
      </div>
      <a href="testimonials.html" class="btn btn--dark arrow">كل الآراء ({TESTI_N}) </a>
    </div>
    {SWIPE_HINT}<div class="grid g3 swipe" data-lb="h-voices">{FEATURED_CARDS}</div>
  </div>
</section>"""

INSIGHTS_HOME = f"""<section class="section section--white">
  <div class="container">
    <div class="heading heading--row">
      <div>
        <span class="label">INSIGHTS</span>
        <h2 id="h-insights">مقالات لأصحاب الأعمال.</h2>
        <p>أدلة عملية عن اختيار الشريك التسويقي، والبحث المحلي، وقراءة نتائج الإعلانات بواقعية.</p>
      </div>
      <a href="insights.html" class="btn btn--dark arrow">كل المقالات </a>
    </div>
    {SWIPE_HINT}<div class="grid g3 swipe" data-lb="h-insights">{"[[insights_latest|3]]" if THEME else insight_cards(ARTICLES)}</div>
  </div>
</section>"""

FCASES_HTML = """      <a href="work.html#les-senes" class="fcase reveal"><img src="assets/img/work/les-senes.webp" alt="Les Sènes Spa — مادة حملة" loading="lazy" width="671" height="900"><div class="glass"><span class="label">CASE 01</span><h3>Les Sènes Spa</h3><p>محتوى وإعلانات وFresha وظهور محلي في رحلة حجز واحدة</p></div></a>
      <a href="work.html#beautiful-shine" class="fcase reveal"><img src="assets/img/work/beautiful-shine.webp" alt="Beautiful Shine — مادة حملة" loading="lazy" width="675" height="900"><div class="glass"><span class="label">CASE 02</span><h3>Beautiful Shine</h3><p>محتوى وحضور وإعلانات وتقارير أداء مترابطة</p></div></a>
      <a href="work.html#cryo" class="fcase reveal"><img src="assets/img/work/cryo.webp" alt="CRYO Infinity Jeddah" loading="lazy" width="675" height="900"><div class="glass"><span class="label">CASE 03</span><h3>CRYO Infinity Jeddah</h3><p>مسار واحد نحو الحجز عبر Fresha</p></div></a>"""
FCASES = "      [[feature_cases]]" if THEME else FCASES_HTML
# entry by business type → the matching integrated solution + similar cases
BIZ = [
 ("مراكز التجميل والعافية والعيادات", "BEAUTY · WELLNESS · CLINICS", "محتوى وإعلانات وظهور محلي ومسار حجز واحد.", "x06", "نمو أعمال الخدمات", [("les-senes", "Les Sènes Spa"), ("cryo", "CRYO Infinity")]),
 ("الفعاليات والشركات B2B", "EVENTS · B2B", "تموضع مؤسسي ومحتوى ومتابعة تخاطب صنّاع القرار.", "x05", "توليد طلب الشركات", [("osus", "OSUS Events"), ("imperio", "IMPERIO Events")]),
 ("علامة جديدة أو إعادة تموضع", "NEW BRAND · REBRAND", "فلسفة العلامة وتموضعها وهويتها ووجهة الإطلاق.", "x01", "إطلاق علامة", [("sandouka", "Sandouka Coffee"), ("bud-studio", "BU’D Studio")]),
 ("العقارات", "REAL ESTATE", "تقديم المشاريع ومحتوى وحملات تستقطب الجمهور المناسب.", "x03", "نمو الأداء", [("kyan", "Kyan Real Estate")]),
 ("الأنظمة والأتمتة والذكاء الاصطناعي", "SYSTEMS · AUTOMATION · AI", "تنظيم المتابعة والعمليات ونماذج تقنية قابلة للاختبار.", "x07", "التقنية والأتمتة", [("mireva", "Mireva AI"), ("restaurant-ops", "Restaurant Ops")]),
]
biz_cells = "".join(f"""<div class="cell spot reveal biz"><span class="label">{en}</span><h3>{t}</h3><p>{d}</p>
  <a class="biz__main" href="pricing.html#{x}">الحل المناسب: {xn} ←</a>
  <div class="biz__cases"><span>أعمال مشابهة:</span> {" · ".join(f'<a href="work.html#{cid}">{cn}</a>' for cid, cn in cs)}</div></div>""" for t, en, d, x, xn, cs in BIZ)

home = f"""<section class="hero grain">
  {grid_lines("a")}
  <div class="container hero__grid">
    <div>
      <span class="chip"><span class="dot"></span>وكالة تسويق رقمي<span class="chip__en"> · BUILD · SCALE · GROW</span></span>
      <h1>نمو أعمالك يحتاج <span class="blk">منظومة</span> متكاملة، <span class="nowrap">لا خدمات متفرقة<span class="dot">.</span></span></h1>
      <p class="lead lead--full">في MKN ARABIA نربط الاستراتيجية والهوية والمحتوى والإعلانات والتقنية والقياس داخل خطة واحدة تساعدك على اكتساب عملاء أكثر جدية، وتحسين التجربة الرقمية، وتطوير عملياتك.</p>
      <p class="lead lead--short">استراتيجية، هوية، محتوى، إعلانات، تقنية وقياس — في خطة واحدة تجلب لك عملاء أكثر جدية.</p>
      <div class="hero__actions">
        <a {BOOK_A} class="btn btn--blue">احجز استشارة مجانية</a>
        <a href="#" data-wa class="btn btn--line">تحدث معنا عبر واتساب</a>
      </div>
      <p class="hero__note">30 دقيقة مع المؤسس عبر Google Meet · مجانية · دون أي التزام</p>
      <div class="hero__meta">
        <div class="glass"><span class="label">MARKETS</span>السعودية · الإمارات · الأردن · فلسطين · مصر</div>
        <div class="glass"><span class="label">TRUSTED BY</span>{BRANDS_N} علامة تجارية · شراكات مستمرة منذ 2023</div>
      </div>
    </div>
    <div class="stage" aria-hidden="true">
      <div class="stage__photo"><img src="assets/img/brand/campaign-tablet.webp" alt="" width="688" height="864" fetchpriority="high"></div>
      <div class="glass stage__card stage__card--b"><span class="label">SLOGAN</span><div class="slogan" style="font-size:24px">سوّق بالعربي، سوّق صح</div></div>
      <div class="glass stage__card stage__card--a"><span class="label">ONE SYSTEM</span><div style="font-weight:600;color:#fff;margin-top:4px">استراتيجية · إبداع · أداء · تقنية</div></div>
    </div>
  </div>
</section>

{logos_rail()}

<div class="marquee" aria-hidden="true"><div class="marquee__track">{marquee}</div></div>

<section class="section section--dark grain" id="work">
  {grid_lines("a")}
  <div class="container">
    <div class="heading heading--row">
      <div>
        <span class="label">SELECTED WORK · {CASES_N} CASES</span>
        <h2 style="color:#fff" id="h-work">أعمال مختارة.</h2>
        <p>قصص عمل من قطاعات مختلفة، تُعرض بموافقة أصحابها.</p>
      </div>
      <a href="work.html" class="btn btn--line arrow">كل الأعمال </a>
    </div>
    {SWIPE_HINT}<div class="feature-cases swipe" data-lb="h-work">
{FCASES}
    </div>
    <p class="windex__h">حالات أخرى</p>
    <div class="windex">{"[[case_index]]" if THEME else windex}</div>
    <div class="inline-cta glass reveal">
      <p><b>شاهدت أعمالنا؟</b> لنتحدث عن نشاطك في استشارة مجانية مدتها 30 دقيقة.</p>
      <div class="hero__actions"><a {BOOK_A} class="btn btn--blue">احجز استشارة مجانية</a><a href="#" data-wa="مرحباً MKN ARABIA، شاهدت أعمالكم وأرغب بمناقشة نشاطي" class="btn btn--line">واتساب</a></div>
    </div>
  </div>
</section>

<section class="section section--white" id="by-business">
  {grid_lines("c")}
  <div class="container">
    <div class="heading">
      <span class="label">BY BUSINESS TYPE</span>
      <h2 id="h-biz">ابدأ من نوع نشاطك.</h2>
      <p>اختر الأقرب لنشاطك لترى الحل المناسب وأعمالًا مشابهة.</p>
    </div>
    {SWIPE_HINT}<div class="grid biz-grid swipe" data-lb="h-biz">{biz_cells}</div>
  </div>
</section>

<section class="section section--diff-l">
  <div class="container">
    <div class="heading heading--row">
      <div>
        <span class="label">SERVICE MAP · D01–D08</span>
        <h2 id="h-map">ثمانية مجالات خدمة لنمو أعمالك.</h2>
        <p style="color:var(--ink)">نختار الخدمات حسب احتياج العمل، ونفصل أتعاب التنفيذ عن ميزانيات الإعلان وتكاليف الأدوات؛ فتعرف ما تدفعه مقابل العمل، وما تدفعه للمنصات والموردين.</p>
      </div>
      <a href="services.html" class="btn btn--dark arrow">كل الخدمات </a>
    </div>
    {SWIPE_HINT}<div class="grid g4 swipe" data-lb="h-map">{dept_cells}</div>
  </div>
</section>

<section class="section section--dark grain">
  {grid_lines("b")}
  <div class="container capmap">
    <div>
      <div class="heading" style="margin-bottom:32px">
        <span class="label">CAPABILITY SYSTEM</span>
        <h2 id="h-axes">أربعة محاور، هدف تجاري واحد.</h2>
        <p>تتكامل المحاور على مسار يبدأ من السياق التجاري ويمر بالهوية والمحتوى والاستقطاب والتجربة والقياس والتحسين. لا يحتاج كل عميل إلى كل محور بالعمق نفسه؛ نختار نقطة البداية وفق الأدلة والموارد والهدف.</p>
      </div>
      {SWIPE_HINT}<div class="grid g2 swipe" data-lb="h-axes">{axes_html}</div>
      <a href="about.html#method" class="btn btn--line arrow" style="margin-top:24px">منهجية العمل </a>
    </div>
    {orbit()}
  </div>
</section>

{TESTI_HOME}

{FOUNDER_HOME}

<section class="section slogan-sec">
  {grid_lines("c")}
  <div class="container">
    <div class="heading heading--row" style="margin-bottom:0">
      <div>
        <span class="label">OUR VOICE</span>
        <h2 class="sr-only" id="h-voice">سوّق بالعربي، سوّق صح</h2>
        <p class="slogan-big" aria-hidden="true">سوّق بالعربي،<br><span class="sky">سوّق صح.</span></p>
      </div>
      <p class="muted" style="max-width:380px;font-size:18px">نبني رسائل ومواد تراعي لغة العميل والسياق المحلي والعرض التجاري وسلوك الاكتشاف والشراء في المنطقة.</p>
    </div>
    {SWIPE_HINT}<div class="portraits swipe" data-lb="h-voice">{portraits}</div>
  </div>
</section>

{INSIGHTS_HOME}

{CTA}"""
ORG = "https://mknarabia.com/#org"
ORG_LD = json.dumps({
  "@context": "https://schema.org", "@type": "Organization", "@id": ORG, "name": "MKN ARABIA",
  "url": "https://mknarabia.com/", "logo": "https://mknarabia.com/assets/img/logo-dark.png",
  "slogan": "سوّق بالعربي، سوّق صح", "email": "contact@mknarabia.com",
  "founder": {"@type": "Person", "@id": "https://mknarabia.com/#founder", "name": "Noureddin Abuallan", "alternateName": "د. نور الدين أبو علّان",
              "honorificPrefix": "Dr.", "jobTitle": "CEO & Founder", "image": "https://mknarabia.com/assets/img/brand/founder-sq.jpg",
              "url": "https://mknarabia.com/about.html#founder", "sameAs": ["https://www.linkedin.com/in/noureddinabuallan"]},
  "address": {"@type": "PostalAddress", "addressCountry": "JO"},
  "areaServed": ["SA", "AE", "JO", "PS", "EG"],
  "sameAs": ["https://instagram.com/mknarabia", "https://facebook.com/mknarabia", "https://linkedin.com/company/mknarabia"],
  "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "telephone": "+201140552627", "email": "contact@mknarabia.com", "availableLanguage": ["ar", "en"],
                   "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}}
}, ensure_ascii=False)
SITE_LD = json.dumps({"@context": "https://schema.org", "@type": "WebSite", "@id": "https://mknarabia.com/#website", "name": "MKN ARABIA",
                      "url": "https://mknarabia.com/", "inLanguage": "ar", "publisher": {"@id": ORG}}, ensure_ascii=False)
page("index.html", "وكالة تسويق رقمي للسعودية والخليج | MKN ARABIA",
     "استراتيجيات تسويق، بناء علامات تجارية، إعلانات مدفوعة، مواقع وأنظمة CRM وSaaS تساعد الشركات في السعودية والإمارات والمنطقة على بناء نمو رقمي قابل للقياس.",
     "./", home, head_extra=f'\n<script type="application/ld+json">{ORG_LD}</script>\n<script type="application/ld+json">{SITE_LD}</script>')

# ===================== CROSS-LINKS (cases ↔ services ↔ solutions ↔ articles) =====================
CASE_LINKS = {"les-senes": (["d03", "d04", "d06"], "x06"), "beautiful-shine": (["d03", "d04", "d06"], "x06"), "cryo": (["d05", "d06"], "x06"),
              "bud-studio": (["d02"], "x01"), "sandouka": (["d01", "d02"], "x01"), "osus": (["d02", "d03"], "x05"), "imperio": (["d02"], "x01"),
              "mireva": (["d08"], "x08"), "restaurant-ops": (["d07", "d08"], "x07"), "kyan": (["d03", "d04"], "x03")}
CASE_NAME = {cid: n for cid, n, _ in CASES}
DEPT_BY_KEY = {d["code"].lower(): d for d in DEPTS}
BUNDLE_NAME = {x.lower(): t for x, t, *_ in BUNDLES}
DEPT_CASES = {}
SVC_SLUG = {"d01": "growth-strategy", "d02": "branding", "d03": "content", "d04": "paid-ads", "d05": "websites", "d06": "seo-geo", "d07": "crm-automation", "d08": "custom-software"}
for _cid, (_ds, _x) in CASE_LINKS.items():
    for _k in _ds: DEPT_CASES.setdefault(_k, []).append(_cid)
ART = {a["slug"]: a for a in ARTICLES}
DEPT_READ = {"d04": ART["meta-ads-metrics-vs-real-revenue"], "d06": ART["seo-google-business-gcc-service-brands"]}
def case_links(key, limit=3):
    return " · ".join(f'<a href="work.html#{c}">{CASE_NAME[c]}</a>' for c in DEPT_CASES.get(key, [])[:limit])

# ===================== SERVICES =====================
rows = ""
for d in DEPTS:
    key = d["code"].lower()
    subs = "".join(f'<div><span class="label">{en}</span><b>{t}</b><p>{s}</p></div>' for t, en, s in d["subs"])
    work_row = f'<div><b>من أعمالنا في هذا المجال</b><span>{case_links(key)}</span></div>' if key in DEPT_CASES else ""
    read = DEPT_READ.get(key)
    read_row = f'<div><b>اقرأ</b><span><a href="insights/{read["slug"]}.html">{read["title"]}</a></span></div>' if read else ""
    rows += f'''<article class="dept glass glass--light reveal" id="{key}">
  <div>
    <div class="dept__code">{d["code"]}</div>
    <span class="label label--muted">{d["axis"]}</span>
    <h2 id="h-{key}">{d["t"]}</h2>
    <p class="muted">{d["lead"]}</p>
    <div class="dept__meta">
      <div><b>العميل المناسب</b><span>{d["fit"]}</span></div>
      <div><b>المشكلة</b><span>{d["prob"]}</span></div>
      <div><b>قياس النجاح</b><span>{d["measure"]}</span></div>
      {work_row}{read_row}
    </div>
    <div class="hero__actions" style="margin-top:28px">
      <a href="services/{SVC_SLUG[key]}.html" class="btn btn--dark btn--sm">تفاصيل الخدمة</a>
      <a href="pricing.html#{key}" class="btn btn--ghost btn--sm">الباقات وعرض السعر</a>
    </div>
  </div>
  <div>
    <span class="label label--muted">{len(d["subs"]):02d} SERVICES · DEFINED DELIVERABLES</span>
    <p class="swipe-hint subs-hint" aria-hidden="true">اسحب لعرض كل الخدمات</p>
    <div class="subs swipe" style="margin-top:14px" data-lb="h-{key}">{subs}</div>
    <p class="note"><span><b>{d["special_label"]}:</b> {d["special"]}</span></p>
  </div>
</article>'''

services = page_hero("SERVICE MAP · D01–D08", "خدمات التسويق الرقمي: ثمانية مجالات، مخرجات محددة.",
  "ثمانية مجالات خدمة، لكل منها مخرجات وكميات وحدود واضحة. التهيئات التقنية المتقدمة والمتاجر والأنظمة والذكاء الاصطناعي تُقدّم كحلول بعد دراسة الاحتياج.", actions=True) + f'''
<section class="section section--dark grain">
  {grid_lines("c")}
  <div class="container">
    <div class="heading">
      <span class="label">PROBLEMS WE SOLVE</span>
      <h2 style="color:#fff">مشكلات نسمعها كثيرًا، وكيف نعالجها.</h2>
      <p>سبع مشكلات يواجهها أصحاب الأعمال، وما نفعله لكل منها، وما تحصل عليه في النهاية.</p>
    </div>
    <table class="ptable reveal">
      <thead><tr><th>PROBLEM · المشكلة</th><th>WHAT WE DO · ما نفعله</th><th>YOU GET · ما تحصل عليه</th></tr></thead>
      <tbody>{prob_rows}</tbody>
    </table>
  </div>
</section>
<section class="section section--aura section--jump">
  <div class="container">
    <h2 class="sr-only">مجالات الخدمة الثمانية</h2>
    <nav class="jump glass glass--light" aria-label="مجالات الخدمة">{"".join(f'<a href="#{d["code"].lower()}"><span class="label">{d["code"]}</span>{d["short"]}</a>' for d in DEPTS)}</nav>
    {rows}
  </div>
</section>
{CTA}'''
page("services.html", "خدمات التسويق الرقمي: استراتيجية، إعلانات، مواقع وCRM | MKN ARABIA",
     "ثمانية مجالات بمخرجات محددة: الاستراتيجية، الهوية، المحتوى، الإعلانات، المواقع، البحث والقياس، CRM والأتمتة، والأنظمة المخصصة.",
     "services.html", services)

# ===================== PACKAGES / QUOTE =====================
WA_ICON = WA_SVG.replace('<svg ', '<svg class="ico" ')
def tier_html(d, i, tr):
    ar, en, price, unit, setup, goal, spec = tr
    lis = "".join(f'<li><span>{k}</span>{v}</li>' for k, v in spec)
    hl = " tier--hl" if i == 1 else ""
    pid = f'{d["code"]}-{en}'
    name = f'{d["code"]} {d["short"]} — باقة {ar}'
    btn = "btn--blue" if i == 1 else "btn--dark"
    return f"""<div class="tier cell spot{hl}">
  <div class="tier__name"><h3>{ar}</h3><span class="label">{en}</span></div>
  <div class="unit" style="margin-top:6px">{unit_label(unit, setup)}</div>
  <p class="goal">{goal}</p>
  <ul class="spec">{lis}</ul>
  <a href="#" class="btn {btn}" style="margin-top:22px" data-wa="مرحباً MKN ARABIA، أرغب بعرض سعر لـ {name}" data-quote="{pid}" data-quote-name="{name}" data-dept="{d["code"]}">{WA_ICON}اطلب عرض سعر</a>
</div>"""

def unit_label(unit, setup):
    u = {"مشروع": "مشروع محدد", "شهريًا": "دورة شهرية", "مرحلة دراسة": "مرحلة دراسة", "مرحلة تجريبية": "مرحلة تجريبية",
         "مرحلة تطوير": "مرحلة تطوير", "مشروع مشروط": "مشروع مشروط بدراسة جدوى"}.get(unit, unit)
    return u + (" · + رسوم إعداد لمرة واحدة" if setup else "")

tabs = ""; panels = ""
for k, d in enumerate(DEPTS):
    c = d["code"]; key = c.lower()
    tabs += f'<button type="button" class="tab" role="tab" id="tab-{key}" data-key="{key}" aria-controls="panel-{key}" aria-selected="{"true" if k == 0 else "false"}" tabindex="{0 if k == 0 else -1}"><span class="label">{c}</span>{d["short"]}</button>'
    ts = "".join(tier_html(d, i, tr) for i, tr in enumerate(TIERS[c]))
    ex = case_links(key, 2)
    more = (f'مثال من أعمالنا: {ex} · ' if ex else "") + f'<a href="services.html#{key}">تفاصيل خدمات {d["short"]} ←</a>'
    panels += f"""<div class="panel" role="tabpanel" id="panel-{key}" aria-labelledby="tab-{key}" tabindex="0"{"" if k == 0 else " hidden"}>
  {SWIPE_HINT}<div class="grid g3 swipe" data-lb="tab-{key}">{ts}</div>
  <p class="note"><span><b>{d["special_label"]}:</b> {d["special"]}</span></p>
  <p class="panel__more">{more}</p>
</div>"""

bundles_html = "".join(f"""<div class="bundle cell spot reveal" id="{x.lower()}">
  <span class="label">{x}</span>
  <h3>{t}</h3><div class="en">{en}</div>
  <p>{desc}</p>
  <div class="time">المدة: {time}</div>
  <div class="money"><a href="#" class="btn btn--light btn--sm" data-wa="مرحباً MKN ARABIA، أرغب بعرض سعر للحل المتكامل {x} — {t}" data-quote="{x}" data-quote-name="{x} {t}" data-dept="BUNDLE">{WA_ICON}اطلب عرض سعر</a></div>
</div>""" for x, t, en, desc, money, time in BUNDLES)

QUOTE_STEPS = [("أرسل احتياجك", "الهدف، والسوق، والموعد، والميزانية، والأصول المتاحة."),
               ("نراجع ونوصي", "نحدد الباقة أو الحل المناسب، والكميات والمدخلات المطلوبة."),
               ("عرض مخصص", "المخرجات، والمراحل، وجولات التعديل، والأتعاب، وجدول الدفع."),
               ("اعتماد وبدء", "يبدأ التنفيذ بعد اعتماد العرض واكتمال متطلبات البدء.")]
quote_steps_html = "".join(f'<div class="cell reveal"><h3>{t}</h3><p>{d}</p></div>' for t, d in QUOTE_STEPS)
ENGAGE = [("01 · FOUNDATION", "تأسيس", "مشروع محدد لبناء أساس: تدقيق أو هوية أو وجهة أو وثيقة عملية. ينتهي بالمخرج ومحضر تسليم."),
          ("02 · GROWTH", "نمو", "تشغيل دوري أو مشروع أوسع يربط المحتوى والاستقطاب والتجربة والقياس."),
          ("03 · SCALE", "توسع", "نطاق أكثر اتصالًا أو مرحلة تقنية مشروطة بدراسة، مع حوكمة أو تقارير أو تكاملات إضافية.")]
engage_html = "".join(f'<div class="cell reveal"><span class="label">{a}</span><h3>{t}</h3><p>{d}</p></div>' for a, t, d in ENGAGE)
_TB = {t["brand"]: t for t in TESTIMONIALS}
def proof_strip(brands, heading="أصحاب أعمال وثقوا بنا", cls="section section--white"):
    quotes = f"[[proof_quotes|{','.join(brands)}]]" if THEME else "".join(tcard(_TB[b]) for b in brands)
    return f"""<section class="{cls} proof">
  <div class="container">
    <div class="heading heading--row">
      <div><span class="label">TRUSTED BY</span><h2>{heading}</h2><p>{BRANDS_N} علامة تجارية في السعودية والإمارات والأردن وفلسطين ومصر.</p></div>
      <a href="work.html" class="btn btn--dark arrow">أعمالنا </a>
    </div>
    {logos_static()}
    <div class="grid g2" style="margin-top:20px">{quotes}</div>
  </div>
</section>"""

pricing = page_hero("PACKAGES · CUSTOM QUOTE", "الباقات وطلب عرض السعر.",
  "8 مجالات · 24 باقة · 8 حلول متكاملة. اختر ما يناسب احتياجك واطلب عرض سعر؛ نراجع النطاق ونرسل لك عرضًا مخصصًا بالمخرجات والمدة والأتعاب.", actions=True) + f"""
<section class="section section--aura section--jump" id="packages">
  <div class="container">
    <div class="heading">
      <span class="label">24 PACKAGES</span>
      <h2 id="h-packages">باقات كل مجال.</h2>
      <p>أسماء «تأسيس» و«نمو» و«توسع» تصف حجم الاحتياج ومرحلته، لا مستوى الجودة. اختر المجال لعرض الهدف والمخرجات والمدة لكل باقة.</p>
    </div>
    <div class="grid g3 engage swipe" data-lb="h-packages">{engage_html}</div>
    <div class="tabs glass glass--light" role="tablist" id="dept-tabs" aria-label="مجالات الباقات">{tabs}</div>
    {panels}
    <p class="form-note quote-note">{WA_ICON}أزرار «اطلب عرض سعر» تفتح واتساب برسالة جاهزة باسم الباقة · نرد خلال يوم عمل.</p>
    <div class="help-strip glass glass--light reveal">
      <div><b>لست متأكدًا أي باقة تناسبك؟</b><p>في استشارة مجانية مدتها 30 دقيقة نرشّح لك الباقة والنطاق المناسبين.</p></div>
      <div class="hero__actions"><a {BOOK_A} class="btn btn--dark">احجز استشارة مجانية</a><a href="contact.html#contact-form" class="btn btn--ghost">أو أرسل احتياجك عبر النموذج</a></div>
    </div>
  </div>
</section>

{proof_strip(["Les Sènes Spa", "OSUS Events"])}

<section class="section section--diff-d grain" id="bundles">
  <div class="container">
    <div class="heading">
      <span class="label">INTEGRATED BUNDLES · X01–X08</span>
      <h2 style="color:#fff" id="h-bundles">الحلول المتكاملة.</h2>
      <p>ثمانية حلول تجمع أكثر من مجال في نطاق واحد، لإطلاق العلامات ونمو الأداء والتجارة والخدمات والتحول الرقمي.</p>
    </div>
    <div class="grid g4 swipe" data-lb="h-bundles">{bundles_html}</div>
  </div>
</section>

<section class="section section--dark grain" id="quote">
  <div class="container">
    <div class="heading">
      <span class="label">CUSTOM QUOTE</span>
      <h2 style="color:#fff">كيف يصلك عرض السعر.</h2>
      <p>تثبت الأتعاب في عرض مخصص بعد اعتماد النطاق. الإنفاق الإعلاني والضرائب والتراخيص والاشتراكات منفصلة ما لم ترد كبند صريح.</p>
    </div>
    <div class="grid g4 steps">{quote_steps_html}</div>
    <h3 class="subhead" id="h-types">أنواع التعاقد</h3>
    <div class="grid g4 swipe" data-lb="h-types">
      <div class="cell reveal"><span class="label">PROJECT</span><h3>مشروع</h3><p>مخرج محدد ومحضر تسليم.</p></div>
      <div class="cell reveal"><span class="label">MONTHLY</span><h3>شهري</h3><p>دورة تشغيل بكميات محددة.</p></div>
      <div class="cell reveal"><span class="label">ONE-OFF SETUP</span><h3>إعداد لمرة واحدة</h3><p>يُدفع مرة واحدة قبل التشغيل.</p></div>
      <div class="cell reveal"><span class="label">PHASE</span><h3>مرحلة</h3><p>دراسة أو تجربة أو تطوير.</p></div>
    </div>
    <h3 class="subhead">شروط أساسية</h3>
    <ul class="grid g2">
      <li class="cell reveal"><h3>جولات التعديل</h3><p>جولتان للمشاريع، وجولة مجمعة لكل دفعة محتوى أو دورة شهرية.</p></li>
      <li class="cell reveal"><h3>الإنفاق الإعلاني</h3><p>يدفعه العميل للمنصة مباشرة، ولا يدخل ضمن أتعابنا.</p></li>
      <li class="cell reveal"><h3>المدد</h3><p>تقديرية وتبدأ بعد اكتمال المدخلات والوصول والدفعة المتفق عليها.</p></li>
      <li class="cell reveal"><h3>النتائج</h3><p>MKN ARABIA مسؤولة عن المخرجات والقياس المتفق عليه، ولا تضمن مبيعات أو حجوزات أو ترتيبًا لم تثبت في اختبار محدد.</p></li>
    </ul>
    <div class="hero__actions" style="margin-top:36px">
      <a href="#" data-wa="مرحباً MKN ARABIA، أرغب بعرض سعر مخصص" data-quote="GENERAL" data-quote-name="عرض سعر مخصص" data-dept="GENERAL" class="btn btn--blue">اطلب عرضًا مخصصًا عبر واتساب</a>
      <a href="contact.html#contact-form" class="btn btn--line">أرسل تفاصيل مشروعك</a>
    </div>
  </div>
</section>
{CTA}"""
page("pricing.html", "باقات التسويق الرقمي وطلب عرض سعر مخصص | MKN ARABIA", "24 باقة في 8 مجالات و8 حلول متكاملة من MKN ARABIA — اختر ما يناسبك واطلب عرض سعر مخصص.", "pricing.html", pricing)

# ===================== WORK =====================
NO_NUMBERS = {  # owner decision: revenue/platform figures are not published
  "les-senes": "", "beautiful-shine": "", "cryo": "",
  "osus": "طبيعة النتائج: علامة مؤسسية متماسكة وحضور رقمي يدعم تواصل OSUS مع الشركات وصنّاع القرار في قطاع الفعاليات.",
}
TESTI_BY_CASE = {t["case"]: t for t in TESTIMONIALS if t["case"]}
def testi_html(t):
    ltr = ' dir="ltr"' if t["country"] == "uk" else ""
    return f"""<figure class="tquote"><blockquote{ltr}>{t["text"]}</blockquote><figcaption><b>{t["brand"]}</b>{f"<span>{t['place']}</span>" if t["place"] else ""}</figcaption></figure>"""

CASES_DATA = []
def full_case(cid, idx, name, sub, img, ch, role, done, out, stats=None, src="", reading="", wide=False, tile=None):
    if cid in NO_NUMBERS:
        stats, src, reading = None, "", NO_NUMBERS[cid]
    CASES_DATA.append(dict(slug=cid, name=name, sub=sub.replace(" — ", " · "), image=(f"clients/{img}.webp" if tile else f"work/{img}.webp"),
                           tile=tile or "", wide=bool(wide), challenge=ch, role=role, done=done, outputs=out, reading=reading,
                           depts=CASE_LINKS[cid][0], bundle=CASE_LINKS[cid][1]))
    st = ""
    if stats:
        st = '<div class="stats">' + "".join(f'<div><b class="{"hi" if hi else ""}">{v}</b><span>{l}</span></div>' for v, l, hi in stats) + (f'<div class="src">{src}</div>' if src else "") + "</div>"
    rd = f'<p class="reading">{reading}</p>' if reading else ""
    sub = sub.replace(" — ", " · ")
    if tile:  # logo shown on its brand colour until a real application image exists
        media = f'<div class="case__img case__img--tile" style="background:{tile}"><img src="assets/img/clients/{img}.webp" alt="{e(name)}" loading="lazy"></div>'
    else:
        media = f'<div class="case__img{" case__img--wide" if wide else ""}"><img src="assets/img/work/{img}.webp" alt="{e(name)}" loading="lazy"></div>'
    ds, x = CASE_LINKS[cid]
    rel = " · ".join(f'<a href="services.html#{k}">{DEPT_BY_KEY[k]["short"]}</a>' for k in ds)
    nxt = f'''<div class="case__next">
      <p><b>خدمات مرتبطة:</b> {rel} · <a href="pricing.html#{x}">الحل المتكامل: {BUNDLE_NAME[x]}</a></p>
      <div class="hero__actions"><a href="#" data-wa="مرحباً MKN ARABIA، شاهدت حالة {e(name)} وأرغب بمناقشة مشروع مشابه لنشاطي" class="btn btn--dark btn--sm">ناقش مشروعًا مشابهًا</a><a {BOOK_A} class="btn btn--ghost btn--sm">احجز استشارة مجانية</a></div>
    </div>'''
    return f'''<article class="case glass glass--light reveal{" case--wide" if wide else ""}" id="{cid}">
  {media}
  <div>
    <span class="label">SELECTED WORK · CASE {idx:02d}</span>
    <h2>{name}</h2>
    <p class="sub">{sub}</p>
    <dl>
      <div><dt>التحدي</dt><dd>{ch}</dd></div>
      <div><dt>دورنا</dt><dd>{role}</dd></div>
      <div><dt>ما نفذناه</dt><dd>{done}</dd></div>
      <div><dt>المخرجات</dt><dd>{out}</dd></div>
    </dl>
    {st}{rd}
    {testi_html(TESTI_BY_CASE[cid]) if cid in TESTI_BY_CASE else ""}
    {nxt}
  </div>
</article>'''
cases_html = "".join([
 full_case("les-senes",1,"Les Sènes Spa","الجمال والعافية · شراكة مستمرة منذ نوفمبر 2023","les-senes",
  "أنشطة استقطاب وحجز وقياس تحتاج ربطًا أوضح بين التواصل والزيارة.",
  "استراتيجية رقمية ومحتوى وإعلانات وإدارة حضور وقراءة تقارير ومراجعة تجربة الحجز.",
  "تقرير مالي وإعلاني يفصل مبيعات المركز عن محادثات Meta؛ دليل تواصل وقوالب يربط نوايا العميل بالحجز ويحدد تصعيد الحالات.",
  "تقرير من 9 صفحات؛ دليل تواصل من 30 صفحة؛ تعريفات موحدة لمسار المحادثة والحجز والحضور والقياس.",
  [("1,032,146","ريال إجمالي مبيعات المركز",True),("38,167","ريال إنفاق Meta",False),("2,747","محادثة",False),("13.89","ريال متوسط تكلفة المحادثة",False)],
  "JAN–JUL 2026 · SOURCE: META &amp; FRESHA","قراءة الأرقام: المبيعات إجمالي نشاط المركز، ولا تُنسب إلى الإعلان وحده."),
 full_case("beautiful-shine",2,"Beautiful Shine","الجمال والعافية · أغسطس 2025 – يوليو 2026","beautiful-shine",
  "ربط محتوى الخدمات والإعلان بالاستفسار والحجز، وقياس الأداء على فترات قابلة للمقارنة.",
  "محتوى وحضور وإعلانات وتقارير أداء وقراءة أثر الإدارة.",
  "تقرير أثر إدارة يفصل الفترات المالية بين أنظمة نعيم وFresha وركاز، مع قراءة Meta ومقارنة المتوسطات الشهرية.",
  "تقرير أثر إدارة، جدول فترات غير مكررة، مؤشرات محادثات، توصيات تتبع الحجز.",
  [("17,920.80","متوسط المبيعات الشهري · خط الأساس (يناير–يوليو 2025)",False),("29,168.60","المرحلة الأولى من الإدارة · +62.8%",False),("40,937.23","مرحلة ركاز · +128.4%",True),("2,854","محادثة Meta بإنفاق 29,032.46 ريال · 10.17 ريال للمحادثة",False)],
  "MONTHLY AVERAGE SALES · SAR","قراءة الأرقام: مرحلة ركاز (01-05-2026 حتى 29-07-2026) فترة جزئية تقارب 3 أشهر. تعكس المقارنة أثر فترة الإدارة كاملة، ولا تنسب النمو إلى الإعلان وحده."),
 full_case("cryo",3,"CRYO Infinity Jeddah","العافية والاستشفاء — جدة · تقرير إنجازات يوليو 2026","cryo",
  "قنوات مختلفة تحتاج حضورًا متسقًا وروابط صحيحة ومسارًا واضحًا نحو الحجز.",
  "الحضور والمحتوى والموقع وروابط الحجز والقياس والتقارير.",
  "نقل الموقع وتشغيله وتحديث روابطه، ربط الحجز عبر Fresha، تنظيم روابط الاتصال، تجهيز الحضور الاجتماعي وملف Google المحلي، وتقرير إنجازات.",
  "موقع وروابط حجز، أصول تواصل ومحتوى، ملف حضور محلي، تقرير تنفيذي.",
  [("407","مشاهدات لملف Google",False),("248","تفاعلًا على الملف",False),("23,176.52","ريال مبيعات Fresha شاملة الضريبة (20,153.50 صافي)",True)],
  "JULY 2026 · OPERATING PLATFORMS","أرقام يوليو 2026 من منصات التشغيل، ولا تُنسب المبيعات كلها إلى الإعلان. التطوير المتقدم ثنائي اللغة جزء من خطة المرحلة التالية."),
 full_case("bud-studio",4,"BU’D Studio","العمارة والتصميم الداخلي · 2026","bud-studio",
  "حضور لا يوضح بما يكفي فلسفة التصميم ومستوى الأعمال.","تموضع وحضور رقمي واتجاه إبداعي.",
  "تطوير لغة العرض والتموضع والتقديم الإبداعي للاستوديو، وامتد العمل لاحقًا إلى مشروع Donuttery من خلال الاستوديو.",
  "اتجاه عرض وهوية واتساق رقمي.",reading="طبيعة النتائج: مخرج نوعي في التموضع وطريقة عرض الأعمال."),
 full_case("sandouka",5,"Sandouka Coffee","الأغذية والمشروبات — فلسطين · 2025","sandouka",
  "هوية معاصرة مرتبطة بمعنى العلامة وانتمائها.","فلسفة واستراتيجية وتموضع وهوية واتجاه علامة.",
  "بناء الأساس الاستراتيجي والإبداعي للعلامة، وربط فلسفتها بنظام هوية متكامل.",
  "فلسفة العلامة، الهوية، الاتجاه البصري.",reading="نطاق العمل: مشروع علامة وهوية؛ لم يشمل الموقع أو إدارة الإعلانات."),
 full_case("osus",6,"OSUS Events","الفعاليات B2B · السعودية · 2026","osus",
  "عرض مهني يخاطب المؤسسات وصنّاع القرار.","استراتيجية وهوية وحضور ومحتوى وتوجيه استقطاب B2B.",
  "بناء العلامة وأصولها والحضور الرقمي وتنظيم التواصل المؤسسي.","هوية ودليل وتطبيقات وحضور رقمي ومواد حملات.", tile="#314b48"),
 full_case("imperio",7,"IMPERIO Events","الفعاليات والتجارب — السعودية · 2026 · مشروع مكتمل","imperio-seal",
  "شخصية متميزة ونظام قابل للاستخدام في تطبيقات متعددة.","اكتشاف وتموضع واتجاه هوية وتطبيقات.",
  "مشروع علامة متكامل من الاكتشاف حتى التطبيقات.","هوية ودليل استخدام وتطبيقات.",reading="طبيعة النتائج: مخرج علامة نوعي.", tile="#2a0403"),
 full_case("mireva",8,"Mireva Group / Mireva AI","التقنية والجمال · B2B/B2C · السعودية · 2025–2026","mireva",
  "تحويل إدخال الصور والأسئلة إلى تجربة تحليل ومخرجات مفهومة للمستخدم والمهني.",
  "تصميم وبناء مسارات تحليل الجلد والشعر بالصور، والتقرير والتوصيات، وربط تجربتي B2B وB2C.",
  "بناء واختبار تجربتي تحليل بالصور مع جولات تحسين.","مسارا إدخال وتحليل وعرض نتائج وتوصيات.",
  reading="مرحلة المشروع: بناء واختبار. التحليل أداة مساعدة وليس تشخيصًا طبيًا.", wide=True),
 full_case("restaurant-ops",9,"MKN Restaurant Operations / Delivery","منتج تقني من تطوير MKN ARABIA · سبتمبر 2026","restaurant-ops",
  "تجميع الطلبات والأدوار والحضور وإجراءات التشغيل في تجربة واحدة.","تطوير الواجهة ووظائف الأعمال ضمن مسار MKN التقني.",
  "نظام يجمع الطلبات والكباتن والحضور والرواتب والأدوار، مع ملفات إصدار وتعليمات رفع وتقارير اختبار.",
  "حزمة واجهة ووظائف، ملفات إصدار وخطوات رفع وتقرير اختبار.",
  reading="مرحلة المنتج: نموذج تطوير قابل للتخصيص؛ النشر على خادم إنتاج وتعدد المستخدمين يُبنى حسب احتياج كل مؤسسة.", wide=True),
 full_case("kyan",10,"Kyan Real Estate","العقارات — فلسطين · شراكة منذ يوليو 2024","kyan",
  "تقديم المشاريع وتوليد طلب مرتبط بالعرض والجمهور المناسب.","تموضع المشاريع والمحتوى والحملات وتوليد الطلب لمشروعي شمس والوفا.",
  "تنظيم اتجاه المحتوى والعرض والاستقطاب حول خصائص كل مشروع وجمهوره.","اتجاه تقديم ومحتوى وحملات.",
  reading="قراءة النتائج: الاستفسار العقاري ليس صفقة مغلقة؛ إتمام البيع مسؤولية فريق المبيعات لدى العميل. الصورة تصور معماري وليست تصويرًا ميدانيًا.", wide=True),
])

_parts = cases_html.split("</article>")
_mid = f'''<div class="inline-cta glass glass--light reveal">
      <p><b>عندك تحدٍّ مشابه؟</b> نناقشه معك في استشارة مجانية مدتها 30 دقيقة.</p>
      <div class="hero__actions"><a {BOOK_A} class="btn btn--dark">احجز استشارة مجانية</a><a href="#" data-wa="مرحباً MKN ARABIA، اطلعت على أعمالكم وأرغب بمناقشة مشروعي" class="btn btn--ghost">واتساب</a></div>
    </div>'''
cases_html = "</article>".join(_parts[:5]) + "</article>" + _mid + "</article>".join(_parts[5:])
def subnav(current):
    items = [("work.html", f"دراسات الحالة · {CASES_N}"), ("testimonials.html", f"آراء العملاء · {TESTI_N}")]
    return '<nav class="subnav" aria-label="الأعمال">' + "".join(
        f'<a href="{h}"{" aria-current=" + chr(34) + "page" + chr(34) if h == current else ""}>{t}</a>' for h, t in items) + "</nav>"

work = page_hero(f"SELECTED WORK · {CASES_N} CASES", "أعمال مختارة.",
  "قصص عمل من السعودية والأردن وفلسطين: التحدي، وما نفذناه، وما سلّمناه. تُعرض الأسماء والبيانات بموافقة أصحابها.",
  actions=True, extra=subnav("work.html")) + f'''
<section class="section section--dark grain" style="padding:56px 0">
  <div class="container">
    <h2 class="sr-only">فهرس الحالات</h2>
    <div class="windex">{"[[case_index]]" if THEME else windex}</div>
  </div>
</section>
<section class="section section--aura">
  <div class="container">{"[[cases_full]]" if THEME else cases_html}
    <div class="hero__actions" style="justify-content:center;margin-top:16px"><a href="testimonials.html" class="btn btn--dark arrow">اقرأ آراء كل العملاء ({TESTI_N}) </a></div>
  </div>
</section>
{CTA}'''
page("work.html", "أعمالنا: حالات تسويق رقمي وعلامات تجارية | MKN ARABIA",
     "10 حالات من أعمال MKN ARABIA في العافية والفعاليات والعقار والمطاعم والتقنية في السعودية والأردن وفلسطين: التحدي، دورنا، وما نفّذناه.",
     "work.html", work)

# ===================== ABOUT =====================
VALUES = [("01 · CLARITY","الوضوح","أهداف ونطاق ومؤشرات يعرفها الطرفان."),("02 · ACCOUNTABILITY","المسؤولية","تقييم العمل وفق المخرجات والبيانات والمسؤوليات المتفق عليها."),
          ("03 · QUALITY","الجودة","مواد وتجارب تتسق مع قيمة العلامة."),("04 · TRANSPARENCY","الشفافية","فصل الأتعاب والإنفاق والافتراضات والقيود."),
          ("05 · IMPROVEMENT","التحسين المستمر","مراجعة الأدلة وتعديل ما يحتاج تطويرًا."),("06 · PARTNERSHIP","الشراكة","تعاون يحترم أدوار العميل وقدرته التشغيلية.")]
values_html = "".join(f'<div class="cell reveal"><span class="label">{a}</span><h3>{t}</h3><p>{d}</p></div>' for a, t, d in VALUES)
METHOD = [("DISCOVER","اكتشاف","نفهم الهدف والسوق والعرض والمدخلات والقيود."),("STRATEGIZE","استراتيجية","الأولويات والجمهور والرسائل والقنوات وتعريف النجاح."),
          ("BUILD","بناء","ننفذ المخرجات المحددة بعد اعتماد الاتجاه والمواد."),("LAUNCH","إطلاق","نختبر ونسلم أو نفعل النطاق المتفق عليه."),
          ("MEASURE","قياس","نقرأ البيانات المتاحة حسب مصادرها وحدودها."),("OPTIMIZE","تحسين","ما يتغير، وما يستمر، وما يحتاج نطاقًا جديدًا.")]
method_html = "".join(f'<div class="cell reveal"><h3>{t}</h3><span class="en">{en}</span><p style="margin-top:8px">{d}</p></div>' for en, t, d in METHOD)
PATH = [("الحضور الرقمي", "موقع وروابط حجز وحضور محلي يقود إلى الحجز.", "cryo"),
        ("المواد الإبداعية", "فلسفة علامة وهوية واتجاه بصري متكامل.", "sandouka"),
        ("تشغيل الاستقطاب", "محتوى وحملات وتوليد طلب حول خصائص كل مشروع.", "kyan"),
        ("قراءة التقارير", "تقارير تفصل بيانات المنصة عن نتائج النشاط.", "beautiful-shine"),
        ("التجارب التقنية", "تجارب تحليل بالصور لمسارات B2B وB2C.", "mireva"),
        ("الأنظمة المخصصة", "نظام يجمع الطلبات والأدوار والحضور في تجربة واحدة.", "restaurant-ops")]
path_html = "".join(f'<a href="work.html#{cid}" class="cell spot reveal icard"><span class="label" aria-hidden="true">0{i}</span><span class="go" aria-hidden="true">←</span><h3>{t}</h3><p>{d}</p><span class="more">مثال: {CASE_NAME[cid]}</span></a>' for i, (t, d, cid) in enumerate(PATH, 1))
RESP = [("الهدف والنطاق","توصية وصياغة وتحديد نطاق التنفيذ","اعتماد الهدف والميزانية"),("المواد والبيانات","تحديد المتطلبات وتنظيمها","تسليم مواد وحقوق وبيانات صحيحة"),
        ("الوصول للأدوات","استخدام صلاحيات متفق عليها","ملكية الحسابات وإتاحة الوصول"),("المراجعة","إعداد المخرج والتعديل المحدد","ملاحظات مجمعة وصاحب اعتماد"),
        ("الإعلان","تشغيل وقياس ضمن النطاق","دفع الإنفاق واعتماد العرض"),("الحجز والمبيعات","تصميم المسار أو ربطه إن شمل العرض","الرد والتأهيل والإغلاق وتنفيذ الخدمة"),
        ("التقنية","اختبار وتسليم وفق المعايير","قبول المتطلبات وتوفير البيئة والمالك"),("نشر الحالة","إعداد نسخة مناسبة","الإذن بالاسم والصورة والبيانات")]
resp_html = "".join(f'<tr><td>{a}</td><td data-l="MKN ARABIA">{b}</td><td data-l="العميل">{c}</td></tr>' for a, b, c in RESP)
LAYERS = [("منصة وإعلان","إنفاق ونقر وتواصل","لا يثبت وحده البيع"),("وجهة رقمية","نموذج وإجراء وبدء حجز","يعتمد على الحدث وصحة التتبع"),
          ("عملية تجارية","تأهيل وحجز وحضور","تحتاج تسجيلًا من العميل"),("نتيجة النشاط","مبيعات وتحصيل وعودة","ليست تلقائيًا إيرادًا منسوبًا للإعلان")]
layers_html = "".join(f'<tr><td data-label="الطبقة"><span class="label">0{i}</span>{a}</td><td data-label="أمثلة">{b}</td><td data-label="حدود الاستنتاج">{c}</td></tr>' for i, (a, b, c) in enumerate(LAYERS, 1))

VOICE = [("مرح","جاد",42),("تقليدي","عصري",28),("بسيط","معقّد",62),("قريب","متحفّظ",78),("ثابت","ديناميكي",30),("عملي","مثالي",84),("عفوي","مدروس",34)]
# the dot sits at left:var(--v) in an RTL row, so a small value is closer to the second (left) word
voice_html = "".join(f'<div class="voice__row"><span>{r}</span><div class="voice__track" aria-hidden="true"><i style="--v:{v}%"></i></div><span>{l}</span><span class="sr-only">: أقرب إلى «{l if v < 50 else r}»</span></div>' for r, l, v in VOICE)
about = page_hero("ABOUT MKN ARABIA", "شريك استراتيجي في النمو الرقمي والإبداع والتقنية.",
  "MKN ARABIA شريك استراتيجي لنمو الأعمال، يجمع الاستراتيجية والإبداع والأداء والتقنية حول أولويات العميل التجارية. نربط التموضع والمحتوى والاستقطاب والتجربة الرقمية والقياس ضمن نطاق واضح للتنفيذ والتحسين.", actions=True) + logos_rail() + f'''
<section class="section section--aura">
  <div class="container">
    <div class="heading">
      <span class="label">WHAT MAKES US DIFFERENT</span>
      <h2>ما الذي يميزنا عن الوكالات التقليدية؟</h2>
      <p>بدلًا من إدارة كل قناة كجزيرة منفصلة، نربط قرارات التسويق برحلة العميل وبالعمليات داخل الشركة، ونسعى لأن تكون أولويات التنفيذ شفافة وقياس الأداء مفهومًا للإدارة، بعيدًا عن تقارير النشاط السطحي.</p>
    </div>
    <div class="grid g3">
      <div class="cell spot reveal"><span class="label">01</span><h3>نبدأ بالمشكلة التجارية</h3><p>نسأل أولًا: ما المشكلة التي نريد حلها؟ ثم نختار الأدوات والقنوات.</p></div>
      <div class="cell spot reveal"><span class="label">02</span><h3>الحل حسب الاحتياج</h3><p>قد يكون حملة أداء، أو إعادة بناء الهوية، أو تحسين موقع التحويل، أو تنظيم متابعة العملاء باستخدام CRM.</p></div>
      <div class="cell spot reveal"><span class="label">03</span><h3>ليست كل شركة بحاجة إلى كل خدمة</h3><p>نوصي بما يخدم الهدف فعلًا، ونوضح ما يُنفَّذ مباشرة وما يحتاج دراسة أو موردًا.</p></div>
    </div>
  </div>
</section>

<section class="section section--white">
  <div class="container">
    <div class="heading">
      <span class="label">HOW THE WORK HAS GROWN</span>
      <h2 id="h-path">مسار الأعمال.</h2>
      <p>من الحضور الرقمي إلى الأنظمة المخصصة: كل مرحلة مرتبطة بحالة عمل حقيقية يمكنك الاطلاع عليها.</p>
    </div>
    {SWIPE_HINT}<div class="grid g3 swipe" data-lb="h-path">{path_html}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="grid g2">
      <div class="cell reveal" style="padding:44px"><span class="label">VISION</span><h3 style="font-size:28px">الرؤية</h3><p style="font-size:18px">أن نساعد الأعمال الطموحة في المنطقة على بناء علامات أقوى وبنية رقمية أكثر ملاءمة ومنظومات نمو قابلة للتحسين.</p></div>
      <div class="cell reveal" style="padding:44px;background:var(--ink);color:#fff"><span class="label" style="color:var(--sky)">MISSION</span><h3 style="font-size:28px">الرسالة</h3><p style="font-size:18px;color:var(--muted-d)">ربط الاستراتيجية والإبداع والأداء والتقنية في حلول تجارية محددة، تعزز التموضع وتنظم الاستقطاب والتجربة والقياس حول أولويات العميل.</p></div>
    </div>
  </div>
</section>

<section class="section section--white">
  <div class="container">
    <div class="heading">
      <span class="label">SIX VALUES · ONE STANDARD</span>
      <h2 id="h-values">القيم.</h2>
    </div>
    <div class="grid g3 swipe" data-lb="h-values">{values_html}</div>
  </div>
</section>

<section class="section section--dark grain">
  {grid_lines("b")}
  <div class="container capmap">
    <div>
      <span class="label">BRAND VOICE</span>
      <h2 style="color:#fff;font-size:clamp(30px,3.8vw,48px);margin-top:14px">شخصية العلامة.</h2>
      <p>كيف نتحدث مع عملائنا وجمهورهم: لغة عملية وقريبة وعصرية، تشرح بوضوح وتبتعد عن المبالغة.</p>
      <p class="slogan" style="margin-top:24px">سوّق بالعربي، سوّق صح</p>
    </div>
    <div class="voice glass reveal" style="padding:32px">{voice_html}</div>
  </div>
</section>

<section class="section section--dark grain" style="padding-top:0">
  <div class="container">
    <div class="heading">
      <span class="label">MARKET FOCUS · CORE → REGION</span>
      <h2 style="color:#fff" id="h-markets">التركيز السوقي.</h2>
      <p>نعمل على حلول تراعي لغة العميل والسياق المحلي والعرض التجاري وسلوك الاكتشاف والشراء. يثبت نطاق كل مشروع السوق المستهدف واللغة والقنوات ومتطلبات المواد.</p>
    </div>
    <div class="markets swipe" data-lb="h-markets">
      <div class="glass reveal"><span class="label">CORE · KSA</span><h3>السعودية</h3><p>سوق أساسي، مع علاقات وسجل أعمال.</p></div>
      <div class="glass reveal"><span class="label">CORE · UAE</span><h3>الإمارات</h3><p>سوق أساسي ضمن التركيز الإقليمي.</p></div>
      <div class="glass reveal"><span class="label">ACTIVE · EGY</span><h3>مصر</h3><p>علاقات وسجل أعمال.</p></div>
      <div class="glass reveal"><span class="label">ACTIVE · JOR</span><h3>الأردن</h3><p>علاقات وسجل أعمال.</p></div>
      <div class="glass reveal"><span class="label">ACTIVE · PSE</span><h3>فلسطين</h3><p>علاقات وسجل أعمال.</p></div>
      <div class="glass reveal"><span class="label">REGION · GCC · MENA</span><h3>الخليج والشرق الأوسط</h3><p>أسواق أخرى ضمن نطاق مخصص؛ نراجع فروق الرسائل والأسعار واللغة والقنوات قبل التوسع.</p></div>
    </div>
    <p class="reading" style="color:var(--muted-d);margin-top:24px">نخدم هذه الأسواق من مقرنا في الأردن.</p>
  </div>
</section>

{founder_block("section section--cream", "القيادة.", "founder")}

<section class="section section--white" id="method">
  <div class="container">
    <div class="heading">
      <span class="label">HOW WE WORK · DISCOVER → OPTIMIZE</span>
      <h2 id="h-method">منهجية العمل.</h2>
      <p>ست خطوات في دورة واحدة. يحدد عرض كل مشروع زمن المراحل وعدد الاجتماعات وصاحب الاعتماد، والمشاريع التقنية تبدأ باكتشاف مستقل إذا لم يكن النطاق أو الربط واضحًا.</p>
    </div>
    <div class="grid g3 steps swipe" data-lb="h-method">{method_html}</div>
    <div class="loop-box reveal">
      <span class="label">THE GROWTH LOOP</span>
      <h3>حلقة واحدة، لا قنوات منفصلة.</h3>
      <p>قبل اختيار الخدمة نراجع نقطة التعطل: وضوح العرض، جودة المواد، مصدر الاستقطاب، صفحة الهبوط، أو متابعة الاستفسار.</p>
      {LOOP_FLOW}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="heading">
      <span class="label">SHARED RESPONSIBILITIES</span>
      <h2>مسؤوليات التعاون.</h2>
      <p>نعتمد جهة اتصال واحدة من العميل، ونستخدم سجل قرارات وطلبات تغيير عند العمل عبر أكثر من وظيفة.</p>
    </div>
    <div class="ftable-wrap glass glass--light reveal">
      <table class="resp">
        <caption class="sr-only">مسؤوليات التعاون بين MKN ARABIA والعميل</caption>
        <thead><tr><th>المهمة</th><th>MKN ARABIA</th><th>العميل</th></tr></thead>
        <tbody>{resp_html}</tbody>
      </table>
    </div>
  </div>
</section>

<section class="section section--dark">
  <div class="container">
    <div class="heading">
      <span class="label">MEASUREMENT THAT SERVES DECISIONS</span>
      <h2 style="color:#fff">القياس الذي يخدم القرار.</h2>
      <p>نثبت تعريف كل مؤشر ومصدره قبل المقارنة. لا نستخدم نسبة إجمالي المبيعات إلى الإنفاق بوصفها ROAS دون إسناد مثبت.</p>
    </div>
    <table class="ptable reveal">
      <thead><tr><th>LAYER · الطبقة</th><th>EXAMPLES · أمثلة</th><th>LIMIT · حدود الاستنتاج</th></tr></thead>
      <tbody>{layers_html}</tbody>
    </table>
  </div>
</section>
{CTA}'''
page("about.html", "من نحن: وكالة تسويق رقمي عربية للنمو | MKN ARABIA", "تعرّف على MKN ARABIA: المسار، الرؤية والرسالة، القيم الست، التركيز السوقي، القيادة، منهجية العمل ومسؤوليات التعاون.", "about.html", about)

# ===================== CONTACT =====================
opts = "".join(f'<option value="{d["code"]} · {d["short"]}">{d["short"]}</option>' for d in DEPTS)
FAQ = [("ما الدول التي تخدمونها؟","السعودية والإمارات وقطر والكويت والبحرين وسلطنة عُمان، إضافة إلى الأردن وفلسطين ومصر. نعمل عن بُعد من مقرنا في الأردن، ولكل سوق خليجي صفحة توضح طريقة العمل."),("هل أحتاج إلى جميع الخدمات؟","لا. يبدأ النطاق بما يحتاجه العمل فعليًا، وقد يكون خدمة واحدة أو مجموعة أعمال مترابطة."),
       ("هل تشمل الأتعاب الإنفاق الإعلاني؟","يُفصل الإنفاق ويدفع للمنصة مباشرة، إلا إذا نص العرض على آلية أخرى واضحة."),
       ("هل تشمل المواد التصوير؟","الإنتاج من مواد العميل حسب النطاق. التصوير والممثلون والموسيقى المدفوعة والمواد المرخصة تبين في إضافة مستقلة."),
       ("هل تضمنون البيع أو الترتيب؟","نلتزم بمخرجات محددة وقياس وتحسين. النتائج تعتمد أيضًا على العرض والسوق والميزانية وتشغيل العميل."),
       ("هل تشمل باقة الموقع متجرًا أو CRM؟","لا، إلا إذا ذكرت المخرجات صراحة. التكامل المخصص أو التجارة يحتاج نطاقًا مستقلًا."),
       ("هل حلول AI جاهزة لكل مشروع؟","تبدأ بدراسة البيانات والاستخدام والتكلفة والاختبار. النموذج التجريبي ليس إطلاقًا عامًا أو أداة تشخيصية معتمدة."),
       ("كيف أتلقى الملفات؟","يحدد العرض صيغ التسليم والملفات الأصلية والحقوق والتراخيص، ولا يشمل نقل الشيفرة المصدرية أو أي حقوق غير مذكورة فيه."),
       ("ماذا إذا تغيرت الأولويات؟","نوثق التغيير والمخرج والتكلفة والمدة قبل تنفيذه."),
       ("كيف يتم قياس الأداء؟","بحسب النشاط: عملاء محتملون مؤهلون، وحجوزات، ومحادثات، ومبيعات، وجودة مسار التحويل؛ دون مساواة بيانات المنصة بإيرادات منسوبة للإعلان."),
       ("هل توفرون الدعم باللغة الإنجليزية؟","نعم، يمكن تطوير محتوى وخطط عمل بلغتين بناءً على نطاق المشروع."),
       ("هل يمكنكم العمل مع فريقنا الداخلي؟","نعم، عبر مسؤوليات متفق عليها ومسار اعتماد واضح للمحتوى والتسليم."),
       ("متى تردون على الطلبات؟","نرد خلال يوم عمل، والتواصل متاح طوال أيام الأسبوع عبر واتساب أو البريد أو حجز استشارة.")]
faq_html = "".join(f'<details{" open" if i == 1 else ""}><summary><span class="label">Q{i:02d}</span>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ, 1))

def field_err(fid):
    return f'<p class="err" id="e-{fid}" hidden></p>'
contact = page_hero("LET'S START", "ابدأ التعاون.",
  "اختر الطريقة الأسهل لك: استشارة مجانية، أو رسالة واتساب، أو موجز مكتوب. أخبرنا بهدفك وسوقك، ونقترح عليك نطاقًا واضحًا وعرضًا مخصصًا.") + f'''
<section class="section section--aura" id="contact-main">
  <div class="container contact-grid">
    <div class="reveal">
      <span class="label">CONTACT</span>
      <h2 style="font-size:34px;margin:12px 0 18px">تواصل مباشرة.</h2>
      <div class="cinfo glass glass--light">
        <a {BOOK_A} class="cinfo__primary"><span class="label">BOOKING · المسار الأسرع</span><b>احجز استشارة مجانية · 30 دقيقة</b></a>
        <a href="#" data-wa class="cinfo__wa"><span class="label">WHATSAPP</span><b>+20 114 055 2627</b></a>
        <a data-email href="mailto:contact@mknarabia.com"><span class="label">EMAIL</span><b>contact@mknarabia.com</b></a>
        <div class="cinfo__social">
          <a href="https://instagram.com/mknarabia" target="_blank" rel="noopener"><span class="label">INSTAGRAM</span><b>@mknarabia</b></a>
          <a href="https://facebook.com/mknarabia" target="_blank" rel="noopener"><span class="label">FACEBOOK</span><b>@mknarabia</b></a>
          <a href="https://linkedin.com/company/mknarabia" target="_blank" rel="noopener"><span class="label">LINKEDIN</span><b>MKN ARABIA</b></a>
        </div>
      </div>
      <p class="reading">متاحون للتواصل طوال أيام الأسبوع، ونرد خلال يوم عمل.</p>
      <p class="reading">المقر في الأردن · نخدم السعودية والإمارات والأردن وفلسطين ومصر.</p>
      <p class="reading"><a href="#book" style="text-decoration:underline;text-underline-offset:3px">أو اختر موعدًا مباشرة من التقويم أدناه</a></p>
    </div>

    <form class="form glass glass--light reveal" id="contact-form" novalidate>
      <span class="label">PROJECT BRIEF</span>
      <h3 style="margin-top:8px">أرسل تفاصيل مشروعك</h3>
      <p class="muted" style="font-size:15px">يصلنا طلبك على البريد، ونفتح لك واتساب برسالة جاهزة لتسريع التواصل. نرد خلال يوم عمل.</p>
      <div class="hp" aria-hidden="true"><label for="f-website">اترك هذا الحقل فارغًا</label><input type="text" id="f-website" name="website" tabindex="-1" autocomplete="off"></div>
      <div class="form-row">
        <div class="field"><label for="f-name">الاسم الكامل *</label><input type="text" id="f-name" name="name" required autocomplete="name">{field_err("name")}</div>
        <div class="field"><label for="f-company">اسم الشركة / العلامة</label><input type="text" id="f-company" name="company" autocomplete="organization"></div>
      </div>
      <div class="form-row">
        <div class="field"><label for="f-phone">رقم الهاتف (مع رمز الدولة) *</label><input id="f-phone" name="phone" type="tel" required dir="ltr" autocomplete="tel" placeholder="+966 5X XXX XXXX">{field_err("phone")}</div>
        <div class="field"><label for="f-email">البريد الإلكتروني</label><input id="f-email" name="email" type="email" dir="ltr" autocomplete="email">{field_err("email")}</div>
      </div>
      <div class="form-row">
        <div class="field"><label for="f-country">السوق المستهدف *</label>
          <select id="f-country" name="country" required><option value="">اختر</option><option>السعودية</option><option>الإمارات</option><option>قطر</option><option>الكويت</option><option>البحرين</option><option>سلطنة عُمان</option><option>الأردن</option><option>فلسطين</option><option>مصر</option><option>سوق آخر في المنطقة</option></select>{field_err("country")}</div>
        <div class="field"><label for="f-service">ما الذي تحتاجه؟ *</label>
          <select id="f-service" name="service" required><option value="">اختر</option><option value="UNSURE · غير متأكد">غير متأكد — أحتاج تشخيصًا</option>{opts}<option value="X01–X08 · حل متكامل">حل متكامل يجمع أكثر من خدمة</option></select>{field_err("service")}</div>
      </div>
      <div class="form-row">
        <div class="field"><label for="f-timing">الموعد المتوقع للبدء</label>
          <select id="f-timing" name="timing"><option value="">اختر</option><option>فورًا</option><option>خلال شهر</option><option>خلال 3 أشهر</option><option>أستكشف فقط</option></select></div>
        <div class="field"><label for="f-budget">الميزانية التقريبية (للمشروع أو شهريًا، بالدولار)</label>
          <select id="f-budget" name="budget"><option value="">اختر</option><option>أقل من 1,000</option><option>1,000 – 3,000</option><option>3,000 – 7,000</option><option>أكثر من 7,000</option></select></div>
      </div>
      <div class="field"><label for="f-msg">الهدف والأصول المتاحة</label><textarea id="f-msg" name="message" placeholder="ما الهدف الذي تريد العمل عليه؟ ما الذي تملكه اليوم (موقع، حسابات، هوية، بيانات)؟"></textarea></div>
      <button type="submit" class="btn btn--dark" style="width:100%">{WA_ICON}إرسال الطلب</button>
      <div class="form-success" role="status" aria-live="polite"></div>
      <div class="form-alt" hidden>
        <a href="#" id="wa-retry" target="_blank" rel="noopener">افتح واتساب مرة أخرى</a> ·
        <a href="#" id="mail-alt">أرسله بالبريد بدلًا من ذلك</a> ·
        <button type="button" id="copy-brief">انسخ الطلب</button>
      </div>
      <p class="form-note">تُستخدم بياناتك فقط للتواصل بخصوص طلبك.</p>
    </form>
  </div>
</section>

{proof_strip(["Beautiful Shine", "Kyan Real Estate"], "أصحاب أعمال عملنا معهم")}

<section class="section section--dark grain" id="book">
  {grid_lines("b")}
  <div class="container capmap" style="align-items:start">
    <div>
      <span class="label">BOOK A FREE CONSULTATION</span>
      <h2 style="color:#fff;font-size:clamp(30px,3.8vw,46px);margin-top:14px">خلّنا نناقش فرص نمو أعمالك.</h2>
      <p>احجز استشارة مجانية لمدة 30 دقيقة عبر Google Meet، دون أي التزام.</p>
      <ul class="checks-d">
        <li>تتحدث مباشرة مع د. نور الدين أبو علّان، المؤسس والرئيس التنفيذي.</li>
        <li>طبيعة نشاطك التجاري والسوق والجمهور المستهدف.</li>
        <li>أهدافك التسويقية والتحديات الحالية.</li>
        <li>فرص تطوير الهوية، والإعلانات، والمواقع والمتاجر، والظهور في البحث، والأتمتة.</li>
        <li>الخطوات المناسبة لأعمالك خلال المرحلة القادمة.</li>
      </ul>
      <div class="hero__meta">
        <div class="glass"><span class="label">DURATION</span>30 دقيقة</div>
        <div class="glass"><span class="label">FORMAT</span>Google Meet</div>
        <div class="glass"><span class="label">FEE</span>مجانية</div>
      </div>
    </div>
    <div class="glass booking reveal">
      <iframe src="{BOOK_EMBED}" title="احجز استشارة مجانية — MKN ARABIA" loading="lazy"></iframe>
      <div class="booking__alt"><p class="form-note">إن لم يظهر التقويم:</p><a {BOOK_A} class="btn btn--dark btn--sm">افتح صفحة الحجز في نافذة جديدة</a></div>
    </div>
  </div>
</section>

<section class="section section--white">
  <div class="container">
    <div class="heading heading--row">
      <div>
        <span class="label">AFTER YOU REACH OUT</span>
        <h2>ماذا يحدث بعد التواصل.</h2>
        <p>في المشاريع التقنية الكبيرة نبدأ عادةً بدراسة قصيرة مدفوعة، ثم نرسل عرض التنفيذ ولك حرية القرار.</p>
      </div>
      <a href="about.html#method" class="btn btn--ghost arrow">منهجية العمل الكاملة </a>
    </div>
    <div class="grid g4 steps">{quote_steps_html}</div>
  </div>
</section>

<section class="section section--aura">
  <div class="container" style="max-width:900px">
    <div class="heading">
      <span class="label">{"[[faq_count]]" if THEME else f"{len(FAQ):02d}"} QUESTIONS · CLEAR ANSWERS</span>
      <h2>أسئلة قبل التعاون.</h2>
    </div>
    <div class="faq">{"[[faq]]" if THEME else faq_html}</div>
    <p class="reading" style="margin-top:22px">لم تجد إجابتك؟ <a href="#" data-wa="مرحباً MKN ARABIA، لدي سؤال قبل التعاون" style="text-decoration:underline;text-underline-offset:3px">اسألنا على واتساب</a></p>
  </div>
</section>'''
page("contact.html", "احجز استشارة تسويق مجانية | MKN ARABIA", "احجز استشارة مجانية مع MKN ARABIA أو تواصل عبر واتساب +20 114 055 2627 أو البريد contact@mknarabia.com.", "contact.html", contact)

# ===================== TESTIMONIALS =====================
groups = ""
for code, cname, en in COUNTRIES:
    items = [t for t in TESTIMONIALS if t["country"] == code]
    if not items: continue
    feat = (len(items) + 1) % 3 == 0 and len(items) > 3   # one wide card keeps the last row full
    cards = ""
    for i, t in enumerate(items):
        extra = (" tcard--feature" if feat and i == 0 else "") + (" tcard--more" if len(items) > 4 and i >= 3 else "")
        cards += tcard(t, extra)
    more = f'<button type="button" class="btn btn--ghost btn--sm tmore" data-more>عرض كل آراء {cname} ({len(items)})</button>' if len(items) > 4 else ""
    groups += f"""<div class="tgroup" id="{code}">
  <div class="heading" style="margin-bottom:22px"><span class="label">{en} · {len(items)}</span><h2>{cname}</h2></div>
  <div class="grid g3">{cards}</div>{more}
</div>"""
    if code == "sa":
        groups += f"""<div class="inline-cta glass glass--light reveal">
  <p><b>أعجبك ما قرأت؟</b> نناقش نشاطك في استشارة مجانية مدتها 30 دقيقة.</p>
  <div class="hero__actions"><a {BOOK_A} class="btn btn--dark">احجز استشارة مجانية</a><a href="#" data-wa class="btn btn--ghost">واتساب</a></div>
</div>"""
testimonials_page = page_hero("CLIENT VOICES", "آراء العملاء.",
  f"{TESTI_N} رأيًا من أصحاب أعمال في {'[[countries_phrase]]' if THEME else 'ست دول'} عن تجربتهم مع MKN ARABIA. جميع الآراء منشورة بموافقة أصحابها.",
  actions=True, extra=subnav("testimonials.html")) + logos_rail(sub="مختارات من العلامات التي عملنا معها في المنطقة.") + f"""
<section class="section section--aura section--jump">
  <div class="container">
    <nav class="jump jump--6 glass glass--light" aria-label="الدول">{"[[testimonial_jump]]" if THEME else "".join(f'<a href="#{c}"><span class="label">{en}</span>{n}</a>' for c, n, en in COUNTRIES)}</nav>
    {"[[testimonial_groups]]" if THEME else groups}
  </div>
</section>
{CTA}"""
page("testimonials.html", "آراء عملاء MKN ARABIA في السعودية والإمارات والأردن", "آراء أصحاب الأعمال الذين عملوا مع MKN ARABIA في السعودية والإمارات والأردن وفلسطين ومصر والمملكة المتحدة.",
     "testimonials.html", testimonials_page, section="work.html")

# ===================== INSIGHTS =====================
insights = page_hero("INSIGHTS", "مقالات لأصحاب الأعمال.",
  "أدلة عملية لفهم التسويق وبناء مسار عملاء واضح وقياسه بواقعية — من فريق MKN ARABIA.", actions=True) + f"""
<section class="section section--aura">
  <div class="container">
    <h2 class="sr-only">أحدث المقالات</h2>
    <div class="grid g3">{"[[insights_all]]" if THEME else insight_cards(ARTICLES)}</div>
  </div>
</section>
{CTA}"""
page("insights.html", "مقالات التسويق الرقمي لأصحاب الأعمال | MKN ARABIA", "مقالات MKN ARABIA لأصحاب الأعمال: اختيار وكالة التسويق، البحث المحلي وملف Google، وقراءة نتائج إعلانات Meta.", "insights.html", insights)

for i, art in enumerate(ARTICLES):
    body_html = f'<p class="lead-p">{art["lead"]}</p>' + "".join(f"<h2>{h}</h2>" + "".join(f"<p>{x}</p>" for x in ps) for h, ps in art["sections"])
    others = [x for x in ARTICLES if x is not art]
    related = " · ".join(f'<a href="{h}">{t}</a>' for h, t in art.get("related", []))
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": art["title"], "description": art["desc"],
                     "inLanguage": "ar", "image": "https://mknarabia.com/assets/img/og-image.jpg",
                     "author": {"@type": "Organization", "@id": ORG, "name": "MKN ARABIA", "url": "https://mknarabia.com/"},
                     "publisher": {"@type": "Organization", "@id": ORG, "name": "MKN ARABIA", "logo": {"@type": "ImageObject", "url": "https://mknarabia.com/assets/img/logo-dark.png"}},
                     "mainEntityOfPage": f"https://mknarabia.com/insights/{art['slug']}.html"}, ensure_ascii=False)
    crumbs = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": "https://mknarabia.com/"},
        {"@type": "ListItem", "position": 2, "name": "المقالات", "item": "https://mknarabia.com/insights.html"},
        {"@type": "ListItem", "position": 3, "name": art["title"]}]}, ensure_ascii=False)
    byline = f'<p class="byline"><span>فريق MKN ARABIA</span> · <span>قراءة {ar_minutes(read_min(art))}</span></p>'
    body = page_hero(f'INSIGHTS · {art["topic"]}', art["title"], art["desc"], extra=byline, chip=False) + f"""
<section class="section section--aura">
  <div class="container">
    <article class="prose glass glass--light reveal">
      {body_html}
      <div class="related"><b>اقرأ أيضًا في خدماتنا وأعمالنا:</b> {related}</div>
      <div class="prose-cta">
        <p>{art["cta"]}</p>
        <div class="hero__actions">
          <a {BOOK_A} class="btn btn--dark">احجز استشارة مجانية</a>
          <a href="#" data-wa="مرحباً MKN ARABIA، قرأت مقال: {art["title"]}" class="btn btn--ghost">تحدث معنا عبر واتساب</a>
        </div>
      </div>
    </article>
    <div class="heading" style="margin:56px 0 24px"><span class="label">READ NEXT</span><h2>مقالات أخرى.</h2></div>
    <div class="grid g2">{insight_cards(others)}</div>
  </div>
</section>"""
    page(f'insights/{art["slug"]}.html', art["seo"], art["desc"], "insights.html", body,
         head_extra=f'\n<script type="application/ld+json">{ld}</script>\n<script type="application/ld+json">{crumbs}</script>', og_type="article")
privacy = page_hero("PRIVACY", "سياسة الخصوصية.", "كيف نتعامل مع بيانات زوار الموقع ومن يتواصل معنا.") + """
<section class="section section--white">
  <div class="container" style="max-width:860px">
    <div class="faq">
      <details open><summary><span class="label">01</span>البيانات التي نجمعها</summary><p>عند إرسال نموذج التواصل أو مراسلتنا على واتساب: الاسم ورقم الهاتف والبريد واسم الشركة وتفاصيل الطلب التي تختار مشاركتها. وعند تصفح الموقع: بيانات استخدام عامة مثل الصفحات التي زرتها ومصدر الزيارة (مثل معاملات UTM أو الحملة الإعلانية) ونوع الجهاز.</p></details>
      <details open><summary><span class="label">02</span>أدوات القياس</summary><p>قد نستخدم Google Analytics وGoogle Tag Manager وبكسلات المنصات الإعلانية (مثل Meta وTikTok وGoogle Ads) لقياس أداء الموقع والحملات. تستخدم هذه الأدوات ملفات تعريف الارتباط أو تقنيات مشابهة، ونحتفظ بمصدر الزيارة على جهازك لمدة تصل إلى 90 يومًا لربط الطلب بالحملة التي جاء منها.</p></details>
      <details open><summary><span class="label">03</span>كيف نستخدم البيانات</summary><p>يصلنا طلب النموذج على بريدنا الإلكتروني، ويفتح لك واتساب برسالة جاهزة إن اخترت إرسالها. نستخدم البيانات للرد على طلبك وإعداد عرض السعر، ولفهم أداء الموقع والحملات وتحسينها. لا نبيع بياناتك الشخصية.</p></details>
      <details open><summary><span class="label">04</span>خياراتك</summary><p>يمكنك حذف ملفات تعريف الارتباط وبيانات الموقع من إعدادات متصفحك، أو استخدام إعدادات الإعلانات في حساباتك على المنصات. ولطلب الاطلاع على بياناتك أو حذفها راسلنا على <a data-email href="mailto:contact@mknarabia.com">contact@mknarabia.com</a>.</p></details>
    </div>
    <p class="note"><span>آخر تحديث: أكتوبر <span class="ltr">2026</span>.</span></p>
  </div>
</section>"""
page("privacy.html", "سياسة الخصوصية | MKN ARABIA", "سياسة الخصوصية لموقع MKN ARABIA وأدوات القياس المستخدمة.", "", privacy)

utm = page_hero("INTERNAL TOOL · UTM BUILDER", "منشئ روابط الحملات.",
  "أداة داخلية لفريق MKN ARABIA: أنشئ رابطًا موحدًا لكل حملة أو منشور، حتى يظهر مصدر كل زيارة وكل طلب في Google Analytics وفي رسالة واتساب.") + """
<section class="section section--white">
  <div class="container contact-grid">
    <div class="form glass glass--light" id="utm-form">
      <div class="field"><label for="u-page">الصفحة</label>
        <select id="u-page"><option value="">الرئيسية</option><option value="#by-business">الرئيسية — ابدأ من نوع نشاطك</option><option>services.html</option><option>pricing.html</option><option value="pricing.html#x06">الحلول — نمو أعمال الخدمات (X06)</option><option>work.html</option><option>testimonials.html</option><option>about.html</option><option>contact.html</option><option>insights.html</option></select></div>
      <div class="field"><label for="u-preset">القناة (يملأ المصدر والوسيط تلقائيًا)</label>
        <select id="u-preset">
          <option value="facebook|paid_social">Meta Ads — Facebook</option>
          <option value="instagram|paid_social">Meta Ads — Instagram</option>
          <option value="google|cpc">Google Ads — Search</option>
          <option value="google|display">Google Ads — Display</option>
          <option value="youtube|paid_video">YouTube Ads</option>
          <option value="tiktok|paid_social">TikTok Ads</option>
          <option value="snapchat|paid_social">Snapchat Ads</option>
          <option value="linkedin|paid_social">LinkedIn Ads</option>
          <option value="instagram|social">Instagram — منشور / بايو</option>
          <option value="linkedin|social">LinkedIn — منشور</option>
          <option value="whatsapp|messaging">WhatsApp — رسالة / حالة</option>
          <option value="email|email">Email</option>
          <option value="qr|offline">QR — مطبوعات</option>
          <option value="|">مخصص</option>
        </select></div>
      <div class="form-row">
        <div class="field"><label for="u-source">utm_source *</label><input type="text" id="u-source" dir="ltr" required></div>
        <div class="field"><label for="u-medium">utm_medium *</label><input type="text" id="u-medium" dir="ltr" required></div>
      </div>
      <div class="field"><label for="u-campaign">utm_campaign * <span class="muted">(مثال: ksa-leadgen-2026-11)</span></label><input type="text" id="u-campaign" dir="ltr" required></div>
      <div class="form-row">
        <div class="field"><label for="u-content">utm_content <span class="muted">(الإعلان / التصميم)</span></label><input type="text" id="u-content" dir="ltr"></div>
        <div class="field"><label for="u-term">utm_term <span class="muted">(الكلمة / الجمهور)</span></label><input type="text" id="u-term" dir="ltr"></div>
      </div>
    </div>
    <div>
      <span class="label">RESULT</span>
      <h3 style="margin:8px 0 14px">الرابط الجاهز</h3>
      <div id="u-out" class="ltr" style="display:block;text-align:left;word-break:break-all;background:var(--ink);color:#fff;padding:20px;font-family:var(--mono);font-size:14px;min-height:90px"></div>
      <button type="button" id="u-copy" class="btn btn--blue" style="margin-top:14px">نسخ الرابط</button>
      <ul class="spec" style="margin-top:28px">
        <li><span>القاعدة</span><div>أحرف إنجليزية صغيرة وشرطات فقط، بدون مسافات.</div></li>
        <li><span>campaign</span><div>السوق-الهدف-السنة-الشهر، مثل <b class="ltr">ksa-leadgen-2026-11</b></div></li>
        <li><span>content</span><div>اسم التصميم أو الإعلان، مثل <b class="ltr">reel-01</b></div></li>
        <li><span>term</span><div>الكلمة المفتاحية أو الجمهور، مثل <b class="ltr">spa-riyadh</b></div></li>
      </ul>
    </div>
  </div>
</section>
<script>
(function(){
  var $=function(id){return document.getElementById(id)};
  function slug(v){return (v||"").trim().toLowerCase().replace(/\\s+/g,"-").replace(/[^a-z0-9\\-_.]/g,"")}
  function preset(){var p=$("u-preset").value.split("|"); if(p[0]||p[1]){$("u-source").value=p[0];$("u-medium").value=p[1];} build();}
  function build(){
    var v=$("u-page").value, h="", k=v.indexOf("#"); if(k>=0){h=v.slice(k);v=v.slice(0,k);} var base="https://mknarabia.com/"+v, q=new URLSearchParams();
    [["utm_source","u-source"],["utm_medium","u-medium"],["utm_campaign","u-campaign"],["utm_content","u-content"],["utm_term","u-term"]].forEach(function(k){var v=slug($(k[1]).value); if(v) q.set(k[0],v);});
    $("u-out").textContent=base+(q.toString()?"?"+q.toString():"")+h;
  }
  $("u-preset").addEventListener("change",preset);
  document.querySelectorAll("#utm-form input, #utm-form select").forEach(function(el){el.addEventListener("input",build)});
  $("u-copy").addEventListener("click",function(){var t=$("u-out").textContent; try{navigator.clipboard.writeText(t); this.textContent="تم النسخ ✓";}catch(e){}});
  preset();
})();
</script>"""
if THEME:  # WordPress addresses are /services/ … rather than services.html, so the options carry full URLs
    utm = utm.replace('<option value="">الرئيسية</option>', '<option value="{{u:home}}">الرئيسية</option>')
    utm = utm.replace('<option value="#by-business">', '<option value="{{u:home}}#by-business">')
    utm = utm.replace('<option value="pricing.html#x06">', '<option value="{{u:pricing}}#x06">')
    for _s, _t in [("services", "الخدمات"), ("pricing", "الباقات"), ("work", "أعمالنا"), ("testimonials", "آراء العملاء"),
                   ("about", "من نحن"), ("contact", "تواصل"), ("insights", "المقالات")]:
        utm = utm.replace(f"<option>{_s}.html</option>", f'<option value="{{{{u:{_s}}}}}">{_t}</option>')
    utm = utm.replace('var base="https://mknarabia.com/"+v', "var base=v")
page("utm.html", "منشئ روابط الحملات | MKN ARABIA", "أداة داخلية لإنشاء روابط UTM.", "", utm)

nf = '''<section class="page-hero grain" style="min-height:80vh;display:grid;place-items:center;text-align:center">
  <div class="container">
    <h1 class="big-mono" style="text-align:center;margin:0">404<span>.</span></h1>
    <p style="margin:20px auto 28px">عذرًا، الصفحة التي تبحث عنها غير موجودة أو تغيّر رابطها.</p>
    <div class="hero__actions" style="justify-content:center">
      <a href="./" class="btn btn--blue">العودة للرئيسية</a>
      <a href="services.html" class="btn btn--line">الخدمات</a>
      <a href="work.html" class="btn btn--line">أعمالنا</a>
      <a href="#" data-wa="مرحباً MKN ARABIA، وصلت إلى رابط غير موجود" class="btn btn--line">تحدث معنا عبر واتساب</a>
    </div>
  </div>
</section>'''
page("404.html", "الصفحة غير موجودة | MKN ARABIA", "الصفحة غير موجودة", "", nf)

# ===================== SERVICE PAGES & GULF MARKETS =====================
# One indexable page per service area and per Gulf market. Built only from the approved service data:
# no prices, no local offices, no results or clients that are not published elsewhere on the site.
SERVICE_SLUG = SVC_SLUG
GCC = [  # slug, short, official, label, ISO, main cities
    ("saudi-arabia", "السعودية", "المملكة العربية السعودية", "SAUDI ARABIA", "SA", "الرياض وجدة والدمام"),
    ("uae", "الإمارات", "الإمارات العربية المتحدة", "UAE", "AE", "دبي وأبوظبي والشارقة"),
    ("qatar", "قطر", "دولة قطر", "QATAR", "QA", "الدوحة"),
    ("kuwait", "الكويت", "دولة الكويت", "KUWAIT", "KW", "مدينة الكويت"),
    ("bahrain", "البحرين", "مملكة البحرين", "BAHRAIN", "BH", "المنامة"),
    ("oman", "سلطنة عُمان", "سلطنة عُمان", "OMAN", "OM", "مسقط"),
]
GROWTH_META = {}  # page file -> extra data for the WordPress theme (schema)

def svc_url(key):
    return f"services/{SERVICE_SLUG[key]}.html"

def faq_block(items, label="FAQ"):
    rows = "".join(f'<details{" open" if i == 1 else ""}><summary><span class="label">Q{i:02d}</span>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(items, 1))
    return f'''<section class="section section--white">
  <div class="container" style="max-width:900px">
    <div class="heading"><span class="label">{label}</span><h2>أسئلة شائعة.</h2></div>
    <div class="faq">{rows}</div>
  </div>
</section>'''

SEO_GEO_EXTRA = """
<section class="section section--white">
  <div class="container">
    <div class="heading">
      <span class="label">SEARCH · MAPS · AI ANSWERS</span>
      <h2 id="h-geo">الظهور في Google وفي إجابات الذكاء الاصطناعي.</h2>
      <p>يبحث العميل اليوم في Google وخرائطه، ويسأل أيضًا مساعدات مثل ChatGPT وGemini وPerplexity وCopilot. لا توجد طريقة تضمن الترتيب أو الذكر في إجابة بعينها؛ ما نعمل عليه هو ما يجعل الموقع قابلًا للاكتشاف والفهم والاستشهاد، ثم نقيس أثره على الطلب.</p>
    </div>
    <div class="grid g4 swipe" data-lb="h-geo">
      <div class="cell reveal"><span class="label">01 · ACCESS</span><h3>الإتاحة والفهرسة</h3><p>صفحات قابلة للزحف وخريطة موقع سليمة وروابط داخلية واضحة، ومراجعة Search Console وBing Webmaster Tools.</p></div>
      <div class="cell reveal"><span class="label">02 · CLARITY</span><h3>محتوى يجيب بوضوح</h3><p>صفحة لكل خدمة وسوق: ماذا تقدم، لمن، بأي نطاق وحدود، مع أمثلة حقيقية وأسئلة يطرحها العملاء فعلًا.</p></div>
      <div class="cell reveal"><span class="label">03 · ENTITY</span><h3>هوية واضحة للمؤسسة</h3><p>بيانات منظمة تطابق ما يراه الزائر، واتساق الاسم والوصف والروابط بين الموقع وملف Google والحسابات الرسمية.</p></div>
      <div class="cell reveal"><span class="label">04 · MEASURE</span><h3>من الظهور إلى الطلب</h3><p>نفصل الظهور والنقر عن التواصل والطلب المؤهل، ونتابع الإحالات من محركات البحث ومنصات الذكاء الاصطناعي في GA4.</p></div>
    </div>
  </div>
</section>"""

def service_page(d):
    key = d["code"].lower()
    subs = "".join(f'<div class="cell reveal"><span class="label">{en}</span><h3>{t}</h3><p>{s}</p></div>' for t, en, s in d["subs"])
    tiers = ""
    for ar, en, _price, unit, _setup, goal, spec in TIERS[d["code"]]:
        lis = "".join(f'<li><span>{k}</span>{v}</li>' for k, v in spec if "الإنفاق" not in k)
        tiers += f'<div class="cell reveal"><span class="label">{en} · {unit}</span><h3>{ar}</h3><p>{goal}</p><ul class="spec" style="margin-top:14px">{lis}</ul></div>'
    cases = DEPT_CASES.get(key, [])
    work = ""
    if cases:
        work = '<div class="windex">' + "".join(f'<a href="work.html#{c}"><span class="n">{i:02d}</span><strong>{CASE_NAME[c]}</strong><span class="s">{next(s_ for cid, _, s_ in CASES if cid == c)}</span></a>' for i, c in enumerate(cases, 1)) + "</div>"
    read = DEPT_READ.get(key)
    read_html = f'<p style="margin-top:22px">اقرأ أيضًا: <a href="insights/{read["slug"]}.html">{read["title"]}</a></p>' if read else ""
    markets = " · ".join(f'<a href="markets/{m[0]}.html">{m[1]}</a>' for m in GCC)
    durations = "؛ ".join(f'{ar}: {dict(spec).get("المدة") or dict(spec).get("التعاقد") or unit}' for ar, _e, _p, unit, _s, _g, spec in TIERS[d["code"]])
    faqs = [
        (f"ما الذي تشمله خدمة {d['short']}؟", f"{len(d['subs'])} خدمات بمخرجات محددة: " + "، ".join(t for t, _, _ in d["subs"]) + ". يُحدد النطاق النهائي في عرض مكتوب قبل البدء."),
        ("كم يستغرق التنفيذ؟", f"يختلف حسب النطاق. المدد التقديرية للنطاقات الثلاثة: {durations}. تبدأ المدة بعد اكتمال المدخلات والوصول والدفعة المتفق عليها."),
        ("هل تقدمون الخدمة لشركات في الخليج من خارج بلدها؟", "نعم. مقرنا في الأردن ونعمل عن بُعد مع عملاء في السعودية والإمارات وقطر والكويت والبحرين وسلطنة عُمان، عبر اجتماعات Google Meet وواتساب ومراحل اعتماد مكتوبة."),
        ("ما الذي لا يدخل في النطاق؟", f"{d['special']} ويُتفق على أي بند خارج النطاق كتابةً قبل تنفيذه."),
        ("كيف أحصل على عرض سعر؟", "احجز استشارة مجانية مدتها 30 دقيقة أو أرسل احتياجك عبر النموذج أو واتساب؛ نراجع الهدف والسوق والمدخلات ونرسل عرضًا بالمخرجات والمدة والأتعاب."),
    ]
    body = page_hero(f"SERVICE · {d['code']} · {d['axis']}", d["t"] + ".", d["lead"], actions=True) + f'''
<section class="section section--aura">
  <div class="container">
    <div class="heading"><span class="label">WHO IT IS FOR</span><h2 id="h-fit">لمن هذه الخدمة.</h2></div>
    <div class="grid g3 swipe" data-lb="h-fit">
      <div class="cell reveal"><span class="label">FIT</span><h3>العميل المناسب</h3><p>{d["fit"]}</p></div>
      <div class="cell reveal"><span class="label">PROBLEM</span><h3>المشكلة</h3><p>{d["prob"]}</p></div>
      <div class="cell reveal"><span class="label">SUCCESS</span><h3>كيف نقيس النجاح</h3><p>{d["measure"]}</p></div>
    </div>
  </div>
</section>
<section class="section section--white">
  <div class="container">
    <div class="heading"><span class="label">{len(d["subs"]):02d} SERVICES · DEFINED DELIVERABLES</span><h2 id="h-subs">ما الذي نقدمه.</h2><p>كل خدمة لها مخرجات وكميات وحدود مكتوبة، وتُجمع في نطاق واحد حسب احتياجك.</p></div>
    {SWIPE_HINT}<div class="grid g3 swipe" data-lb="h-subs">{subs}</div>
    <p class="note" style="margin-top:22px"><span><b>{d["special_label"]}:</b> {d["special"]}</span></p>
  </div>
</section>{SEO_GEO_EXTRA if key == "d06" else ""}
<section class="section section--dark grain">
  {grid_lines("c")}
  <div class="container">
    <div class="heading"><span class="label">3 SCOPES · CUSTOM QUOTE</span><h2 style="color:#fff" id="h-scopes">ثلاثة نطاقات للبدء.</h2><p>«تأسيس» و«نمو» و«توسع» تصف حجم الاحتياج لا مستوى الجودة. الأتعاب في عرض مخصص بعد اعتماد النطاق.</p></div>
    <div class="grid g3 swipe" data-lb="h-scopes">{tiers}</div>
    <div class="hero__actions" style="margin-top:32px">
      <a href="pricing.html#{key}" class="btn btn--blue">تفاصيل الباقات وطلب عرض سعر</a>
      <a href="#" data-wa="مرحباً MKN ARABIA، أرغب بعرض سعر لخدمة {d["short"]} ({d["code"]})" data-quote="{d["code"]}" data-quote-name="{d["short"]}" data-dept="{d["code"]}" class="btn btn--line">اطلب عرضًا عبر واتساب</a>
    </div>
  </div>
</section>
<section class="section section--aura">
  <div class="container">
    <div class="heading"><span class="label">METHOD</span><h2>كيف نعمل.</h2></div>
    <div class="grid g3">{method_html}</div>
    {('<h3 style="margin:44px 0 16px;font-size:22px">من أعمالنا في هذا المجال</h3>' + work) if work else ""}
    {read_html}
    <p style="margin-top:22px"><b>نخدم الشركات في:</b> {markets} · <a href="markets.html">كل الأسواق</a></p>
  </div>
</section>
{faq_block(faqs)}
{CTA}'''
    fname = svc_url(key)
    title = f"{d['short']} للشركات في السعودية والخليج | MKN ARABIA"
    desc = f"{d['lead']} {len(d['subs'])} خدمات بمخرجات محددة لشركات السعودية والإمارات وقطر والكويت والبحرين وعُمان."
    GROWTH_META[fname] = {"kind": "service", "name": d["t"], "short": d["short"], "code": d["code"], "offers": [t for t, _, _ in d["subs"]], "faq": faqs}
    page(fname, title, desc, "", body, section="services.html")

for _d in DEPTS:
    service_page(_d)

# ---------- markets ----------
MARKET_ANGLE = {
    "saudi-arabia": ("أغلب أعمالنا المنشورة من السعودية: مراكز تجميل وعافية في الرياض وجدة، وفعاليات B2B، وتقنية.",
                     ["قنوات الحجز المستخدمة فعليًا (Fresha أو نظام الحجز أو واتساب) وكيف تُقاس.",
                      "الظهور في خرائط Google لكل فرع أو مدينة بشكل منفصل.",
                      "المتاجر على سلة أو زد أو Shopify وربطها بالحملات والقياس.",
                      "المحتوى بالعربية بلغة قريبة من جمهور كل مدينة وقطاع."]),
    "uae": ("من عملائنا في الإمارات E SPA Dubai، ونقدم لشركات الإمارات هوية ومواقع ومحتوى وإعلانات وتوليد طلب.",
            ["جمهور متعدد اللغات: متى تحتاج الصفحات والإعلانات نسخة عربية وإنجليزية مستقلة.",
             "الظهور المحلي في دبي وأبوظبي والشارقة حسب مكان الخدمة الفعلي.",
             "مسار التواصل: واتساب، نموذج، أو حجز مباشر، وأيّها يمكن قياسه.",
             "الاتساق بين الهوية والموقع والإعلانات في سوق شديد التنافس."]),
    "qatar": ("نقدم لشركات قطر ما نقدمه في السعودية والإمارات: هوية وموقع ومحتوى وتوليد طلب، من خلال مراحل اعتماد واضحة.",
              ["التقديم المؤسسي للشركات والجهات التي تخاطب صناع القرار (B2B).",
               "الحاجة إلى نسخة إنجليزية للموقع والعروض المؤسسية.",
               "مسار الاستفسار والمتابعة للطلبات المؤسسية بدل الاكتفاء بالمحادثات.",
               "ما يتطلب حضورًا محليًا (تصوير، فعاليات) وكيف يُنسق مع مورد محلي."]),
    "kuwait": ("نقدم لشركات الكويت هوية ومواقع ومحتوى وإعلانات وتنظيم متابعة الاستفسارات.",
               ["تحويل الاستفسارات من واتساب وإنستغرام إلى متابعة منظمة يمكن قياسها.",
                "الهوية والموقع للأعمال الخدمية والعلامات الجديدة.",
                "المحتوى بالعربية بنبرة تناسب جمهور النشاط.",
                "ما يحتاج تصويرًا أو إنتاجًا محليًا وكيف يُنسق."]),
    "bahrain": ("نقدم خدماتنا لشركات البحرين، خصوصًا الشركات الخدمية وB2B التي تحتاج موقعًا واضحًا ومتابعة طلبات منظمة.",
                ["موقع يشرح الخدمة ويقود إلى طلب واضح.",
                 "ربط النموذج وواتساب بنظام متابعة أو CRM بحسب حجم الطلبات.",
                 "النسخة العربية والإنجليزية للصفحات الأساسية عند الحاجة.",
                 "الظهور في Google وخرائطه لمكان الخدمة الفعلي."]),
    "oman": ("نقدم لشركات سلطنة عُمان موقعًا وهوية ومحتوى وظهورًا في البحث ومسار استفسار واضحًا.",
             ["التمييز في المحتوى والبحث بين «عُمان» و«عمّان» عاصمة الأردن.",
              "الظهور المحلي في مسقط أو مدينة الخدمة الفعلية.",
              "موقع خدمي يجيب عن أسئلة العميل قبل التواصل.",
              "تنظيم متابعة الاستفسارات وقياس مصدرها."]),
}

def market_page(m):
    slug, short, official, label, iso, cities = m
    intro, checks = MARKET_ANGLE[slug]
    code = {"saudi-arabia": "sa", "uae": "ae"}.get(slug)
    quotes = sorted([t for t in TESTIMONIALS if t["country"] == code], key=lambda t: not (t["featured"] or t["case"]))[:3] if code else []
    proof = ""
    if quotes:
        cards = f"[[proof_quotes|{','.join(html.unescape(t['brand']) for t in quotes)}]]" if THEME else "".join(tcard(t) for t in quotes)
        proof = f'''<div class="grid g3" style="margin-top:20px">{cards}</div>
    <p style="margin-top:16px"><a href="testimonials.html#{code}" class="arrow">كل آراء العملاء في {short} </a></p>'''
    else:
        proof = f'<p class="note"><span>لم ننشر بعد دراسات حالة أو آراء عملاء من {short}. نعرض أعمالنا في السعودية والإمارات والأردن وفلسطين كما هي، بموافقة أصحابها، دون نسبتها إلى سوق آخر.</span></p>'
    cases_html = ""
    if slug == "saudi-arabia":
        sa_cases = ["les-senes", "beautiful-shine", "cryo", "osus", "imperio", "mireva"]
        cases_html = '<div class="windex" style="margin-top:20px">' + "".join(f'<a href="work.html#{c}"><span class="n">{i:02d}</span><strong>{CASE_NAME[c]}</strong><span class="s">{next(s_ for cid, _, s_ in CASES if cid == c)}</span></a>' for i, c in enumerate(sa_cases, 1)) + "</div>"
    svc_cells = "".join(f'<a href="{svc_url(d["code"].lower())}" class="cell spot reveal"><span class="label" aria-hidden="true">{d["code"]} · {d["axis"]}</span><span class="go" aria-hidden="true">←</span><h3>{d["short"]}</h3><p>{d["fit"]}</p></a>' for d in DEPTS)
    checks_html = "".join(f"<li>{c}</li>" for c in checks)
    faqs = [
        (f"هل لديكم مكتب في {short}؟", f"لا. مقر MKN ARABIA في الأردن، ونخدم عملاءنا في {official} عن بُعد عبر اجتماعات Google Meet وواتساب وملفات مشتركة ومراحل اعتماد مكتوبة."),
        ("كيف تتم الاستشارة الأولى؟", "استشارة مجانية مدتها 30 دقيقة مع المؤسس عبر Google Meet، نراجع فيها الهدف والسوق والوضع الحالي ونقترح نقطة البداية."),
        ("هل تكتبون المحتوى بالعربية والإنجليزية؟", "نعم. العربية أساس عملنا، ونضيف الإنجليزية للصفحات والمواد التي تحتاجها، ضمن النطاق المتفق عليه."),
        ("ماذا عن التصوير والإنتاج داخل البلد؟", "إذا احتاج المشروع تصويرًا أو حضورًا ميدانيًا نحدد ذلك في النطاق، ويُنفذ عبر فريق العميل أو مورد محلي ننسق معه، ويُتفق على تكلفته منفصلًا."),
        ("بماذا نبدأ؟", "غالبًا بتشخيص سريع: الموقع والحضور والإعلانات ومسار التواصل، ثم خطة بأولويات واضحة قبل أي تنفيذ واسع."),
    ]
    body = page_hero(f"MARKETS · {label}", f"تسويق رقمي للشركات في {short}.",
        f"{intro} نخدم الشركات في {cities} وبقية مدن {short} عن بُعد، بمخرجات ومدد مكتوبة.", actions=True) + f'''
<section class="section section--aura">
  <div class="container">
    <div class="heading"><span class="label">SERVICES</span><h2 id="h-msvc">ما نقدمه لشركات {short}.</h2><p>ثمانية مجالات خدمة، تبدأ بما يحتاجه نشاطك فعليًا.</p></div>
    {SWIPE_HINT}<div class="grid g4 swipe" data-lb="h-msvc">{svc_cells}</div>
  </div>
</section>
<section class="section section--white">
  <div class="container contact-grid">
    <div>
      <span class="label">HOW WE WORK</span>
      <h2 style="margin:10px 0 16px">كيف نعمل مع شركات {short}.</h2>
      <ul class="spec">
        <li><span>المقر</span><div>الأردن · نخدم {official} عن بُعد</div></li>
        <li><span>الاجتماعات</span><div>Google Meet بمواعيد تناسب توقيت الخليج</div></li>
        <li><span>التواصل</span><div>واتساب وبريد إلكتروني · نرد خلال يوم عمل</div></li>
        <li><span>الاعتماد</span><div>عرض مكتوب، ثم مراحل اعتماد ومحضر تسليم لكل مخرج</div></li>
        <li><span>اللغة</span><div>العربية، والإنجليزية حسب الحاجة</div></li>
      </ul>
    </div>
    <div>
      <span class="label">WHAT WE CHECK FIRST</span>
      <h2 style="margin:10px 0 16px">ما نراجعه قبل البدء.</h2>
      <ul class="checks">{checks_html}</ul>
    </div>
  </div>
</section>
<section class="section section--aura">
  <div class="container">
    <div class="heading"><span class="label">PROOF</span><h2>من أعمالنا وآراء العملاء.</h2></div>
    {cases_html}{proof}
  </div>
</section>
{faq_block(faqs)}
{CTA}'''
    fname = f"markets/{slug}.html"
    title = f"تسويق رقمي للشركات في {short} | MKN ARABIA"
    desc = f"MKN ARABIA تخدم الشركات في {official} عن بُعد: استراتيجية، هوية، محتوى، إعلانات، مواقع، ظهور في البحث وCRM، بمخرجات ومدد مكتوبة."
    GROWTH_META[fname] = {"kind": "market", "name": f"خدمات التسويق الرقمي للشركات في {short}", "country": official, "iso": iso, "faq": faqs}
    page(fname, title, desc, "", body)

for _m in GCC:
    market_page(_m)

markets_cards = "".join(f'<a href="markets/{m[0]}.html" class="cell spot reveal"><span class="label" aria-hidden="true">{m[3]}</span><span class="go" aria-hidden="true">←</span><h3>{m[1]}</h3><p>{m[5]}</p></a>' for m in GCC)
markets_hub = page_hero("MARKETS · GCC", "الأسواق التي نخدمها.",
    "نخدم الشركات في السعودية والإمارات وقطر والكويت والبحرين وسلطنة عُمان عن بُعد من مقرنا في الأردن، ولدينا عملاء أيضًا في الأردن وفلسطين ومصر.", actions=True) + f'''
<section class="section section--aura">
  <div class="container">
    <div class="heading"><span class="label">6 GCC MARKETS</span><h2 id="h-mk">اختر سوقك.</h2><p>لكل سوق صفحة توضح طريقة العمل وما نراجعه قبل البدء، والأعمال المنشورة منه إن وجدت.</p></div>
    {SWIPE_HINT}<div class="grid g3 swipe" data-lb="h-mk">{markets_cards}</div>
    <p class="note" style="margin-top:22px"><span>لا نملك مكاتب أو فروعًا في هذه الدول؛ نعمل عن بُعد، وننسق مع موردين محليين عند الحاجة إلى تصوير أو حضور ميداني.</span></p>
  </div>
</section>
{CTA}'''
GROWTH_META["markets.html"] = {"kind": "markets", "name": "الأسواق التي تخدمها MKN ARABIA"}
page("markets.html", "الأسواق: السعودية والإمارات وقطر والكويت والبحرين وعُمان | MKN ARABIA",
     "MKN ARABIA تخدم الشركات في دول الخليج الست عن بُعد من الأردن. تعرّف على طريقة العمل في كل سوق.", "", markets_hub)

SITEMAP_PAGES = ["", "services.html", "pricing.html", "work.html", "testimonials.html", "insights.html", "about.html", "contact.html", "privacy.html", "markets.html"] + [f"insights/{a['slug']}.html" for a in ARTICLES] + [svc_url(k) for k in SERVICE_SLUG] + [f"markets/{m[0]}.html" for m in GCC]
LASTMOD = "2026-10-11"
with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in SITEMAP_PAGES:
        f.write(f"  <url><loc>https://mknarabia.com/{u}</loc><lastmod>{LASTMOD}</lastmod></url>\n")
    f.write("</urlset>\n")

# ===================== WORDPRESS THEME EXPORT =====================
SLUG_OF = {"index.html": "home", "services.html": "services", "pricing.html": "pricing", "work.html": "work",
           "testimonials.html": "testimonials", "insights.html": "insights", "about.html": "about", "contact.html": "contact",
           "privacy.html": "privacy", "utm.html": "utm", "404.html": "404", "markets.html": "markets"}
SLUG_OF.update({svc_url(k): "services/" + v for k, v in SERVICE_SLUG.items()})
SLUG_OF.update({f"markets/{m[0]}.html": "markets/" + m[0] for m in GCC})
NAV_TITLE = {"services": "الخدمات", "markets": "الأسواق"}
CONTACT_LITERALS = [  # site-wide contact details become settings in WordPress
    (BOOK_EMBED, "{{book_embed}}"), (BOOK, "{{book}}"),
    ("https://www.linkedin.com/in/noureddinabuallan", "{{linkedin_founder}}"),
    ("https://linkedin.com/company/mknarabia", "{{linkedin}}"), ("https://instagram.com/mknarabia", "{{instagram}}"),
    ("https://facebook.com/mknarabia", "{{facebook}}"), ("+20 114 055 2627", "{{wa_display}}"),
    ("mailto:contact@mknarabia.com", "mailto:{{email}}"), ("contact@mknarabia.com", "{{email}}"),
]
def to_fragment(body):
    body = polish("<body>" + body)[len("<body>"):]
    for a, b in CONTACT_LITERALS:
        body = body.replace(a, b)
    body = re.sub(r'(href|src)="assets/', r'\1="{{a}}/', body)
    body = re.sub(r'href="\./"', 'href="{{u:home}}"', body)
    body = re.sub(r'href="insights/([a-z0-9-]+)\.html"', r'href="{{post:\1}}"', body)
    body = re.sub(r'href="((?:services|markets)/[a-z0-9-]+)\.html', r'href="{{u:\1}}', body)
    body = re.sub(r'href="(services|pricing|work|testimonials|insights|about|contact|privacy|utm|markets)\.html', r'href="{{u:\1}}', body)
    return body

def article_html(a):
    return f'<p class="lead-p">{a["lead"]}</p>' + "".join(f"<h2>{h}</h2>" + "".join(f"<p>{x}</p>" for x in ps) for h, ps in a["sections"])

def placeholder_url(href):
    m = re.match(r'^(services|pricing|work|testimonials|insights|about|contact|privacy)\.html(#.*)?$', href)
    return "{{u:%s}}%s" % (m.group(1), m.group(2) or "") if m else href

def export_theme():
    os.makedirs(os.path.join(THEME_DIR, "fragments"), exist_ok=True)
    os.makedirs(os.path.join(THEME_DIR, "seed"), exist_ok=True)
    pages = {}
    for fname, pg in THEME_PAGES.items():
        if fname not in SLUG_OF:
            continue
        slug = SLUG_OF[fname]
        with open(os.path.join(THEME_DIR, "fragments", slug.replace("/", "__") + ".html"), "w", encoding="utf-8") as f:
            f.write(to_fragment(pg["body"]))
        pages[slug] = {"title": pg["title"], "desc": pg["desc"]}
        meta = GROWTH_META.get(fname)
        if meta:
            pages[slug].update(meta)
        h1 = re.search(r"<h1>(.*?)</h1>", pg["body"], flags=re.S)
        pages[slug]["h1"] = html.unescape(re.sub(r"<[^>]+>", "", h1.group(1))).strip().rstrip(".") if h1 else slug
    # windex sub-lines and home teasers for the cases
    sub_of = {cid: s_ for cid, _, s_ in CASES}
    teaser, card_alt = {}, {}
    for m in re.finditer(r'href="work\.html#([a-z0-9-]+)" class="fcase reveal"><img [^>]*alt="([^"]*)".*?<p>(.*?)</p>', FCASES_HTML, flags=re.S):
        teaser[m.group(1)] = m.group(3)
        card_alt[m.group(1)] = html.unescape(m.group(2))
    cases = []
    for i, c in enumerate(CASES_DATA):
        c = dict(c)
        c["index_sub"] = sub_of.get(c["slug"], "")
        c["index_name"] = next((n for cid, n, _ in CASES if cid == c["slug"]), c["name"])
        c["teaser"] = teaser.get(c["slug"], "")
        c["image_alt"] = card_alt.get(c["slug"], c["name"])
        c["featured"] = c["slug"] in teaser
        cases.append(c)
    seed = {
        "articles": [dict(slug=a["slug"], title=a["title"], seo=a["seo"], desc=a["desc"], topic=a["topic"], cta=a["cta"],
                          content=article_html(a), related=[[placeholder_url(h), t] for h, t in a.get("related", [])]) for a in ARTICLES],
        "testimonials": [dict(brand=html.unescape(t["brand"]), place=t["place"], country=t["country"], text=t["text"], case=t["case"] or "",
                              featured=bool(t["featured"]), logo=TLOGO.get(t["brand"], "")) for t in TESTIMONIALS],
        "cases": cases,
        "clients": [dict(key=k, label=v["label"], tone=v.get("tone", "light"), bg=v.get("bg", ""), fit=v.get("fit", ""), clip=v.get("clip", ""),
                         file=v.get("src", k + ".webp")) for k, v in _LOGOS.items()],
        "faq": [dict(q=q, a=a) for q, a in FAQ],
        "settings": {"whatsapp": "201140552627", "wa_display": "+20 114 055 2627", "email": "contact@mknarabia.com",
                     "lead_email": "contact@mknarabia.com", "book": BOOK, "book_embed": BOOK_EMBED,
                     "instagram": "https://instagram.com/mknarabia", "facebook": "https://facebook.com/mknarabia",
                     "linkedin": "https://linkedin.com/company/mknarabia", "linkedin_founder": "https://www.linkedin.com/in/noureddinabuallan"},
    }
    with open(os.path.join(THEME_DIR, "seed", "content.json"), "w", encoding="utf-8") as f:
        json.dump(seed, f, ensure_ascii=False, indent=1)
    site = {
        "nav": [["home" if h == "./" else h.replace(".html", ""), t] for h, t in NAV],
        "depts": [{"code": d["code"], "key": d["code"].lower(), "short": d["short"], "slug": SVC_SLUG[d["code"].lower()]} for d in DEPTS],
        "bundles": {x.lower(): t for x, t, *_ in BUNDLES},
        "countries": [list(c) for c in COUNTRIES],
        "pages": pages,
        "case_mid_cta": to_fragment(_mid),
        "testi_mid_cta": to_fragment(f"""<div class="inline-cta glass glass--light reveal">
  <p><b>أعجبك ما قرأت؟</b> نناقش نشاطك في استشارة مجانية مدتها 30 دقيقة.</p>
  <div class="hero__actions"><a {BOOK_A} class="btn btn--dark">احجز استشارة مجانية</a><a href="#" data-wa class="btn btn--ghost">واتساب</a></div>
</div>"""),
        "cta": to_fragment(CTA),
        "wa_svg": WA_SVG,
        "badge": to_fragment(badge("footer-badge")),
        "grid_lines_b": grid_lines("b"),
        "org_founder_linkedin": "https://www.linkedin.com/in/noureddinabuallan",
    }
    os.makedirs(os.path.join(THEME_DIR, "data"), exist_ok=True)
    with open(os.path.join(THEME_DIR, "data", "site.json"), "w", encoding="utf-8") as f:
        json.dump(site, f, ensure_ascii=False, indent=1)
    # theme assets = the static site's assets (fonts, css, js, images; client logos and case images seed the media library)
    dst = os.path.join(THEME_DIR, "assets")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(OUT, "assets"), dst)
    print("theme fragments:", len(pages), "· cases:", len(cases), "· testimonials:", len(seed["testimonials"]))

if THEME:
    export_theme()
else:
    print("ok")
    subprocess.run([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, MKN_TARGET="theme"), check=True)
