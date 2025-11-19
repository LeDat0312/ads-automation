# ✅ Fix 502 Bad Gateway - CAPTCHA Integration Issue

## 🔍 **Vấn Đề:**
```
502 Bad Gateway
nginx/1.18.0 (Ubuntu)
```

Sau khi thêm chức năng đăng ký với CAPTCHA, backend crash và không khởi động được.

---

## 🎯 **Nguyên Nhân Chính:**

### **1. ❌ Lỗi StreamingResponse.set_cookie() (ĐÃ FIX)**

**Code CŨ (SAI):**
```python
@router.get("/captcha")
async def get_captcha(response: Response):  # ← Tham số response không dùng
    image_bytes = generate_captcha_image(text)
    
    # StreamingResponse KHÔNG HỖ TRỢ set_cookie trực tiếp!
    response = StreamingResponse(image_bytes, media_type="image/png")
    response.set_cookie(...)  # ❌ AttributeError!
```

**Code MỚI (ĐÚNG):**
```python
@router.get("/captcha")
async def get_captcha():  # ← Bỏ tham số response
    image_bytes = generate_captcha_image(text)
    captcha_hash = hash_captcha(text, settings.SECRET_KEY)
    
    # Đọc bytes từ BytesIO
    content = image_bytes.read()
    
    # Dùng Response thay vì StreamingResponse
    response = Response(content=content, media_type="image/png")
    response.set_cookie(
        key="captcha_hash",
        value=captcha_hash,
        httponly=True,
        max_age=300,
        samesite="lax"
    )
    return response  # ✅ OK!
```

**Lý do:**
- `StreamingResponse` dùng cho stream data (file lớn, video, etc.)
- `Response` dùng cho binary data nhỏ (như ảnh CAPTCHA)
- Chỉ `Response` mới có method `set_cookie()` hoạt động đúng

---

### **2. ⚠️ Thiếu Pillow (Có thể xảy ra)**

**Lỗi:**
```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter
# ModuleNotFoundError: No module named 'PIL'
```

**Fix:**
```bash
pip install Pillow
```

**Đã có trong requirements.txt:**
```
Pillow==10.1.0
```

---

### **3. ✅ SECRET_KEY đã được cấu hình**

File `app/core/config.py`:
```python
SECRET_KEY: str = Field(..., env="SECRET_KEY", min_length=32)
```

Nếu thiếu trong `.env`:
```bash
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

---

## 🔧 **Các Thay Đổi Đã Thực Hiện:**

### **File: `app/api/routes/auth.py`**

**Thay đổi:** Fix `get_captcha()` endpoint

```diff
@router.get("/captcha")
-async def get_captcha(response: Response):
+async def get_captcha():
    """Generate CAPTCHA image"""
    text = generate_captcha_text()
    image_bytes = generate_captcha_image(text)
    
-   # Create hash and set cookie
    captcha_hash = hash_captcha(text, settings.SECRET_KEY)
    
-   # Return image
-   response = StreamingResponse(image_bytes, media_type="image/png")
+   # Read bytes from BytesIO
+   content = image_bytes.read()
+   
+   # Return image with cookie (use Response instead of StreamingResponse)
+   response = Response(content=content, media_type="image/png")
    response.set_cookie(
        key="captcha_hash",
        value=captcha_hash,
        httponly=True,
        max_age=300,
        samesite="lax"
    )
    return response
```

---

## 📋 **Script Tự Động Fix Trên VPS:**

Tôi đã tạo `fix_502_backend.sh` với các bước:

1. ✅ Check virtualenv
2. ✅ Install Pillow nếu thiếu
3. ✅ Check SECRET_KEY trong .env
4. ✅ Test Python imports
5. ✅ Restart backend service
6. ✅ Test CAPTCHA endpoint
7. ✅ Health check

**Chạy trên VPS:**
```bash
# Upload file fix_502_backend.sh lên VPS
scp fix_502_backend.sh user@your-vps:/path/to/

# SSH vào VPS
ssh user@your-vps

# Sửa tên service trong script
nano fix_502_backend.sh
# Đổi "your-backend-service" thành tên service thực tế
# Ví dụ: "ads-automation" hoặc "uvicorn"

# Chạy
chmod +x fix_502_backend.sh
sudo ./fix_502_backend.sh
```

---

## ✅ **Kiểm Tra Thủ Công:**

### **Bước 1: Pull code mới**
```bash
cd /path/to/ads-automation
git pull origin main
```

### **Bước 2: Cài dependencies**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### **Bước 3: Test imports**
```bash
python3 << EOF
from app.core.captcha import generate_captcha_text
from app.api.routes.auth import router
from app.main import app
print("✅ All imports OK")
EOF
```

### **Bước 4: Test chạy thủ công**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Quan sát console:**
- ✅ Nếu start OK → Không có lỗi syntax
- ❌ Nếu crash → Xem lỗi gì và fix

### **Bước 5: Restart service**
```bash
sudo systemctl restart your-backend-service
sudo systemctl status your-backend-service
```

### **Bước 6: Test endpoints**
```bash
# Test health
curl http://localhost:8000/api/health

# Test CAPTCHA
curl http://localhost:8000/auth/captcha -o /tmp/test.png
file /tmp/test.png  # Should say "PNG image data"

# Test register page
curl -I http://localhost:8000/auth/register
# Should return 200 OK
```

---

## 🐛 **Troubleshooting:**

### **Vẫn lỗi 502 sau khi fix?**

**Kiểm tra logs:**
```bash
# Backend log
sudo journalctl -u your-backend-service -n 100 --no-pager

# Nginx log
sudo tail -100 /var/log/nginx/error.log
```

**Tìm lỗi:**
- `ModuleNotFoundError` → Thiếu package, chạy `pip install -r requirements.txt`
- `AttributeError` → Lỗi code, xem stack trace
- `Connection refused` → Backend chưa chạy hoặc port sai
- `ImportError` → Syntax error trong Python code

---

## 📊 **Checklist:**

- [x] Fix `get_captcha()` endpoint (StreamingResponse → Response)
- [x] Pillow trong requirements.txt
- [x] SECRET_KEY trong config.py
- [x] captcha.py không có lỗi syntax
- [x] auth.py imports đúng
- [x] Tạo script auto-fix cho VPS
- [x] Tạo hướng dẫn troubleshooting

---

## 🚀 **Kết Quả Mong Đợi:**

Sau khi fix:
- ✅ Backend start thành công
- ✅ `/auth/register` hiển thị trang đăng ký
- ✅ `/auth/captcha` trả về ảnh PNG
- ✅ CAPTCHA verify hoạt động
- ✅ Đăng ký user mới thành công
- ✅ Website không còn lỗi 502

---

## 📞 **Nếu Vẫn Lỗi:**

Gửi cho tôi output của:

```bash
# 1. Import test
python3 -c "from app.main import app; print('OK')" 2>&1

# 2. Backend log
sudo journalctl -u your-backend-service -n 50 --no-pager

# 3. Check Pillow
pip list | grep Pillow

# 4. Test manual run
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Copy error messages
```

Tôi sẽ fix ngay!
