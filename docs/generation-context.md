# Generation Context — Sub-Agent Instructions

This document provides detailed context and instructions for generating each tutorial part.
Each section below corresponds to one `docs/part-*.md` file.

---

## Global Rules

### Language
- **Thai** for all explanations, descriptions, and narrative
- **English** for all technical terms (Docker, Container, Image, Volume, Nginx, etc.)
- Code comments in **English**
- Example: "เราจะใช้ Docker เพื่อสร้าง Container สำหรับ Django Application"

### Target Audience
- Junior developers who know: Django, PostgreSQL, HTML, CSS, Vue/Nuxt
- They do NOT know: Linux, Docker, deployment, cloud servers, CI/CD
- Assume zero Linux experience

### Writing Style
- Conversational, encouraging tone — like a senior developer mentoring a junior
- Use analogies to explain abstract concepts (e.g., "Image เหมือนสูตรอาหาร, Container เหมือนจานอาหารที่ทำออกมา")
- Every command must be explained — never say "just run this"
- Show expected output after every command
- Use ⚠️ for common mistakes, 💡 for tips, 📝 for notes, ✅ for verification steps

### Teaching Debugging & Error Reading (สำคัญมาก!)
This is a core principle of the entire tutorial. Students must learn to **read and understand error messages** — not just follow correct steps. For every part:

1. **Intentionally show the wrong way first** — Let students see the error, THEN fix it
2. **Show real error messages** — Copy the actual error output, highlight the important line
3. **Teach a systematic debugging approach**:
   - Step 1: อ่าน error message — บรรทัดไหนสำคัญ?
   - Step 2: ดู logs — `docker compose logs <service>`
   - Step 3: เข้าไปใน container ดู — `docker compose exec <service> bash`
   - Step 4: Google the error — ใช้ keyword อะไร?
4. **Include a "🔥 ผิดพลาดที่พบบ่อย" section** in every part with 2-3 common mistakes:
   - Show the exact error message students will see
   - Explain what the error means (สาเหตุ)
   - Show how to fix it (วิธีแก้)
   - Explain WHY the fix works (ทำไมถึงแก้ได้)
5. **Never just say "if you see an error, do X"** — always show the actual error text and teach students to identify the key information in it
6. **Use the 🔍 emoji for "reading error messages"** sections where you break down an error line by line

Example format for error analysis:
```
🔍 อ่าน Error Message:

$ docker compose up
ERROR: for web  Cannot start service web: driver failed programming 
external connectivity on endpoint: Bind for 0.0.0.0:8000 failed: 
port is already allocated
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                    ⬆️ บรรทัดนี้บอกว่า: port 8000 ถูกใช้งานอยู่แล้ว

สาเหตุ: มี process อื่นใช้ port 8000 อยู่
วิธีแก้: หา process ที่ใช้ port นี้แล้วหยุดมัน
$ sudo lsof -i :8000
$ kill <PID>
```

### Format
- Each part is a standalone markdown file in `docs/`
- Start with title, time estimate, and learning objectives
- End with navigation links (← previous | next →)
- Use fenced code blocks with language tags (`bash`, `python`, `yaml`, `nginx`)
- Include a "🔥 ผิดพลาดที่พบบ่อย" (Common Mistakes & Debugging) section in each part
- Include a "📋 สรุป" (Summary) section before the exercises
- Include a "🧪 ลองทำ" (Try it) section at the end of each part with exercises

### Sample Project Reference
The tutorial uses a sample Django Notes API project located in `sample/`:
```
sample/
├── app/                    # Django project
│   ├── Dockerfile          # Django + Gunicorn image
│   ├── requirements.txt    # Python dependencies
│   ├── manage.py
│   ├── config/             # Django settings
│   │   ├── __init__.py
│   │   ├── settings.py     # Uses python-decouple for env vars
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── notes/              # Simple Notes CRUD app
│       ├── __init__.py
│       ├── admin.py
│       ├── models.py       # Note model: title, body, timestamps
│       ├── serializers.py  # DRF ModelSerializer
│       ├── urls.py         # Router-based URLs
│       └── views.py        # ModelViewSet (full CRUD)
├── nginx/
│   ├── Dockerfile          # nginx:1.27-alpine based
│   └── nginx.conf          # Reverse proxy + static files
├── docker-compose.yml      # All 3 services: db, web, nginx
└── .env.example            # Environment variable template
```

Key technical details of the sample project:
- Django 5.1 + DRF + django-cors-headers
- python-decouple for environment variable management
- Gunicorn as WSGI server (3 workers)
- PostgreSQL 16 Alpine
- Nginx 1.27 Alpine as reverse proxy
- Static files shared via Docker volume between Django and Nginx

---

## Part 0: ภาพรวม — เราจะสร้างอะไร?

**File**: `docs/part-0-big-picture.md`
**Time**: 30 minutes
**Goal**: Students see the forest before the trees

### Content to generate:

1. **"Deployment" คืออะไร?**
   - Compare: `python manage.py runserver` on laptop vs. a URL anyone can visit
   - Analogy: ร้านอาหาร — coding = ทำอาหารที่บ้าน, deployment = เปิดร้านอาหาร
   - What changes: need a server that runs 24/7, a domain name, security, etc.

2. **Architecture Diagram**
   - Draw the full stack as ASCII art:
     ```
     Internet → Domain (DNS) → Server (Ubuntu)
                                  ├── Nginx (Port 80/443) — รับ request, serve static files
                                  │     ↓
                                  ├── Django + Gunicorn (Port 8000) — process request
                                  │     ↓
                                  └── PostgreSQL (Port 5432) — เก็บข้อมูล
                                  
     ทั้งหมดอยู่ใน Docker Containers
     ```
   - Explain each piece in ONE sentence

3. **ทำไมต้องใช้เครื่องมือเหล่านี้?**
   - Table comparing "ถ้าไม่ใช้" vs "ถ้าใช้" for each tool:
     | เครื่องมือ | ถ้าไม่ใช้ | ถ้าใช้ |
     |-----------|----------|-------|
     | Docker | ต้องติดตั้ง Python, PostgreSQL, Nginx ทีละตัว, version อาจไม่ตรง | สร้าง Container ที่เหมือนกันทุกเครื่อง |
     | Nginx | Django serve ไฟล์เองทุกอย่าง, ช้า, ไม่ปลอดภัย | จัดการ static files, HTTPS, security |
     | Gunicorn | `runserver` ไม่เหมาะกับ production, ช้า, ไม่ stable | รัน Django แบบ production-ready |
     | Docker Compose | ต้อง run docker command ทีละตัว | จัดการทุก container ด้วยไฟล์เดียว |

4. **สิ่งที่เราจะสร้างในบทเรียนนี้**
   - Screenshot/description of the sample Notes API project
   - List all 10 parts briefly — "road map" ของการเรียน

5. **Prerequisites**
   - สิ่งที่ต้องมี: คอมพิวเตอร์ที่เชื่อมต่อ Internet, GitHub account
   - สิ่งที่ต้องรู้: Django พื้นฐาน, SQL พื้นฐาน

6. **สิ่งที่สำคัญที่สุดที่จะได้เรียน: การอ่าน Error Message**
   - "ในบทเรียนนี้ เราจะไม่แค่สอนวิธีทำที่ถูกต้อง แต่จะสอนวิธี debug เมื่อมีปัญหา"
   - Error message คือ "เพื่อน" ไม่ใช่ "ศัตรู" — มันบอกเราว่าอะไรผิด
   - ทุก Part จะมี section "🔥 ผิดพลาดที่พบบ่อย" ที่สอนอ่าน error และ debug

---

## Part 1: เตรียมเครื่องมือ — Setup Environment

**File**: `docs/part-1-setup-environment.md`
**Time**: 1-2 hours
**Goal**: Students have a working Linux environment with Git, Docker, Docker Compose installed

### Content to generate:

1. **ทำไมต้อง Linux?**
   - Brief history: Linus Torvalds, 1991, open source
   - Why servers use Linux: free, stable, lightweight, most cloud VMs are Linux
   - Ubuntu = popular Linux distribution, beginner-friendly

2. **เลือก Environment** (provide instructions for all options)
   - **Option A: WSL2 on Windows**
     - Step-by-step: Enable WSL, install Ubuntu 24.04 from Microsoft Store
     - Open terminal, set username/password
   - **Option B: Cloud VM (provider-agnostic)**
     - Generic steps: Create an Ubuntu 24.04 VM, open ports 22/80/443
     - SSH connection: `ssh username@your-server-ip`
     - Mention: Google Cloud, DigitalOcean, AWS, Linode all work
   - **Option C: VirtualBox** (brief mention)

3. **Linux Command Line พื้นฐาน**
   Teach each command IN CONTEXT of a real task, not as isolated list:
   
   - **Task: สำรวจ Server**
     - `pwd` — "ตอนนี้ฉันอยู่ไหน?"
     - `ls`, `ls -la` — "มีอะไรอยู่ตรงนี้บ้าง?"
     - `cd /home`, `cd ~`, `cd ..` — "ย้ายไปที่อื่น"
   
   - **Task: สร้างโฟลเดอร์โปรเจค**
     - `mkdir -p projects/my-app` — สร้างโฟลเดอร์
     - `touch test.txt` — สร้างไฟล์เปล่า
     - `nano test.txt` or `vim test.txt` — แก้ไขไฟล์
     - `cat test.txt` — อ่านไฟล์
     - `cp`, `mv`, `rm`, `rm -rf` — คัดลอก, ย้าย, ลบ
   
   - **Task: ติดตั้งโปรแกรม**
     - `sudo apt update` — อัพเดท package list
     - `sudo apt install tree` — ติดตั้ง tree
     - `tree` — ดูโครงสร้างโฟลเดอร์
   
   - **Task: ดู Process**
     - `ps aux` — ดู process ที่กำลังทำงาน
     - `top` or `htop` — monitor แบบ real-time
     - `Ctrl+C` — หยุด process

4. **ติดตั้ง Git**
   ```bash
   sudo apt install git
   git --version
   git config --global user.name "Your Name"
   git config --global user.email "your@email.com"
   ```

5. **ติดตั้ง Docker & Docker Compose**
   - Follow official Docker docs method (apt repository method)
   - Add user to docker group: `sudo usermod -aG docker $USER`
   - Verify: `docker --version`, `docker compose version`
   - Test: `docker run hello-world`

6. **✅ Verification Checklist**
   - [ ] `git --version` shows version
   - [ ] `docker --version` shows version
   - [ ] `docker compose version` shows version
   - [ ] `docker run hello-world` runs successfully

7. **🔥 ผิดพลาดที่พบบ่อย (Common Mistakes)**
   - **"Permission denied" when running docker**
     - Show error: `Got permission denied while trying to connect to the Docker daemon socket`
     - สาเหตุ: User ยังไม่ได้อยู่ใน docker group
     - วิธีแก้: `sudo usermod -aG docker $USER` แล้ว logout/login ใหม่
     - 🔍 สอนอ่าน: "permission denied" + "Docker daemon socket" = ปัญหาสิทธิ์
   - **"command not found" after installing Docker**
     - สาเหตุ: ติดตั้งไม่ครบ หรือ PATH ไม่ถูก
     - วิธีแก้: ตรวจสอบ installation steps อีกครั้ง
   - **SSH connection refused**
     - Show error: `ssh: connect to host X port 22: Connection refused`
     - สาเหตุ: SSH server ไม่ได้รัน, firewall block port 22, หรือ IP ผิด
     - วิธี debug: ทีละ step — เช็ค IP → เช็ค firewall → เช็ค SSH service

---

## Part 2: ทำความเข้าใจ Django Project

**File**: `docs/part-2-understanding-django-project.md`
**Time**: 30 minutes
**Goal**: Students understand the sample project and key settings for deployment

### Content to generate:

1. **Overview ของ Sample Project**
   - Simple Notes API — CRUD for notes
   - Show project structure with `tree` command
   - Explain each file briefly

2. **settings.py — สิ่งที่ต้องเข้าใจก่อน Deploy**
   - `DEBUG` — True for development, False for production (explain why)
   - `ALLOWED_HOSTS` — Security: which domains can access
   - `DATABASES` — Currently configured for PostgreSQL via env vars
   - `STATIC_ROOT` — Where collected static files go
   - `SECRET_KEY` — Must be different in production

3. **Environment Variables ด้วย python-decouple**
   - Why hardcoding secrets is bad (show GitHub search for leaked keys)
   - How `config('DB_PASSWORD')` reads from `.env`
   - `.env.example` vs `.env` — one is committed, one is NOT

4. **Development vs Production**
   | | Development | Production |
   |--|------------|-----------|
   | Server | `runserver` | Gunicorn |
   | Database | SQLite | PostgreSQL |
   | DEBUG | True | False |
   | Static Files | Django serves | Nginx serves |
   | HTTPS | No | Yes |

5. **Gunicorn คืออะไร?**
   - `runserver` is single-threaded, for dev only
   - Gunicorn = production WSGI server, multiple workers
   - Analogy: runserver = พนักงานคนเดียว, Gunicorn = พนักงานหลายคนทำงานพร้อมกัน

---

## Part 3: Git & เอาโค้ดขึ้น Server

**File**: `docs/part-3-git-and-server.md`
**Time**: 1 hour
**Goal**: Students can clone code to server AND understand why we need Docker

### Content to generate:

1. **Git พื้นฐาน (Review)**
   - `git clone`, `git pull`, `git status`, `git log --oneline -5`
   - This is review for students who already know Git

2. **สร้าง SSH Key สำหรับ GitHub**
   - `ssh-keygen -t ed25519 -C "your@email.com"`
   - `cat ~/.ssh/id_ed25519.pub` — copy this
   - Add to GitHub → Settings → SSH Keys
   - Test: `ssh -T git@github.com`

3. **Clone Project ขึ้น Server**
   ```bash
   cd ~
   git clone git@github.com:your-username/django-postgresql-nginx-docker.git
   cd django-postgresql-nginx-docker/sample
   ls -la
   ```

4. **🧪 ลอง Run Django แบบ Manual (สำคัญมาก!)**
   This is the "feel the pain" section:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   cd app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   
   - Try to run: `python manage.py runserver 0.0.0.0:8000`
   - **Problem 1**: No PostgreSQL installed → error
   - Install PostgreSQL manually → tedious, version issues
   - **Problem 2**: Close terminal → server stops
   - **Problem 3**: No static file serving in production
   - **Problem 4**: Only 1 process
   
   **Conclusion**: "ถ้าเราต้อง setup ทุกอย่างเอง ทุกครั้งที่ย้าย server จะเสียเวลามาก → นี่คือเหตุผลที่เราต้องใช้ Docker"

5. **🔥 ผิดพลาดที่พบบ่อย & การอ่าน Error**
   - **🔍 Django OperationalError — "could not connect to server"**
     ```
     django.db.utils.OperationalError: could not connect to server:
     Connection refused. Is the server running on host "localhost" (127.0.0.1)
     and accepting TCP/IP connections on port 5432?
     ```
     - วิธีอ่าน: "could not connect" + "localhost" + "port 5432" = PostgreSQL ไม่ได้รัน หรือ host/port ผิด
     - สาเหตุ: ยังไม่ได้ install PostgreSQL, หรือ PostgreSQL ไม่ได้ start
     - วิธี debug: เช็คว่า PostgreSQL รันอยู่: `sudo systemctl status postgresql`
   - **"ModuleNotFoundError: No module named 'decouple'"**
     - สาเหตุ: ลืม activate virtualenv หรือลืม `pip install`
     - วิธี debug: `which python` → ถ้าไม่ใช่ venv path แสดงว่าลืม activate
   - **"Address already in use" — port 8000**
     - สาเหตุ: มี process อื่นใช้ port อยู่
     - วิธีแก้: `sudo lsof -i :8000` → `kill <PID>`

6. **Clean up**
   ```bash
   deactivate
   rm -rf venv
   ```

---

## Part 4: Docker Fundamentals

**File**: `docs/part-4-docker-fundamentals.md`
**Time**: 2-3 hours
**Goal**: Students understand Docker concepts and can build/run containers

### Content to generate:

1. **Docker คืออะไร?**
   - Problem: "works on my machine" → ไม่ work บน server
   - Solution: Package ทุกอย่างลงใน Container ที่เหมือนกันทุกเครื่อง
   - Analogy: Container = กล่องข้าว (ข้าว + กับ + ช้อน ครบทุกอย่าง, พร้อมกินทุกที่)

2. **Core Concepts**
   - **Image** = สูตรอาหาร (blueprint, read-only)
   - **Container** = จานอาหารที่ทำออกมา (running instance, can be created/stopped/deleted)
   - **Dockerfile** = ขั้นตอนการทำอาหาร (instructions to build an image)
   - **Registry (Docker Hub)** = หนังสือสูตรอาหาร (place to store/share images)
   - Show relationship diagram

3. **Hands-on: Container ตัวแรก**
   ```bash
   docker run hello-world
   ```
   - Explain what happened step by step (pull image → create container → run → exit)
   
   ```bash
   docker run -it ubuntu:24.04 bash
   ```
   - Explore inside: `ls`, `cat /etc/os-release`, `exit`
   - This is a full Ubuntu running inside a container!

4. **Docker Commands**
   - `docker images` — list images
   - `docker ps` — list running containers
   - `docker ps -a` — list ALL containers (including stopped)
   - `docker stop <id>` — stop container
   - `docker rm <id>` — remove container
   - `docker rmi <image>` — remove image

5. **Run PostgreSQL ด้วย Docker**
   ```bash
   # ❌ This fails — needs configuration
   docker run postgres:16-alpine
   
   # ✅ This works — with environment variables
   docker run -d \
     --name my-postgres \
     -e POSTGRES_DB=testdb \
     -e POSTGRES_USER=testuser \
     -e POSTGRES_PASSWORD=testpass \
     -p 5432:5432 \
     postgres:16-alpine
   ```
   - Explain each flag: `-d` (detached), `--name`, `-e` (env var), `-p` (port)
   - **Port Binding** `-p 5432:5432`: "เปิดประตูจาก host เข้าไปใน container"
   - Verify: `docker exec -it my-postgres psql -U testuser testdb`

6. **Volume — ข้อมูลที่ไม่หาย**
   - Stop and remove container → data is GONE
   - Demonstrate this:
     ```bash
     docker exec -it my-postgres psql -U testuser testdb -c "CREATE TABLE demo(id int); INSERT INTO demo VALUES(1);"
     docker stop my-postgres && docker rm my-postgres
     # Run again → table is gone!
     ```
   - Solution: Volumes
     ```bash
     docker volume create pgdata
     docker run -d --name my-postgres -v pgdata:/var/lib/postgresql/data ...
     ```
   - Now stop/remove/recreate → data survives!
   - `docker volume ls`, `docker volume inspect pgdata`

7. **Build Image ของ Django**
   - Walk through the Dockerfile line by line (reference `sample/app/Dockerfile`)
   - Explain each instruction: FROM, ENV, WORKDIR, RUN, COPY, EXPOSE, CMD
   - Build: `docker build -t notes-api ./app`
   - Run: `docker run -p 8000:8000 notes-api` (will fail → no DB → that's OK, we'll fix in Part 5)

8. **Network — Container คุยกันยังไง?**
   - By default, containers are isolated
   - `docker network create mynet`
   - `docker run --network mynet --name db ...`
   - `docker run --network mynet --name web ...`
   - Containers on same network find each other by name
   - Django `DB_HOST=db` (not localhost!)

9. **🔥 ผิดพลาดที่พบบ่อย & การอ่าน Error**
   - **🔍 "Bind for 0.0.0.0:5432 failed: port is already allocated"**
     ```
     Error response from daemon: driver failed programming external 
     connectivity on endpoint my-postgres: Bind for 0.0.0.0:5432 
     failed: port is already allocated
     ```
     - วิธีอ่าน: "Bind failed" + "port is already allocated" = port ถูกใช้แล้ว
     - สาเหตุ: มี container เก่า หรือ PostgreSQL บน host ใช้ port 5432 อยู่
     - วิธี debug: `docker ps -a` → มี container ชื่อ my-postgres อยู่ไหม? → `docker rm -f my-postgres`
     - หรือ: `sudo lsof -i :5432` → ดูว่า process อะไรใช้อยู่
   - **🔍 "FATAL: password authentication failed for user"**
     ```
     psql: error: FATAL: password authentication failed for user "testuser"
     ```
     - สาเหตุ: password ไม่ตรงกับตอนสร้าง container, หรือ volume เก็บ password เก่า
     - วิธีแก้: `docker volume rm pgdata` แล้วสร้างใหม่ (⚠️ ข้อมูลหาย!)
     - บทเรียน: volume เก็บข้อมูลรวมถึง user/password ที่สร้างครั้งแรก
   - **🔍 Docker build fails — "COPY failed: file not found"**
     ```
     COPY failed: file not found in build context or excluded by .dockerignore
     ```
     - วิธีอ่าน: "file not found in build context" = Dockerfile หาไฟล์ไม่เจอ
     - สาเหตุ: `docker build` context path ผิด, หรือไฟล์อยู่ใน `.dockerignore`
     - วิธี debug: เช็ค `ls` ใน directory ที่ build, เช็ค `.dockerignore`
   - **🔍 Container ดูเหมือนรันแต่เข้าไม่ได้**
     - วิธี debug แบบ systematic:
       1. `docker ps` — container รันอยู่จริงไหม?
       2. `docker logs <container>` — มี error อะไรไหม?
       3. `docker exec -it <container> bash` — เข้าไปดูข้างในได้ไหม?
       4. `curl localhost:<port>` — เรียกจาก host ได้ไหม?

---

## Part 5: Docker Compose — จัดการหลาย Container

**File**: `docs/part-5-docker-compose.md`
**Time**: 2 hours
**Goal**: Students can write and use docker-compose.yml

### Content to generate:

1. **ทำไมต้อง Docker Compose?**
   - Recap Part 4: we ran `docker run` with many flags for each container
   - With 3 containers (db, web, nginx) = 3 long commands, easy to get wrong
   - Docker Compose = one YAML file to define everything

2. **docker-compose.yml Structure**
   - Walk through `sample/docker-compose.yml` line by line
   - Explain each key: `services`, `image`, `build`, `volumes`, `environment`, `env_file`, `ports`, `depends_on`, `healthcheck`

3. **First Run: Django + PostgreSQL only**
   - Start with a simplified compose (just db + web, no nginx yet)
   - ```bash
     docker compose up -d --build
     ```
   - Watch the output, explain what's happening
   - Check status: `docker compose ps`
   - View logs: `docker compose logs web`, `docker compose logs -f`

4. **Essential Commands**
   - `docker compose up -d` — start all services in background
   - `docker compose up -d --build` — rebuild images then start
   - `docker compose down` — stop and remove containers
   - `docker compose down -v` — also remove volumes (⚠️ destroys data!)
   - `docker compose ps` — list services and their status
   - `docker compose logs -f web` — follow logs of web service
   - `docker compose exec web bash` — get shell inside running container
   - `docker compose restart web` — restart one service

5. **Run Migrations & Create Superuser**
   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```
   - Access Django Admin: `http://server-ip:8000/admin/`
   - Test API: `http://server-ip:8000/api/notes/`

6. **Environment Variables with .env**
   - Copy `.env.example` to `.env`
   - Explain `env_file:` directive in compose
   - `docker compose config` — see resolved values
   - ⚠️ `.env` must be in `.gitignore`

7. **Compose Networking (automatic)**
   - Compose creates a default network for all services
   - Services can find each other by service name
   - `DB_HOST=db` because the service is named `db`

8. **🔥 ผิดพลาดที่พบบ่อย & การอ่าน Error**
   - **🔍 "web" service fails: "Connection refused" to database**
     ```
     django.db.utils.OperationalError: could not connect to server:
     Connection refused. Is the server running on host "db" (172.18.0.2)
     and accepting TCP/IP connections on port 5432?
     ```
     - วิธีอ่าน: ดูว่า host เป็น "db" (ถูกต้อง) แต่ connection refused = db ยังไม่พร้อม
     - สาเหตุ: `depends_on` ไม่ได้ wait จนกว่า DB จะพร้อมรับ connection — แค่ wait จนกว่า container start
     - วิธีแก้: ใช้ `depends_on` + `condition: service_healthy` + `healthcheck`
     - บทเรียน: "container started" ≠ "service ready"
   - **🔍 YAML syntax error**
     ```
     yaml.scanner.ScannerError: mapping values are not allowed here
       in "docker-compose.yml", line 15, column 12
     ```
     - วิธีอ่าน: "line 15, column 12" = ไปดูบรรทัดที่ 15 ตำแหน่งที่ 12
     - สาเหตุ: indentation ผิด (YAML ใช้ space ไม่ใช่ tab, indentation สำคัญมาก)
     - วิธี debug: `docker compose config` — จะแสดง error ถ้า YAML ผิด
     - 💡 Tip: ใช้ editor ที่ highlight YAML syntax
   - **🔍 "docker compose: command not found" vs "docker-compose"**
     - Docker Compose V1: `docker-compose` (มีขีด, ติดตั้งแยก)
     - Docker Compose V2: `docker compose` (ไม่มีขีด, มาพร้อม Docker)
     - เราใช้ V2 — ถ้าไม่ work ให้เช็ค Docker version
   - **🔍 Environment variable ไม่ถูกส่งเข้า container**
     - วิธี debug: `docker compose exec web env | grep DB_` — ดูว่ามี env var ไหม
     - สาเหตุ: `.env` path ผิด, หรือชื่อ variable ผิด
     - `docker compose config` — ดู resolved values

---

## Part 6: Nginx — Reverse Proxy

**File**: `docs/part-6-nginx.md`
**Time**: 2 hours
**Goal**: Students understand Nginx, write config, complete the full stack

### Content to generate:

1. **Nginx คืออะไร?**
   - Web server & reverse proxy
   - Used by ~34% of all websites
   - Very fast at serving static files
   - Handles thousands of concurrent connections

2. **Reverse Proxy อธิบายง่ายๆ**
   - Analogy: Nginx = พนักงานต้อนรับ (receptionist), Django/Gunicorn = พ่อครัว (chef)
   - Receptionist decides: static file request → serve directly, API request → forward to chef
   - Benefits: security (Django hidden from internet), performance, HTTPS termination
   
   - Diagram:
     ```
     Without Nginx:
     Internet → Django (ทำทุกอย่างเอง, เหนื่อย)
     
     With Nginx:
     Internet → Nginx → Django (ทำแค่ API)
                  ↓
              Static Files (Nginx จัดการเอง)
     ```

3. **nginx.conf — อธิบายทีละบรรทัด**
   - Walk through `sample/nginx/nginx.conf`
   - `upstream django` — define where Django is
   - `server` block — listen on port 80
   - `location /static/` — serve static files directly
   - `location /` — proxy_pass to Django
   - Explain proxy headers (X-Real-IP, X-Forwarded-For, etc.)

4. **Nginx Dockerfile**
   - Walk through `sample/nginx/Dockerfile` (very simple — 3 lines)

5. **Complete docker-compose.yml**
   - Now add nginx service to the compose file
   - Key points:
     - Only nginx exposes port 80 to the outside
     - web service NO LONGER exposes port 8000 (internal only)
     - `static_volume` shared between web (write) and nginx (read)
   - Show the full `docker-compose.yml`

6. **Collect Static Files & Run**
   ```bash
   docker compose up -d --build
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py collectstatic --noinput
   ```
   - Access: `http://server-ip/` (port 80, no need to specify)
   - Access admin: `http://server-ip/admin/`
   - Access API: `http://server-ip/api/notes/`
   - 🎉 "Full stack is running!"

7. **ทดสอบ Static Files**
   - Go to `/admin/` — if CSS loads, Nginx is serving static files correctly
   - Check nginx logs: `docker compose logs nginx`

8. **🔥 ผิดพลาดที่พบบ่อย & การอ่าน Error**
   - **🔍 Nginx "502 Bad Gateway"**
     ```
     502 Bad Gateway
     nginx/1.27.0
     ```
     - วิธีอ่าน: 502 = Nginx ทำงานอยู่ แต่ connect ไปที่ Django/Gunicorn ไม่ได้
     - วิธี debug:
       1. `docker compose ps` — web service รันอยู่ไหม?
       2. `docker compose logs web` — Gunicorn มี error อะไร?
       3. เช็ค `upstream` ใน nginx.conf — ชื่อ service ตรงกับ compose ไหม?
     - สาเหตุที่พบบ่อย: web container crash, upstream name ผิด, port ผิด
   - **🔍 Django Admin CSS ไม่โหลด (หน้าเป็นขาวเปล่า)**
     - สาเหตุ: ลืม run `collectstatic`, หรือ volume mount ผิด
     - วิธี debug:
       1. `docker compose exec web ls /app/staticfiles/` — มีไฟล์ไหม?
       2. `docker compose exec nginx ls /app/staticfiles/` — nginx เห็นไฟล์ไหม?
       3. ถ้าไม่มี → `docker compose exec web python manage.py collectstatic --noinput`
     - บทเรียน: web สร้างไฟล์ → shared volume → nginx อ่านไฟล์
   - **🔍 Nginx "403 Forbidden" สำหรับ static files**
     - สาเหตุ: permission ไม่ถูก — nginx user อ่านไฟล์ไม่ได้
     - วิธีแก้: `docker compose exec web chmod -R 755 /app/staticfiles/`
   - **🔍 "host not found in upstream" error**
     ```
     nginx: [emerg] host not found in upstream "web" in /etc/nginx/conf.d/nginx.conf:3
     ```
     - วิธีอ่าน: "host not found" + "upstream web" = nginx หา service ชื่อ "web" ไม่เจอ
     - สาเหตุ: ชื่อใน `upstream` ไม่ตรงกับชื่อ service ใน docker-compose.yml
     - วิธีแก้: เช็คว่า service name match กัน

---

## Part 7: Production Readiness — Domain, HTTPS, Security

**File**: `docs/part-7-production-readiness.md`
**Time**: 1-2 hours
**Goal**: Students set up domain, HTTPS, and basic security

### Content to generate:

1. **Domain & DNS**
   - What is a domain name, what is DNS
   - How to set up an A record pointing to your server IP
   - Provider-agnostic instructions (any domain registrar works)
   - Test: `ping yourdomain.com`, `curl http://yourdomain.com`
   - Update `ALLOWED_HOSTS` in `.env`
   - Update `server_name` in nginx.conf

2. **HTTPS ด้วย Let's Encrypt**
   - Why HTTPS is non-negotiable (security, SEO, browser warnings)
   - What is SSL/TLS certificate (briefly)
   - Let's Encrypt = free certificates
   - Method: Use Certbot with Docker
   - Modified `docker-compose.yml` to include certbot service
   - Modified `nginx.conf` for HTTPS:
     - Listen on 443 with ssl
     - Redirect 80 → 443
     - Certificate paths
   - Auto-renewal with cron or certbot timer
   - ✅ Test: visit `https://yourdomain.com`

3. **Security พื้นฐาน**
   - `DEBUG=False` (never True in production)
   - `ALLOWED_HOSTS` — set to your domain only
   - Strong passwords for database and Django admin
   - Firewall: `sudo ufw allow 22,80,443`
   - Non-root user best practice
   - Keep Docker images updated

4. **Database Backup & Restore**
   ```bash
   # Backup
   docker compose exec db pg_dump -U postgres notesdb > backup_$(date +%Y%m%d).sql
   
   # Restore
   docker compose exec -T db psql -U postgres notesdb < backup_20240101.sql
   ```
   - Set up daily backup with cron

5. **Run Migrations ใน Production**
   - Always backup before migrating
   - `docker compose exec web python manage.py migrate --noinput`
   - Check: `docker compose exec web python manage.py showmigrations`

6. **🔥 ผิดพลาดที่พบบ่อย & การอ่าน Error**
   - **🔍 Let's Encrypt "too many failed authorizations"**
     - สาเหตุ: DNS ยังไม่ propagate, หรือ port 80 ไม่เปิด
     - วิธี debug: `dig yourdomain.com` → IP ตรงไหม? `sudo ufw status` → port 80 เปิดไหม?
   - **🔍 "NET::ERR_CERT_AUTHORITY_INVALID" ใน browser**
     - สาเหตุ: ใช้ self-signed cert หรือ Let's Encrypt ยังไม่ issue cert สำเร็จ
     - วิธี debug: `docker compose logs certbot` → ดู error
   - **🔍 Django "CSRF verification failed"**
     - สาเหตุ: หลังเปิด HTTPS, Django ต้องรู้ว่า request มาผ่าน proxy
     - วิธีแก้: เพิ่ม `CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']` ใน settings
     - และเช็คว่า nginx ส่ง `X-Forwarded-Proto` header
   - **🔍 DEBUG=False แล้วเจอ "Server Error (500)" ไม่มี detail**
     - นี่คือ behavior ที่ถูกต้อง! Production ไม่ควรแสดง error detail ให้ user
     - วิธีดู error จริง: `docker compose logs web` → error อยู่ใน log
     - บทเรียน: production error ดูจาก log, ไม่ใช่จากหน้าเว็บ

---

## Part 8: CI/CD — Auto Deploy ด้วย GitHub Actions

**File**: `docs/part-8-cicd.md`
**Time**: 2 hours
**Goal**: Students set up automated deployment pipeline

### Content to generate:

1. **CI/CD คืออะไร?**
   - Manual deploy process (recap what we did):
     1. SSH to server
     2. `git pull`
     3. `docker compose up -d --build`
     4. Run migrations
   - Problems: error-prone, slow, requires SSH access, easy to forget steps
   - CI/CD = automate this entire process
   - CI = Continuous Integration (test code), CD = Continuous Deployment (deploy code)

2. **GitHub Actions Overview**
   - Free for public repos, generous free tier for private
   - Workflow = YAML file in `.github/workflows/`
   - Triggered by events (push, pull request, etc.)
   - Runs on GitHub's servers

3. **Walk through deploy.yml**
   - Reference `.github/workflows/deploy.yml` in the repo
   - Explain each section:
     - `on: push: branches: [main]` — trigger on push to main
     - `jobs.deploy.runs-on` — runs on Ubuntu
     - SSH action — connects to your server
     - Script steps — git pull, compose up, migrate

4. **ตั้งค่า GitHub Secrets**
   - Go to GitHub repo → Settings → Secrets → Actions
   - Add:
     - `SERVER_HOST` — your server IP
     - `SERVER_USER` — SSH username
     - `SERVER_SSH_KEY` — private SSH key
   - ⚠️ Never put these in code!
   - Show screenshots / step-by-step

5. **ทดสอบ Pipeline**
   - Make a small code change (e.g., change API response)
   - `git add . && git commit -m "test deploy" && git push`
   - Go to GitHub → Actions tab → watch it run
   - Visit your site → see the change
   - 🎉 "You just deployed automatically!"

6. **เพิ่ม Testing (Optional)**
   - Add a test step before deploy
   - Run Django tests in a Docker container
   - Only deploy if tests pass

7. **🔥 ผิดพลาดที่พบบ่อย & การอ่าน Error**
   - **🔍 GitHub Actions: "Permission denied (publickey)"**
     ```
     ssh: connect to host X.X.X.X port 22: Permission denied (publickey)
     ```
     - วิธีอ่าน: "Permission denied (publickey)" = SSH key ไม่ match
     - สาเหตุ: ลืมเพิ่ม public key บน server, หรือ private key ใน GitHub Secret ไม่ถูก
     - วิธี debug:
       1. ลอง SSH จากเครื่องตัวเอง → ได้ไหม?
       2. เช็ค `~/.ssh/authorized_keys` บน server
       3. เช็ค GitHub Secret → copy ถูกต้องไหม? มี newline ต่อท้ายไหม?
   - **🔍 GitHub Actions: "docker compose: command not found"**
     - สาเหตุ: Server ไม่ได้ install Docker หรือยังเป็น V1
     - วิธี debug: SSH เข้า server → `docker compose version`
   - **🔍 Deploy สำเร็จแต่เว็บไม่เปลี่ยน**
     - สาเหตุ: Docker cache — image ไม่ได้ build ใหม่
     - วิธีแก้: ใช้ `docker compose up -d --build` (มี `--build`)
     - หรือ: `docker compose build --no-cache web`
   - **🔍 อ่าน GitHub Actions Logs**
     - สอนวิธีอ่าน log ใน Actions tab
     - Green checkmark = pass, Red X = fail
     - Click เข้าไปดู step ที่ fail → expand log → อ่าน error
     - 💡 ส่วนใหญ่ error จะอยู่ใน output บรรทัดท้ายๆ

---

## Part 9: สรุปและก้าวต่อไป

**File**: `docs/part-9-recap.md`
**Time**: 30 minutes
**Goal**: Consolidate learning, provide reference material, suggest next steps

### Content to generate:

1. **Review Architecture**
   - Show the same diagram from Part 0
   - But now explain each piece with confidence
   - "ตอน Part 0 เราเห็น diagram นี้แล้วงง, ตอนนี้เราเข้าใจทุกส่วนแล้ว"

2. **Cheat Sheet — คำสั่งที่ใช้บ่อย**
   Organized by task:
   
   **Docker Compose**
   | คำสั่ง | ใช้ตอนไหน |
   |--------|----------|
   | `docker compose up -d --build` | Start/rebuild ทุก service |
   | `docker compose down` | หยุดทุก service |
   | `docker compose ps` | ดู status |
   | `docker compose logs -f web` | ดู log ของ Django |
   | `docker compose exec web bash` | เข้าไปใน container |
   | `docker compose exec web python manage.py migrate` | Run migration |
   
   **Server Management**
   | คำสั่ง | ใช้ตอนไหน |
   |--------|----------|
   | `df -h` | เช็คพื้นที่ disk |
   | `free -h` | เช็ค RAM |
   | `docker system prune` | ลบ resource ที่ไม่ใช้ |
   
   **Update & Deploy**
   | คำสั่ง | ใช้ตอนไหน |
   |--------|----------|
   | `git pull origin main` | ดึงโค้ดล่าสุด |
   | `docker compose up -d --build` | Rebuild |
   | `docker compose exec db pg_dump ...` | Backup database |

3. **Common Troubleshooting — Systematic Debugging Guide**
   สอนกระบวนการ debug แบบเป็นระบบ:
   
   **Step 1: ดู Status**
   ```bash
   docker compose ps           # service ไหนรันอยู่?
   docker compose ps -a        # มี service ไหน exit ไปไหม?
   ```
   
   **Step 2: อ่าน Logs**
   ```bash
   docker compose logs web     # ดู log ของ Django
   docker compose logs db      # ดู log ของ PostgreSQL
   docker compose logs nginx   # ดู log ของ Nginx
   docker compose logs -f      # follow log ทุก service
   ```
   
   **Step 3: เข้าไปใน Container**
   ```bash
   docker compose exec web bash    # เข้าไปดูข้างใน
   docker compose exec db psql -U postgres  # เช็ค database
   ```
   
   **Step 4: เช็ค Resources**
   ```bash
   df -h                       # disk เต็มไหม?
   free -h                     # RAM พอไหม?
   docker system df             # Docker ใช้ disk เท่าไหร่?
   ```
   
   **Quick Reference — Error → สาเหตุ → วิธีแก้**
   | Error | สาเหตุ | วิธีแก้ |
   |-------|--------|--------|
   | Container won't start | Config error, missing env var | `docker compose logs <service>` |
   | Port already in use | Process อื่นใช้ port อยู่ | `sudo lsof -i :<port>` → `kill` |
   | Permission denied | Docker group, file permission | `sudo usermod -aG docker $USER` |
   | Connection refused to DB | DB ยังไม่พร้อม, host ผิด | เช็ค DB_HOST, healthcheck |
   | 502 Bad Gateway | Django/Gunicorn ไม่รัน | `docker compose logs web` |
   | Static files ไม่โหลด | ลืม collectstatic, volume ผิด | `docker compose exec web python manage.py collectstatic` |
   | HTTPS cert error | DNS ไม่ตรง, port 80 ไม่เปิด | `dig domain`, `ufw status` |
   | Deploy ไม่เปลี่ยน | Docker cache | `docker compose up -d --build` |

4. **🧪 Exercise: Deploy Nuxt/Vue Frontend**
   - Challenge: Add a Nuxt/Vue frontend to the stack
   - Hints:
     - Build Nuxt with `npm run build` / `npm run generate`
     - Serve built files through Nginx
     - Add a new service in docker-compose.yml OR serve through existing Nginx
   - This is left as an exercise for the student

5. **What's Next?**
   - Monitoring: Prometheus + Grafana, Sentry for error tracking
   - Scaling: Multiple servers, load balancer
   - Container Orchestration: Kubernetes (when you outgrow Compose)
   - Managed Services: Cloud SQL, Cloud Run, App Engine
   - Infrastructure as Code: Terraform, Ansible
   - Logging: ELK Stack, Loki

---

## Sub-Agent Prompt Template

When generating each part, use this prompt template:

```
You are writing a tutorial for junior developers learning to deploy Django with Docker.

**Context:**
- Target audience: Junior devs who know Django/Vue but NOT Linux/Docker/deployment  
- Language: Thai for explanations, English for technical terms
- Tone: Mentoring, encouraging, conversational
- Repo structure: [paste relevant sample/ files]

**Your task:**
Generate the complete content for [Part X: Title].

**Requirements:**
- Follow the generation context from `docs/generation-context.md` for this part
- Include all code blocks with expected output
- Use emoji markers: ⚠️ common mistakes, 💡 tips, 📝 notes, ✅ verification, 🔍 error analysis, 🔥 debugging
- Include a "🔥 ผิดพลาดที่พบบ่อย" section with real error messages and step-by-step debugging
- End with "📋 สรุป" (summary) and "🧪 ลองทำ" (exercises)
- Include navigation links at bottom
- Reference files from sample/ directory when showing code

**Important — Debugging is a CORE skill being taught:**
- Intentionally show the WRONG way first, then the error, then the fix
- Show REAL error messages — copy exact error output students will see
- For each error: show the message → highlight the key line → explain สาเหตุ → show วิธีแก้ → explain ทำไมถึงแก้ได้
- Teach students to read error messages systematically: which line matters? What keywords to look for?
- Every command must be explained — never say "just run this"
- Show expected output after key commands
- Use analogies for abstract concepts
- Teach concepts BEFORE they are needed, not after
```
