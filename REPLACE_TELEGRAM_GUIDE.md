# 🔄 HƯỚNG DẪN THAY THẾ TELEGRAM.GS

## 🎯 MỤC TIÊU

Thay thế `Telegram.gs` hiện tại bằng version chỉ có phần thông báo (đã loại bỏ webhook, commands).

---

## ✅ CÁC BƯỚC

### **BƯỚC 1: Backup file cũ (QUAN TRỌNG!)**

1. Mở Google Apps Script Editor
2. Tìm file `Telegram.gs`
3. Copy toàn bộ nội dung
4. Tạo file mới: `Telegram.gs.backup`
5. Paste vào file backup
6. Lưu

### **BƯỚC 2: Thay thế file**

1. Mở file `Telegram.gs`
2. **XÓA TOÀN BỘ** nội dung hiện tại
3. Mở file `Telegram_Notification_Only.gs` (đã tạo)
4. Copy toàn bộ nội dung
5. Paste vào `Telegram.gs`
6. Lưu

### **BƯỚC 3: Kiểm tra**

1. Kiểm tra các file khác vẫn gọi được `guiThongBaoTelegram()`:
   - `Code.gs` → ✅ Vẫn dùng được
   - `FacebookAPI.gs` → ✅ Vẫn dùng được
   - `Logics.gs` → ✅ Vẫn dùng được

2. Test gửi thông báo:
   ```javascript
   // Chạy trong Script Editor
   var settings = getSettingsSafe_();
   guiThongBaoTelegram("Test message", settings['TELEGRAM_BOT_TOKEN'], settings['TELEGRAM_CHAT_ID']);
   ```

---

## ✅ CÁC HÀM CÒN LẠI

### **1. Gửi thông báo:**
- ✅ `guiThongBaoTelegram()` - Hàm chính
- ✅ `guiThongBaoTelegramFormatted()` - Format đẹp
- ✅ `guiThongBaoLoi()` - Thông báo lỗi
- ✅ `guiThongBaoThanhCong()` - Thông báo thành công
- ✅ `markdownToHtml()` - Convert Markdown → HTML

### **2. Quản lý Enable/Disable:**
- ✅ `isAutomationEnabled()` - Kiểm tra enabled
- ✅ `enableAutomation()` - Bật automation
- ✅ `disableAutomation()` - Tắt automation
- ✅ `getAllAutomationStatus()` - Lấy tất cả trạng thái

---

## ❌ ĐÃ XÓA

### **Webhook & Commands:**
- ❌ `doPost()` - Webhook handler
- ❌ `doGet()` - GET handler
- ❌ `processWebhookUpdate_()` - Xử lý webhook
- ❌ `handleTelegramMessage()` - Xử lý commands
- ❌ `handleHelpCommand()` - /help
- ❌ `handleStatusCommand()` - /status
- ❌ `handleEnableCommand()` - /enable
- ❌ `handleDisableCommand()` - /disable
- ❌ `handleReportCommand()` - /report
- ❌ Tất cả các command handlers khác

### **Message Processing:**
- ❌ `isMessageProcessed_()` - Kiểm tra message đã xử lý
- ❌ `markMessageAsProcessed_()` - Đánh dấu message
- ❌ `extractCommand_()` - Extract command
- ❌ `checkRateLimit_()` - Rate limiting
- ❌ `checkUserIsAdmin()` - Kiểm tra admin
- ❌ `testBotToken()` - Test bot token
- ❌ `setupTelegramWebhook()` - Setup webhook
- ❌ `resetWebhook()` - Reset webhook

---

## 📝 LƯU Ý

### **Các file khác KHÔNG CẦN THAY ĐỔI:**
- ✅ `Code.gs` - Vẫn dùng `guiThongBaoTelegram()` → OK
- ✅ `FacebookAPI.gs` - Vẫn dùng `guiThongBaoTelegram()` → OK
- ✅ `Logics.gs` - Vẫn dùng `guiThongBaoTelegram()` → OK
- ✅ `Pages.gs` - Vẫn dùng `guiThongBaoTelegram()` → OK

### **Nếu cần webhook sau này:**
- Có thể tạo file riêng: `TelegramWebhook.gs`
- Hoặc dùng Make.com để handle webhook
- Hoặc restore từ backup

---

## 🚀 SAU KHI THAY THẾ

### **File `Telegram.gs` sẽ chỉ còn:**
- ✅ ~200 dòng code (thay vì 3000+ dòng)
- ✅ Chỉ có hàm gửi thông báo
- ✅ Không có webhook, không có commands
- ✅ Dễ maintain hơn

### **Automation vẫn chạy bình thường:**
- ✅ `runAutomation()` vẫn gửi thông báo qua Telegram
- ✅ Tất cả notifications vẫn hoạt động
- ✅ Chỉ mất phần nhận commands từ Telegram

---

**Bạn đã sẵn sàng thay thế chưa? 🚀**

