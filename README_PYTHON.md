# 🚀 HƯỚNG DẪN SỬ DỤNG - PYTHON VERSION

## 📋 TỔNG QUAN

Đây là phiên bản Python của hệ thống Facebook Ads Automation, được migrate từ Google Apps Script.

## 🛠️ CẤU TRÚC PROJECT

```
facebook-ads-automation/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings management
│   │   └── database.py         # PostgreSQL models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── automation.py       # Automation logic
│   │   ├── facebook_api.py     # Facebook API integration
│   │   ├── logics.py           # Logic rules
│   │   └── telegram_bot.py     # Telegram Bot
│   ├── models/
│   │   └── __init__.py
│   └── schemas/
│       └── __init__.py
├── requirements.txt
├── env.example
├── .env                        # Tạo từ env.example
└── README_PYTHON.md
```

## 🚀 SETUP

### **1. Cài đặt Python và dependencies:**

```bash
# Tạo virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Setup database PostgreSQL:**

```bash
# Tạo database
sudo -u postgres psql
CREATE DATABASE facebook_ads_db;
CREATE USER fbads_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE facebook_ads_db TO fbads_user;
\q
```

### **3. Tạo file .env:**

```bash
# Copy từ env.example
cp env.example .env

# Edit .env với các giá trị thực tế
nano .env
```

### **4. Khởi tạo database:**

```bash
# Chạy migrations (nếu có Alembic)
# Hoặc database sẽ tự động tạo tables khi chạy app
python -c "from app.core.database import init_db; init_db()"
```

### **5. Chạy ứng dụng:**

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (với systemd)
# Xem deploy.sh
```

## 📝 CẤU HÌNH

### **File .env:**

```env
# Facebook API
ACCESS_TOKEN=your_facebook_access_token
AD_ACCOUNT_IDS=act_123456789,act_987654321
DATA_DATE_PRESET=yesterday

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TELEGRAM_AUTHORIZED_CHAT_ID=your_authorized_chat_id

# Database
DATABASE_URL=postgresql://fbads_user:your_password@localhost:5432/facebook_ads_db

# Automation Settings
RUN_WINDOW_START_HOUR=6
RUN_WINDOW_END_HOUR=23
DELAY_KHI_TAT_BATCH=1000
```

## 🔄 SO SÁNH VỚI GOOGLE APPS SCRIPT

| Google Apps Script | Python |
|-------------------|--------|
| `Code.gs` | `app/services/automation.py` |
| `Facebook API.gs` | `app/services/facebook_api.py` |
| `Logics.gs` | `app/services/logics.py` |
| `Telegram.gs` | `app/services/telegram_bot.py` |
| `Pages.gs` | (Không cần trong Python version) |
| Google Sheets | PostgreSQL |
| `PropertiesService` | Database tables |
| `CacheService` | (Có thể dùng Redis sau) |

## 🎯 SỬ DỤNG

### **1. Chạy automation:**

```bash
# Chạy automation (trong khung giờ cho phép)
curl -X POST http://localhost:8000/automation/run

# Test automation (bỏ qua khung giờ)
curl -X POST http://localhost:8000/automation/test
```

### **2. Hoặc chạy trực tiếp:**

```python
from app.services.automation import run_automation, test_run_automation

# Chạy automation
run_automation()

# Test automation
test_run_automation()
```

## 📊 DATABASE

### **Tables:**

1. **ads_metrics** - Lưu trữ dữ liệu ads từ Facebook API
2. **logic_rules** - Lưu trữ logic rules (thay thế cho LogicRules sheet)
3. **system_settings** - Lưu trữ system settings (thay thế cho CaiDat sheet)
4. **automation_status** - Lưu trữ trạng thái enable/disable automation

### **Migration từ Google Sheets:**

```python
# Cần migrate dữ liệu từ Google Sheets sang PostgreSQL
# Có thể viết script migration riêng
```

## 🔧 DEPLOYMENT

### **Với Systemd:**

```bash
# Tạo service file
sudo nano /etc/systemd/system/facebook-ads-api.service

# Start service
sudo systemctl start facebook-ads-api
sudo systemctl enable facebook-ads-api
```

### **Với Cron (để chạy automation định kỳ):**

```bash
# Edit crontab
crontab -e

# Chạy automation mỗi 15 phút
*/15 * * * * cd /path/to/project && source venv/bin/activate && python -c "from app.services.automation import run_automation; run_automation()"
```

## 🐛 TROUBLESHOOTING

### **Lỗi database connection:**

```bash
# Kiểm tra PostgreSQL đang chạy
sudo systemctl status postgresql

# Kiểm tra connection
psql -U fbads_user -d facebook_ads_db -h localhost
```

### **Lỗi Facebook API:**

```bash
# Kiểm tra ACCESS_TOKEN
# Kiểm tra permissions của token
# Kiểm tra rate limits
```

## 📚 TÀI LIỆU THAM KHẢO

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Chúc bạn sử dụng thành công! 🚀**

