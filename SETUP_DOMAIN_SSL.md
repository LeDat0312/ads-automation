# 🌐 SETUP DOMAIN & SSL

## ✅ THÔNG TIN

- **Domain:** `updatemetaads.site`
- **IP:** `54.179.208.122`
- **DNS:** A record `@` → `54.179.208.122` (TTL 14400)

---

## 🎯 MỤC TIÊU

1. ✅ Setup Nginx reverse proxy
2. ✅ Setup Let's Encrypt SSL (HTTPS)
3. ✅ Cấu hình domain thay vì IP
4. ✅ Cập nhật Telegram webhook URL
5. ✅ Cập nhật `.env` với domain mới

---

## 📋 CÁC BƯỚC

### **BƯỚC 1: Install Nginx**

```bash
sudo apt update
sudo apt install -y nginx
```

### **BƯỚC 2: Install Certbot (Let's Encrypt)**

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### **BƯỚC 3: Cấu hình Firewall**

```bash
# Cho phép HTTP (80) và HTTPS (443)
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw status
```

### **BƯỚC 4: Kiểm tra DNS đã propagate chưa**

```bash
# Test DNS resolution
dig updatemetaads.site +short
# Hoặc
nslookup updatemetaads.site

# Phải trả về: 54.179.208.122
```

**⏰ Đợi 5-10 phút nếu DNS chưa propagate!**

### **BƯỚC 5: Cấu hình Nginx (trước khi SSL)**

```bash
sudo nano /etc/nginx/sites-available/updatemetaads.site
```

**Nội dung:**

```nginx
server {
    listen 80;
    server_name updatemetaads.site www.updatemetaads.site;

    # Logs
    access_log /var/log/nginx/updatemetaads.access.log;
    error_log /var/log/nginx/updatemetaads.error.log;

    # Reverse proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (nếu cần)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/updatemetaads.site /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **BƯỚC 6: Setup SSL Certificate (Let's Encrypt)**

```bash
# Request SSL certificate
sudo certbot --nginx -d updatemetaads.site -d www.updatemetaads.site

# Chọn:
# - Email: nhập email của bạn
# - Agree to terms: Y
# - Share email: N (optional)
# - Redirect HTTP to HTTPS: 2 (Redirect)
```

**Certbot sẽ tự động:**
- Tạo SSL certificate
- Cấu hình Nginx với HTTPS
- Setup auto-renewal

### **BƯỚC 7: Test SSL**

```bash
# Test HTTPS
curl https://updatemetaads.site/health

# Test từ browser
# https://updatemetaads.site
```

### **BƯỚC 8: Cập nhật `.env`**

```bash
cd ~/ads-automation
nano .env
```

**Cập nhật:**

```env
# Cũ: WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook
# Mới:
WEBHOOK_URL=https://updatemetaads.site/api/telegram/webhook
```

### **BƯỚC 9: Cập nhật Telegram Webhook**

```bash
# Test webhook URL
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -d "url=https://updatemetaads.site/api/telegram/webhook" \
  -d "secret_token=<WEBHOOK_SECRET>"

# Verify webhook
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"
```

**Thay:**
- `<BOT_TOKEN>` = `TELEGRAM_BOT_TOKEN` từ `.env`
- `<WEBHOOK_SECRET>` = `TELEGRAM_WEBHOOK_SECRET` từ `.env`

### **BƯỚC 10: Restart services**

```bash
# Restart Nginx
sudo systemctl restart nginx

# Restart API (nếu cần)
sudo supervisorctl restart ads-automation-api

# Check status
sudo systemctl status nginx
sudo supervisorctl status
```

---

## 🔍 VERIFY

### **Test từ browser:**

1. **HTTP:** `http://updatemetaads.site/health`
   - Phải redirect về HTTPS

2. **HTTPS:** `https://updatemetaads.site/health`
   - Phải trả về: `{"status":"healthy"}`

3. **API:** `https://updatemetaads.site/api/rules`
   - Phải trả về JSON

### **Test SSL:**

```bash
# Check SSL certificate
openssl s_client -connect updatemetaads.site:443 -servername updatemetaads.site

# Check SSL expiration
echo | openssl s_client -connect updatemetaads.site:443 -servername updatemetaads.site 2>/dev/null | openssl x509 -noout -dates
```

---

## 🔄 AUTO-RENEWAL

**Certbot đã tự động setup auto-renewal!**

### **Test renewal:**

```bash
sudo certbot renew --dry-run
```

### **Check renewal timer:**

```bash
sudo systemctl status certbot.timer
```

---

## 📋 CHECKLIST

- [ ] Install Nginx
- [ ] Install Certbot
- [ ] Configure firewall
- [ ] Verify DNS propagation
- [ ] Configure Nginx
- [ ] Setup SSL certificate
- [ ] Test HTTPS
- [ ] Update `.env` với domain
- [ ] Update Telegram webhook
- [ ] Restart services
- [ ] Verify từ browser

---

## ⚠️ LƯU Ý

1. **DNS Propagation:** Có thể mất 5-60 phút để DNS propagate
2. **Firewall:** Đảm bảo ports 80 và 443 đã mở
3. **Email:** Dùng email thật để nhận thông báo renewal
4. **Auto-renewal:** Certbot tự động renew mỗi 90 ngày
5. **Backup:** Backup file cấu hình Nginx trước khi sửa

---

**Bây giờ hãy bắt đầu setup! 🚀**


