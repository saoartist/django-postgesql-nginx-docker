# Part 2: ทำความเข้าใจ Django Project

> ⏱️ เวลาโดยประมาณ: 30 นาที

## 🎯 สิ่งที่จะได้เรียนรู้ใน Part นี้

- เข้าใจโครงสร้าง Sample Project (Notes API)
- รู้จัก Settings ที่สำคัญสำหรับ Production
- เข้าใจ Environment Variables และทำไมต้องใช้
- เข้าใจความต่าง Development vs Production
- รู้ว่า Gunicorn คืออะไร และทำไมต้องใช้แทน `runserver`

---

## 1. Overview ของ Sample Project

เรามาดูโครงสร้างของ project ที่เราจะ deploy กัน — เป็น **Notes API** ง่ายๆ ที่รองรับ CRUD (Create, Read, Update, Delete)

```
sample/
├── app/                        # 🐍 Django project
│   ├── Dockerfile              # คำสั่งสร้าง Docker image สำหรับ Django
│   ├── requirements.txt        # Python dependencies
│   ├── manage.py               # Django management script
│   ├── config/                 # Django settings & configuration
│   │   ├── __init__.py
│   │   ├── settings.py         # ⭐ ไฟล์สำคัญ — ค่าตั้งค่าทั้งหมด
│   │   ├── urls.py             # URL routing หลัก
│   │   └── wsgi.py             # Entry point สำหรับ Gunicorn
│   └── notes/                  # 📝 Notes app (CRUD)
│       ├── __init__.py
│       ├── admin.py            # Django Admin registration
│       ├── models.py           # Note model: title, body, timestamps
│       ├── serializers.py      # DRF ModelSerializer
│       ├── urls.py             # Router-based URLs
│       └── views.py            # ModelViewSet (full CRUD)
├── nginx/
│   ├── Dockerfile              # คำสั่งสร้าง Docker image สำหรับ Nginx
│   └── nginx.conf              # Nginx configuration
├── docker-compose.yml          # ⭐ จัดการ 3 services: db, web, nginx
└── .env.example                # ⭐ Template สำหรับ environment variables
```

### ไฟล์สำคัญที่ต้องเข้าใจ

ไม่ต้องจำทุกไฟล์ — แค่โฟกัสที่ 3 ไฟล์หลัก:

| ไฟล์ | ทำหน้าที่อะไร |
|------|--------------|
| `config/settings.py` | ศูนย์กลางค่าตั้งค่าทั้งหมดของ Django |
| `.env.example` | Template ค่า secret ที่ต้องตั้งเอง |
| `docker-compose.yml` | กำหนดว่าจะรัน services อะไรบ้าง (จะเรียนใน Part 5) |

---

## 2. settings.py — สิ่งที่ต้องเข้าใจก่อน Deploy

`settings.py` คือ "สมอง" ของ Django project — ค่าตั้งค่าทุกอย่างอยู่ที่นี่ มาดูเฉพาะส่วนที่สำคัญสำหรับ deployment:

### SECRET_KEY — กุญแจลับของ Django

```python
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
```

- Django ใช้ `SECRET_KEY` ในการเข้ารหัส session, CSRF token, password hashing
- ถ้าคนอื่นรู้ SECRET_KEY ของเรา = **ระบบไม่ปลอดภัย**
- ใน production ต้องเปลี่ยนเป็น random string ยาวๆ ที่ไม่มีใครเดาได้

💡 **Tip**: สร้าง SECRET_KEY ใหม่ด้วย Python:
```python
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### DEBUG — โหมดพัฒนา vs โหมด Production

```python
DEBUG = config('DEBUG', default=False, cast=bool)
```

- `DEBUG=True` → Django แสดง error detail ทั้งหมดบนหน้าเว็บ (สะดวกตอน dev)
- `DEBUG=False` → Django ซ่อน error detail (จำเป็นสำหรับ production)

⚠️ **ถ้าเปิด `DEBUG=True` บน production** → ใครก็เห็น code, database structure, environment variables ของเรา = **อันตรายมาก!**

ลองนึกภาพ: ใน DEBUG mode ถ้ามี error Django จะแสดงหน้า error สีเหลืองที่มี:
- source code บรรทัดที่ error
- ค่า variables ทั้งหมดใน request
- database queries ที่ถูกรัน
- settings ทั้งหมด (รวมถึง SECRET_KEY!)

### ALLOWED_HOSTS — ใครเข้าถึงได้บ้าง?

```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
```

- เป็น list ของ domain/IP ที่อนุญาตให้เข้า Django
- ถ้าใครเข้ามาจาก domain ที่ไม่อยู่ใน list → Django จะ reject
- ใน production ตั้งเป็น domain จริง เช่น `ALLOWED_HOSTS=my-notes-app.com,www.my-notes-app.com`

📝 **Note**: `Csv()` จาก python-decouple แปลง string `"localhost,127.0.0.1"` เป็น Python list `['localhost', '127.0.0.1']` ให้อัตโนมัติ

### DATABASES — เชื่อมต่อฐานข้อมูล

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='notesdb'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

สังเกตว่า:
- ใช้ **PostgreSQL** ไม่ใช่ SQLite — เพราะ PostgreSQL เหมาะกับ production มากกว่า
- ทุกค่า (ชื่อ DB, user, password, host, port) อ่านจาก **environment variables** — ไม่ได้ hardcode ไว้ใน code
- `DB_HOST=db` — ค่านี้คือชื่อ service ใน Docker Compose (จะเข้าใจเพิ่มใน Part 5)

### STATIC_ROOT — ไฟล์ CSS, JS, images

```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

- `STATIC_URL` = URL prefix สำหรับ static files (เช่น `/static/admin/css/base.css`)
- `STATIC_ROOT` = โฟลเดอร์ที่ Django จะรวม static files ทั้งหมดไว้เมื่อรัน `collectstatic`
- ใน production, **Nginx** จะเป็นคนเสิร์ฟไฟล์จาก `STATIC_ROOT` — ไม่ใช่ Django

---

## 3. Environment Variables ด้วย python-decouple

### ทำไมห้าม Hardcode ค่า Secret?

ลองนึกภาพ... ถ้าเราเขียนแบบนี้ใน `settings.py`:

```python
# ❌ อย่าทำแบบนี้!
SECRET_KEY = 'my-super-secret-key-12345'
DATABASES = {
    'default': {
        'PASSWORD': 'real-database-password',
    }
}
```

แล้วเรา push code ขึ้น GitHub... **ทุกคนที่เข้า repository เห็น password ของเราทันที!**

📝 **Note**: บน GitHub มี bot ที่ scan public repos หา secret keys อัตโนมัติ — ถ้าเจอ AWS key อาจถูกใช้ในไม่กี่วินาที!

### วิธีที่ถูกต้อง: ใช้ Environment Variables

`python-decouple` คือ library ที่ช่วยอ่านค่า configuration จากไฟล์ `.env`:

```python
from decouple import config

# อ่านค่า SECRET_KEY จาก .env file หรือ environment variable
# ถ้าหาไม่เจอ ใช้ default value
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
```

### `.env.example` vs `.env`

| ไฟล์ | Commit ขึ้น Git? | เนื้อหา |
|------|------------------|--------|
| `.env.example` | ✅ ใช่ | Template — ค่าตัวอย่าง ไม่ใช่ค่าจริง |
| `.env` | ❌ ห้าม! | ค่าจริงที่ใช้เชื่อมต่อ database, secret keys |

ดูไฟล์ `.env.example` ของเรา:

```bash
# Django
SECRET_KEY=change-me-to-a-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=notesdb
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# CORS (frontend URL)
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

เมื่อจะ deploy จริง เราจะ:
1. Copy `.env.example` เป็น `.env`
2. เปลี่ยนค่าให้เป็นค่าจริงของ production
3. **ห้ามเด็ดขาดที่จะ commit `.env` ขึ้น Git!**

---

## 4. Development vs Production — ต่างกันตรงไหน?

นี่คือภาพรวมที่สำคัญมาก — หลายอย่างที่ใช้ตอน dev **ห้ามใช้ใน production**:

| | 🏠 Development | 🏭 Production |
|--|---------------|--------------|
| **Server** | `python manage.py runserver` | **Gunicorn** (WSGI server) |
| **Database** | SQLite (ง่าย, ไฟล์เดียว) | **PostgreSQL** (เสถียร, concurrent) |
| **DEBUG** | `True` (เห็น error detail) | `False` (ซ่อน error) |
| **Static Files** | Django serve เอง | **Nginx** serve (เร็วกว่ามาก) |
| **HTTPS** | ไม่จำเป็น | **จำเป็น** (security) |
| **SECRET_KEY** | ค่า default ได้ | **ต้องเป็น random string** |
| **ALLOWED_HOSTS** | `localhost` | **domain จริง** |
| **Workers** | 1 (single thread) | **หลายตัว** (Gunicorn workers) |

💡 **Key Insight**: `runserver` ไม่ได้ออกแบบมาสำหรับ production — Django docs เขียนไว้ชัดเจนว่า "DO NOT USE THIS SERVER IN A PRODUCTION SETTING"

---

## 5. Gunicorn คืออะไร?

### ปัญหาของ `runserver`

`python manage.py runserver` คือ development server ที่มากับ Django — มันทำงานแบบ **single-threaded** คือรับ request ได้ทีละอัน

ลองนึกภาพร้านอาหาร:
- `runserver` = **พนักงานคนเดียว** ที่รับออเดอร์ ทำอาหาร เสิร์ฟ เก็บจาน คนเดียว → ถ้ามีลูกค้า 10 คนพร้อมกัน จะรอนานมาก!

### Gunicorn = พนักงานหลายคน

**Gunicorn** (Green Unicorn) คือ **Production WSGI Server** สำหรับ Python:

- `Gunicorn` = **ผู้จัดการร้าน + พนักงานหลายคน** → รับ request หลายอันพร้อมกันได้

```
runserver (development):
Request 1 → [Django] → Response 1
Request 2 → (รอ...) → [Django] → Response 2
Request 3 → (รอ...) → (รอ...) → [Django] → Response 3

Gunicorn (production):
Request 1 → [Worker 1] → Response 1
Request 2 → [Worker 2] → Response 2   ← ทำพร้อมกัน!
Request 3 → [Worker 3] → Response 3   ← ทำพร้อมกัน!
```

ใน project ของเรา Gunicorn ถูกตั้งค่าไว้ใน `docker-compose.yml`:

```yaml
web:
  build: ./app
  command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

อธิบาย:
- `config.wsgi:application` — บอก Gunicorn ว่า Django app อยู่ที่ไหน
- `--bind 0.0.0.0:8000` — ฟังที่ port 8000, `0.0.0.0` = รับ connection จากทุก IP
- `--workers 3` — สร้าง worker 3 ตัว = รองรับ request พร้อมกัน 3 อัน

---

## 📋 สรุป

ใน Part นี้เราได้เข้าใจ:

| หัวข้อ | สิ่งที่เรียนรู้ |
|--------|---------------|
| **Project Structure** | โครงสร้างของ Notes API — Django + DRF + PostgreSQL |
| **settings.py** | ค่าตั้งค่าสำคัญ: SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASES, STATIC_ROOT |
| **Environment Variables** | ทำไมต้องใช้ `.env` แทน hardcode — security! |
| **Dev vs Production** | `runserver` vs Gunicorn, SQLite vs PostgreSQL, DEBUG True vs False |
| **Gunicorn** | Production WSGI server ที่รัน Django ด้วย multiple workers |

📝 **Note**: ยังไม่ต้องจำทุกอย่าง — เราจะกลับมาดูไฟล์เหล่านี้อีกเมื่อเรา deploy จริงใน Part ถัดๆ ไป

---

## 🧪 ลองทำ

1. **อ่าน `settings.py`**: เปิดไฟล์ `sample/app/config/settings.py` อ่านทั้งไฟล์ — ลองหาว่ามี `config()` กี่ที่? แต่ละที่อ่านค่าอะไร?

2. **ดู `.env.example`**: เปิดไฟล์ `sample/.env.example` — ค่าไหนที่ต้องเปลี่ยนก่อน deploy? ค่าไหนใช้ค่า default ได้?

3. **ตอบคำถาม**: ถ้าเราตั้ง `DEBUG=True` บน production server จะเกิดอะไรขึ้นถ้ามี error? ใครจะเห็นอะไรบ้าง?

4. **ดู models.py**: เปิด `sample/app/notes/models.py` — Note model มี field อะไรบ้าง? ทำไมถึงมี `created_at` และ `updated_at`?

---

[← Part 1: เตรียมเครื่องมือ](part-1-setup-environment.md) | [Part 3: Git & Server →](part-3-git-and-server.md)
