# 🔧 FIX PSQL PROMPT - THOÁT KHỎI PSQL

## 🔍 VẤN ĐỀ

Bạn đang trong psql prompt (`ads_automation=>`) và đang cố chạy lệnh bash.

**Cần:** Thoát khỏi psql trước.

---

## ✅ THOÁT KHỎI PSQL

### **Trong psql prompt, gõ:**

```sql
\q
```

**Hoặc:**
```sql
exit
```

**Sau đó bạn sẽ quay về bash prompt:**
```
adsuser@ip-172-26-10-102:~/ads-automation$
```

---

## 🚀 SAU KHI THOÁT PSQL

### **BƯỚC 1: Test settings:**

```bash
cd ~/ads-automation
source venv/bin/activate

python -c "
from app.core.config import get_settings
settings = get_settings()
print('✅ Settings loaded!')
print(f'DATABASE_URL: {settings.DATABASE_URL[:50]}...')
print(f'TELEGRAM_CHAT_ID: {settings.TELEGRAM_CHAT_ID}')
print(f'WEBHOOK_URL: {settings.WEBHOOK_URL}')
"
```

### **BƯỚC 2: Initialize database:**

```bash
source venv/bin/activate
python scripts/init_db.py
```

**Kết quả mong đợi:**
```
🚀 Initializing database...
📋 Database URL: postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation...
✅ Database initialized successfully!

📋 Created tables:
  - ads_metrics
  - logic_rules
  - system_settings
  - automation_status
  - telegram_updates
  - jobs
```

### **BƯỚC 3: Nếu không có output, test từng bước:**

```bash
python -c "
import sys
import os
sys.path.insert(0, '.')

from app.core.config import get_settings
from app.core.database import init_db, Base

print('🚀 Initializing database...')

try:
    settings = get_settings()
    print(f'📋 Database URL: {settings.DATABASE_URL[:50]}...')
    
    init_db()
    print('✅ Database initialized!')
    
    from app.core.database import engine
    Base.metadata.create_all(bind=engine)
    print('✅ Tables created!')
    
    print('\n📋 Created tables:')
    for table in Base.metadata.tables:
        print(f'  - {table}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## 🔍 DEBUG NẾU KHÔNG CÓ OUTPUT

### **Check file init_db.py:**

```bash
cat scripts/init_db.py | head -50
```

### **Check có hàm main() không:**

```bash
grep "def main" scripts/init_db.py
grep "__main__" scripts/init_db.py
```

### **Chạy trực tiếp:**

```bash
python -c "import scripts.init_db; scripts.init_db.main()"
```

---

## ✅ QUICK STEPS

1. **Thoát psql:** Gõ `\q` và Enter
2. **Test settings:** Chạy lệnh test settings
3. **Init database:** Chạy `python scripts/init_db.py`
4. **Verify:** `psql -U adsuser -d ads_automation -h localhost -c "\dt"`

---

**Bây giờ hãy thoát psql (`\q`) và chạy lại các lệnh! 🚀**


