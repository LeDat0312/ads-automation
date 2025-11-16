# 🚀 SETUP PYTHON VERSION - HƯỚNG DẪN NHANH

## ✅ ĐÃ TẠO CÁC FILE PYTHON

### **1. Core Files:**
- ✅ `app/core/config.py` - Quản lý settings (thay thế `layCaiDatHeThong()`)
- ✅ `app/core/database.py` - PostgreSQL models (thay thế Google Sheets)

### **2. Services:**
- ✅ `app/services/automation.py` - Automation logic (thay thế `Code.gs`)
- ✅ `app/services/facebook_api.py` - Facebook API (thay thế `Facebook API.gs`)
- ✅ `app/services/logics.py` - Logic rules (thay thế `Logics.gs`)
- ✅ `app/services/telegram_bot.py` - Telegram Bot (thay thế `Telegram.gs`)

### **3. Main:**
- ✅ `app/main.py` - FastAPI entry point

## 🚀 BƯỚC TIẾP THEO

### **1. Setup Environment:**

```bash
# Tạo virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Setup Database:**

```bash
# Tạo database PostgreSQL
sudo -u postgres psql
CREATE DATABASE facebook_ads_db;
CREATE USER fbads_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE facebook_ads_db TO fbads_user;
\q
```

### **3. Cấu hình .env:**

```bash
# Copy từ env.example
cp env.example .env

# Edit .env
nano .env
```

### **4. Khởi tạo Database:**

```bash
# Chạy để tạo tables
python -c "from app.core.database import init_db; init_db()"
```

### **5. Migrate dữ liệu từ Google Sheets:**

**QUAN TRỌNG:** Cần migrate dữ liệu từ Google Sheets sang PostgreSQL:
- **LogicRules sheet** → `logic_rules` table
- **CaiDat sheet** → `system_settings` table (hoặc dùng .env)
- **Data_FB sheet** → `ads_metrics` table (sẽ được tự động lấy từ Facebook API)

### **6. Chạy ứng dụng:**

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Hoặc chạy trực tiếp
python -c "from app.services.automation import run_automation; run_automation()"
```

## 📋 SO SÁNH VỚI GOOGLE APPS SCRIPT

| Chức năng | Google Apps Script | Python |
|-----------|-------------------|--------|
| Settings | `layCaiDatHeThong()` | `app/core/config.py` |
| Database | Google Sheets | PostgreSQL |
| Automation | `runAutomation()` | `app/services/automation.py` |
| Facebook API | `pullFacebookData()` | `app/services/facebook_api.py` |
| Logic Rules | `buildLogicMap()` | `app/services/logics.py` |
| Telegram | `guiThongBaoTelegram()` | `app/services/telegram_bot.py` |

## ⚠️ LƯU Ý QUAN TRỌNG

### **1. Database:**
- **Google Sheets** được thay thế bằng **PostgreSQL**
- Cần migrate dữ liệu từ Sheets sang Database
- Logic rules cần được import vào `logic_rules` table

### **2. Settings:**
- Settings được lưu trong `.env` file
- Không cần Google Sheets `CaiDat` nữa
- Tất cả settings đọc từ environment variables

### **3. Automation:**
- Chức năng tương tự như Google Apps Script
- Chạy qua FastAPI hoặc trực tiếp Python
- Có thể schedule với cron hoặc systemd timer

### **4. Telegram Bot:**
- Chức năng tương tự
- Cần setup webhook riêng (có thể thêm sau)
- Commands vẫn hoạt động tương tự

## 🔧 CẦN BỔ SUNG

### **1. Telegram Webhook:**
- Cần thêm API endpoint cho Telegram webhook
- Xem `Telegram.gs` để implement các commands

### **2. Reporting:**
- Cần migrate `tongKetCuoiNgay()` và `generateSummaryReport()`
- Xem `Code.gs` và `Telegram.gs` để implement

### **3. Migration Script:**
- Cần script để migrate dữ liệu từ Google Sheets sang PostgreSQL
- Có thể dùng Google Sheets API hoặc export CSV

## 📚 TÀI LIỆU

- Xem `README_PYTHON.md` để biết chi tiết
- Xem code comments trong các file Python
- So sánh với file .gs tương ứng để hiểu logic

---

**Chúc bạn setup thành công! 🚀**

