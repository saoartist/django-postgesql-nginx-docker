# Part 4: Docker Fundamentals

> ⏱️ เวลาโดยประมาณ: 2-3 ชั่วโมง

## 🎯 สิ่งที่จะได้เรียนรู้ใน Part นี้

- เข้าใจว่า Docker คืออะไร และทำไมเราต้องใช้
- เข้าใจ Core Concepts: Image, Container, Dockerfile, Registry
- รัน Container ตัวแรก
- ใช้ Docker กับ PostgreSQL
- เข้าใจ Volume — ข้อมูลที่ไม่หายเมื่อลบ Container
- สร้าง Docker Image สำหรับ Django
- เข้าใจ Network — Container คุยกันยังไง

---

## 1. Docker คืออะไร?

### ปัญหา: "Works on my machine!"

เคยเจอไหม? — เขียน code บนเครื่อง dev แล้วทำงานปกติ แต่พอเอาขึ้น server แล้วพัง:

- Python version ไม่ตรง
- Library ไม่ได้ install
- PostgreSQL version ต่างกัน
- OS ต่างกัน (macOS vs Ubuntu)

### Solution: Docker

**Docker** แก้ปัญหานี้ด้วยการ **pack ทุกอย่างที่ application ต้องการ** ลงใน "กล่อง" (Container) ที่ทำงานเหมือนกันทุกเครื่อง

### 🍱 Analogy: กล่องข้าว

| | ทำอาหารที่ร้าน (ไม่มี Docker) | กล่องข้าวพร้อมกิน (มี Docker) |
|--|---|---|
| ต้องเตรียมอะไร | ครัว, เตา, วัตถุดิบ, สูตร | ไม่ต้องเตรียมอะไร — ทุกอย่างอยู่ในกล่อง |
| ใช้ที่ไหนได้ | เฉพาะในครัวที่มีอุปกรณ์ | ที่ไหนก็ได้ — บ้าน, ออฟฟิศ, ปิคนิค |
| เหมือนกันทุกครั้ง? | ขึ้นอยู่กับเตาและวัตถุดิบ | เหมือนกันทุกกล่อง |

Container = **กล่องข้าวพร้อมกิน** ที่มี code + dependencies + runtime ครบทุกอย่าง พร้อมรันได้ทุกที่!

---

## 2. Core Concepts

มาทำความรู้จักกับ 4 concepts หลักของ Docker:

```
┌─────────────────────────────────────────────────────┐
│  🏪 Registry (Docker Hub)                            │
│  = หนังสือรวมสูตรอาหาร — ที่เก็บ images สาธารณะ      │
│                                                      │
│  ┌──────────┐   docker build   ┌──────────────┐     │
│  │📄Dockerfile│ ─────────────► │ 📦 Image      │     │
│  │= ขั้นตอน   │                │ = สูตรอาหาร    │     │
│  │  การทำ     │                │   (read-only) │     │
│  └──────────┘                  └──────┬───────┘     │
│                                       │              │
│                              docker run│              │
│                                       ▼              │
│                               ┌──────────────┐      │
│                               │ 🍽️ Container  │      │
│                               │ = จานอาหาร    │      │
│                               │   ที่ทำออกมา   │      │
│                               │  (running)    │      │
│                               └──────────────┘      │
└─────────────────────────────────────────────────────┘
```

### 📦 Image (สูตรอาหาร)

- **Blueprint** ที่บอกว่า application ต้องการอะไรบ้าง
- **Read-only** — สร้างแล้วเปลี่ยนไม่ได้
- สร้างจาก **Dockerfile**
- ตัวอย่าง: `python:3.12-slim`, `postgres:16-alpine`, `nginx:1.27-alpine`

### 🍽️ Container (จานอาหาร)

- **Running instance** ของ Image — เหมือน "จานอาหารที่ทำออกมาจากสูตร"
- สร้าง, หยุด, ลบได้ตลอด — ไม่กระทบ Image
- จาก Image เดียว สร้างได้หลาย Container (เหมือนสูตรเดียว ทำได้หลายจาน)

### 📄 Dockerfile (ขั้นตอนการทำ)

- ไฟล์ text ที่บอกวิธีสร้าง Image — เหมือน **recipe**
- เขียนทีละ step: ใช้ base image อะไร, install อะไร, copy ไฟล์อะไร

### 🏪 Registry / Docker Hub (หนังสือรวมสูตร)

- ที่เก็บ Images สาธารณะ — เหมือน "GitHub สำหรับ Docker Images"
- `docker pull python:3.12-slim` = ดึงสูตรจาก Docker Hub มาเครื่องเรา

---

## 3. Hands-on: Container ตัวแรก

### Hello World

```bash
docker run hello-world
```

> `docker run` = สร้างและรัน container จาก image ที่ระบุ

มาดูว่า Docker ทำอะไรบ้าง เมื่อเรารันคำสั่งนี้:

```
1. Docker หา image "hello-world" บนเครื่อง → ไม่มี
2. Docker ดึง (pull) image จาก Docker Hub → download มา
3. Docker สร้าง Container จาก image นั้น
4. Docker รัน Container → แสดงข้อความ "Hello from Docker!"
5. Container ทำงานเสร็จ → หยุดรัน (exit)
```

### ลองเข้าไปใน Ubuntu Container

```bash
docker run -it ubuntu:24.04 bash
```

> `-i` = interactive mode (รับ input จากเราได้)
> `-t` = allocate terminal (แสดงผลสวย)
> `-it` = รวมกันคือ "เปิด interactive terminal"
> `ubuntu:24.04` = ใช้ Ubuntu 24.04 image
> `bash` = คำสั่งที่จะรันข้างใน container

**แสดงผล:**
```
Unable to find image 'ubuntu:24.04' locally
24.04: Pulling from library/ubuntu
...
root@a1b2c3d4e5f6:/#
```

🎉 ตอนนี้คุณอยู่ **ข้างใน** Ubuntu container! prompt เปลี่ยนเป็น `root@...`

ลองสำรวจ:

```bash
cat /etc/os-release
```

**แสดงผล:**
```
PRETTY_NAME="Ubuntu 24.04 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
...
```

```bash
ls /
```

**แสดงผล:**
```
bin  boot  dev  etc  home  lib  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
```

นี่คือ Ubuntu เต็มตัวที่รันอยู่ข้างใน container! แต่ **แยกจาก host** ของเราอย่างสมบูรณ์

พิมพ์ `exit` เพื่อออก:

```bash
exit
```

---

## 4. Docker Commands — คำสั่งที่ใช้บ่อย

### ดู Images ที่มีบนเครื่อง

```bash
docker images
```

**แสดงผล:**
```
REPOSITORY    TAG       IMAGE ID       CREATED         SIZE
ubuntu        24.04     a1b2c3d4e5f6   2 weeks ago     78.1MB
hello-world   latest    d2c94e258dcb   9 months ago    13.3kB
```

> `REPOSITORY` = ชื่อ image, `TAG` = version, `SIZE` = ขนาด

### ดู Containers ที่กำลังรัน

```bash
docker ps
```

> แสดงเฉพาะ containers ที่กำลังรันอยู่ (ตอนนี้อาจไม่มี)

```bash
docker ps -a
```

> `-a` = แสดงทุก containers รวมถึงที่หยุดแล้ว

**แสดงผล:**
```
CONTAINER ID   IMAGE          COMMAND    CREATED         STATUS                     NAMES
a1b2c3d4e5f6   ubuntu:24.04   "bash"     5 minutes ago   Exited (0) 2 minutes ago   eager_newton
f6e5d4c3b2a1   hello-world    "/hello"   10 minutes ago  Exited (0) 10 minutes ago  amazing_bell
```

### หยุดและลบ Container

```bash
docker stop <container_id>    # หยุด container ที่กำลังรัน
docker rm <container_id>      # ลบ container ที่หยุดแล้ว
docker rm -f <container_id>   # force — หยุดและลบในคำสั่งเดียว
```

> 💡 ไม่ต้องพิมพ์ ID ทั้งหมด — แค่ 3-4 ตัวแรกพอ เช่น `docker rm a1b2`

### ลบ Image

```bash
docker rmi <image_name>
```

> เช่น `docker rmi hello-world`

ลบทุก containers ที่หยุดแล้ว + images ที่ไม่ใช้:

```bash
docker system prune
```

> ⚠️ ระวัง — จะลบ resources ที่ไม่ได้ใช้ทั้งหมด

---

## 5. Run PostgreSQL ด้วย Docker

ยังจำใน Part 3 ไหม? — เราอยากได้ PostgreSQL แต่ต้องติดตั้งเอง ยุ่งยากมาก

ด้วย Docker — **แค่คำสั่งเดียว!**

### ❌ ลองแบบผิดก่อน

```bash
docker run postgres:16-alpine
```

**แสดงผล (error):**
```
Error: Database is uninitialized and superuser password is not specified.
       You must specify POSTGRES_PASSWORD to a non-empty value for the superuser.
       ...
```

🔍 **อ่าน Error Message:**
- `"Database is uninitialized"` = database ยังไม่ได้ setup
- `"superuser password is not specified"` = ยังไม่ได้ตั้ง password
- `"You must specify POSTGRES_PASSWORD"` = **ต้องกำหนดค่า `POSTGRES_PASSWORD`**

Error message บอกเราชัดเจนว่าต้องทำอะไร!

### ✅ แบบถูกต้อง — กำหนด Environment Variables

```bash
docker run -d \
  --name my-postgres \
  -e POSTGRES_DB=testdb \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  -p 5432:5432 \
  postgres:16-alpine
```

อธิบายทุก flag:

| Flag | ความหมาย |
|------|----------|
| `-d` | **Detached mode** — รัน background ไม่ block terminal |
| `--name my-postgres` | ตั้งชื่อ container ว่า `my-postgres` (ง่ายกว่าจำ ID) |
| `-e POSTGRES_DB=testdb` | **Environment Variable** — ชื่อ database ที่จะสร้างอัตโนมัติ |
| `-e POSTGRES_USER=testuser` | user สำหรับเข้า database |
| `-e POSTGRES_PASSWORD=testpass` | password ของ user |
| `-p 5432:5432` | **Port Binding** — "เปิดประตู" จาก host เข้า container |
| `postgres:16-alpine` | ใช้ image PostgreSQL 16 (Alpine = เวอร์ชันเล็ก ~80MB) |

**แสดงผล:**
```
Unable to find image 'postgres:16-alpine' locally
16-alpine: Pulling from library/postgres
...
Status: Downloaded newer image for postgres:16-alpine
a1b2c3d4e5f6789...
```

> ตัวเลขยาวๆ ที่แสดง = Container ID

### 🚪 Port Binding `-p 5432:5432` อธิบายเพิ่ม

```
          Host (Server)                Container
        ┌──────────────┐            ┌──────────────┐
        │              │            │              │
        │   Port 5432 ◄── -p 5432:5432 ──► Port 5432 │
        │              │            │  (PostgreSQL) │
        │              │            │              │
        └──────────────┘            └──────────────┘
```

- `-p 5432:5432` = **host_port:container_port**
- "เปิดประตูจาก host port 5432 เข้าไปที่ container port 5432"
- ถ้าไม่ `-p` → PostgreSQL ทำงานใน container แต่ **เข้าถึงจากข้างนอกไม่ได้**
- เราสามารถเปลี่ยน host port ได้ เช่น `-p 5433:5432` → เข้าถึงผ่าน host port 5433

### ตรวจสอบว่า Container ทำงาน

```bash
docker ps
```

**แสดงผล:**
```
CONTAINER ID   IMAGE                COMMAND                  CREATED          STATUS          PORTS                    NAMES
a1b2c3d4e5f6   postgres:16-alpine   "docker-entrypoint.s…"   30 seconds ago   Up 29 seconds   0.0.0.0:5432->5432/tcp   my-postgres
```

> `STATUS: Up 29 seconds` = ทำงานอยู่ 🟢

### ทดสอบเข้า PostgreSQL

```bash
docker exec -it my-postgres psql -U testuser testdb
```

> `docker exec` = รันคำสั่งข้างใน container ที่กำลังทำงาน
> `-it` = interactive terminal
> `psql` = PostgreSQL client
> `-U testuser` = ใช้ user ที่เราสร้าง
> `testdb` = ชื่อ database

**แสดงผล:**
```
psql (16.x)
Type "help" for help.

testdb=#
```

🎉 เราเข้า PostgreSQL ได้แล้ว! — ใช้เวลาแค่ 1 คำสั่ง ไม่ต้อง install อะไรบน host เลย!

ลองสร้าง table:

```sql
CREATE TABLE demo (id serial PRIMARY KEY, name text);
INSERT INTO demo (name) VALUES ('hello docker');
SELECT * FROM demo;
```

**แสดงผล:**
```
 id |    name
----+-------------
  1 | hello docker
(1 row)
```

พิมพ์ `\q` เพื่อออกจาก psql:

```
\q
```

---

## 6. Volume — ข้อมูลที่ไม่หาย

### ปัญหา: ลบ Container = ข้อมูลหาย!

มาพิสูจน์กัน — ลบ container ที่เพิ่งสร้าง:

```bash
docker stop my-postgres && docker rm my-postgres
```

> `&&` = รัน command ถัดไปถ้า command แรกสำเร็จ

สร้างใหม่ด้วยคำสั่งเดิม:

```bash
docker run -d \
  --name my-postgres \
  -e POSTGRES_DB=testdb \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  -p 5432:5432 \
  postgres:16-alpine
```

ลองดูข้อมูล:

```bash
docker exec -it my-postgres psql -U testuser testdb -c "SELECT * FROM demo;"
```

**แสดงผล (error):**
```
ERROR:  relation "demo" does not exist
LINE 1: SELECT * FROM demo;
                       ^
```

😱 **ข้อมูลหายหมด!** — table `demo` ที่เราสร้างไว้ไม่มีอยู่แล้ว

**สาเหตุ**: ข้อมูลใน container ถูกเก็บใน container's filesystem — เมื่อลบ container ข้อมูลก็หายไปด้วย

### Solution: Volume — ที่เก็บข้อมูลถาวร

**Volume** คือที่เก็บข้อมูลที่อยู่ **นอก container** — ไม่หายเมื่อลบ container

ลบ container เก่าก่อน:

```bash
docker rm -f my-postgres
```

สร้าง volume:

```bash
docker volume create pgdata
```

> สร้าง named volume ชื่อ `pgdata`

รัน PostgreSQL ใหม่ พร้อม volume:

```bash
docker run -d \
  --name my-postgres \
  -e POSTGRES_DB=testdb \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16-alpine
```

> `-v pgdata:/var/lib/postgresql/data` = mount volume `pgdata` ไปที่ path `/var/lib/postgresql/data` ใน container
> `/var/lib/postgresql/data` = path ที่ PostgreSQL เก็บข้อมูลจริงๆ

```
          Host                          Container
        ┌────────────┐              ┌────────────────┐
        │            │              │                │
        │  Volume    │◄──── -v ────►│ /var/lib/      │
        │  "pgdata"  │              │ postgresql/data│
        │  (ข้อมูล    │              │                │
        │   อยู่ที่นี่) │              │                │
        └────────────┘              └────────────────┘
```

ทดสอบ — สร้างข้อมูล:

```bash
docker exec -it my-postgres psql -U testuser testdb -c "CREATE TABLE demo(id serial PRIMARY KEY, name text); INSERT INTO demo(name) VALUES('saved with volume');"
```

ลบ container:

```bash
docker rm -f my-postgres
```

สร้าง container ใหม่ด้วย **volume เดิม**:

```bash
docker run -d \
  --name my-postgres \
  -e POSTGRES_DB=testdb \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16-alpine
```

ลองดูข้อมูล:

```bash
docker exec -it my-postgres psql -U testuser testdb -c "SELECT * FROM demo;"
```

**แสดงผล:**
```
 id |       name
----+-------------------
  1 | saved with volume
(1 row)
```

🎉 **ข้อมูลยังอยู่!** — เพราะ volume เก็บข้อมูลนอก container

### Volume Commands

```bash
docker volume ls                    # ดู volumes ทั้งหมด
docker volume inspect pgdata        # ดูรายละเอียดของ volume
docker volume rm pgdata             # ลบ volume (⚠️ ข้อมูลหายถาวร!)
```

Clean up ก่อนไปต่อ:

```bash
docker rm -f my-postgres
docker volume rm pgdata
```

---

## 7. สร้าง Docker Image ของ Django

ตอนนี้เรารู้วิธีใช้ image สำเร็จรูป (postgres, ubuntu) แล้ว — มาลองสร้าง image ของเราเองบ้าง!

### อ่าน Dockerfile ทีละบรรทัด

เปิดไฟล์ `sample/app/Dockerfile`:

```dockerfile
# ใช้ Python 3.12 slim เป็น base image
# "slim" = version ที่ตัดสิ่งไม่จำเป็นออก ทำให้ image เล็กลง
FROM python:3.12-slim

# ตั้งค่า environment variables ของ Python
# PYTHONDONTWRITEBYTECODE: ไม่สร้างไฟล์ .pyc (ไม่จำเป็นใน container)
# PYTHONUNBUFFERED: แสดง print/log ทันที ไม่ buffer (สำคัญสำหรับ docker logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# กำหนด working directory ใน container
# ทุกคำสั่งหลังจากนี้จะทำงานใน /app
WORKDIR /app

# ติดตั้ง system dependencies ที่ psycopg2 ต้องการ
# gcc, libpq-dev = library สำหรับเชื่อมต่อ PostgreSQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt ก่อน แล้ว install dependencies
# ทำแยกจาก COPY . . เพื่อใช้ Docker cache
# (ถ้า requirements.txt ไม่เปลี่ยน → ไม่ต้อง pip install ใหม่)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code ทั้งหมดเข้า container
COPY . .

# รวม static files ไว้ที่ /app/staticfiles
RUN python manage.py collectstatic --noinput

# ประกาศว่า container ใช้ port 8000
# (เป็นแค่ documentation — ไม่ได้ "เปิด" port จริง)
EXPOSE 8000

# คำสั่งที่รันเมื่อ container start
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### Dockerfile Instructions สรุป

| Instruction | ทำอะไร | Analogy |
|-------------|--------|---------|
| `FROM` | เลือก base image | เริ่มจากสูตรพื้นฐาน |
| `ENV` | ตั้ง environment variable | ตั้งค่าเตาอบ |
| `WORKDIR` | ตั้ง working directory | เข้าห้องครัว |
| `RUN` | รัน command (ตอน build) | เตรียมวัตถุดิบ |
| `COPY` | copy ไฟล์จาก host เข้า image | เอาวัตถุดิบเข้าครัว |
| `EXPOSE` | ประกาศ port (documentation) | ติดป้ายบอกหมายเลขห้อง |
| `CMD` | คำสั่ง default เมื่อ container start | เริ่มทำอาหาร! |

### Build Image

```bash
cd ~/django-postgresql-nginx-docker/sample
docker build -t notes-api ./app
```

> `docker build` = สร้าง image จาก Dockerfile
> `-t notes-api` = ตั้งชื่อ (tag) ว่า `notes-api`
> `./app` = ใช้ Dockerfile ใน directory `./app` (build context = `./app`)

**แสดงผล:**
```
[+] Building 45.3s (12/12) FINISHED
 => [1/7] FROM python:3.12-slim
 => [2/7] RUN apt-get update ...
 => [3/7] WORKDIR /app
 => [4/7] COPY requirements.txt .
 => [5/7] RUN pip install --no-cache-dir -r requirements.txt
 => [6/7] COPY . .
 => [7/7] RUN python manage.py collectstatic --noinput
 => exporting to image
 => => naming to docker.io/library/notes-api
```

ตรวจสอบ image:

```bash
docker images
```

**แสดงผล:**
```
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
notes-api    latest    abc123def456   15 seconds ago   350MB
...
```

### ลอง Run

```bash
docker run -p 8000:8000 notes-api
```

> Container จะรัน Django ด้วย Gunicorn — แต่จะ error!

**แสดงผล (error):**
```
django.db.utils.OperationalError: could not connect to server:
Connection refused. Is the server running on host "db" ...
```

❌ **error เพราะไม่มี PostgreSQL** — Django พยายามเชื่อมต่อ `DB_HOST=db` แต่ไม่มี container ชื่อ `db` ให้เชื่อมต่อ

💡 **ไม่ต้องกังวล!** — ใน Part 5 เราจะใช้ Docker Compose เชื่อม Django กับ PostgreSQL ให้ทำงานด้วยกัน

กด `Ctrl+C` เพื่อหยุด แล้ว clean up:

```bash
docker rm -f $(docker ps -aq --filter ancestor=notes-api) 2>/dev/null
```

---

## 8. Network — Container คุยกันยังไง?

ก่อนจะไปเรียน Docker Compose ใน Part ถัดไป มาเข้าใจ concept สำคัญอีกอันก่อน: **Docker Network**

### ปัญหา: Container แต่ละตัวถูกแยกจากกัน

โดยปกติ containers ถูก **แยก (isolate)** จากกัน — เหมือนอยู่คนละห้อง ถึงจะอยู่ในอาคารเดียวกันก็พูดคุยกันไม่ได้

### Solution: สร้าง Docker Network

```bash
docker network create mynet
```

> สร้าง network ชื่อ `mynet` — เหมือนสร้าง "ห้องรวม" ให้ containers คุยกันได้

รัน PostgreSQL ใน network:

```bash
docker run -d \
  --name db \
  --network mynet \
  -e POSTGRES_DB=testdb \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  postgres:16-alpine
```

> `--network mynet` = ให้ container นี้อยู่ใน network `mynet`
> `--name db` = ชื่อ container = `db` (⭐ ชื่อนี้จะกลายเป็น hostname ใน network!)

ตอนนี้ container อื่นที่อยู่ใน network `mynet` สามารถเชื่อมต่อ PostgreSQL ผ่านชื่อ `db` ได้:

```
ใน Docker Network "mynet":

┌──────┐                    ┌──────┐
│  web │ ── DB_HOST=db ──►  │  db  │
│      │    port 5432       │      │
└──────┘                    └──────┘
  ↑                           ↑
  Container ชื่อ "web"        Container ชื่อ "db"
  (Django)                   (PostgreSQL)
```

**Key Insight**: ใน Docker network, containers หากันด้วย **ชื่อ container** — ไม่ใช่ IP address, ไม่ใช่ `localhost`!

นี่คือเหตุผลที่ใน `.env` เราตั้ง:
```
DB_HOST=db    ← ชื่อ container/service, ไม่ใช่ localhost!
```

Clean up:

```bash
docker rm -f db
docker network rm mynet
```

💡 **Tip**: ใน Part 5 เราจะเรียน Docker Compose ซึ่งจะสร้าง network ให้อัตโนมัติ — ไม่ต้อง create เอง!

---

## 🤖 เมื่อติดปัญหา — ลองใช้ AI ช่วย Debug

ถ้าเจอ error กับ Docker ลอง copy error message แล้วใช้ prompt นี้:

```
ฉันกำลังเรียนรู้เรื่อง Docker fundamentals
ฉันรัน command: [วาง command ที่พิมพ์]
แล้วเจอ error นี้:

[วาง error message ที่เห็น]

ช่วยอธิบายว่า:
1. Error นี้หมายความว่าอะไร?
2. สาเหตุน่าจะเป็นอะไร?
3. ฉันควรตรวจสอบอะไรบ้าง? (อย่าบอกคำตอบตรงๆ แต่ช่วย guide ให้ฉันหาคำตอบเอง)
```

💡 **Tip**: วิธี debug Docker แบบเป็นระบบ:

```bash
# Step 1: Container รันอยู่ไหม?
docker ps

# Step 2: ดู log ของ container
docker logs <container_name>

# Step 3: เข้าไปดูข้างใน container
docker exec -it <container_name> bash

# Step 4: ดูว่า port ถูกใช้อยู่ไหม
sudo lsof -i :<port>
```

---

## 📋 สรุป

ใน Part นี้เราได้เรียนรู้ Docker Fundamentals ทั้งหมด:

| Concept | สิ่งที่เรียนรู้ |
|---------|---------------|
| **Docker คืออะไร** | Pack ทุกอย่างใน Container ที่ทำงานเหมือนกันทุกเครื่อง |
| **Image** | Blueprint (read-only) — สร้างจาก Dockerfile |
| **Container** | Running instance ของ Image — สร้าง/หยุด/ลบได้ |
| **Port Binding** | `-p host:container` — เปิดประตูจาก host เข้า container |
| **Environment Variables** | `-e KEY=VALUE` — ส่งค่าตั้งค่าเข้า container |
| **Volume** | `-v name:/path` — ข้อมูลไม่หายเมื่อลบ container |
| **Dockerfile** | สูตรสร้าง Image — FROM, COPY, RUN, CMD |
| **Network** | เชื่อม containers ให้คุยกันด้วยชื่อ |

**สิ่งที่ยังขาด**: เรายังต้องรัน `docker run` ยาวๆ สำหรับแต่ละ container ซึ่งมี 3 ตัว (db, web, nginx) — ใน Part 5 เราจะใช้ **Docker Compose** จัดการทุกอย่างด้วยไฟล์ YAML ไฟล์เดียว! 🎉

---

## 🧪 ลองทำ

1. **รัน Nginx container**: ลอง `docker run -d --name my-nginx -p 8080:80 nginx:1.27-alpine` — แล้วเปิด browser ไปที่ `http://localhost:8080` (หรือ `http://server-ip:8080`) ควรเห็นหน้า "Welcome to nginx!" จากนั้นลบ: `docker rm -f my-nginx`

2. **ดู Dockerfile ของ Nginx**: เปิดไฟล์ `sample/nginx/Dockerfile` อ่าน — มีแค่ 3 บรรทัด! ลองอธิบายว่าแต่ละบรรทัดทำอะไร

3. **Volume ทดลอง**: สร้าง container ที่ mount volume ลองเขียนไฟล์ข้างใน แล้วลบ container สร้างใหม่ — ไฟล์ยังอยู่ไหม?

4. **ตอบคำถาม**: ทำไมเราถึง COPY `requirements.txt` ก่อนแล้วค่อย `pip install` แยกจาก `COPY . .`? (Hint: Docker cache)

---

[← Part 3: Git & Server](part-3-git-and-server.md) | [Part 5: Docker Compose →](part-5-docker-compose.md)
