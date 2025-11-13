# Hướng dẫn Pull Code về VPS

## Bước 1: SSH vào VPS
```bash
ssh adsuser@54.179.208.122
```

## Bước 2: Navigate đến thư mục project
```bash
cd ~/ads-automation
```

## Bước 3: Pull code mới từ GitHub
```bash
# Activate virtual environment
source venv/bin/activate

# Pull code mới
git pull origin main

# Nếu có conflict, stash local changes trước
# git stash
# git pull origin main
# git stash pop
```

## Bước 4: Restart services (nếu cần)
```bash
# Restart API
sudo supervisorctl restart ads-automation-api

# Restart workers
sudo supervisorctl restart ads-automation-worker:*

# Kiểm tra status
sudo supervisorctl status
```

## Bước 5: Kiểm tra logs (nếu có lỗi)
```bash
# Logs API
sudo tail -f /var/log/ads-automation/api.out.log

# Logs Worker
sudo tail -f /var/log/ads-automation/worker.out.log
```

## Lệnh nhanh (tất cả trong một)
```bash
cd ~/ads-automation && source venv/bin/activate && git pull origin main && sudo supervisorctl restart ads-automation-api && sudo supervisorctl restart ads-automation-worker:* && sudo supervisorctl status
```



