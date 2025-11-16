# 🔍 DEBUG - KHÔNG THẤY LOG TRONG doGet()

## 🎯 VẤN ĐỀ

Khi chạy hàm `doGet()` trong Script Editor:
- ✅ Chạy thành công (không có lỗi)
- ❌ Không thấy Logger.log trong Execution log
- ❌ Chỉ thấy "Đã bắt đầu" và "Đã hoàn tất"

---

## 🔍 NGUYÊN NHÂN

### **1. Logger.log không hiển thị trong một số trường hợp:**

- Logger.log **có thể không hiển thị** khi hàm trả về HTML output
- Logger.log **có thể bị cache** hoặc không được flush
- Logger.log **có thể không hiển thị** trong Execution log nếu hàm chạy quá nhanh

### **2. Hàm doGet() đặc biệt:**

- `doGet()` là hàm **entry point** cho Web App
- Khi chạy trong Script Editor, có thể không có parameters
- Khi chạy trong Script Editor, có thể không trả về đúng format

---

## ✅ GIẢI PHÁP: TRẢ VỀ HTML ĐỂ TEST

Thay vì chỉ dùng Logger.log, tôi đã sửa hàm `doGet()` để:
1. ✅ **Trả về HTML với thông tin debug** nếu có lỗi
2. ✅ **Trả về HTML test** nếu không load được file
3. ✅ **Hiển thị error message** chi tiết nếu có lỗi

---

## 🧪 CÁCH TEST

### **BƯỚC 1: Chạy lại hàm doGet()**

1. **Mở Script Editor**
2. **Chọn file `TemplatesUI.gs`**
3. **Chọn hàm `doGet`** trong dropdown
4. **Click Run** (▶)
5. **Xem Return value** (bên dưới Execution log):
   - Nếu thấy HTML với "Templates UI - Test" → ✅ Hàm chạy đúng
   - Nếu thấy "Lỗi khi load TemplatesUI_HTML.html" → ❌ Có lỗi với file HTML
   - Nếu thấy "LỖI NGHIÊM TRỌNG" → ❌ Có lỗi tổng quát

### **BƯỚC 2: Deploy và test trong browser**

1. **Deploy Web App:**
   - Deploy → New deployment
   - Type: Web app
   - Execute as: Me
   - Who has access: Anyone
   - Deploy
   - Copy URL

2. **Mở URL trong browser:**
   - Sẽ thấy Templates UI (nếu file HTML load được)
   - Hoặc thấy error message với thông tin chi tiết

---

## 🔍 KIỂM TRA FILE HTML

### **BƯỚC 1: Kiểm tra file name**

1. **Trong Script Editor:**
   - Xem file `TemplatesUI_HTML.html` có tồn tại không
   - Tên file phải chính xác: `TemplatesUI_HTML.html`
   - **KHÔNG có khoảng trắng**, **KHÔNG có typo**

### **BƯỚC 2: Kiểm tra file content**

1. **Mở file `TemplatesUI_HTML.html`**
2. **Kiểm tra:**
   - File không rỗng
   - Có tag `<html>`, `<head>`, `<body>`
   - Không có lỗi syntax

### **BƯỚC 3: Test load file**

1. **Tạo hàm test:**
   ```javascript
   function testLoadHTML() {
     try {
       var html = HtmlService.createTemplateFromFile('TemplatesUI_HTML');
       Logger.log("✅ Load file thành công");
       return "OK";
     } catch (e) {
       Logger.log("🚨 Lỗi: " + e.message);
       return "ERROR: " + e.message;
     }
   }
   ```

2. **Chạy hàm `testLoadHTML()`**
3. **Xem Execution log**

---

## ⚠️ LƯU Ý

### **1. Logger.log trong doGet():**

- Logger.log **có thể không hiển thị** trong Execution log khi chạy `doGet()`
- **Cách tốt nhất:** Trả về HTML với thông tin debug

### **2. Test trong Script Editor vs Browser:**

- **Script Editor:** Có thể không có parameters, có thể không trả về đúng format
- **Browser (Web App):** Có parameters, trả về đúng format HTML

### **3. Deploy và test:**

- **Cách tốt nhất:** Deploy Web App và test trong browser
- Sẽ thấy kết quả thực tế

---

## 📝 CHECKLIST

- [ ] Đã sửa hàm doGet() để trả về HTML debug
- [ ] Đã chạy lại hàm doGet() trong Script Editor
- [ ] Đã xem Return value (bên dưới Execution log)
- [ ] Đã kiểm tra file TemplatesUI_HTML.html tồn tại
- [ ] Đã deploy Web App
- [ ] Đã test URL trong browser

---

**Hãy chạy lại hàm `doGet()` và xem Return value! Nếu vẫn không thấy, hãy deploy và test trong browser! 🚀**

