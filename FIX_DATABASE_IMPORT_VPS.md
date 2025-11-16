# 🔧 FIX DATABASE.PY IMPORT TRÊN VPS

## ❌ VẤN ĐỀ

File `database.py` trên VPS vẫn có import `Job` ở dòng 19 (top level), gây circular import.

---

## ✅ GIẢI PHÁP NHANH

### **BƯỚC 1: Check file database.py**

```bash
cd ~/ads-automation
head -25 app/core/database.py
```

**Nếu thấy dòng:**
```python
from app.models.job import Job  # ❌ SAI - phải xóa!
```

### **BƯỚC 2: Sửa file bằng sed (tự động)**

```bash
cd ~/ads-automation

# Backup
cp app/core/database.py app/core/database.py.backup

# Xóa dòng 19 nếu có import Job
sed -i '19d' app/core/database.py

# Verify
head -25 app/core/database.py
```

**Phải KHÔNG còn dòng `from app.models.job import Job` ở top level!**

### **BƯỚC 3: Verify import chỉ có trong init_db()**

```bash
cd ~/ads-automation
grep -A 10 "def init_db" app/core/database.py | grep "from app.models.job import"
```

**Phải thấy import trong function `init_db()`!**

### **BƯỚC 4: Test import**

```bash
cd ~/ads-automation
source venv/bin/activate

python -c "from app.workers.telegram_worker import worker_loop; print('✅ Import OK')"
```

**Nếu OK, tiếp tục. Nếu lỗi, check lại!**

### **BƯỚC 5: Restart workers**

```bash
sudo supervisorctl restart ads-automation-worker:*
sleep 2
sudo supervisorctl status
```

**Phải thấy `RUNNING`!**

---

## 🔍 HOẶC SỬA THỦ CÔNG BẰNG NANO

### **BƯỚC 1: Mở file**

```bash
cd ~/ads-automation
nano app/core/database.py
```

### **BƯỚC 2: Tìm và xóa dòng import Job ở top level**

1. Tìm dòng 19 (hoặc gần đó) có:
   ```python
   from app.models.job import Job
   ```
2. **XÓA dòng này** (nếu có ở top level, không phải trong function)
3. **Đảm bảo** trong function `init_db()` (khoảng dòng 128-130) có:
   ```python
   def init_db():
       ...
       from app.models.job import Job  # ✅ ĐÚNG - chỉ trong function!
   ```

### **BƯỚC 3: Lưu và thoát**

- `Ctrl + O` (Save)
- `Enter` (Confirm)
- `Ctrl + X` (Exit)

### **BƯỚC 4: Test và restart**

```bash
source venv/bin/activate
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Import OK')"
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

---

## 📋 KẾT QUẢ MONG ĐỢI

**File `database.py` phải:**
- ❌ **KHÔNG có** `from app.models.job import Job` ở top level (sau dòng 14)
- ✅ **CÓ** `from app.models.job import Job` trong function `init_db()` (khoảng dòng 128-130)

**Chạy các bước trên và báo lại kết quả! 🚀**


