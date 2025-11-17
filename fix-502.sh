#!/bin/bash

# =============================================================================
# 🔧 Fix 502 Bad Gateway for updatemetaads.site
# =============================================================================
# Script khắc phục lỗi 502 Bad Gateway nginx
# Kiểm tra và sửa các vấn đề thường gặp
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
║                    🔧 Fix 502 Bad Gateway Error                              ║
║                                                                               ║
║  Khắc phục lỗi 502 cho updatemetaads.site                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
${NC}"

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
    echo -e "${RED}❌ Vui lòng chạy với quyền root: sudo bash fix-502.sh${NC}"
    exit 1
fi

PROJECT_DIR="/var/www/ads-automation"

print_step "Chẩn đoán nguyên nhân lỗi 502"

# Check 1: Nginx status
print_warning "1. Kiểm tra Nginx status:"
if systemctl is-active --quiet nginx; then
    print_success "Nginx đang chạy"
else
    print_error "Nginx không chạy"
    echo "Đang khởi động Nginx..."
    systemctl start nginx
    systemctl enable nginx
fi

# Check 2: Application status in Supervisor
print_warning "2. Kiểm tra Application status:"
SUPERVISOR_STATUS=$(supervisorctl status | grep ads-automation || echo "NOT_FOUND")
echo "$SUPERVISOR_STATUS"

if echo "$SUPERVISOR_STATUS" | grep -q "RUNNING"; then
    print_success "Application đang chạy trong supervisor"
else
    print_error "Application không chạy hoặc không có trong supervisor"
    
    # Try to start the application
    print_warning "Đang cố gắng khởi động application..."
    supervisorctl start ads-automation || print_error "Không thể start application"
fi

# Check 3: Port 8000 listening
print_warning "3. Kiểm tra port 8000:"
if netstat -tulpn | grep -q ":8000"; then
    print_success "Port 8000 đang listen"
    netstat -tulpn | grep ":8000"
else
    print_error "Port 8000 không listen"
    
    # Check if project directory exists
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Cố gắng khởi động application thủ công..."
        cd "$PROJECT_DIR"
        
        # Check if venv exists
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
            
            # Try to start application manually for testing
            print_warning "Test start application..."
            timeout 10s python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
            sleep 3
            
            if netstat -tulpn | grep -q ":8000"; then
                print_success "Application có thể start được"
                # Kill the test process
                pkill -f "uvicorn app.main:app" || true
            else
                print_error "Application không thể start"
                # Check for errors
                python -c "import app.main; print('Import OK')" || print_error "Có lỗi import"
            fi
        else
            print_error "Không tìm thấy Python virtual environment"
        fi
    else
        print_error "Không tìm thấy project directory: $PROJECT_DIR"
    fi
fi

# Check 4: Nginx configuration
print_warning "4. Kiểm tra Nginx configuration:"
nginx -t || print_error "Nginx configuration có lỗi"

# Check 5: Application logs
print_warning "5. Kiểm tra Application logs (20 dòng cuối):"
if [ -f "/var/log/ads-automation.log" ]; then
    tail -20 /var/log/ads-automation.log
else
    print_error "Không tìm thấy log file: /var/log/ads-automation.log"
fi

# Check 6: Supervisor logs
print_warning "6. Kiểm tra Supervisor logs:"
supervisorctl tail ads-automation 2>/dev/null || print_error "Không thể đọc supervisor logs"

# Check 7: Environment file
print_warning "7. Kiểm tra Environment configuration:"
if [ -f "$PROJECT_DIR/.env" ]; then
    print_success "File .env tồn tại"
    # Check some important variables without revealing secrets
    if grep -q "DATABASE_URL" "$PROJECT_DIR/.env"; then
        print_success "DATABASE_URL được cấu hình"
    else
        print_error "DATABASE_URL không được cấu hình"
    fi
else
    print_error "Không tìm thấy file .env"
fi

# Quick fix attempts
print_step "Thử các giải pháp nhanh"

print_warning "Fix 1: Restart tất cả services"
supervisorctl stop ads-automation || true
sleep 2
supervisorctl start ads-automation
sleep 3
systemctl reload nginx

print_warning "Fix 2: Kiểm tra lại port 8000"
if netstat -tulpn | grep -q ":8000"; then
    print_success "Port 8000 đang hoạt động"
else
    print_warning "Port 8000 vẫn không hoạt động, thử cách khác..."
    
    # Force kill any process on port 8000
    fuser -k 8000/tcp 2>/dev/null || true
    sleep 2
    
    # Restart supervisor completely
    systemctl restart supervisor
    sleep 5
    supervisorctl start ads-automation
fi

print_warning "Fix 3: Test application trực tiếp"
cd "$PROJECT_DIR"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    
    # Quick health check
    timeout 5s python -c "
from app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get('/health')
print(f'Health check: {response.status_code}')
" 2>/dev/null && print_success "Application health check OK" || print_error "Application health check failed"
fi

# Final status check
print_step "Kiểm tra trạng thái cuối cùng"

print_warning "Services status:"
systemctl is-active nginx && echo "✅ Nginx: RUNNING" || echo "❌ Nginx: STOPPED"
supervisorctl status | grep ads-automation || echo "❌ Application: NOT FOUND"

print_warning "Port check:"
netstat -tulpn | grep ":8000" && echo "✅ Port 8000: LISTENING" || echo "❌ Port 8000: NOT LISTENING"

print_warning "HTTP test:"
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Local HTTP: OK"
elif curl -f -s http://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx proxy: OK"
else
    echo "❌ HTTP test: FAILED"
fi

echo -e "\n${BLUE}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           📋 DIAGNOSTIC SUMMARY                              ║
║                                                                               ║
║  Nếu vẫn gặp lỗi 502, các bước tiếp theo:                                   ║
║                                                                               ║
║  1. Kiểm tra chi tiết logs:                                                  ║
║     tail -f /var/log/ads-automation.log                                      ║
║     tail -f /var/log/nginx/error.log                                         ║
║                                                                               ║
║  2. Restart toàn bộ hệ thống:                                                ║
║     systemctl restart supervisor                                             ║
║     systemctl restart nginx                                                  ║
║                                                                               ║
║  3. Kiểm tra cấu hình môi trường:                                            ║
║     nano $PROJECT_DIR/.env                                                   ║
║                                                                               ║
║  4. Chạy application thủ công để debug:                                      ║
║     cd $PROJECT_DIR && source venv/bin/activate                              ║
║     uvicorn app.main:app --host 0.0.0.0 --port 8000                         ║
║                                                                               ║
║  5. Nếu cần rebuild hoàn toàn:                                               ║
║     bash update-vps.sh                                                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
${NC}"