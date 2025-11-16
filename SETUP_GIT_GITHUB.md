# 📦 SETUP GIT & GITHUB - BACKUP & DEPLOY

## 🎯 LỢI ÍCH

✅ **Backup tự động** - Code được lưu trên GitHub  
✅ **Version control** - Theo dõi thay đổi  
✅ **Deploy nhanh** - Chỉ cần 1 lệnh `git clone`  
✅ **Collaboration** - Dễ dàng làm việc nhóm  
✅ **Rollback** - Dễ dàng quay lại version cũ  

---

## 🚀 BƯỚC 1: TẠO GIT REPOSITORY

### **Trên máy local (Windows):**

#### **1.1. Install Git (nếu chưa có):**

Download từ: https://git-scm.com/download/win

#### **1.2. Configure Git:**

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### **1.3. Initialize repository:**

```bash
# Navigate đến thư mục project
cd "C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet"

# Initialize Git
git init

# Add tất cả files
git add .

# Commit lần đầu
git commit -m "Initial commit: Facebook Ads Automation System"
```

---

## 📝 BƯỚC 2: TẠO .GITIGNORE

### **Tạo file `.gitignore` trong thư mục project:**

```bash
# Tạo file .gitignore
notepad .gitignore
```

**Nội dung:**

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Google Apps Script (nếu không cần)
*.gs
*.html

# Temporary files
*.tmp
*.bak
*.cache

# Secrets
secrets/
*.pem
*.key
```

**Lưu file.**

---

## 🌐 BƯỚC 3: TẠO REPOSITORY TRÊN GITHUB

### **3.1. Tạo GitHub account (nếu chưa có):**

- Truy cập: https://github.com
- Sign up

### **3.2. Tạo repository mới:**

1. Click **"New repository"**
2. **Repository name:** `ads-automation` (hoặc tên khác)
3. **Description:** `Facebook Ads Automation System`
4. **Visibility:** 
   - ✅ **Private** (khuyến nghị - bảo mật hơn)
   - Hoặc **Public** (nếu muốn open source)
5. **KHÔNG** check "Initialize with README"
6. Click **"Create repository"**

### **3.3. Push code lên GitHub:**

```bash
# Thêm remote
git remote add origin https://github.com/YOUR_USERNAME/ads-automation.git

# Push code
git branch -M main
git push -u origin main
```

**Sẽ hỏi username và password/token:**
- Username: GitHub username
- Password: GitHub Personal Access Token (không dùng password)

---

## 🔐 BƯỚC 4: TẠO PERSONAL ACCESS TOKEN

### **Nếu GitHub hỏi password:**

1. Vào GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token"**
3. **Note:** `ads-automation`
4. **Expiration:** Chọn thời hạn
5. **Scopes:** Check `repo`
6. Click **"Generate token"**
7. **Copy token** (chỉ hiện 1 lần)
8. Dùng token này thay cho password khi push

---

## 📥 BƯỚC 5: CLONE VỀ VPS MỚI

### **Trên VPS:**

```bash
# Install Git (nếu chưa có)
sudo apt update
sudo apt install git -y

# Clone repository
cd ~
git clone https://github.com/YOUR_USERNAME/ads-automation.git

# Hoặc clone vào thư mục cụ thể
git clone https://github.com/YOUR_USERNAME/ads-automation.git ~/ads-automation

# Navigate vào thư mục
cd ~/ads-automation

# Verify
ls -la
```

**Kết quả mong đợi:**
```
app/
scripts/
requirements.txt
env.example
.gitignore
README.md (nếu có)
```

---

## ⚙️ BƯỚC 6: SETUP SAU KHI CLONE

### **Trên VPS:**

```bash
cd ~/ads-automation

# Tạo .env từ env.example
cp env.example .env

# Edit .env
nano .env
# Điền các giá trị thực tế

# Tạo venv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py
```

---

## 🔄 BƯỚC 7: UPDATE CODE

### **Trên máy local:**

```bash
# Make changes to files
# ...

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push origin main
```

### **Trên VPS:**

```bash
cd ~/ads-automation

# Pull latest changes
git pull origin main

# Restart services (nếu cần)
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker:*
```

---

## 📋 BƯỚC 8: TẠO README.MD

### **Tạo file `README.md` trong project:**

```markdown
# Facebook Ads Automation System

Hệ thống tự động hóa quảng cáo Facebook với Python + FastAPI.

## Features

- ✅ Automation ads (pause/resume based on rules)
- ✅ Telegram Bot notifications
- ✅ Flexible LogicRules system
- ✅ Job queue for heavy tasks
- ✅ Webhook siêu nhẹ

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- Telegram Bot API
- Facebook Graph API

## Quick Start

1. Clone repository
2. Copy `env.example` to `.env`
3. Configure `.env`
4. Install dependencies: `pip install -r requirements.txt`
5. Initialize database: `python scripts/init_db.py`
6. Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Documentation

- `QUICK_START_PYTHON.md` - Quick start guide
- `SETUP_LIGHTSAIL_SERVER.md` - Server setup
- `LOGICRULES_FLEXIBLE_SOLUTION.md` - LogicRules system

## License

Private
```

---

## 🔒 BẢO MẬT

### **KHÔNG commit:**

- ❌ `.env` file
- ❌ SSH keys (`.pem`)
- ❌ Database passwords
- ❌ API tokens

### **Đã có trong .gitignore:**

- ✅ `.env`
- ✅ `venv/`
- ✅ `__pycache__/`
- ✅ `*.pem`

---

## ✅ CHECKLIST

- [ ] Install Git trên máy local
- [ ] Configure Git (user.name, user.email)
- [ ] Initialize repository: `git init`
- [ ] Tạo `.gitignore`
- [ ] Commit lần đầu: `git commit -m "Initial commit"`
- [ ] Tạo GitHub repository
- [ ] Tạo Personal Access Token
- [ ] Push code: `git push -u origin main`
- [ ] Test clone về VPS: `git clone ...`
- [ ] Tạo README.md

---

## 🎯 LỢI ÍCH SAU KHI SETUP

### **Deploy VPS mới chỉ cần:**

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/ads-automation.git ~/ads-automation

# 2. Setup
cd ~/ads-automation
cp env.example .env
nano .env  # Điền config

# 3. Install
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Initialize
python scripts/init_db.py

# 5. Run
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Chỉ 5 bước! 🚀**

---

**Bây giờ hãy setup Git và push code lên GitHub! 📦**

