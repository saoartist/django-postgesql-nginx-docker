# 🚀 Django + PostgreSQL + Nginx + Docker Deployment Tutorial

คู่มือสำหรับ Junior Developer ที่ต้องการเรียนรู้การ Deploy เว็บแอปพลิเคชัน Django ขึ้น Production Server

## 🎯 เหมาะสำหรับใคร?

นักพัฒนาที่เขียน Django, PostgreSQL, HTML, CSS, Vue/Nuxt ได้แล้ว แต่ยังไม่เคยใช้ Linux และยังไม่เคย Deploy Web Server

## 📋 สิ่งที่จะได้เรียนรู้

เมื่อเรียนจบ คุณจะสามารถ:
- ใช้งาน Linux Command Line พื้นฐานได้
- เข้าใจ Docker, Container, Image, Volume, Network
- สร้าง Dockerfile และ docker-compose.yml
- Deploy Django + PostgreSQL + Nginx ด้วย Docker Compose
- ตั้งค่า HTTPS ด้วย Let's Encrypt
- สร้าง CI/CD Pipeline ด้วย GitHub Actions

## 🏗️ Architecture Overview

```
User Request
    │
    ▼
┌─────────┐     ┌──────────────┐     ┌──────────────┐
│  Nginx  │────▶│    Django     │────▶│  PostgreSQL  │
│ (Port 80│     │  (Gunicorn)  │     │  (Port 5432) │
│  / 443) │     │  (Port 8000) │     │              │
└─────────┘     └──────────────┘     └──────────────┘
     │
     └── Static Files (CSS, JS, Images)

ทั้งหมดทำงานอยู่ใน Docker Containers บน Ubuntu Server
```

## 📚 สารบัญ

| Part | หัวข้อ | เวลาโดยประมาณ |
|------|--------|---------------|
| [Part 0](docs/part-0-big-picture.md) | ภาพรวม — เราจะสร้างอะไร? | 30 นาที |
| [Part 1](docs/part-1-setup-environment.md) | เตรียมเครื่องมือ — Setup Environment | 1-2 ชม. |
| [Part 2](docs/part-2-understanding-django-project.md) | ทำความเข้าใจ Django Project | 30 นาที |
| [Part 3](docs/part-3-git-and-server.md) | Git & เอาโค้ดขึ้น Server | 1 ชม. |
| [Part 4](docs/part-4-docker-fundamentals.md) | Docker Fundamentals | 2-3 ชม. |
| [Part 5](docs/part-5-docker-compose.md) | Docker Compose — จัดการหลาย Container | 2 ชม. |
| [Part 6](docs/part-6-nginx.md) | Nginx — Reverse Proxy | 2 ชม. |
| [Part 7](docs/part-7-production-readiness.md) | Production Readiness — Domain, HTTPS, Security | 1-2 ชม. |
| [Part 8](docs/part-8-cicd.md) | CI/CD — Auto Deploy ด้วย GitHub Actions | 2 ชม. |
| [Part 9](docs/part-9-recap.md) | สรุปและก้าวต่อไป | 30 นาที |

## 🗂️ โครงสร้าง Repo

```
.
├── README.md                          # หน้านี้
├── docs/                              # เนื้อหาแต่ละ Part
│   ├── part-0-big-picture.md
│   ├── part-1-setup-environment.md
│   ├── part-2-understanding-django-project.md
│   ├── part-3-git-and-server.md
│   ├── part-4-docker-fundamentals.md
│   ├── part-5-docker-compose.md
│   ├── part-6-nginx.md
│   ├── part-7-production-readiness.md
│   ├── part-8-cicd.md
│   └── part-9-recap.md
├── sample/                            # ตัวอย่าง Django Project
│   ├── app/                           # Django + Gunicorn
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── manage.py
│   │   ├── config/                    # Django settings
│   │   └── notes/                     # Simple Notes API app
│   ├── nginx/                         # Nginx config
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── .env.example
└── .github/
    └── workflows/
        └── deploy.yml
```

## 🏃 Quick Start

```bash
# Clone repo
git clone https://github.com/your-username/django-postgresql-nginx-docker.git
cd django-postgresql-nginx-docker/sample

# Copy environment file
cp .env.example .env

# Build and run
docker compose up -d --build

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# เปิดเบราว์เซอร์ไปที่ http://localhost
```

## 📝 Exercise สำหรับนักเรียน

หลังจากเรียนจบทั้ง 9 Part, ลองทำ Exercise นี้:
- **Deploy Nuxt/Vue Frontend** ผ่าน Nginx เพิ่มเติมจาก Django Backend

## 📄 License

MIT
