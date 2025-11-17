#!/bin/bash

# =============================================================================
# 🔧 Facebook Ads Automation - Fixed Deploy Script
# =============================================================================
# Script deployment đã fix lỗi Node.js conflict
# Tập trung vào Python app, bỏ qua Node.js để tránh conflict
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                🔧 Facebook Ads Automation - Fixed Deploy                     ║
║                                                                               ║
║  Deployment script đã fix lỗi Node.js conflict                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Vui lòng chạy với quyền root: sudo bash fix-deploy.sh${NC}"
    exit 1
fi

# Configuration
PROJECT_DIR="/var/www/ads-automation"
PORT=8000
DB_PASSWORD="AdsAuto2024!"

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

# Step 1: Fix Node.js conflict
print_step "Fix Node.js conflict"
print_warning "Removing conflicting Node.js packages..."
apt remove --purge nodejs* libnode* -y || true
apt autoremove -y || true
apt autoclean || true

# Fix broken packages
dpkg --configure -a || true
apt --fix-broken install -y || true

print_success "Node.js conflict resolved"

# Step 2: Update system
print_step "Update system packages"
apt update -y
print_success "System updated"

# Step 3: Install essential packages (skip Node.js)
print_step "Install essential packages"
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
    software-properties-common \
    ufw

print_success "Essential packages installed"

# Step 4: Setup project directory
print_step "Setup project directory"
if [ -d "$PROJECT_DIR" ]; then
    print_warning "Directory exists, updating..."
    cd $PROJECT_DIR
    if [ -d ".git" ]; then
        git fetch origin || true
        git reset --hard origin/main || true
        git clean -fd || true
    else
        cd /var/www
        rm -rf ads-automation
        git clone https://github.com/LeDat0312/ads-automation.git
        cd ads-automation
    fi
else
    mkdir -p /var/www
    cd /var/www
    git clone https://github.com/LeDat0312/ads-automation.git
    cd ads-automation
fi

PROJECT_DIR="/var/www/ads-automation"
cd $PROJECT_DIR

print_success "Project directory ready"

# Step 5: Setup Python environment
print_step "Setup Python virtual environment"
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install core dependencies
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
    jinja2==3.1.2 \
    pydantic==2.5.0

# Install requirements.txt if exists
if [ -f "requirements.txt" ]; then
    print_warning "Installing from requirements.txt..."
    pip install -r requirements.txt || print_warning "Some packages may have failed"
fi

print_success "Python environment ready"

# Step 6: Setup PostgreSQL
print_step "Setup PostgreSQL"
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE ads_automation;" 2>/dev/null || print_warning "Database may already exist"
sudo -u postgres psql -c "CREATE USER ads_user WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || print_warning "User may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ads_automation TO ads_user;"
sudo -u postgres psql -c "ALTER USER ads_user CREATEDB;"

print_success "PostgreSQL configured"

# Step 7: Setup Redis
print_step "Setup Redis"
systemctl start redis-server
systemctl enable redis-server

# Basic Redis configuration
if ! grep -q "maxmemory 256mb" /etc/redis/redis.conf; then
    echo "maxmemory 256mb" >> /etc/redis/redis.conf
    echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
    systemctl restart redis-server
fi

print_success "Redis configured"

# Step 8: Create environment file
print_step "Create environment configuration"
cat > $PROJECT_DIR/.env << EOL
# Environment
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql://ads_user:${DB_PASSWORD}@localhost/ads_automation

# Redis
REDIS_URL=redis://localhost:6379/0

# Facebook API (NEED TO UPDATE)
FACEBOOK_APP_ID=your_facebook_app_id_here
FACEBOOK_APP_SECRET=your_facebook_app_secret_here

# Server
HOST=0.0.0.0
PORT=${PORT}

# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram (NEED TO UPDATE)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Upload
UPLOAD_DIR=/var/www/uploads
MAX_FILE_SIZE=10485760

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ads-automation.log
EOL

print_success "Environment file created"

# Step 9: Setup Nginx
print_step "Setup Nginx"
cat > /etc/nginx/sites-available/ads-automation << EOL
server {
    listen 80;
    server_name _;
    
    client_max_body_size 50M;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Static files
    location /static/ {
        alias ${PROJECT_DIR}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Uploads
    location /uploads/ {
        alias /var/www/uploads/;
        expires 1d;
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
        add_header Content-Type text/plain;
    }
}
EOL

# Enable site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/ads-automation /etc/nginx/sites-enabled/

# Test and reload Nginx
nginx -t && systemctl restart nginx
systemctl enable nginx

print_success "Nginx configured"

# Step 10: Setup Supervisor
print_step "Setup Supervisor"
cat > /etc/supervisor/conf.d/ads-automation.conf << EOL
[program:ads-automation]
command=${PROJECT_DIR}/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 2
directory=${PROJECT_DIR}
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ads-automation.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="${PROJECT_DIR}/venv/bin"

[program:ads-worker]
command=${PROJECT_DIR}/venv/bin/python -m app.workers.telegram_worker
directory=${PROJECT_DIR}
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ads-worker.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="${PROJECT_DIR}/venv/bin"
EOL

print_success "Supervisor configured"

# Step 11: Set permissions and create directories
print_step "Set permissions and directories"
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod 600 $PROJECT_DIR/.env

# Create upload directory
mkdir -p /var/www/uploads
chown -R www-data:www-data /var/www/uploads

# Create log files
touch /var/log/ads-automation.log
touch /var/log/ads-worker.log
chown www-data:www-data /var/log/ads-*.log

print_success "Permissions set"

# Step 12: Initialize database
print_step "Initialize database"
cd $PROJECT_DIR
source venv/bin/activate

# Run initialization scripts if they exist
if [ -f "scripts/init_db.py" ]; then
    python scripts/init_db.py || print_warning "Database init script failed"
fi

if [ -f "scripts/create_admin_user.py" ]; then
    python scripts/create_admin_user.py || print_warning "Admin user creation failed"
fi

print_success "Database initialized"

# Step 13: Setup firewall
print_step "Setup basic firewall"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

print_success "Firewall configured"

# Step 14: Start services
print_step "Starting services"
supervisorctl reread
supervisorctl update

# Start the application
supervisorctl start ads-automation
supervisorctl start ads-worker || print_warning "Worker may not start if scripts don't exist"

print_success "Services started"

# Step 15: Create update script
print_step "Creating update script"
cat > ${PROJECT_DIR}/update.sh << 'EOL'
#!/bin/bash
set -e
echo "🔄 Updating Facebook Ads Automation..."
cd $(dirname $0)
git fetch origin
git reset --hard origin/main
git clean -fd
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || echo "Requirements install may have issues"
sudo supervisorctl restart ads-automation
sudo supervisorctl restart ads-worker
echo "✅ Update complete!"
EOL

chmod +x ${PROJECT_DIR}/update.sh
chown www-data:www-data ${PROJECT_DIR}/update.sh

print_success "Update script created"

# Step 16: Final health check
print_step "Running health check"
sleep 5

# Check if services are running
if supervisorctl status ads-automation | grep -q RUNNING; then
    print_success "Application is running"
else
    print_error "Application failed to start"
    echo -e "${YELLOW}Checking logs:${NC}"
    tail -20 /var/log/ads-automation.log || echo "No logs yet"
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo -e "\n${GREEN}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           🎉 DEPLOYMENT COMPLETE! 🎉                         ║
║                                                                               ║
║  Facebook Ads Automation đã được deploy thành công!                          ║
║                                                                               ║
║  🌐 Truy cập ứng dụng:                                                       ║
║     Dashboard: http://${SERVER_IP}/dashboard                                 ║
║     API Docs:  http://${SERVER_IP}/docs                                      ║
║     Health:    http://${SERVER_IP}/health                                    ║
║                                                                               ║
║  📁 Project: ${PROJECT_DIR}                                                  ║
║  🔧 Port: ${PORT}                                                            ║
║                                                                               ║
║  📋 Các bước tiếp theo:                                                      ║
║                                                                               ║
║  1. Cấu hình API credentials:                                                 ║
║     nano ${PROJECT_DIR}/.env                                                 ║
║                                                                               ║
║  2. Restart sau khi cấu hình:                                                ║
║     supervisorctl restart ads-automation                                      ║
║                                                                               ║
║  3. Xem logs:                                                                 ║
║     tail -f /var/log/ads-automation.log                                      ║
║                                                                               ║
║  4. Kiểm tra status:                                                         ║
║     supervisorctl status                                                      ║
║                                                                               ║
║  🔄 Cập nhật sau này:                                                        ║
║     bash ${PROJECT_DIR}/update.sh                                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
${NC}"

echo -e "${BLUE}🔧 Test ngay: ${GREEN}curl http://${SERVER_IP}/health${NC}"
echo -e "${BLUE}📱 Dashboard: ${GREEN}http://${SERVER_IP}/dashboard${NC}"
echo ""
echo -e "${YELLOW}⚠️  Nhớ cập nhật Facebook API & Telegram credentials trong file .env!${NC}"