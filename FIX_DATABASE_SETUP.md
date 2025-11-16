# ✅ FIX DATABASE SETUP

## 🔍 PHÂN TÍCH

Từ hình ảnh, tôi thấy bạn đã:
- ✅ Tạo database: `ads_automation`
- ✅ Tạo user: `adsuser` với password `@Levandat0312`
- ✅ Grant privileges
- ✅ Alter user CREATEDB
- ✅ Gõ `\q` để thoát psql

**VẤN ĐỀ:** Bạn vẫn đang trong heredoc (`<< EOF`), cần nhập `EOF` để kết thúc.

---

## 🔧 CÁCH SỬA

### **BƯỚC 1: Kết thúc heredoc**

Bạn đang thấy dấu `>` prompt. Hãy nhập:

```bash
EOF
```

**Sau khi nhập `EOF`, bạn sẽ thấy:**
```
CREATE DATABASE
CREATE ROLE
GRANT
ALTER ROLE
```

### **BƯỚC 2: Thoát root (nếu cần)**

```bash
exit
# Hoặc
logout
```

Bạn sẽ quay về user `ubuntu` hoặc `adsuser`.

---

## ✅ VERIFY SETUP

### **1. Test connection:**

```bash
# Test kết nối (sẽ hỏi password)
psql -U adsuser -d ads_automation -h localhost
```

**Nhập password:** `@Levandat0312`

**Nếu vào được psql prompt:**
```
psql (14.x)
Type "help" for help.

ads_automation=> 
```

**Thoát:**
```bash
\q
```

### **2. List databases:**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\l"
```

---

## 📝 UPDATE .ENV FILE

Bây giờ bạn cần update `.env` file với password:

```bash
cd ~/ads-automation
nano .env
```

**Tìm dòng:**
```bash
DATABASE_URL=postgresql://adsuser:your_secure_password@localhost:5432/ads_automation
```

**Thay thành:**
```bash
DATABASE_URL=postgresql://adsuser:@Levandat0312@localhost:5432/ads_automation
```

**⚠️ LƯU Ý:** Password có ký tự đặc biệt `@`, có thể cần URL encode:
```bash
# @ trong URL = %40
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
```

**Hoặc dùng format khác:**
```bash
# Nếu có vấn đề với @, thử escape
DATABASE_URL=postgresql://adsuser:@Levandat0312@localhost:5432/ads_automation
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🧪 TEST VỚI PYTHON

```bash
cd ~/ads-automation
source venv/bin/activate

# Test connection
python3 -c "
from app.core.config import get_settings
from app.core.database import init_db
try:
    init_db()
    print('✅ Database connection OK!')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

---

## 🔧 NẾU GẶP LỖI VỚI PASSWORD CÓ @

Nếu password `@Levandat0312` gây vấn đề với DATABASE_URL, có 2 cách:

### **Option 1: URL Encode**

```bash
# @ = %40
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
```

### **Option 2: Đổi password (nếu cần)**

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

- [ ] Nhập `EOF` để kết thúc heredoc
- [ ] Test connection: `psql -U adsuser -d ads_automation -h localhost`
- [ ] Update `.env` với password `@Levandat0312` (hoặc URL encode)
- [ ] Test với Python: `python scripts/init_db.py`

---

**Bây giờ hãy nhập `EOF` để kết thúc! 🚀**

