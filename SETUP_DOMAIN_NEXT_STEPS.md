# 🚀 SETUP DOMAIN - BƯỚC TIẾP THEO

## ✅ ĐÃ HOÀN THÀNH

- ✅ SSL certificate đã được cài đặt
- ✅ HTTPS đã hoạt động

---

## 📋 CÁC BƯỚC TIẾP THEO

### **BƯỚC 1: Test HTTPS**

```bash
# Test từ command line
curl https://updatemetaads.site/health

# Kết quả mong đợi:
# {"status":"healthy"}
```

**Hoặc mở browser:** `https://updatemetaads.site/health`

---

### **BƯỚC 2: Cập nhật `.env` với domain mới**

```bash
cd ~/ads-automation
nano .env
```

**Tìm dòng `WEBHOOK_URL` và sửa:**

```env
# Cũ:
WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook

# Mới:
WEBHOOK_URL=https://updatemetaads.site/api/telegram/webhook
```

**Lưu:** `Ctrl+X`, `Y`, `Enter`

---

### **BƯỚC 3: Cập nhật Telegram Webhook**

```bash
cd ~/ads-automation
source venv/bin/activate

# Lấy BOT_TOKEN và WEBHOOK_SECRET từ .env
BOT_TOKEN=$(python -c "from app.core.config import get_settings; print(get_settings().TELEGRAM_BOT_TOKEN)")
WEBHOOK_SECRET=$(python -c "from app.core.config import get_settings; print(get_settings().TELEGRAM_WEBHOOK_SECRET)")

# Update webhook
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"https://updatemetaads.site/api/telegram/webhook\",
    \"secret_token\": \"${WEBHOOK_SECRET}\"
  }"

# Verify webhook
curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
```

**Kết quả mong đợi:**
```json
{
  "ok": true,
  "result": {
    "url": "https://updatemetaads.site/api/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

### **BƯỚC 4: Test Webhook từ Telegram**

1. Mở Telegram bot
2. Gửi lệnh `/start` hoặc `/help`
3. Check logs để xem có nhận được request không:

```bash
# Check API logs
sudo tail -f /var/log/ads-automation/api.out.log

# Check Nginx logs
sudo tail -f /var/log/nginx/updatemetaads.access.log
```

---

### **BƯỚC 5: Restart services (nếu cần)**

```bash
# Restart API để load .env mới
sudo supervisorctl restart ads-automation-api

# Check status
sudo supervisorctl status
```

---

## ✅ VERIFY TẤT CẢ

### **Test HTTPS:**

```bash
# Test health check
curl https://updatemetaads.site/health

# Test API endpoint
curl https://updatemetaads.site/api/rules
```

### **Test từ browser:**

1. Mở: `https://updatemetaads.site/health`
2. Phải thấy: `{"status":"healthy"}`
3. Click vào icon khóa → Phải hiển thị "Secure" và "Valid"

### **Test Telegram:**

1. Gửi `/start` trong Telegram
2. Bot phải phản hồi
3. Check logs để verify webhook hoạt động

---

## 📋 CHECKLIST

- [ ] Test HTTPS: `curl https://updatemetaads.site/health`
- [ ] Cập nhật `.env` với domain mới
- [ ] Update Telegram webhook
- [ ] Verify webhook info
- [ ] Test webhook từ Telegram
- [ ] Check logs
- [ ] Restart API (nếu cần)

---

## 🎉 HOÀN THÀNH!

Sau khi hoàn thành các bước trên:
- ✅ Domain đã được setup với SSL
- ✅ HTTPS hoạt động
- ✅ Telegram webhook đã được cập nhật
- ✅ Hệ thống sẵn sàng sử dụng!

---

**Bây giờ hãy bắt đầu với Bước 1: Test HTTPS! 🚀**


