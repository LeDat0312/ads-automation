# 🚀 SETUP TEMPLATES UI - GOOGLE APPS SCRIPT

## 🎯 MỤC TIÊU

Tạo Templates UI trong Google Apps Script (không cần Python server), tương tự Meta Ads/Birch.

---

## 📋 CÁC BƯỚC SETUP

### **BƯỚC 1: Thêm Files vào Google Apps Script**

1. Mở Google Apps Script Editor
2. Tạo file mới: `TemplatesUI.gs`
3. Copy toàn bộ code từ file `TemplatesUI.gs` đã tạo
4. Tạo file HTML mới: `TemplatesUI_HTML.html`
5. Copy toàn bộ code từ file `TemplatesUI_HTML.html` đã tạo

### **BƯỚC 2: Deploy Web App**

1. Vào **Deploy** → **Manage deployments**
2. Click **New deployment**
3. Chọn type: **Web app**
4. Settings:
   - **Execute as:** Me
   - **Who has access:** Anyone
5. Click **Deploy**
6. Copy **Web app URL**

### **BƯỚC 3: Truy cập Templates UI**

Mở browser và vào Web app URL vừa copy.

---

## 🎨 TÍNH NĂNG

### **✅ CÓ:**
- ✅ Tab filter (E-commerce/Lead Generation/Both)
- ✅ Category sections (Essential/Pause/Scale/Optimise/Time)
- ✅ Template cards với icon, title, description
- ✅ Labels (ROAS-based, CPA-based, New)
- ✅ Apply button
- ✅ Modal để apply template

### **📋 TEMPLATES CÓ SẴN:**

#### **Essential:**
- Quick Start ROAS (E-commerce)
- Quick Start CPA (Lead Generation)

#### **Pause:**
- Forfeit the game (E-commerce)
- Down and out (ROAS/CPA)
- On the safe side (Lead Generation)
- Stop Loss (Both)

#### **Scale:**
- Scale Ad Sets (Both)
- Scale Slow and Fast (E-commerce)
- Daily scaling (E-commerce)
- Double down (E-commerce)
- Profit marching (E-commerce)
- To the moon (Lead Generation)

#### **Optimise:**
- Power of threes (ROAS/CPA)
- Roundtable Ad Sets (E-commerce)
- Budget Ladder (E-commerce)
- Fire and Ice (E-commerce)
- Burnouts (Lead Generation)
- Notify about Key Metrics Drops (Both)

#### **Time:**
- Day parting (Both)
- Midnight reset (Both)

---

## 🚀 CÁCH SỬ DỤNG

### **1. Truy cập UI:**
Mở Web app URL trong browser.

### **2. Chọn Campaign Type:**
- Click tab "E-commerce" hoặc "Lead Generation"
- Templates sẽ được filter tự động

### **3. Chọn Template:**
- Xem templates theo category
- Click "Apply" trên template card
- Nhập Account ID và Prefix (optional)
- Click "Apply"

### **4. Template sẽ được apply:**
- Tạo logic rules trong LogicRules sheet
- Hoặc lưu vào database (nếu có)

---

## 🔧 CUSTOMIZE

### **Thêm Template Mới:**

1. Mở `TemplatesUI.gs`
2. Tìm function `getAllTemplates()`
3. Thêm template mới vào array:

```javascript
{
  name: "Your Template Name",
  description: "Description here",
  campaign_type: "ECOMMERCE", // or "LEAD", "BOTH"
  category: "pause", // or "scale", "optimise", "time"
  labels: ["ROAS-based"],
  icon: "pause",
  template_config: {
    rules: [
      {
        name: "Rule Name",
        logic_type: "logic1",
        conditions: {
          spend: { operator: ">", value: 20000 },
          roas: { operator: "<", value: 2.0 }
        },
        action: "PAUSE"
      }
    ]
  }
}
```

---

## 📝 LƯU Ý

### **Apply Template:**
- Hiện tại function `applyTemplate()` chỉ return success
- Cần implement logic để lưu vào LogicRules sheet
- Hoặc tích hợp với database (nếu có)

### **Tích hợp với LogicRules:**
Cần modify function `applyTemplate()` để:
1. Parse template config
2. Convert thành format LogicRules
3. Ghi vào LogicRules sheet

---

## 🎯 NEXT STEPS

1. ✅ Templates UI đã có
2. ⏸️ Implement save to LogicRules sheet
3. ⏸️ Thêm preview modal
4. ⏸️ Thêm customize values
5. ⏸️ Thêm manage applied templates

---

**Bạn có thể truy cập Templates UI sau khi deploy Web App! 🚀**

