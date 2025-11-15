# 🔧 HƯỚNG DẪN CHẠY MIGRATION TELEGRAM BOT SETTINGS

## ❌ LỖI GẶP PHẢI

```
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL: Peer authentication failed for user "your_username"
```

**Nguyên nhân:** Đã dùng placeholder `your_username` và `your_database` thay vì thông tin thực tế.

## ✅ GIẢI PHÁP

### **Cách 1: Dùng Python Script (Khuyến nghị)**

```bash
cd ~/ads-automation
source venv/bin/activate
git pull origin main  # Pull script mới
python scripts/run_telegram_migration.py
```

Script này sẽ:
- Tự động đọc `DATABASE_URL` từ `.env` file
- Chạy migration SQL
- Kiểm tra kết quả

### **Cách 2: Dùng psql với thông tin thực tế**

1. **Lấy thông tin database từ .env:**
   ```bash
   cd ~/ads-automation
   grep DATABASE_URL .env
   ```

2. **Parse thông tin từ DATABASE_URL:**
   - Format: `postgresql://username:password@host:port/database`
   - Ví dụ: `postgresql://adsuser:password123@localhost:5432/ads_automation`
   - Username: `adsuser`
   - Database: `ads_automation`

3. **Chạy migration:**
   ```bash
   psql -U adsuser -d ads_automation -f scripts/add_telegram_columns.sql
   ```

### **Cách 3: Chạy SQL trực tiếp trong psql**

```bash
# Kết nối vào database
psql -U adsuser -d ads_automation

# Trong psql prompt, chạy:
\i scripts/add_telegram_columns.sql

# Hoặc copy/paste nội dung SQL file
```

## 🔍 KIỂM TRA SAU KHI MIGRATION

```bash
# Kết nối vào database
psql -U adsuser -d ads_automation

# Kiểm tra các cột đã được thêm
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'user_settings'
AND column_name LIKE 'telegram%'
ORDER BY column_name;
```

Kết quả mong đợi:
```
     column_name              | data_type | is_nullable | column_default
------------------------------+-----------+-------------+----------------
 telegram_bot_last_checked    | timestamp | YES         | NULL
 telegram_bot_status          | varchar   | YES         | 'NOT_SET'::character varying
 telegram_bot_token_encrypted | text      | YES         | NULL
 telegram_chat_id             | varchar   | YES         | NULL
```

## 🚀 SAU KHI MIGRATION THÀNH CÔNG

1. **Kiểm tra service đã restart:**
   ```bash
   sudo supervisorctl status ads-automation-api
   ```

2. **Kiểm tra logs:**
   ```bash
   sudo supervisorctl tail -50 ads-automation-api
   ```

3. **Truy cập website:**
   - Vào `https://updatemetaads.site/settings`
   - Kiểm tra section "Telegram Bot" có hiển thị không

## ⚠️ LƯU Ý

- Migration script sử dụng `IF NOT EXISTS`, nên có thể chạy nhiều lần an toàn
- Nếu cột đã tồn tại, script sẽ bỏ qua và không báo lỗi
- Đảm bảo `.env` file có `DATABASE_URL` đúng

