# 🔧 Hướng dẫn Sửa Lỗi Database và Service trên VPS

## ❌ Lỗi gặp phải:

1. **Database không tồn tại:**
   ```
   psql: error: database "ads_automation_db" does not exist
   ```

2. **Service failed:**
   ```
   ads-automation.service: activating (auto-restart) (Result: exit-code)
   Process: ... (code=exited, status=1/FAILURE)
   ```

---

## 🔍 Bước 1: Kiểm tra DATABASE_URL trong .env

```bash
cd /home/adsuser/ads-automation
cat .env | grep DATABASE_URL
```

**Lưu ý:** Tên database được lấy từ `DATABASE_URL`, có thể không phải `ads_automation_db`.

Ví dụ:
- `postgresql://user:pass@localhost/ads_db` → database name là `ads_db`
- `postgresql://user:pass@localhost:5432/automation` → database name là `automation`

---

## 🔧 Bước 2: Tạo Database (nếu chưa có)

### 2.1. Lấy tên database từ DATABASE_URL

```bash
cd /home/adsuser/ads-automation
DB_URL=$(grep DATABASE_URL .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
echo "Database URL: $DB_URL"

# Extract database name
DB_NAME=$(echo $DB_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
echo "Database name: $DB_NAME"
```

### 2.2. Tạo database

```bash
# Kết nối PostgreSQL như superuser
sudo -u postgres psql

# Hoặc nếu có user riêng
psql -U postgres
```

Trong PostgreSQL shell:

```sql
-- Kiểm tra database có tồn tại không
\l

-- Nếu chưa có, tạo database mới
CREATE DATABASE your_database_name;

-- Tạo user nếu chưa có (thay your_user, your_password)
CREATE USER your_user WITH PASSWORD 'your_password';

-- Cấp quyền
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_user;

-- Thoát
\q
```

**Hoặc dùng lệnh một dòng:**

```bash
# Lấy thông tin từ .env
cd /home/adsuser/ads-automation
DB_URL=$(grep DATABASE_URL .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")

# Extract components (adjust based on your format)
DB_USER=$(echo $DB_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DB_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_NAME=$(echo $DB_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_HOST=$(echo $DB_URL | sed -n 's/.*@\([^:]*\).*/\1/p')

echo "User: $DB_USER"
echo "Database: $DB_NAME"
echo "Host: $DB_HOST"

# Tạo database
sudo -u postgres createdb -O $DB_USER $DB_NAME 2>/dev/null || echo "Database may already exist"
```

---

## 🔍 Bước 3: Kiểm tra Logs Service để xem lỗi cụ thể

```bash
# Xem log chi tiết
sudo journalctl -u ads-automation.service -n 100 --no-pager

# Hoặc xem log realtime
sudo journalctl -u ads-automation.service -f

# Xem log gần đây nhất
sudo journalctl -u ads-automation.service --since "10 minutes ago"
```

**Tìm lỗi phổ biến:**
- `DATABASE_URL không được để trống` → Kiểm tra .env file
- `could not connect to server` → Database chưa chạy hoặc sai host/port
- `database does not exist` → Cần tạo database
- `authentication failed` → Sai username/password
- `ModuleNotFoundError` → Thiếu dependencies

---

## 🔧 Bước 4: Sửa lỗi cụ thể

### 4.1. Nếu lỗi "DATABASE_URL không được để trống"

```bash
cd /home/adsuser/ads-automation

# Kiểm tra .env file tồn tại
ls -la .env

# Kiểm tra nội dung
cat .env | grep DATABASE_URL

# Nếu thiếu, thêm vào
echo 'DATABASE_URL=postgresql://user:password@localhost/database_name' >> .env
```

### 4.2. Nếu lỗi "could not connect to server"

```bash
# Kiểm tra PostgreSQL đang chạy
sudo systemctl status postgresql

# Nếu chưa chạy, start
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 4.3. Nếu lỗi "ModuleNotFoundError"

```bash
cd /home/adsuser/ads-automation

# Activate virtual environment
source venv/bin/activate  # hoặc: . venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ✅ Bước 5: Test và Restart Service

```bash
# Test database connection
cd /home/adsuser/ads-automation
source venv/bin/activate
python3 -c "
from app.core.config import get_settings
from app.core.database import init_db
try:
    settings = get_settings()
    print(f'✅ DATABASE_URL loaded: {settings.DATABASE_URL[:50]}...')
    init_db()
    print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"

# Nếu test thành công, restart service
sudo systemctl restart ads-automation.service

# Kiểm tra status
sudo systemctl status ads-automation.service
```

---

## 📋 Script tự động kiểm tra và sửa

Tạo file `fix_database_service.sh`:

```bash
#!/bin/bash
cd /home/adsuser/ads-automation

echo "🔍 Checking DATABASE_URL..."
if ! grep -q "DATABASE_URL" .env; then
    echo "❌ DATABASE_URL not found in .env"
    exit 1
fi

DB_URL=$(grep DATABASE_URL .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
DB_NAME=$(echo $DB_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DB_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')

echo "📋 Database: $DB_NAME, User: $DB_USER"

echo "🔍 Checking PostgreSQL service..."
if ! systemctl is-active --quiet postgresql; then
    echo "⚠️  PostgreSQL not running, starting..."
    sudo systemctl start postgresql
fi

echo "🔍 Checking if database exists..."
if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "📦 Creating database $DB_NAME..."
    sudo -u postgres createdb -O $DB_USER $DB_NAME
    echo "✅ Database created"
else
    echo "✅ Database exists"
fi

echo "🧪 Testing database connection..."
source venv/bin/activate
python3 -c "
from app.core.config import get_settings
from app.core.database import init_db
try:
    init_db()
    print('✅ Database connection OK')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
" || exit 1

echo "🔄 Restarting service..."
sudo systemctl restart ads-automation.service
sleep 3

echo "📊 Service status:"
sudo systemctl status ads-automation.service --no-pager -l

echo "✅ Done!"
```

**Cấp quyền và chạy:**

```bash
chmod +x fix_database_service.sh
./fix_database_service.sh
```

---

## 🔄 Bước 6: Chạy Migration sau khi database OK

```bash
cd /home/adsuser/ads-automation
source venv/bin/activate
python3 -m migrations.add_channels_management_tables
```

---

## 📝 Checklist

- [ ] Database đã được tạo
- [ ] DATABASE_URL trong .env đúng
- [ ] PostgreSQL đang chạy
- [ ] Test connection thành công
- [ ] Service restart và không còn lỗi
- [ ] Migration đã chạy thành công

---

## 💡 Tips

1. **Luôn kiểm tra log trước khi fix:**
   ```bash
   sudo journalctl -u ads-automation.service -n 50
   ```

2. **Nếu không chắc tên database, kiểm tra trong .env:**
   ```bash
   grep DATABASE_URL .env
   ```

3. **Test connection trước khi restart service:**
   ```bash
   python3 -c "from app.core.database import init_db; init_db(); print('OK')"
   ```

