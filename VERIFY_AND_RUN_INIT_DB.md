# ✅ VERIFY VÀ CHẠY INIT_DB

## 🔍 KIỂM TRA FILE

### **Check file trên VPS:**

```bash
cd ~/ads-automation
cat scripts/init_db.py
```

**So sánh với code bạn đã paste - phải giống nhau.**

---

## ✅ CODE ĐÃ ĐÚNG

Code bạn paste đã đúng:
- ✅ Import `get_settings` và `init_db` đúng
- ✅ Gọi `init_db()` trước khi import engine
- ✅ Có traceback để debug
- ✅ Có error handling

---

## 🚀 CHẠY THỬ

### **Chạy init_db:**

```bash
cd ~/ads-automation
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

---

## 🔍 NẾU VẪN LỖI

### **Test database connection trước:**

```bash
# Test connection
psql -U adsuser -d ads_automation -h localhost
# Nhập password: @Levandat0312
# Nếu vào được → OK
# Thoát: \q
```

### **Test với Python:**

```bash
source venv/bin/activate
python3 -c "
from app.core.config import get_settings
from app.core.database import init_db
try:
    settings = get_settings()
    print(f'DATABASE_URL: {settings.DATABASE_URL[:50]}...')
    init_db()
    print('✅ Database connection OK!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## ✅ CHECKLIST

- [ ] File `scripts/init_db.py` đã đúng
- [ ] .env đã có DATABASE_URL đúng
- [ ] Database connection OK
- [ ] Chạy `python scripts/init_db.py`
- [ ] Verify tables: `psql -U adsuser -d ads_automation -h localhost -c "\dt"`

---

**Chạy `python scripts/init_db.py` để test! 🚀**


