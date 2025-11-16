# 🔍 DEBUG INIT_DB - KHÔNG CÓ OUTPUT

## 🔍 VẤN ĐỀ

Chạy `python scripts/init_db.py` nhưng không có output.

**Có thể:**
1. Script chạy thành công nhưng không in gì
2. Có lỗi nhưng không hiển thị
3. Database đã được init rồi

---

## ✅ KIỂM TRA

### **BƯỚC 1: Check database đã có tables chưa:**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\dt"
```

**Nếu thấy tables** → Database đã được init thành công!

### **BƯỚC 2: Test trực tiếp với Python:**

```bash
cd ~/ads-automation
source venv/bin/activate

python -c "
import sys
import os
sys.path.insert(0, '.')

print('🚀 Starting...')

from app.core.config import get_settings
from app.core.database import init_db, Base

print('✅ Imports OK')

try:
    settings = get_settings()
    print(f'📋 Database URL: {settings.DATABASE_URL[:50]}...')
    
    print('🔄 Initializing database...')
    init_db()
    print('✅ Database initialized!')
    
    from app.core.database import engine
    print('🔄 Creating tables...')
    Base.metadata.create_all(bind=engine)
    print('✅ Tables created!')
    
    # List tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f'\n📋 Created {len(tables)} tables:')
    for table in tables:
        print(f'  - {table}')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

### **BƯỚC 3: Check file init_db.py:**

```bash
cat scripts/init_db.py
```

**Kiểm tra:**
- Có hàm `main()` không?
- Có `if __name__ == "__main__": main()` không?

---

## 🔍 NẾU SCRIPT KHÔNG CHẠY

### **Check file có thể execute không:**

```bash
ls -la scripts/init_db.py
python scripts/init_db.py 2>&1
```

### **Chạy trực tiếp:**

```bash
python -c "
import sys
sys.path.insert(0, '.')
exec(open('scripts/init_db.py').read())
"
```

---

## ✅ VERIFY DATABASE

### **Check tables:**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\dt"
```

**Nếu thấy 6 tables:**
- ✅ Database đã được init thành công!
- ✅ Có thể tiếp tục bước tiếp theo

---

## 🚀 NEXT STEPS

Nếu database đã có tables:
1. ✅ Test API server
2. ✅ Setup Supervisor
3. ✅ Setup Nginx
4. ✅ Setup Telegram webhook

---

**Chạy lệnh ở Bước 1 và Bước 2 để kiểm tra! 🚀**


