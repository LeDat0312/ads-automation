# 🔧 KHẮC PHỤC LỖI 403 FORBIDDEN - WEBHOOK SECRET

## ❌ VẤN ĐỀ

Bot Telegram trả về lỗi `403 Forbidden` khi nhận webhook từ Telegram. Nguyên nhân:
- Webhook chưa được setup với `secret_token`
- Telegram gửi header `X-Telegram-Bot-Api-Secret-Token` nhưng server không nhận được hoặc không khớp

## ✅ GIẢI PHÁP

### **BƯỚC 1: Kiểm tra .env trên VPS**

```bash
cd ~/ads-automation
source venv/bin/activate

# Kiểm tra webhook secret
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'WEBHOOK_SECRET: {settings.TELEGRAM_WEBHOOK_SECRET}')
print(f'WEBHOOK_URL: {settings.WEBHOOK_URL}')
print(f'BOT_TOKEN: {settings.TELEGRAM_BOT_TOKEN[:20]}...')
"
```

### **BƯỚC 2: Setup lại webhook với secret_token**

```bash
cd ~/ads-automation
source venv/bin/activate

# Lấy thông tin từ .env
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'BOT_TOKEN={settings.TELEGRAM_BOT_TOKEN}')
print(f'WEBHOOK_SECRET={settings.TELEGRAM_WEBHOOK_SECRET}')
print(f'WEBHOOK_URL={settings.WEBHOOK_URL}')
" > /tmp/webhook_info.txt

# Đọc thông tin
source /tmp/webhook_info.txt

# Setup webhook với secret_token
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"${WEBHOOK_URL}\",
    \"secret_token\": \"${WEBHOOK_SECRET}\",
    \"allowed_updates\": [\"message\"],
    \"drop_pending_updates\": true
  }"
```

**Kết quả mong đợi:**
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

### **BƯỚC 3: Verify webhook**

```bash
# Kiểm tra webhook info
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
    "max_connections": 40,
    "ip_address": "54.179.208.122"
  }
}
```

### **BƯỚC 4: Restart API để load code mới**

```bash
sudo supervisorctl restart ads-automation-api
sudo supervisorctl status
```

### **BƯỚC 5: Test bot**

Gửi lệnh `/help` trong Telegram và kiểm tra logs:

```bash
# Xem logs real-time
sudo tail -f /var/log/ads-automation/api.out.log
```

## 🔍 DEBUG NẾU VẪN LỖI

### **Kiểm tra header trong code:**

```bash
# Xem code webhook handler
cat app/api/routes/telegram.py | grep -A 10 "verify_webhook_secret"
```

### **Test webhook thủ công:**

```bash
# Tạo test request với secret token
curl -X POST "https://updatemetaads.site/api/telegram/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: ${WEBHOOK_SECRET}" \
  -d '{
    "update_id": 999999999,
    "message": {
      "message_id": 1,
      "from": {"id": 123456789, "is_bot": false, "first_name": "Test"},
      "chat": {"id": -1003433325208, "type": "supergroup"},
      "date": 1234567890,
      "text": "/help"
    }
  }'
```

## 📝 LƯU Ý

1. **Secret token phải khớp:**
   - Secret trong `.env` (`TELEGRAM_WEBHOOK_SECRET`)
   - Secret khi setup webhook (`secret_token` trong `setWebhook`)
   - Secret trong header (`X-Telegram-Bot-Api-Secret-Token`)

2. **Sau khi update code:**
   - Code mới đã tự động thêm `secret_token` khi setup webhook
   - Nhưng webhook hiện tại có thể chưa có secret, cần setup lại

3. **Nếu vẫn lỗi:**
   - Kiểm tra `.env` có đúng secret không
   - Kiểm tra webhook URL có đúng không
   - Kiểm tra logs để xem lỗi chi tiết

