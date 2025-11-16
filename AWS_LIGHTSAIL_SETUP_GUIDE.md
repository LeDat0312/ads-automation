# 🚀 AWS LIGHTSAIL SETUP GUIDE - HƯỚNG DẪN CHI TIẾT

## 📊 ĐÁNH GIÁ CẤU HÌNH CỦA BẠN

### **✅ CẤU HÌNH HIỆN TẠI:**
- **RAM:** 2GB
- **vCPU:** 2 cores
- **SSD:** 60GB
- **OS:** Ubuntu 22.04 LTS
- **Provider:** Amazon Lightsail

### **🎯 ĐÁNH GIÁ:**

#### **✅ ĐỦ CHO:**
- ✅ Development/Testing
- ✅ Small production (ít traffic)
- ✅ Python + FastAPI + PostgreSQL (nhẹ)
- ✅ Telegram Bot
- ✅ Dashboard Overview

#### **⚠️ CẦN LƯU Ý:**
- ⚠️ **RAM 2GB:** Hơi ít cho production lớn
  - PostgreSQL: ~500MB
  - Python/FastAPI: ~200-300MB
  - Nginx: ~50MB
  - System: ~500MB
  - **Còn lại:** ~700MB (có thể đủ nhưng hơi chật)
  
- ⚠️ **Nên upgrade nếu:**
  - Traffic cao (>1000 requests/phút)
  - Nhiều concurrent users
  - Cần cache (Redis)
  - Cần background jobs

#### **💡 KHUYẾN NGHỊ:**
- **Hiện tại:** Đủ cho bắt đầu và testing
- **Sau 1-2 tháng:** Nên upgrade lên 4GB RAM nếu traffic tăng
- **Cost:** Lightsail 4GB RAM = $20/tháng (rẻ hơn EC2)

---

## 🎯 SO SÁNH VỚI KHUYẾN NGHỊ

| Thông số | Khuyến nghị | Của bạn | Đánh giá |
|----------|-------------|---------|----------|
| **RAM** | 4GB | 2GB | ⚠️ Hơi ít |
| **CPU** | 2 cores | 2 cores | ✅ Đủ |
| **SSD** | 50GB | 60GB | ✅ Đủ |
| **OS** | Ubuntu 22.04 | Ubuntu 22.04 | ✅ Perfect |

**Kết luận:** Cấu hình của bạn **ĐỦ** để bắt đầu, nhưng nên **monitor RAM usage** và upgrade nếu cần.

---

## 🚀 HƯỚNG DẪN SETUP AWS LIGHTSAIL

### **BƯỚC 1: KẾT NỐI VPS**

#### **1.1. Lấy SSH Key từ Lightsail:**

1. Vào AWS Lightsail Console
2. Chọn instance của bạn
3. Click "Connect using SSH" (hoặc "Account" → "SSH keys")
4. Download SSH key (.pem file)

#### **1.2. Kết nối SSH với MobaXterm:**

**Trong MobaXterm:**
1. Click "Session" → "New session"
2. Chọn "SSH"
3. Remote host: `your-lightsail-ip`
4. Username: `ubuntu` (mặc định của Lightsail)
5. **Chọn "Use private key"** và chọn file `.pem` key
6. Click "OK"
7. Login thành công

---

### **BƯỚC 2: SETUP VPS CƠ BẢN**

#### **2.1. Update hệ thống:**

```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git build-essential
```

#### **2.2. Setup Firewall:**

**Lightsail Firewall (trong Console):**
- Vào Lightsail Console
- Chọn instance → "Networking" tab
- Add rules:
  - SSH (22) - từ IP của bạn (hoặc từ mọi nơi)
  - HTTP (80) - từ mọi nơi
  - HTTPS (443) - từ mọi nơi

**UFW (trên VPS):**
```bash
# Install UFW
sudo apt install ufw -y

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

#### **2.3. Tạo User Mới (Không dùng ubuntu user trực tiếp):**

```bash
# Tạo user mới (ví dụ: metaupdateads)
sudo adduser metaupdateads

# Hệ thống sẽ hỏi:
# - Password: Nhập password mới
# - Retype password: Nhập lại password
# - Các thông tin khác: Có thể bỏ qua (Enter)

# Thêm user vào sudo group
sudo usermod -aG sudo metaupdateads

# Verify
groups metaupdateads
# Kết quả: metaupdateads : metaupdateads sudo

# Test
su - metaupdateads
sudo whoami
# Kết quả: root
```

**⚠️ LƯU Ý:** 
- User `ubuntu` có quyền sudo sẵn, có thể dùng để thêm user khác vào sudo group
- Sau khi tạo user mới, logout và login lại với user mới

---

### **BƯỚC 3: INSTALL PYTHON 3.11+**

#### **3.1. Install Python:**

```bash
# Install dependencies
sudo apt install software-properties-common -y

# Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y

# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev python3.11-distutils -y

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Verify installation
python3.11 --version
pip3.11 --version
```

#### **3.2. Setup Python Virtual Environment:**

```bash
# Create project directory
mkdir -p ~/projects/facebook-ads-automation
cd ~/projects/facebook-ads-automation

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install basic packages
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary pydantic python-dotenv
```

---

### **BƯỚC 4: INSTALL POSTGRESQL (Tối ưu cho 2GB RAM)**

#### **4.1. Install PostgreSQL:**

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL
sudo systemctl start postgresql

# Enable PostgreSQL (start on boot)
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

#### **4.2. Tối ưu PostgreSQL cho 2GB RAM:**

**⚠️ QUAN TRỌNG:** File config cần quyền root/sudo, **KHÔNG THỂ** edit trực tiếp từ GUI editor của MobaXterm.

**CÁCH 1: Dùng sed để sửa tự động (KHUYẾN NGHỊ - NHANH NHẤT):**

```bash
# Backup file config
sudo cp /etc/postgresql/14/main/postgresql.conf /etc/postgresql/14/main/postgresql.conf.backup

# Thêm các config tối ưu vào cuối file
sudo sh -c 'echo "" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "# Custom settings for 2GB RAM" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "shared_buffers = 512MB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "effective_cache_size = 1GB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "maintenance_work_mem = 128MB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "work_mem = 10MB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "max_connections = 50" >> /etc/postgresql/14/main/postgresql.conf'

# Verify
sudo tail -10 /etc/postgresql/14/main/postgresql.conf

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check status
sudo systemctl status postgresql
```

**CÁCH 2: Dùng nano trong terminal:**

```bash
# Edit file với sudo nano (trong terminal MobaXterm, KHÔNG dùng GUI editor)
sudo nano /etc/postgresql/14/main/postgresql.conf

# Trong nano:
# 1. Nhấn Ctrl+W để search
# 2. Tìm và sửa các dòng sau (bỏ comment # và sửa giá trị):
#    - shared_buffers = 512MB
#    - effective_cache_size = 1GB
#    - maintenance_work_mem = 128MB
#    - work_mem = 10MB
#    - max_connections = 50
# 3. Save: Ctrl+O, Enter
# 4. Exit: Ctrl+X

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**CÁCH 3: Uncomment và sửa các dòng hiện có:**

```bash
# Uncomment và sửa shared_buffers
sudo sed -i 's/^#shared_buffers = 128MB/shared_buffers = 512MB/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^shared_buffers = 128MB/shared_buffers = 512MB/' /etc/postgresql/14/main/postgresql.conf

# Uncomment và sửa effective_cache_size
sudo sed -i 's/^#effective_cache_size = 4GB/effective_cache_size = 1GB/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^effective_cache_size = 4GB/effective_cache_size = 1GB/' /etc/postgresql/14/main/postgresql.conf

# Uncomment và sửa maintenance_work_mem
sudo sed -i 's/^#maintenance_work_mem = 64MB/maintenance_work_mem = 128MB/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^maintenance_work_mem = 64MB/maintenance_work_mem = 128MB/' /etc/postgresql/14/main/postgresql.conf

# Uncomment và sửa work_mem
sudo sed -i 's/^#work_mem = 4MB/work_mem = 10MB/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^work_mem = 4MB/work_mem = 10MB/' /etc/postgresql/14/main/postgresql.conf

# Uncomment và sửa max_connections
sudo sed -i 's/^#max_connections = 100/max_connections = 50/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^max_connections = 100/max_connections = 50/' /etc/postgresql/14/main/postgresql.conf

# Verify
sudo grep -E "shared_buffers|effective_cache_size|maintenance_work_mem|work_mem|max_connections" /etc/postgresql/14/main/postgresql.conf | grep -v "^#"

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### **4.3. Verify PostgreSQL Config:**

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Check config
SHOW shared_buffers;
SHOW effective_cache_size;
SHOW maintenance_work_mem;
SHOW work_mem;
SHOW max_connections;

# Exit
\q
```

#### **4.4. Setup Database:**

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE facebook_ads_db;

# Create user
CREATE USER fbads_user WITH PASSWORD 'your_secure_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE facebook_ads_db TO fbads_user;

# Exit PostgreSQL
\q
```

---

### **BƯỚC 5: INSTALL DOCKER (Optional - nếu dùng Docker)**

#### **5.1. Install Docker:**

```bash
# Install dependencies
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release -y

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list
sudo apt update

# Install Docker
sudo apt install docker-ce docker-ce-cli containerd.io -y

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
exit
ssh -i your-key.pem your-username@your-lightsail-ip

# Test Docker
docker run hello-world
```

#### **5.2. Install Docker Compose:**

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

---

### **BƯỚC 6: INSTALL NGINX**

#### **6.1. Install Nginx:**

```bash
# Install Nginx
sudo apt install nginx -y

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

#### **6.2. Configure Nginx:**

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/facebook-ads-api

# Add configuration:
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Increase timeouts for long-running requests
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;

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

    # Static files (nếu có)
    location /static {
        alias /path/to/static/files;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/facebook-ads-api /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

### **BƯỚC 7: SETUP SSL (LET'S ENCRYPT)**

#### **7.1. Install Certbot:**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test renewal
sudo certbot renew --dry-run
```

---

### **BƯỚC 8: SETUP SYSTEMD SERVICE (Chạy FastAPI app)**

#### **8.1. Create Systemd Service:**

```bash
# Create service file
sudo nano /etc/systemd/system/facebook-ads-api.service

# Add configuration:
[Unit]
Description=Facebook Ads Automation API
After=network.target postgresql.service

[Service]
Type=simple
User=metaupdateads
WorkingDirectory=/home/metaupdateads/projects/facebook-ads-automation
Environment="PATH=/home/metaupdateads/projects/facebook-ads-automation/venv/bin"
ExecStart=/home/metaupdateads/projects/facebook-ads-automation/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start facebook-ads-api

# Enable service (start on boot)
sudo systemctl enable facebook-ads-api

# Check status
sudo systemctl status facebook-ads-api

# View logs
sudo journalctl -u facebook-ads-api -f
```

---

### **BƯỚC 9: MONITOR RAM USAGE**

#### **9.1. Install Monitoring Tools:**

```bash
# Install htop
sudo apt install htop -y

# Install monitoring script
sudo apt install sysstat -y

# Check RAM usage
free -h

# Check processes using RAM
ps aux --sort=-%mem | head -10
```

#### **9.2. Setup Swap (Nếu RAM hết):**

```bash
# Check current swap
swapon --show

# Create swap file (2GB)
sudo fallocate -l 2G /swapfile

# Set permissions
sudo chmod 600 /swapfile

# Setup swap
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
swapon --show
```

---

## 📊 TỐI ƯU CHO 2GB RAM

### **1. PostgreSQL:**
```bash
# /etc/postgresql/14/main/postgresql.conf
shared_buffers = 512MB          # 25% của RAM
effective_cache_size = 1GB      # 50% của RAM
maintenance_work_mem = 128MB    # Cho maintenance
work_mem = 10MB                 # Per connection
max_connections = 50            # Giảm connections để tiết kiệm RAM
```

### **2. Python/FastAPI:**
```bash
# Sử dụng workers = 1 (không dùng multiple workers)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

### **3. Nginx:**
```nginx
# /etc/nginx/nginx.conf
worker_processes 1;  # Số CPU cores
worker_connections 512;  # Giảm connections
```

### **4. System:**
```bash
# Disable unnecessary services
sudo systemctl disable snapd
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

---

## 🔒 SECURITY SETUP

### **1. Lightsail Firewall:**
- Vào Lightsail Console
- Instance → Networking
- Add rules:
  - SSH (22) - từ IP của bạn (hoặc từ mọi nơi)
  - HTTP (80) - từ mọi nơi
  - HTTPS (443) - từ mọi nơi

### **2. Fail2Ban:**
```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Start Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

# Check status
sudo systemctl status fail2ban
```

### **3. Automatic Updates:**
```bash
# Install unattended-upgrades
sudo apt install unattended-upgrades -y

# Enable automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades
```

### **4. SSH Security:**
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Sửa các dòng sau:
# PermitRootLogin no                # Không cho root login
# PasswordAuthentication yes        # Cho phép password (nếu cần)
# PubkeyAuthentication yes          # Cho phép key

# Restart SSH
sudo systemctl restart sshd
```

---

## 📋 CHECKLIST SETUP

### **✅ SAU KHI SETUP XONG:**

- [ ] Đã SSH vào Lightsail thành công
- [ ] Đã update hệ thống
- [ ] Đã setup firewall (UFW + Lightsail)
- [ ] Đã tạo user mới (metaupdateads)
- [ ] Đã thêm user vào sudo group
- [ ] Đã install Python 3.11+
- [ ] Đã install PostgreSQL
- [ ] Đã tối ưu PostgreSQL config (2GB RAM)
- [ ] Đã setup PostgreSQL database
- [ ] Đã install Docker (nếu cần)
- [ ] Đã install Nginx
- [ ] Đã setup Nginx reverse proxy
- [ ] Đã setup SSL (Let's Encrypt)
- [ ] Đã setup Systemd service
- [ ] Đã setup monitoring
- [ ] Đã setup swap (nếu cần)
- [ ] Đã test tất cả services

---

## 🚨 TROUBLESHOOTING

### **Lỗi: "Permission denied" khi edit PostgreSQL config**

**Nguyên nhân:** File config thuộc về root/postgres, cần quyền sudo

**Giải pháp:**
```bash
# KHÔNG dùng GUI editor của MobaXterm
# Dùng terminal với sudo:
sudo nano /etc/postgresql/14/main/postgresql.conf

# Hoặc dùng sed để sửa tự động:
sudo sh -c 'echo "shared_buffers = 512MB" >> /etc/postgresql/14/main/postgresql.conf'
```

### **Lỗi: "PostgreSQL failed to start"**

**Nguyên nhân:** Config có lỗi syntax

**Giải pháp:**
```bash
# Restore backup
sudo cp /etc/postgresql/14/main/postgresql.conf.backup /etc/postgresql/14/main/postgresql.conf

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check logs
sudo journalctl -u postgresql -n 50
```

### **Lỗi: "usermod: Permission denied"**

**Nguyên nhân:** User không có quyền sudo

**Giải pháp:**
```bash
# Login với user ubuntu (có quyền sudo)
ssh ubuntu@your-lightsail-ip

# Thêm user vào sudo group
sudo usermod -aG sudo metaupdateads
```

---

## 💰 COST ESTIMATION

### **AWS LIGHTSAIL:**
- **2GB RAM, 2 vCPU, 60GB SSD:** $10/tháng
- **4GB RAM, 2 vCPU, 80GB SSD:** $20/tháng (nếu upgrade)
- **Domain:** $10-15/năm
- **SSL:** Free (Let's Encrypt)
- **Total:** $10/tháng + $10-15/năm

---

## 🎯 KẾT LUẬN

### **CẤU HÌNH CỦA BẠN:**
- ✅ **ĐỦ** để bắt đầu và testing
- ⚠️ **CẦN MONITOR** RAM usage
- 💡 **NÊN UPGRADE** lên 4GB RAM nếu traffic tăng

### **KHUYẾN NGHỊ:**
1. **Bắt đầu với 2GB RAM** - đủ cho development
2. **Monitor RAM usage** trong 1-2 tuần
3. **Upgrade lên 4GB** nếu RAM usage > 80%
4. **Tối ưu code** để giảm RAM usage

---

## 📚 TÀI LIỆU THAM KHẢO

- [AWS Lightsail Documentation](https://lightsail.aws.amazon.com/ls/docs/)
- [PostgreSQL Configuration](https://www.postgresql.org/docs/current/runtime-config.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)

---

**Chúc bạn setup thành công! 🚀**


