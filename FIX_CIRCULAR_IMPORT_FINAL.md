# 🔧 FIX CIRCULAR IMPORT - FINAL

## ❌ VẤN ĐỀ

```
ImportError: cannot import name 'Job' from partially initialized module 'app.models.job'
```

**Nguyên nhân:** Circular import giữa `database.py` và `job.py`

---

## ✅ GIẢI PHÁP

### **BƯỚC 1: Xóa Python cache trên VPS**

```bash
cd ~/ads-automation
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
```

### **BƯỚC 2: Pull code mới nhất từ GitHub**

```bash
cd ~/ads-automation
git stash  # Lưu local changes nếu có
git pull origin main
```

### **BƯỚC 3: Verify file database.py không có import Job ở top level**

```bash
cd ~/ads-automation
grep -n "from app.models.job import" app/core/database.py
```

**Kết quả phải RỖNG!** (không có dòng nào)

Nếu có, cần xóa dòng đó.

### **BƯỚC 4: Verify import Job chỉ có trong init_db()**

```bash
cd ~/ads-automation
grep -A 5 "def init_db" app/core/database.py | grep "from app.models.job import"
```

**Phải thấy import trong function `init_db()`!**

### **BƯỚC 5: Test import**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import worker
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Import OK')"
```

**Nếu OK, tiếp tục. Nếu lỗi, check lại các bước trên.**

### **BƯỚC 6: Restart workers**

```bash
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

**Phải thấy `RUNNING`!**

### **BƯỚC 7: Test bot**

1. Gửi `/start` trong Telegram
2. Check logs:
   ```bash
   sudo tail -f /var/log/ads-automation/worker.out.log
   ```

---

## 🔍 NẾU VẪN LỖI

### **Check file database.py trên VPS:**

```bash
cd ~/ads-automation
head -30 app/core/database.py
```

**Phải KHÔNG có:**
```python
from app.models.job import Job  # ❌ SAI!
```

**Chỉ có trong `init_db()`:**
```python
def init_db():
    ...
    from app.models.job import Job  # ✅ ĐÚNG!
```

---

**Chạy các bước trên và báo lại kết quả! 🚀**


