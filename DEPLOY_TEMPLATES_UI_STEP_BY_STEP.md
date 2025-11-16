# 🚀 HƯỚNG DẪN DEPLOY TEMPLATES UI - TỪNG BƯỚC

## 🎯 VẤN ĐỀ

URL `https://script.google.com/macros/s/AKfycbxpgq-Ru9aBXAJ7blRltCKEqaPV4coXPIgm3cNFDXgaNx_0WVkPqZ7e9wIlZ2Lc6aoE/exec` vẫn hiển thị "Telegram Bot Webhook đang hoạt động!"

**Nguyên nhân:** URL này đang trỏ đến deployment của `Telegram.gs` (có hàm `doGet()` cũ), không phải `TemplatesUI.gs`.

---

## ✅ GIẢI PHÁP

### **CÁCH 1: Tạo Deployment MỚI Cho TemplatesUI (KHUYẾN NGHỊ)**

#### **BƯỚC 1: Kiểm tra Files**

1. Mở Google Apps Script Editor
2. Kiểm tra có 2 files:
   - ✅ `TemplatesUI.gs` (có hàm `doGet()`)
   - ✅ `TemplatesUI_HTML.html`

#### **BƯỚC 2: Tạo Deployment MỚI**

1. **Vào Deploy → Manage deployments**
2. **Click "New deployment"** (KHÔNG edit deployment cũ)
3. **Chọn type:** Web app
4. **Settings:**
   - **Execute as:** Me
   - **Who has access:** Anyone
5. **Click "Deploy"**
6. **Copy Web app URL MỚI** (sẽ khác URL cũ)

#### **BƯỚC 3: Truy cập URL MỚI**

- Mở URL mới trong browser
- Sẽ thấy Templates UI

---

### **CÁCH 2: Update Deployment Hiện Tại**

Nếu bạn muốn dùng cùng URL (không khuyến nghị):

1. **Vào Deploy → Manage deployments**
2. **Click vào deployment hiện tại** (có URL cũ)
3. **Click Edit** (biểu tượng bút chì)
4. **Chọn "New version"**
5. **Đảm bảo:**
   - **Execute as:** Me
   - **Who has access:** Anyone
6. **Click "Deploy"**
7. **Truy cập lại URL** (có thể cần clear cache)

---

## 🔍 KIỂM TRA

### **1. Kiểm tra TemplatesUI.gs có hàm doGet():**

Mở `TemplatesUI.gs`, tìm:
```javascript
function doGet(e) {
  return HtmlService.createTemplateFromFile('TemplatesUI_HTML')
    .evaluate()
    .setTitle('Rule Templates - Meta Ads Style')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}
```

✅ **PHẢI CÓ** hàm `doGet()` (không phải `doGetTemplatesUI()`)

### **2. Kiểm tra TemplatesUI_HTML.html:**

- ✅ File phải có tên chính xác: `TemplatesUI_HTML.html`
- ✅ Không có khoảng trắng, không có typo

### **3. Kiểm tra Telegram.gs:**

Nếu `Telegram.gs` vẫn có hàm `doGet()` trả về "Telegram Bot Webhook đang hoạt động!", bạn có 2 lựa chọn:

**Option A:** Xóa hàm `doGet()` trong Telegram.gs (nếu không cần webhook)
**Option B:** Đổi tên hàm `doGet()` trong Telegram.gs thành `doGetTelegram()` (để tránh conflict)

---

## ⚠️ LƯU Ý QUAN TRỌNG

### **Nếu có nhiều files có hàm doGet():**

Google Apps Script sẽ chọn hàm `doGet()` đầu tiên nó tìm thấy. Nếu cả `Telegram.gs` và `TemplatesUI.gs` đều có `doGet()`, có thể bị conflict.

**Giải pháp:**
1. **Xóa hoặc đổi tên** hàm `doGet()` trong `Telegram.gs`
2. **Hoặc** chỉ giữ `doGet()` trong `TemplatesUI.gs`

---

## 🚀 CÁC BƯỚC CHÍNH XÁC

### **BƯỚC 1: Xóa/Đổi tên doGet() trong Telegram.gs**

1. Mở `Telegram.gs`
2. Tìm hàm `doGet()` (khoảng dòng 992)
3. **Xóa hoặc đổi tên** thành `doGetTelegram()`:

```javascript
// XÓA HOẶC ĐỔI TÊN:
function doGetTelegram(e) {  // Đổi tên từ doGet()
  var output = ContentService.createTextOutput("Telegram Bot Webhook đang hoạt động!");
  output.setMimeType(ContentService.MimeType.TEXT);
  return output;
}
```

### **BƯỚC 2: Tạo Deployment MỚI**

1. **Deploy → New deployment**
2. **Web app**
3. **Settings:**
   - Execute as: Me
   - Who has access: Anyone
4. **Deploy**
5. **Copy URL mới**

### **BƯỚC 3: Test**

1. Mở URL mới
2. Sẽ thấy Templates UI

---

## 📝 CHECKLIST

- [ ] `TemplatesUI.gs` có hàm `doGet()`
- [ ] `TemplatesUI_HTML.html` tồn tại
- [ ] `Telegram.gs` KHÔNG có hàm `doGet()` (hoặc đã đổi tên)
- [ ] Đã tạo deployment MỚI
- [ ] Đã copy URL mới
- [ ] Đã truy cập URL mới

---

**Bạn thử xóa/đổi tên hàm `doGet()` trong Telegram.gs và tạo deployment mới nhé! 🚀**

