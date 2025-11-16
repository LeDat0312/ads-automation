# 🚀 GIT & GITHUB DEPLOYMENT GUIDE

## 🎯 TẠI SAO NÊN DÙNG GIT/GITHUB?

### **✅ LỢI ÍCH:**
- ✅ **Version Control:** Theo dõi thay đổi code
- ✅ **Backup:** Code được lưu trên GitHub (cloud)
- ✅ **Deploy dễ dàng:** Chỉ cần `git clone` trên VPS mới
- ✅ **Collaboration:** Nhiều người có thể làm việc cùng
- ✅ **Rollback:** Có thể quay lại version cũ nếu có lỗi
- ✅ **History:** Xem lịch sử thay đổi
- ✅ **Branching:** Test code mới mà không ảnh hưởng production

---

## 📋 SETUP GIT REPOSITORY

### **BƯỚC 1: TẠO GITHUB REPOSITORY**

1. Vào https://github.com
2. Click "New repository"
3. Repository name: `facebook-ads-automation` (hoặc tên khác)
4. Description: "Facebook Ads Automation System with Python + FastAPI + Telegram Bot"
5. Chọn **Private** (khuyến nghị - bảo mật code)
6. **KHÔNG** chọn "Initialize with README" (sẽ tạo sau)
7. Click "Create repository"

---

### **BƯỚC 2: INITIALIZE GIT TRONG PROJECT**

#### **2.1. Tạo .gitignore file:**

```bash
# Trong thư mục project của bạn
# Tạo file .gitignore
```

**Nội dung file `.gitignore`:**

```
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

# Environment variables
.env
.env.local
.env.*.local

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

# Secrets
secrets/
*.pem
*.key
config.ini

# Test coverage
.coverage
htmlcov/

# Distribution
dist/
build/
*.egg-info/

# Jupyter Notebook
.ipynb_checkpoints

# Google Apps Script (nếu có)
.gs files backup
```

#### **2.2. Initialize Git:**

```bash
# Trong thư mục project
cd /path/to/your/project

# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Facebook Ads Automation System"

# Add remote repository
git remote add origin https://github.com/your-username/facebook-ads-automation.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

### **BƯỚC 3: TẠO README.md**

**File `README.md`:**

```markdown
# 🚀 Facebook Ads Automation System

## 📋 Mô tả

Hệ thống automation quản lý quảng cáo Facebook tương tự Madgicx, sử dụng:
- Python + FastAPI
- PostgreSQL
- Telegram Bot
- Google Sheets (optional)

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Database:** PostgreSQL
- **Bot:** Telegram Bot API
- **Deployment:** AWS Lightsail, Docker

## 🚀 Setup

### Requirements

- Python 3.11+
- PostgreSQL 14+
- Telegram Bot Token
- Facebook Access Token

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/facebook-ads-automation.git
cd facebook-ads-automation

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp env.example .env
nano .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentation

- [Setup Guide](./docs/SETUP.md)
- [API Documentation](./docs/API.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

## 📝 License

MIT License
```

---

## 🚀 DEPLOYMENT WORKFLOW

### **WORKFLOW: Local → GitHub → VPS**

```
Local Development
    ↓
Commit & Push to GitHub
    ↓
Pull on VPS
    ↓
Deploy on VPS
```

---

## 📋 SETUP TRÊN VPS

### **BƯỚC 1: INSTALL GIT**

```bash
# Install Git
sudo apt update
sudo apt install git -y

# Verify
git --version
```

### **BƯỚC 2: CLONE REPOSITORY**

```bash
# Tạo thư mục projects
mkdir -p ~/projects
cd ~/projects

# Clone repository
git clone https://github.com/your-username/facebook-ads-automation.git
cd facebook-ads-automation

# Verify
ls -la
```

### **BƯỚC 3: SETUP ENVIRONMENT**

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (KHÔNG commit vào Git)
cp env.example .env
nano .env
```

### **BƯỚC 4: SETUP DATABASE**

```bash
# Run migrations
alembic upgrade head

# Or create database manually
sudo -u postgres psql
CREATE DATABASE facebook_ads_db;
\q
```

### **BƯỚC 5: DEPLOY**

```bash
# Restart service
sudo systemctl restart facebook-ads-api

# Check status
sudo systemctl status facebook-ads-api

# View logs
sudo journalctl -u facebook-ads-api -f
```

---

## 🔄 UPDATE CODE TRÊN VPS

### **CÁCH 1: Pull từ GitHub (KHUYẾN NGHỊ)**

```bash
# Vào thư mục project
cd ~/projects/facebook-ads-automation

# Pull latest code
git pull origin main

# Restart service
sudo systemctl restart facebook-ads-api

# Check status
sudo systemctl status facebook-ads-api
```

### **CÁCH 2: Automated Deployment (CI/CD)**

**Setup GitHub Actions (optional):**

```yaml
# .github/workflows/deploy.yml
name: Deploy to VPS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd ~/projects/facebook-ads-automation
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart facebook-ads-api
```

---

## 🔒 SECURITY BEST PRACTICES

### **1. KHÔNG COMMIT SECRETS:**

**File `env.example` (commit vào Git - không có dấu chấm):**
```env
# Facebook API
ACCESS_TOKEN=your_access_token_here
AD_ACCOUNT_IDS=act_123456789,act_987654321

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_AUTHORIZED_CHAT_ID=your_authorized_chat_id_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/facebook_ads_db

# API Keys
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```

**File `.env` (KHÔNG commit vào Git - trong .gitignore):**
```env
# Actual secrets (chỉ có trên VPS)
ACCESS_TOKEN=actual_token_here
TELEGRAM_BOT_TOKEN=actual_token_here
DATABASE_URL=postgresql://actual_user:actual_password@localhost:5432/facebook_ads_db
```

### **2. SỬ DỤNG GITHUB SECRETS:**

- Vào GitHub Repository → Settings → Secrets
- Add secrets:
  - `VPS_HOST`: IP của VPS
  - `VPS_USER`: Username trên VPS
  - `VPS_SSH_KEY`: SSH private key

### **3. SỬ DỤNG ENVIRONMENT VARIABLES:**

**File `config.py`:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Facebook API
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
AD_ACCOUNT_IDS = os.getenv('AD_ACCOUNT_IDS', '').split(',')

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
```

---

## 📋 GIT WORKFLOW

### **WORKFLOW HÀNG NGÀY:**

```bash
# 1. Làm việc trên code
# ... edit files ...

# 2. Check status
git status

# 3. Add changes
git add .

# 4. Commit
git commit -m "Add new feature: dashboard overview"

# 5. Push to GitHub
git push origin main

# 6. Pull on VPS
ssh user@vps-ip
cd ~/projects/facebook-ads-automation
git pull origin main
sudo systemctl restart facebook-ads-api
```

### **BRANCHING STRATEGY:**

```bash
# Create feature branch
git checkout -b feature/dashboard-overview

# Work on feature
# ... edit files ...

# Commit
git add .
git commit -m "Add dashboard overview"

# Push branch
git push origin feature/dashboard-overview

# Create Pull Request on GitHub
# Merge to main after review

# Switch back to main
git checkout main
git pull origin main
```

---

## 📋 REQUIREMENTS.TXT

**File `requirements.txt`:**

```
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# HTTP Client
httpx==0.25.2
requests==2.31.0

# Environment
python-dotenv==1.0.0

# Telegram
python-telegram-bot==20.7

# Facebook API
facebook-sdk==3.1.0

# AI Integration
openai==1.3.7
google-generativeai==0.3.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# Monitoring
prometheus-client==0.19.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
```

---

## 📋 PROJECT STRUCTURE

```
facebook-ads-automation/
├── .git/
├── .gitignore
├── env.example
├── README.md
├── requirements.txt
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py
│   │   │   ├── automation.py
│   │   │   ├── reports.py
│   │   │   └── alerts.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── adset.py
│   │   └── metrics.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── facebook_api.py
│   │   ├── telegram_bot.py
│   │   ├── automation.py
│   │   ├── dashboard.py
│   │   └── ai_service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── automation.py
│   │   └── reports.py
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py
│       └── validators.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services.py
├── docs/
│   ├── SETUP.md
│   ├── API.md
│   └── DEPLOYMENT.md
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

---

## 🔄 DEPLOYMENT SCRIPT

### **DEPLOY.SH:**

```bash
#!/bin/bash

# Deployment script
set -e

echo "🚀 Starting deployment..."

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running migrations..."
alembic upgrade head

# Restart service
echo "🔄 Restarting service..."
sudo systemctl restart facebook-ads-api

# Check status
echo "✅ Checking status..."
sudo systemctl status facebook-ads-api --no-pager

echo "🎉 Deployment completed!"
```

**Make executable:**
```bash
chmod +x deploy.sh
```

**Run:**
```bash
./deploy.sh
```

---

## 📋 GIT COMMANDS CHEAT SHEET

### **BASIC COMMANDS:**
```bash
# Check status
git status

# Add files
git add .
git add file.py

# Commit
git commit -m "Your message"

# Push
git push origin main

# Pull
git pull origin main

# Clone
git clone https://github.com/username/repo.git

# Branch
git checkout -b feature/new-feature
git checkout main
git merge feature/new-feature
```

### **USEFUL COMMANDS:**
```bash
# View history
git log
git log --oneline

# View changes
git diff

# Undo changes
git checkout -- file.py

# Reset to previous commit
git reset --hard HEAD~1

# Stash changes
git stash
git stash pop
```

---

## 🎯 KHUYẾN NGHỊ

### **✅ NÊN LÀM:**
1. ✅ **Dùng Git/GitHub** để version control
2. ✅ **Commit thường xuyên** với messages rõ ràng
3. ✅ **Dùng branches** cho features mới
4. ✅ **.gitignore** để exclude secrets
5. ✅ **README.md** với hướng dẫn đầy đủ
6. ✅ **requirements.txt** để quản lý dependencies
7. ✅ **env.example** để document environment variables (không có dấu chấm để có thể commit vào Git)

### **❌ KHÔNG NÊN:**
1. ❌ **Commit secrets** (.env, tokens, keys)
2. ❌ **Commit large files** (database dumps, logs)
3. ❌ **Commit compiled files** (__pycache__, .pyc)
4. ❌ **Commit IDE files** (.vscode, .idea)

---

## 🚀 QUICK START

### **TRÊN MÁY LOCAL:**
```bash
# 1. Initialize Git
git init
git add .
git commit -m "Initial commit"

# 2. Add remote
git remote add origin https://github.com/your-username/facebook-ads-automation.git

# 3. Push
git branch -M main
git push -u origin main
```

### **TRÊN VPS:**
```bash
# 1. Clone repository
git clone https://github.com/your-username/facebook-ads-automation.git
cd facebook-ads-automation

# 2. Setup environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Setup .env
cp env.example .env
nano .env

# 4. Deploy
./deploy.sh
```

---

## 📋 CHECKLIST

### **✅ SETUP GIT:**
- [ ] Đã tạo GitHub repository
- [ ] Đã tạo .gitignore
- [ ] Đã tạo README.md
- [ ] Đã tạo requirements.txt
- [ ] Đã tạo env.example
- [ ] Đã commit và push code lên GitHub

### **✅ DEPLOYMENT:**
- [ ] Đã install Git trên VPS
- [ ] Đã clone repository
- [ ] Đã setup virtual environment
- [ ] Đã install dependencies
- [ ] Đã setup .env file
- [ ] Đã setup database
- [ ] Đã deploy và test

---

## 🎯 KẾT LUẬN

### **✅ KHUYẾN NGHỊ: DÙNG GIT/GITHUB**

**Lợi ích:**
- ✅ Version control
- ✅ Backup code
- ✅ Deploy dễ dàng
- ✅ Collaboration
- ✅ Rollback dễ dàng

**Workflow:**
1. Develop trên local
2. Commit và push lên GitHub
3. Pull trên VPS
4. Deploy

**Security:**
- ✅ Không commit secrets
- ✅ Dùng .env file
- ✅ Private repository

---

**Chúc bạn setup thành công! 🚀**

