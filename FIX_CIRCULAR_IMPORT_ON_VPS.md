# 🔧 FIX CIRCULAR IMPORT TRÊN VPS

## ❌ VẤN ĐỀ

Vẫn còn circular import vì code trên VPS chưa được cập nhật.

---

## ✅ SỬA TRỰC TIẾP TRÊN VPS

### **BƯỚC 1: Check file hiện tại:**

```bash
cd ~/ads-automation
grep -n "from app.models.job import Job" app/core/database.py
```

**Nếu thấy dòng này ở top level (không phải trong function), cần sửa!**

### **BƯỚC 2: Sửa file database.py:**

```bash
cd ~/ads-automation
nano app/core/database.py
```

**Tìm và XÓA các dòng import models ở top level (khoảng dòng 16-20):**

```python
# XÓA các dòng này:
from app.models.telegram_update import TelegramUpdate
from app.models.job import Job
from app.models.logic_rule import LogicRule
```

**Tìm function `init_db()` (khoảng dòng 122) và THÊM import vào trong function:**

```python
def init_db():
    """Initialize database connection"""
    global engine, SessionLocal
    
    # Import models ở đây để tránh circular import
    from app.models.telegram_update import TelegramUpdate
    from app.models.job import Job
    from app.models.logic_rule import LogicRule
    
    settings = get_settings()
    # ... (phần còn lại)
```

### **BƯỚC 3: Verify file đã đúng:**

```bash
# Check không còn import ở top level
grep -n "from app.models.job import Job" app/core/database.py

# Phải không có kết quả (hoặc chỉ có trong function init_db)

# Check import trong init_db
grep -A 5 "def init_db" app/core/database.py | grep "from app.models"
```

### **BƯỚC 4: Xóa Python cache:**

```bash
cd ~/ads-automation
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

### **BƯỚC 5: Test lại:**

```bash
source venv/bin/activate

# Test import
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker import OK')"
```

---

## 🚀 QUICK FIX (Sửa tự động)

### **Option 1: Sửa bằng sed:**

```bash
cd ~/ads-automation

# Backup file
cp app/core/database.py app/core/database.py.backup

# Xóa import models ở top level (sau dòng Base = declarative_base())
sed -i '/^Base = declarative_base()$/a\
# Models sẽ được import trong init_db() để tránh circular import
' app/core/database.py

# Xóa các dòng import models ở top level
sed -i '/^from app.models.telegram_update import TelegramUpdate$/d' app/core/database.py
sed -i '/^from app.models.job import Job$/d' app/core/database.py
sed -i '/^from app.models.logic_rule import LogicRule$/d' app/core/database.py

# Thêm import vào trong init_db()
sed -i '/def init_db():/a\
    # Import models ở đây để tránh circular import\
    from app.models.telegram_update import TelegramUpdate\
    from app.models.job import Job\
    from app.models.logic_rule import LogicRule\
' app/core/database.py
```

### **Option 2: Sửa bằng Python script:**

```bash
cd ~/ads-automation
cat > /tmp/fix_database.py << 'PYEOF'
import re

# Read file
with open('app/core/database.py', 'r') as f:
    content = f.read()

# Remove imports at top level (after Base = declarative_base())
pattern = r'(Base = declarative_base\(\)\s*\n)(\s*#.*\n)?(\s*from app\.models\.telegram_update import TelegramUpdate\s*\n)?(\s*from app\.models\.job import Job\s*\n)?(\s*from app\.models\.logic_rule import LogicRule\s*\n)?'
replacement = r'\1\n# Models sẽ được import trong init_db() để tránh circular import\n\n'
content = re.sub(pattern, replacement, content)

# Add imports inside init_db() if not already there
if 'def init_db():' in content and 'from app.models.job import Job' not in content.split('def init_db():')[1].split('\n\n')[0]:
    pattern = r'(def init_db\(\):\s*\n\s*""".*?"""\s*\n\s*global engine, SessionLocal\s*\n)'
    replacement = r'\1    # Import models ở đây để tránh circular import\n    from app.models.telegram_update import TelegramUpdate\n    from app.models.job import Job\n    from app.models.logic_rule import LogicRule\n    \n'
    content = re.sub(pattern, replacement, content)

# Write file
with open('app/core/database.py', 'w') as f:
    f.write(content)

print("✅ Fixed database.py")
PYEOF

python /tmp/fix_database.py
```

---

## ✅ VERIFY SAU KHI SỬA

### **Check file:**

```bash
# Check không còn import ở top level
head -25 app/core/database.py | grep "from app.models"

# Phải không có kết quả

# Check import trong init_db
sed -n '/def init_db/,/settings = get_settings/p' app/core/database.py | grep "from app.models"

# Phải thấy import models
```

### **Test import:**

```bash
source venv/bin/activate
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker import OK')"
```

**Kết quả mong đợi:** `✅ Worker import OK` (không có lỗi!)

---

## 📋 CHECKLIST

- [ ] Check file database.py
- [ ] Xóa import models ở top level
- [ ] Thêm import vào trong init_db()
- [ ] Xóa Python cache
- [ ] Test import worker
- [ ] Restart worker

---

**Bây giờ hãy sửa file database.py trên VPS! 🚀**


