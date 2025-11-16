# ✅ CẬP NHẬT .ENV VỚI CHAT ID

## 🎯 THÔNG TIN ĐÃ LẤY ĐƯỢC

Từ response, tôi thấy:
- ✅ **Chat ID:** `-1003433325208`
- ✅ **Chat Title:** "BC ADS Lào"
- ✅ **Chat Type:** "supergroup"

---

## 📝 CẬP NHẬT .ENV

### **BƯỚC 1: Tạo Webhook Secret và Secret Key:**

```bash
# Trên VPS
cd ~/ads-automation

# Tạo Webhook Secret
openssl rand -hex 32

# Tạo Secret Key
openssl rand -hex 32
```

**Copy 2 secrets này** (sẽ dùng cho `TELEGRAM_WEBHOOK_SECRET` và `SECRET_KEY`)

### **BƯỚC 2: Edit .env:**

```bash
nano .env
```

### **BƯỚC 3: Cập nhật các giá trị:**

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
TELEGRAM_WEBHOOK_SECRET=PASTE_WEBHOOK_SECRET_HERE
WEBHOOK_URL=https://your-server-ip/api/telegram/webhook

# ===== Automation =====
RUN_WINDOW_START_HOUR=6
RUN_WINDOW_END_HOUR=23
DELAY_KHI_TAT_BATCH=1000
NOTIFY_NO_VIOLATION_MINUTES=30

# ===== Server =====
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=PASTE_SECRET_KEY_HERE

# ===== Job Queue =====
JOB_QUEUE_WORKERS=2
JOB_RATE_LIMIT_SECONDS=30
JOB_MAX_ATTEMPTS=3
```

**Thay:**
- `PASTE_WEBHOOK_SECRET_HERE` → Webhook secret đã tạo
- `PASTE_SECRET_KEY_HERE` → Secret key đã tạo
- `your-server-ip` → IP của server (ví dụ: `172.26.10.102`)

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🔍 VERIFY .ENV

```bash
# Check .env (không hiển thị toàn bộ, chỉ check một vài dòng)
grep TELEGRAM_CHAT_ID .env
grep TELEGRAM_WEBHOOK_SECRET .env
grep SECRET_KEY .env
```

**Kết quả mong đợi:**
```
TELEGRAM_CHAT_ID=-1003433325208
TELEGRAM_WEBHOOK_SECRET=...
SECRET_KEY=...
```

---

## 🌐 WEBHOOK_URL

### **Tạm thời (chưa có domain):**

```bash
# Dùng IP của server
WEBHOOK_URL=https://172.26.10.102/api/telegram/webhook
```

**⚠️ Lưu ý:** 
- Cần server đã chạy API và accessible từ internet
- Nếu chưa có SSL, có thể dùng HTTP (không khuyến nghị)
- Setup webhook sau khi API server đã chạy

---

## ✅ CHECKLIST

- [x] Chat ID: `-1003433325208`
- [ ] Tạo Webhook Secret: `openssl rand -hex 32`
- [ ] Tạo Secret Key: `openssl rand -hex 32`
- [ ] Update .env với Chat ID
- [ ] Update .env với Webhook Secret
- [ ] Update .env với Secret Key
- [ ] Update .env với WEBHOOK_URL (sau khi deploy)

---

## 🚀 NEXT STEPS

1. ✅ Tạo Webhook Secret và Secret Key
2. ✅ Update .env
3. ⏭️ Continue setup: install dependencies, init database
4. ⏭️ Setup webhook sau khi API server chạy

---

**Bây giờ hãy tạo Webhook Secret và Secret Key, sau đó update .env! 🚀**


