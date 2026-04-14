# Part 7: Production Readiness — Domain, HTTPS, Security

> ⏱️ เวลาโดยประมาณ: 1-2 ชั่วโมง

## 🎯 สิ่งที่จะได้เรียนรู้ใน Part นี้

- ตั้งค่า Domain & DNS ให้ชี้มาที่ server
- ติดตั้ง HTTPS ด้วย Let's Encrypt (ฟรี!)
- Security พื้นฐานสำหรับ production
- Backup & Restore Database
- Run Migration ใน Production อย่างปลอดภัย

---

## 1. Domain & DNS

### Domain Name คืออะไร?

ตอนนี้เราเข้าเว็บด้วย IP เช่น `http://203.0.113.50` — จำยาก ไม่น่าเชื่อถือ

**Domain Name** คือ "ชื่อ" ที่ใช้แทน IP:
- `http://203.0.113.50` → `http://my-notes-app.com` ← จำง่ายกว่า!

### DNS คืออะไร?

**DNS** (Domain Name System) = "สมุดโทรศัพท์ของ Internet"

```
User พิมพ์: my-notes-app.com
                    │
                    ▼
             DNS Server ค้นหา
             "my-notes-app.com อยู่ที่ IP ไหน?"
                    │
                    ▼
             ตอบ: 203.0.113.50
                    │
                    ▼
             Browser เชื่อมต่อไป 203.0.113.50
```

### ตั้งค่า A Record

ที่ Domain Registrar ของคุณ (เช่น Cloudflare, Namecheap, GoDaddy, Google Domains — ใช้เจ้าไหนก็ได้):

1. ไปที่ DNS Settings ของ domain
2. เพิ่ม **A Record**:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `@` | `203.0.113.50` | 300 |
| A | `www` | `203.0.113.50` | 300 |

> `@` = root domain (เช่น `my-notes-app.com`)
> `www` = subdomain `www.my-notes-app.com`
> TTL = Time To Live (วินาที) — 300 = 5 นาที (เปลี่ยน DNS แล้วต้องรอ propagate)

### ทดสอบ DNS

```bash
# ทดสอบจากเครื่องของคุณ (ไม่ใช่ server)
ping my-notes-app.com
```

**แสดงผลที่ถูกต้อง:**
```
PING my-notes-app.com (203.0.113.50): 56 data bytes
64 bytes from 203.0.113.50: icmp_seq=0 ttl=64 time=5.2 ms
```

> ถ้า IP ตรงกับ server ของเรา = DNS ทำงานแล้ว ✅

```bash
curl http://my-notes-app.com/api/notes/
```

> ทดสอบว่า request ผ่าน domain ถึง server ได้

### อัพเดท ALLOWED_HOSTS

แก้ไขไฟล์ `.env` บน server:

```bash
# แก้ .env
nano ~/django-postgresql-nginx-docker/sample/.env
```

เปลี่ยน:

```
ALLOWED_HOSTS=localhost,127.0.0.1,my-notes-app.com,www.my-notes-app.com
```

### อัพเดท server_name ใน nginx.conf

แก้ไข `sample/nginx/nginx.conf`:

```nginx
server {
    listen 80;
    server_name my-notes-app.com www.my-notes-app.com;
    ...
}
```

> เปลี่ยนจาก `_` (wildcard) เป็น domain จริง

Rebuild:

```bash
cd ~/django-postgresql-nginx-docker/sample
docker compose up -d --build
```

---

## 2. HTTPS ด้วย Let's Encrypt

### ทำไม HTTPS ถึงจำเป็น?

| ❌ HTTP | ✅ HTTPS |
|---------|---------|
| ข้อมูลส่งแบบ plain text | ข้อมูลถูกเข้ารหัส 🔐 |
| ใครก็ดักฟังได้ (WiFi สาธารณะ) | คนดักฟังอ่านไม่ออก |
| Browser แสดง "Not Secure" ⚠️ | Browser แสดง 🔒 |
| SEO ranking ต่ำ | Google ให้คะแนน SEO สูงกว่า |

**ใน production, HTTPS ไม่ใช่ตัวเลือก — เป็นสิ่งจำเป็น!**

### SSL/TLS Certificate คืออะไร?

- **Certificate** = ใบรับรองดิจิทัลที่พิสูจน์ว่า "domain นี้เป็นของเราจริงๆ"
- **Let's Encrypt** = ออก certificate ฟรี! อัตโนมัติ! 🎉

### ติดตั้ง Certbot ด้วย Docker

เราจะเพิ่ม **Certbot** service เข้า docker-compose.yml:

#### Step 1: แก้ docker-compose.yml

เพิ่ม certbot service และ volumes ใหม่:

```yaml
services:
  # ... db, web เหมือนเดิม ...

  nginx:
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"   # ← เพิ่ม HTTPS port!
    volumes:
      - static_volume:/app/staticfiles
      - certbot_conf:/etc/letsencrypt      # ← certificate files
      - certbot_www:/var/www/certbot        # ← challenge files
    depends_on:
      - web

  certbot:
    image: certbot/certbot
    volumes:
      - certbot_conf:/etc/letsencrypt
      - certbot_www:/var/www/certbot

volumes:
  pgdata:
  static_volume:
  certbot_conf:     # ← เพิ่ม
  certbot_www:      # ← เพิ่ม
```

#### Step 2: แก้ nginx.conf สำหรับ HTTPS

**Phase 1 — ขอ certificate ก่อน** (ยังเป็น HTTP):

```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name my-notes-app.com www.my-notes-app.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect ทุกอย่างไป HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}
```

> `/.well-known/acme-challenge/` = path ที่ Let's Encrypt ใช้ตรวจสอบว่าเราเป็นเจ้าของ domain

Apply config:

```bash
docker compose up -d --build
```

ขอ certificate:

```bash
docker compose run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  -d my-notes-app.com -d www.my-notes-app.com \
  --email your@email.com --agree-tos --no-eff-email
```

> `certonly` = ขอ cert อย่างเดียว ไม่ install
> `--webroot` = ใช้ webroot plugin (ผ่าน Nginx)
> `-d` = domain ที่ต้องการ cert
> `--agree-tos` = ยอมรับ terms of service

**แสดงผลที่ถูกต้อง:**
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/my-notes-app.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/my-notes-app.com/privkey.pem
```

#### Step 3: เพิ่ม HTTPS ใน nginx.conf

**Phase 2 — เปิดใช้ HTTPS:**

```nginx
upstream django {
    server web:8000;
}

# HTTP → Redirect to HTTPS
server {
    listen 80;
    server_name my-notes-app.com www.my-notes-app.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS
server {
    listen 443 ssl;
    server_name my-notes-app.com www.my-notes-app.com;

    ssl_certificate /etc/letsencrypt/live/my-notes-app.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/my-notes-app.com/privkey.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /app/staticfiles/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Apply:

```bash
docker compose up -d --build
```

#### Step 4: ทดสอบ

เปิด browser ไปที่ `https://my-notes-app.com`:

- ✅ ควรเห็น 🔒 ใน URL bar
- ✅ เข้า `http://my-notes-app.com` จะ redirect ไป `https://` อัตโนมัติ

#### Step 5: Auto-renewal

Let's Encrypt certificate หมดอายุทุก 90 วัน — ต้อง renew อัตโนมัติ:

```bash
# ทดสอบ renewal (dry run)
docker compose run --rm certbot renew --dry-run
```

ตั้ง cron job สำหรับ auto-renewal:

```bash
crontab -e
```

เพิ่มบรรทัดนี้:

```
0 12 * * * cd /home/your-name/django-postgresql-nginx-docker/sample && docker compose run --rm certbot renew && docker compose exec nginx nginx -s reload
```

> รันทุกวันเวลาเที่ยง — เช็คว่าต้อง renew ไหม, ถ้า renew แล้ว reload nginx

---

## 3. Security พื้นฐาน

### Checklist ก่อนเปิดให้คนใช้จริง:

#### ✅ Django Settings

```bash
# แก้ .env
nano ~/django-postgresql-nginx-docker/sample/.env
```

```
DEBUG=False                      # ← ห้าม True ใน production!
SECRET_KEY=<random-string-ยาวๆ>  # ← ต้องเปลี่ยนจาก default!
ALLOWED_HOSTS=my-notes-app.com,www.my-notes-app.com
```

สร้าง SECRET_KEY ใหม่:

```bash
docker compose exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

💡 หลังเปิด HTTPS อย่าลืมเพิ่มใน `settings.py`:

```python
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://my-notes-app.com',
    cast=Csv(),
)
```

#### ✅ Firewall

```bash
# ดู firewall status
sudo ufw status

# ถ้ายังไม่ได้เปิด:
sudo ufw allow 22     # SSH
sudo ufw allow 80     # HTTP (redirect to HTTPS)
sudo ufw allow 443    # HTTPS
sudo ufw enable       # เปิดใช้ firewall

sudo ufw status
```

**แสดงผล:**
```
Status: active
To                         Action      From
--                         ------      ----
22                         ALLOW       Anywhere
80                         ALLOW       Anywhere
443                        ALLOW       Anywhere
```

> เปิดแค่ 3 ports ที่จำเป็น — อื่นๆ ปิดหมด!

#### ✅ Strong Passwords

- Database password → เปลี่ยนจาก `postgres` เป็น random string
- Django admin → ใช้ password ที่แข็งแรง
- ⚠️ หลังเปลี่ยน DB password ต้อง update `.env` ด้วย **และ** `docker compose down -v` + `up` ใหม่ (เพราะ volume เก็บ password เก่า)

#### ✅ Non-root User

ไม่ควรใช้ `root` user ในการ deploy — สร้าง user ใหม่ที่มีสิทธิ์ `sudo` แทน

#### ✅ Keep Images Updated

```bash
# pull image versions ล่าสุด
docker compose pull
docker compose up -d --build
```

---

## 4. Database Backup & Restore

### Backup — สำคัญมาก!

```bash
# Backup database เป็นไฟล์ SQL
docker compose exec db pg_dump -U postgres notesdb > backup_$(date +%Y%m%d_%H%M%S).sql
```

> `pg_dump` = PostgreSQL backup tool
> `-U postgres` = user
> `notesdb` = ชื่อ database
> `> backup_...sql` = เขียนลงไฟล์

**แสดงผล:**
```
(ไม่มี output = สำเร็จ)
```

ตรวจสอบไฟล์:

```bash
ls -lh backup_*.sql
```

```
-rw-r--r-- 1 your-name your-name 12K Jan  1 00:00 backup_20250101_120000.sql
```

### Restore

```bash
# Restore จากไฟล์ backup
docker compose exec -T db psql -U postgres notesdb < backup_20250101_120000.sql
```

> `-T` = ปิด pseudo-TTY (จำเป็นเมื่อ redirect input ด้วย `<`)

### Auto Backup ด้วย Cron

```bash
crontab -e
```

เพิ่ม:

```
0 2 * * * cd /home/your-name/django-postgresql-nginx-docker/sample && docker compose exec -T db pg_dump -U postgres notesdb > /home/your-name/backups/backup_$(date +\%Y\%m\%d).sql
```

> Backup ทุกวัน ตี 2

สร้างโฟลเดอร์ backup:

```bash
mkdir -p ~/backups
```

💡 **Tip**: สำหรับ production จริงๆ ควร copy backup ไปเก็บอีกที่ (S3, Google Cloud Storage) ด้วย — ถ้า server พังทั้ง backup ก็หาย!

---

## 5. Run Migration ใน Production

### Best Practice: Backup ก่อน Migrate เสมอ!

```bash
# Step 1: Backup database ก่อน
docker compose exec db pg_dump -U postgres notesdb > backup_before_migrate.sql

# Step 2: ดูว่ามี migration อะไรที่ยังไม่ได้ run
docker compose exec web python manage.py showmigrations
```

**แสดงผล:**
```
admin
 [X] 0001_initial
 [X] 0002_logentry_remove_auto_add
auth
 [X] 0001_initial
 ...
notes
 [X] 0001_initial
 [ ] 0002_add_category    ← ยังไม่ได้ run!
```

> `[X]` = run แล้ว, `[ ]` = ยังไม่ได้ run

```bash
# Step 3: Run migration
docker compose exec web python manage.py migrate --noinput
```

> `--noinput` = ไม่ถามยืนยัน

```bash
# Step 4: ตรวจสอบ
docker compose exec web python manage.py showmigrations
```

> ทุกอันควรเป็น `[X]` แล้ว

---

## 🤖 เมื่อติดปัญหา — ลองใช้ AI ช่วย Debug

ถ้าเจอ error เรื่อง Domain, HTTPS, หรือ Security ลอง copy error message:

```
ฉันกำลังเรียนรู้เรื่อง production deployment (Domain, HTTPS, Security)
ฉันใช้ Ubuntu 24.04, Docker Compose, Nginx, Let's Encrypt
ฉันทำตาม step [อธิบายสิ่งที่ทำ]
แล้วเจอ error นี้:

[วาง error message ที่เห็น]

ช่วยอธิบายว่า:
1. Error นี้หมายความว่าอะไร?
2. สาเหตุน่าจะเป็นอะไร?
3. ฉันควรตรวจสอบอะไรบ้าง? (อย่าบอกคำตอบตรงๆ แต่ช่วย guide ให้ฉันหาคำตอบเอง)
```

💡 **Tip**: error ที่พบบ่อยใน Part นี้:
- **CSRF verification failed** → หลังเปิด HTTPS ต้องเพิ่ม `CSRF_TRUSTED_ORIGINS` ใน settings
- **Server Error (500) ไม่มี detail** → นี่คือ behavior ปกติเมื่อ `DEBUG=False` — ดู error จริงใน `docker compose logs web`
- **Certificate error** → DNS ยังไม่ propagate หรือ port 80 ไม่เปิด — รัน `dig my-notes-app.com` เพื่อเช็ค

---

## 📋 สรุป

ใน Part นี้เราทำให้ระบบพร้อมสำหรับ production:

| หัวข้อ | สิ่งที่ทำ |
|--------|----------|
| **Domain & DNS** | ตั้ง A Record ชี้มาที่ server, อัพเดท ALLOWED_HOSTS |
| **HTTPS** | ติดตั้ง Let's Encrypt ด้วย Certbot + Docker |
| **Security** | DEBUG=False, Firewall, Strong passwords |
| **Backup** | pg_dump + cron สำหรับ auto backup |
| **Migration** | Backup → showmigrations → migrate → ตรวจสอบ |

🎉 **ตอนนี้เรามี production-ready deployment แล้ว!**

```
https://my-notes-app.com 🔒
     │
     ▼
  Nginx (443/SSL) → Django/Gunicorn → PostgreSQL
     │
   Firewall (ports 22, 80, 443 only)
```

ใน Part ถัดไป เราจะทำให้ทุกอย่าง **อัตโนมัติ** ด้วย CI/CD — push code แล้ว deploy ให้เอง!

---

## 🧪 ลองทำ

1. **ทดสอบ DNS**: ถ้ามี domain ตั้ง A Record แล้วลอง `ping` และ `curl` ดู

2. **ทดสอบ Backup/Restore**: สร้าง notes หลายๆ อัน, backup, ลบ notes ทั้งหมด, restore — ข้อมูลกลับมาไหม?

3. **ดู Firewall**: รัน `sudo ufw status` — ports ไหนเปิดอยู่? มี port ไหนที่ไม่ควรเปิดไหม?

4. **ตอบคำถาม**: ทำไมเราต้อง backup database ก่อน run migration? เกิดอะไรขึ้นได้ถ้า migration ผิดพลาด?

---

[← Part 6: Nginx](part-6-nginx.md) | [Part 8: CI/CD →](part-8-cicd.md)
