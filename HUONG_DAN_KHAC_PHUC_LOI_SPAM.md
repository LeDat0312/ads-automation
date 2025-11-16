# Hướng dẫn khắc phục lỗi spam và lỗi 302

## 🔴 Vấn đề hiện tại

1. **Lỗi 302**: Webhook trả về "302 Moved Temporarily" thay vì "200 OK"
2. **Spam messages**: Bot liên tục gửi cùng một câu trả lời nhiều lần
3. **Pending updates**: Có 1 pending update đang chờ xử lý

## ✅ Giải pháp

### Bước 1: Xóa webhook và pending updates

1. Mở Apps Script Editor
2. Chạy hàm `deleteWebhook()` để xóa webhook cũ và pending updates
3. Đợi 2-3 giây

### Bước 2: Authorize Web App (QUAN TRỌNG)

Lỗi 302 thường xảy ra khi Web App chưa được authorize. Để khắc phục:

1. **Mở URL webhook trong browser (Incognito/Private mode)**:
   ```
   https://script.google.com/macros/s/AKfycbyuPEzIdqvWP1tMPF8v5Yui20EfJd4PvLo7PtdCL186-WFIqzae8sfm_ROFbVOSv-eA/exec
   ```

2. **Nếu thấy thông báo "Telegram Bot Webhook đang hoạt động!"**:
   - ✅ Web App đã được authorize thành công
   - Tiếp tục Bước 3

3. **Nếu thấy trang "Google hasn't verified this app"**:
   - Click **"Advanced"** (Ở cuối trang)
   - Click **"Go to [Project] (unsafe)"** (hoặc "Go to [Your Project Name] (unsafe)")
   - Click **"Allow"**
   - Sau đó bạn sẽ thấy "Telegram Bot Webhook đang hoạt động!"
   - ✅ Web App đã được authorize thành công

### Bước 3: Cài đặt lại webhook

1. Trong Apps Script Editor, chạy hàm `setupTelegramWebhook()`
2. Đợi 2-3 giây
3. Chạy hàm `checkTelegramWebhook()` để kiểm tra

### Bước 4: Kiểm tra kết quả

1. Gửi lệnh `/test` trong nhóm Telegram
2. Bot chỉ nên trả lời **1 lần**
3. Kiểm tra execution logs để xem có lỗi gì không

## 🔧 Các cải tiến đã thực hiện

### 1. Response format đúng
- Response luôn là JSON: `{"ok": true}`
- MIME type: `application/json`
- Tránh lỗi 302

### 2. Tracking message chính xác
- Tracking theo `messageId + command`
- Sử dụng Cache Service (nhanh) + Properties Service (persistent)
- Mỗi message chỉ được xử lý 1 lần

### 3. Rate limiting toàn cục
- Rate limit: 10 giây cho mỗi command
- Tracking theo `chatId + command + userId`
- Hỗ trợ đa luồng (nhiều admin có thể gửi commands khác nhau)

### 4. Xóa pending updates
- Khi reset webhook, tự động xóa pending updates
- Sử dụng `drop_pending_updates=true`

## 📝 Lưu ý

1. **Lỗi 302**: Nếu vẫn thấy lỗi 302 sau khi authorize, thử:
   - Mở URL webhook trong Incognito/Private mode
   - Đảm bảo Web App được deploy với quyền "Anyone"
   - Kiểm tra execution logs để xem có lỗi gì không

2. **Spam messages**: Nếu vẫn thấy spam:
   - Chạy `deleteWebhook()` để xóa pending updates
   - Chạy `setupTelegramWebhook()` để cài đặt lại
   - Kiểm tra execution logs để xem message ID có được tracking đúng không

3. **Rate limiting**: Nếu muốn thay đổi rate limit:
   - Sửa biến `rateLimitSeconds` trong hàm `handleTelegramMessage`
   - Mặc định: 10 giây

## 🚀 Các bước tiếp theo

1. ✅ Xóa webhook và pending updates
2. ✅ Authorize Web App
3. ✅ Cài đặt lại webhook
4. ✅ Test commands
5. ✅ Kiểm tra logs

## 📞 Hỗ trợ

Nếu vẫn gặp vấn đề:
1. Kiểm tra execution logs trong Apps Script Editor
2. Kiểm tra Cloud Logs (Stackdriver)
3. Kiểm tra webhook status bằng lệnh `/check_webhook`

