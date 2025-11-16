# 🔧 FIX INDENTATION ERROR

## 🔍 VẤN ĐỀ

Lỗi: `IndentationError: unexpected indent` ở dòng 21 trong `config.py`

**Nguyên nhân:** File có thể bị lỗi indentation sau khi merge hoặc có mixed tabs/spaces.

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Kiểm tra file trên VPS:**

```bash
cd ~/ads-automation
head -25 app/core/config.py
```

### **BƯỚC 2: Sửa file:**

```bash
nano app/core/config.py
```

**Kiểm tra dòng 18-22, phải giống như sau (4 spaces indentation):**

```python
    # ===== Facebook API =====
    ACCESS_TOKEN: str = Field(..., env="ACCESS_TOKEN")
    AD_ACCOUNT_IDS: Union[str, List[str]] = Field(..., env="AD_ACCOUNT_IDS")
    DATA_DATE_PRESET: str = Field(default="yesterday", env="DATA_DATE_PRESET")
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **BƯỚC 3: Verify syntax:**

```bash
python -m py_compile app/core/config.py
```

**Nếu không có lỗi** → OK

---

## 🔄 CÁCH 2: PULL LẠI TỪ GITHUB (NẾU FILE TRÊN GITHUB ĐÚNG)

### **Discard local changes và pull:**

```bash
cd ~/ads-automation

# Discard local changes
git checkout -- app/core/config.py

# Pull
git pull origin main

# Verify
python -m py_compile app/core/config.py
```

---

## 🔍 CHECK FILE TRÊN GITHUB

### **File trên GitHub có đúng không?**

Kiểm tra trên GitHub:
- https://github.com/LeDat0312/ads-automation/blob/main/app/core/config.py

**Nếu file trên GitHub đúng:**
- Dùng cách 2 (pull lại)

**Nếu file trên GitHub cũng sai:**
- Sửa trực tiếp trên VPS (cách 1)
- Commit và push lên GitHub

---

## ⚡ QUICK FIX

```bash
cd ~/ads-automation

# Discard và pull lại
git checkout -- app/core/config.py
git pull origin main

# Verify syntax
python -m py_compile app/core/config.py

# Test import
python -c "from app.core.config import get_settings; print('OK')"
```

---

**Chạy Quick Fix để sửa lỗi! 🚀**


