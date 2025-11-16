# 🚀 QUICK FIX CIRCULAR IMPORT

## ⚡ CHẠY TRỰC TIẾP TRÊN VPS

### **BƯỚC 1: Xóa cache và pull code**

```bash
cd ~/ads-automation

# Xóa Python cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Pull code mới nhất
git stash 2>/dev/null || true
git pull origin main
```

### **BƯỚC 2: Verify file database.py**

```bash
cd ~/ads-automation

# Check xem có import Job ở top level không (PHẢI RỖNG)
grep -n "^from app.models.job import" app/core/database.py

# Check xem có import Job trong init_db() không (PHẢI CÓ)
grep -A 10 "def init_db" app/core/database.py | grep "from app.models.job import"
```

**Kết quả mong đợi:**
- Dòng 1: **RỖNG** (không có output)
- Dòng 2: **CÓ** (thấy dòng import trong function)

### **BƯỚC 3: Test import**

```bash
cd ~/ads-automation
source venv/bin/activate

python -c "from app.workers.telegram_worker import worker_loop; print('✅ Import OK')"
```

**Nếu OK, tiếp tục. Nếu lỗi, báo lại!**

### **BƯỚC 4: Restart workers**

```bash
sudo supervisorctl restart ads-automation-worker:*
sleep 2
sudo supervisorctl status
```

**Phải thấy `RUNNING`!**

### **BƯỚC 5: Test bot**

1. Gửi `/start` trong Telegram
2. Check logs:
   ```bash
   sudo tail -f /var/log/ads-automation/worker.out.log
   ```

---

## 🔍 NẾU VẪN LỖI SAU BƯỚC 3

### **Check file database.py trực tiếp:**

```bash
cd ~/ads-automation
head -30 app/core/database.py
```

**Phải KHÔNG có dòng:**
```python
from app.models.job import Job  # ❌ SAI - không được có ở top level!
```

**Chỉ có trong function:**
```python
def init_db():
    ...
    from app.models.job import Job  # ✅ ĐÚNG - chỉ trong function!
```

---

**Chạy các bước trên và báo lại kết quả! 🚀**
