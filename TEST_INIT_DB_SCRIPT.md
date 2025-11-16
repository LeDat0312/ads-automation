# 🧪 TEST INIT_DB SCRIPT

## ✅ KẾT QUẢ

- ✅ Import OK: `from app.core.config import get_settings` thành công
- ⚠️ Script `init_db.py` chạy nhưng không có output

---

## 🔍 KIỂM TRA

### **BƯỚC 1: Chạy script với output đầy đủ:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Chạy với Python và xem output
python scripts/init_db.py
```

### **BƯỚC 2: Nếu không có output, test từng bước:**

```bash
python -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath('scripts/init_db.py'))))

from app.core.config import get_settings
from app.core.database import init_db, Base
from app.models.telegram_update import TelegramUpdate
from app.models.job import Job
from app.models.logic_rule import LogicRule
from app.core.database import AdMetrics, SystemSetting, AutomationStatus

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

## 🔍 DEBUG CHI TIẾT

### **Check file init_db.py có đúng không:**

```bash
cat scripts/init_db.py
```

**Phải thấy:**
- Có hàm `main()`
- Có `if __name__ == "__main__": main()`

### **Chạy với Python trực tiếp:**

```bash
python -c "
import scripts.init_db
scripts.init_db.main()
"
```

---

## ⚡ QUICK TEST

```bash
cd ~/ads-automation
source venv/bin/activate

# Test đơn giản
python -c "
from app.core.config import get_settings
from app.core.database import init_db

settings = get_settings()
print(f'📋 DATABASE_URL: {settings.DATABASE_URL[:50]}...')

try:
    init_db()
    print('✅ Database connection OK!')
    
    from app.core.database import engine, Base
    Base.metadata.create_all(bind=engine)
    print('✅ Tables created!')
    
    # List tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f'\n📋 Tables: {tables}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## 🔍 VERIFY DATABASE

### **Check tables đã được tạo chưa:**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\dt"
```

**Nếu thấy tables** → Database đã được init thành công!

---

**Chạy Quick Test ở trên để kiểm tra! 🚀**


