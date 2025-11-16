# 🔍 DEBUG WORKER ERROR

## ❌ VẤN ĐỀ

```
ads-automation-worker:ads-automation-worker_00: ERROR (spawn error)
ads-automation-worker:ads-automation-worker_01: ERROR (spawn error)
```

---

## 🔍 KIỂM TRA LOGS

### **BƯỚC 1: Check error logs:**

```bash
sudo tail -50 /var/log/ads-automation/worker.err.log
```

**Sẽ thấy lỗi chi tiết!**

### **BƯỚC 2: Check output logs:**

```bash
sudo tail -50 /var/log/ads-automation/worker.out.log
```

---

## 🧪 TEST WORKER MANUALLY

### **BƯỚC 3: Test worker trực tiếp:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import (có thể vẫn lỗi circular import)
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker import OK')"
```

**Nếu vẫn lỗi circular import, cần sửa `database.py` trước!**

### **BƯỚC 4: Test chạy worker:**

```bash
# Test với worker ID
timeout 5 python -m app.workers.telegram_worker 00 2>&1 || true
```

---

## 🔧 FIX CIRCULAR IMPORT (Nếu chưa fix)

### **Check file database.py:**

```bash
# Check có import models ở top level không
head -25 app/core/database.py | grep "from app.models"
```

**Nếu có kết quả, cần sửa!**

### **Sửa file database.py:**

```bash
cd ~/ads-automation
nano app/core/database.py
```

**Tìm và XÓA (khoảng dòng 16-20):**
```python
from app.models.telegram_update import TelegramUpdate
from app.models.job import Job
from app.models.logic_rule import LogicRule
```

**Tìm function `init_db()` và THÊM sau `global engine, SessionLocal`:**
```python
def init_db():
    """Initialize database connection"""
    global engine, SessionLocal
    
    # Import models ở đây để tránh circular import
    from app.models.telegram_update import TelegramUpdate
    from app.models.job import Job
    from app.models.logic_rule import LogicRule
    # Import các models khác nếu có
    
    settings = get_settings()
    # ... (phần còn lại)
```

### **Xóa cache và test lại:**

```bash
cd ~/ads-automation

# Xóa cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Test
source venv/bin/activate
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker import OK')"
```

---

## ✅ SAU KHI FIX

### **Restart workers:**

```bash
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

---

## 📋 CHECKLIST

- [ ] Check error logs
- [ ] Check output logs
- [ ] Test worker manually
- [ ] Fix circular import (nếu cần)
- [ ] Xóa Python cache
- [ ] Test import worker
- [ ] Restart workers
- [ ] Check status

---

**Bây giờ hãy check logs để xem lỗi cụ thể! 🚀**


