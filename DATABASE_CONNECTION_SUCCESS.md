# ✅ KẾT NỐI DATABASE THÀNH CÔNG!

## 🎉 XÁC NHẬN

Bạn đã kết nối thành công vào database `ads_automation`!

**Dấu hiệu:**
- ✅ `ads_automation=>` prompt - Đang trong database
- ✅ SSL connection - Kết nối an toàn
- ✅ Không có lỗi

---

## 🔧 BƯỚC TIẾP THEO

### **1. Thoát khỏi psql:**

```bash
\q
```

Bạn sẽ quay về shell prompt.

### **2. List tables (hiện tại sẽ rỗng):**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\dt"
```

**Kết quả:** Sẽ rỗng vì chưa tạo tables.

---

## 📝 UPDATE .ENV FILE

### **Bước 1: Navigate to project:**

```bash
cd ~/ads-automation
```

### **Bước 2: Check nếu có .env:**

```bash
ls -la .env
# Nếu không có, copy từ env.example
cp env.example .env
```

### **Bước 3: Edit .env:**

```bash
nano .env
```

### **Bước 4: Update DATABASE_URL:**

**Tìm dòng:**
```bash
DATABASE_URL=postgresql://adsuser:your_secure_password@localhost:5432/ads_automation
```

**Thay thành (URL encode @ thành %40):**
```bash
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Set permissions:**
```bash
chmod 600 .env
```

---

## 🗄️ INITIALIZE DATABASE TABLES

### **Bước 1: Activate venv:**

```bash
cd ~/ads-automation
source venv/bin/activate
```

**Verify venv:**
```bash
which python
# Nên thấy: /home/adsuser/ads-automation/venv/bin/python
```

### **Bước 2: Check nếu có scripts/init_db.py:**

```bash
ls -la scripts/init_db.py
```

**Nếu không có, tạo thư mục:**
```bash
mkdir -p scripts
```

### **Bước 3: Run init script:**

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

### **Bước 4: Verify tables:**

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

## 🧪 TEST VỚI PYTHON

### **Test connection:**

```bash
cd ~/ads-automation
source venv/bin/activate

python3 -c "
from app.core.config import get_settings
from app.core.database import init_db
try:
    settings = get_settings()
    print('✅ Config loaded')
    print(f'Database: {settings.DATABASE_URL.split(\"@\")[-1]}')
    init_db()
    print('✅ Database connection OK!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## ⚠️ NẾU GẶP LỖI

### **Lỗi: "No module named 'app'"**

```bash
# Đảm bảo đang ở đúng thư mục
cd ~/ads-automation
pwd
# Nên thấy: /home/adsuser/ads-automation

# Check structure
ls -la app/
# Nên thấy: __init__.py, core/, models/, etc.
```

### **Lỗi: "DATABASE_URL not set"**

```bash
# Check .env file
cat .env | grep DATABASE_URL

# Verify .env được load
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DATABASE_URL'))"
```

### **Lỗi: "password authentication failed"**

```bash
# Test lại connection
psql -U adsuser -d ads_automation -h localhost
# Nhập password: @Levandat0312

# Nếu không vào được, check user
sudo -u postgres psql -c "\du"
```

---

## ✅ CHECKLIST

- [x] Database connection OK
- [ ] Thoát psql: `\q`
- [ ] Update `.env` với password (URL encode `@` thành `%40`)
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Run `python scripts/init_db.py`
- [ ] Verify tables: `psql -U adsuser -d ads_automation -h localhost -c "\dt"`
- [ ] Test với Python

---

**Bây giờ hãy thoát psql (`\q`) và tiếp tục setup! 🚀**

