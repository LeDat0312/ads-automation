# 📦 VPS Deployment Guide

## 🚀 **Hướng dẫn Deploy lên VPS**

### **Option 1: Quick Deploy (Recommended)**
```bash
# Download và chạy script tự động
curl -sSL https://raw.githubusercontent.com/LeDat0312/ads-automation/main/quick-deploy.sh | sudo bash
```

### **Option 2: Manual Deploy** 
```bash
# Download deployment script
wget https://raw.githubusercontent.com/LeDat0312/ads-automation/main/deploy.sh
chmod +x deploy.sh

# Chạy deployment
sudo ./deploy.sh production
```

### **Option 3: Clone và Deploy thủ công**
```bash
# Clone repository
git clone https://github.com/LeDat0312/ads-automation.git
cd ads-automation

# Chạy deploy script
sudo bash deploy.sh production
```

---

## ⚙️ **System Requirements**

- **OS**: Ubuntu 20.04+ / Debian 11+
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 20GB minimum
- **Network**: Public IP address
- **Domain**: Optional (có thể dùng IP)

---

## 📋 **Sau khi Deploy xong**

### **1. Cấu hình Environment**
```bash
sudo nano /var/www/ads-automation/.env
```

Cập nhật các thông tin:
```env
# Database
DATABASE_URL=postgresql://ads_user:YOUR_PASSWORD@localhost/ads_automation

# Facebook API
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Domain
DOMAIN=your-domain.com
```

### **2. Restart Services**
```bash
sudo supervisorctl restart ads-automation-production
sudo systemctl reload nginx
```

### **3. Setup SSL (Optional)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔧 **Useful Commands**

### **Service Management**
```bash
# Check status
sudo supervisorctl status

# Restart application
sudo supervisorctl restart ads-automation-production

# Check logs
sudo tail -f /var/log/ads-automation-production.log

# Nginx status
sudo systemctl status nginx
```

### **Updates**
```bash
# Update to latest version
cd /var/www/ads-automation
sudo bash update.sh
```

### **Backup**
```bash
# Manual backup
sudo /opt/backups/backup-ads-automation.sh

# Check backups
ls -la /opt/backups/
```

---

## 🌐 **Access URLs**

- **Dashboard**: `http://your-server-ip/dashboard`
- **API Docs**: `http://your-server-ip/docs`
- **Admin**: `http://your-server-ip/admin`
- **Health Check**: `http://your-server-ip/health`

---

## 🔍 **Troubleshooting**

### **Check if services are running:**
```bash
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server
```

### **Check logs:**
```bash
# Application logs
sudo tail -f /var/log/ads-automation-production.log

# Nginx logs
sudo tail -f /var/nginx/error.log

# System logs
sudo journalctl -f -u ads-automation-production
```

### **Common Issues:**

**1. Port already in use:**
```bash
sudo netstat -tulpn | grep :8000
sudo kill -9 <PID>
```

**2. Permission issues:**
```bash
sudo chown -R www-data:www-data /var/www/ads-automation
sudo chmod -R 755 /var/www/ads-automation
```

**3. Database connection:**
```bash
sudo -u postgres psql -c "\l"  # List databases
sudo -u postgres psql ads_automation -c "\dt"  # List tables
```

---

## 🔄 **CI/CD Setup (Optional)**

### **GitHub Actions Deploy**
Tạo file `.github/workflows/deploy.yml`:

```yaml
name: Deploy to VPS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.KEY }}
          script: |
            cd /var/www/ads-automation
            sudo bash update.sh
```

---

## 📊 **Monitoring Setup**

### **Setup log rotation:**
```bash
sudo nano /etc/logrotate.d/ads-automation
```

```
/var/log/ads-automation*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
```

### **Setup monitoring:**
```bash
# Install htop for monitoring
sudo apt install htop

# Monitor system resources
htop

# Monitor application
sudo supervisorctl tail -f ads-automation-production
```

---

## 🔒 **Security**

### **Firewall rules:**
```bash
sudo ufw status
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### **Fail2ban (optional):**
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

---

## 📞 **Support**

Nếu gặp vấn đề, hãy:

1. Check logs trước: `/var/log/ads-automation-production.log`
2. Restart services: `sudo supervisorctl restart ads-automation-production`
3. Check system resources: `htop`, `df -h`
4. Backup trước khi sửa: `/opt/backups/backup-ads-automation.sh`

**Liên hệ hỗ trợ:** 
- GitHub Issues: https://github.com/LeDat0312/ads-automation/issues
- Email: support@yourdomain.com