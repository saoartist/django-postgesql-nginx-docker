# Part 5: Docker Compose — จัดการหลาย Container

> ⏱️ เวลาโดยประมาณ: 2 ชั่วโมง

## 🎯 สิ่งที่จะได้เรียนรู้ใน Part นี้

- เข้าใจว่าทำไมต้องใช้ Docker Compose
- อ่าน docker-compose.yml ออกทุกบรรทัด
- ใช้คำสั่ง Docker Compose ที่สำคัญได้คล่อง
- รัน Django + PostgreSQL ด้วย Docker Compose
- จัดการ Environment Variables ด้วย .env file

---

## 1. ทำไมต้อง Docker Compose?

ใน Part 4 เราเรียนรู้การรัน container ด้วย `docker run` — จำได้ไหมว่ามันยาวขนาดไหน?

```bash
# Container 1: PostgreSQL
docker run -d --name db --network mynet \
  -e POSTGRES_DB=notesdb -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres -v pgdata:/var/lib/postgresql/data \
  postgres:16-alpine

# Container 2: Django
docker run -d --name web --network mynet \
  -e DB_HOST=db -e DB_PORT=5432 -e DB_NAME=notesdb \
  -p 8000:8000 notes-api

# Container 3: Nginx
docker run -d --name nginx --network mynet \
  -p 80:80 -v static_volume:/app/staticfiles \
  my-nginx
```

😩 ปัญหา:
- **3 คำสั่งยาวๆ** — ง่ายมากที่จะพิมพ์ผิด
- **ต้องจำลำดับ** — db ต้อง start ก่อน web, web ก่อน nginx
- **ต้อง manage network เอง** — `docker network create mynet`
- **ต้อง manage volume เอง** — `docker volume create pgdata`
- **ถ้าจะ update?** — ต้อง stop, remove, run ใหม่ทุกตัว

### Docker Compose = ทุกอย่างในไฟล์เดียว

**Docker Compose** ให้เราเขียน config ของทุก container ไว้ในไฟล์ YAML ไฟล์เดียว (`docker-compose.yml`) แล้วจัดการทุกอย่างด้วยคำสั่งเดียว:

```bash
docker compose up -d --build    # สร้างและรันทุก container
docker compose down             # หยุดทุก container
```

เหมือน "remote control" ที่ควบคุมทุก container พร้อมกัน 🎮

---

## 2. docker-compose.yml — อ่านทีละบรรทัด

มาเปิดไฟล์ `sample/docker-compose.yml` แล้วอ่านกันทีละส่วน:

```yaml
# =============================================================================
# Docker Compose — Development
# =============================================================================
# This file defines all 3 services: PostgreSQL, Django, and Nginx.
# Run with: docker compose up -d --build
# =============================================================================

services:
  # ===========================================================================
  # PostgreSQL Database
  # ===========================================================================
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME:-notesdb}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ===========================================================================
  # Django + Gunicorn
  # ===========================================================================
  web:
    build: ./app
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - static_volume:/app/staticfiles
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy

  # ===========================================================================
  # Nginx — Reverse Proxy
  # ===========================================================================
  nginx:
    build: ./nginx
    ports:
      - "80:80"
    volumes:
      - static_volume:/app/staticfiles
    depends_on:
      - web

# =============================================================================
# Named Volumes
# =============================================================================
volumes:
  pgdata:
  static_volume:
```

### อธิบายทุก key:

#### `services:` — กำหนด containers ที่ต้องการ

ทุกอย่างอยู่ภายใต้ `services:` — ในที่นี้มี 3 services: `db`, `web`, `nginx`

#### Service: `db` (PostgreSQL)

| Key | ค่า | ความหมาย |
|-----|-----|---------|
| `image` | `postgres:16-alpine` | ใช้ image สำเร็จรูปจาก Docker Hub (ไม่ต้อง build เอง) |
| `volumes` | `pgdata:/var/lib/postgresql/data` | เก็บข้อมูล DB ใน named volume — ไม่หายเมื่อ restart |
| `environment` | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | ตั้งค่า database ที่จะสร้างอัตโนมัติ |
| `ports` | `"5432:5432"` | เปิด port สำหรับเข้าผ่าน tools ภายนอก (pgAdmin, DBeaver) |
| `healthcheck` | `pg_isready` | เช็คว่า PostgreSQL **พร้อมรับ connection** จริงๆ |

💡 **`${DB_NAME:-notesdb}` คืออะไร?**
- อ่านค่าจาก environment variable `DB_NAME`
- ถ้าไม่มี → ใช้ค่า default `notesdb`
- `:-` คือ YAML syntax สำหรับ default value

💡 **ทำไมต้อง `healthcheck`?**
- PostgreSQL container อาจ **start แล้วแต่ยังไม่พร้อม** รับ connection
- `healthcheck` ทำให้ Docker รู้ว่า "database พร้อมแล้วจริงๆ" ก่อนจะ start service อื่นที่ขึ้นกับมัน
- สำคัญมาก: **"container started" ≠ "service ready"**

#### Service: `web` (Django + Gunicorn)

| Key | ค่า | ความหมาย |
|-----|-----|---------|
| `build` | `./app` | build image จาก Dockerfile ใน `./app` directory |
| `command` | `gunicorn ...` | override CMD ใน Dockerfile — รัน Gunicorn |
| `volumes` | `static_volume:/app/staticfiles` | แชร์ static files กับ Nginx |
| `env_file` | `.env` | โหลด environment variables จากไฟล์ `.env` |
| `depends_on` | `db: condition: service_healthy` | **รอจนกว่า db จะ healthy** ก่อน start |

📝 **Note**: สังเกตว่า `web` **ไม่มี `ports:`** — เราไม่เปิด port 8000 ออก internet! Nginx จะเป็นตัวรับ request แล้วส่งต่อมาให้ web ผ่าน Docker network ภายใน

#### Service: `nginx` (Reverse Proxy)

| Key | ค่า | ความหมาย |
|-----|-----|---------|
| `build` | `./nginx` | build image จาก `./nginx/Dockerfile` |
| `ports` | `"80:80"` | **เฉพาะ Nginx ที่เปิด port ออกข้างนอก** — port 80 (HTTP) |
| `volumes` | `static_volume:/app/staticfiles` | **อ่าน** static files ที่ Django สร้างไว้ |
| `depends_on` | `web` | start หลัง web |

#### `volumes:` — Named Volumes

```yaml
volumes:
  pgdata:          # เก็บข้อมูล PostgreSQL — ข้อมูลไม่หายเมื่อ restart
  static_volume:   # แชร์ static files ระหว่าง Django (เขียน) กับ Nginx (อ่าน)
```

```
static_volume ทำงานยังไง:

┌─────────┐     write     ┌──────────────┐     read      ┌─────────┐
│   web   │ ────────────► │ static_volume │ ◄──────────── │  nginx  │
│ (Django) │  collectstatic│  (shared)     │  serve files  │         │
└─────────┘               └──────────────┘               └─────────┘
```

---

## 3. First Run: Django + PostgreSQL

### Step 1: เตรียม .env file

```bash
cd ~/django-postgresql-nginx-docker/sample
cp .env.example .env
```

> copy template มาเป็นไฟล์ `.env` จริง — ตอนนี้ค่า default ใช้ได้เลย

### Step 2: รันทุก service

```bash
docker compose up -d --build
```

> `up` = สร้าง + start ทุก services
> `-d` = detached mode (รัน background)
> `--build` = build images ใหม่ (จาก Dockerfile)

**แสดงผล:**
```
[+] Building 42.5s (12/12) FINISHED
 => [web] ...
 => [nginx] ...
[+] Running 4/4
 ✔ Network sample_default      Created
 ✔ Volume "sample_pgdata"      Created
 ✔ Volume "sample_static_volume" Created
 ✔ Container sample-db-1       Healthy
 ✔ Container sample-web-1      Started
 ✔ Container sample-nginx-1    Started
```

สังเกต:
- Docker Compose สร้าง **network** ให้อัตโนมัติ (`sample_default`)
- Docker Compose สร้าง **volumes** ให้อัตโนมัติ
- db start ก่อน → รอจน healthy → web start → nginx start (ตามลำดับ `depends_on`)

### Step 3: ตรวจสอบ status

```bash
docker compose ps
```

**แสดงผล:**
```
NAME              IMAGE              COMMAND                  SERVICE   CREATED          STATUS                    PORTS
sample-db-1       postgres:16-alpine "docker-entrypoint.s…"   db        30 seconds ago   Up 29 seconds (healthy)   0.0.0.0:5432->5432/tcp
sample-web-1      sample-web         "gunicorn config.wsg…"   web       25 seconds ago   Up 24 seconds             8000/tcp
sample-nginx-1    sample-nginx       "/docker-entrypoint.…"   nginx     20 seconds ago   Up 19 seconds             0.0.0.0:80->80/tcp
```

✅ ทุก service `Up` — สังเกต:
- `db` = `healthy` 🟢
- `web` = port 8000 แต่ **ไม่ได้ expose ออก** (ไม่มี `0.0.0.0:`)
- `nginx` = port 80 expose ออก (`0.0.0.0:80->80`)

### Step 4: ดู logs

```bash
docker compose logs web
```

> ดู log ของ Django/Gunicorn

**แสดงผล:**
```
sample-web-1  | [INFO] Starting gunicorn 22.0.0
sample-web-1  | [INFO] Listening at: http://0.0.0.0:8000
sample-web-1  | [INFO] Using worker: sync
sample-web-1  | [INFO] Booting worker with pid: 8
sample-web-1  | [INFO] Booting worker with pid: 9
sample-web-1  | [INFO] Booting worker with pid: 10
```

ดู log แบบ follow (real-time):

```bash
docker compose logs -f
```

> `-f` = follow — log ใหม่จะแสดงขึ้นมาเรื่อยๆ, กด `Ctrl+C` เพื่อหยุด

---

## 4. Essential Commands — คำสั่งที่ต้องจำ

| คำสั่ง | ทำอะไร | ใช้ตอนไหน |
|--------|--------|----------|
| `docker compose up -d` | start ทุก services (background) | เริ่มต้นระบบ |
| `docker compose up -d --build` | rebuild images แล้ว start | เมื่อแก้ code หรือ Dockerfile |
| `docker compose down` | หยุดและลบ containers | หยุดระบบ |
| `docker compose down -v` | หยุดและลบ containers + **volumes** | ⚠️ reset ทุกอย่าง (ข้อมูลหาย!) |
| `docker compose ps` | ดู status ของทุก services | เช็คว่าอะไรรันอยู่ |
| `docker compose logs web` | ดู log ของ service `web` | debug Django |
| `docker compose logs -f` | follow logs ทุก services | monitor real-time |
| `docker compose exec web bash` | เข้าไปข้างใน container `web` | debug, ตรวจสอบไฟล์ |
| `docker compose restart web` | restart เฉพาะ service `web` | แก้ปัญหาเฉพาะ service |
| `docker compose config` | แสดง resolved config ทั้งหมด | ตรวจสอบ env vars, YAML syntax |

💡 **Tip**: `docker compose down` vs `docker compose down -v`:
- `down` = ลบ containers + networks → **data ใน volumes ยังอยู่**
- `down -v` = ลบ containers + networks + **volumes** → **data หายหมด!** ⚠️

---

## 5. Run Migrations & Create Superuser

ตอนนี้ Django server รันอยู่แล้ว แต่ database ยังว่างเปล่า — ยังไม่ได้ run migration

### Run Migrations

```bash
docker compose exec web python manage.py migrate
```

> `docker compose exec` = รัน command ข้างใน container ที่กำลังทำงาน
> `web` = ชื่อ service
> `python manage.py migrate` = command ที่จะรันข้างใน

**แสดงผล:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, notes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying notes.0001_initial... OK
  Applying sessions.0001_initial... OK
```

### Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

**แสดงผล:**
```
Username (leave blank to use 'root'): admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

### ทดสอบ!

เปิด browser แล้วเข้า:

- **Django Admin**: `http://server-ip/admin/` — login ด้วย superuser ที่สร้าง
- **API**: `http://server-ip/api/notes/` — ควรเห็น DRF browsable API

> ใช้ port 80 (default HTTP) — ไม่ต้องพิมพ์ port number เพราะ Nginx รับ request ที่ port 80

🎉 **Django + PostgreSQL + Nginx ทำงานร่วมกันแล้ว!**

---

## 6. Environment Variables ด้วย .env

### env_file vs environment

ใน docker-compose.yml มี 2 วิธีส่ง environment variables:

```yaml
# วิธีที่ 1: เขียนตรงๆ ในไฟล์ (ไม่ดี — secret อยู่ใน code!)
environment:
  DB_NAME: notesdb
  DB_PASSWORD: super-secret

# วิธีที่ 2: อ่านจาก .env file (ดี — secret แยกจาก code!) ⭐
env_file:
  - .env
```

### ดู resolved values

```bash
docker compose config
```

> แสดง docker-compose.yml หลัง resolve ค่าจาก `.env` แล้ว — ดีมากสำหรับ debug!

### ดู env vars ข้างใน container

```bash
docker compose exec web env | grep DB_
```

**แสดงผล:**
```
DB_NAME=notesdb
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

⚠️ **สำคัญ**: `.env` ต้องอยู่ใน `.gitignore` — **ห้าม commit ขึ้น Git เด็ดขาด!**

---

## 7. Compose Networking (อัตโนมัติ)

หนึ่งในความสะดวกของ Docker Compose คือ — **สร้าง network ให้อัตโนมัติ!**

### ทุก service อยู่ใน network เดียวกัน

```
Docker Compose Network: "sample_default"

┌──────────┐      ┌──────────┐      ┌──────────┐
│    db    │      │   web    │      │  nginx   │
│ postgres │◄────►│  django  │◄────►│  nginx   │
│          │      │          │      │          │
│ port:5432│      │ port:8000│      │ port:80  │
└──────────┘      └──────────┘      └──────────┘
     ▲                                    ▲
     │                                    │
  ไม่เปิด                            เปิดออก
  ออกข้างนอก                         internet
  (internal only)                   (port 80)
```

- ทุก service สามารถ "คุยกัน" ได้โดยใช้ **ชื่อ service** เป็น hostname
- `web` เชื่อมต่อ database ด้วย `DB_HOST=db` — `db` คือชื่อ service
- `nginx` ส่ง request ไป `web:8000` — `web` คือชื่อ service

📝 **Note**: ไม่ต้อง `docker network create` เอง — Compose ทำให้!

### ทำไม `DB_HOST=db` ไม่ใช่ `DB_HOST=localhost`?

นี่คือ concept สำคัญ:
- `localhost` หมายถึง "เครื่องนี้" — แต่แต่ละ container เป็น "เครื่อง" ของตัวเอง
- `db` คือ hostname ของ container ชื่อ `db` ใน Docker network
- Django (ใน container `web`) ต้องเชื่อมไปที่ **container อื่น** → ต้องใช้ชื่อ service

---

## 🤖 เมื่อติดปัญหา — ลองใช้ AI ช่วย Debug

ถ้าเจอ error กับ Docker Compose ลอง copy error message แล้วใช้ prompt นี้:

```
ฉันกำลังเรียนรู้เรื่อง Docker Compose สำหรับ Django deployment
ฉันรัน command: [วาง command ที่พิมพ์]
docker-compose.yml ของฉันมีหน้าตาแบบนี้: [วาง content ของไฟล์]
แล้วเจอ error นี้:

[วาง error message ที่เห็น]

ช่วยอธิบายว่า:
1. Error นี้หมายความว่าอะไร?
2. สาเหตุน่าจะเป็นอะไร?
3. ฉันควรตรวจสอบอะไรบ้าง? (อย่าบอกคำตอบตรงๆ แต่ช่วย guide ให้ฉันหาคำตอบเอง)
```

💡 **Tip**: วิธี debug Docker Compose แบบเป็นระบบ:

```bash
# 1. เช็คว่า YAML ถูกต้อง
docker compose config

# 2. ดู status ทุก service
docker compose ps

# 3. ดู logs ของ service ที่มีปัญหา
docker compose logs web
docker compose logs db

# 4. ดู env vars ที่ถูกส่งเข้า container
docker compose exec web env | grep DB_
```

---

## 📋 สรุป

ใน Part นี้เราได้เรียนรู้ Docker Compose:

| หัวข้อ | สิ่งที่เรียนรู้ |
|--------|---------------|
| **ทำไม Compose** | จัดการหลาย containers ด้วยไฟล์ YAML ไฟล์เดียว |
| **docker-compose.yml** | `services`, `image/build`, `volumes`, `environment/env_file`, `ports`, `depends_on`, `healthcheck` |
| **Essential Commands** | `up -d --build`, `down`, `ps`, `logs`, `exec`, `config` |
| **Migrations** | `docker compose exec web python manage.py migrate` |
| **.env file** | แยก secrets ออกจาก code, ห้าม commit ขึ้น Git |
| **Networking** | Compose สร้าง network อัตโนมัติ, services คุยกันด้วยชื่อ |

**Key Insight**: Docker Compose เปลี่ยนจาก "3 คำสั่ง `docker run` ยาวๆ" เป็น "1 ไฟล์ YAML + `docker compose up`" — ง่ายขึ้นมาก, ผิดพลาดน้อยลง!

---

## 🧪 ลองทำ

1. **ลอง restart**: รัน `docker compose restart web` — ดู logs ว่า Gunicorn restart ไหม

2. **เข้าไปข้างใน container**: รัน `docker compose exec web bash` แล้วลองดูโครงสร้างไฟล์ด้วย `ls -la /app/` — ไฟล์ตรงกับ source code ไหม? พิมพ์ `exit` เพื่อออก

3. **ทดลอง `down -v`**: ลอง `docker compose down -v` แล้ว `docker compose up -d --build` ใหม่ — จะต้อง migrate ใหม่ไหม? superuser ยังอยู่ไหม? (⚠️ คำตอบ: ต้อง migrate ใหม่, superuser หาย — เพราะ volume ถูกลบ!)

4. **docker compose config**: ลองแก้ค่าใน `.env` (เช่น `DB_NAME=mydb`) แล้วรัน `docker compose config` — ค่าเปลี่ยนตามไหม?

5. **ตอบคำถาม**: ทำไม `web` service ไม่มี `ports:` แต่ `nginx` มี? ถ้า `web` มี `ports: "8000:8000"` จะเกิดอะไรขึ้น?

---

[← Part 4: Docker Fundamentals](part-4-docker-fundamentals.md) | [Part 6: Nginx →](part-6-nginx.md)
