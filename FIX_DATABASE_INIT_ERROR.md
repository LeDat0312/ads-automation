# 🔧 FIX DATABASE INIT ERROR

## 🔍 VẤN ĐỀ

Lỗi: `'NoneType' object has no attribute '_run_ddl_visitor'`

**Nguyên nhân:** Engine chưa được khởi tạo trước khi gọi `Base.metadata.create_all(bind=engine)`

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Kiểm tra database connection:**

```bash
# Test connection
psql -U adsuser -d ads_automation -h localhost
# Nhập password: @Levandat0312
# Nếu vào được → OK
# Thoát: \q
```

### **BƯỚC 2: Kiểm tra .env:**

```bash
cd ~/ads-automation
grep DATABASE_URL .env
```

**Phải thấy:**
```
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
```

### **BƯỚC 3: Sửa scripts/init_db.py:**

```bash
nano scripts/init_db.py
```

**Thay đổi:**

```python
"""
Initialize Database
Tạo tất cả tables từ models
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.core.database import Base, init_db
# Import models để đảm bảo chúng được đăng ký với Base
from app.models.telegram_update import TelegramUpdate
from app.models.job import Job
from app.models.logic_rule import LogicRule
from app.core.database import AdMetrics, SystemSetting, AutomationStatus

def main():
    """Initialize database"""
    print("🚀 Initializing database...")
    
    try:
        # Load settings để đảm bảo DATABASE_URL được load
        settings = get_settings()
        print(f"📋 Database URL: {settings.DATABASE_URL[:30]}...")
        
        # Initialize database (tạo engine)
        init_db()
        
        # Import engine sau khi init
        from app.core.database import engine
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully!")
        print("\n📋 Created tables:")
        for table in Base.metadata.tables:
            print(f"  - {table}")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **BƯỚC 4: Chạy lại:**

```bash
cd ~/ads-automation
source venv/bin/activate
python scripts/init_db.py
```

---

## 🔍 DEBUG NẾU VẪN LỖI

### **Test database connection:**

```bash
# Test với Python
python3 -c "
from app.core.config import get_settings
from app.core.database import init_db
try:
    settings = get_settings()
    print(f'DATABASE_URL: {settings.DATABASE_URL}')
    init_db()
    print('✅ Database connection OK!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

### **Check PostgreSQL đang chạy:**

```bash
sudo systemctl status postgresql
```

### **Check database tồn tại:**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\l" | grep ads_automation
```

---

## ⚡ QUICK FIX

### **Nếu vẫn không work, thử cách này:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test connection trước
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
"

# Nếu OK, chạy init
python scripts/init_db.py
```

---

**Sửa file init_db.py như trên và chạy lại! 🚀**


