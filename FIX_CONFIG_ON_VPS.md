# 🔧 FIX CONFIG.PY TRÊN VPS

## ❌ VẤN ĐỀ

Code trên VPS chưa được cập nhật, vẫn còn lỗi validation.

---

## ✅ SỬA TRỰC TIẾP TRÊN VPS

### **BƯỚC 1: Check file hiện tại:**

```bash
cd ~/ads-automation
grep -A 2 "AD_ACCOUNT_IDS:" app/core/config.py
```

**Nếu thấy:**
```python
AD_ACCOUNT_IDS: Union[str, List[str]] = Field(..., env="AD_ACCOUNT_IDS")
```

**Cần sửa thành:**
```python
AD_ACCOUNT_IDS: str = Field(..., env="AD_ACCOUNT_IDS")
```

### **BƯỚC 2: Check validator:**

```bash
grep -A 10 "@validator" app/core/config.py
```

**Nếu thấy `@validator('AD_ACCOUNT_IDS', pre=True)`, cần xóa decorator này!**

### **BƯỚC 3: Sửa file config.py:**

```bash
cd ~/ads-automation
nano app/core/config.py
```

**Tìm và sửa:**

1. **Dòng type hint (khoảng dòng 20):**
   ```python
   # Từ:
   AD_ACCOUNT_IDS: Union[str, List[str]] = Field(..., env="AD_ACCOUNT_IDS")
   
   # Thành:
   AD_ACCOUNT_IDS: str = Field(..., env="AD_ACCOUNT_IDS")
   ```

2. **Tìm `@validator('AD_ACCOUNT_IDS', pre=True)` (khoảng dòng 47):**
   ```python
   # XÓA dòng này:
   @validator('AD_ACCOUNT_IDS', pre=True)
   
   # Sửa function thành method (thêm self):
   def parse_ad_account_ids(self, v: str = None) -> List[str]:
       """Parse AD_ACCOUNT_IDS từ string sang list"""
       if v is None:
           v = self.AD_ACCOUNT_IDS
       # ... (phần còn lại giữ nguyên)
   ```

3. **Sửa property `ad_account_ids_list` (khoảng dòng 70):**
   ```python
   @property
   def ad_account_ids_list(self) -> List[str]:
       """Trả về AD_ACCOUNT_IDS dạng list"""
       return self.parse_ad_account_ids(self.AD_ACCOUNT_IDS)
   ```

**Lưu:** `Ctrl+X`, `Y`, `Enter`

---

## 🚀 HOẶC SỬA BẰNG SED (NHANH HƠN)

```bash
cd ~/ads-automation

# Backup
cp app/core/config.py app/core/config.py.backup

# Sửa type hint
sed -i 's/AD_ACCOUNT_IDS: Union\[str, List\[str\]\]/AD_ACCOUNT_IDS: str/' app/core/config.py

# Xóa @validator decorator
sed -i '/@validator.*AD_ACCOUNT_IDS/d' app/core/config.py

# Sửa function signature (thêm self)
sed -i 's/def parse_ad_account_ids(cls, v):/def parse_ad_account_ids(self, v: str = None) -> List[str]:/' app/core/config.py

# Thêm check v is None
sed -i '/def parse_ad_account_ids/a\        if v is None:\n            v = self.AD_ACCOUNT_IDS' app/core/config.py

# Sửa property
sed -i '/def ad_account_ids_list/,/return self.parse_ad_account_ids/{
    /if isinstance(self.AD_ACCOUNT_IDS, list):/d
    /return self.AD_ACCOUNT_IDS/d
}' app/core/config.py
```

---

## ✅ VERIFY SAU KHI SỬA

```bash
# Check type hint
grep "AD_ACCOUNT_IDS:" app/core/config.py

# Phải thấy: AD_ACCOUNT_IDS: str

# Check không còn @validator
grep "@validator.*AD_ACCOUNT_IDS" app/core/config.py

# Phải không có kết quả

# Check function signature
grep -A 2 "def parse_ad_account_ids" app/core/config.py

# Phải thấy: def parse_ad_account_ids(self, v: str = None)
```

---

## 🧪 TEST

```bash
cd ~/ads-automation
source venv/bin/activate

# Xóa cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true

# Test
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'✅ AD_ACCOUNT_IDS: {settings.AD_ACCOUNT_IDS}')
print(f'✅ Type: {type(settings.AD_ACCOUNT_IDS)}')
print(f'✅ ad_account_ids_list: {settings.ad_account_ids_list}')
"
```

---

**Bây giờ hãy sửa file config.py trên VPS! 🚀**


