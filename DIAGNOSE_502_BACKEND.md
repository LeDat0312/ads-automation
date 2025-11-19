# 🔍 Chẩn Đoán Lỗi 502 Bad Gateway - Backend Crash

## ❌ Triệu chứng:
```
502 Bad Gateway
nginx/1.18.0 (Ubuntu)
```

## 🎯 Nguyên nhân phổ biến sau khi thêm CAPTCHA:

### **1. Thiếu thư viện Pillow (PIL)**

**Lỗi:**
```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter
# ModuleNotFoundError: No module named 'PIL'
```

**Giải pháp VPS:**
```bash
# SSH vào VPS
ssh user@your-vps-ip

# Di chuyển vào thư mục project
cd /path/to/ads-automation

# Activate virtualenv (nếu có)
source venv/bin/activate

# Cài Pillow
pip install Pillow

# Restart backend
sudo systemctl restart your-backend-service
```

---

### **2. Lỗi import trong auth.py**

**Kiểm tra:**
```bash
# Test import trên VPS
cd /path/to/ads-automation
python3 -c "from app.core.captcha import generate_captcha_text, generate_captcha_image, hash_captcha, verify_captcha"
```

**Nếu lỗi:** Cài thiếu package hoặc fix syntax error

---

### **3. SECRET_KEY chưa được cấu hình**

**Lỗi:**
```python
# app/api/routes/auth.py line 63
captcha_hash = hash_captcha(text, settings.SECRET_KEY)
# AttributeError: 'Settings' object has no attribute 'SECRET_KEY'
```

**Fix:** Thêm SECRET_KEY vào `.env`
```bash
# Trên VPS
cd /path/to/ads-automation
nano .env

# Thêm dòng này:
SECRET_KEY=your-super-secret-key-here-change-this-in-production

# Save (Ctrl+O, Enter, Ctrl+X)
```

---

### **4. Backend crash do syntax error**

**Kiểm tra:**
```bash
# Test chạy backend thủ công
cd /path/to/ads-automation
source venv/bin/activate
python3 -m app.main
# HOẶC
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Xem lỗi gì xuất hiện
```

---

## 📋 **Script Chẩn Đoán Tự Động:**

Tạo file `diagnose_backend.sh` trên VPS:

```bash
#!/bin/bash
echo "=== 🔍 Backend Diagnostic ==="
echo ""

echo "1️⃣ Check Python process:"
ps aux | grep uvicorn | grep -v grep || echo "❌ Backend NOT running"
echo ""

echo "2️⃣ Check port 8000:"
sudo netstat -tulpn | grep :8000 || echo "❌ Port 8000 not listening"
echo ""

echo "3️⃣ Test Python imports:"
python3 << EOF
try:
    from PIL import Image
    print("✅ Pillow installed")
except ImportError:
    print("❌ Pillow NOT installed - run: pip install Pillow")

try:
    from app.core.captcha import generate_captcha_text
    print("✅ captcha.py imports OK")
except Exception as e:
    print(f"❌ captcha.py error: {e}")

try:
    from app.api.routes.auth import router
    print("✅ auth.py imports OK")
except Exception as e:
    print(f"❌ auth.py error: {e}")

try:
    from app.core.config import get_settings
    settings = get_settings()
    if hasattr(settings, 'SECRET_KEY'):
        print("✅ SECRET_KEY configured")
    else:
        print("❌ SECRET_KEY NOT configured - add to .env")
except Exception as e:
    print(f"❌ Settings error: {e}")
EOF
echo ""

echo "4️⃣ Backend logs (last 30 lines):"
sudo journalctl -u your-backend-service -n 30 --no-pager || echo "❌ Cannot read logs"
echo ""

echo "5️⃣ Nginx error log:"
sudo tail -20 /var/log/nginx/error.log
echo ""

echo "=== End Diagnostic ==="
```

**Chạy:**
```bash
chmod +x diagnose_backend.sh
./diagnose_backend.sh
```

---

## ✅ **Fix Từng Bước:**

### **Bước 1: Cài Pillow**
```bash
pip install Pillow
```

### **Bước 2: Thêm SECRET_KEY vào .env**
```bash
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

### **Bước 3: Kiểm tra config.py có SECRET_KEY field**

Mở `app/core/config.py` và đảm bảo có:
```python
class Settings(BaseSettings):
    SECRET_KEY: str = "default-secret-key-change-this"
    # ... other fields
```

### **Bước 4: Test chạy backend thủ công**
```bash
cd /path/to/ads-automation
source venv/bin/activate
python3 -c "from app.main import app; print('✅ Import OK')"

# Nếu OK, chạy:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Quan sát console để thấy lỗi gì xuất hiện**

### **Bước 5: Restart service**
```bash
sudo systemctl restart your-backend-service
sudo systemctl status your-backend-service
```

### **Bước 6: Test API**
```bash
curl http://localhost:8000/auth/captcha -o /tmp/test.png
file /tmp/test.png  # Should say "PNG image data"

curl http://localhost:8000/api/health
# Should return: {"status": "healthy", ...}
```

---

## 🐛 **Lỗi Phổ Biến Khác:**

### **Lỗi 1: ImportError - PIL**
```
ModuleNotFoundError: No module named 'PIL'
```
**Fix:**
```bash
pip install Pillow
```

### **Lỗi 2: AttributeError - SECRET_KEY**
```
AttributeError: 'Settings' object has no attribute 'SECRET_KEY'
```
**Fix:** Thêm vào `app/core/config.py`:
```python
SECRET_KEY: str = "change-this-secret-key"
```

### **Lỗi 3: Font file not found**
```
OSError: cannot open resource
```
**Fix:** `captcha.py` đã dùng `ImageFont.load_default()` nên không cần font file

### **Lỗi 4: Response has no attribute set_cookie**
```python
# Lỗi ở auth.py line 79-80
response = StreamingResponse(...)
response.set_cookie(...)  # ← Sai!
```
**Fix:**
```python
# Cách đúng:
from fastapi.responses import Response
response = Response(content=image_bytes.read(), media_type="image/png")
response.set_cookie(...)
```

---

## 🔧 **Fix Code Nếu Cần:**

### **Fix 1: Sửa get_captcha endpoint**

Nếu lỗi `set_cookie` không work với `StreamingResponse`:

```python
@router.get("/captcha")
async def get_captcha():
    """Generate CAPTCHA image"""
    text = generate_captcha_text()
    image_bytes = generate_captcha_image(text)
    
    # Create hash
    captcha_hash = hash_captcha(text, settings.SECRET_KEY)
    
    # Read bytes for Response
    content = image_bytes.read()
    
    # Return image with cookie
    response = Response(content=content, media_type="image/png")
    response.set_cookie(
        key="captcha_hash",
        value=captcha_hash,
        httponly=True,
        max_age=300,
        samesite="lax"
    )
    return response
```

### **Fix 2: Thêm SECRET_KEY vào config.py**

Nếu chưa có:

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "default-secret-key-CHANGE-THIS-IN-PRODUCTION"
    DATABASE_URL: str
    # ... other fields
    
    class Config:
        env_file = ".env"
```

---

## 📊 **Log Mẫu Khi Backend Crash:**

```
[ERROR] ModuleNotFoundError: No module named 'PIL'
  File "app/core/captcha.py", line 5, in <module>
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
```

```
[ERROR] AttributeError: 'Settings' object has no attribute 'SECRET_KEY'
  File "app/api/routes/auth.py", line 63, in get_captcha
    captcha_hash = hash_captcha(text, settings.SECRET_KEY)
```

```
[ERROR] AttributeError: 'StreamingResponse' object has no attribute 'set_cookie'
  File "app/api/routes/auth.py", line 74, in get_captcha
    response.set_cookie(...)
```

---

## ✅ **Checklist Fix 502:**

- [ ] Pillow đã cài: `pip list | grep Pillow`
- [ ] SECRET_KEY trong .env: `grep SECRET_KEY .env`
- [ ] Backend imports OK: `python3 -c "from app.main import app"`
- [ ] Backend đang chạy: `ps aux | grep uvicorn`
- [ ] Port 8000 listening: `netstat -tulpn | grep :8000`
- [ ] Test CAPTCHA API: `curl http://localhost:8000/auth/captcha -o test.png`
- [ ] Test health check: `curl http://localhost:8000/api/health`
- [ ] Nginx config OK: `sudo nginx -t`

---

## 🚀 **Script Fix Tất Cả:**

```bash
#!/bin/bash
echo "🔧 Fixing 502 Backend Errors..."

# 1. Install Pillow
echo "📦 Installing Pillow..."
pip install Pillow

# 2. Add SECRET_KEY if not exists
if ! grep -q "SECRET_KEY" .env; then
    echo "🔑 Adding SECRET_KEY to .env..."
    echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
fi

# 3. Test imports
echo "🧪 Testing Python imports..."
python3 << EOF
from app.main import app
from app.core.captcha import generate_captcha_text
print("✅ All imports OK")
EOF

# 4. Restart backend
echo "🔄 Restarting backend..."
sudo systemctl restart your-backend-service
sleep 3

# 5. Check status
echo "📊 Checking status..."
sudo systemctl status your-backend-service --no-pager | head -10

echo "✅ Fix completed!"
echo "🧪 Test: curl http://localhost:8000/auth/captcha -o /tmp/test.png"
```

---

## 📞 **Gửi Log Cho Tôi:**

Nếu vẫn lỗi, gửi output của:

```bash
# 1. Backend logs
sudo journalctl -u your-backend-service -n 50 --no-pager

# 2. Python test
python3 << EOF
try:
    from app.main import app
    print("✅ app.main imports OK")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
EOF

# 3. Package check
pip list | grep -i pillow

# 4. .env check
grep SECRET_KEY .env
```

Tôi sẽ fix cụ thể dựa trên lỗi!
