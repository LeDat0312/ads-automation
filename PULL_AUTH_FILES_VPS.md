# 🚀 PULL AUTHENTICATION FILES LÊN VPS

## 📋 CÁC FILE MỚI ĐÃ TẠO

1. `app/models/user.py` - User model
2. `app/core/security.py` - Security utilities (JWT, password hashing)
3. `scripts/create_admin_user.py` - Script tạo admin user
4. `app/core/database.py` - Đã cập nhật để import User model
5. `requirements.txt` - Đã thêm dependencies: `python-jose[cryptography]` và `passlib[bcrypt]`

---

## 🔧 BƯỚC 1: COMMIT VÀ PUSH TỪ LOCAL

### **Trên máy local (Windows PowerShell):**

```powershell
# Vào thư mục project
cd "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"

# Kiểm tra trạng thái
git status

# Add các file mới
git add app/models/user.py
git add app/core/security.py
git add scripts/create_admin_user.py
git add app/core/database.py
git add requirements.txt

# Commit
git commit -m "Add authentication system: User model, security utilities, and create_admin_user script"

# Push lên GitHub
git push origin main
```

---

## 🔧 BƯỚC 2: PULL TRÊN VPS

### **Trên VPS (SSH vào server):**

```bash
# Vào thư mục project
cd ~/ads-automation

# Activate virtual environment
source venv/bin/activate

# Pull code mới nhất
git stash
git pull origin main

# Kiểm tra các file đã có
ls -la app/models/user.py
ls -la app/core/security.py
ls -la scripts/create_admin_user.py

# Cài đặt dependencies mới
pip install python-jose[cryptography] passlib[bcrypt]

# Kiểm tra import
python -c "from app.models.user import User; from app.core.security import get_password_hash; print('✅ Import OK')"
```

---

## 🔧 BƯỚC 3: TẠO ADMIN USER

### **Chạy script tạo admin user:**

```bash
# Đảm bảo đang trong virtual environment
source venv/bin/activate

# Chạy script
python scripts/create_admin_user.py
```

**Script sẽ hỏi:**
- Username: (nhập username, ví dụ: `admin`)
- Email: (nhập email, ví dụ: `admin@example.com`)
- Password: (nhập password, sẽ không hiện khi gõ)
- Confirm Password: (nhập lại password)
- Display Name: (tùy chọn, nhấn Enter để dùng username)

**Ví dụ:**
```
Username: admin
Email: admin@example.com
Password: ********
Confirm Password: ********
Display Name (optional, press Enter for default): Admin User
```

---

## 🔧 BƯỚC 4: RESTART SERVICES (NẾU CẦN)

### **Nếu đã chạy API service, restart để load User model:**

```bash
# Restart API service
sudo supervisorctl restart ads-automation-api

# Kiểm tra status
sudo supervisorctl status ads-automation-api
```

---

## ✅ VERIFY

### **Kiểm tra database có bảng users:**

```bash
# Kết nối PostgreSQL
psql -U adsuser -d ads_automation

# Kiểm tra bảng users
\dt users

# Xem cấu trúc bảng
\d users

# Xem users đã tạo
SELECT id, username, email, role, is_active FROM users;

# Thoát
\q
```

---

## 🐛 TROUBLESHOOTING

### **Lỗi: "ModuleNotFoundError: No module named 'jose'"**

```bash
pip install python-jose[cryptography]
```

### **Lỗi: "ModuleNotFoundError: No module named 'passlib'"**

```bash
pip install passlib[bcrypt]
```

### **Lỗi: "SECRET_KEY không được để trống"**

Kiểm tra file `.env` có `SECRET_KEY`:
```bash
grep SECRET_KEY .env
```

Nếu chưa có, thêm vào `.env`:
```bash
# Tạo SECRET_KEY ngẫu nhiên
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Thêm vào .env
echo "SECRET_KEY=your_generated_secret_key_here" >> .env
```

### **Lỗi: "User already exists"**

User đã tồn tại trong database. Có thể:
- Dùng username/email khác
- Hoặc xóa user cũ trong database

---

## 📝 QUICK COMMANDS (COPY & PASTE)

### **Trên VPS:**

```bash
cd ~/ads-automation && source venv/bin/activate && git stash && git pull origin main && pip install -q python-jose[cryptography] passlib[bcrypt] && python -c "from app.models.user import User; print('✅ OK')" && python scripts/create_admin_user.py
```

---

**Sau khi hoàn thành, bạn sẽ có:**
- ✅ User model trong database
- ✅ Admin user để đăng nhập
- ✅ Authentication system sẵn sàng sử dụng

