# 🔧 HƯỚNG DẪN CẤU HÌNH CONSOLE ĐỂ DEBUG

## ⚙️ Console Settings (F12 → Console → Click icon ⚙️)

### **BẮT BUỘC BẬT:**
1. ✅ **Preserve log** - Giữ log khi refresh trang
2. ✅ **Show CORS errors in console** - Hiển thị lỗi CORS
3. ✅ **Log XMLHttpRequests** - Log các request API
4. ✅ **Group similar messages in console** - Nhóm các message giống nhau (tùy chọn)

### **TẮT FILTER:**
1. Click vào icon **Filter** (hình phễu) ở thanh toolbar
2. Đảm bảo **TẤT CẢ** các filter đều được bật:
   - ✅ **All levels** (hoặc bật riêng: Verbose, Info, Warnings, Errors)
   - ✅ **All contexts**
   - ✅ **All time**

### **CLEAR CONSOLE:**
1. Click icon **Clear console** (hình thùng rác) hoặc nhấn `Ctrl+L`
2. Refresh trang (F5)
3. Xem log mới

## 🧪 TEST CONSOLE

Paste code này vào Console để test:

```javascript
console.log('TEST LOG');
console.error('TEST ERROR');
console.warn('TEST WARNING');
alert('Nếu bạn thấy alert này, JavaScript đang hoạt động');
```

Nếu không thấy gì → Console đang bị filter hoặc có vấn đề.

## 🔍 KIỂM TRA LỖI JAVASCRIPT

1. **Mở Console** (F12 → Console)
2. **Xem tab "Issues"** (nếu có) - thường ở góc trên bên phải
3. **Xem các dòng màu đỏ** - đây là lỗi JavaScript
4. **Copy toàn bộ lỗi** và gửi cho tôi

## 📋 CHECKLIST

- [ ] Đã bật "Preserve log"
- [ ] Đã tắt tất cả filters
- [ ] Đã clear console
- [ ] Đã refresh trang (F5)
- [ ] Đã thấy log `🚀 Dashboard script loading...`
- [ ] Đã thấy log `✅ Dashboard script started`
- [ ] Đã thấy log `✅ All functions defined`

