# Part 6: Nginx — Reverse Proxy

> ⏱️ เวลาโดยประมาณ: 2 ชั่วโมง

## 🎯 สิ่งที่จะได้เรียนรู้ใน Part นี้

- เข้าใจว่า Nginx คืออะไร และ Reverse Proxy ทำงานยังไง
- อ่าน nginx.conf ออกทุกบรรทัด
- เข้าใจ Nginx Dockerfile
- เห็นภาพ docker-compose.yml เต็มรูปแบบ 3 services
- ตั้งค่า Static Files ให้ Nginx serve
- รัน Full Stack: Nginx + Django + PostgreSQL 🎉

---

## 1. Nginx คืออะไร?

**Nginx** (อ่านว่า "engine-x") คือ **Web Server** และ **Reverse Proxy** ที่ได้รับความนิยมสูงสุดอันหนึ่ง:

- 🌐 ใช้โดย **~34% ของเว็บไซต์ทั่วโลก**
- ⚡ เร็วมากในการ serve static files (CSS, JS, images)
- 📦 รองรับ **หลายพัน concurrent connections** พร้อมกัน
- 🔒 จัดการ HTTPS/SSL ได้
- 🪶 ใช้ memory น้อยมาก

ถ้า Gunicorn คือ "ผู้จัดการครัว" ที่ดูแล Django workers — **Nginx คือ "พนักงานต้อนรับ"** ที่เป็นด่านแรกรับลูกค้า (request) ที่เข้ามา

---

## 2. Reverse Proxy อธิบายง่ายๆ

### 🍽️ Analogy: ร้านอาหาร

**Nginx = พนักงานต้อนรับ (Receptionist)**, **Django/Gunicorn = พ่อครัว (Chef)**

- ลูกค้าไม่เคยเข้าครัวโดยตรง — ทุกอย่างผ่าน receptionist
- ลูกค้าขอน้ำเปล่า (static file)? → Receptionist ส่งเองได้เลย ไม่ต้องรอพ่อครัว
- ลูกค้าสั่งอาหาร (API request)? → Receptionist ส่ง order ไปให้พ่อครัว

### Diagram: มี Nginx vs ไม่มี

```
❌ Without Nginx:
┌──────────┐
│ Internet │──── request ────►  Django (ทำทุกอย่างเอง)
│          │                      • รับ request
│          │                      • ประมวลผล API
│          │                      • serve CSS, JS, images ← ช้า!
│          │                      • จัดการ HTTPS ← ไม่เหมาะ!
└──────────┘

✅ With Nginx:
┌──────────┐         ┌─────────┐         ┌──────────┐
│ Internet │── req ──►│  Nginx  │── API ──►│  Django  │
│          │         │         │  only    │ (Gunicorn)│
│          │         │ • HTTPS │         │          │
│          │         │ • Static│         │ ทำแค่ API │
│          │         │   Files │         │          │
└──────────┘         └─────────┘         └──────────┘
```

### ข้อดีของ Reverse Proxy:

| ข้อดี | อธิบาย |
|-------|--------|
| **Security** | Django ซ่อนอยู่หลัง Nginx — internet เข้าถึง Django ตรงๆ ไม่ได้ |
| **Performance** | Nginx serve static files เร็วกว่า Django 10-100 เท่า |
| **HTTPS** | Nginx จัดการ SSL/TLS certificate — Django ไม่ต้องรู้เรื่อง HTTPS |
| **Load Balancing** | (อนาคต) สามารถกระจาย request ไปหลาย Django servers ได้ |

---

## 3. nginx.conf — อธิบายทีละบรรทัด

เปิดไฟล์ `sample/nginx/nginx.conf`:

```nginx
# =============================================================================
# Nginx Configuration
# =============================================================================
# This config sets up Nginx as a reverse proxy for Django/Gunicorn
# and serves static files directly.
# =============================================================================

upstream django {
    # "web" is the service name in docker-compose.yml
    # Docker Compose DNS resolves this to the Django container
    server web:8000;
}

server {
    listen 80;
    server_name _;

    # Maximum upload size (adjust as needed)
    client_max_body_size 10M;

    # =========================================================================
    # Static files — served directly by Nginx (fast!)
    # =========================================================================
    location /static/ {
        alias /app/staticfiles/;
    }

    # =========================================================================
    # All other requests — forwarded to Django/Gunicorn
    # =========================================================================
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### อธิบายทีละส่วน:

#### `upstream django { ... }`

```nginx
upstream django {
    server web:8000;
}
```

- กำหนดว่า "django" คืออะไร → คือ server ที่ `web:8000`
- `web` = ชื่อ service ใน docker-compose.yml — Docker Compose DNS จะ resolve ชื่อนี้เป็น IP ของ container `web`
- `8000` = port ที่ Gunicorn ฟังอยู่

💡 **Key Insight**: ชื่อ `web` ที่นี่ **ต้องตรงกับชื่อ service** ใน docker-compose.yml — ถ้าไม่ตรง Nginx จะหา container ไม่เจอ!

#### `server { ... }`

```nginx
server {
    listen 80;        # ฟังที่ port 80 (HTTP)
    server_name _;    # รับทุก domain name (_ = wildcard)
    client_max_body_size 10M;  # ขนาดไฟล์ upload สูงสุด 10MB
    ...
}
```

#### `location /static/ { ... }` — Static Files

```nginx
location /static/ {
    alias /app/staticfiles/;
}
```

- request ที่ขึ้นต้นด้วย `/static/` → **Nginx ส่งไฟล์เองโดยตรง**
- ไม่ส่งต่อไป Django เลย — เร็วมาก! ⚡
- `alias /app/staticfiles/` = ไฟล์อยู่ที่ path นี้ใน container
- path นี้มาจาก shared volume `static_volume` ที่ Django เขียนไฟล์ลงไป

#### `location / { ... }` — ส่งต่อไป Django

```nginx
location / {
    proxy_pass http://django;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

- **request อื่นๆ ทั้งหมด** (API, Admin, etc.) → ส่งต่อไป Django
- `proxy_pass http://django` = ส่ง request ไปที่ upstream ที่ชื่อ `django` (คือ `web:8000`)

**Proxy Headers** — สำคัญมาก:

| Header | ค่า | ทำไมต้องมี |
|--------|-----|----------|
| `Host` | domain ที่ client ใช้ | Django รู้ว่า request มาจาก domain ไหน |
| `X-Real-IP` | IP จริงของ client | ไม่งั้น Django จะเห็นแค่ IP ของ Nginx |
| `X-Forwarded-For` | chain ของ IPs | กรณีผ่าน proxy หลายชั้น |
| `X-Forwarded-Proto` | `http` หรือ `https` | Django รู้ว่า request มาผ่าน HTTPS หรือเปล่า |

```
Request Flow:

Client (IP: 203.0.113.50) ──► Nginx ──► Django

ถ้าไม่มี proxy headers:
  Django เห็น: IP = 172.18.0.3 (IP ของ Nginx container)  ← ผิด!

ถ้ามี proxy headers:
  Django เห็น: IP = 203.0.113.50 (IP จริงของ client)    ← ถูก!
```

---

## 4. Nginx Dockerfile — สั้นมาก!

เปิดไฟล์ `sample/nginx/Dockerfile`:

```dockerfile
# Uses the official Nginx Alpine image (very small ~5MB)
# and replaces the default config with our custom one.

FROM nginx:1.27-alpine

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom config
COPY nginx.conf /etc/nginx/conf.d/
```

แค่ 3 คำสั่ง!

| บรรทัด | ทำอะไร |
|--------|--------|
| `FROM nginx:1.27-alpine` | ใช้ Nginx 1.27 Alpine เป็น base (เล็กมาก ~5MB!) |
| `RUN rm ...default.conf` | ลบ config เริ่มต้นของ Nginx (หน้า "Welcome to nginx!") |
| `COPY nginx.conf ...` | ใส่ config ของเราเข้าไปแทน |

---

## 5. docker-compose.yml เต็มรูปแบบ

ตอนนี้มาดูภาพรวมอีกครั้ง — ทั้ง 3 services ทำงานร่วมกันยังไง:

```
┌──────────────────────────────────────────────────┐
│              Docker Compose Network               │
│                                                  │
│  ┌──────┐      ┌──────────┐      ┌──────────┐   │
│  │  db  │◄────►│   web    │◄────►│  nginx   │──►│── Port 80 ──► Internet
│  │      │      │          │      │          │   │
│  │ 5432 │      │   8000   │      │    80    │   │
│  └──┬───┘      └──┬───────┘      └──┬───────┘   │
│     │              │                 │           │
│     ▼              ▼                 ▼           │
│  pgdata      static_volume     static_volume     │
│  (data)       (write)           (read)           │
└──────────────────────────────────────────────────┘
```

Key points:
- **เฉพาะ `nginx` ที่เปิด port ออก internet** (port 80)
- `web` **ไม่เปิด port** ออกข้างนอก — ปลอดภัย!
- `static_volume` ถูก **share** ระหว่าง `web` (เขียน collectstatic) กับ `nginx` (อ่านและ serve)
- `pgdata` เก็บข้อมูล database — persistent ไม่หาย

---

## 6. Collect Static Files & Run

### Full startup sequence:

```bash
cd ~/django-postgresql-nginx-docker/sample

# Step 1: Build และ start ทุก services
docker compose up -d --build
```

> rebuild images ใหม่ แล้ว start ทุก container

```bash
# Step 2: Run migrations
docker compose exec web python manage.py migrate
```

> สร้าง tables ใน database

```bash
# Step 3: Collect static files
docker compose exec web python manage.py collectstatic --noinput
```

> รวม static files (CSS, JS ของ Django Admin, DRF) ไว้ที่ `/app/staticfiles/`
> `--noinput` = ไม่ต้องถามยืนยัน

**แสดงผล:**
```
128 static files copied to '/app/staticfiles'.
```

```bash
# Step 4: (ถ้ายังไม่มี) สร้าง superuser
docker compose exec web python manage.py createsuperuser
```

### ทดสอบ! 🎉

เปิด browser:

| URL | สิ่งที่ควรเห็น |
|-----|-------------|
| `http://server-ip/` | DRF default page หรือ 404 (ไม่มี root URL) |
| `http://server-ip/admin/` | Django Admin — **มี CSS สวยงาม!** ✨ |
| `http://server-ip/api/notes/` | DRF Browsable API — สร้าง/อ่าน/แก้/ลบ notes ได้ |

📝 **Note**: url ใช้ port 80 (HTTP default) — ไม่ต้องพิมพ์ `:8000` อีกต่อไปแล้ว!

---

## 7. ทดสอบ Static Files

### วิธีเช็คว่า Nginx serve static files ถูกต้อง

**วิธีง่ายสุด**: เปิด `/admin/` — ถ้้า **CSS โหลด** (หน้าสวย มีสี มี layout) = ✅ Nginx serve static files ได้

ถ้าหน้า Admin **เป็นขาวเปล่า ไม่มี CSS** = ❌ Static files มีปัญหา

### ดู Nginx Access Logs

```bash
docker compose logs nginx
```

**แสดงผล (เมื่อมีคนเข้าเว็บ):**
```
sample-nginx-1  | 203.0.113.50 - - [01/Jan/2025:00:00:00 +0000] "GET /admin/ HTTP/1.1" 200 ...
sample-nginx-1  | 203.0.113.50 - - [01/Jan/2025:00:00:00 +0000] "GET /static/admin/css/base.css HTTP/1.1" 200 ...
```

- `200` = success 🟢
- `/static/admin/css/base.css` → Nginx serve ไฟล์ CSS ได้ ✅

### Debug ถ้า Static Files ไม่ work

```bash
# 1. ดูว่า Django สร้างไฟล์ไว้ไหม?
docker compose exec web ls /app/staticfiles/

# 2. ดูว่า Nginx เห็นไฟล์เดียวกันไหม?
docker compose exec nginx ls /app/staticfiles/

# 3. ถ้าไม่มีไฟล์ → collectstatic ใหม่
docker compose exec web python manage.py collectstatic --noinput
```

---

## 🤖 เมื่อติดปัญหา — ลองใช้ AI ช่วย Debug

ถ้าเจอ error กับ Nginx ลอง copy error message แล้วใช้ prompt นี้:

```
ฉันกำลังเรียนรู้เรื่อง Nginx reverse proxy กับ Django + Docker Compose
ฉันเห็น error นี้ใน browser หรือ logs:

[วาง error message หรืออธิบาย symptom เช่น "502 Bad Gateway" หรือ "Admin CSS ไม่โหลด"]

docker-compose.yml: [วาง relevant section]
nginx.conf: [วาง content]

ช่วยอธิบายว่า:
1. Error นี้หมายความว่าอะไร?
2. สาเหตุน่าจะเป็นอะไร?
3. ฉันควรตรวจสอบอะไรบ้าง? (อย่าบอกคำตอบตรงๆ แต่ช่วย guide ให้ฉันหาคำตอบเอง)
```

💡 **Tip**: วิธี debug Nginx แบบเป็นระบบ:

```bash
# เห็น 502 Bad Gateway?
docker compose ps          # web service รันอยู่ไหม?
docker compose logs web    # Gunicorn มี error อะไร?

# Static files ไม่โหลด?
docker compose exec web ls /app/staticfiles/     # web มีไฟล์ไหม?
docker compose exec nginx ls /app/staticfiles/   # nginx เห็นไฟล์ไหม?

# Nginx error log
docker compose logs nginx
```

---

## 📋 สรุป

ใน Part นี้เราได้เรียนรู้ Nginx:

| หัวข้อ | สิ่งที่เรียนรู้ |
|--------|---------------|
| **Nginx คืออะไร** | Web server + Reverse proxy — พนักงานต้อนรับของ app |
| **Reverse Proxy** | Nginx รับ request, ส่งต่อ API ไป Django, serve static files เอง |
| **nginx.conf** | `upstream` (กำหนด backend), `location` (route requests) |
| **Proxy Headers** | ส่ง IP จริงของ client ให้ Django (X-Real-IP, X-Forwarded-For) |
| **Static Files** | Django สร้าง → shared volume → Nginx serve |
| **Full Stack** | 3 services ทำงานร่วมกัน: Nginx → Django → PostgreSQL |

🎉 **ตอนนี้เรามี full stack ที่ทำงานได้จริงแล้ว!**

```
Internet → Nginx (port 80) → Django/Gunicorn (port 8000) → PostgreSQL (port 5432)
```

ใน Part ถัดไป เราจะทำให้ระบบ **พร้อมสำหรับ production จริงๆ** — Domain, HTTPS, Security, Backup!

---

## 🧪 ลองทำ

1. **ทดสอบ API**: เปิด `http://server-ip/api/notes/` ใน browser — ลองสร้าง note ใหม่ผ่าน DRF browsable API

2. **ดู Nginx logs**: เปิดหน้าเว็บหลายๆ หน้า แล้วรัน `docker compose logs nginx` — ลองอ่าน log แต่ละบรรทัด เข้าใจไหม?

3. **ทดลองแก้ nginx.conf**: ลองเปลี่ยน `client_max_body_size 10M;` เป็น `1M` แล้ว rebuild (`docker compose up -d --build`) — จะเกิดอะไรขึ้นถ้า upload ไฟล์ใหญ่กว่า 1MB?

4. **ตอบคำถาม**: ทำไม Nginx ถึง serve static files ได้เร็วกว่า Django? (Hint: Nginx ถูกออกแบบมาเพื่อ serve ไฟล์, Django ถูกออกแบบมาเพื่อประมวลผล Python code)

---

[← Part 5: Docker Compose](part-5-docker-compose.md) | [Part 7: Production Readiness →](part-7-production-readiness.md)
