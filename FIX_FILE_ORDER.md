# 🔧 FIX - VẤN ĐỀ FILE ORDER

## 🎯 VẤN ĐỀ

Google Apps Script có thể chọn hàm `doGet()` từ file **theo thứ tự alphabet** hoặc **theo thứ tự tạo file**.

Nếu `Telegram.gs` đứng trước `TemplatesUI.gs`, Google có thể vẫn chọn `Telegram.gs` dù đã đổi tên hàm.

---

## ✅ GIẢI PHÁP: ĐỔI TÊN FILE

### **CÁCH 1: Đổi tên TemplatesUI.gs (KHUYẾN NGHỊ)**

1. **Trong Google Apps Script Editor:**
   - Click vào file `TemplatesUI.gs`
   - **File → Rename** (hoặc click vào tên file)
   - Đổi tên thành: `00_TemplatesUI.gs` (số 0 đứng đầu)
   - Hoặc: `AAA_TemplatesUI.gs` (chữ A đứng đầu)
   - **Lưu**

2. **Kiểm tra:**
   - File `00_TemplatesUI.gs` (hoặc `AAA_TemplatesUI.gs`) phải đứng **ĐẦU TIÊN** trong danh sách files

3. **Deploy lại:**
   - Deploy → Manage deployments
   - **Xóa TẤT CẢ deployments**
   - Deploy → New deployment
   - Type: Web app
   - Execute as: Me
   - Who has access: Anyone
   - Deploy
   - **Copy URL mới**

4. **Test URL mới**

---

### **CÁCH 2: Đổi tên Telegram.gs (Nếu không muốn đổi TemplatesUI)**

1. **Trong Google Apps Script Editor:**
   - Click vào file `Telegram.gs`
   - **File → Rename**
   - Đổi tên thành: `zz_Telegram.gs` (chữ z đứng cuối)
   - **Lưu**

2. **Kiểm tra:**
   - File `zz_Telegram.gs` phải đứng **CUỐI CÙNG** trong danh sách files
   - File `TemplatesUI.gs` phải đứng **TRƯỚC** `zz_Telegram.gs`

3. **Deploy lại:**
   - Deploy → Manage deployments
   - **Xóa TẤT CẢ deployments**
   - Deploy → New deployment
   - Type: Web app
   - Execute as: Me
   - Who has access: Anyone
   - Deploy
   - **Copy URL mới**

4. **Test URL mới**

---

## 🔍 KIỂM TRA TRONG SCRIPT EDITOR

### **BƯỚC 1: Kiểm tra File Order**

1. **Mở Script Editor**
2. **Xem danh sách files bên trái:**
   - File nào đứng **ĐẦU TIÊN**?
   - File nào có `doGet()`?

### **BƯỚC 2: Test hàm doGet**

1. **Chọn file `TemplatesUI.gs`** (hoặc `00_TemplatesUI.gs`)
2. **Chọn hàm `doGet`** trong dropdown
3. **Click Run** (▶)
4. **Xem Execution log:**
   - Nếu thấy HTML → ✅ Đúng
   - Nếu thấy "Telegram Bot Webhook" → ❌ Vẫn sai

### **BƯỚC 3: Tìm kiếm doGet**

1. **Edit → Find and replace** (Ctrl + H)
2. **Tìm:** `function doGet`
3. **Xem tất cả kết quả:**
   - Chỉ **MỘT** file có `function doGet(` → ✅ Đúng
   - Nhiều hơn **MỘT** file có `function doGet(` → ❌ Vẫn conflict

---

## 🚀 CÁC BƯỚC CHI TIẾT

### **BƯỚC 1: Đổi tên file**

1. **Mở Script Editor**
2. **Click vào `TemplatesUI.gs`**
3. **File → Rename**
4. **Đổi thành:** `00_TemplatesUI.gs`
5. **Enter để lưu**

### **BƯỚC 2: Xóa TẤT CẢ deployments**

1. **Deploy → Manage deployments**
2. **Xóa TẤT CẢ deployments** (không chỉ deployment cũ)
3. **Xác nhận xóa**

### **BƯỚC 3: Tạo deployment MỚI HOÀN TOÀN**

1. **Deploy → New deployment**
2. **Click "Select type"** → Chọn **"Web app"**
3. **Settings:**
   - **Description:** (tùy chọn) "Templates UI"
   - **Execute as:** Me (your-email@gmail.com)
   - **Who has access:** Anyone
4. **Click "Deploy"**
5. **Copy Web app URL MỚI**

### **BƯỚC 4: Test**

1. **Mở URL mới** trong browser (Incognito mode)
2. **Sẽ thấy Templates UI**

---

## ⚠️ LƯU Ý

### **1. File Name:**

- ✅ `00_TemplatesUI.gs` (số 0 đứng đầu)
- ✅ `AAA_TemplatesUI.gs` (chữ A đứng đầu)
- ❌ `TemplatesUI.gs` (có thể bị conflict với `Telegram.gs`)

### **2. Deploy:**

- ✅ **Xóa TẤT CẢ deployments** trước khi tạo mới
- ✅ **Tạo deployment MỚI HOÀN TOÀN** (không edit deployment cũ)
- ✅ **Dùng URL MỚI** (không dùng URL cũ)

### **3. Cache:**

- Đợi 5-10 phút sau khi deploy
- Hoặc thêm `?v=2` vào URL để force refresh

---

## 📝 CHECKLIST

- [ ] Đã đổi tên `TemplatesUI.gs` → `00_TemplatesUI.gs`
- [ ] File `00_TemplatesUI.gs` đứng ĐẦU TIÊN trong danh sách
- [ ] Đã tìm kiếm `function doGet` - chỉ có 1 file
- [ ] Đã test hàm `doGet` trong Script Editor - thấy HTML
- [ ] Đã xóa TẤT CẢ deployments
- [ ] Đã tạo deployment MỚI HOÀN TOÀN
- [ ] Đã copy URL mới
- [ ] Đã test URL mới (Incognito mode)

---

**Hãy thử đổi tên file `TemplatesUI.gs` → `00_TemplatesUI.gs` và deploy lại! 🚀**

