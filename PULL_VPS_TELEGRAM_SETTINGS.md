# 📱 HƯỚNG DẪN PULL CODE TELEGRAM BOT SETTINGS LÊN VPS

## ✅ ĐÃ HOÀN THÀNH

1. ✅ Thêm các trường Telegram Bot vào `UserSettings` model
2. ✅ Tạo service `telegram_token_service.py` để test bot token và chat ID
3. ✅ Thêm API endpoints: `/settings/telegram/save`, `/settings/telegram/test`, `/settings/telegram/status`, `/settings/telegram/delete`
4. ✅ Thêm section UI "Telegram Bot" vào settings page
5. ✅ Thêm JavaScript functions để quản lý Telegram Bot settings

## 🚀 CÁC BƯỚC PULL CODE VÀ SETUP

### **Bước 1: Pull code mới nhất**

```bash
cd ~/ads-automation
source venv/bin/activate
git pull origin main
```

### **Bước 2: Chạy migration database**

Thêm các cột mới vào bảng `user_settings`:

```bash
# Cách 1: Dùng psql
psql -U your_username -d your_database -f scripts/add_telegram_columns.sql

# Cách 2: Dùng Python script
python -c "
from app.core.database import engine
from sqlalchemy import text
with open('scripts/add_telegram_columns.sql', 'r') as f:
    sql = f.read()
with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()
print('✅ Migration completed')
"
```

### **Bước 3: Kiểm tra syntax**

```bash
python -m py_compile app/models/user_settings.py
python -m py_compile app/services/telegram_token_service.py
python -m py_compile app/api/routes/settings.py
python -c "from app.main import app; print('✅ Import OK')"
```

### **Bước 4: Cài đặt dependencies (nếu thiếu)**

```bash
pip install requests
```

### **Bước 5: Restart services**

```bash
sudo supervisorctl restart ads-automation-api
sleep 3
sudo supervisorctl status ads-automation-api
```

### **Bước 6: Kiểm tra logs**

```bash
sudo supervisorctl tail -50 ads-automation-api
```

## 📋 KIỂM TRA SAU KHI DEPLOY

1. Truy cập `https://updatemetaads.site/settings`
2. Kiểm tra section "Telegram Bot" có hiển thị không
3. Thử test bot token và chat ID
4. Thử lưu cấu hình

## 🔧 CÁCH LẤY TELEGRAM BOT TOKEN VÀ CHAT ID

### **Lấy Bot Token:**
1. Mở Telegram, tìm `@BotFather`
2. Gửi lệnh `/newbot` hoặc `/token`
3. Chọn bot cần lấy token
4. Copy token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### **Lấy Chat ID (Group ID):**
1. Tạo nhóm Telegram hoặc dùng nhóm có sẵn
2. Thêm bot vào nhóm
3. Gửi một message bất kỳ trong nhóm
4. Dùng API để lấy Chat ID:
   ```bash
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
   ```
5. Tìm `"chat":{"id":-1001234567890}` trong response
   - Số âm = Group ID (đúng)
   - Số dương = Chat cá nhân (không được phép)

## ⚠️ LƯU Ý

- Chat ID phải là số âm (Group ID)
- Bot phải được thêm vào nhóm trước khi test
- Bot Token được encrypt trước khi lưu vào database
- Mỗi user có Telegram Bot settings riêng

## 🐛 TROUBLESHOOTING

### **Lỗi: Column does not exist**
- Chạy lại migration script: `scripts/add_telegram_columns.sql`

### **Lỗi: Import error**
- Kiểm tra `app/services/telegram_token_service.py` có tồn tại không
- Kiểm tra `requests` đã được cài đặt chưa

### **Lỗi: 500 Internal Server Error**
- Kiểm tra logs: `sudo supervisorctl tail -50 ads-automation-api`
- Kiểm tra database connection
- Kiểm tra syntax errors

