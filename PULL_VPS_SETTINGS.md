# 🚀 PULL CODE LÊN VPS - SETTINGS & USER MANAGEMENT

## 📋 TÓM TẮT THAY ĐỔI

### ✅ Các tính năng mới:
1. **User Settings Model** - Lưu token Facebook (encrypted) cho mỗi user
2. **Account & Prefix Models** - Thêm `user_id` để mỗi user quản lý riêng
3. **AccountPrefix Model** - Liên kết Account với Prefix (1 account có nhiều prefix)
4. **Facebook Token Service** - Test token và sync accounts từ Facebook API
5. **Settings API Routes** - Đầy đủ CRUD cho token, accounts, prefixes
6. **Settings UI** - Trang settings hoàn chỉnh với modal add/edit

### 📁 Files mới:
- `app/models/user_settings.py` - UserSettings model
- `app/services/facebook_token_service.py` - Facebook token service
- `app/api/routes/settings.py` - Settings routes và UI

### 📝 Files đã sửa:
- `app/models/account_prefix.py` - Thêm user_id, AccountPrefix model
- `app/core/security.py` - Thêm encrypt/decrypt token functions
- `app/core/database.py` - Import UserSettings model
- `app/api/routes/auth.py` - Update get_current_user_optional để check cookie
- `app/api/routes/home.py` - Update link settings
- `app/main.py` - Include settings router

---

## 🔧 BƯỚC 1: PULL CODE TỪ GITHUB

```bash
cd ~/ads-automation
source venv/bin/activate

# Stash local changes (nếu có)
git stash

# Pull code mới nhất
git pull origin main

# Nếu có conflict, force pull
# git fetch origin
# git reset --hard origin/main
```

---

## 📦 BƯỚC 2: CÀI ĐẶT DEPENDENCIES

```bash
# Đảm bảo đang trong venv
source venv/bin/activate

# Install dependencies mới (nếu có)
pip install -r requirements.txt

# Verify cryptography đã được cài
pip show cryptography
```

---

## 🗄️ BƯỚC 3: MIGRATE DATABASE

### Tạo tables mới:

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import để tạo tables
python -c "
from app.core.database import init_db
init_db()
print('✅ Database initialized')
"
```

### Hoặc dùng Alembic (nếu có):

```bash
# Tạo migration
alembic revision --autogenerate -m "Add user_settings and update account_prefix models"

# Apply migration
alembic upgrade head
```

---

## ✅ BƯỚC 4: KIỂM TRA CODE

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import
python -c "
from app.main import app
from app.models.user_settings import UserSettings
from app.models.account_prefix import Account, Prefix, AccountPrefix
from app.services.facebook_token_service import test_facebook_token
print('✅ All imports OK')
"
```

---

## 🔄 BƯỚC 5: RESTART SERVICES

```bash
# Restart API service
sudo supervisorctl restart ads-automation-api

# Restart worker services
sudo supervisorctl restart ads-automation-worker:*

# Check status
sudo supervisorctl status
```

---

## 🧪 BƯỚC 6: TEST

### 1. Test trang Settings:
```
https://updatemetaads.site/settings
```

### 2. Test API endpoints:
```bash
# Test token status (cần đăng nhập trước)
curl -X GET "https://updatemetaads.site/settings/token/status" \
  -H "Cookie: access_token=YOUR_TOKEN"

# Test list accounts
curl -X GET "https://updatemetaads.site/settings/accounts" \
  -H "Cookie: access_token=YOUR_TOKEN"
```

---

## ⚠️ LƯU Ý

1. **Database Migration**: 
   - Tables mới sẽ được tạo tự động khi import models
   - Nếu có dữ liệu cũ trong `accounts` và `prefixes`, cần migrate:
     ```sql
     -- Set user_id cho accounts cũ (nếu có)
     UPDATE accounts SET user_id = 1 WHERE user_id IS NULL;
     UPDATE prefixes SET user_id = 1 WHERE user_id IS NULL;
     ```

2. **Token Encryption**:
   - Token được mã hóa bằng Fernet (từ SECRET_KEY)
   - Đảm bảo SECRET_KEY trong .env có ít nhất 32 ký tự

3. **Authentication**:
   - Settings page yêu cầu đăng nhập
   - Token được check từ cả cookie và Bearer header

---

## 🐛 TROUBLESHOOTING

### Lỗi: "ModuleNotFoundError: No module named 'cryptography'"
```bash
pip install cryptography
```

### Lỗi: "Table 'user_settings' already exists"
- Bỏ qua, table đã tồn tại là OK

### Lỗi: "Column 'user_id' does not exist"
- Cần migrate database:
  ```sql
  ALTER TABLE accounts ADD COLUMN user_id INTEGER;
  ALTER TABLE prefixes ADD COLUMN user_id INTEGER;
  ```

### Lỗi: "Cannot decrypt token"
- Token có thể đã được mã hóa với SECRET_KEY khác
- Cần lưu lại token mới

---

## 📝 QUICK COMMANDS

```bash
# Full pull và restart
cd ~/ads-automation && \
source venv/bin/activate && \
git pull origin main && \
pip install -r requirements.txt && \
python -c "from app.core.database import init_db; init_db()" && \
sudo supervisorctl restart ads-automation-api && \
sudo supervisorctl restart ads-automation-worker:*
```

---

## ✅ CHECKLIST

- [ ] Pull code từ GitHub
- [ ] Install dependencies
- [ ] Initialize database (tạo tables mới)
- [ ] Restart API service
- [ ] Restart worker services
- [ ] Test trang Settings
- [ ] Test lưu token
- [ ] Test sync accounts
- [ ] Test add/edit/delete account
- [ ] Test add/edit/delete prefix

---

**Sau khi hoàn thành, truy cập `https://updatemetaads.site/settings` để kiểm tra!** 🎉

