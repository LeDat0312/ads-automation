#!/bin/bash
# Script để pull code từ GitHub về VPS và deploy

# 1. Kill process trên port 8000
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || true

# 2. Dừng services
sudo supervisorctl stop ads-automation ads-worker 2>/dev/null || true

# 3. Đợi 2 giây
sleep 2

# 4. Vào thư mục project
cd ~/ads-automation

# 5. Pull code mới
git pull origin main

# 6. Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# 7. Build frontend
cd frontend
npm install
npm run build
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist
cd ..

# 8. Restart services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ads-automation
sudo supervisorctl start ads-worker

# 9. Đợi và kiểm tra
sleep 5
sudo supervisorctl status

echo "✅ Hoàn tất deploy!"

