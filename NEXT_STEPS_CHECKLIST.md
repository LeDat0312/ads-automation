# 📋 CHECKLIST - CÁC BƯỚC TIẾP THEO

## 🎯 MỤC TIÊU

Hoàn thiện hệ thống để có thể chạy automation và sử dụng dashboard.

---

## ✅ ĐÃ HOÀN THÀNH

- ✅ Python code structure (FastAPI)
- ✅ Database models (PostgreSQL)
- ✅ Facebook API integration
- ✅ Telegram Bot integration
- ✅ Automation logic
- ✅ Dashboard web UI
- ✅ Rule templates system
- ✅ Campaign type detection

---

## 📋 CẦN LÀM TIẾP THEO

### **PHASE 1: SETUP CƠ BẢN (Ưu tiên cao)**

#### **1.1. Setup Database PostgreSQL:**
- [ ] Install PostgreSQL trên VPS
- [ ] Tạo database `facebook_ads_db`
- [ ] Tạo user `fbads_user`
- [ ] Update `.env` với DATABASE_URL
- [ ] Chạy `init_db()` để tạo tables
- [ ] Verify tables đã được tạo

**Commands:**
```bash
# Trên VPS
sudo -u postgres psql
CREATE DATABASE facebook_ads_db;
CREATE USER fbads_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE facebook_ads_db TO fbads_user;
\q

# Trong Python
python -c "from app.core.database import init_db; init_db()"
```

#### **1.2. Setup Environment Variables:**
- [ ] Copy `env.example` thành `.env`
- [ ] Điền Facebook Access Token
- [ ] Điền Ad Account IDs
- [ ] Điền Telegram Bot Token
- [ ] Điền Telegram Chat ID
- [ ] Điền Database URL
- [ ] Verify tất cả settings

**File `.env`:**
```env
ACCESS_TOKEN=your_token
AD_ACCOUNT_IDS=act_123,act_456
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DATABASE_URL=postgresql://fbads_user:password@localhost:5432/facebook_ads_db
```

#### **1.3. Install Dependencies:**
- [ ] Tạo virtual environment
- [ ] Install requirements.txt
- [ ] Verify installation

**Commands:**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### **PHASE 2: MIGRATE DỮ LIỆU (Ưu tiên cao)**

#### **2.1. Migrate Logic Rules từ Google Sheets:**
- [ ] Đọc LogicRules sheet
- [ ] Parse dữ liệu
- [ ] Import vào `logic_rules` table
- [ ] Verify dữ liệu đã được import

**Script cần tạo:**
```python
# migrate_logic_rules.py
# Đọc từ Google Sheets và import vào PostgreSQL
```

#### **2.2. Initialize Rule Templates:**
- [ ] Chạy API để initialize default templates
- [ ] Verify templates đã được tạo
- [ ] Test apply template

**Commands:**
```bash
# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Initialize templates
curl -X POST http://localhost:8000/api/templates/initialize
```

#### **2.3. Setup Campaign Types:**
- [ ] Chạy automation lần đầu để detect campaign types
- [ ] Verify campaign types đã được detect
- [ ] Manual override nếu cần

---

### **PHASE 3: TEST VÀ VERIFY (Ưu tiên cao)**

#### **3.1. Test Facebook API:**
- [ ] Test `pull_facebook_data()`
- [ ] Verify dữ liệu đã được lưu vào database
- [ ] Check metrics đã đúng chưa

**Test:**
```python
from app.services.facebook_api import pull_facebook_data
from app.core.config import get_settings

settings = get_settings()
data = pull_facebook_data(
    settings.ACCESS_TOKEN,
    settings.AD_ACCOUNT_IDS,
    "yesterday"
)
print(f"Got {len(data)} ads")
```

#### **3.2. Test Automation:**
- [ ] Test `run_automation()`
- [ ] Verify adsets đã được tắt/bật đúng
- [ ] Check Telegram notifications

**Test:**
```python
from app.services.automation import test_run_automation
test_run_automation()
```

#### **3.3. Test Dashboard:**
- [ ] Truy cập `http://localhost:8000/api/dashboard/`
- [ ] Test filters (Account, Prefix, Status, Date)
- [ ] Test export CSV
- [ ] Verify stats đã đúng

#### **3.4. Test Rule Templates:**
- [ ] List templates: `GET /api/templates`
- [ ] Get template: `GET /api/templates/1`
- [ ] Apply template: `POST /api/templates/1/apply`
- [ ] Verify rule đã được tạo

---

### **PHASE 4: CẢI THIỆN (Ưu tiên trung bình)**

#### **4.1. Template UI trong Dashboard:**
- [ ] Thêm section "Templates" trong dashboard
- [ ] Dropdown chọn template
- [ ] Preview conditions
- [ ] Select account/prefix
- [ ] Apply template button

#### **4.2. Campaign Type UI:**
- [ ] Hiển thị campaign type trong dashboard
- [ ] Filter theo campaign type
- [ ] Manual override campaign type

#### **4.3. Google Sheets Sync (Optional):**
- [ ] Script sync LogicRules từ Sheets → Database
- [ ] Auto-sync hoặc manual sync
- [ ] Two-way sync (nếu cần)

---

### **PHASE 5: DEPLOYMENT (Ưu tiên cao)**

#### **5.1. Deploy trên VPS:**
- [ ] Setup systemd service
- [ ] Setup Nginx reverse proxy
- [ ] Setup SSL (Let's Encrypt)
- [ ] Test production

**Systemd service:**
```bash
sudo nano /etc/systemd/system/facebook-ads-api.service
# Xem AWS_LIGHTSAIL_SETUP_GUIDE.md
```

#### **5.2. Schedule Automation:**
- [ ] Setup cron job hoặc systemd timer
- [ ] Chạy automation mỗi 15 phút (6h-23h)
- [ ] Test schedule

**Cron:**
```bash
# Chạy mỗi 15 phút từ 6h-23h
*/15 6-23 * * * cd /path/to/project && source venv/bin/activate && python -c "from app.services.automation import run_automation; run_automation()"
```

#### **5.3. Monitoring:**
- [ ] Setup logging
- [ ] Setup error alerts
- [ ] Monitor performance

---

### **PHASE 6: MAKE.COM INTEGRATION (Optional)**

#### **6.1. Create Make.com Scenario:**
- [ ] Schedule trigger (Every 15 min)
- [ ] HTTP request to Python API
- [ ] AI integration (OpenAI/Gemini/Lexi)
- [ ] Telegram notifications

#### **6.2. Test Make.com:**
- [ ] Test scenario
- [ ] Verify automation chạy đúng
- [ ] Check AI recommendations

---

## 🚀 QUICK START - BẮT ĐẦU NGAY

### **Bước 1: Setup Database (5 phút)**
```bash
# Trên VPS
sudo -u postgres psql
CREATE DATABASE facebook_ads_db;
CREATE USER fbads_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE facebook_ads_db TO fbads_user;
\q
```

### **Bước 2: Setup Environment (2 phút)**
```bash
# Copy env.example
cp env.example .env

# Edit .env
nano .env
# Điền các giá trị: ACCESS_TOKEN, AD_ACCOUNT_IDS, TELEGRAM_BOT_TOKEN, etc.
```

### **Bước 3: Install & Run (3 phút)**
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.core.database import init_db; init_db()"

# Initialize templates
python -c "from app.services.rule_template_service import initialize_default_templates; initialize_default_templates()"

# Run server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Bước 4: Test (5 phút)**
```bash
# Test automation
curl -X POST http://localhost:8000/automation/test

# Test dashboard
# Mở browser: http://localhost:8000/api/dashboard/

# Test templates
curl http://localhost:8000/api/templates
```

---

## 📝 PRIORITY ORDER

### **🔴 URGENT (Làm ngay):**
1. Setup Database PostgreSQL
2. Setup Environment Variables (.env)
3. Install Dependencies
4. Initialize Database Tables
5. Initialize Rule Templates
6. Test Facebook API
7. Test Automation

### **🟡 IMPORTANT (Làm sau):**
1. Migrate Logic Rules từ Google Sheets
2. Test Dashboard
3. Test Rule Templates
4. Deploy trên VPS
5. Schedule Automation

### **🟢 NICE TO HAVE (Có thể làm sau):**
1. Template UI trong Dashboard
2. Campaign Type UI
3. Google Sheets Sync
4. Make.com Integration
5. AI Integration

---

## 🎯 KẾT QUẢ MONG ĐỢI

Sau khi hoàn thành Phase 1-3, bạn sẽ có:
- ✅ Database đã setup và có dữ liệu
- ✅ Automation chạy được
- ✅ Dashboard hiển thị dữ liệu
- ✅ Templates có thể apply
- ✅ Campaign types đã được detect

---

## 📚 TÀI LIỆU THAM KHẢO

- `AWS_LIGHTSAIL_SETUP_GUIDE.md` - Setup VPS
- `README_PYTHON.md` - Hướng dẫn Python
- `SETUP_PYTHON.md` - Quick setup
- `DASHBOARD_GUIDE.md` - Dashboard usage
- `RULE_TEMPLATES_SYSTEM.md` - Templates system

---

**Bắt đầu với Phase 1 nhé! 🚀**

