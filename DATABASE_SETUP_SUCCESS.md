# ✅ DATABASE SETUP THÀNH CÔNG!

## 🎉 KẾT QUẢ

Từ output, tôi thấy:
- ✅ `CREATE DATABASE` - Database đã được tạo
- ✅ `CREATE ROLE` - User `adsuser` đã được tạo
- ✅ `GRANT` - Privileges đã được grant
- ✅ `ALTER ROLE` - User đã có quyền CREATEDB

**Warning "could not change directory to /root"** - Không quan trọng, chỉ là warning về directory, không ảnh hưởng đến database.

---

## ✅ BƯỚC TIẾP THEO

### **1. Test Connection:**

```bash
# Test kết nối database
psql -U adsuser -d ads_automation -h localhost
```

**Nhập password:** `@Levandat0312`

**Kết quả mong đợi:**
```
Password for user adsuser: 
psql (14.x)
Type "help" for help.

ads_automation=> 
```

**Thoát:** `\q`

### **2. List Tables (sau khi init):**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\dt"
# Hiện tại sẽ rỗng, sau khi init_db.py sẽ có tables
```

---

## 📝 UPDATE .ENV FILE

### **Bước 1: Navigate to project:**

```bash
cd ~/ads-automation
```

### **Bước 2: Edit .env:**

```bash
nano .env
```

### **Bước 3: Update DATABASE_URL:**

**Tìm dòng:**
```bash
DATABASE_URL=postgresql://adsuser:your_secure_password@localhost:5432/ads_automation
```

**Thay thành (URL encode @ thành %40):**
```bash
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
```

**Hoặc thử trực tiếp (nếu URL encode không work):**
```bash
DATABASE_URL=postgresql://adsuser:@Levandat0312@localhost:5432/ads_automation
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🗄️ INITIALIZE DATABASE TABLES

### **Bước 1: Activate venv:**

```bash
cd ~/ads-automation
source venv/bin/activate
```

### **Bước 2: Run init script:**

```bash
python scripts/init_db.py
```

**Kết quả mong đợi:**
```
🚀 Initializing database...
✅ Database initialized successfully!

📋 Created tables:
  - ads_metrics
  - logic_rules
  - system_settings
  - automation_status
  - telegram_updates
  - jobs
```

### **Bước 3: Verify tables:**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\dt"
```

**Kết quả mong đợi:**
```
                  List of relations
 Schema |         Name          | Type  |  Owner   
--------+-----------------------+-------+----------
 public | ads_metrics           | table | adsuser
 public | automation_status     | table | adsuser
 public | jobs                  | table | adsuser
 public | logic_rules           | table | adsuser
 public | system_settings       | table | adsuser
 public | telegram_updates      | table | adsuser
(6 rows)
```

---

## 🧪 TEST API CONNECTION

### **Test với Python:**

```bash
cd ~/ads-automation
source venv/bin/activate

python3 -c "
from app.core.config import get_settings
from app.core.database import init_db
try:
    settings = get_settings()
    print(f'✅ Config loaded')
    print(f'Database URL: {settings.DATABASE_URL[:30]}...')
    init_db()
    print('✅ Database connection OK!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## ⚠️ NẾU GẶP LỖI VỚI PASSWORD

Nếu password `@Levandat0312` gây vấn đề với DATABASE_URL (do ký tự `@`), có thể:

### **Option 1: URL Encode (thử trước):**
```bash
# @ = %40
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
```

### **Option 2: Đổi password (nếu Option 1 không work):**

```bash
sudo -u postgres psql << EOF
ALTER USER adsuser WITH PASSWORD 'Levandat0312Secure';
\q
EOF
```

**Update .env:**
```bash
DATABASE_URL=postgresql://adsuser:Levandat0312Secure@localhost:5432/ads_automation
```

---

## ✅ CHECKLIST

- [x] Database created
- [x] User created
- [x] Privileges granted
- [ ] Test connection: `psql -U adsuser -d ads_automation -h localhost`
- [ ] Update `.env` với password (URL encode `@` thành `%40`)
- [ ] Run `python scripts/init_db.py`
- [ ] Verify tables: `psql -U adsuser -d ads_automation -h localhost -c "\dt"`

---

**Bây giờ hãy test connection và update .env! 🚀**

