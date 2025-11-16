# 🚀 HƯỚNG DẪN CHẠY TEMPLATES UI

## ✅ KHÔNG CẦN CHẠY HÀM GÌ!

TemplatesUI là một **Web App**, chỉ cần:
1. ✅ **Deploy as Web App**
2. ✅ **Truy cập URL**

**KHÔNG CẦN** chạy hàm `doGet()` hay bất kỳ hàm nào khác!

---

## 📋 CÁC BƯỚC CHI TIẾT

### **BƯỚC 1: Kiểm tra Files**

Đảm bảo có 2 files:
- ✅ `TemplatesUI.gs` (có hàm `doGet()`)
- ✅ `TemplatesUI_HTML.html`

### **BƯỚC 2: Kiểm tra Conflict**

Đảm bảo **CHỈ** `TemplatesUI.gs` có hàm `doGet()`:

1. **Telegram.gs:**
   - ✅ Có `doGetTelegram()` (KHÔNG có `doGet()`)

2. **MakeCom_GoogleScript_Integration.gs:**
   - ✅ Có `doGetMakeCom()` (KHÔNG có `doGet()`) - hoặc đã xóa file

3. **TemplatesUI.gs:**
   - ✅ Có `doGet()` (file duy nhất)

### **BƯỚC 3: Lưu Files**

1. **Lưu tất cả files** (Ctrl + S)
2. Đảm bảo không có lỗi syntax

### **BƯỚC 4: Deploy Web App**

1. **Vào Deploy → New deployment** (hoặc Manage deployments)
2. **Click "Select type"** → Chọn **"Web app"**
3. **Settings:**
   - **Description:** (tùy chọn) "Templates UI"
   - **Execute as:** Me (your-email@gmail.com)
   - **Who has access:** Anyone
4. **Click "Deploy"**
5. **Copy Web app URL** (sẽ có dạng: `https://script.google.com/macros/s/.../exec`)

### **BƯỚC 5: Truy cập URL**

1. **Mở URL** trong browser (Chrome, Firefox, Edge...)
2. **Sẽ thấy Templates UI** với:
   - Header: "Rule Templates"
   - Tabs: E-commerce, Lead Generation, Both
   - Categories: Essential, Pause, Scale, Optimise, Time
   - Template cards với nút "Apply"

---

## 🔍 KIỂM TRA

### **Nếu thấy "Telegram Bot Webhook đang hoạt động!":**

1. **Kiểm tra deployment:**
   - Đảm bảo đang dùng URL từ deployment MỚI
   - Không dùng URL từ deployment cũ

2. **Kiểm tra files:**
   - Chỉ `TemplatesUI.gs` có `doGet()`
   - `Telegram.gs` có `doGetTelegram()` (không phải `doGet()`)

3. **Xóa deployment cũ và tạo mới:**
   - Deploy → Manage deployments
   - Xóa deployment cũ
   - Tạo deployment mới

### **Nếu thấy lỗi "Script function not found: doGet":**

1. **Kiểm tra `TemplatesUI.gs`:**
   - Phải có hàm `doGet(e)`
   - Không có typo

2. **Kiểm tra file name:**
   - File phải tên chính xác: `TemplatesUI.gs`
   - Không có khoảng trắng, không có typo

### **Nếu thấy lỗi "Template file not found: TemplatesUI_HTML":**

1. **Kiểm tra file name:**
   - File phải tên chính xác: `TemplatesUI_HTML.html`
   - Không có khoảng trắng, không có typo

2. **Kiểm tra trong Script Editor:**
   - File `TemplatesUI_HTML.html` phải có trong project
   - Không bị ẩn hoặc xóa

---

## ⚠️ LƯU Ý

### **1. Không cần chạy hàm test:**

- ❌ **KHÔNG CẦN** chạy `doGet()` trong Script Editor
- ❌ **KHÔNG CẦN** chạy `getTemplatesData()` trong Script Editor
- ✅ **CHỈ CẦN** deploy và truy cập URL

### **2. Permissions:**

- Lần đầu truy cập URL, Google sẽ yêu cầu **authorize**
- Click **"Authorize access"**
- Chọn tài khoản Google
- Click **"Advanced"** → **"Go to [Project Name] (unsafe)"**
- Click **"Allow"**

### **3. Cache:**

- Nếu thấy UI cũ, **clear browser cache** (Ctrl + Shift + Delete)
- Hoặc mở **Incognito mode** (Ctrl + Shift + N)

---

## 📝 CHECKLIST

- [ ] Có file `TemplatesUI.gs` với hàm `doGet()`
- [ ] Có file `TemplatesUI_HTML.html`
- [ ] `Telegram.gs` có `doGetTelegram()` (không có `doGet()`)
- [ ] `MakeCom_GoogleScript_Integration.gs` đã xóa hoặc có `doGetMakeCom()`
- [ ] Đã lưu tất cả files
- [ ] Đã deploy Web App
- [ ] Đã copy URL
- [ ] Đã truy cập URL
- [ ] Đã authorize (nếu cần)
- [ ] Thấy Templates UI

---

## 🎯 TÓM TẮT

### **CÁCH CHẠY:**
1. ✅ Deploy Web App
2. ✅ Truy cập URL
3. ✅ Done!

### **KHÔNG CẦN:**
- ❌ Chạy hàm trong Script Editor
- ❌ Setup database
- ❌ Cấu hình đặc biệt

---

**Chỉ cần deploy và truy cập URL là xong! 🚀**

