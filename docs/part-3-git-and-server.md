# Part 3: Git & เอาโค้ดขึ้น Server

> ⏱️ เวลาโดยประมาณ: 1 ชั่วโมง

## 🎯 สิ่งที่จะได้เรียนรู้ใน Part นี้

- ใช้ Git พื้นฐาน (clone, pull, status, log)
- สร้าง SSH Key สำหรับเชื่อมต่อ GitHub
- Clone project ขึ้น Server
- ลอง Run Django แบบ Manual — เพื่อ **เข้าใจปัญหาจริงๆ** ก่อนใช้ Docker

---

## 1. Git พื้นฐาน (Review)

เราเคยใช้ Git มาก่อนแล้ว — มาทบทวนคำสั่งสำคัญกัน:

| คำสั่ง | ทำอะไร |
|--------|--------|
| `git clone <url>` | copy repository ทั้งหมดมาที่เครื่อง |
| `git pull` | ดึง code ล่าสุดจาก remote (GitHub) |
| `git status` | ดูว่ามีไฟล์อะไรเปลี่ยนแปลงบ้าง |
| `git log --oneline -5` | ดู 5 commits ล่าสุดแบบย่อ |

📝 **Note**: ใน deployment workflow เราจะใช้ `git clone` (ครั้งแรก) และ `git pull` (อัพเดท) เป็นหลัก

---

## 2. สร้าง SSH Key สำหรับ GitHub

ก่อนจะ clone project บน server ได้ เราต้องตั้งค่าให้ server สามารถเข้าถึง GitHub ได้ก่อน

### ทำไมต้อง SSH Key?

เวลา clone private repository จาก GitHub เราต้องพิสูจน์ตัวตน มี 2 วิธี:
- **HTTPS + Token** — ต้องพิมพ์ token ทุกครั้ง
- **SSH Key** ⭐ — ตั้งค่าครั้งเดียว ใช้ได้ตลอด

SSH Key ทำงานแบบ "กุญแจคู่":
- 🔐 **Private key** = กุญแจของเรา (เก็บบน server, **ห้ามส่งให้ใคร!**)
- 🔓 **Public key** = แม่กุญแจ (ส่งให้ GitHub, ใครมีก็ได้)

### Step 1: สร้าง SSH Key

```bash
ssh-keygen -t ed25519 -C "your@email.com"
```

> `ssh-keygen` = สร้าง SSH key pair
> `-t ed25519` = ใช้ algorithm Ed25519 (เร็วและปลอดภัย)
> `-C "your@email.com"` = comment เพื่อระบุว่า key นี้ของใคร

**แสดงผล:**
```
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/your-name/.ssh/id_ed25519):
```

กด `Enter` เพื่อใช้ path default

```
Enter passphrase (empty for no passphrase):
```

กด `Enter` สองครั้ง (ไม่ต้องใส่ passphrase สำหรับ server — สะดวกกว่า)

**แสดงผลสุดท้าย:**
```
Your identification has been saved in /home/your-name/.ssh/id_ed25519
Your public key has been saved in /home/your-name/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx your@email.com
```

### Step 2: Copy Public Key

```bash
cat ~/.ssh/id_ed25519.pub
```

**แสดงผล (ตัวอย่าง):**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJxxxxxxxxxxxxxxxxxxxxxxxxxxxxx your@email.com
```

**Copy ทั้งบรรทัดนี้** (ตั้งแต่ `ssh-ed25519` ถึงท้ายสุด)

### Step 3: เพิ่มใน GitHub

1. เปิด GitHub → ไปที่ **Settings** (มุมขวาบน กดรูป profile → Settings)
2. เลือก **SSH and GPG keys** (ในเมนูด้านซ้าย)
3. กด **New SSH key**
4. **Title**: ตั้งชื่อที่จำได้ เช่น `my-server` หรือ `wsl-ubuntu`
5. **Key**: paste public key ที่ copy มา
6. กด **Add SSH key**

### Step 4: ทดสอบ Connection

```bash
ssh -T git@github.com
```

> ทดสอบว่า SSH key ของเรา connect GitHub ได้

**แสดงผลครั้งแรก:**
```
The authenticity of host 'github.com (140.82.121.4)' can't be established.
ED25519 key fingerprint is SHA256:+DiY3wvvxxxxxxxxxxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

พิมพ์ `yes` แล้ว Enter

**แสดงผลที่บอกว่าสำเร็จ:**
```
Hi your-username! You've been successfully authenticated, but GitHub does not provide shell access.
```

✅ ถ้าเห็นข้อความนี้ แสดงว่า server ของเราเชื่อมต่อ GitHub ได้แล้ว!

---

## 3. Clone Project ขึ้น Server

ตอนนี้ server ของเราสามารถเข้าถึง GitHub ได้แล้ว มา clone project กัน:

```bash
cd ~
git clone git@github.com:your-username/django-postgresql-nginx-docker.git
```

> `cd ~` = กลับไป home directory
> `git clone` = download repository ทั้งหมดมาที่เครื่อง

**แสดงผล:**
```
Cloning into 'django-postgresql-nginx-docker'...
remote: Enumerating objects: 42, done.
remote: Counting objects: 100% (42/42), done.
remote: Compressing objects: 100% (30/30), done.
Receiving objects: 100% (42/42), 12.34 KiB | 1.23 MiB/s, done.
```

เข้าไปดูโครงสร้าง:

```bash
cd django-postgresql-nginx-docker/sample
ls -la
```

**แสดงผล:**
```
total 24
drwxr-xr-x 4 your-name your-name 4096 Jan  1 00:00 .
drwxr-xr-x 5 your-name your-name 4096 Jan  1 00:00 ..
-rw-r--r-- 1 your-name your-name  633 Jan  1 00:00 .env.example
drwxr-xr-x 4 your-name your-name 4096 Jan  1 00:00 app
-rw-r--r-- 1 your-name your-name 2082 Jan  1 00:00 docker-compose.yml
drwxr-xr-x 2 your-name your-name 4096 Jan  1 00:00 nginx
```

ลองดู tree (ถ้าติดตั้ง tree ไว้จาก Part 1):

```bash
tree -L 3
```

**แสดงผล:**
```
.
├── .env.example
├── app
│   ├── Dockerfile
│   ├── config
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   ├── notes
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   └── requirements.txt
├── docker-compose.yml
└── nginx
    ├── Dockerfile
    └── nginx.conf
```

---

## 4. 🧪 ลอง Run Django แบบ Manual (สำคัญมาก!)

> 🎯 **จุดประสงค์ของ section นี้: ให้เข้าใจว่า deploy แบบ manual มัน "ลำบาก" แค่ไหน — เพื่อเห็นคุณค่าของ Docker ใน Part ถัดไป**

เรามาลอง setup Django แบบดั้งเดิม — **ไม่ใช้ Docker** — ดูว่าเจอปัญหาอะไรบ้าง

### Step 1: ติดตั้ง Python และสร้าง Virtual Environment

```bash
sudo apt install -y python3 python3-pip python3-venv
```

> ติดตั้ง Python 3 และ tools ที่จำเป็น

```bash
cd ~/django-postgresql-nginx-docker/sample/app
python3 -m venv venv
source venv/bin/activate
```

> สร้างและ activate virtual environment — เหมือนที่ทำใน development

**แสดงผล (prompt จะเปลี่ยน):**
```
(venv) your-name@server:~/django-postgresql-nginx-docker/sample/app$
```

```bash
pip install -r requirements.txt
```

> ติดตั้ง Python dependencies ทั้งหมด

**แสดงผล:**
```
Collecting Django>=5.1,<5.2
...
Successfully installed Django-5.1.x djangorestframework-3.15.x ...
```

### Step 2: ลอง Run Django

```bash
python manage.py runserver 0.0.0.0:8000
```

> `0.0.0.0` = ฟังจากทุก IP (ไม่ใช่แค่ localhost)
> `:8000` = port 8000

### ❌ Problem 1: ไม่มี PostgreSQL!

Django จะพัง ทันที! เพราะ `settings.py` ตั้งค่า database เป็น PostgreSQL แต่เรายังไม่ได้ติดตั้ง PostgreSQL บน server

🔍 **อ่าน Error Message:**

```
django.db.utils.OperationalError: could not connect to server:
Connection refused. Is the server running on host "db" (127.0.0.1)
and accepting TCP/IP connections on port 5432?
             ^^^^^^^^^^^^^^^^^^^^     ^^^^
             ⬆️ host "db" ไม่มีอยู่    ⬆️ ไม่มี PostgreSQL ฟังที่ port 5432
```

**วิธีอ่าน error นี้:**
- `"could not connect to server"` = เชื่อมต่อ database ไม่ได้
- `host "db"` = Django พยายามเชื่อมไปที่ host ชื่อ `db` (ซึ่งเป็นชื่อ Docker service — แต่เราไม่ได้ใช้ Docker!)
- `port 5432` = port ของ PostgreSQL

**สาเหตุ**: ไม่มี PostgreSQL ติดตั้งอยู่บน server, และ `DB_HOST=db` ไม่มีความหมายนอก Docker network

ถ้าจะแก้ต้อง... ติดตั้ง PostgreSQL เอง:

```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb notesdb
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

> นี่คือแค่ setup พื้นฐาน — ยังต้องแก้ settings ให้ `DB_HOST=localhost` อีก... เห็นไหมว่ายุ่งยาก?

### ❌ Problem 2: ปิด Terminal = Server หยุด!

สมมติว่า setup database สำเร็จแล้ว (เราจะไม่ทำจริง) — `runserver` จะรันได้ **แต่**:

- ถ้าเราปิด terminal → Django server หยุดทันที!
- ถ้า SSH connection หลุด → Django server หยุด!
- ต้อง process ทำงาน background อยู่ตลอดเวลา... ยุ่งยากมาก

### ❌ Problem 3: Static Files ไม่มีคนเสิร์ฟ

- ในตอน dev, `runserver` serve static files ให้อัตโนมัติ
- แต่ใน production (`DEBUG=False`) Django **ไม่ serve static files** → หน้า Admin จะได้ไม่มี CSS (เปล่าๆ ขาวๆ)
- ต้องใช้ Nginx มา serve static files... ต้อง setup อีก

### ❌ Problem 4: รองรับแค่ 1 Request ต่อครั้ง

- `runserver` ทำงานแบบ single-threaded
- ถ้ามี 10 คนเข้าพร้อมกัน → 9 คนต้องรอ
- ต้องใช้ Gunicorn... ต้อง setup อีก

### 💡 สรุปปัญหาทั้งหมด

| ปัญหา | ถ้าแก้แบบ Manual | ถ้าใช้ Docker |
|--------|------------------|--------------|
| ไม่มี PostgreSQL | ติดตั้งเอง, สร้าง DB, ตั้งค่า user | `docker compose up` — มี PostgreSQL พร้อมใช้ |
| Terminal ปิด = Server หยุด | ใช้ `nohup`, `screen`, `systemd` | Container รัน background อัตโนมัติ |
| Static files | ติดตั้ง Nginx เอง, config เอง | Nginx container พร้อม config |
| Single-threaded | ติดตั้ง Gunicorn, configure เอง | กำหนดใน docker-compose.yml |
| Version ไม่ตรง | ต้อง manage เอง | Dockerfile กำหนด version ชัดเจน |

> **🎯 "ถ้าเราต้อง setup ทุกอย่างเอง ทุกครั้งที่ย้าย server จะเสียเวลามาก → นี่คือเหตุผลที่เราต้องใช้ Docker!"**

---

## 5. Clean Up

ก่อนจบ มา clean up สิ่งที่เราสร้างไว้:

```bash
deactivate
```

> ออกจาก virtual environment

```bash
cd ~/django-postgresql-nginx-docker/sample/app
rm -rf venv
```

> ลบ virtual environment — เราจะไม่ใช้มันอีก เพราะจะใช้ Docker แทน

---

## 🤖 เมื่อติดปัญหา — ลองใช้ AI ช่วย Debug

ถ้าเจอ error ระหว่าง clone หรือ setup ลอง copy error message แล้วใช้ prompt นี้:

```
ฉันกำลังเรียนรู้เรื่อง Git SSH setup และ Django manual deployment
ฉันใช้ Ubuntu 24.04 บน [WSL2 / Cloud VM]
ฉันทำตาม step [อธิบายสิ่งที่ทำ เช่น สร้าง SSH key, clone repo, pip install]
แล้วเจอ error นี้:

[วาง error message ที่เห็น]

ช่วยอธิบายว่า:
1. Error นี้หมายความว่าอะไร?
2. สาเหตุน่าจะเป็นอะไร?
3. ฉันควรตรวจสอบอะไรบ้าง? (อย่าบอกคำตอบตรงๆ แต่ช่วย guide ให้ฉันหาคำตอบเอง)
```

💡 **Tip**: error ที่พบบ่อยใน Part นี้:
- `Permission denied (publickey)` → SSH key ไม่ match กับที่ GitHub — ลองเช็คว่า copy public key ถูกไหม
- `ModuleNotFoundError: No module named 'decouple'` → ลืม activate venv หรือลืม `pip install`
- `OperationalError: could not connect to server` → ไม่มี PostgreSQL — นี่คือ expected result ที่เราอยากเห็น!

---

## 📋 สรุป

ใน Part นี้เราได้:

| สิ่งที่ทำ | ทำไม |
|----------|------|
| สร้าง SSH Key | เพื่อเชื่อมต่อ server กับ GitHub ได้โดยไม่ต้องพิมพ์ password |
| Clone project ขึ้น server | เอาโค้ดไปอยู่บน server พร้อม deploy |
| ลอง run Django แบบ manual | **เพื่อเข้าใจปัญหาจริงๆ** — ก่อนจะไปเรียน Docker |

**บทเรียนสำคัญ**: การ deploy แบบ manual นั้นยุ่งยาก, ซ้ำซ้อน, และเสี่ยงผิดพลาด ตั้งแต่ Part 4 เป็นต้นไป เราจะเรียน Docker ที่แก้ปัญหาเหล่านี้ทั้งหมด! 🐳

---

## 🧪 ลองทำ

1. **ทดสอบ SSH**: ลอง `ssh -T git@github.com` อีกครั้ง — ยังเชื่อมต่อได้อยู่ไหม?

2. **Git log**: รัน `git log --oneline -10` ใน project directory — ดู commit history ของ project

3. **ตอบคำถาม**: นอกจาก 4 ปัญหาที่เราเจอกับ manual deployment ลองคิดอีก 1-2 ปัญหาที่อาจเกิดขึ้นถ้าเราต้อง deploy บน server เครื่องใหม่ทุกครั้ง

4. **ลองคิด**: ถ้ามี developer 3 คน ทำงาน project เดียวกัน แต่ละคน install Python version ต่างกัน, PostgreSQL version ต่างกัน — จะเกิดปัญหาอะไร? Docker ช่วยแก้ปัญหานี้ยังไง?

---

[← Part 2: ทำความเข้าใจ Django Project](part-2-understanding-django-project.md) | [Part 4: Docker Fundamentals →](part-4-docker-fundamentals.md)
