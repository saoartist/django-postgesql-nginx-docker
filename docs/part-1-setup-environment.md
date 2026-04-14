# Part 1: เตรียมเครื่องมือ — Setup Environment

> ⏱️ เวลาโดยประมาณ: 1-2 ชั่วโมง

## 🎯 สิ่งที่จะได้เรียนรู้ใน Part นี้

- เข้าใจว่าทำไม Server ถึงใช้ Linux
- เลือกและตั้งค่า Linux Environment
- ใช้ Linux Command พื้นฐานได้อย่างมั่นใจ
- ติดตั้ง Git, Docker, Docker Compose

---

## 1. ทำไมต้อง Linux?

ก่อนจะ deploy อะไร เราต้องเข้าใจก่อนว่า server ส่วนใหญ่ในโลกนี้ **ไม่ได้รัน Windows หรือ macOS** — แต่รัน **Linux**

### ประวัติสั้นๆ

Linux ถูกสร้างโดย **Linus Torvalds** ในปี 1991 เป็น open-source operating system ที่ใครก็สามารถใช้ได้ฟรี

### ทำไม Server ถึงใช้ Linux?

| เหตุผล | อธิบาย |
|--------|--------|
| **ฟรี** | ไม่ต้องจ่ายค่า license เหมือน Windows Server |
| **เสถียร** | รันได้เป็นปีๆ โดยไม่ต้อง restart |
| **เบา** | ใช้ RAM น้อย — ไม่มี GUI ไม่จำเป็น |
| **ปลอดภัย** | ออกแบบมาให้ปลอดภัย, มี permission system ที่ดี |
| **Cloud ใช้** | AWS, GCP, DigitalOcean — VM เกือบทั้งหมดคือ Linux |

**Ubuntu** คือ Linux distribution ที่ได้รับความนิยมสูงมาก — ใช้ง่าย, มี community ใหญ่, มี documentation เยอะ เราจะใช้ **Ubuntu 24.04** ในบทเรียนนี้

---

## 2. เลือก Environment

เราต้องมี Linux environment สำหรับทำงาน เลือกได้ 3 วิธี:

### Option A: WSL2 on Windows (แนะนำสำหรับ Windows users) ⭐

WSL2 (Windows Subsystem for Linux) ให้เรารัน Linux ใน Windows ได้โดยตรง — ไม่ต้องติดตั้ง Virtual Machine แยก

**Step 1**: เปิด PowerShell แบบ Administrator แล้วพิมพ์:

```powershell
wsl --install -d Ubuntu-24.04
```

📝 **Note**: คำสั่งนี้จะ download และติดตั้ง Ubuntu 24.04 — อาจใช้เวลาสักครู่

**แสดงผลที่คาดว่าจะเห็น:**
```
Installing: Ubuntu 24.04 LTS
Ubuntu 24.04 LTS has been installed.
Launching Ubuntu 24.04 LTS...
```

**Step 2**: ระบบจะถามให้ตั้ง username และ password

```
Enter new UNIX username: your-name
New password: ********
Retype new password: ********
```

⚠️ **ตอนพิมพ์ password จะไม่เห็นอะไรบนหน้าจอ** — นี่คือ behavior ปกติของ Linux ไม่ใช่ bug! แค่พิมพ์ไปแล้วกด Enter

**Step 3**: เมื่อเข้า Ubuntu terminal แล้ว ให้ update ระบบ:

```bash
sudo apt update && sudo apt upgrade -y
```

> `sudo` = **S**uper **U**ser **Do** — รัน command ด้วยสิทธิ์ admin
> `apt` = package manager ของ Ubuntu — เหมือน `pip` ของ Python
> `&&` = รัน command ถัดไปถ้า command แรกสำเร็จ
> `-y` = ตอบ yes อัตโนมัติ ไม่ต้องกดยืนยัน

### Option B: Cloud VM (สำหรับคนที่มี Cloud account)

นี่คือวิธีที่ใกล้กับ production จริงมากที่สุด — เรามี server อยู่บน cloud จริงๆ

**Step 1**: สร้าง VM (Virtual Machine) บน cloud provider ที่คุณเลือก:
- Google Cloud, DigitalOcean, AWS, Linode, Vultr — ใช้ได้ทุกเจ้า
- เลือก **Ubuntu 24.04** เป็น OS
- ขนาดเล็กสุดพอ: 1-2 vCPU, 1-2 GB RAM
- เปิด ports: **22** (SSH), **80** (HTTP), **443** (HTTPS)

**Step 2**: เชื่อมต่อ SSH:

```bash
ssh username@your-server-ip
```

> `ssh` = Secure Shell — วิธีเชื่อมต่อไปยัง server ระยะไกลแบบปลอดภัย
> `username` = ชื่อ user ที่ได้จาก cloud provider
> `your-server-ip` = IP address ของ VM เช่น `203.0.113.50`

**แสดงผลที่คาดว่าจะเห็น (ครั้งแรก):**
```
The authenticity of host '203.0.113.50' can't be established.
ED25519 key fingerprint is SHA256:xxxxx.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

พิมพ์ `yes` แล้วกด Enter — นี่คือการยืนยันว่าเราเชื่อ server นี้

### Option C: VirtualBox (ทางเลือก)

ถ้าไม่ได้ใช้ Windows หรือไม่มี cloud account — สามารถติดตั้ง [VirtualBox](https://www.virtualbox.org/) แล้วสร้าง Ubuntu VM ได้ แต่จะหนักกว่า Option A มาก

---

## 3. Linux Command Line พื้นฐาน

เรามาเรียนรู้ command พื้นฐานกัน — แต่ไม่ใช่แบบท่องจำ! เราจะเรียนผ่านการ **ทำ task จริง**

### 🔍 Task 1: สำรวจ Server — "ตอนนี้ฉันอยู่ไหน? มีอะไรอยู่ตรงนี้?"

```bash
pwd
```

> `pwd` = **P**rint **W**orking **D**irectory — แสดง path ที่เราอยู่ตอนนี้

**แสดงผล:**
```
/home/your-name
```

นี่คือ **Home Directory** ของเรา — เหมือน "ห้องของเรา" บน server

```bash
ls
```

> `ls` = **L**i**s**t — แสดงไฟล์และโฟลเดอร์ที่อยู่ใน directory ปัจจุบัน

**แสดงผล (ถ้าเพิ่งสร้างใหม่อาจไม่มีอะไร):**
```
(ว่างเปล่า หรือมีไฟล์เริ่มต้นบางอย่าง)
```

ลอง `ls` แบบ detail:

```bash
ls -la
```

> `-l` = แสดงแบบ long format (permission, owner, size, date)
> `-a` = แสดงไฟล์ที่ซ่อนด้วย (ไฟล์ที่ขึ้นต้นด้วย `.`)

**แสดงผล:**
```
total 20
drwxr-xr-x 3 your-name your-name 4096 Jan  1 00:00 .
drwxr-xr-x 3 root      root      4096 Jan  1 00:00 ..
-rw-r--r-- 1 your-name your-name  220 Jan  1 00:00 .bash_logout
-rw-r--r-- 1 your-name your-name 3771 Jan  1 00:00 .bashrc
-rw-r--r-- 1 your-name your-name  807 Jan  1 00:00 .profile
```

ลองย้ายไปที่อื่น:

```bash
cd /home
```

> `cd` = **C**hange **D**irectory — ย้ายไปที่ path ที่ระบุ

```bash
pwd    # จะแสดง /home
ls     # จะเห็นชื่อ user ต่างๆ
```

กลับบ้าน:

```bash
cd ~
```

> `~` = shortcut สำหรับ home directory ของเรา (`/home/your-name`)

ย้อนกลับ 1 ระดับ:

```bash
cd ..
```

> `..` = directory ระดับบน (parent directory)

### 📁 Task 2: สร้างโฟลเดอร์โปรเจค

```bash
mkdir -p projects/my-app
```

> `mkdir` = **M**a**k**e **Dir**ectory — สร้างโฟลเดอร์
> `-p` = สร้าง parent directories ด้วย (ถ้ายังไม่มี) — ในที่นี้สร้างทั้ง `projects` และ `my-app` ข้างใน

```bash
cd projects/my-app
pwd
```

**แสดงผล:**
```
/home/your-name/projects/my-app
```

สร้างไฟล์เปล่า:

```bash
touch test.txt
```

> `touch` = สร้างไฟล์เปล่า (หรือ update timestamp ถ้าไฟล์มีอยู่แล้ว)

แก้ไขไฟล์ด้วย `nano` (text editor ง่ายที่สุดบน Linux):

```bash
nano test.txt
```

> พิมพ์ข้อความอะไรก็ได้ แล้วกด `Ctrl+X` → `Y` → `Enter` เพื่อบันทึกและออก

อ่านไฟล์:

```bash
cat test.txt
```

> `cat` = con**cat**enate — แสดงเนื้อหาของไฟล์

คำสั่งจัดการไฟล์เพิ่มเติม:

```bash
cp test.txt test_backup.txt   # คัดลอกไฟล์
mv test_backup.txt backup.txt  # เปลี่ยนชื่อ (หรือย้าย)
rm backup.txt                  # ลบไฟล์
rm -rf some-folder/            # ลบโฟลเดอร์และทุกอย่างข้างใน
```

> ⚠️ `rm -rf` ลบแบบไม่ถามยืนยัน และ **กู้คืนไม่ได้!** — ใช้ด้วยความระวัง

### 📦 Task 3: ติดตั้งโปรแกรม

```bash
sudo apt update
```

> อัพเดท package list — บอก Ubuntu ว่ามี software version ใหม่อะไรบ้าง (ยังไม่ติดตั้งอะไร)

```bash
sudo apt install -y tree
```

> ติดตั้ง `tree` — เครื่องมือแสดงโครงสร้างโฟลเดอร์แบบสวยงาม

```bash
cd ~/projects
tree
```

**แสดงผล:**
```
.
└── my-app
    └── test.txt

1 directory, 1 file
```

### 👁️ Task 4: ดู Process ที่กำลังทำงาน

```bash
ps aux
```

> แสดง process ทั้งหมดที่กำลังทำงาน — ยาวมาก! ลองใช้ `ps aux | head` ดูแค่ 10 บรรทัดแรก

> `|` (pipe) = ส่ง output ของ command แรกไปเป็น input ของ command ถัดไป
> `head` = แสดงแค่ส่วนหัวของ output

```bash
top
```

> แสดง process แบบ real-time — เหมือน Task Manager ของ Windows
> กด `q` เพื่อออก

💡 **Tip**: `Ctrl+C` = หยุด process ที่กำลังรัน — จำไว้ให้ดี จะใช้บ่อยมาก!

---

## 4. ติดตั้ง Git

Git เป็นเครื่องมือ version control ที่เราจะใช้ดึงโค้ดจาก GitHub มาที่ server

```bash
sudo apt install -y git
```

> ติดตั้ง git ผ่าน package manager ของ Ubuntu

ตรวจสอบว่าติดตั้งสำเร็จ:

```bash
git --version
```

**แสดงผลที่คาดว่าจะเห็น:**
```
git version 2.43.0
```

> version อาจต่างกันเล็กน้อย — ไม่เป็นไร ขอแค่แสดง version number ก็ถือว่า OK

ตั้งค่า Git:

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

> `--global` = ตั้งค่าสำหรับ user นี้ทุก project
> ชื่อและ email นี้จะปรากฏใน commit ของเรา

✅ **ตรวจสอบ:** `git config --list` จะแสดงค่าที่เราตั้งไว้

---

## 5. ติดตั้ง Docker & Docker Compose

Docker คือหัวใจหลักของบทเรียนนี้ — เราจะเรียนรู้แบบลึกใน Part 4 แต่ตอนนี้มาติดตั้งกันก่อน

### Step 1: ลบ Docker version เก่า (ถ้ามี)

```bash
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null
```

> `2>/dev/null` = ซ่อน error message ถ้าไม่มี package เหล่านี้ (ไม่ต้องสนใจ warning)

### Step 2: ติดตั้ง package ที่จำเป็น

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
```

> เหล่านี้คือ tools พื้นฐานที่ Docker ต้องใช้ เช่น `curl` (download จาก internet), `ca-certificates` (ตรวจสอบ HTTPS)

### Step 3: เพิ่ม Docker's official GPG key

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

> GPG key = ลายเซ็นดิจิทัลเพื่อยืนยันว่า package มาจาก Docker จริงๆ — เรื่อง security

### Step 4: เพิ่ม Docker repository

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

> บอก Ubuntu ว่าให้หา Docker package จาก Docker's official repository (ไม่ใช่ Ubuntu default ที่อาจ outdated)

### Step 5: ติดตั้ง Docker

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

> `docker-ce` = Docker Community Edition (ตัวหลัก)
> `docker-compose-plugin` = Docker Compose V2 (สำหรับ `docker compose` command)

### Step 6: เพิ่ม user เข้า docker group

```bash
sudo usermod -aG docker $USER
```

> โดยปกติ Docker ต้องใช้ `sudo` ทุกครั้ง — คำสั่งนี้เพิ่ม user ของเราเข้า docker group เพื่อไม่ต้องพิมพ์ `sudo` ก่อนทุก docker command

⚠️ **สำคัญ! ต้อง logout แล้ว login ใหม่** เพื่อให้ group membership มีผล:

```bash
# ถ้าใช้ SSH:
exit
ssh username@your-server-ip

# ถ้าใช้ WSL:
# ปิด terminal แล้วเปิดใหม่
```

### Step 7: ตรวจสอบ

```bash
docker --version
```

**แสดงผลที่คาดว่าจะเห็น:**
```
Docker version 27.x.x, build xxxxxxx
```

```bash
docker compose version
```

**แสดงผลที่คาดว่าจะเห็น:**
```
Docker Compose version v2.x.x
```

### Step 8: ทดสอบ

```bash
docker run hello-world
```

> คำสั่งนี้จะ download image `hello-world` จาก Docker Hub แล้วรันเป็น container

**แสดงผลที่คาดว่าจะเห็น:**
```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
...
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

🎉 ถ้าเห็นข้อความ "Hello from Docker!" แสดงว่า Docker ทำงานได้ถูกต้องแล้ว!

---

## ✅ Verification Checklist

ก่อนไปต่อ Part 2 ตรวจสอบว่าทุกอย่างพร้อม:

- [ ] `git --version` — แสดง version number
- [ ] `docker --version` — แสดง version number
- [ ] `docker compose version` — แสดง version number
- [ ] `docker run hello-world` — แสดง "Hello from Docker!"

ถ้าทุกอย่างผ่าน ✅ — คุณพร้อมแล้ว!

---

## 🤖 เมื่อติดปัญหา — ลองใช้ AI ช่วย Debug

ถ้า setup ไม่ผ่าน หรือเจอ error ลอง copy error message แล้วใช้ prompt นี้ถาม AI:

```
ฉันกำลังเรียนรู้เรื่อง Linux server setup และ Docker installation
ฉันใช้ Ubuntu 24.04 บน [WSL2 / Cloud VM / VirtualBox]
ฉันทำตาม step [อธิบายสิ่งที่ทำ]
แล้วเจอ error นี้:

[วาง error message ที่เห็น]

ช่วยอธิบายว่า:
1. Error นี้หมายความว่าอะไร?
2. สาเหตุน่าจะเป็นอะไร?
3. ฉันควรตรวจสอบอะไรบ้าง? (อย่าบอกคำตอบตรงๆ แต่ช่วย guide ให้ฉันหาคำตอบเอง)
```

💡 **Tip**: error ที่พบบ่อยสุดในขั้นตอนนี้:
- `"Permission denied"` ตอนรัน docker → มักเกิดจากลืม logout/login ใหม่หลัง `usermod`
- `"command not found"` → ติดตั้งไม่ครบ ลอง copy error message ไปถาม AI

---

## 📋 สรุป

ใน Part นี้เราได้:

| สิ่งที่ทำ | ทำไม |
|----------|------|
| ติดตั้ง Linux environment | Server ใช้ Linux — เราต้องคุ้นเคยกับมัน |
| เรียนรู้ Linux commands | เพื่อจัดการไฟล์, ติดตั้งโปรแกรม, ดู process บน server |
| ติดตั้ง Git | เพื่อดึงโค้ดจาก GitHub มาที่ server |
| ติดตั้ง Docker & Docker Compose | เครื่องมือหลักในการ deploy — จะเรียนลึกใน Part 4 |

---

## 🧪 ลองทำ

1. **สำรวจ server**: ลอง `cd` ไปที่ `/var`, `/etc`, `/usr` — ดูว่ามีอะไรอยู่บ้าง ใช้ `ls` และ `tree -L 1` เพื่อดูภาพรวม
2. **ติดตั้ง htop**: รัน `sudo apt install -y htop` แล้วลองใช้ `htop` ดู — มันดีกว่า `top` ตรงไหน?
3. **ทดลอง Docker**: รัน `docker run -it ubuntu:24.04 bash` — คุณจะเข้าไปอยู่ "ข้างใน" Ubuntu container! ลอง `cat /etc/os-release` แล้วพิมพ์ `exit` เพื่อออก

---

[← Part 0: ภาพรวม](part-0-big-picture.md) | [Part 2: ทำความเข้าใจ Django Project →](part-2-understanding-django-project.md)
