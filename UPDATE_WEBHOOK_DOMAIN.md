# 🔄 UPDATE TELEGRAM WEBHOOK VỚI DOMAIN

## ✅ DOMAIN MỚI

- **Domain:** `updatemetaads.site`
- **Webhook URL:** `https://updatemetaads.site/api/telegram/webhook`

---

## 🔧 CẬP NHẬT

### **BƯỚC 1: Cập nhật `.env`**

```bash
cd ~/ads-automation
nano .env
```

**Tìm và sửa:**

```env
# Cũ:
# WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook

# Mới:
WEBHOOK_URL=https://updatemetaads.site/api/telegram/webhook
```

**Lưu và thoát:** `Ctrl+X`, `Y`, `Enter`

### **BƯỚC 2: Lấy thông tin từ `.env`**

```bash
cd ~/ads-automation
source venv/bin/activate

# Lấy BOT_TOKEN và WEBHOOK_SECRET
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'BOT_TOKEN: {settings.TELEGRAM_BOT_TOKEN}')
print(f'WEBHOOK_SECRET: {settings.TELEGRAM_WEBHOOK_SECRET}')
print(f'WEBHOOK_URL: {settings.WEBHOOK_URL}')
"
```

### **BƯỚC 3: Update Telegram Webhook**

```bash
# Thay <BOT_TOKEN> và <WEBHOOK_SECRET> bằng giá trị từ .env
BOT_TOKEN="8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k"
WEBHOOK_SECRET="961197b8cca6e1468b412b1e98fda145d19d9cb73ef4bcf1429e8da2e26b9083"
WEBHOOK_URL="https://updatemetaads.site/api/telegram/webhook"

# Set webhook
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"${WEBHOOK_URL}\",
    \"secret_token\": \"${WEBHOOK_SECRET}\"
  }"
```

**Kết quả mong đợi:**
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

### **BƯỚC 4: Verify Webhook**

```bash
# Get webhook info
curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
```

**Kết quả mong đợi:**
```json
{
  "ok": true,
  "result": {
    "url": "https://updatemetaads.site/api/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": 0,
    "last_error_message": "",
    "secret_token": "..."
  }
}
```

### **BƯỚC 5: Test Webhook**

```bash
# Test từ Telegram
# Gửi /start hoặc /help trong Telegram

# Check logs
sudo tail -f /var/log/ads-automation/api.out.log
sudo tail -f /var/log/nginx/updatemetaads.access.log
```

### **BƯỚC 6: Restart API (nếu cần)**

```bash
sudo supervisorctl restart ads-automation-api
sudo supervisorctl status
```

---

## 🔍 VERIFY

### **Test Webhook URL:**

```bash
# Test HTTPS
curl https://updatemetaads.site/health

# Test API endpoint
curl https://updatemetaads.site/api/telegram/webhook -X POST -H "Content-Type: application/json" -d '{"test": true}'
```

### **Test từ Telegram:**

1. Gửi `/start` trong Telegram
2. Gửi `/help` trong Telegram
3. Check logs để xem có nhận được request không

---

## 📋 CHECKLIST

- [ ] Cập nhật `.env` với domain mới
- [ ] Lấy BOT_TOKEN và WEBHOOK_SECRET
- [ ] Update Telegram webhook
- [ ] Verify webhook info
- [ ] Test webhook từ Telegram
- [ ] Check logs
- [ ] Restart API (nếu cần)

---

## ⚠️ LƯU Ý

1. **SSL:** Đảm bảo SSL đã được setup trước khi update webhook
2. **DNS:** Đảm bảo DNS đã propagate (5-60 phút)
3. **Firewall:** Đảm bảo ports 80 và 443 đã mở
4. **Secret Token:** Dùng `TELEGRAM_WEBHOOK_SECRET` từ `.env`
5. **HTTPS:** Telegram chỉ chấp nhận HTTPS webhook

---

## 🔄 ROLLBACK (nếu cần)

```bash
# Rollback về IP
WEBHOOK_URL="https://54.179.208.122/api/telegram/webhook"

curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"${WEBHOOK_URL}\",
    \"secret_token\": \"${WEBHOOK_SECRET}\"
  }"
```

---

**Bây giờ hãy update webhook với domain mới! 🚀**


