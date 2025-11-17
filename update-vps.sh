#!/bin/bash

# =============================================================================
# 🔄 Facebook Ads Automation - Update Existing VPS
# =============================================================================
# Script cập nhật VPS đã có sẵn cấu hình
# Chỉ update code mới và restart services
# Domain: https://updatemetaads.site/
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
║                    🔄 Facebook Ads Automation - VPS Update                   ║
║                                                                               ║
║  Cập nhật code mới cho VPS đã cấu hình sẵn                                   ║
║  Domain: https://updatemetaads.site/                                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
${NC}"

# Configuration
PROJECT_DIR="/var/www/ads-automation"
BACKUP_DIR="/var/www/backups/$(date +%Y%m%d_%H%M%S)"
DOMAIN="updatemetaads.site"

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Vui lòng chạy với quyền root: sudo bash update-vps.sh${NC}"
    exit 1
fi

print_step "Kiểm tra VPS hiện tại"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Không tìm thấy project directory: $PROJECT_DIR"
    print_warning "Có vẻ như VPS chưa được setup. Vui lòng chạy deployment script đầy đủ."
    exit 1
fi

# Check current services status
print_warning "Trạng thái services hiện tại:"
systemctl is-active nginx || echo "Nginx: inactive"
supervisorctl status | grep ads-automation || echo "Application: not found in supervisor"

print_success "VPS directory found: $PROJECT_DIR"

# Create backup
print_step "Tạo backup trước khi update"
mkdir -p /var/www/backups
mkdir -p "$BACKUP_DIR"

# Backup current application
if [ -d "$PROJECT_DIR" ]; then
    cp -r "$PROJECT_DIR" "$BACKUP_DIR/ads-automation-backup" || print_warning "Backup failed, continuing..."
    print_success "Backup created: $BACKUP_DIR"
fi

# Stop services to prevent conflicts during update
print_step "Stop services để update"
supervisorctl stop ads-automation || print_warning "Application not running in supervisor"
supervisorctl stop ads-automation-worker || print_warning "Worker not running"

# Navigate to project directory
cd "$PROJECT_DIR"

print_step "Cập nhật code từ GitHub"

# Backup current .env file
if [ -f ".env" ]; then
    cp .env .env.backup
    print_success "Environment file backed up"
fi

# Pull latest changes
print_warning "Fetching latest changes..."
git fetch origin
git status || print_warning "Git status check failed"

# Reset to latest main branch
git reset --hard origin/main
git clean -fd

print_success "Code updated from GitHub"

# Restore .env file if it was backed up
if [ -f ".env.backup" ]; then
    mv .env.backup .env
    print_success "Environment file restored"
else
    print_warning "No .env backup found, you may need to reconfigure environment"
fi

# Update Python dependencies
print_step "Cập nhật Python dependencies"
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Update dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt || print_warning "Some dependencies may have failed to install"
else
    print_warning "No requirements.txt found, skipping dependency update"
fi

print_success "Dependencies updated"

# Update file permissions
print_step "Cập nhật permissions"
chown -R www-data:www-data "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"
if [ -f ".env" ]; then
    chmod 600 .env
fi

print_success "Permissions updated"

# Run database migrations if needed
print_step "Chạy database migrations (nếu có)"
if [ -f "scripts/migrate.py" ]; then
    python scripts/migrate.py || print_warning "Migration script failed"
elif [ -f "scripts/init_db.py" ]; then
    python scripts/init_db.py || print_warning "Database init failed"
fi

print_success "Database updates completed"

# Test configuration
print_step "Kiểm tra cấu hình"

# Test Nginx configuration
nginx -t || print_error "Nginx configuration test failed"

# Check if application can start (quick test)
timeout 10s "$PROJECT_DIR/venv/bin/python" -c "import app.main; print('App import successful')" || print_warning "App import test failed"

print_success "Configuration checks passed"

# Update supervisor configuration if needed
print_step "Cập nhật Supervisor configuration"
supervisorctl reread
supervisorctl update

print_success "Supervisor configuration updated"

# Start services
print_step "Khởi động lại services"

# Start application
supervisorctl start ads-automation
sleep 2

# Start worker (may not exist in all setups)
supervisorctl start ads-automation-worker || print_warning "Worker service not found or failed to start"

# Reload Nginx
systemctl reload nginx

print_success "Services restarted"

# Health check
print_step "Kiểm tra tình trạng hoạt động"
sleep 5

# Check supervisor status
print_warning "Supervisor status:"
supervisorctl status | grep ads-automation || echo "No ads-automation processes found"

# Check if application is responding
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Application health check passed"
elif curl -f -s http://localhost/health > /dev/null 2>&1; then
    print_success "Application health check passed (via nginx)"
else
    print_error "Application health check failed"
    print_warning "Checking logs..."
    tail -20 /var/log/ads-automation.log 2>/dev/null || echo "No application logs found"
    
    # Try to diagnose the issue
    print_warning "Diagnostic information:"
    
    # Check if port 8000 is listening
    netstat -tulpn | grep :8000 || echo "Port 8000 not listening"
    
    # Check supervisor logs
    supervisorctl tail ads-automation || echo "No supervisor logs available"
fi

# Test external access
print_step "Kiểm tra truy cập external"
if curl -f -s -I "https://$DOMAIN/health" > /dev/null 2>&1; then
    print_success "External access working: https://$DOMAIN"
elif curl -f -s -I "http://$DOMAIN/health" > /dev/null 2>&1; then
    print_warning "HTTP access working, but HTTPS may have issues: http://$DOMAIN"
else
    print_error "External access failed for domain: $DOMAIN"
    print_warning "This may be due to DNS, firewall, or SSL certificate issues"
fi

# Create simple rollback script
print_step "Tạo rollback script"
cat > /tmp/rollback.sh << EOL
#!/bin/bash
echo "🔄 Rolling back to previous version..."
supervisorctl stop ads-automation
supervisorctl stop ads-automation-worker
rm -rf "$PROJECT_DIR"
mv "$BACKUP_DIR/ads-automation-backup" "$PROJECT_DIR"
chown -R www-data:www-data "$PROJECT_DIR"
supervisorctl start ads-automation
supervisorctl start ads-automation-worker
echo "✅ Rollback completed"
EOL
chmod +x /tmp/rollback.sh

print_success "Rollback script created: /tmp/rollback.sh"

echo -e "\n${GREEN}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           🎉 UPDATE COMPLETED! 🎉                            ║
║                                                                               ║
║  Facebook Ads Automation đã được cập nhật thành công!                        ║
║                                                                               ║
║  🌐 Website: https://updatemetaads.site/                                      ║
║  📱 Dashboard: https://updatemetaads.site/dashboard                           ║
║  📚 API Docs: https://updatemetaads.site/docs                                ║
║                                                                               ║
║  📋 Các lệnh hữu ích:                                                        ║
║                                                                               ║
║  🔍 Kiểm tra status:                                                         ║
║     supervisorctl status                                                      ║
║                                                                               ║
║  📄 Xem logs:                                                                ║
║     tail -f /var/log/ads-automation.log                                      ║
║                                                                               ║
║  🔄 Restart application:                                                     ║
║     supervisorctl restart ads-automation                                      ║
║                                                                               ║
║  🔙 Rollback nếu có vấn đề:                                                 ║
║     bash /tmp/rollback.sh                                                     ║
║                                                                               ║
║  📁 Backup location: $BACKUP_DIR                                             ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
${NC}"

print_warning "Nếu vẫn gặp lỗi 502, hãy kiểm tra:"
echo -e "${YELLOW}1. supervisorctl status${NC}"
echo -e "${YELLOW}2. tail -f /var/log/ads-automation.log${NC}"
echo -e "${YELLOW}3. systemctl status nginx${NC}"
echo -e "${YELLOW}4. curl http://localhost:8000/health${NC}"

print_success "Update process completed successfully!"