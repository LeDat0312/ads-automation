# 📱 TELEGRAM SETUP - HƯỚNG DẪN CHI TIẾT

## 🎯 CẦN LẤY

1. ✅ **TELEGRAM_CHAT_ID** - ID nhóm/chat
2. ✅ **TELEGRAM_WEBHOOK_SECRET** - Secret key (tự tạo)
3. ✅ **WEBHOOK_URL** - URL webhook (sau khi deploy)

---

## 📋 BƯỚC 1: LẤY TELEGRAM CHAT ID

### **Cách 1: Dùng Bot @userinfobot (Dễ nhất)**

1. **Mở Telegram**
2. **Tìm bot:** `@userinfobot`
3. **Start bot** → Bot sẽ gửi thông tin của bạn
4. **Copy "Id"** → Đây là Chat ID cá nhân

### **Cách 2: Dùng Bot @RawDataBot**

1. **Mở Telegram**
2. **Tìm bot:** `@RawDataBot`
3. **Start bot** → Bot sẽ gửi JSON data
4. **Tìm `"id"`** trong JSON → Đây là Chat ID

### **Cách 3: Lấy ID nhóm (Group Chat ID)**

1. **Thêm bot vào nhóm:**
   - Vào nhóm Telegram
   - Add member → Tìm bot của bạn (tên bot từ `TELEGRAM_BOT_TOKEN`)
   - Add bot vào nhóm

2. **Gửi message trong nhóm:**
   - Gửi bất kỳ message nào trong nhóm

3. **Lấy Chat ID:**
   ```bash
   # Trên VPS hoặc máy local
   curl "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/getUpdates"
   ```

   **Tìm trong response:**
   ```json
   {
     "message": {
       "chat": {
         "id": -1001234567890,  // ← Đây là Chat ID (số âm = nhóm)
         "title": "Tên nhóm"
       }
     }
   }
   ```

   **Lưu ý:** 
   - Số dương = Chat cá nhân
   - Số âm = Nhóm/Channel

### **Cách 4: Dùng Bot của bạn**

1. **Gửi message cho bot:**
   - Tìm bot của bạn trên Telegram
   - Gửi bất kỳ message nào (ví dụ: `/start`)

2. **Lấy Chat ID:**
   ```bash
   curl "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/getUpdates"
   ```

   **Tìm `"chat":{"id":...}` trong response**

---

## 🔐 BƯỚC 2: TẠO TELEGRAM_WEBHOOK_SECRET

### **Webhook Secret là gì?**

- Là một chuỗi bí mật để xác thực webhook từ Telegram
- Tự tạo, không lấy từ đâu cả
- Tối thiểu 32 ký tự

### **Cách tạo:**

```bash
# Trên VPS hoặc máy local
# Tạo random secret (32 ký tự)
openssl rand -hex 32

# Hoặc
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Ví dụ output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**Copy secret này** và dùng cho `TELEGRAM_WEBHOOK_SECRET`

---

## 🌐 BƯỚC 3: WEBHOOK_URL

### **Webhook URL là gì?**

- URL để Telegram gửi updates đến server của bạn
- Format: `https://your-domain.com/api/telegram/webhook`

### **Cách lấy:**

#### **Option 1: Dùng IP của server (tạm thời)**

```bash
# Nếu chưa có domain, dùng IP
WEBHOOK_URL=https://your-server-ip/api/telegram/webhook
```

**Ví dụ:**
```
WEBHOOK_URL=https://172.26.10.102/api/telegram/webhook
```

**⚠️ Lưu ý:** Cần mở port 443 (HTTPS) hoặc dùng HTTP (không khuyến nghị)

#### **Option 2: Dùng domain (khuyến nghị)**

1. **Mua domain** (ví dụ: `yourdomain.com`)
2. **Point domain về server IP**
3. **Setup SSL certificate** (Let's Encrypt)
4. **Webhook URL:**
   ```
   WEBHOOK_URL=https://yourdomain.com/api/telegram/webhook
   ```

#### **Option 3: Dùng ngrok (test local)**

```bash
# Install ngrok
# Download từ: https://ngrok.com/download

# Chạy ngrok
ngrok http 8000

# Sẽ có URL như: https://abc123.ngrok.io
# Webhook URL:
WEBHOOK_URL=https://abc123.ngrok.io/api/telegram/webhook
```

---

## 📝 CẬP NHẬT .ENV

### **Sau khi có đủ thông tin:**

```bash
cd ~/ads-automation
nano .env
```

**Cập nhật:**

```bash
# Telegram
TELEGRAM_BOT_TOKEN=8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k
TELEGRAM_CHAT_ID=-1001234567890  # ID nhóm (số âm)
TELEGRAM_AUTHORIZED_CHAT_ID=-1001234567890  # Cùng ID nhóm
TELEGRAM_WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
WEBHOOK_URL=https://your-server-ip/api/telegram/webhook  # Hoặc domain

# Secret Key (tạo tương tự webhook secret)
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🔧 SETUP WEBHOOK SAU KHI CÓ URL

### **Sau khi có WEBHOOK_URL:**

```bash
# Set webhook cho Telegram bot
curl -X POST "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/setWebhook" \
  -d "url=https://your-server-ip/api/telegram/webhook" \
  -d "secret_token=YOUR_WEBHOOK_SECRET"
```

**Thay:**
- `your-server-ip` → IP hoặc domain của bạn
- `YOUR_WEBHOOK_SECRET` → Secret bạn đã tạo

### **Verify webhook:**

```bash
# Check webhook info
curl "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/getWebhookInfo"
```

---

## ✅ QUICK SUMMARY

### **1. TELEGRAM_CHAT_ID:**
- Dùng bot `@userinfobot` hoặc `@RawDataBot`
- Hoặc: `curl "https://api.telegram.org/bot<TOKEN>/getUpdates"`
- Số âm = Nhóm, Số dương = Chat cá nhân

### **2. TELEGRAM_WEBHOOK_SECRET:**
- Tự tạo: `openssl rand -hex 32`
- Tối thiểu 32 ký tự
- Lưu lại để dùng

### **3. WEBHOOK_URL:**
- Format: `https://your-domain-or-ip/api/telegram/webhook`
- Cần server đã chạy và accessible từ internet
- Setup sau khi deploy API server

---

## 🚀 NEXT STEPS

1. ✅ Lấy Chat ID (dùng bot @userinfobot)
2. ✅ Tạo Webhook Secret (`openssl rand -hex 32`)
3. ✅ Tạo Secret Key (`openssl rand -hex 32`)
4. ✅ Update .env với các giá trị
5. ⏭️ Setup webhook sau khi deploy API server

---

**Bây giờ hãy lấy Chat ID và tạo Webhook Secret! 🚀**


