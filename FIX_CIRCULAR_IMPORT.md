# 🔧 FIX CIRCULAR IMPORT

## ❌ VẤN ĐỀ

```
ImportError: cannot import name 'Job' from partially initialized module 'app.models.job' 
(most likely due to a circular import)
```

**Nguyên nhân:**
- `app/core/database.py` import `Job` từ `app/models/job` (top level)
- `app/models/job.py` import `Base` từ `app/core/database` (top level)
- → Circular import!

---

## ✅ GIẢI PHÁP

**Di chuyển import models vào trong function `init_db()`:**

- ❌ **Trước:** Import models ở top level trong `database.py`
- ✅ **Sau:** Import models trong function `init_db()`

**Lý do:**
- Khi `init_db()` được gọi, `Base` đã được định nghĩa
- Models import `Base` không còn gây circular import
- `Base.metadata.create_all()` vẫn hoạt động bình thường

---

## 🧪 TEST FIX

### **BƯỚC 1: Pull code mới (từ GitHub):**

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

### **BƯỚC 2: Test import:**

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

### **BƯỚC 3: Test worker chạy:**

```bash
# Test chạy worker (sẽ chạy vô hạn, dừng bằng Ctrl+C sau 5 giây)
timeout 5 python -m app.workers.telegram_worker worker-test 2>&1 || true
```

**Kết quả mong đợi:**
```
🚀 Starting Telegram worker: worker-test
(đợi 5 giây, không có lỗi)
```

### **BƯỚC 4: Restart worker trong Supervisor:**

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

### **Check Python cache:**

```bash
# Xóa Python cache
find ~/ads-automation -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find ~/ads-automation -name "*.pyc" -delete 2>/dev/null || true

# Test lại
python -c "from app.workers.telegram_worker import worker_loop; print('OK')"
```

### **Check imports:**

```bash
# Test từng import
python -c "from app.core.database import Base; print('Base OK')"
python -c "from app.models.job import Job; print('Job OK')"
python -c "from app.services.job_queue import JobQueue; print('JobQueue OK')"
python -c "from app.workers.telegram_worker import worker_loop; print('Worker OK')"
```

---

## 📋 CHECKLIST

- [ ] Pull code mới
- [ ] Test import worker
- [ ] Test import job_queue
- [ ] Test chạy worker
- [ ] Restart worker trong Supervisor
- [ ] Check status và logs
- [ ] Verify không còn circular import

---

**Bây giờ hãy test fix! 🚀**


