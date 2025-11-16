# ✅ TEST WORKER FIX

## 🔧 ĐÃ SỬA

- ✅ Sửa `JobQueue` để quản lý database session tốt hơn
- ✅ Worker tạo session mới mỗi lần cần thiết, tránh timeout
- ✅ Sửa worker để xử lý job với session riêng

---

## 🧪 TEST WORKER

### **BƯỚC 1: Pull code mới (từ GitHub):**

```bash
cd ~/ads-automation
git pull origin main
```

**Nếu có conflict, hãy commit local changes trước:**

```bash
git add .
git commit -m "Fix worker session management"
git pull origin main
```

### **BƯỚC 2: Test worker manually:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import
python -c "
from app.workers.telegram_worker import worker_loop
print('✅ Worker import OK')
"

# Test chạy worker (sẽ chạy vô hạn, dừng bằng Ctrl+C sau 5 giây)
timeout 5 python -m app.workers.telegram_worker worker-test 2>&1 || true
```

### **BƯỚC 3: Restart worker trong Supervisor:**

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

**Không có lỗi!**

---

## 🔍 NẾU VẪN CÓ LỖI

### **Check logs chi tiết:**

```bash
# Check error logs
sudo tail -100 /var/log/ads-automation/worker.err.log

# Check output logs
sudo tail -100 /var/log/ads-automation/worker.out.log
```

### **Test database connection:**

```bash
python -c "
from app.core.database import get_db_session
try:
    db = get_db_session()
    print('✅ Database connection OK')
    db.close()
except Exception as e:
    print(f'❌ Database Error: {e}')
    import traceback
    traceback.print_exc()
"
```

### **Test JobQueue:**

```bash
python -c "
from app.services.job_queue import JobQueue
try:
    queue = JobQueue()
    print('✅ JobQueue OK')
    jobs = queue.get_next_job()
    print(f'Next job: {jobs}')
except Exception as e:
    print(f'❌ JobQueue Error: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## 📋 NEXT STEPS

- [ ] Pull code mới
- [ ] Test worker manually
- [ ] Restart worker trong Supervisor
- [ ] Check status và logs
- [ ] Setup Nginx (bước tiếp theo)
- [ ] Setup Telegram webhook (bước tiếp theo)

---

**Bây giờ hãy test worker! 🚀**


