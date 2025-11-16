# 🔧 FIX LOGICRULE IMPORT ERROR

## ❌ VẤN ĐỀ

```
ImportError: cannot import name 'LogicRule' from 'app.core.database'
```

**Nguyên nhân:** `LogicRule` được định nghĩa trong `app/models/logic_rule.py`, không phải trong `app.core.database`.

---

## ✅ ĐÃ SỬA

Đã sửa import trong 3 files:
1. ✅ `app/services/logics.py`
2. ✅ `app/services/rule_template_service.py`
3. ✅ `app/api/routes/dashboard.py`

**Từ:**
```python
from app.core.database import get_db_session, LogicRule
```

**Thành:**
```python
from app.core.database import get_db_session
from app.models.logic_rule import LogicRule
```

---

## 🚀 CẬP NHẬT TRÊN VPS

### **BƯỚC 1: Pull code mới:**

```bash
cd ~/ads-automation
git pull origin main
```

### **BƯỚC 2: Xóa Python cache:**

```bash
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

### **BƯỚC 3: Restart API:**

```bash
sudo supervisorctl restart ads-automation-api
sudo supervisorctl status
```

### **BƯỚC 4: Test API:**

```bash
# Test trực tiếp
curl http://localhost:8000/health

# Test HTTPS
curl https://updatemetaads.site/health
```

**Kết quả mong đợi:**
```json
{"status":"healthy"}
```

---

## ✅ VERIFY

```bash
# Check API status
sudo supervisorctl status

# Check port 8000
sudo ss -tlnp | grep 8000

# Test API
curl http://localhost:8000/health
curl https://updatemetaads.site/health
```

---

**Bây giờ hãy pull code và restart API! 🚀**


