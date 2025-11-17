# 🔧 Fix Node.js Conflict và Tiếp tục Deployment

## ⚠️ **Sửa lỗi Node.js conflict hiện tại:**

```bash
# 1. Fix lỗi Node.js conflict
sudo apt remove --purge nodejs libnode72 -y
sudo apt autoremove -y
sudo apt autoclean

# 2. Clear APT cache
sudo rm -rf /var/cache/apt/archives/*.deb

# 3. Fix broken packages
sudo dpkg --configure -a
sudo apt --fix-broken install -y

# 4. Tiếp tục deployment (chạy script fix)
sudo bash fixed-deploy.sh
```

---

## 🚀 **Hoặc chạy lệnh đơn giản này:**

```bash
# Chạy trên VPS ngay:
wget -O fix-deploy.sh https://raw.githubusercontent.com/LeDat0312/ads-automation/main/fix-deploy.sh
chmod +x fix-deploy.sh
sudo bash fix-deploy.sh
```

---

## 📋 **Hướng dẫn chi tiết:**

### **Bước 1: Fix Node.js conflict**
```bash
sudo apt remove --purge nodejs libnode72 -y
sudo apt autoremove -y
sudo apt update
```

### **Bước 2: Install Python và dependencies cơ bản**
```bash
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo apt install -y git nginx postgresql redis-server supervisor
sudo apt install -y build-essential libpq-dev libssl-dev libffi-dev
```

### **Bước 3: Skip Node.js và deploy Python app**
```bash
cd /var/www
sudo mkdir -p ads-automation
cd ads-automation
sudo git clone https://github.com/LeDat0312/ads-automation.git .
```

### **Bước 4: Setup Python environment**
```bash
sudo python3.11 -m venv venv
sudo ./venv/bin/pip install --upgrade pip
sudo ./venv/bin/pip install fastapi uvicorn sqlalchemy psycopg2-binary redis python-dotenv
```

### **Bước 5: Quick setup services**
```bash
# PostgreSQL
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE ads_automation;"
sudo -u postgres psql -c "CREATE USER ads_user WITH PASSWORD 'AdsAuto2024!';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ads_automation TO ads_user;"

# Redis
sudo systemctl start redis-server

# Environment
sudo tee /var/www/ads-automation/.env << EOF
DATABASE_URL=postgresql://ads_user:AdsAuto2024!@localhost/ads_automation
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
PORT=8000
EOF
```

### **Bước 6: Setup Nginx**
```bash
sudo tee /etc/nginx/sites-available/ads-automation << EOF
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    location /static/ {
        alias /var/www/ads-automation/static/;
    }
}
EOF

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/ads-automation /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### **Bước 7: Setup Supervisor**
```bash
sudo tee /etc/supervisor/conf.d/ads-automation.conf << EOF
[program:ads-automation]
command=/var/www/ads-automation/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
directory=/var/www/ads-automation
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/ads-automation.log
EOF

sudo chown -R www-data:www-data /var/www/ads-automation
sudo supervisorctl reread && sudo supervisorctl update
sudo supervisorctl start ads-automation
```

---

## ✅ **Kiểm tra sau khi setup:**

```bash
# Check services
sudo supervisorctl status
sudo systemctl status nginx

# Check logs
sudo tail -f /var/log/ads-automation.log

# Test application
curl http://localhost:8000/health
```

---

## 🌐 **Truy cập ứng dụng:**

- **Dashboard**: `http://YOUR-SERVER-IP/dashboard`
- **API Docs**: `http://YOUR-SERVER-IP/docs`
- **Health Check**: `http://YOUR-SERVER-IP/health`

---

## 🔄 **Nếu vẫn có lỗi, chạy lệnh này:**

```bash
# Complete reset và deploy lại
sudo apt remove --purge nodejs* libnode* -y
sudo apt autoremove -y
sudo apt update
cd ~
rm -rf ads-automation
git clone https://github.com/LeDat0312/ads-automation.git
cd ads-automation
sudo bash direct-deploy.sh --skip-nodejs
```