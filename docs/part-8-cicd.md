# Part 8: CI/CD — Auto Deploy ด้วย GitHub Actions

> ⏱️ เวลาโดยประมาณ: 2 ชั่วโมง

## 🎯 สิ่งที่จะได้เรียนรู้ใน Part นี้

- เข้าใจ CI/CD คืออะไร ทำไมต้องใช้
- เข้าใจ GitHub Actions — workflow, jobs, steps
- อ่าน deploy.yml ออกทุกบรรทัด
- ตั้งค่า GitHub Secrets สำหรับ SSH
- ทดสอบ auto deploy — push code แล้ว deploy อัตโนมัติ!

---

## 1. CI/CD คืออะไร?

### ทบทวน: ตอนนี้เรา deploy ยังไง?

ทุกครั้งที่แก้ code แล้วอยาก deploy เราต้อง:

```bash
# 1. SSH เข้า server
ssh username@server-ip

# 2. ดึง code ล่าสุด
cd ~/django-postgresql-nginx-docker/sample
git pull origin main

# 3. Rebuild + restart containers
docker compose up -d --build

# 4. Run migrations
docker compose exec -T web python manage.py migrate --noinput

# 5. Collect static files
docker compose exec -T web python manage.py collectstatic --noinput
```

### ปัญหาของ Manual Deploy

| ปัญหา | อธิบาย |
|--------|--------|
| **น่าเบื่อ** | ทำซ้ำเหมือนเดิมทุกครั้ง 😴 |
| **ลืมได้** | ลืม migrate? ลืม collectstatic? → เว็บพัง |
| **ช้า** | ต้อง SSH เข้าไปทำเอง →  5-10 นาทีต่อครั้ง |
| **ต้องมี SSH access** | ถ้าอยู่ข้างนอกไม่มี key = deploy ไม่ได้ |
| **ไม่มี audit trail** | ใครทำอะไรเมื่อไหร่? ไม่รู้ |

### Solution: CI/CD

**CI** = **C**ontinuous **I**ntegration — รัน test อัตโนมัติเมื่อมี code ใหม่
**CD** = **C**ontinuous **D**eployment — deploy อัตโนมัติเมื่อ test ผ่าน

```
Developer                    GitHub                         Server
┌──────────┐   git push     ┌─────────────┐   SSH          ┌──────────┐
│  แก้ code │ ────────────► │   GitHub     │ ────────────► │  Deploy  │
│  แล้ว push│               │   Actions    │  auto deploy  │  อัตโนมัติ │
└──────────┘               │ (run tests)  │               └──────────┘
                           └─────────────┘

      ← ทุกอย่างอัตโนมัติ ไม่ต้อง SSH เอง! →
```

ใชีวิตของ developer เปลี่ยนจาก:
1. แก้ code
2. `git push`
3. **จบ!** — GitHub Actions ทำส่วนที่เหลือให้

---

## 2. GitHub Actions Overview

**GitHub Actions** คือบริการ CI/CD ที่มาพร้อม GitHub:

| คุณสมบัติ | รายละเอียด |
|-----------|----------|
| **ราคา** | ฟรี สำหรับ public repos, มี free tier สำหรับ private |
| **ตั้งค่า** | เขียน YAML file ใน `.github/workflows/` |
| **Trigger** | push, pull request, schedule, หรือ manual |
| **รันที่ไหน** | บน GitHub's servers (Ubuntu, macOS, Windows) |

### โครงสร้างของ Workflow

```
Workflow (.yml file)
  └── Job (deploy)
        └── Steps
              ├── Step 1: เชื่อมต่อ SSH
              ├── Step 2: git pull
              ├── Step 3: docker compose up
              └── Step 4: migrate
```

- **Workflow** = ไฟล์ YAML ที่กำหนดว่าจะทำอะไร
- **Job** = กลุ่มของ steps ที่รันบนเครื่องเดียวกัน
- **Step** = คำสั่ง/action แต่ละอัน

---

## 3. Walk Through deploy.yml

เปิดไฟล์ `.github/workflows/deploy.yml`:

```yaml
# =============================================================================
# GitHub Actions — Deploy to Server
# =============================================================================
# This workflow:
# 1. Runs on push to 'main' branch
# 2. SSHs into your server
# 3. Pulls latest code
# 4. Rebuilds and restarts Docker containers
#
# Required GitHub Secrets:
#   SERVER_HOST     — Your server IP address
#   SERVER_USER     — SSH username (e.g., ubuntu)
#   SERVER_SSH_KEY  — Private SSH key for authentication
# =============================================================================

name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: Deploy to Server
    runs-on: ubuntu-latest

    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            # Navigate to project directory
            cd /home/${{ secrets.SERVER_USER }}/django-postgresql-nginx-docker/sample

            # Pull latest code
            git pull origin main

            # Rebuild and restart containers
            docker compose up -d --build

            # Run migrations
            docker compose exec -T web python manage.py migrate --noinput

            # Collect static files
            docker compose exec -T web python manage.py collectstatic --noinput

            # Show running containers
            docker compose ps
```

### อธิบายทีละส่วน:

#### `name: Deploy`

```yaml
name: Deploy
```

> ชื่อ workflow ที่จะแสดงใน GitHub Actions tab

#### `on: push: branches: [main]`

```yaml
on:
  push:
    branches: [main]
```

> **Trigger**: workflow นี้จะรัน **เมื่อมี push ไปที่ branch `main`**
> push ไป branch อื่น = ไม่รัน (ปลอดภัย!)

#### `jobs: deploy:`

```yaml
jobs:
  deploy:
    name: Deploy to Server
    runs-on: ubuntu-latest
```

> `runs-on: ubuntu-latest` = GitHub จะใช้ Ubuntu VM ในการรัน job นี้
> VM นี้ไม่ใช่ server ของเรา — เป็น VM ชั่วคราวของ GitHub

#### `steps: - uses: appleboy/ssh-action@v1`

```yaml
steps:
  - name: Deploy via SSH
    uses: appleboy/ssh-action@v1
    with:
      host: ${{ secrets.SERVER_HOST }}
      username: ${{ secrets.SERVER_USER }}
      key: ${{ secrets.SERVER_SSH_KEY }}
```

- `uses: appleboy/ssh-action@v1` = ใช้ **Action สำเร็จรูป** ที่ช่วย SSH ไปยัง server
- `${{ secrets.SERVER_HOST }}` = อ่านค่าจาก **GitHub Secrets** (ค่าลับที่ไม่โชว์ใน code)

#### `script: |`

```yaml
script: |
  cd /home/${{ secrets.SERVER_USER }}/django-postgresql-nginx-docker/sample
  git pull origin main
  docker compose up -d --build
  docker compose exec -T web python manage.py migrate --noinput
  docker compose exec -T web python manage.py collectstatic --noinput
  docker compose ps
```

> คำสั่งที่จะรันบน **server ของเรา** ผ่าน SSH — เหมือนที่เราพิมพ์เองทุกครั้ง แต่ตอนนี้ **อัตโนมัติ!**

📝 **Note**: `-T` ใน `docker compose exec -T` = ปิด pseudo-TTY — จำเป็นเมื่อรัน exec ผ่าน script (ไม่มี terminal จริง)

---

## 4. ตั้งค่า GitHub Secrets

### ทำไมต้อง Secrets?

เราต้องส่ง server IP, username, SSH key ให้ GitHub Actions — แต่ **ห้ามเขียนใน code!**

**GitHub Secrets** = ที่เก็บค่าลับที่:
- เข้ารหัส (encrypted) ✅
- ไม่โชว์ใน logs ✅
- ไม่อยู่ใน code ✅

### Step-by-Step

#### Step 1: สร้าง SSH Key สำหรับ CI/CD

บน server ของคุณ:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions
```

> สร้าง key pair ใหม่เฉพาะสำหรับ CI/CD — แยกจาก key ที่ใช้เอง

```bash
# เพิ่ม public key เข้า authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
```

> อนุญาตให้ key นี้ SSH เข้า server ได้

```bash
# copy private key (เพื่อเอาไปใส่ GitHub Secret)
cat ~/.ssh/github_actions
```

**Copy ทั้งหมดตั้งแต่** `-----BEGIN OPENSSH PRIVATE KEY-----` **ถึง** `-----END OPENSSH PRIVATE KEY-----`

#### Step 2: เพิ่ม Secrets ใน GitHub

1. ไปที่ GitHub repository ของคุณ
2. กด **Settings** (tab ด้านบน)
3. กด **Secrets and variables** → **Actions** (เมนูด้านซ้าย)
4. กด **New repository secret**

เพิ่ม 3 secrets:

| Secret Name | Value | ตัวอย่าง |
|-------------|-------|---------|
| `SERVER_HOST` | IP ของ server | `203.0.113.50` |
| `SERVER_USER` | SSH username | `ubuntu` หรือ `your-name` |
| `SERVER_SSH_KEY` | Private key ทั้งหมด | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

⚠️ **สำคัญมาก**: `SERVER_SSH_KEY` ต้อง copy **ทั้ง private key** รวมบรรทัด `BEGIN` และ `END` ด้วย!

---

## 5. ทดสอบ Pipeline

### ลองส่ง Deploy ครั้งแรก!

#### Step 1: แก้ code เล็กน้อย

ลองแก้ไฟล์อะไรสักอย่าง เช่น เพิ่ม comment ใน `views.py`:

```bash
# บนเครื่อง dev ของคุณ (ไม่ใช่ server)
cd django-postgresql-nginx-docker/sample/app/notes/views.py
```

เพิ่ม comment:

```python
class NoteViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Notes.
    Deployed automatically via GitHub Actions! 🚀
    ...
    """
```

#### Step 2: Push

```bash
git add .
git commit -m "test: auto deploy via github actions"
git push origin main
```

#### Step 3: ดู Actions Tab

1. เปิด GitHub repository ในbrowser
2. กด Tab **Actions**
3. จะเห็น workflow "Deploy" กำลังรัน (สัญลักษณ์ 🟡 หมุน)
4. รอ... (ปกติ 1-3 นาที)
5. ✅ สำเร็จ = เครื่องหมาย ✅ สีเขียว
6. ❌ ล้มเหลว = เครื่องหมาย ❌ สีแดง

#### Step 4: กดเข้าไปดู Log

กดที่ workflow run → กดที่ job "Deploy to Server" → ดู log ทีละ step

**Log ที่ควรเห็น:**
```
Run appleboy/ssh-action@v1
======CMD======
cd /home/ubuntu/django-postgresql-nginx-docker/sample
git pull origin main
docker compose up -d --build
docker compose exec -T web python manage.py migrate --noinput
docker compose exec -T web python manage.py collectstatic --noinput
docker compose ps
======END======
...
out: Already up to date.  (ถ้าไม่มี code change)
out: [+] Running 3/3
out:  ✔ Container sample-db-1     Running
out:  ✔ Container sample-web-1    Running
out:  ✔ Container sample-nginx-1  Running
```

🎉 **ยินดีด้วย! คุณเพิ่ง deploy อัตโนมัติครั้งแรก!**

ตั้งแต่นี้ ทุกครั้งที่ push code ไป `main` → เว็บจะอัพเดทอัตโนมัติ!

---

## 6. เพิ่ม Testing (Optional)

ถ้าอยากเพิ่ม **รัน test ก่อน deploy** (CI ตัว "I"):

```yaml
name: Test & Deploy

on:
  push:
    branches: [main]

jobs:
  # ==========================================================================
  # Job 1: Run Tests
  # ==========================================================================
  test:
    name: Run Tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd sample/app
          pip install -r requirements.txt

      - name: Run tests
        env:
          DB_HOST: localhost
          DB_NAME: testdb
          DB_USER: postgres
          DB_PASSWORD: postgres
          DB_PORT: 5432
          SECRET_KEY: test-secret-key
          DEBUG: True
        run: |
          cd sample/app
          python manage.py test

  # ==========================================================================
  # Job 2: Deploy (only if tests pass)
  # ==========================================================================
  deploy:
    name: Deploy to Server
    runs-on: ubuntu-latest
    needs: test    # ← deploy ต่อเมื่อ test ผ่านเท่านั้น!

    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /home/${{ secrets.SERVER_USER }}/django-postgresql-nginx-docker/sample
            git pull origin main
            docker compose up -d --build
            docker compose exec -T web python manage.py migrate --noinput
            docker compose exec -T web python manage.py collectstatic --noinput
            docker compose ps
```

Key addition:
- `needs: test` = deploy job จะ **รอ test job ผ่านก่อน**
- ถ้า test fail → deploy ไม่รัน → production ปลอดภัย! ✅

```
Push code → Run Tests → ✅ Pass → Deploy
                       → ❌ Fail → หยุด! (ไม่ deploy)
```

---

## 🤖 เมื่อติดปัญหา — ลองใช้ AI ช่วย Debug

ถ้า GitHub Actions ล้มเหลว ลอง copy log แล้วใช้ prompt นี้:

```
ฉันกำลังเรียนรู้เรื่อง GitHub Actions CI/CD สำหรับ Django deployment
Workflow ของฉัน (.github/workflows/deploy.yml) มีหน้าตาแบบนี้:
[วาง content ของ deploy.yml]

เมื่อ push code แล้ว Actions ล้มเหลว, error log คือ:
[วาง error log จาก Actions tab]

ช่วยอธิบายว่า:
1. Error นี้หมายความว่าอะไร?
2. สาเหตุน่าจะเป็นอะไร?
3. ฉันควรตรวจสอบอะไรบ้าง? (อย่าบอกคำตอบตรงๆ แต่ช่วย guide ให้ฉันหาคำตอบเอง)
```

💡 **Tip**: วิธีอ่าน GitHub Actions logs:
- ✅ Green checkmark = step นั้นผ่าน
- ❌ Red X = step นั้นล้มเหลว
- กดเข้าไปที่ step ที่ fail → expand log
- error มักจะอยู่ **บรรทัดท้ายๆ** ของ log

---

## 📋 สรุป

ใน Part นี้เราได้ตั้งค่า CI/CD:

| หัวข้อ | สิ่งที่เรียนรู้ |
|--------|---------------|
| **CI/CD คืออะไร** | CI = test อัตโนมัติ, CD = deploy อัตโนมัติ |
| **GitHub Actions** | Workflow (YAML) → Job → Steps → Action |
| **deploy.yml** | push to main → SSH to server → git pull → compose up → migrate |
| **GitHub Secrets** | เก็บ SERVER_HOST, SERVER_USER, SERVER_SSH_KEY อย่างปลอดภัย |
| **Testing** | (Optional) รัน test ก่อน deploy — ถ้า fail ไม่ deploy |

**ชีวิตใหม่ของ developer:**

```
1. แก้ code
2. git push
3. ☕ ไปชงกาแฟ
4. กลับมาเว็บอัพเดทแล้ว! 🎉
```

---

## 🧪 ลองทำ

1. **ทดสอบ Deploy**: แก้ไฟล์เล็กน้อย (เช่น เปลี่ยน comment) → push → ดู Actions tab → เว็บอัพเดทไหม?

2. **ทดสอบ Failure**: ลองใส่ syntax error ใน settings.py → push → ดูว่า Actions fail ยังไง → อ่าน log → แก้ → push อีกรอบ

3. **ดู Actions History**: ไปที่ Actions tab → ดู workflow runs ทั้งหมด — เหมือน history ของทุก deployment

4. **ตอบคำถาม**: ถ้าเรา push ไป branch `feature/new-api` จะ trigger deploy ไหม? ทำไม? (Hint: ดูที่ `on: push: branches:`)

---

[← Part 7: Production Readiness](part-7-production-readiness.md) | [Part 9: สรุป →](part-9-recap.md)
