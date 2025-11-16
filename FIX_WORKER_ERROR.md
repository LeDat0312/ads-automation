# 🔧 FIX WORKER ERROR

## 🔍 VẤN ĐỀ

- ✅ `ads-automation-api` - RUNNING
- ❌ `ads-automation-worker` - FATAL (Exited too quickly)

**Nguyên nhân:** Worker có thể có lỗi import hoặc thiếu dependencies.

---

## 🔍 KIỂM TRA LOGS

### **BƯỚC 1: Check worker logs:**

```bash
# Check error logs
sudo tail -50 /var/log/ads-automation/worker.err.log

# Check output logs
sudo tail -50 /var/log/ads-automation/worker.out.log
```

**Sẽ thấy lỗi chi tiết.**

---

## ✅ CÁCH SỬA

### **CÁCH 1: Test worker manually:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import worker
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Import OK')"

# Test chạy worker (sẽ chạy vô hạn, dừng bằng Ctrl+C)
python -m app.workers.telegram_worker worker-1
```

### **CÁCH 2: Check worker code:**

```bash
cat app/workers/telegram_worker.py
```

**Kiểm tra:**
- Có import đúng không?
- Có lỗi syntax không?
- Có dependencies thiếu không?

---

## 🔧 FIX WORKER CODE

### **Nếu worker có lỗi, sửa:**

Có thể worker cần fix một số imports hoặc logic. Hãy check logs trước để biết lỗi cụ thể.

---

## 🧪 TEST WORKER MANUALLY

### **Test từng bước:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test 1: Import
python -c "from app.workers import telegram_worker; print('✅ Import OK')"

# Test 2: Import job_queue
python -c "from app.services.job_queue import JobQueue; print('✅ JobQueue OK')"

# Test 3: Test worker
python -c "
from app.workers.telegram_worker import worker_loop
print('✅ Worker import OK')
"
```

---

## 🔍 DEBUG CHI TIẾT

### **Check tất cả dependencies:**

```bash
python -c "
try:
    from app.services.job_queue import JobQueue
    print('✅ JobQueue OK')
except Exception as e:
    print(f'❌ JobQueue Error: {e}')
    import traceback
    traceback.print_exc()

try:
    from app.services.command_processor import CommandProcessor
    print('✅ CommandProcessor OK')
except Exception as e:
    print(f'❌ CommandProcessor Error: {e}')
    import traceback
    traceback.print_exc()

try:
    from app.workers.telegram_worker import worker_loop
    print('✅ Worker OK')
except Exception as e:
    print(f'❌ Worker Error: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## ⚠️ TẠM THỜI: DISABLE WORKER

### **Nếu worker không cần thiết ngay:**

Có thể tạm thời disable worker và chỉ chạy API:

```bash
# Stop workers
sudo supervisorctl stop ads-automation-worker:*

# Comment out worker config trong supervisor (nếu cần)
# Hoặc để đó, worker sẽ tự restart
```

**API vẫn chạy bình thường, chỉ worker bị lỗi.**

---

## ✅ CHECKLIST

- [ ] Check worker logs: `sudo tail -50 /var/log/ads-automation/worker.err.log`
- [ ] Test worker manually: `python -m app.workers.telegram_worker worker-1`
- [ ] Fix lỗi (nếu có)
- [ ] Restart worker: `sudo supervisorctl restart ads-automation-worker:*`

---

**Bây giờ hãy check worker logs để xem lỗi gì! 🚀**


