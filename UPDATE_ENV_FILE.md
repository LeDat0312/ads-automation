# 📝 UPDATE .ENV FILE TRÊN VPS

## ✅ FILE .ENV HOÀN CHỈNH

Copy nội dung sau vào file `.env` trên VPS:

```bash
cd ~/ads-automation
nano .env
```

**Xóa toàn bộ nội dung cũ và paste nội dung mới:**

```env
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

**Lưu:** `Ctrl+X`, `Y`, `Enter`

---

## 🚀 HOẶC DÙNG TEE (NHANH HƠN)

```bash
cd ~/ads-automation

# Backup file cũ
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Tạo file mới
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

```bash
# Check file
cat .env | grep "AD_ACCOUNT_IDS"

# Phải thấy:
# AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636

# Test load settings
source venv/bin/activate
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'✅ AD_ACCOUNT_IDS: {settings.AD_ACCOUNT_IDS}')
print(f'✅ ad_account_ids_list: {settings.ad_account_ids_list}')
"
```

**Kết quả mong đợi:**
```
✅ AD_ACCOUNT_IDS: act_723686686812438,act_2827767517395636
✅ ad_account_ids_list: ['act_723686686812438', 'act_2827767517395636']
```

---

## 🔄 SAU KHI UPDATE

```bash
# Xóa Python cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Test worker
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker import OK')"

# Restart workers
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

---

## 📝 LƯU Ý

1. **AD_ACCOUNT_IDS:** Phải là string với dấu phẩy, KHÔNG phải list Python
2. **WEBHOOK_URL:** Hiện đang dùng IP. Sau khi setup domain SSL, update thành `https://updatemetaads.site/api/telegram/webhook`
3. **Permissions:** File `.env` nên có permission 600 (chỉ owner đọc/ghi)

---

**Bây giờ hãy update file `.env` trên VPS! 🚀**


