# 🌐 CẬP NHẬT WEBHOOK_URL VỚI IP SERVER

## 🎯 IP SERVER

- ✅ **Server IP:** `54.179.208.122`

---

## 📝 CẬP NHẬT .ENV

### **Edit .env:**

```bash
cd ~/ads-automation
nano .env
```

### **Cập nhật WEBHOOK_URL:**

```bash
WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook
```

**Hoặc nếu chưa có SSL, dùng HTTP (tạm thời, không khuyến nghị):**

```bash
WEBHOOK_URL=http://54.179.208.122/api/telegram/webhook
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## ✅ VERIFY

```bash
# Check WEBHOOK_URL
grep WEBHOOK_URL .env
```

**Kết quả mong đợi:**
```
WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook
```

---

## ⚠️ LƯU Ý VỀ HTTPS

### **Nếu dùng HTTPS:**

- Cần SSL certificate
- Cần mở port 443
- Telegram yêu cầu HTTPS cho webhook

### **Nếu chưa có SSL:**

1. **Dùng HTTP tạm thời:**
   ```bash
   WEBHOOK_URL=http://54.179.208.122/api/telegram/webhook
   ```
   **⚠️ Lưu ý:** Telegram có thể không chấp nhận HTTP, cần HTTPS

2. **Setup SSL sau:**
   - Dùng Let's Encrypt
   - Hoặc dùng domain với SSL

---

## 🔧 SETUP WEBHOOK SAU KHI API CHẠY

### **Sau khi API server đã chạy:**

```bash
# Set webhook cho Telegram bot
curl -X POST "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/setWebhook" \
  -d "url=https://54.179.208.122/api/telegram/webhook" \
  -d "secret_token=bac722f5ee22f178b4c1304e1a70293547706dbed02f7159e8fba75fba30791d"
```

**Hoặc nếu dùng HTTP:**
```bash
curl -X POST "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/setWebhook" \
  -d "url=http://54.179.208.122/api/telegram/webhook" \
  -d "secret_token=bac722f5ee22f178b4c1304e1a70293547706dbed02f7159e8fba75fba30791d"
```

### **Verify webhook:**

```bash
# Check webhook info
curl "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/getWebhookInfo"
```

---

## 🔒 SETUP SSL (KHUYẾN NGHỊ)

### **Nếu có domain:**

1. **Point domain về IP:** `54.179.208.122`
2. **Setup Let's Encrypt:**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d yourdomain.com
   ```
3. **Update WEBHOOK_URL:**
   ```bash
   WEBHOOK_URL=https://yourdomain.com/api/telegram/webhook
   ```

---

## ✅ CHECKLIST

- [ ] Update WEBHOOK_URL trong .env: `https://54.179.208.122/api/telegram/webhook`
- [ ] Verify: `grep WEBHOOK_URL .env`
- [ ] Setup SSL (nếu có domain)
- [ ] Setup webhook sau khi API server chạy

---

**Bây giờ hãy update WEBHOOK_URL trong .env với IP mới! 🚀**


