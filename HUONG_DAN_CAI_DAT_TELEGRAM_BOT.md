# HƯỚNG DẪN CÀI ĐẶT TELEGRAM BOT

## 📋 YÊU CẦU

1. **Telegram Bot Token** - Lấy từ @BotFather
2. **Google Apps Script Project** - Đã có code Telegram bot
3. **Telegram Group** - Nhóm Telegram để bot hoạt động

## 🔧 CÁC BƯỚC CÀI ĐẶT

### BƯỚC 1: Tạo Telegram Bot (nếu chưa có)

1. Mở Telegram, tìm **@BotFather**
2. Gửi lệnh `/newbot`
3. Đặt tên bot (ví dụ: `My Automation Bot`)
4. Đặt username bot (ví dụ: `my_automation_bot`)
5. **Copy Bot Token** (ví dụ: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### BƯỚC 2: Thêm Bot vào Nhóm Telegram

1. Tạo một **nhóm Telegram** (group hoặc supergroup)
2. Thêm bot vào nhóm bằng cách:
   - Tìm bot theo username (ví dụ: `@my_automation_bot`)
   - Click "Add to Group"
   - Chọn nhóm muốn thêm
3. **Quan trọng**: Cấp quyền **Admin** cho bot (để bot có thể đọc tin nhắn)

### BƯỚC 3: Lấy Chat ID của Nhóm

1. Trong nhóm Telegram, gửi bất kỳ tin nhắn nào (ví dụ: `/test`)
2. Mở trình duyệt, truy cập:
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   ```
   (Thay `<BOT_TOKEN>` bằng Bot Token của bạn)

3. Tìm `"chat":{"id":-1234567890}` - Số này là **Chat ID** (số âm)
4. **Copy Chat ID** (ví dụ: `-1234567890`)

**Hoặc dùng cách khác:**
- Thêm bot @userinfobot vào nhóm
- Bot sẽ hiển thị Chat ID của nhóm

### BƯỚC 4: Cấu hình trong Google Sheets

1. Mở Google Sheets chứa code
2. Mở sheet **"CaiDat"**
3. Cập nhật các giá trị sau:

| Key | Giá trị | Ví dụ |
|-----|---------|-------|
| `TELEGRAM_BOT_TOKEN` | Bot Token từ @BotFather | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `TELEGRAM_CHAT_ID` | Chat ID của nhóm (số âm) | `-1234567890` |
| `TELEGRAM_AUTHORIZED_CHAT_ID` | Chat ID của nhóm (số âm) - giống TELEGRAM_CHAT_ID | `-1234567890` |

**Lưu ý:**
- `TELEGRAM_AUTHORIZED_CHAT_ID` phải khớp với Chat ID của nhóm
- Nếu không có `TELEGRAM_AUTHORIZED_CHAT_ID`, hệ thống sẽ dùng `TELEGRAM_CHAT_ID`

### BƯỚC 5: Deploy Google Apps Script như Web App

1. Mở **Google Apps Script Editor**
2. Chọn **Deploy** → **New deployment**
3. Chọn type: **Web app**
4. Cấu hình:
   - **Execute as**: Me (your email)
   - **Who has access**: Anyone
5. Click **Deploy**
6. **Copy Web App URL** (ví dụ: `https://script.google.com/macros/s/AKfycbyT3uJ7vyR-VgNZMF9RD8CTgPLJg3OYJzAiuiQOpGQUmi8G-ZS-r19tFnqWCGvT62e5/exec`)
7. **Quan trọng**: URL phải có `/exec` ở cuối (không phải `/dev`)

### BƯỚC 6: Cài đặt Webhook

1. Trong Google Apps Script Editor, chạy hàm `setupTelegramWebhookWithUrl()` hoặc `setupTelegramWebhook()`
2. Hoặc mở trình duyệt, truy cập:
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=<WEB_APP_URL>
   ```
   (Thay `<BOT_TOKEN>` bằng Bot Token và `<WEB_APP_URL>` bằng Web App URL)

3. Kiểm tra webhook đã được cài đặt:
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo
   ```

### BƯỚC 7: Kiểm tra Bot hoạt động

1. Trong nhóm Telegram, gửi lệnh `/test`
2. Bot sẽ reply: "✅ WEBHOOK ĐANG HOẠT ĐỘNG!"
3. Nếu không có reply, kiểm tra:
   - Bot đã được thêm vào nhóm chưa?
   - Bot có quyền Admin trong nhóm không?
   - Chat ID trong sheet có đúng không?
   - Webhook URL có đúng không?

## 🔒 BẢO MẬT

### Bot chỉ hoạt động trong nhóm được phép:

1. **Chặn chat cá nhân**: Bot sẽ KHÔNG phản hồi commands trong chat riêng
2. **Chỉ nhóm được phép**: Bot chỉ xử lý commands từ nhóm có Chat ID khớp với `TELEGRAM_AUTHORIZED_CHAT_ID`
3. **Quyền Admin/Creator**: Chỉ Admin/Creator trong nhóm mới được sử dụng bot (trừ lệnh `/myid`)

### Kiểm tra quyền:

- Bot phải là **Admin** trong nhóm (để đọc tin nhắn)
- User gửi command phải là **Admin/Creator** trong nhóm (để sử dụng bot)

## 📝 CÁC LỆNH CÓ SẴN

- `/test` - Kiểm tra webhook hoạt động
- `/myid` - Xem Chat ID và User ID (cho phép tất cả members)
- `/help` - Xem hướng dẫn
- `/enable <account_id> <prefix>` - Bật automation
- `/disable <account_id> <prefix>` - Tắt automation
- `/status` - Xem trạng thái enable/disable
- `/disable_all` - Tắt tất cả automation
- `/enable_all` - Bật lại tất cả automation
- `/report` - Xem báo cáo tài chính
- `/statusads` - Xem báo cáo trạng thái ads
- `/check_webhook` - Kiểm tra trạng thái webhook
- `/reset_webhook` - Reset và cài đặt lại webhook

## 🐛 XỬ LÝ LỖI

### Lỗi: Bot không phản hồi

1. Kiểm tra Bot Token trong sheet `CaiDat`
2. Kiểm tra Chat ID trong sheet `CaiDat`
3. Kiểm tra webhook đã được cài đặt chưa
4. Kiểm tra bot đã được thêm vào nhóm chưa
5. Kiểm tra bot có quyền Admin trong nhóm không

### Lỗi: Webhook không hoạt động

1. Kiểm tra Web App URL có đúng không (phải có `/exec`)
2. Kiểm tra Web App đã deploy với quyền "Anyone" chưa
3. Chạy lại `setupTelegramWebhookWithUrl()`
4. Kiểm tra Execution logs trong Apps Script Editor

### Lỗi: "Chat ID không khớp"

1. Kiểm tra `TELEGRAM_AUTHORIZED_CHAT_ID` trong sheet `CaiDat`
2. Đảm bảo Chat ID là số âm (ví dụ: `-1234567890`)
3. Sử dụng lệnh `/myid` trong nhóm để xem Chat ID

## 💡 LƯU Ý

1. **Bot chỉ hoạt động trong nhóm**: Bot sẽ KHÔNG phản hồi commands trong chat riêng
2. **Chat ID phải là số âm**: Nhóm có Chat ID âm, chat riêng có Chat ID dương
3. **Web App URL phải có `/exec`**: Không dùng `/dev` endpoint
4. **Bot phải là Admin**: Bot cần quyền Admin để đọc tin nhắn trong nhóm
5. **Chỉ Admin/Creator mới dùng được bot**: Members thường không thể sử dụng bot (trừ `/myid`)

## 📞 HỖ TRỢ

Nếu gặp vấn đề, kiểm tra:
1. Execution logs trong Apps Script Editor
2. Webhook info: `https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo`
3. Bot info: `https://api.telegram.org/bot<BOT_TOKEN>/getMe`

