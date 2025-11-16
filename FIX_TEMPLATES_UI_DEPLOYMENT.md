# 🔧 SỬA LỖI TEMPLATES UI DEPLOYMENT

## 🎯 VẤN ĐỀ

Khi truy cập Web App URL, vẫn thấy "Telegram Bot Webhook đang hoạt động!" thay vì Templates UI.

**Nguyên nhân:**
- URL đang trỏ đến deployment cũ (Telegram.gs với `doGet()` cũ)
- Hoặc TemplatesUI.gs chưa có hàm `doGet()` đúng

---

## ✅ GIẢI PHÁP

### **CÁCH 1: Tạo Deployment Mới Cho TemplatesUI (KHUYẾN NGHỊ)**

1. **Đảm bảo có file:**
   - ✅ `TemplatesUI.gs` (đã có hàm `doGet()`)
   - ✅ `TemplatesUI_HTML.html` (đã sửa để dùng `google.script.run`)

2. **Deploy Web App:**
   - Vào **Deploy** → **Manage deployments**
   - Click **New deployment**
   - Chọn type: **Web app**
   - Settings:
     - **Execute as:** Me
     - **Who has access:** Anyone
   - Click **Deploy**
   - **Copy Web app URL mới**

3. **Truy cập URL mới:**
   - Mở URL mới trong browser
   - Sẽ thấy Templates UI

---

### **CÁCH 2: Sửa Deployment Cũ**

1. **Vào Deploy → Manage deployments**
2. **Chọn deployment cũ** (có message "Telegram Bot Webhook đang hoạt động!")
3. **Click Edit (biểu tượng bút chì)**
4. **Chọn "New version"**
5. **Deploy**
6. **Truy cập lại URL**

---

## 🔍 KIỂM TRA

### **1. Kiểm tra TemplatesUI.gs có hàm doGet():**

```javascript
function doGet(e) {
  return HtmlService.createTemplateFromFile('TemplatesUI_HTML')
    .evaluate()
    .setTitle('Rule Templates - Meta Ads Style')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}
```

### **2. Kiểm tra TemplatesUI_HTML.html dùng google.script.run:**

```javascript
// ĐÚNG:
google.script.run
    .withSuccessHandler(displayTemplates)
    .withFailureHandler(showError)
    .getTemplatesData(campaignType, null);

// SAI (fetch API không hoạt động trong Google Apps Script):
const response = await fetch(`/api/templates/ui?campaign_type=${campaignType}`);
```

---

## 🚀 CÁC BƯỚC CHÍNH XÁC

### **BƯỚC 1: Kiểm tra Files**

1. ✅ `TemplatesUI.gs` có hàm `doGet()`
2. ✅ `TemplatesUI_HTML.html` dùng `google.script.run` (không dùng `fetch`)

### **BƯỚC 2: Deploy**

1. Vào **Deploy** → **Manage deployments**
2. Click **New deployment**
3. Chọn type: **Web app**
4. Settings:
   - **Execute as:** Me
   - **Who has access:** Anyone
5. Click **Deploy**
6. **Copy Web app URL**

### **BƯỚC 3: Test**

1. Mở URL trong browser
2. Sẽ thấy Templates UI với tabs (E-commerce, Lead Generation, Both)
3. Sẽ thấy templates theo category (Essential, Pause, Scale, Optimise, Time)

---

## ⚠️ LƯU Ý

### **Nếu vẫn thấy "Telegram Bot Webhook đang hoạt động!":**

1. **Kiểm tra URL:**
   - Đảm bảo đang dùng URL mới từ deployment mới
   - Không dùng URL cũ từ Telegram.gs

2. **Kiểm tra file:**
   - Đảm bảo `TemplatesUI.gs` có hàm `doGet()`
   - Đảm bảo `TemplatesUI_HTML.html` tồn tại

3. **Clear cache:**
   - Thử mở URL trong incognito mode
   - Hoặc clear browser cache

---

## 📝 CODE ĐÃ SỬA

### **TemplatesUI.gs:**
- ✅ Đã đổi `doGetTemplatesUI()` → `doGet()`
- ✅ Serve HTML từ `TemplatesUI_HTML.html`

### **TemplatesUI_HTML.html:**
- ✅ Đã sửa `fetch()` → `google.script.run`
- ✅ Đã thêm hàm `displayTemplates()`
- ✅ Đã sửa `applyTemplate()` dùng `google.script.run`

---

**Bạn thử deploy lại và truy cập URL mới nhé! 🚀**

