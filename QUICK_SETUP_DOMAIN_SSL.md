# ⚡ QUICK SETUP DOMAIN & SSL

## 🚀 CÁCH NHANH NHẤT

### **Option 1: Chạy script tự động**

```bash
# Download script
cd ~/ads-automation
wget https://raw.githubusercontent.com/LeDat0312/ads-automation/main/QUICK_SETUP_DOMAIN_SSL.sh
# Hoặc tạo file và copy nội dung từ QUICK_SETUP_DOMAIN_SSL.sh

# Chạy script
chmod +x QUICK_SETUP_DOMAIN_SSL.sh
./QUICK_SETUP_DOMAIN_SSL.sh
```

### **Option 2: Chạy từng lệnh thủ công**

```bash
# 1. Install Nginx & Certbot
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 2. Configure Firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH

# 3. Check DNS
dig updatemetaads.site +short
# Phải trả về: 54.179.208.122

# 4. Create Nginx config
sudo tee /etc/nginx/sites-available/updatemetaads.site > /dev/null << 'EOF'
server {
    listen 80;
    server_name updatemetaads.site www.updatemetaads.site;
    access_log /var/log/nginx/updatemetaads.access.log;
    error_log /var/log/nginx/updatemetaads.error.log;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

# 5. Enable site
sudo ln -s /etc/nginx/sites-available/updatemetaads.site /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 6. Setup SSL
sudo certbot --nginx -d updatemetaads.site -d www.updatemetaads.site

# Chọn:
# - Email: nhập email
# - Agree: Y
# - Redirect: 2 (Redirect HTTP to HTTPS)

# 7. Test
curl https://updatemetaads.site/health
```

---

## 🔧 SAU KHI SETUP SSL

### **1. Update `.env`:**

```bash
cd ~/ads-automation
nano .env
```

**Sửa:**
```env
WEBHOOK_URL=https://updatemetaads.site/api/telegram/webhook
```

### **2. Update Telegram Webhook:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Lấy tokens
BOT_TOKEN=$(python -c "from app.core.config import get_settings; print(get_settings().TELEGRAM_BOT_TOKEN)")
WEBHOOK_SECRET=$(python -c "from app.core.config import get_settings; print(get_settings().TELEGRAM_WEBHOOK_SECRET)")

# Update webhook
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"https://updatemetaads.site/api/telegram/webhook\",
    \"secret_token\": \"${WEBHOOK_SECRET}\"
  }"

# Verify
curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
```

### **3. Restart API:**

```bash
sudo supervisorctl restart ads-automation-api
```

---

## ✅ VERIFY

### **Test từ browser:**

1. **HTTPS:** `https://updatemetaads.site/health`
   - Phải trả về: `{"status":"healthy"}`

2. **API:** `https://updatemetaads.site/api/rules`
   - Phải trả về JSON

3. **SSL:** Click vào icon khóa trong browser
   - Phải hiển thị "Secure" và "Valid"

### **Test từ command line:**

```bash
# Test HTTPS
curl https://updatemetaads.site/health

# Test SSL certificate
openssl s_client -connect updatemetaads.site:443 -servername updatemetaads.site < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

---

## 📋 CHECKLIST

- [ ] Install Nginx & Certbot
- [ ] Configure Firewall
- [ ] Verify DNS propagation
- [ ] Create Nginx config
- [ ] Enable site
- [ ] Setup SSL certificate
- [ ] Test HTTPS
- [ ] Update `.env` với domain
- [ ] Update Telegram webhook
- [ ] Restart API
- [ ] Verify từ browser

---

## ⚠️ LƯU Ý

1. **DNS:** Có thể mất 5-60 phút để DNS propagate
2. **Email:** Dùng email thật để nhận thông báo renewal
3. **Firewall:** Đảm bảo ports 80 và 443 đã mở
4. **Auto-renewal:** Certbot tự động renew mỗi 90 ngày
5. **HTTPS:** Telegram chỉ chấp nhận HTTPS webhook

---

## 🔍 TROUBLESHOOTING

### **Lỗi: "DNS not resolved"**

```bash
# Check DNS
dig updatemetaads.site +short
nslookup updatemetaads.site

# Đợi DNS propagate (5-60 phút)
```

### **Lỗi: "502 Bad Gateway"**

```bash
# Check API
curl http://localhost:8000/health

# Check Supervisor
sudo supervisorctl status

# Restart API
sudo supervisorctl restart ads-automation-api
```

### **Lỗi: "SSL certificate failed"**

```bash
# Check Nginx config
sudo nginx -t

# Check Certbot logs
sudo tail -50 /var/log/letsencrypt/letsencrypt.log

# Retry SSL setup
sudo certbot --nginx -d updatemetaads.site -d www.updatemetaads.site
```

---

**Bây giờ hãy setup domain & SSL! 🚀**


