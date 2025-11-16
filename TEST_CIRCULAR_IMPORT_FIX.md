# 🧪 TEST CIRCULAR IMPORT FIX

## ✅ ĐÃ SỬA

- ✅ Di chuyển import models vào trong function `init_db()`
- ✅ Tránh circular import giữa `database.py` và `job.py`

---

## 🚀 TEST TRÊN VPS

### **BƯỚC 1: Pull code mới:**

```bash
cd ~/ads-automation
git pull origin main
```

**Nếu có conflict:**

```bash
git stash
git pull origin main
git stash pop
```

### **BƯỚC 2: Xóa Python cache (quan trọng!):**

```bash
# Xóa __pycache__ và .pyc files
find ~/ads-automation -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find ~/ads-automation -name "*.pyc" -delete 2>/dev/null || true

# Verify
echo "✅ Cache cleared"
```

### **BƯỚC 3: Test import:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import worker
python -c "
from app.workers.telegram_worker import worker_loop
print('✅ Worker import OK')
"

# Test import job_queue
python -c "
from app.services.job_queue import JobQueue
print('✅ JobQueue import OK')
"

# Test import database
python -c "
from app.core.database import init_db, Base
print('✅ Database import OK')
"
```

**Kết quả mong đợi:** Tất cả đều OK, không có lỗi ImportError!

### **BƯỚC 4: Test worker chạy:**

```bash
# Test chạy worker (sẽ chạy vô hạn, dừng bằng Ctrl+C sau 5 giây)
timeout 5 python -m app.workers.telegram_worker worker-test 2>&1 || true
```

**Kết quả mong đợi:**
```
🚀 Starting Telegram worker: worker-test
(đợi 5 giây, không có lỗi)
```

### **BƯỚC 5: Restart worker trong Supervisor:**

```bash
# Restart workers
sudo supervisorctl restart ads-automation-worker:*

# Check status
sudo supervisorctl status

# Check logs
sudo tail -50 /var/log/ads-automation/worker.out.log
sudo tail -50 /var/log/ads-automation/worker.err.log
```

---

## ✅ KẾT QUẢ MONG ĐỢI

### **Status:**

```
ads-automation-api                  RUNNING   pid ..., uptime ...
ads-automation-worker:ads-automation-worker_00   RUNNING   pid ..., uptime ...
ads-automation-worker:ads-automation-worker_01   RUNNING   pid ..., uptime ...
```

### **Logs:**

```
🚀 Starting Telegram worker: worker-00
🚀 Starting Telegram worker: worker-01
```

**Không có lỗi ImportError!**

---

## 🔍 NẾU VẪN CÓ LỖI

### **Check code đã được pull chưa:**

```bash
# Check file database.py
grep -A 5 "def init_db" ~/ads-automation/app/core/database.py

# Phải thấy:
# def init_db():
#     """Initialize database connection"""
#     global engine, SessionLocal
#     
#     # Import models ở đây để tránh circular import
#     from app.models.telegram_update import TelegramUpdate
```

### **Nếu code chưa được pull:**

```bash
# Force pull
cd ~/ads-automation
git fetch origin
git reset --hard origin/main
```

### **Check Python cache:**

```bash
# Xóa cache lại
find ~/ads-automation -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find ~/ads-automation -name "*.pyc" -delete 2>/dev/null || true

# Test lại
python -c "from app.workers.telegram_worker import worker_loop; print('OK')"
```

---

## 📋 CHECKLIST

- [ ] Pull code mới
- [ ] Xóa Python cache
- [ ] Test import worker
- [ ] Test import job_queue
- [ ] Test chạy worker
- [ ] Restart worker trong Supervisor
- [ ] Check status và logs
- [ ] Verify không còn circular import

---

**Bây giờ hãy test trên VPS! 🚀**


