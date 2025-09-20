# 🌟 منصة سكاي للتصميم الجرافيكي
# Sky Design Platform

منصة متكاملة لإدارة طلبات التصميم الجرافيكي باللغة العربية مع واجهة سماوية متحركة

## 🚀 المميزات الأساسية

### ✨ التصميم والواجهة
- 🎨 واجهة سماوية متحركة (Sky Theme) مع تأثيرات gaming-like
- 🌐 دعم كامل للغة العربية وRTL
- 📱 تصميم متجاوب (Responsive) لجميع الأجهزة
- ✨ تأثيرات Glassmorphism وParticles
- 🎯 أنيميشنات سلسة مع floating elements

### 💻 التقنيات المستخدمة
- **Backend**: Python 3.11+ / Django 4.2.8
- **Database**: PostgreSQL (SQLite للتطوير)
- **WebSockets**: Django Channels للشات الفوري
- **Frontend**: Django Templates + Tailwind CSS + Alpine.js + HTMX
- **Task Queue**: Celery + Redis
- **Authentication**: Django Allauth

### 🎮 المميزات الخاصة
- 🎡 عجلة الحظ اليومية للجوائز
- 🧩 ألعاب البازل التفاعلية
- 💬 نظام شات فوري بين العميل والمصمم
- 🔔 إشعارات فورية عبر WebSockets
- 📊 لوحات تحكم للمدير والمصممين

## 🔧 التثبيت والتشغيل

### المتطلبات
- Python 3.11+
- pip
- Git
- Redis (اختياري للتطوير)

### خطوات التثبيت

```bash
# 1. استنساخ المشروع
git clone <repository-url>
cd skydesign

# 2. إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. نسخ ملف البيئة
cp .env.example .env
# قم بتعديل .env حسب احتياجاتك

# 5. تطبيق migrations
python manage.py migrate

# 6. إنشاء البيانات الأولية
python manage.py seed_data

# 7. تشغيل الخادم
python manage.py runserver
```

الموقع سيعمل على: http://localhost:8000

## 👤 بيانات الدخول الافتراضية

### حساب المدير (Admin)
- **Username**: admin
- **Password**: admin123
- **الصلاحيات**: كاملة

### حسابات تجريبية أخرى

| النوع | Username | Password | الدور |
|------|----------|----------|-------|
| مصمم | designer1 | designer123 | مصمم جرافيك |
| مصمم | designer2 | designer123 | مصممة |
| مدير | manager1 | manager123 | مدير تنفيذي |
| مدرس | teacher1 | teacher123 | عميل - مدرس |
| محل | shop1 | shop123 | عميل - محل |
| عميل مميز | mustafa | mustafa123 | عميل VIP |

## 📁 هيكل المشروع

```
skydesign/
├── accounts/          # نظام المستخدمين والمصادقة
├── designs/          # طلبات التصميم والمعرض
├── games/            # الألعاب التفاعلية
├── chat/             # الشات والإشعارات
├── manager/          # لوحات الإدارة
├── templates/        # قوالب HTML
│   ├── base/        # القوالب الأساسية
│   ├── accounts/    # صفحات الحسابات
│   ├── designs/     # صفحات التصاميم
│   ├── games/       # صفحات الألعاب
│   └── manager/     # لوحات الإدارة
├── static/          # الملفات الثابتة
│   ├── css/         # أنماط CSS
│   ├── js/          # JavaScript
│   └── images/      # الصور
├── media/           # ملفات المستخدمين
└── logs/            # سجلات النظام
```

## 🌍 النشر على PythonAnywhere

### 1. إنشاء حساب
- قم بإنشاء حساب على [PythonAnywhere](https://www.pythonanywhere.com)
- اختر خطة مناسبة (يمكن البدء بالمجانية)

### 2. رفع المشروع
```bash
# في PythonAnywhere Console
git clone <repository-url>
cd skydesign
mkvirtualenv skydesign --python=python3.11
pip install -r requirements.txt
```

### 3. إعداد قاعدة البيانات
```bash
# تعديل .env للإنتاج
DATABASE_URL=postgres://username:password@hostname/dbname
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic
```

### 4. إعداد Web App
- اذهب إلى Web tab
- أنشئ تطبيق جديد
- اختر Django
- أدخل المسارات:
  - Source code: `/home/username/skydesign`
  - Working directory: `/home/username/skydesign`
  - Virtual env: `/home/username/.virtualenvs/skydesign`
- في WSGI file، أضف:
```python
import sys
import os
sys.path.append('/home/username/skydesign')
os.environ['DJANGO_SETTINGS_MODULE'] = 'skydesign.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 5. إعداد Static Files
في Web tab > Static files:
- URL: `/static/`
- Directory: `/home/username/skydesign/staticfiles`
- URL: `/media/`
- Directory: `/home/username/skydesign/media`

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - تسجيل مستخدم جديد
- `POST /api/auth/login` - تسجيل الدخول
- `POST /api/auth/logout` - تسجيل الخروج
- `GET /api/auth/me` - معلومات المستخدم الحالي

### Design Requests
- `GET /api/requests/` - قائمة الطلبات
- `POST /api/requests/` - إنشاء طلب جديد
- `GET /api/requests/{id}/` - تفاصيل طلب
- `PUT /api/requests/{id}/` - تحديث طلب
- `POST /api/requests/{id}/assign` - تعيين مصمم

### Games
- `GET /api/games/wheel` - عجلة الحظ
- `POST /api/games/wheel/spin` - تدوير العجلة
- `GET /api/games/puzzle` - قائمة البازل
- `GET /api/games/leaderboard` - لوحة المتصدرين

### WebSocket Endpoints
- `ws://localhost:8000/ws/chat/{conversation_id}/` - الشات
- `ws://localhost:8000/ws/notifications/` - الإشعارات

## 🎨 تخصيص التصميم

### تغيير الألوان
قم بتعديل متغيرات CSS في `templates/base/base.html`:
```css
:root {
    --sky-500: #0EA5E9;  /* اللون الأساسي */
    --sky-600: #0284C7;  /* اللون الداكن */
    /* ... */
}
```

### إضافة خطوط
أضف خطوط Google في `<head>`:
```html
<link href="https://fonts.googleapis.com/css2?family=YourFont&display=swap" rel="stylesheet">
```

## 🧪 الاختبارات

```bash
# تشغيل جميع الاختبارات
python manage.py test

# تشغيل اختبارات محددة
python manage.py test accounts
python manage.py test designs.tests.test_models

# مع coverage
pytest --cov=.
```

## 📊 Celery & Background Tasks

للمهام الخلفية (اختياري):
```bash
# تشغيل Redis
redis-server

# تشغيل Celery Worker
celery -A skydesign worker -l info

# تشغيل Celery Beat (للمهام المجدولة)
celery -A skydesign beat -l info
```

## 🔒 الأمان

- تغيير `SECRET_KEY` في الإنتاج
- تغيير كلمة مرور admin الافتراضية
- تفعيل HTTPS في الإنتاج
- استخدام متغيرات البيئة للمعلومات الحساسة
- تحديث `ALLOWED_HOSTS` في الإنتاج

## 🤝 المساهمة

نرحب بمساهماتكم! الرجاء:
1. Fork المشروع
2. إنشاء branch جديد (`git checkout -b feature/amazing`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push للـ branch (`git push origin feature/amazing`)
5. فتح Pull Request

## 📝 الترخيص

هذا المشروع مرخص تحت [MIT License](LICENSE)

## 📞 الدعم والتواصل

- 📧 Email: support@skydesign.com
- 💬 Discord: [رابط السيرفر]
- 📱 WhatsApp: +123456789

## ✅ Checklist للإطلاق

- [x] إعداد Django والنماذج
- [x] نظام المصادقة
- [x] واجهة المستخدم الأساسية
- [x] WebSockets للشات
- [ ] واجهات API الكاملة
- [ ] لوحة الإدارة الكاملة
- [ ] لوحة المدير التنفيذي
- [ ] الألعاب التفاعلية
- [ ] نظام الدفع
- [ ] الاختبارات الشاملة
- [ ] التوثيق الكامل
- [ ] النشر على الإنتاج

---
صُنع بـ ❤️ بواسطة فريق Sky Design