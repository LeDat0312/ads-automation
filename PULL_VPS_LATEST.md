# Hướng Dẫn Pull Code Mới Nhất Về VPS

## 📋 Các thay đổi mới nhất:
- ✅ Tách biệt trang cá nhân (`/profile`) và trang thay đổi mật khẩu (`/change-password`)
- ✅ Xóa card "Thông Tin Tài Khoản" khỏi trang chủ (đã có dropdown menu ở góc phải)
- ✅ Sửa lỗi f-string syntax trong dashboard.py
- ✅ Cải thiện UI và UX

## 🚀 Lệnh Pull Code (Script Nhanh):

```bash
cd ~/ads-automation && \
source venv/bin/activate && \
git pull origin main && \
python -m py_compile app/api/routes/profile.py && \
python -m py_compile app/api/routes/home.py && \
python -m py_compile app/api/routes/dashboard.py && \
python -m py_compile app/main.py && \
python -c "from app.main import app; print('✅ Import OK')" && \
sudo supervisorctl restart ads-automation-api && \
sleep 3 && \
sudo supervisorctl status ads-automation-api
```

## 📝 Lệnh Pull Code (Từng Bước):

```bash
# Bước 1: Vào thư mục dự án
cd ~/ads-automation

# Bước 2: Kích hoạt virtual environment
source venv/bin/activate

# Bước 3: Pull code mới nhất từ GitHub
git pull origin main

# Bước 4: Kiểm tra syntax các file đã thay đổi
python -m py_compile app/api/routes/profile.py
python -m py_compile app/api/routes/home.py
python -m py_compile app/api/routes/dashboard.py
python -m py_compile app/main.py

# Bước 5: Kiểm tra import
python -c "from app.main import app; print('✅ Import OK')"

# Bước 6: Restart service
sudo supervisorctl restart ads-automation-api
sleep 3

# Bước 7: Kiểm tra trạng thái
sudo supervisorctl status ads-automation-api

# Bước 8: Xem logs (nếu cần)
sudo supervisorctl tail -30 ads-automation-api
```

## 🔍 Kiểm Tra Lỗi (Nếu có):

```bash
# Kiểm tra logs của service
sudo supervisorctl tail -50 ads-automation-api

# Kiểm tra logs của nginx (nếu có lỗi 502)
sudo tail -50 /var/log/nginx/error.log

# Kiểm tra Python syntax
python -m py_compile app/api/routes/profile.py
python -m py_compile app/api/routes/home.py
python -m py_compile app/api/routes/dashboard.py
python -m py_compile app/main.py

# Kiểm tra import
python -c "from app.main import app; print('✅ Import OK')"
```

## 📌 Các Route Mới:
- `GET /change-password` - Trang thay đổi mật khẩu riêng biệt

## ⚠️ Lưu ý:
- Trang chủ đã bỏ card "Thông Tin Tài Khoản"
- Người dùng truy cập thông tin tài khoản qua dropdown menu ở góc phải màn hình
- Trang profile chỉ còn: thông tin cá nhân, quản lý avatar, chỉnh sửa thông tin, và nút link đến trang thay đổi mật khẩu

## ✅ Sau khi pull thành công:
1. Kiểm tra website hoạt động bình thường
2. Test trang `/profile` và `/change-password`
3. Kiểm tra dropdown menu ở góc phải màn hình
4. Xác nhận trang chủ không còn card "Thông Tin Tài Khoản"

