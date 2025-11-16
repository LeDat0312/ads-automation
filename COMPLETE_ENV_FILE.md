# 📝 FILE .ENV HOÀN CHỈNH

## ✅ CÁC THÔNG TIN ĐÃ SETUP

Từ các bước trước, đã có:
- ✅ Database password: `@Levandat0312`
- ✅ Telegram Bot Token: `8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k`
- ✅ Telegram Chat ID: `-1003433325208`
- ✅ Webhook Secret: `bac722f5ee22f178b4c1304e1a70293547706dbed02f7159e8fba75fba30791d`
- ✅ Secret Key: `961197b8cca6e1468b412b1e98fda145d19d9cb73ef4bcf1429e8da2e26b9083`
- ✅ Public IP: `54.179.208.122`
- ✅ Facebook Access Token: (đã có)
- ✅ AD Account IDs: `act_723686686812438,act_2827767517395636`

---

## 📝 FILE .ENV HOÀN CHỈNH

```bash
# ===== Database =====
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
REDIS_URL=redis://localhost:6379/0

# ===== Facebook API =====
ACCESS_TOKEN=EAAcklZAcKeSIBPyZBpHIu0ZA87Xq9l0H1EOLr4ZClU0vKrCSHMkMG4IwfCytqWLDxjVTIZBTHUzHpXBfm1qSSk7NrqKyoHju7TZAqThz9fdyoKsKZCIRFjCgJkt3lwm9Myv6J0hODnZA4nT9lxPwlXQZA822QVpXzbomf9eS3UncLcLOC3WIOJcr94WUr2BoK
AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636
DATA_DATE_PRESET=today

# ===== Telegram =====
TELEGRAM_BOT_TOKEN=8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k
TELEGRAM_CHAT_ID=-1003433325208
TELEGRAM_AUTHORIZED_CHAT_ID=-1003433325208
TELEGRAM_WEBHOOK_SECRET=bac722f5ee22f178b4c1304e1a70293547706dbed02f7159e8fba75fba30791d
WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook

# ===== Automation =====
RUN_WINDOW_START_HOUR=6
RUN_WINDOW_END_HOUR=23
DELAY_KHI_TAT_BATCH=1000
NOTIFY_NO_VIOLATION_MINUTES=30

# ===== Server =====
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=961197b8cca6e1468b412b1e98fda145d19d9cb73ef4bcf1429e8da2e26b9083

# ===== Job Queue =====
JOB_QUEUE_WORKERS=2
JOB_RATE_LIMIT_SECONDS=30
JOB_MAX_ATTEMPTS=3
```

---

## 🔧 CẬP NHẬT TRÊN VPS

### **Cách 1: Sửa file .env:**

```bash
cd ~/ads-automation
nano .env
```

**Thay thế toàn bộ nội dung với code ở trên.**

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Set permissions:**
```bash
chmod 600 .env
```

### **Cách 2: Tạo file mới:**

```bash
cd ~/ads-automation
cat > .env << 'EOF'
# ===== Database =====
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
REDIS_URL=redis://localhost:6379/0

# ===== Facebook API =====
ACCESS_TOKEN=EAAcklZAcKeSIBPyZBpHIu0ZA87Xq9l0H1EOLr4ZClU0vKrCSHMkMG4IwfCytqWLDxjVTIZBTHUzHpXBfm1qSSk7NrqKyoHju7TZAqThz9fdyoKsKZCIRFjCgJkt3lwm9Myv6J0hODnZA4nT9lxPwlXQZA822QVpXzbomf9eS3UncLcLOC3WIOJcr94WUr2BoK
AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636
DATA_DATE_PRESET=today

# ===== Telegram =====
TELEGRAM_BOT_TOKEN=8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k
TELEGRAM_CHAT_ID=-1003433325208
TELEGRAM_AUTHORIZED_CHAT_ID=-1003433325208
TELEGRAM_WEBHOOK_SECRET=bac722f5ee22f178b4c1304e1a70293547706dbed02f7159e8fba75fba30791d
WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook

# ===== Automation =====
RUN_WINDOW_START_HOUR=6
RUN_WINDOW_END_HOUR=23
DELAY_KHI_TAT_BATCH=1000
NOTIFY_NO_VIOLATION_MINUTES=30

# ===== Server =====
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=961197b8cca6e1468b412b1e98fda145d19d9cb73ef4bcf1429e8da2e26b9083

# ===== Job Queue =====
JOB_QUEUE_WORKERS=2
JOB_RATE_LIMIT_SECONDS=30
JOB_MAX_ATTEMPTS=3
EOF

# Set permissions
chmod 600 .env
```

---

## ✅ VERIFY

### **Check các giá trị quan trọng:**

```bash
cd ~/ads-automation

# Check DATABASE_URL
grep DATABASE_URL .env

# Check TELEGRAM
grep TELEGRAM .env

# Check WEBHOOK_URL
grep WEBHOOK_URL .env

# Check SECRET_KEY
grep SECRET_KEY .env
```

---

## 🔐 FIX PASSWORD AUTHENTICATION

### **Reset password cho adsuser:**

```bash
sudo -u postgres psql << EOF
ALTER USER adsuser WITH PASSWORD '@Levandat0312';
\q
EOF
```

### **Test connection:**

```bash
psql -U adsuser -d ads_automation -h localhost
# Nhập password: @Levandat0312
# Nếu vào được → OK
# Thoát: \q
```

---

## 🧪 TEST SETTINGS

### **Test với Python:**

```bash
cd ~/ads-automation
source venv/bin/activate

python -c "
from app.core.config import get_settings
settings = get_settings()
print('✅ Settings loaded!')
print(f'DATABASE_URL: {settings.DATABASE_URL[:50]}...')
print(f'TELEGRAM_CHAT_ID: {settings.TELEGRAM_CHAT_ID}')
print(f'WEBHOOK_URL: {settings.WEBHOOK_URL}')
"
```

---

## ✅ CHECKLIST

- [ ] Update .env với tất cả giá trị
- [ ] Set permissions: `chmod 600 .env`
- [ ] Reset PostgreSQL password
- [ ] Test database connection
- [ ] Test settings với Python
- [ ] Run init_db: `python scripts/init_db.py`

---

**Bây giờ hãy update .env với code ở trên! 🚀**


