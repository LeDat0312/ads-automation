#!/bin/bash

# =============================================================================
# 🚀 Facebook Ads Automation - VPS Deployment Script
# =============================================================================
# Tự động deploy project từ GitHub lên VPS
# Usage: bash deploy.sh [production|staging]
# Author: GitHub Copilot
# Date: $(date)
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/LeDat0312/ads-automation.git"
PROJECT_NAME="ads-automation"
PYTHON_VERSION="3.11"
NODE_VERSION="18"

# Environment setup
ENVIRONMENT=${1:-production}
if [ "$ENVIRONMENT" = "staging" ]; then
    PROJECT_DIR="/var/www/ads-automation-staging"
    SERVICE_NAME="ads-automation-staging"
    PORT=8001
    DOMAIN="staging-ads.yourdomain.com"
else
    PROJECT_DIR="/var/www/ads-automation"
    SERVICE_NAME="ads-automation"
    PORT=8000
    DOMAIN="ads.yourdomain.com"
fi

echo -e "${PURPLE}
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 Facebook Ads Automation Deployment                    ║
║                                                                              ║
║  Repository: LeDat0312/ads-automation                                        ║
║  Environment: ${ENVIRONMENT}                                                               ║
║  Target: ${PROJECT_DIR}                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
${NC}"

# Function to print step
print_step() {
    echo -e "${BLUE}📋 Step: $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
check_permissions() {
    print_step "Checking permissions"
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root or with sudo"
        exit 1
    fi
    print_success "Running with root permissions"
}

# Install system dependencies
install_system_deps() {
    print_step "Installing system dependencies"
    
    # Update package list
    apt update -y
    
    # Install required packages
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
        pkg-config
    
    # Install Node.js 18
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    apt install -y nodejs
    
    print_success "System dependencies installed"
}

# Setup project directory
setup_project_dir() {
    print_step "Setting up project directory"
    
    # Create project directory
    mkdir -p $PROJECT_DIR
    cd $PROJECT_DIR
    
    # Clone or update repository
    if [ -d ".git" ]; then
        print_warning "Repository exists, pulling latest changes"
        git fetch origin
        git reset --hard origin/main
        git clean -fd
    else
        print_warning "Cloning repository"
        git clone $REPO_URL .
    fi
    
    # Set proper ownership
    chown -R www-data:www-data $PROJECT_DIR
    chmod -R 755 $PROJECT_DIR
    
    print_success "Project directory setup complete"
}

# Setup Python environment
setup_python_env() {
    print_step "Setting up Python virtual environment"
    
    cd $PROJECT_DIR
    
    # Create virtual environment
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        # Install common dependencies if requirements.txt doesn't exist
        pip install \
            fastapi \
            uvicorn[standard] \
            sqlalchemy \
            psycopg2-binary \
            redis \
            python-multipart \
            python-jose[cryptography] \
            passlib[bcrypt] \
            python-dotenv \
            requests \
            aiofiles \
            jinja2
    fi
    
    print_success "Python environment setup complete"
}

# Setup database
setup_database() {
    print_step "Setting up PostgreSQL database"
    
    # Start PostgreSQL service
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql -c "CREATE DATABASE ads_automation;" || print_warning "Database might already exist"
    sudo -u postgres psql -c "CREATE USER ads_user WITH PASSWORD 'your_secure_password';" || print_warning "User might already exist"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ads_automation TO ads_user;"
    sudo -u postgres psql -c "ALTER USER ads_user CREATEDB;"
    
    print_success "Database setup complete"
}

# Setup Redis
setup_redis() {
    print_step "Setting up Redis"
    
    # Start Redis service
    systemctl start redis-server
    systemctl enable redis-server
    
    # Configure Redis
    sed -i 's/# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
    sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
    
    systemctl restart redis-server
    
    print_success "Redis setup complete"
}

# Create environment file
create_env_file() {
    print_step "Creating environment configuration"
    
    cd $PROJECT_DIR
    
    cat > .env << EOL
# Environment
ENVIRONMENT=$ENVIRONMENT
DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql://ads_user:your_secure_password@localhost/ads_automation

# Redis
REDIS_URL=redis://localhost:6379/0

# Facebook API
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# Server
HOST=0.0.0.0
PORT=$PORT

# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# File Upload
UPLOAD_DIR=/var/www/uploads
MAX_FILE_SIZE=10485760

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ads-automation.log
EOL

    chown www-data:www-data .env
    chmod 600 .env
    
    print_success "Environment file created"
    print_warning "Please edit .env file with your actual configuration values"
}

# Database migration
run_migrations() {
    print_step "Running database migrations"
    
    cd $PROJECT_DIR
    source venv/bin/activate
    
    # Create database tables (if using script)
    if [ -f "scripts/init_db.py" ]; then
        python scripts/init_db.py
    fi
    
    # Create admin user (if using script)
    if [ -f "scripts/create_admin_user.py" ]; then
        python scripts/create_admin_user.py
    fi
    
    print_success "Database migrations complete"
}

# Setup Nginx
setup_nginx() {
    print_step "Setting up Nginx"
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Create Nginx config
    cat > /etc/nginx/sites-available/ads-automation-$ENVIRONMENT << EOL
server {
    listen 80;
    server_name $DOMAIN;
    
    client_max_body_size 50M;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Static files
    location /static/ {
        alias $PROJECT_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:$PORT;
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

    # Enable site
    ln -sf /etc/nginx/sites-available/ads-automation-$ENVIRONMENT /etc/nginx/sites-enabled/
    
    # Test Nginx config
    nginx -t
    
    # Reload Nginx
    systemctl reload nginx
    systemctl enable nginx
    
    print_success "Nginx setup complete"
}

# Setup Supervisor
setup_supervisor() {
    print_step "Setting up Supervisor"
    
    # Create supervisor config
    cat > /etc/supervisor/conf.d/ads-automation-$ENVIRONMENT.conf << EOL
[program:ads-automation-$ENVIRONMENT]
command=$PROJECT_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
directory=$PROJECT_DIR
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ads-automation-$ENVIRONMENT.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="$PROJECT_DIR/venv/bin"

[program:ads-automation-worker-$ENVIRONMENT]
command=$PROJECT_DIR/venv/bin/python -m app.workers.telegram_worker
directory=$PROJECT_DIR
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ads-automation-worker-$ENVIRONMENT.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="$PROJECT_DIR/venv/bin"
EOL

    # Reload supervisor
    supervisorctl reread
    supervisorctl update
    
    print_success "Supervisor setup complete"
}

# Setup SSL with Let's Encrypt (optional)
setup_ssl() {
    print_step "Setting up SSL certificate (optional)"
    
    if command -v certbot &> /dev/null; then
        print_warning "Certbot found, you can run: certbot --nginx -d $DOMAIN"
    else
        print_warning "Install certbot for SSL: apt install certbot python3-certbot-nginx"
    fi
}

# Setup firewall
setup_firewall() {
    print_step "Setting up firewall"
    
    # Install ufw if not present
    apt install -y ufw
    
    # Reset firewall
    ufw --force reset
    
    # Default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow essential ports
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Enable firewall
    ufw --force enable
    
    print_success "Firewall setup complete"
}

# Create update script
create_update_script() {
    print_step "Creating update script"
    
    cat > $PROJECT_DIR/update.sh << 'EOL'
#!/bin/bash
set -e

echo "🔄 Updating Facebook Ads Automation..."

cd $(dirname $0)

# Pull latest changes
git fetch origin
git reset --hard origin/main
git clean -fd

# Update Python dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Restart services
sudo supervisorctl restart ads-automation-production
sudo supervisorctl restart ads-automation-worker-production

echo "✅ Update complete!"
EOL

    chmod +x $PROJECT_DIR/update.sh
    chown www-data:www-data $PROJECT_DIR/update.sh
    
    print_success "Update script created at $PROJECT_DIR/update.sh"
}

# Create backup script
create_backup_script() {
    print_step "Creating backup script"
    
    mkdir -p /opt/backups
    
    cat > /opt/backups/backup-ads-automation.sh << EOL
#!/bin/bash
set -e

BACKUP_DIR="/opt/backups"
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="$PROJECT_DIR"

echo "🗄️ Creating backup..."

# Create backup directory
mkdir -p \$BACKUP_DIR/\$TIMESTAMP

# Backup database
sudo -u postgres pg_dump ads_automation > \$BACKUP_DIR/\$TIMESTAMP/database.sql

# Backup project files
tar -czf \$BACKUP_DIR/\$TIMESTAMP/project.tar.gz \$PROJECT_DIR

# Backup environment
cp \$PROJECT_DIR/.env \$BACKUP_DIR/\$TIMESTAMP/

# Keep only last 7 days of backups
find \$BACKUP_DIR -type d -name "202*" -mtime +7 -exec rm -rf {} +

echo "✅ Backup complete: \$BACKUP_DIR/\$TIMESTAMP"
EOL

    chmod +x /opt/backups/backup-ads-automation.sh
    
    # Add to crontab for daily backup at 3 AM
    (crontab -l 2>/dev/null; echo "0 3 * * * /opt/backups/backup-ads-automation.sh") | crontab -
    
    print_success "Backup script created with daily cron job"
}

# Main deployment function
main() {
    echo -e "${PURPLE}Starting deployment process...${NC}\n"
    
    check_permissions
    install_system_deps
    setup_project_dir
    setup_python_env
    setup_database
    setup_redis
    create_env_file
    run_migrations
    setup_nginx
    setup_supervisor
    setup_firewall
    create_update_script
    create_backup_script
    
    echo -e "\n${GREEN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🎉 DEPLOYMENT COMPLETE! 🎉                        ║
║                                                                              ║
║  Your Facebook Ads Automation system is now running on:                     ║
║                                                                              ║
║  🌐 URL: http://$DOMAIN                                        ║
║  📁 Path: $PROJECT_DIR                                           ║
║  🔧 Port: $PORT                                                              ║
║                                                                              ║
║  📋 Next Steps:                                                              ║
║  1. Edit .env file: nano $PROJECT_DIR/.env                       ║
║  2. Setup SSL: certbot --nginx -d $DOMAIN                       ║
║  3. Check logs: tail -f /var/log/ads-automation-$ENVIRONMENT.log             ║
║  4. Update: bash $PROJECT_DIR/update.sh                          ║
║                                                                              ║
║  🔍 Useful Commands:                                                         ║
║  • supervisorctl status                                                      ║
║  • supervisorctl restart ads-automation-$ENVIRONMENT                        ║
║  • nginx -t && systemctl reload nginx                                       ║
║  • /opt/backups/backup-ads-automation.sh                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
${NC}"
}

# Run main function
main "$@"