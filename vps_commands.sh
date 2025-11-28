#!/bin/bash
# Quick commands for VPS management

# Check running processes
check_processes() {
    echo "🔍 Checking running processes..."
    ps aux | grep -E "uvicorn|ad_studio_publisher" | grep -v grep
}

# View logs
view_logs() {
    echo "📝 Recent uvicorn logs:"
    tail -30 /home/adsuser/ads-automation/uvicorn.log
    echo ""
    echo "📝 Recent worker logs:"
    tail -30 /home/adsuser/ads-automation/worker.log
}

# Restart all services
restart_all() {
    echo "🔄 Restarting all services..."
    cd /home/adsuser/ads-automation
    pkill -f "uvicorn app.main:app" || true
    pkill -f "app.workers.ad_studio_publisher" || true
    sleep 2
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
    sleep 2
    nohup python3 -m app.workers.ad_studio_publisher > worker.log 2>&1 &
    echo "✅ Services restarted"
}

# Stop all services
stop_all() {
    echo "🛑 Stopping all services..."
    pkill -f "uvicorn app.main:app" || true
    pkill -f "app.workers.ad_studio_publisher" || true
    echo "✅ Services stopped"
}

# Check media files
check_media() {
    echo "📁 Media directory status:"
    ls -lh /home/adsuser/ads-automation/media/ad_studio/ 2>/dev/null || echo "No media files yet"
}

# Test database connection
test_db() {
    echo "🗄️ Testing database connection..."
    cd /home/adsuser/ads-automation
    python3 -c "from app.core.database import SessionLocal; db = SessionLocal(); print('✅ Database connection OK'); db.close()"
}

# Show menu
case "$1" in
    check)
        check_processes
        ;;
    logs)
        view_logs
        ;;
    restart)
        restart_all
        ;;
    stop)
        stop_all
        ;;
    media)
        check_media
        ;;
    test-db)
        test_db
        ;;
    *)
        echo "AdStudio VPS Management Tool"
        echo ""
        echo "Usage: bash vps_commands.sh [command]"
        echo ""
        echo "Commands:"
        echo "  check     - Check running processes"
        echo "  logs      - View recent logs"
        echo "  restart   - Restart all services"
        echo "  stop      - Stop all services"
        echo "  media     - Check media files"
        echo "  test-db   - Test database connection"
        echo ""
        echo "Examples:"
        echo "  bash vps_commands.sh check"
        echo "  bash vps_commands.sh logs"
        echo "  bash vps_commands.sh restart"
        ;;
esac
