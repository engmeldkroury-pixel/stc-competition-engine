# STC v0.5 — Vercel Zero-New-Spend Runbook

## الهدف
تشغيل Python/FastAPI عند وصول فرصة بدون شراء VPS جديد، مع إبقاء Hostinger/MySQL مصدر الحقيقة الدائم.

## المعمارية

TradingView -> Hostinger Bridge -> MySQL -> Vercel `/process` -> Claim -> STC decision -> Ack + result -> MySQL

Hostinger Cron -> Vercel `/process` يعمل كـwatchdog إذا فشل الـtrigger الفوري.

## لماذا لا نعتمد على SQLite على Vercel؟
Vercel Function filesystem ليس مصدر حالة دائم. لذلك v0.5 يعالج الحدث بدون اعتماد على SQLite ويعيد النتيجة إلى Hostinger أثناء Ack.

## متغيرات Vercel السرية المطلوبة

- `STC_TRIGGER_TOKEN`: Secret لحماية `/process`.
- `STC_BRIDGE_URL`: `https://stc.feama.site`
- `STC_WORKER_TOKEN`: نفس worker_api_token الموجود سرًا في Hostinger.
- اختياري `STC_WORKER_ID=stc-vercel-worker`
- اختياري `STC_WORKER_BATCH_LIMIT=5`

لا تضع هذه القيم داخل الكود أو المحادثة.

## endpoints

- `GET /health`: فحص النسخة فقط.
- `POST /process`: محمي بـBearer `STC_TRIGGER_TOKEN`، يسحب دفعة من Bridge ويعيد النتيجة إليه.

## حدود الأمان

- لا Auto Trading.
- لا Buy/Sell.
- لا حسابات مسابقة تتعدل من هذا Processor.
- أي Signal ناتجة تظل `manual_approval_required`.

## Rollback

Vercel deployment يمكن إيقافه بدون تأثير على استقبال TradingView؛ Hostinger Bridge يظل يحتفظ بالأحداث.
