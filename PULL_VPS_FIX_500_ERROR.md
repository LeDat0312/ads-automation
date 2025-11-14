# 🔧 HƯỚNG DẪN SỬA LỖI HTTP 500 - SETTINGS PAGE

## 📋 VẤN ĐỀ

Lỗi HTTP 500 khi:
- Tải danh sách accounts (`/settings/accounts`)
- Tải danh sách prefixes (`/settings/prefixes`)
- Đồng bộ accounts từ Facebook (`/settings/accounts/sync`)

## 🔍 NGUYÊN NHÂN

Có thể do:
1. Database chưa có cột `user_id` trong bảng `accounts` và `prefixes`
2. Lỗi khi query database
3. Thiếu error handling trong code

## ✅ GIẢI PHÁP

### BƯỚC 1: Pull code mới nhất

```bash
cd ~/ads-automation
source venv/bin/activate
git pull origin main
```

### BƯỚC 2: Kiểm tra và sửa database

```bash
# Chạy script kiểm tra và sửa database
python scripts/check_and_fix_database.py
```

Script này sẽ:
- Kiểm tra xem các bảng `accounts`, `prefixes`, `account_prefixes` có cột `user_id` chưa
- Nếu thiếu, sẽ tự động thêm cột `user_id` và các index/foreign key cần thiết

### BƯỚC 3: Khởi tạo lại database (nếu cần)

Nếu script trên không chạy được, có thể khởi tạo lại database:

```bash
# Khởi tạo database (sẽ tạo tất cả tables nếu chưa có)
python -c "from app.core.database import init_db; init_db()"
```

### BƯỚC 4: Restart services

```bash
sudo supervisorctl restart ads-automation-api
sudo supervisorctl status ads-automation-api
```

### BƯỚC 5: Kiểm tra logs

```bash
# Xem logs lỗi
sudo tail -50 /var/log/ads-automation/api.err.log

# Xem logs thông thường
sudo tail -50 /var/log/ads-automation/api.log
```

## 🔍 KIỂM TRA THỦ CÔNG

Nếu vẫn còn lỗi, kiểm tra thủ công:

```bash
# Kết nối PostgreSQL
psql -U adsuser -d ads_automation

# Kiểm tra cấu trúc bảng accounts
\d accounts

# Kiểm tra cấu trúc bảng prefixes
\d prefixes

# Kiểm tra cấu trúc bảng users
\d users

# Nếu thiếu cột user_id, thêm thủ công:
ALTER TABLE accounts ADD COLUMN user_id INTEGER;
CREATE INDEX ix_accounts_user_id ON accounts(user_id);
ALTER TABLE accounts ADD CONSTRAINT fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE prefixes ADD COLUMN user_id INTEGER;
CREATE INDEX ix_prefixes_user_id ON prefixes(user_id);
ALTER TABLE prefixes ADD CONSTRAINT fk_prefixes_user_id FOREIGN KEY (user_id) REFERENCES users(id);

# Thoát
\q
```

## 📝 LƯU Ý

- **Backup database trước khi chạy migration**: Nếu có dữ liệu quan trọng, hãy backup trước
- **Kiểm tra logs**: Luôn kiểm tra logs để xem lỗi cụ thể
- **Test sau khi sửa**: Sau khi sửa, test lại các chức năng trên settings page

## 🆘 NẾU VẪN LỖI

Nếu vẫn còn lỗi sau khi làm các bước trên:

1. **Kiểm tra logs chi tiết**:
   ```bash
   sudo tail -100 /var/log/ads-automation/api.err.log | grep -A 10 "Error"
   ```

2. **Kiểm tra database connection**:
   ```bash
   python -c "from app.core.database import get_db_session; db = get_db_session(); print('✅ Database OK')"
   ```

3. **Kiểm tra models**:
   ```bash
   python -c "from app.models.account_prefix import Account, Prefix; print('✅ Models OK')"
   ```

4. **Gửi logs cho developer**: Copy toàn bộ error logs và gửi để được hỗ trợ

