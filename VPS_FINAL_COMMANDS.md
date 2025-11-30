# 🚀 CÂU LỆNH HOÀN CHỈNH ĐỂ SỬA LỖI VÀ DEPLOY TRÊN VPS

## ✅ Code đã được push lên GitHub thành công!

**Latest commits:**
- ✅ Fix xung đột tên bảng database
- ✅ Fix database và service errors
- ✅ Script tự động kiểm tra và sửa lỗi
- ✅ Hướng dẫn chi tiết

---

## 📥 BƯỚC 1: Pull Code Mới

```bash
cd /home/adsuser/ads-automation
git pull origin main
```

---

## 🔧 BƯỚC 2: Sửa Lỗi Database và Service (CHỌN 1 CÁCH)

### ⚡ Cách 1: Dùng Script Tự Động (Khuyên dùng)

```bash
cd /home/adsuser/ads-automation
chmod +x fix_database_service.sh
./fix_database_service.sh
```

### 🔨 Cách 2: Thủ Công (Nếu script không hoạt động)

#### 2.1. Kiểm tra DATABASE_URL thực tế

```bash
cd /home/adsuser/ads-automation
cat .env | grep DATABASE_URL
```

**Lưu ý:** Tên database có thể KHÔNG phải "ads_automation_db". 
Nó nằm cuối URL: `postgresql://user:pass@host/database_name`

#### 2.2. Xem lỗi cụ thể từ service logs

```bash
sudo journalctl -u ads-automation.service -n 50 --no-pager
```

#### 2.3. Tạo database nếu chưa có

```bash
# Lấy tên database từ .env
DB_NAME=$(grep DATABASE_URL .env | sed -n 's|.*/\([^?]*\).*|\1|p')
echo "Database name: $DB_NAME"

# Tạo database
sudo -u postgres createdb $DB_NAME

# Hoặc nếu cần user riêng
DB_USER=$(grep DATABASE_URL .env | sed -n 's|postgresql://\([^:]*\):.*|\1|p')
sudo -u postgres createdb -O $DB_USER $DB_NAME
```

#### 2.4. Kiểm tra PostgreSQL đang chạy

```bash
sudo systemctl status postgresql
sudo systemctl start postgresql  # Nếu chưa chạy
```

#### 2.5. Test database connection

```bash
cd /home/adsuser/ads-automation
source venv/bin/activate

python3 -c "
from app.core.config import get_settings
from app.core.database import init_db
try:
    init_db()
    print('✅ Database connection OK')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## 🗄️ BƯỚC 3: Chạy Migration (Tạo Bảng Mới)

```bash
cd /home/adsuser/ads-automation
source venv/bin/activate  # Nếu chưa activate
python3 -m migrations.add_channels_management_tables
```

**Kết quả mong đợi:**
```
🚀 Starting Channel Management migration...
✅ Tables created successfully
```

---

## 🔄 BƯỚC 4: Restart Service

```bash
sudo systemctl restart ads-automation.service
sudo systemctl status ads-automation.service
```

**Kết quả mong đợi:**
```
● ads-automation.service - Facebook Ads Automation API
   Loaded: loaded (...)
   Active: active (running) since ...
```

---

## ✅ BƯỚC 5: Verify (Kiểm Tra)

### 5.1. Kiểm tra database tables

```bash
# Lấy tên database
DB_NAME=$(grep DATABASE_URL /home/adsuser/ads-automation/.env | sed -n 's|.*/\([^?]*\).*|\1|p')

# Kiểm tra bảng mới
psql -U adsuser -d $DB_NAME -c "\dt channels*"
psql -U adsuser -d $DB_NAME -c "\dt posting_settings"
```

### 5.2. Kiểm tra service logs

```bash
sudo journalctl -u ads-automation.service -n 20 --no-pager
```

### 5.3. Kiểm tra API endpoints

```bash
curl http://localhost:8000/health
# Kết quả: {"status":"healthy"}
```

---

## 🔥 COPY-PASTE TOÀN BỘ (1 LỆNH)

**Nếu database đã tồn tại và chỉ cần pull code:**

```bash
cd /home/adsuser/ads-automation && \
git pull origin main && \
source venv/bin/activate && \
python3 -m migrations.add_channels_management_tables && \
sudo systemctl restart ads-automation.service && \
echo "✅ Done! Check status with: sudo systemctl status ads-automation.service"
```

---

## ⚠️ NẾU GẶP LỖI

### Lỗi 1: "database does not exist"

```bash
# Tạo database
DB_NAME=$(grep DATABASE_URL /home/adsuser/ads-automation/.env | sed -n 's|.*/\([^?]*\).*|\1|p')
sudo -u postgres createdb $DB_NAME
```

### Lỗi 2: "could not connect to server"

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Lỗi 3: "DATABASE_URL không được để trống"

```bash
# Kiểm tra .env file
cd /home/adsuser/ads-automation
ls -la .env
cat .env | grep DATABASE_URL
```

### Lỗi 4: Service không start

```bash
# Xem log chi tiết
sudo journalctl -u ads-automation.service -n 100 --no-pager

# Kiểm tra Python dependencies
cd /home/adsuser/ads-automation
source venv/bin/activate
pip install -r requirements.txt
```

### Lỗi 5: "Table already exists"

Nếu bảng đã tồn tại từ lần chạy trước, bạn có thể bỏ qua migration hoặc xóa bảng cũ:

```bash
# ⚠️ CẨN THẬN - Sẽ xóa dữ liệu!
DB_NAME=$(grep DATABASE_URL /home/adsuser/ads-automation/.env | sed -n 's|.*/\([^?]*\).*|\1|p')
psql -U adsuser -d $DB_NAME << EOF
DROP TABLE IF EXISTS auto_comment_templates CASCADE;
DROP TABLE IF EXISTS posting_settings CASCADE;
DROP TABLE IF EXISTS channel_group_memberships CASCADE;
DROP TABLE IF EXISTS channel_groups CASCADE;
DROP TABLE IF EXISTS channels CASCADE;
EOF

# Sau đó chạy lại migration
python3 -m migrations.add_channels_management_tables
```

---

## 📋 CHECKLIST CUỐI CÙNG

- [ ] Code đã pull thành công
- [ ] Database đã được tạo (nếu chưa có)
- [ ] Migration đã chạy thành công
- [ ] Service đang chạy (active/running)
- [ ] Không có lỗi trong logs
- [ ] API endpoint `/health` trả về OK
- [ ] Có thể truy cập `/settings/channels` trên frontend

---

## 📚 FILES HƯỚNG DẪN CHI TIẾT

- `VPS_FIX_DATABASE_AND_SERVICE.md` - Hướng dẫn chi tiết sửa database
- `VPS_QUICK_FIX.txt` - Hướng dẫn nhanh
- `fix_database_service.sh` - Script tự động sửa lỗi
- `VPS_PULL_SIMPLE.sh` - Script pull code đơn giản

---

## 🎯 KẾT QUẢ MONG ĐỢI

Sau khi hoàn thành, bạn sẽ có:
- ✅ Database với 5 bảng mới (channels, channel_groups, ...)
- ✅ Service đang chạy ổn định
- ✅ API endpoints hoạt động: `/api/channels`, `/api/channel-groups`, `/api/posting/settings`
- ✅ Frontend pages: `/settings/channels`, `/settings/channel-groups`, `/settings/posting`

---

**Chúc bạn deploy thành công! 🚀**

