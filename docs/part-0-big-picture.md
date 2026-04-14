# Part 0: ภาพรวม — เราจะสร้างอะไร?

> ⏱️ เวลาโดยประมาณ: 30 นาที

## 🎯 สิ่งที่จะได้เรียนรู้ใน Part นี้

- เข้าใจว่า "Deployment" คืออะไร
- เห็นภาพรวม Architecture ทั้งหมด
- รู้ว่าแต่ละเครื่องมือทำหน้าที่อะไร และทำไมเราถึงต้องใช้มัน
- เข้าใจ Road Map ของบทเรียนทั้งหมด 10 Parts

---

## 1. "Deployment" คืออะไร?

ลองนึกภาพ... ตอนนี้เราเขียน Django project เสร็จแล้ว เราเปิด terminal แล้วพิมพ์:

```bash
python manage.py runserver
```

เว็บเราก็ทำงานสวยงาม — แต่แค่บนเครื่องของเรา 🏠

ถ้าเราอยากให้คนอื่นเข้าใช้งานได้ล่ะ? อยากให้มี URL เช่น `https://my-notes-app.com` ที่ใครก็เข้าได้จากทั่วโลก?

**นั่นคือ Deployment — กระบวนการเอา Application ของเราไป "เปิดตัว" บน Server จริงๆ ให้คนอื่นใช้งานได้**

### 🍳 Analogy: ร้านอาหาร

| | ทำอาหารที่บ้าน (Development) | เปิดร้านอาหาร (Production) |
|--|---|---|
| ใครกินได้ | แค่ตัวเอง | ลูกค้าทุกคน |
| เปิดตอนไหน | อยากทำก็ทำ | ต้องเปิด 24/7 |
| อุปกรณ์ | หม้อกะทะที่บ้าน | ครัวมาตรฐาน, ตู้แช่, เตาแรงสูง |
| พนักงาน | ทำคนเดียว | ต้องมีหลายคน |
| ความปลอดภัย | ไม่ต้องคิด | สุขอนามัย, ใบอนุญาต |

`python manage.py runserver` เหมือนทำอาหารที่บ้าน — สะดวก แต่ไม่เหมาะจะเปิดร้าน

สิ่งที่เปลี่ยนเมื่อเราจะ Deploy:
- ต้องมี **Server** ที่รัน 24/7 (ไม่ใช่ laptop ที่เราปิดตอนนอน)
- ต้องมี **Domain Name** (URL ที่จำง่าย)
- ต้องมี **Security** (HTTPS, firewall)
- ต้อง **รองรับคนเข้าใช้พร้อมกันหลายคน**
- ต้อง **ไม่พังเมื่อมี error**

---

## 2. Architecture — ระบบทั้งหมดหน้าตาเป็นยังไง?

นี่คือภาพรวมของสิ่งที่เราจะสร้างในบทเรียนนี้:

```
Internet
  │
  ▼
Domain (DNS)  ──────────────────►  Server (Ubuntu VM)
                                    │
                                    ├── 🌐 Nginx (Port 80/443)
                                    │     • รับ request จาก internet
                                    │     • serve static files (CSS, JS, images)
                                    │     • ส่งต่อ request ไปที่ Django
                                    │     ↓
                                    ├── 🐍 Django + Gunicorn (Port 8000)
                                    │     • ประมวลผล request
                                    │     • รัน business logic
                                    │     • ส่งข้อมูลกลับ
                                    │     ↓
                                    └── 🐘 PostgreSQL (Port 5432)
                                          • เก็บข้อมูลทั้งหมด

                  ┌──────────────────────────┐
                  │   ทั้งหมดอยู่ใน Docker    │
                  │      Containers          │
                  └──────────────────────────┘
```

### แต่ละส่วนทำอะไร?

- **Nginx** — เหมือน "พนักงานต้อนรับ" ที่คอยรับแขก ส่งต่อคำสั่งไปครัว หรือเสิร์ฟของที่เตรียมไว้แล้ว (static files)
- **Gunicorn** — เหมือน "ผู้จัดการครัว" ที่คุม Django workers หลายคนให้ทำงานพร้อมกัน
- **Django** — เหมือน "พ่อครัว" ที่ทำอาหาร (ประมวลผล request, query ข้อมูล)
- **PostgreSQL** — เหมือน "ตู้เก็บวัตถุดิบ" (ฐานข้อมูล)
- **Docker** — เหมือน "กล่องขนส่ง" ที่ pack ทุกอย่างไว้ด้วยกัน พร้อมใช้ทุกที่

---

## 3. ทำไมต้องใช้เครื่องมือเหล่านี้?

คำถามที่ดีมาก — ทำไมเราไม่แค่ `runserver` แล้วให้คนเข้ามาเลย?

| เครื่องมือ | ❌ ถ้าไม่ใช้ | ✅ ถ้าใช้ |
|-----------|------------|---------|
| **Docker** | ต้องติดตั้ง Python, PostgreSQL, Nginx ทีละตัวบน Server — version อาจไม่ตรงกับเครื่อง dev, ตั้งค่ายุ่งยาก | สร้าง Container ที่เหมือนกันทุกเครื่อง — "works on my machine" ไม่เป็นปัญหาอีกต่อไป |
| **Nginx** | Django ต้อง serve ไฟล์ CSS/JS เอง — ช้า, ไม่รองรับ HTTPS, ไม่ปลอดภัย | จัดการ static files ได้เร็ว, รองรับ HTTPS, ป้องกัน Django จาก internet โดยตรง |
| **Gunicorn** | `runserver` รองรับแค่คนเดียว, ไม่เสถียร, ไม่เหมาะกับ production | รัน Django แบบ production-ready, รองรับหลาย request พร้อมกัน |
| **Docker Compose** | ต้องพิมพ์ `docker run ...` ยาวๆ ทีละ container — ง่ายที่จะพิมพ์ผิด | จัดการทุก container ด้วยไฟล์ YAML ไฟล์เดียว — `docker compose up` จบ |
| **PostgreSQL** | ใช้ SQLite ที่เหมาะกับ dev — แต่รองรับคนเข้าพร้อมกันไม่ดี, ไม่เหมาะกับ production | Database ที่เสถียร, รองรับ concurrent access, ใช้ใน production จริง |

💡 **Tip**: ถ้ายังรู้สึกว่า "ทำไมต้องยุ่งยากขนาดนี้" — ไม่ต้องกังวล! ใน Part 3 เราจะลอง deploy แบบ manual ก่อน แล้วจะเข้าใจเองว่าเครื่องมือเหล่านี้ช่วยชีวิตเราได้แค่ไหน

---

## 4. สิ่งที่เราจะสร้างในบทเรียนนี้

### 📦 Sample Project: Notes API

เราจะใช้ project ตัวอย่างเล็กๆ — **Notes API** — เป็น REST API สำหรับจดบันทึก (Notes) ที่รองรับ CRUD operations:

- `GET /api/notes/` — ดู notes ทั้งหมด
- `POST /api/notes/` — สร้าง note ใหม่
- `GET /api/notes/{id}/` — ดู note ตัวเดียว
- `PUT /api/notes/{id}/` — แก้ไข note
- `DELETE /api/notes/{id}/` — ลบ note

เทคโนโลยีที่ใช้:
- **Django 5.1** + **Django REST Framework** — สร้าง API
- **PostgreSQL 16** — ฐานข้อมูล
- **Gunicorn** — Production WSGI server
- **Nginx** — Reverse proxy + static files
- **Docker & Docker Compose** — จัดการทุก service

📝 **Note**: Project นี้ตั้งใจให้เล็กและเข้าใจง่าย เพราะจุดประสงค์หลักคือเรียนรู้กระบวนการ deployment ไม่ใช่เขียน Django ที่ซับซ้อน

### 🗺️ Road Map — 10 Parts ของบทเรียน

| Part | หัวข้อ | สิ่งที่จะทำ |
|------|-------|------------|
| **0** | ภาพรวม | **← คุณอยู่ที่นี่!** เข้าใจ big picture |
| **1** | Setup Environment | ตั้งค่า Linux, ติดตั้ง Git, Docker |
| **2** | ทำความเข้าใจ Django Project | อ่านโค้ด, เข้าใจ settings สำหรับ production |
| **3** | Git & เอาโค้ดขึ้น Server | Clone project, ลอง run แบบ manual |
| **4** | Docker Fundamentals | เรียนรู้ Docker, Image, Container, Volume |
| **5** | Docker Compose | จัดการหลาย container ด้วยไฟล์เดียว |
| **6** | Nginx | ตั้งค่า reverse proxy, serve static files |
| **7** | Production Readiness | Domain, HTTPS, Security, Backup |
| **8** | CI/CD | Auto deploy ด้วย GitHub Actions |
| **9** | สรุปและก้าวต่อไป | Cheat sheet, troubleshooting guide, next steps |

---

## 5. Prerequisites — สิ่งที่ต้องมีก่อนเริ่ม

### สิ่งที่ต้องมี:
- ✅ คอมพิวเตอร์ที่เชื่อมต่อ Internet
- ✅ GitHub Account (ถ้ายังไม่มี ไปสมัครที่ [github.com](https://github.com))

### สิ่งที่ต้องรู้มาก่อน:
- ✅ Django พื้นฐาน — เคยสร้าง project, เขียน models, views, urls ได้
- ✅ SQL พื้นฐาน — รู้จัก SELECT, INSERT, UPDATE, DELETE
- ✅ ใช้ Terminal/Command Line พื้นฐานได้ (ไม่ต้องเก่ง — เราจะสอน Linux commands ใน Part 1)

### สิ่งที่ไม่ต้องรู้มาก่อน:
- ❌ Linux — เราจะสอนตั้งแต่ต้น
- ❌ Docker — เราจะสอนตั้งแต่ต้น
- ❌ Nginx — เราจะสอนตั้งแต่ต้น
- ❌ Server management — เราจะสอนตั้งแต่ต้น
- ❌ CI/CD — เราจะสอนตั้งแต่ต้น

---

## 6. สิ่งที่สำคัญที่สุดที่จะได้เรียน: การอ่าน Error Message

> 🎯 **ในบทเรียนนี้ เราจะไม่แค่สอนวิธีทำที่ถูกต้อง — แต่จะสอนวิธี debug เมื่อมีปัญหา**

นี่คือทักษะที่สำคัญที่สุดสำหรับ developer: **ความสามารถในการอ่านและเข้าใจ Error Message**

Error message ไม่ใช่ "ศัตรู" — มันคือ **"เพื่อน"** ที่พยายามบอกเราว่าอะไรผิด ถ้าเราอ่านมันเป็น เราจะแก้ปัญหาได้เร็วขึ้นมาก

### วิธี Debug แบบเป็นระบบที่เราจะใช้ตลอดบทเรียน:

```
🔍 Step 1: อ่าน Error Message — บรรทัดไหนสำคัญ? keyword อะไรบอก hint?
🔍 Step 2: ดู Logs — docker compose logs <service>
🔍 Step 3: เข้าไปใน Container ดู — docker compose exec <service> bash
🔍 Step 4: ลองค้นหา — ใช้ keyword จาก error message
```

### 🤖 เมื่อติดปัญหา — ลองใช้ AI ช่วย Debug

เมื่อเจอ error ที่แก้ไม่ได้ ลองใช้ prompt นี้ถาม AI (เช่น ChatGPT, Claude, Gemini):

```
ฉันกำลังเรียนรู้เรื่อง [หัวข้อ เช่น Docker, Nginx, Django deployment]
ฉันทำตาม step [อธิบายสิ่งที่ทำ]
แล้วเจอ error นี้:

[วาง error message ที่เห็น]

ช่วยอธิบายว่า:
1. Error นี้หมายความว่าอะไร?
2. สาเหตุน่าจะเป็นอะไร?
3. ฉันควรตรวจสอบอะไรบ้าง? (อย่าบอกคำตอบตรงๆ แต่ช่วย guide ให้ฉันหาคำตอบเอง)
```

💡 **Tip**: การเรียนรู้ที่ดีที่สุดคือการ debug ด้วยตัวเอง — AI ควรเป็น "ผู้ช่วยสอน" ไม่ใช่ "คนให้คำตอบ"

---

## 📋 สรุป

ในบทเรียนนี้ เราจะเรียนรู้กระบวนการ deploy Django application ตั้งแต่ต้นจนจบ:

1. **Setup** Linux environment และติดตั้งเครื่องมือ
2. **เข้าใจ** Django project structure และ production settings
3. **ลอง deploy แบบ manual** เพื่อเข้าใจปัญหา
4. **เรียนรู้ Docker** เพื่อแก้ปัญหาเหล่านั้น
5. **ใช้ Docker Compose** จัดการหลาย containers
6. **ตั้งค่า Nginx** เป็น reverse proxy
7. **เตรียม production**: Domain, HTTPS, Security
8. **Auto deploy** ด้วย GitHub Actions
9. **สรุป** ทุกสิ่งที่เรียนมา

ทุก Part จะมีการฝึก debug ด้วย — เราจะ **ตั้งใจทำผิดก่อน** เพื่อดู error จริง แล้วค่อยแก้ไข เพราะ **การเข้าใจ error สำคัญกว่าการทำถูกตั้งแต่แรก**

---

## 🧪 ลองทำ

1. **อ่าน Architecture Diagram** ด้านบนอีกครั้ง — ลองอธิบายให้เพื่อนฟังว่าแต่ละส่วนทำหน้าที่อะไร
2. **เข้าไปดู** `sample/` folder ใน repository — ลอง browse โครงสร้างไฟล์คร่าวๆ (ยังไม่ต้องเข้าใจทุกอย่าง)
3. **ตอบคำถาม**: ถ้าเราแค่ `python manage.py runserver` แล้วเปิด port ให้คนเข้า จะมีปัญหาอะไรบ้าง? (ลองคิดอย่างน้อย 3 ข้อ)

---

[← กลับหน้าหลัก](../README.md) | [Part 1: เตรียมเครื่องมือ →](part-1-setup-environment.md)
