# 🔍 CHECK WORKER ERROR

## 🔍 KIỂM TRA LOGS

### **BƯỚC 1: Check worker error logs:**

```bash
sudo tail -50 /var/log/ads-automation/worker.err.log
```

**Sẽ thấy lỗi chi tiết!**

---

## 🧪 TEST WORKER MANUALLY

### **BƯỚC 2: Test worker import:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import
python -c "
try:
    from app.workers.telegram_worker import worker_loop
    print('✅ Worker import OK')
except Exception as e:
    print(f'❌ Worker import Error: {e}')
    import traceback
    traceback.print_exc()
"
```

### **BƯỚC 3: Test worker chạy:**

```bash
# Test chạy worker (sẽ chạy vô hạn, dừng bằng Ctrl+C sau 5 giây)
timeout 5 python -m app.workers.telegram_worker worker-test || true
```

---

## 🔧 CÁC LỖI THƯỜNG GẶP

### **Lỗi 1: Database connection**

```bash
# Test database connection
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

### **Lỗi 2: Missing columns**

```bash
# Check Job table schema
psql -U adsuser -d ads_automation -h localhost -c "\d jobs"
```

**Phải có các columns:**
- `id`
- `job_type`
- `priority`
- `status`
- `payload`
- `attempts`
- `max_attempts`
- `error_message`
- `chat_id`
- `user_id`
- `created_at`
- `started_at`
- `completed_at`

### **Lỗi 3: Import error**

```bash
# Test tất cả imports
python -c "
try:
    from app.services.job_queue import JobQueue
    print('✅ JobQueue OK')
except Exception as e:
    print(f'❌ JobQueue Error: {e}')

try:
    from app.services.command_processor import CommandProcessor
    print('✅ CommandProcessor OK')
except Exception as e:
    print(f'❌ CommandProcessor Error: {e}')

try:
    from app.services.telegram_bot import send_message
    print('✅ TelegramBot OK')
except Exception as e:
    print(f'❌ TelegramBot Error: {e}')

try:
    from app.core.config import get_settings
    print('✅ Config OK')
except Exception as e:
    print(f'❌ Config Error: {e}')
"
```

---

## ✅ FIX WORKER (Nếu cần)

### **Nếu database schema sai:**

```bash
# Re-run init_db
cd ~/ads-automation
source venv/bin/activate
python scripts/init_db.py
```

### **Nếu có lỗi import:**

Có thể cần fix code. Hãy check logs trước!

---

## 🔍 DEBUG CHI TIẾT

### **Test worker với debug:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Chạy worker với Python debug
python -m app.workers.telegram_worker worker-debug 2>&1 | head -50
```

---

## ⚠️ TẠM THỜI: DISABLE WORKER

### **Nếu worker không cần thiết ngay:**

```bash
# Stop workers
sudo supervisorctl stop ads-automation-worker:*

# Hoặc disable trong supervisor config
sudo nano /etc/supervisor/conf.d/ads-automation.conf
# Comment out worker section
```

**API vẫn chạy bình thường!**

---

**Bây giờ hãy check logs để xem lỗi cụ thể! 🚀**


