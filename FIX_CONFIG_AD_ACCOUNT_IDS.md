# 🔧 FIX CONFIG AD_ACCOUNT_IDS

## ❌ VẤN ĐỀ

Vẫn lỗi validation vì `AD_ACCOUNT_IDS` đang được parse thành list từ `.env`.

---

## ✅ GIẢI PHÁP

### **BƯỚC 1: Check file `.env`:**

```bash
cd ~/ads-automation
cat .env | grep "AD_ACCOUNT_IDS"
```

**Phải thấy:**
```env
AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636
```

**KHÔNG phải:**
```env
AD_ACCOUNT_IDS=['act_723686686812438', 'act_2827767517395636']
```

### **BƯỚC 2: Sửa file `.env` (nếu cần):**

```bash
cd ~/ads-automation
nano .env
```

**Tìm `AD_ACCOUNT_IDS` và đảm bảo format đúng:**
```env
AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636
```

**Lưu:** `Ctrl+X`, `Y`, `Enter`

### **BƯỚC 3: Check file `config.py`:**

```bash
cd ~/ads-automation
grep -A 5 "AD_ACCOUNT_IDS" app/core/config.py
```

**Phải thấy:**
```python
AD_ACCOUNT_IDS: Union[str, List[str]] = Field(..., env="AD_ACCOUNT_IDS")
```

**Nếu không có `Union[str, List[str]]`, cần sửa!**

### **BƯỚC 4: Sửa file `config.py` (nếu cần):**

```bash
cd ~/ads-automation
nano app/core/config.py
```

**Tìm dòng:**
```python
AD_ACCOUNT_IDS: str = Field(..., env="AD_ACCOUNT_IDS")
```

**Sửa thành:**
```python
from typing import List, Optional, Union

AD_ACCOUNT_IDS: Union[str, List[str]] = Field(..., env="AD_ACCOUNT_IDS")
```

**Lưu:** `Ctrl+X`, `Y`, `Enter`

### **BƯỚC 5: Xóa Python cache:**

```bash
cd ~/ads-automation
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

### **BƯỚC 6: Test lại:**

```bash
source venv/bin/activate
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'✅ AD_ACCOUNT_IDS: {settings.AD_ACCOUNT_IDS}')
print(f'✅ ad_account_ids_list: {settings.ad_account_ids_list}')
"
```

---

## 🚀 QUICK FIX

### **Sửa cả `.env` và `config.py`:**

```bash
cd ~/ads-automation

# 1. Sửa .env
sed -i "s/AD_ACCOUNT_IDS=.*/AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636/" .env

# 2. Check config.py có Union chưa
if ! grep -q "Union\[str, List\[str\]\]" app/core/config.py; then
    echo "⚠️  Need to fix config.py"
    # Sửa thủ công bằng nano
    nano app/core/config.py
fi

# 3. Xóa cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true

# 4. Test
source venv/bin/activate
python -c "from app.core.config import get_settings; s = get_settings(); print('✅ OK')"
```

---

## ✅ VERIFY

```bash
# Check .env
grep "AD_ACCOUNT_IDS" ~/ads-automation/.env

# Check config.py
grep "AD_ACCOUNT_IDS" ~/ads-automation/app/core/config.py

# Test
cd ~/ads-automation
source venv/bin/activate
python -c "from app.core.config import get_settings; s = get_settings(); print('✅ OK:', s.ad_account_ids_list)"
```

---

**Bây giờ hãy check và sửa cả `.env` và `config.py`! 🚀**


