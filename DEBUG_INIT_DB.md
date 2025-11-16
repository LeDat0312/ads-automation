# 🔍 DEBUG INIT_DB - KHÔNG CÓ OUTPUT

## 🔍 VẤN ĐỀ

Chạy `python scripts/init_db.py` nhưng không có output.

**Có thể:**
1. File không chạy được
2. Có lỗi nhưng không hiển thị
3. Import lỗi

---

## ✅ CÁCH KIỂM TRA

### **BƯỚC 1: Check file có tồn tại không:**

```bash
cd ~/ads-automation
ls -la scripts/init_db.py
```

### **BƯỚC 2: Check Python path:**

```bash
which python
# Nên thấy: /home/adsuser/ads-automation/venv/bin/python
```

### **BƯỚC 3: Chạy với Python trực tiếp:**

```bash
python3 scripts/init_db.py
```

### **BƯỚC 4: Chạy với output đầy đủ:**

```bash
python -u scripts/init_db.py
```

### **BƯỚC 5: Test import:**

```bash
python -c "
import sys
sys.path.insert(0, '.')
from app.core.config import get_settings
print('✅ Import OK')
settings = get_settings()
print(f'DATABASE_URL: {settings.DATABASE_URL[:50]}...')
"
```

---

## 🔧 CHẠY TRỰC TIẾP VỚI PYTHON

### **Test từng bước:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test 1: Check Python
python --version

# Test 2: Test import
python -c "from app.core.config import get_settings; print('Import OK')"

# Test 3: Test database connection
python -c "
from app.core.config import get_settings
from app.core.database import init_db
try:
    settings = get_settings()
    print(f'📋 DATABASE_URL: {settings.DATABASE_URL[:50]}...')
    init_db()
    print('✅ Database connection OK!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"

# Test 4: Chạy init_db.py
python scripts/init_db.py
```

---

## 🔍 NẾU VẪN KHÔNG CÓ OUTPUT

### **Check file có đúng không:**

```bash
head -20 scripts/init_db.py
```

**Phải thấy:**
```python
"""
Initialize Database
Tạo tất cả tables từ models
"""
...
```

### **Check quyền file:**

```bash
ls -la scripts/init_db.py
# Phải có quyền execute: -rwxr-xr-x hoặc -rw-r--r--
```

### **Chạy với bash:**

```bash
bash -x scripts/init_db.py
```

---

## ⚡ QUICK TEST

```bash
cd ~/ads-automation
source venv/bin/activate

# Test đơn giản nhất
python -c "print('Hello from Python')"

# Nếu OK, test import
python -c "import sys; sys.path.insert(0, '.'); from app.core.config import get_settings; print('Import OK')"

# Nếu OK, chạy init_db
python scripts/init_db.py
```

---

**Chạy các lệnh test ở trên để tìm vấn đề! 🔍**


