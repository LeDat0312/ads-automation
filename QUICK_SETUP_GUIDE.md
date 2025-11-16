# 🚀 QUICK SETUP GUIDE - BẮT ĐẦU NGAY

## ⚡ SETUP NHANH (15 PHÚT)

### **BƯỚC 1: SETUP DATABASE (5 phút)**

```bash
# Trên VPS (hoặc local nếu có PostgreSQL)
sudo -u postgres psql

# Tạo database
CREATE DATABASE facebook_ads_db;

# Tạo user
CREATE USER fbads_user WITH PASSWORD 'your_secure_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE facebook_ads_db TO fbads_user;

# Exit
\q
```

### **BƯỚC 2: SETUP ENVIRONMENT (2 phút)**

```bash
# Copy env.example
cp env.example .env

# Edit .env với các giá trị thực tế
nano .env
```

**Nội dung `.env` cần điền:**
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

### **BƯỚC 3: INSTALL & INITIALIZE (3 phút)**

```bash
# Tạo virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (tạo tables)
python -c "from app.core.database import init_db; init_db()"

# Initialize default templates
python -c "from app.services.rule_template_service import initialize_default_templates; initialize_default_templates()"
```

### **BƯỚC 4: RUN SERVER (1 phút)**

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (với systemd)
# Xem AWS_LIGHTSAIL_SETUP_GUIDE.md
```

### **BƯỚC 5: TEST (4 phút)**

#### **5.1. Test Automation:**
```bash
# Test automation (bỏ qua khung giờ)
curl -X POST http://localhost:8000/automation/test
```

#### **5.2. Test Dashboard:**
```
Mở browser: http://localhost:8000/api/dashboard/
```

#### **5.3. Test Templates:**
```bash
# List templates
curl http://localhost:8000/api/templates

# Apply template
curl -X POST http://localhost:8000/api/templates/1/apply \
  -H "Content-Type: application/json" \
  -d '{"account_id": "act_123", "prefix": "PX"}'
```

---

## 📋 CHECKLIST

### **✅ SAU KHI SETUP:**
- [ ] Database đã được tạo
- [ ] .env file đã được điền đầy đủ
- [ ] Dependencies đã được install
- [ ] Database tables đã được tạo
- [ ] Default templates đã được initialize
- [ ] Server đã chạy được
- [ ] Automation test thành công
- [ ] Dashboard truy cập được
- [ ] Templates API hoạt động

---

## 🔧 TROUBLESHOOTING

### **Lỗi: Database connection failed**
```bash
# Kiểm tra PostgreSQL đang chạy
sudo systemctl status postgresql

# Kiểm tra connection
psql -U fbads_user -d facebook_ads_db -h localhost
```

### **Lỗi: Module not found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### **Lỗi: Facebook API error**
- Kiểm tra ACCESS_TOKEN
- Kiểm tra permissions của token
- Kiểm tra Ad Account IDs format

---

## 🎯 NEXT STEPS

Sau khi setup xong:
1. ✅ Test automation
2. ✅ Migrate Logic Rules từ Google Sheets (nếu cần)
3. ✅ Apply templates cho accounts/prefixes
4. ✅ Setup schedule automation
5. ✅ Deploy trên VPS (production)

---

**Chúc bạn setup thành công! 🚀**

