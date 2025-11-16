# 🧪 TEST HÀM doGet() - TEMPLATES UI

## 🎯 VẤN ĐỀ

Khi chạy hàm `doGet()` trong Script Editor:
- ✅ Chạy thành công (không có lỗi)
- ❌ Không có log gì (chỉ có "Đã bắt đầu" và "Đã hoàn tất")
- ❌ Không biết hàm có trả về HTML không

---

## ✅ ĐÃ SỬA

Đã thêm **Logger.log** vào hàm `doGet()` để debug:
- ✅ Log khi bắt đầu
- ✅ Log parameters
- ✅ Log từng bước
- ✅ Log lỗi nếu có

---

## 🧪 CÁCH TEST

### **BƯỚC 1: Chạy lại hàm doGet()**

1. **Mở Script Editor**
2. **Chọn file `TemplatesUI.gs`**
3. **Chọn hàm `doGet`** trong dropdown
4. **Click Run** (▶)
5. **Xem Execution log:**
   - Sẽ thấy các log:
     - `✅ [doGet] Bắt đầu serve Templates UI`
     - `✅ [doGet] Parameters: ...`
     - `✅ [doGet] Đã tạo HTML template...`
     - `✅ [doGet] Đã evaluate template...`
     - `✅ [doGet] Trả về HTML output`

### **BƯỚC 2: Kiểm tra kết quả**

1. **Xem Execution log:**
   - Nếu thấy tất cả log ✅ → Hàm chạy đúng
   - Nếu thấy log 🚨 → Có lỗi, xem error message

2. **Xem Return value:**
   - Execution log sẽ hiển thị return value
   - Nếu thấy HTML → ✅ Đúng
   - Nếu thấy "Lỗi khi load Templates UI" → ❌ Có lỗi

---

## 🔍 KIỂM TRA FILE HTML

### **BƯỚC 1: Kiểm tra file name**

1. **Trong Script Editor:**
   - Xem file `TemplatesUI_HTML.html` có tồn tại không
   - Tên file phải chính xác: `TemplatesUI_HTML.html`
   - Không có khoảng trắng, không có typo

### **BƯỚC 2: Kiểm tra file content**

1. **Mở file `TemplatesUI_HTML.html`**
2. **Kiểm tra:**
   - File không rỗng
   - Có tag `<html>`, `<head>`, `<body>`
   - Không có lỗi syntax

---

## 🚀 TEST TRỰC TIẾP TRONG BROWSER

### **CÁCH 1: Deploy và test**

1. **Deploy Web App:**
   - Deploy → New deployment
   - Type: Web app
   - Execute as: Me
   - Who has access: Anyone
   - Deploy
   - Copy URL

2. **Mở URL trong browser:**
   - Sẽ thấy Templates UI
   - Hoặc thấy error message

### **CÁCH 2: Test bằng URL với parameters**

1. **Copy Web app URL**
2. **Thêm `?test=1` vào cuối:**
   ```
   https://script.google.com/macros/s/.../exec?test=1
   ```
3. **Mở trong browser**
4. **Xem kết quả**

---

## ⚠️ LƯU Ý

### **1. Logger.log trong Web App:**

- Logger.log **CHỈ hiển thị** trong Script Editor (Execution log)
- Logger.log **KHÔNG hiển thị** khi truy cập Web App URL
- Để debug Web App, cần xem Execution log trong Script Editor

### **2. Nếu không thấy log:**

1. **Kiểm tra Execution log:**
   - View → Execution log
   - Hoặc xem bên dưới code editor

2. **Kiểm tra hàm:**
   - Đảm bảo đã chọn đúng hàm `doGet`
   - Đảm bảo đã click Run

3. **Clear cache:**
   - File → Clear cache
   - Chạy lại hàm

---

## 📝 CHECKLIST

- [ ] Đã thêm Logger.log vào hàm doGet()
- [ ] Đã chạy lại hàm doGet() trong Script Editor
- [ ] Đã thấy các log trong Execution log
- [ ] Đã kiểm tra file TemplatesUI_HTML.html tồn tại
- [ ] Đã deploy Web App
- [ ] Đã test URL trong browser

---

**Hãy chạy lại hàm `doGet()` và xem Execution log! 🧪**

