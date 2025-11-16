# 🎨 TÙY CHỈNH TEMPLATES UI - NHƯ BIRCH

## 🎯 YÊU CẦU

Người dùng muốn:
1. ✅ **Logic được áp dụng thực sự** (lưu vào LogicRules sheet)
2. ✅ **Tùy chỉnh sâu hơn** như Birch:
   - Conditions phức tạp (multiple conditions với AND/OR)
   - Timeframes (Today, Last 3 days, Last 7 days)
   - Comparisons (>, <, >=, <=, ==, multipliers like 1.3x, 1.5x)
   - Thresholds (values, percentages)
   - Schedule (every 60 minutes, specific days/times)
   - Notifications (Email, Slack)
   - Filters (ad sets status, campaign types)

---

## ✅ ĐÃ IMPLEMENT

### **1. Lưu vào LogicRules Sheet:**
- ✅ Hàm `saveLogicRulesToSheet()` - Lưu logic rules vào LogicRules sheet
- ✅ Hàm `mapLogicTypeToKey()` - Map logic_type sang LogicRules key
- ✅ Tự động tạo cột mới nếu chưa có (account_id|prefix)
- ✅ Tự động tạo hàng mới nếu chưa có (logic key)
- ✅ Clear cache sau khi lưu

### **2. Form Tùy Chỉnh (Cần implement):**
- ❌ Form tùy chỉnh conditions
- ❌ Form tùy chỉnh thresholds
- ❌ Form tùy chỉnh timeframes
- ❌ Form tùy chỉnh schedule
- ❌ Form tùy chỉnh notifications
- ❌ Form tùy chỉnh filters

---

## 🚀 NEXT STEPS

### **BƯỚC 1: Test Hàm Lưu**

1. **Chạy hàm `applyTemplate()` trong Script Editor:**
   - Chọn template
   - Nhập Account ID và Prefix
   - Kiểm tra LogicRules sheet xem có được lưu không

### **BƯỚC 2: Tạo Form Tùy Chỉnh**

1. **Update HTML:**
   - Thêm form tùy chỉnh conditions
   - Thêm form tùy chỉnh thresholds
   - Thêm form tùy chỉnh timeframes
   - Thêm form tùy chỉnh schedule
   - Thêm form tùy chỉnh notifications

2. **Update JavaScript:**
   - Xử lý form tùy chỉnh
   - Gửi custom values đến server

3. **Update Server-side:**
   - Nhận custom values
   - Áp dụng custom values vào logic rules

---

## 📝 FORMAT LOGICRULES SHEET

### **Headers (Hàng 1):**
- Cột A: KEY
- Cột B: Ghi chú
- Cột C: DEFAULT|DEFAULT
- Cột D+: act_123|PX, act_123|FL, ...

### **Rows (Hàng 2+):**
- SL_1_SPEND: Giá trị spend threshold
- SL_1_DATA: Giá trị data threshold
- SL_1_GIA_DATA: Giá trị giá data threshold
- SL_1_ROAS: Giá trị ROAS threshold
- SL_2_SPEND: Giá trị spend threshold cho logic2
- SL_3_SPEND: Giá trị spend threshold cho logic3
- ...

---

## 🔍 KIỂM TRA

### **1. Test Hàm Lưu:**
1. Chạy `applyTemplate()` với template "Quick Start ROAS"
2. Kiểm tra LogicRules sheet:
   - Có cột mới cho account_id|prefix không?
   - Có giá trị được lưu không?

### **2. Test Logic:**
1. Chạy `runAutomation()`
2. Kiểm tra xem logic có được áp dụng không

---

**Đã implement hàm lưu vào LogicRules sheet. Cần test và tạo form tùy chỉnh! 🚀**


