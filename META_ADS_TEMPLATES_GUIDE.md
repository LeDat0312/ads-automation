# 🎨 META ADS STYLE TEMPLATES - HƯỚNG DẪN

## 🎯 MỤC TIÊU

Tạo hệ thống rule templates tương tự Meta Ads automation rules:
- ✅ Chọn template sẵn (1 click)
- ✅ Phân loại theo E-commerce/Lead Generation
- ✅ Phân loại theo category (Essential/Pause/Scale/Optimise)
- ✅ Apply cho account/campaign/prefix
- ✅ Customize nếu cần

---

## 📋 TEMPLATES CÓ SẴN

### **1. ESSENTIAL (Quick Start):**

#### **Quick Start ROAS (E-commerce):**
- Pause Low ROAS
- Resume High ROAS
- Scale Budget

#### **Quick Start CPA (Lead Generation):**
- Pause High CPA
- Resume Low CPA
- Scale Budget

---

### **2. PAUSE:**

#### **E-commerce:**
- **"Forfeit the game":** Tắt adset khi đã chi > 50% budget và ROAS thấp
- **"Down and out":** Tắt khi ROAS < average ROAS

#### **Lead Generation:**
- **"Down and out":** Tắt khi CPA > average CPA
- **"No leads":** Tắt khi chi tiêu cao nhưng không có lead

---

### **3. SCALE:**

#### **E-commerce:**
- **"Scale Ad Sets":** Tăng budget cho adset tốt, giảm cho adset kém
- **"Daily scaling":** Scale budget nếu đã chi 50% budget với ROAS cao

#### **Lead Generation:**
- **"To the moon":** Scale budget nếu CPA < average CPA

---

### **4. OPTIMISE:**

#### **E-commerce:**
- **"Power of threes (ROAS)":** Tắt tất cả lúc midnight, chỉ bật lại top 3 performers
- **"Roundtable Ad Sets":** Launch 3 adset mới nếu account ROAS > 3

#### **Lead Generation:**
- **"Power of threes (CPA)":** Tắt tất cả lúc midnight, chỉ bật lại top 3 performers
- **"Burnouts":** Notify nếu CTR giảm
- **"Notify about Key Metrics Drops":** Notify nếu Leads, CPL, CPM thay đổi

---

## 🚀 CÁCH SỬ DỤNG

### **1. Truy cập Templates UI:**

```
http://localhost:8000/api/templates/ui/page
```

### **2. Chọn Campaign Type:**
- Click tab "E-commerce" hoặc "Lead Generation"
- Templates sẽ được filter theo type

### **3. Chọn Template:**
- Xem templates theo category (Essential/Pause/Scale/Optimise)
- Click "Apply" trên template card

### **4. Apply Template:**
- Nhập Account ID
- Nhập Prefix (optional)
- Click "Apply"
- Template sẽ được tạo thành logic rule

---

## 📝 API ENDPOINTS

### **1. Get Templates UI:**
```
GET /api/templates/ui?campaign_type=ECOMMERCE&category=essential
```

### **2. Get Template Details:**
```
GET /api/templates/ui/{template_name}
```

### **3. Apply Template:**
```
POST /api/templates/ui/{template_name}/apply
Body: {
  "account_id": "act_123",
  "prefix": "PX",
  "campaign_id": "campaign_123",
  "custom_values": {}
}
```

---

## 🎨 UI FEATURES

### **✅ CÓ:**
- ✅ Tab filter (E-commerce/Lead Generation/Both)
- ✅ Category sections (Essential/Pause/Scale/Optimise)
- ✅ Template cards với icon, title, description
- ✅ Labels (ROAS-based, CPA-based, New)
- ✅ Apply button
- ✅ Preview (sẽ thêm)

### **⏸️ SẼ THÊM:**
- ⏸️ Preview modal
- ⏸️ Customize values
- ⏸️ Apply cho nhiều accounts/campaigns
- ⏸️ Manage applied templates

---

## 💡 SO SÁNH VỚI GOOGLE SHEETS

| Tính năng | Google Sheets | Templates UI |
|-----------|---------------|--------------|
| **Setup** | ⚠️ Phức tạp, không trực quan | ✅ Chọn template (1 click) |
| **Customize** | ✅ Linh hoạt | ✅ Có thể customize |
| **Visual** | ❌ Chỉ có text | ✅ Cards, icons, labels |
| **Category** | ❌ Không có | ✅ Có category |
| **Campaign Type** | ⚠️ Phải tự phân loại | ✅ Auto filter |
| **Speed** | ⚠️ Chậm | ✅ Nhanh |

---

## 🎯 LỢI ÍCH

### **✅ DỄ SỬ DỤNG:**
- ✅ Chọn template sẵn (như Meta Ads)
- ✅ Không cần hiểu logic phức tạp
- ✅ Visual interface

### **✅ NHANH:**
- ✅ Apply trong vài giây
- ✅ Không cần edit Google Sheets
- ✅ Tự động tạo logic rules

### **✅ LINH HOẠT:**
- ✅ Có thể customize values
- ✅ Apply cho nhiều accounts/campaigns
- ✅ Quản lý dễ dàng

---

## 📝 NEXT STEPS

1. ✅ Templates đã được định nghĩa
2. ✅ API endpoints đã có
3. ✅ UI page đã có
4. ⏸️ Thêm preview modal
5. ⏸️ Thêm customize values
6. ⏸️ Thêm manage applied templates

---

**Bạn có thể truy cập Templates UI tại: `http://localhost:8000/api/templates/ui/page` 🚀**

