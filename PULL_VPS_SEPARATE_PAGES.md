# Hướng Dẫn Pull Code Về VPS

## Các thay đổi mới nhất:
- ✅ Tách biệt trang cá nhân và trang thay đổi mật khẩu
- ✅ Thêm tính năng xóa tài khoản
- ✅ Xóa card "Thông Tin Tài Khoản" khỏi trang chủ (đã có dropdown menu)

## Lệnh Pull Code:

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
python -m py_compile app/main.py

# Bước 5: Kiểm tra import
python -c "from app.main import app; print('✅ Import OK')"

# Bước 6: Restart services
sudo supervisorctl restart ads-automation-api
sleep 3

# Bước 7: Kiểm tra trạng thái
sudo supervisorctl status ads-automation-api

# Bước 8: Xem logs (nếu cần)
sudo supervisorctl tail -30 ads-automation-api
```

## Script nhanh (copy toàn bộ và chạy):

```bash
cd ~/ads-automation && \
source venv/bin/activate && \
git pull origin main && \
python -m py_compile app/api/routes/profile.py && \
python -m py_compile app/api/routes/home.py && \
python -m py_compile app/main.py && \
python -c "from app.main import app; print('✅ Import OK')" && \
sudo supervisorctl restart ads-automation-api && \
sleep 3 && \
sudo supervisorctl status ads-automation-api
```

## Các route mới:
- `GET /change-password` - Trang thay đổi mật khẩu riêng biệt
- `DELETE /profile/delete` - Xóa tài khoản và tất cả dữ liệu liên quan

## Lưu ý:
- Trang chủ đã bỏ card "Thông Tin Tài Khoản"
- Người dùng truy cập thông tin tài khoản qua dropdown menu ở góc phải
- Tính năng xóa tài khoản yêu cầu xác nhận kép (confirm + nhập "XÓA")

