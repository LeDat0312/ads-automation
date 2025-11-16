# 🚀 SETUP SCALE AD SETS UI - TÙY CHỈNH SÂU NHƯ BIRCH

## 🎯 TỔNG QUAN

Đã tạo giao diện tùy chỉnh sâu cho "Scale Ad Sets" giống như Birch, với đầy đủ các tính năng:

1. ✅ **Trang Overview** (Ảnh 1-2): Hiển thị strategy và nút "Create 2 rules"
2. ✅ **Modal Tạo Folder** (Ảnh 3): Tạo folder mới hoặc gộp vào folder có sẵn
3. ✅ **Trang General** (Ảnh 4): Quản lý rules với toggle switch, edit, duplicate, delete, logs
4. ✅ **Trang Customize** (Ảnh 5-13): Tùy chỉnh chi tiết với:
   - Ad Account selection
   - Filter configuration
   - Task với conditions phức tạp
   - Schedule (interval hoặc custom)
   - Notifications
   - Time Zone

---

## 📁 FILES ĐÃ TẠO

### **1. TemplatesUI_ScaleAdSets_HTML.html**
- Trang tùy chỉnh chi tiết cho rule
- Form đầy đủ: Ad Account, Filter, Task, Schedule, Notifications, Time Zone

### **2. TemplatesUI_ScaleAdSets.gs**
- Server-side functions:
  - `getConnectedAccounts()` - Lấy danh sách tài khoản
  - `getAvailableMetrics()` - Lấy metrics từ Meta Ads hoặc Custom
  - `saveRuleDraft()` - Lưu draft
  - `setRuleLive()` - Set rule live và convert sang LogicRules
  - `createScaleAdSetsRules()` - Tạo 2 rules (Increase + Decrease)
  - `getAllRuleFolders()` - Lấy tất cả folders
  - `toggleRuleStatus()` - Bật/tắt rule
  - `duplicateRule()` - Duplicate rule
  - `deleteRule()` - Xóa rule

### **3. TemplatesUI_General_HTML.html**
- Trang quản lý rules (General)
- Hiển thị folders và rules
- Toggle switch, edit, duplicate, delete, logs

### **4. TemplatesUI_ScaleAdSets_Overview_HTML.html**
- Trang overview của "Scale Ad Sets"
- Hiển thị strategy và nút "Create 2 rules"

---

## 🚀 CÁC BƯỚC SETUP

### **BƯỚC 1: Thêm Files vào Google Apps Script**

1. **Copy các files vào Script Editor:**
   - `TemplatesUI_ScaleAdSets_HTML.html`
   - `TemplatesUI_General_HTML.html`
   - `TemplatesUI_ScaleAdSets_Overview_HTML.html`
   - `TemplatesUI_ScaleAdSets.gs`

2. **Copy hàm `saveLogicRulesToSheet()` từ `TemplatesUI_SaveFunction.gs` vào cuối `TemplatesUI.gs`**

### **BƯỚC 2: Update TemplatesUI.gs**

File `TemplatesUI.gs` đã được update để:
- Route các pages khác nhau (`?page=scale-ad-sets`, `?page=general`, etc.)
- Gọi các hàm từ `TemplatesUI_ScaleAdSets.gs`

### **BƯỚC 3: Test**

1. **Deploy Web App:**
   - Deploy → New deployment
   - Type: Web app
   - Execute as: Me
   - Who has access: Anyone
   - Deploy

2. **Test các pages:**
   - `?page=templates` - Templates UI (mặc định)
   - `?page=scale-ad-sets-overview` - Scale Ad Sets Overview
   - `?page=scale-ad-sets` - Customize rule
   - `?page=general` - General rules management

---

## 📋 CÁC TÍNH NĂNG

### **1. Scale Ad Sets Overview:**
- ✅ Hiển thị strategy description
- ✅ Nút "Create 2 rules"
- ✅ Modal tạo folder mới hoặc gộp vào folder có sẵn
- ✅ List 2 rules: Increase và Decrease

### **2. General Page:**
- ✅ Hiển thị folders và rules
- ✅ Toggle switch để bật/tắt rule
- ✅ Edit, Duplicate, Delete, Logs buttons
- ✅ Filter: All rules, Active, Triggered
- ✅ Search và Account filter

### **3. Customize Page:**
- ✅ **Ad Account:** Chọn tối đa 5 tài khoản
- ✅ **Filter:** Ad sets, Campaign status, etc.
- ✅ **Task:**
  - Multiple conditions với AND logic
  - Timeframes: Today, Last 3 days, Last 7 days
  - Comparisons: >, <, >=, <=, ==, multipliers (0.8x, 0.9x)
  - Metric selection từ Meta Ads hoặc Custom metrics
- ✅ **Schedule:**
  - Run every X minutes/hours
  - Run on specific days and times (grid)
- ✅ **Notifications:** Email, Slack
- ✅ **Time Zone:** Dropdown selection

---

## 🔧 CẦN HOÀN THIỆN

### **1. Metric Selection Modal:**
- ✅ UI đã có
- ❌ Cần load metrics từ server
- ❌ Cần search functionality

### **2. Browse Templates:**
- ✅ UI đã có
- ❌ Cần load templates từ server
- ❌ Cần sidebar functionality

### **3. Convert Rule to LogicRules:**
- ✅ Hàm `convertRuleToLogicRules()` đã có (placeholder)
- ❌ Cần implement logic conversion chi tiết

### **4. Estimated Match:**
- ✅ UI đã có
- ❌ Cần tính toán dựa trên filters

---

## 📝 CHECKLIST

- [ ] Đã copy tất cả HTML files vào Script Editor
- [ ] Đã copy `TemplatesUI_ScaleAdSets.gs` vào Script Editor
- [ ] Đã copy hàm `saveLogicRulesToSheet()` vào `TemplatesUI.gs`
- [ ] Đã test deploy Web App
- [ ] Đã test các pages
- [ ] Đã test tạo rules
- [ ] Đã test toggle switch
- [ ] Đã test edit, duplicate, delete

---

**Đã tạo đầy đủ giao diện! Cần copy files vào Script Editor và test! 🚀**

