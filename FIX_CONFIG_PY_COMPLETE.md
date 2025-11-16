# 🔧 FIX CONFIG.PY - CODE HOÀN CHỈNH

## 📝 CODE ĐÃ ĐƯỢC SỬA

File `app/core/config.py` đã được viết lại hoàn chỉnh với:
- ✅ Import `Union` từ typing
- ✅ `AD_ACCOUNT_IDS: Union[str, List[str]]` để hỗ trợ cả string và list
- ✅ Indentation đúng (4 spaces)
- ✅ Tất cả imports đầy đủ

---

## 🔄 CÁCH CẬP NHẬT TRÊN VPS

### **BƯỚC 1: Sửa file trên VPS:**

```bash
cd ~/ads-automation
nano app/core/config.py
```

### **BƯỚC 2: Thay thế toàn bộ nội dung:**

**Xóa toàn bộ và paste code mới từ file đã fix.**

**Hoặc copy từ GitHub sau khi push.**

---

## 📤 HOẶC PULL TỪ GITHUB

### **Sau khi code đã được push lên GitHub:**

```bash
cd ~/ads-automation
git pull origin main
```

---

## ✅ VERIFY

### **Test syntax:**

```bash
python3 -m py_compile app/core/config.py
```

### **Test import:**

```bash
source venv/bin/activate
python -c "from app.core.config import get_settings; print('✅ Import OK')"
```

### **Test settings:**

```bash
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'DATABASE_URL: {settings.DATABASE_URL[:50]}...')
print(f'AD_ACCOUNT_IDS: {settings.AD_ACCOUNT_IDS}')
print('✅ Settings OK')
"
```

---

## 🚀 SAU KHI FIX

### **Chạy init_db:**

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

---

**File đã được fix! Hãy update trên VPS và test lại! 🚀**


