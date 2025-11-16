# 🚀 SETUP AMAZON LIGHTSAIL SERVER - TỪ ĐẦU

## 📋 THÔNG TIN SERVER

- **Provider:** Amazon Lightsail
- **Region:** Singapore
- **Specs:** 2 vCPU, 2GB RAM
- **OS:** Ubuntu 22.04 LTS (recommended)
- **Tool:** MobaXterm

---

## 🔧 BƯỚC 1: TẠO INSTANCE TRÊN LIGHTSAIL

1. **Đăng nhập AWS Lightsail:**
   - Vào https://lightsail.aws.amazon.com
   - Chọn region: **Singapore (ap-southeast-1)**

2. **Tạo Instance:**
   - Click **"Create instance"**
   - **Platform:** Linux/Unix
   - **Blueprint:** Ubuntu 22.04 LTS
   - **Instance plan:** $10/month (2 vCPU, 2GB RAM)
   - **Instance name:** `ads-automation-server`
   - Click **"Create instance"**

3. **Lấy thông tin kết nối:**
   - Sau khi tạo xong, click vào instance
   - Tab **"Connect"** → Copy **SSH command** hoặc dùng **"Connect using SSH"**

---

## 🔌 BƯỚC 2: KẾT NỐI VỚI MOBAXTERM

### **2.1. Tạo SSH Session:**

1. **Mở MobaXterm**
2. **Click "Session"** → **"SSH"**
3. **Điền thông tin:**
   - **Remote host:** `your-instance-ip` (lấy từ Lightsail)
   - **Username:** `ubuntu` (mặc định cho Ubuntu)
   - **Port:** `22`
   - **Advanced SSH settings:**
     - ✅ Use private key: Chọn file `.pem` từ Lightsail (download về máy)
4. **Click "OK"** → Kết nối

### **2.2. Lần đầu kết nối:**

```bash
# MobaXterm sẽ tự động kết nối
# Nếu hỏi "Are you sure you want to continue connecting?" → Yes
```

---

## 🛠️ BƯỚC 3: SETUP CƠ BẢN

### **3.1. Update hệ thống:**

```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Reboot (nếu cần)
sudo reboot
```

### **3.2. Tạo user mới (optional, khuyến nghị):**

```bash
# Tạo user mới
sudo adduser adsuser
sudo usermod -aG sudo adsuser

# Switch sang user mới
su - adsuser
```

### **3.3. Setup SSH key (nếu chưa có):**

```bash
# Tạo SSH key pair (trên máy local)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy public key lên server
# Trong MobaXterm, mở file manager → Upload file ~/.ssh/id_rsa.pub
# Hoặc dùng:
cat ~/.ssh/id_rsa.pub | ssh ubuntu@your-server-ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

---

## 🐍 BƯỚC 4: CÀI ĐẶT PYTHON & DEPENDENCIES

### **4.1. Cài Python 3.11+:**

```bash
# Cài Python 3.11
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# Verify
python3.11 --version
```

### **4.2. Cài PostgreSQL:**

```bash
# Cài PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Tạo database và user
sudo -u postgres psql << EOF
CREATE DATABASE ads_automation;
CREATE USER adsuser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ads_automation TO adsuser;
ALTER USER adsuser CREATEDB;
\q
EOF

# Test connection
psql -U adsuser -d ads_automation -h localhost
```

### **4.3. Cài Redis (cho job queue):**

```bash
# Cài Redis
sudo apt install redis-server -y

# Start service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test
redis-cli ping
# Should return: PONG
```

### **4.4. Cài Nginx (cho reverse proxy):**

```bash
# Cài Nginx
sudo apt install nginx -y

# Start service
sudo systemctl start nginx
sudo systemctl enable nginx

# Test
curl http://localhost
```

### **4.5. Cài các tools khác:**

```bash
# Git
sudo apt install git -y

# Build tools
sudo apt install build-essential -y

# Supervisor (để quản lý processes)
sudo apt install supervisor -y
```

---

## 📁 BƯỚC 5: SETUP PROJECT

### **5.1. Clone hoặc upload code:**

```bash
# Tạo thư mục project
mkdir -p ~/ads-automation
cd ~/ads-automation

# Option 1: Clone từ Git (nếu có)
# git clone https://github.com/your-repo/ads-automation.git .

# Option 2: Upload code qua MobaXterm
# - Mở MobaXterm file manager
# - Kéo thả files vào ~/ads-automation
```

### **5.2. Tạo virtual environment:**

```bash
# Tạo venv
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### **5.3. Install dependencies:**

```bash
# Install từ requirements.txt
pip install -r requirements.txt
```

---

## ⚙️ BƯỚC 6: CẤU HÌNH ENVIRONMENT

### **6.1. Tạo .env file:**

```bash
# Tạo .env
nano .env
```

**Nội dung .env:**

```bash
# Database
DATABASE_URL=postgresql://adsuser:your_secure_password@localhost:5432/ads_automation

# Redis
REDIS_URL=redis://localhost:6379/0

# Facebook API
ACCESS_TOKEN=your_facebook_access_token
AD_ACCOUNT_IDS=act_123456789,act_987654321

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret_key

# Server
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Security
SECRET_KEY=your_secret_key_here_min_32_chars

# Automation
RUN_WINDOW_START_HOUR=6
RUN_WINDOW_END_HOUR=23
DELAY_KHI_TAT_BATCH=1000
DATA_DATE_PRESET=yesterday
```

### **6.2. Set permissions:**

```bash
# Chỉ owner đọc được .env
chmod 600 .env
```

---

## 🗄️ BƯỚC 7: INITIALIZE DATABASE

### **7.1. Run migrations:**

```bash
# Activate venv
source venv/bin/activate

# Initialize database
python scripts/init_db.py

# Hoặc dùng Alembic
alembic upgrade head
```

### **7.2. Verify:**

```bash
# Connect và check tables
psql -U adsuser -d ads_automation -h localhost -c "\dt"
```

---

## 🚀 BƯỚC 8: SETUP SUPERVISOR

### **8.1. Tạo config file:**

```bash
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

**Nội dung:**

```ini
[program:ads-automation-api]
command=/home/ubuntu/ads-automation/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/home/ubuntu/ads-automation
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/ads-automation/api.err.log
stdout_logfile=/var/log/ads-automation/api.out.log
environment=PATH="/home/ubuntu/ads-automation/venv/bin"

[program:ads-automation-worker]
command=/home/ubuntu/ads-automation/venv/bin/python -m app.workers.telegram_worker
directory=/home/ubuntu/ads-automation
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/ads-automation/worker.err.log
stdout_logfile=/var/log/ads-automation/worker.out.log
environment=PATH="/home/ubuntu/ads-automation/venv/bin"
numprocs=2
process_name=%(program_name)s_%(process_num)02d
```

### **8.2. Tạo log directory:**

```bash
sudo mkdir -p /var/log/ads-automation
sudo chown ubuntu:ubuntu /var/log/ads-automation
```

### **8.3. Reload supervisor:**

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ads-automation-api
sudo supervisorctl start ads-automation-worker
```

### **8.4. Check status:**

```bash
sudo supervisorctl status
```

---

## 🌐 BƯỚC 9: SETUP NGINX REVERSE PROXY

### **9.1. Tạo config:**

```bash
sudo nano /etc/nginx/sites-available/ads-automation
```

**Nội dung:**

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Hoặc IP của server

    client_max_body_size 10M;

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

### **9.2. Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/ads-automation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 BƯỚC 10: SETUP FIREWALL

### **10.1. Cấu hình UFW:**

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## ✅ BƯỚC 11: VERIFY SETUP

### **11.1. Test API:**

```bash
# Trong MobaXterm terminal
curl http://localhost:8000/health

# Từ máy local
curl http://your-server-ip/health
```

### **11.2. Test Database:**

```bash
psql -U adsuser -d ads_automation -h localhost -c "SELECT COUNT(*) FROM logic_rules;"
```

### **11.3. Test Redis:**

```bash
redis-cli ping
```

### **11.4. Check logs:**

```bash
# API logs
tail -f /var/log/ads-automation/api.out.log

# Worker logs
tail -f /var/log/ads-automation/worker.out.log

# Supervisor logs
sudo tail -f /var/log/supervisor/supervisord.log
```

---

## 🔄 BƯỚC 12: SETUP SSL (OPTIONAL)

### **12.1. Cài Certbot:**

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### **12.2. Get certificate:**

```bash
sudo certbot --nginx -d your-domain.com
```

---

## 📝 QUICK COMMANDS

```bash
# Restart services
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker

# View logs
tail -f /var/log/ads-automation/api.out.log
tail -f /var/log/ads-automation/worker.out.log

# Check status
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server

# Update code
cd ~/ads-automation
source venv/bin/activate
git pull  # hoặc upload files mới
pip install -r requirements.txt
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker
```

---

## 🎯 HOÀN TẤT!

Server đã sẵn sàng. Tiếp theo:
1. ✅ Test API endpoints
2. ✅ Setup Telegram webhook
3. ✅ Test automation
4. ✅ Monitor logs

---

**Lưu ý:**
- Thay `your_secure_password`, `your_facebook_access_token`, etc. bằng giá trị thực tế
- Backup `.env` file ở nơi an toàn
- Đổi password mặc định của PostgreSQL
- Setup backup database định kỳ

