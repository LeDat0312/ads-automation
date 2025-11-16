#!/bin/bash

# 🚀 DEPLOYMENT SCRIPT for ADS Automation
# Chạy trên server Ubuntu: bash deploy.sh
# Usage: bash deploy.sh [--backup] [--migrate] [--restart]

set -e  # Exit on error

# ===== CONFIG =====
PROJECT_PATH="/home/adsuser/ads-automation"
VENV_PATH="/home/adsuser/ads-automation/venv"
GITHUB_REPO="https://github.com/LeDat0312/ads-automation.git"
BRANCH="main"
BACKUP_DIR="/home/adsuser/backups"
LOG_FILE="/var/log/ads-automation-deploy.log"

# ===== COLORS =====
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ===== FUNCTIONS =====
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

# ===== MAIN DEPLOYMENT =====

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🚀 ADS Automation Deployment${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 1. Check nếu folder tồn tại
if [ ! -d "$PROJECT_PATH" ]; then
    error "Project path không tồn tại: $PROJECT_PATH"
    exit 1
fi

log "📍 Project path: $PROJECT_PATH"

# 2. Backup (optional)
if [[ "$@" == *"--backup"* ]]; then
    log "💾 Creating backup..."
    BACKUP_NAME="ads-automation-backup-$(date +'%Y%m%d_%H%M%S')"
    mkdir -p "$BACKUP_DIR"
    cp -r "$PROJECT_PATH" "$BACKUP_DIR/$BACKUP_NAME"
    success "Backup created: $BACKUP_DIR/$BACKUP_NAME"
fi

# 3. Pull latest code
log "📥 Pulling latest code from GitHub ($BRANCH)..."
cd "$PROJECT_PATH"
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH
success "Code pulled successfully"

# 4. Activate venv
if [ ! -d "$VENV_PATH" ]; then
    warning "Virtual environment not found. Creating..."
    python3 -m venv "$VENV_PATH"
fi

log "🔌 Activating virtual environment..."
source "$VENV_PATH/bin/activate"
success "Virtual environment activated"

# 5. Install/update dependencies
log "📦 Installing Python dependencies..."
pip install --upgrade pip
if [ -f "$PROJECT_PATH/requirements.txt" ]; then
    pip install -r "$PROJECT_PATH/requirements.txt"
    success "Dependencies installed"
else
    warning "requirements.txt not found"
fi

# 6. Database migration (optional)
if [[ "$@" == *"--migrate"* ]]; then
    log "🗄️  Running database initialization..."
    cd "$PROJECT_PATH"
    python scripts/init_db.py
    success "Database initialized"
fi

# 7. Restart services (optional)
if [[ "$@" == *"--restart"* ]]; then
    log "🔄 Restarting services..."
    
    # Try supervisor first
    if command -v supervisorctl &> /dev/null; then
        log "  - Restarting supervisor services..."
        sudo supervisorctl restart all
        success "Supervisor services restarted"
    fi
    
    # Try systemd services
    if systemctl is-active --quiet ads-automation-api 2>/dev/null; then
        log "  - Restarting ads-automation-api..."
        sudo systemctl restart ads-automation-api
        success "ads-automation-api restarted"
    fi
    
    if systemctl is-active --quiet ads-automation-worker 2>/dev/null; then
        log "  - Restarting ads-automation-worker..."
        sudo systemctl restart ads-automation-worker
        success "ads-automation-worker restarted"
    fi
    
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log "  - Restarting nginx..."
        sudo systemctl restart nginx
        success "nginx restarted"
    fi
fi

# 8. Verify deployment
log "✔️  Verifying deployment..."
cd "$PROJECT_PATH"
python -c "from app.core.config import get_settings; print('✅ App configuration loaded successfully')"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Show usage
echo -e "${BLUE}📝 Usage:${NC}"
echo "  bash deploy.sh                    # Pull code only"
echo "  bash deploy.sh --backup           # Pull code + backup"
echo "  bash deploy.sh --migrate          # Pull code + init database"
echo "  bash deploy.sh --restart          # Pull code + restart services"
echo "  bash deploy.sh --backup --migrate --restart  # Full deployment"
echo ""

# Show logs
echo -e "${BLUE}📋 Deployment log: $LOG_FILE${NC}"
echo ""

log "🎉 Deployment finished at $(date)"
