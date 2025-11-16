# ✅ IMPLEMENT SAVE LOGIC - TEMPLATES UI

## 🎯 VẤN ĐỀ

1. **Logic CHƯA được áp dụng:** Hàm `applyTemplate()` chỉ trả về success message, **KHÔNG lưu vào LogicRules sheet**
2. **Thiếu form tùy chỉnh:** Chỉ có form đơn giản (Account ID + Prefix), **KHÔNG có form tùy chỉnh sâu** như Birch

---

## ✅ ĐÃ IMPLEMENT

### **1. Hàm Lưu vào LogicRules Sheet:**

Đã tạo hàm `saveLogicRulesToSheet()` trong file `TemplatesUI_SaveFunction.gs`. 

**Bạn cần:**
1. Copy toàn bộ code từ file `TemplatesUI_SaveFunction.gs`
2. Paste vào cuối file `TemplatesUI.gs` (sau dòng 714)

### **2. Hàm applyTemplate() đã được sửa:**

Hàm `applyTemplate()` đã gọi `saveLogicRulesToSheet()`, nhưng hàm này chưa có trong file `TemplatesUI.gs`.

---

## 🚀 CÁC BƯỚC

### **BƯỚC 1: Thêm hàm saveLogicRulesToSheet()**

1. **Mở file `TemplatesUI_SaveFunction.gs`**
2. **Copy toàn bộ code** (từ dòng 1 đến dòng 124)
3. **Mở file `TemplatesUI.gs`**
4. **Paste vào cuối file** (sau dòng 714)

### **BƯỚC 2: Test**

1. **Chạy hàm `applyTemplate()` trong Script Editor:**
   - Chọn template "Quick Start ROAS"
   - Nhập Account ID: `2827767517395636`
   - Nhập Prefix: `FL`
   - Xem Execution log

2. **Kiểm tra LogicRules sheet:**
   - Có cột mới `act_2827767517395636|FL` không?
   - Có giá trị được lưu vào `SL_GIAI_DOAN_1_SPEND` không?

### **BƯỚC 3: Test trong UI**

1. **Deploy Web App**
2. **Mở URL**
3. **Apply template**
4. **Kiểm tra LogicRules sheet**

---

## 📝 FORMAT LOGICRULES SHEET

### **Headers (Hàng 1):**
- Cột A: KEY
- Cột B: Ghi chú
- Cột C: DEFAULT|DEFAULT
- Cột D+: act_123|PX, act_123|FL, ...

### **Rows (Hàng 2+):**
- `SL_GIAI_DOAN_1_SPEND`: Giá trị spend threshold
- `SL_GIAI_DOAN_1_DATA`: Giá trị data threshold
- `SL_GIAI_DOAN_2_GIA_DATA`: Giá trị giá data threshold
- `SL_GIAI_DOAN_3_MAX_CPL`: CPL tối đa
- `SL_GIAI_DOAN_4_MAX_CPA`: CPA tối đa
- ...

---

## 🔍 KIỂM TRA

### **1. Test Hàm Lưu:**
1. Chạy `applyTemplate("Quick Start ROAS", "2827767517395636", "FL", {})`
2. Kiểm tra LogicRules sheet:
   - Có cột mới cho `act_2827767517395636|FL` không?
   - Có giá trị được lưu không?

### **2. Test Logic:**
1. Chạy `runAutomation()`
2. Kiểm tra xem logic có được áp dụng không

---

## ⚠️ LƯU Ý

### **1. Logic Rules Keys:**
- `SL_GIAI_DOAN_1_SPEND`: Map từ `condition_spend`
- `SL_GIAI_DOAN_1_DATA`: Map từ `condition_results`
- `SL_GIAI_DOAN_2_GIA_DATA`: Map từ `condition_gia_data`
- `SL_GIAI_DOAN_3_MAX_CPL`: Chưa được map (cần thêm)
- `SL_GIAI_DOAN_4_MAX_CPA`: Chưa được map (cần thêm)

### **2. ROAS Condition:**
- ROAS condition chưa được map - cần thêm logic mapping

---

## 🎨 NEXT STEPS - FORM TÙY CHỈNH

### **Cần implement:**
1. **Form Conditions:**
   - Multiple conditions với AND/OR logic
   - Timeframes (Today, Last 3 days, Last 7 days)
   - Comparisons (>, <, >=, <=, ==, multipliers like 1.3x, 1.5x)

2. **Form Thresholds:**
   - Values, percentages
   - Custom metrics

3. **Form Schedule:**
   - Every 60 minutes
   - Specific days/times

4. **Form Notifications:**
   - Email, Slack

5. **Form Filters:**
   - Ad sets status
   - Campaign types

---

**Đã implement hàm lưu. Cần copy code vào TemplatesUI.gs và test! 🚀**


