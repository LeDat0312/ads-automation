#!/bin/bash

# =============================================================================
# 🚀 Facebook Ads Automation - Direct Deploy Script
# =============================================================================
# Deploy trực tiếp từ git clone, không cần raw URLs
# Sử dụng khi GitHub raw URLs chưa sẵn sáng
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   🚀 Facebook Ads Automation - Direct Deploy                 ║
║                                                                               ║
║  Deploy trực tiếp từ GitHub repository                                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝
${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Vui lòng chạy với quyền root: sudo bash direct-deploy.sh${NC}"
    exit 1
fi

# Environment
ENVIRONMENT=${1:-production}
REPO_URL="https://github.com/LeDat0312/ads-automation.git"
PROJECT_DIR="/var/www/ads-automation"
SERVICE_NAME="ads-automation"
PORT=8000

echo -e "${BLUE}📋 Cấu hình deployment:${NC}"
echo -e "${YELLOW}  Environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}  Project Dir: ${PROJECT_DIR}${NC}"
echo -e "${YELLOW}  Port: ${PORT}${NC}"
echo ""

# Function to print step
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Update system packages
print_step "Cập nhật system packages"
apt update -y
apt upgrade -y
print_success "System đã được cập nhật"

# Install essential packages
print_step "Cài đặt các packages cần thiết"
apt install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    git \
    nginx \
    postgresql \
    postgresql-contrib \
    redis-server \
    supervisor \
    curl \
    wget \
    unzip \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    pkg-config \
    software-properties-common

print_success "Packages đã được cài đặt"

# Install Node.js 18
print_step "Cài đặt Node.js 18"
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
print_success "Node.js 18 đã được cài đặt"

# Clone repository
print_step "Clone repository từ GitHub"
if [ -d "$PROJECT_DIR" ]; then
    print_warning "Directory đã tồn tại, cập nhật code"
    cd $PROJECT_DIR
    git fetch origin
    git reset --hard origin/main
    git clean -fd
else
    print_warning "Clone repository mới"
    git clone $REPO_URL $PROJECT_DIR
    cd $PROJECT_DIR
fi

# Set permissions
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
print_success "Repository đã được clone và set permissions"

# Setup Python virtual environment
print_step "Tạo Python virtual environment"
cd $PROJECT_DIR
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install basic requirements
    pip install \
        fastapi==0.104.1 \
        uvicorn[standard]==0.24.0 \
        sqlalchemy==2.0.23 \
        psycopg2-binary==2.9.9 \
        redis==5.0.1 \
        python-multipart==0.0.6 \
        python-jose[cryptography]==3.3.0 \
        passlib[bcrypt]==1.7.4 \
        python-dotenv==1.0.0 \
        requests==2.31.0 \
        aiofiles==23.2.1 \
        jinja2==3.1.2
fi
print_success "Python dependencies đã được cài đặt"

# Setup PostgreSQL
print_step "Cấu hình PostgreSQL"
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE ads_automation;" 2>/dev/null || print_warning "Database có thể đã tồn tại"
sudo -u postgres psql -c "CREATE USER ads_user WITH PASSWORD 'AdsAuto2024!';" 2>/dev/null || print_warning "User có thể đã tồn tại"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ads_automation TO ads_user;"
sudo -u postgres psql -c "ALTER USER ads_user CREATEDB;"
print_success "PostgreSQL đã được cấu hình"

# Setup Redis
print_step "Cấu hình Redis"
systemctl start redis-server
systemctl enable redis-server

# Configure Redis memory
if ! grep -q "maxmemory 256mb" /etc/redis/redis.conf; then
    echo "maxmemory 256mb" >> /etc/redis/redis.conf
    echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
    systemctl restart redis-server
fi
print_success "Redis đã được cấu hình"

# Create environment file
print_step "Tạo file cấu hình môi trường"
cat > $PROJECT_DIR/.env << EOL
# Environment
ENVIRONMENT=${ENVIRONMENT}
DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql://ads_user:AdsAuto2024!@localhost/ads_automation

# Redis
REDIS_URL=redis://localhost:6379/0

# Facebook API (CẦN CẬP NHẬT)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# Server
HOST=0.0.0.0
PORT=${PORT}

# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram (CẦN CẬP NHẬT)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Upload
UPLOAD_DIR=/var/www/uploads
MAX_FILE_SIZE=10485760

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ads-automation.log
EOL

chown www-data:www-data $PROJECT_DIR/.env
chmod 600 $PROJECT_DIR/.env
print_success "File môi trường đã được tạo"

# Initialize database
print_step "Khởi tạo database"
cd $PROJECT_DIR
source venv/bin/activate

# Run database initialization scripts if they exist
if [ -f "scripts/init_db.py" ]; then
    python scripts/init_db.py
    print_success "Database đã được khởi tạo"
else
    print_warning "Không tìm thấy script init_db.py"
fi

# Create admin user if script exists
if [ -f "scripts/create_admin_user.py" ]; then
    python scripts/create_admin_user.py
    print_success "Admin user đã được tạo"
else
    print_warning "Không tìm thấy script create_admin_user.py"
fi

# Setup Nginx
print_step "Cấu hình Nginx"
cat > /etc/nginx/sites-available/ads-automation << EOL
server {
    listen 80;
    server_name _;
    
    client_max_body_size 50M;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Static files
    location /static/ {
        alias ${PROJECT_DIR}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:${PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}
EOL

# Enable site and remove default
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/ads-automation /etc/nginx/sites-enabled/

# Test nginx config
nginx -t
systemctl restart nginx
systemctl enable nginx
print_success "Nginx đã được cấu hình"

# Setup Supervisor
print_step "Cấu hình Supervisor"
cat > /etc/supervisor/conf.d/ads-automation.conf << EOL
[program:ads-automation]
command=${PROJECT_DIR}/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 4
directory=${PROJECT_DIR}
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ads-automation.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="${PROJECT_DIR}/venv/bin"

[program:ads-automation-worker]
command=${PROJECT_DIR}/venv/bin/python -m app.workers.telegram_worker
directory=${PROJECT_DIR}
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ads-automation-worker.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="${PROJECT_DIR}/venv/bin"
EOL

# Create log files with proper permissions
touch /var/log/ads-automation.log
touch /var/log/ads-automation-worker.log
chown www-data:www-data /var/log/ads-automation*.log

supervisorctl reread
supervisorctl update
print_success "Supervisor đã được cấu hình"

# Create update script
print_step "Tạo script cập nhật"
cat > ${PROJECT_DIR}/update.sh << 'EOL'
#!/bin/bash
set -e

echo "🔄 Cập nhật Facebook Ads Automation..."
cd $(dirname $0)

# Pull latest changes
git fetch origin
git reset --hard origin/main
git clean -fd

# Update dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Restart services
sudo supervisorctl restart ads-automation
sudo supervisorctl restart ads-automation-worker

echo "✅ Cập nhật hoàn tất!"
EOL

chmod +x ${PROJECT_DIR}/update.sh
chown www-data:www-data ${PROJECT_DIR}/update.sh
print_success "Script cập nhật đã được tạo"

# Setup firewall
print_step "Cấu hình firewall"
apt install -y ufw
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
print_success "Firewall đã được cấu hình"

# Start services
print_step "Khởi động dịch vụ"
supervisorctl start ads-automation
supervisorctl start ads-automation-worker
systemctl restart nginx

# Check service status
sleep 5
if supervisorctl status ads-automation | grep -q RUNNING; then
    print_success "Service ads-automation đang chạy"
else
    print_error "Lỗi khi khởi động service ads-automation"
    supervisorctl status ads-automation
fi

echo -e "\n${GREEN}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           🎉 DEPLOYMENT HOÀN TẤT! 🎉                         ║
║                                                                               ║
║  Facebook Ads Automation đã được deploy thành công!                          ║
║                                                                               ║
║  🌐 Truy cập ứng dụng tại:                                                   ║
║     http://$(curl -s ifconfig.me)/dashboard                                   ║
║                                                                               ║
║  📁 Vị trí project: ${PROJECT_DIR}                                           ║
║  🔧 Port: ${PORT}                                                            ║
║                                                                               ║
║  📋 Các bước tiếp theo:                                                      ║
║                                                                               ║
║  1. Chỉnh sửa cấu hình:                                                      ║
║     nano ${PROJECT_DIR}/.env                                                 ║
║                                                                               ║
║  2. Cập nhật Facebook API credentials                                         ║
║  3. Cập nhật Telegram Bot credentials                                         ║
║                                                                               ║
║  4. Restart services sau khi cấu hình:                                       ║
║     supervisorctl restart ads-automation                                      ║
║                                                                               ║
║  🔍 Kiểm tra logs:                                                           ║
║     tail -f /var/log/ads-automation.log                                      ║
║                                                                               ║
║  📈 Kiểm tra status:                                                         ║
║     supervisorctl status                                                      ║
║                                                                               ║
║  🔄 Cập nhật sau này:                                                        ║
║     bash ${PROJECT_DIR}/update.sh                                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
${NC}"

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)
echo -e "${BLUE}📱 Truy cập dashboard tại: ${GREEN}http://${SERVER_IP}/dashboard${NC}"
echo -e "${BLUE}📚 API documentation: ${GREEN}http://${SERVER_IP}/docs${NC}"
echo ""
echo -e "${YELLOW}⚠️  Nhớ cập nhật file .env với thông tin thực tế của bạn!${NC}"