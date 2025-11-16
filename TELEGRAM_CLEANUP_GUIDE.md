# 🧹 HƯỚNG DẪN DỌN DẸP TELEGRAM.GS

## 🎯 MỤC TIÊU

Loại bỏ tất cả phần webhook, nghe, gọi, xử lý commands trong `Telegram.gs`.
**CHỈ GIỮ LẠI** phần gửi thông báo.

---

## ✅ CÁC HÀM CẦN GIỮ LẠI

### **1. markdownToHtml()**
- Chuyển đổi Markdown sang HTML
- Dùng cho formatting message

### **2. guiThongBaoTelegram()**
- Hàm chính gửi message
- **QUAN TRỌNG:** Giữ nguyên toàn bộ

### **3. guiThongBaoTelegramFormatted()**
- Wrapper cho format đẹp hơn

### **4. guiThongBaoLoi()**
- Wrapper cho thông báo lỗi

### **5. guiThongBaoThanhCong()**
- Wrapper cho thông báo thành công

### **6. Quản lý Enable/Disable (nếu cần):**
- `isAutomationEnabled()`
- `enableAutomation()`
- `disableAutomation()`
- `getAllAutomationStatus()`

---

## ❌ CÁC HÀM CẦN XÓA

### **1. Webhook Handlers:**
- `doPost()` - Webhook handler
- `doGet()` - GET handler
- `processWebhookUpdate_()` - Xử lý webhook update
- `testWebhook()` - Test webhook

### **2. Command Handlers:**
- `handleTelegramMessage()` - Xử lý message/commands
- `handleTelegramMessageSafe_()` - Wrapper an toàn
- `extractCommand_()` - Extract command từ text
- `handleHelpCommand()`
- `handleTestCommand()`
- `handleEnableCommand()`
- `handleDisableCommand()`
- `handleStatusCommand()`
- `handleReportCommand()`
- `handleStatusAdsCommand()`
- `handleEnableAllCommand()`
- `handleDisableAllCommand()`
- `handleCheckWebhookCommand()`
- `handleResetWebhookCommand()`
- `handleDashboardCommand()`

### **3. Message Processing:**
- `isMessageProcessed_()` - Kiểm tra message đã xử lý
- `markMessageAsProcessed_()` - Đánh dấu message đã xử lý
- `shouldSendErrorNotification_()` - Kiểm tra có nên gửi error notification

### **4. Rate Limiting:**
- `checkRateLimit_()` - Kiểm tra rate limit
- `setRateLimit_()` - Set rate limit

### **5. Async Task Runners:**
- `_processDirectCommand_()` - Xử lý lệnh nhẹ
- `_processTelegramQueue_()` - Xử lý queue
- `_runTaskReport()` - Task runner cho /report
- `_runTaskStatusAds()` - Task runner cho /statusads
- `_runTaskStatus()` - Task runner cho /status

### **6. Webhook Setup:**
- `setupWebhook()` - Setup webhook
- `resetWebhook()` - Reset webhook
- `checkWebhookStatus()` - Kiểm tra webhook status

### **7. Permission Checks:**
- `checkUserPermission()` - Kiểm tra quyền user
- `isUserAdmin()` - Kiểm tra user là admin

---

## 📋 CÁCH THỰC HIỆN

### **BƯỚC 1: Backup file cũ**
1. Copy toàn bộ `Telegram.gs` hiện tại
2. Lưu vào file backup (ví dụ: `Telegram.gs.backup`)

### **BƯỚC 2: Thay thế file**
1. Xóa toàn bộ nội dung trong `Telegram.gs`
2. Copy toàn bộ code từ `Telegram_Notification_Only.gs` đã tạo
3. Paste vào `Telegram.gs`
4. Lưu

### **BƯỚC 3: Kiểm tra**
1. Kiểm tra các file khác (Code.gs, FacebookAPI.gs, Logics.gs) vẫn gọi được `guiThongBaoTelegram()`
2. Test gửi thông báo từ automation

---

## ✅ KẾT QUẢ

Sau khi dọn dẹp, `Telegram.gs` sẽ chỉ còn:
- ✅ Hàm gửi thông báo (`guiThongBaoTelegram()`)
- ✅ Hàm format (`markdownToHtml()`, `guiThongBaoTelegramFormatted()`, etc.)
- ✅ Hàm quản lý enable/disable (nếu cần)

**KHÔNG CÒN:**
- ❌ Webhook handlers
- ❌ Command handlers
- ❌ Message processing
- ❌ Rate limiting
- ❌ Permission checks

---

## 📝 LƯU Ý

### **Các file khác vẫn dùng được:**
- `Code.gs` vẫn gọi `guiThongBaoTelegram()` → ✅ OK
- `FacebookAPI.gs` vẫn gọi `guiThongBaoTelegram()` → ✅ OK
- `Logics.gs` vẫn gọi `guiThongBaoTelegram()` → ✅ OK

### **Nếu cần webhook sau này:**
- Có thể tạo file riêng: `TelegramWebhook.gs`
- Hoặc dùng Make.com để handle webhook

---

**File `Telegram_Notification_Only.gs` đã được tạo sẵn, bạn chỉ cần copy vào `Telegram.gs`! 🚀**

