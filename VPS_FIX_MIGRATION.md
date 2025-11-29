# 🔧 Hướng dẫn sửa lỗi Migration trên VPS

## ❌ Lỗi gặp phải:

```
sqlalchemy.exc.InvalidRequestError: Table 'channel_groups' is already defined 
for this MetaData instance.
```

**Nguyên nhân:** Cả model cũ và mới đều được import, gây xung đột tên bảng.

## ✅ Đã được sửa:

- Comment out import models cũ trong `app/core/database.py`
- Chỉ giữ lại models mới từ `app/models/channels.py`

---

## 🚀 Các bước để sửa trên VPS:

### Bước 1: Pull code mới (đã fix)

```bash
cd /home/adsuser/ads-automation
git pull origin main
```

Hoặc dùng script:

```bash
cd /home/adsuser/ads-automation
chmod +x vps_pull_channel_backend.sh
./vps_pull_channel_backend.sh
```

### Bước 2: Chạy lại migration

```bash
python3 -m migrations.add_channels_management_tables
```

Hoặc với full path:

```bash
PYTHONPATH=/home/adsuser/ads-automation python3 -m migrations.add_channels_management_tables
```

### Bước 3: Kiểm tra bảng đã được tạo

```bash
psql -U adsuser -d ads_automation_db -c "\dt channels*"
psql -U adsuser -d ads_automation_db -c "\dt posting_settings"
psql -U adsuser -d ads_automation_db -c "\dt auto_comment_templates"
```

Bạn sẽ thấy:
- `channels`
- `channel_groups`
- `channel_group_memberships`
- `posting_settings`
- `auto_comment_templates`

### Bước 4: Restart service

```bash
sudo systemctl restart ads-automation.service
```

---

## 📋 Copy-paste toàn bộ lệnh:

```bash
cd /home/adsuser/ads-automation && \
git pull origin main && \
python3 -m migrations.add_channels_management_tables && \
echo "✅ Migration completed! Check tables in database." && \
sudo systemctl restart ads-automation.service
```

---

## ⚠️ Nếu vẫn gặp lỗi:

### Lỗi: "Table already exists"

Nếu bảng đã tồn tại từ lần chạy trước, bạn có thể:

1. **Xóa bảng cũ và tạo lại** (⚠️ Cẩn thận - sẽ mất dữ liệu):

```bash
psql -U adsuser -d ads_automation_db -c "DROP TABLE IF EXISTS auto_comment_templates CASCADE;"
psql -U adsuser -d ads_automation_db -c "DROP TABLE IF EXISTS posting_settings CASCADE;"
psql -U adsuser -d ads_automation_db -c "DROP TABLE IF EXISTS channel_group_memberships CASCADE;"
psql -U adsuser -d ads_automation_db -c "DROP TABLE IF EXISTS channel_groups CASCADE;"
psql -U adsuser -d ads_automation_db -c "DROP TABLE IF EXISTS channels CASCADE;"

# Sau đó chạy lại migration
python3 -m migrations.add_channels_management_tables
```

2. **Hoặc bỏ qua nếu bảng đã có đúng cấu trúc**

Migration script sẽ không tạo lại bảng nếu đã tồn tại. Nếu bảng đã có đúng cấu trúc, bạn có thể bỏ qua migration.

---

## ✅ Verify sau khi fix:

```bash
# 1. Kiểm tra log migration
python3 -m migrations.add_channels_management_tables 2>&1 | grep -i "success\|error\|table"

# 2. Kiểm tra database
psql -U adsuser -d ads_automation_db -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%channel%' OR table_name LIKE '%posting%' OR table_name LIKE '%auto_comment%'
ORDER BY table_name;"

# 3. Kiểm tra service
sudo systemctl status ads-automation.service

# 4. Test API endpoint (nếu đã có frontend)
curl http://localhost:8000/api/channels
```

---

## 📝 Notes:

- Model cũ (`app/models/channel.py`) vẫn tồn tại nhưng không được import nữa
- Route cũ (`/api/channel/*`) đã bị comment trong `main.py`
- Route mới (`/api/channels/*`, `/api/channel-groups/*`, `/api/posting/settings/*`) đang active
- Frontend đang dùng routes mới ở `/settings/*`

