# 🎨 RULE TEMPLATES UI - GIAO DIỆN CHỌN TEMPLATES

## 🎯 MỤC TIÊU

Tạo giao diện chọn và apply rule templates tương tự Meta Ads/Birch/Madgicx:
- ✅ Chọn template sẵn (1 click)
- ✅ Preview conditions
- ✅ Apply cho account/campaign/objective
- ✅ Customize nếu cần
- ✅ Quản lý dễ dàng

---

## 📋 TEMPLATES CÓ SẴN (Dựa trên Meta Ads)

### **1. QUICK START TEMPLATES:**

#### **ROAS-based (E-commerce):**
- **Quick Start ROAS:** 3 automations cơ bản (pause, start, scale)
- **Pause Low ROAS:** Tắt khi ROAS < 2.0
- **Resume High ROAS:** Bật lại khi ROAS >= 2.0
- **Scale Budget:** Tăng budget khi ROAS tốt

#### **CPA-based (Lead Generation):**
- **Quick Start CPA:** 3 automations cơ bản (pause, start, scale)
- **Pause High CPA:** Tắt khi CPA > threshold
- **Resume Low CPA:** Bật lại khi CPA < threshold
- **Scale Budget:** Tăng budget khi CPA tốt

---

### **2. PAUSE TEMPLATES:**

#### **E-commerce:**
- **"Forfeit the game":** Tắt adset khi đã chi > 50% budget và ROAS thấp
- **"Down and out":** Tắt khi ROAS < average ROAS

#### **Lead Generation:**
- **"Down and out":** Tắt khi CPA > average CPA
- **"No leads":** Tắt khi chi tiêu cao nhưng không có lead

---

### **3. SCALE TEMPLATES:**

#### **E-commerce:**
- **"Scale Ad Sets":** Tăng budget cho adset tốt, giảm cho adset kém
- **"Double down":** Duplicate campaign tốt với budget x2
- **"Daily scaling":** Scale budget nếu đã chi 50% budget với ROAS cao
- **"Profit marching":** Scale budget nếu campaign tốt ngày hôm trước

#### **Lead Generation:**
- **"To the moon":** Scale budget nếu CPA < average CPA
- **"Scale Slow and Fast":** Scale budget dựa trên CPA ở adset và account level

---

### **4. OPTIMISE TEMPLATES:**

#### **E-commerce:**
- **"Budget Ladder":** Reset và adjust budget dựa trên performance hôm qua
- **"Fire and Ice":** Visual indicator cho adset tốt/kém
- **"Power of threes":** Tắt tất cả lúc midnight, chỉ bật lại top 3 performers
- **"Roundtable Ad Sets":** Launch 3 adset mới nếu account ROAS > 3

#### **Lead Generation:**
- **"Power of threes":** Tắt tất cả lúc midnight, chỉ bật lại top 3 performers (CPA-based)
- **"Burnouts":** Notify nếu CTR giảm
- **"Notify about Key Metrics Drops":** Notify nếu Leads, CPL, CPM thay đổi

---

## 🎨 UI DESIGN

### **Layout tương tự Meta Ads:**

```
┌─────────────────────────────────────────┐
│  RULE TEMPLATES                         │
│                                         │
│  [E-commerce] [Lead Generation] [Both] │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Essential                         │ │
│  │                                   │ │
│  │ ┌──────────┐  ┌──────────┐       │ │
│  │ │ Quick    │  │ Quick    │       │ │
│  │ │ Start    │  │ Start    │       │ │
│  │ │ ROAS     │  │ CPA      │       │ │
│  │ │          │  │          │       │ │
│  │ │ 3 auto-  │  │ 3 auto-  │       │ │
│  │ │ mations  │  │ mations  │       │ │
│  │ └──────────┘  └──────────┘       │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Pause                              │ │
│  │                                   │ │
│  │ ┌──────────┐  ┌──────────┐       │ │
│  │ │ Down and │  │ Forfeit  │       │ │
│  │ │ out      │  │ the game │       │ │
│  │ │          │  │          │       │ │
│  │ │ Pause    │  │ Pause    │       │ │
│  │ │ high CPA │  │ low ROAS │       │ │
│  │ └──────────┘  └──────────┘       │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Scale                              │ │
│  │                                   │ │
│  │ [Grid of scale templates]          │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Optimise                           │ │
│  │                                   │ │
│  │ [Grid of optimise templates]       │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 🚀 IMPLEMENTATION

### **1. API Endpoints:**

```python
# app/api/routes/templates.py

@router.get("/templates/ui")
async def get_templates_ui(
    campaign_type: Optional[str] = None,
    category: Optional[str] = None  # 'essential', 'pause', 'scale', 'optimise'
):
    """Get templates grouped by category for UI"""
    
@router.get("/templates/{template_id}/preview")
async def preview_template(template_id: int):
    """Preview template conditions"""
    
@router.post("/templates/{template_id}/apply")
async def apply_template_ui(
    template_id: int,
    account_id: str,
    prefix: Optional[str] = None,
    campaign_id: Optional[str] = None,
    custom_values: Optional[Dict] = None
):
    """Apply template with UI-friendly response"""
```

### **2. Dashboard UI Section:**

Thêm section "Rule Templates" vào dashboard:
- Tab "Templates" bên cạnh "Dashboard"
- Filter theo campaign type (E-commerce/Lead)
- Filter theo category (Essential/Pause/Scale/Optimise)
- Grid layout với cards
- Click card → Preview → Apply

### **3. Template Cards:**

Mỗi card hiển thị:
- Icon
- Title
- Description
- Labels (ROAS-based, CPA-based, New)
- Button "Apply" hoặc "Preview"

---

## 📝 TEMPLATE DEFINITIONS

### **Template 1: Quick Start ROAS (E-commerce)**

```json
{
  "name": "Quick Start ROAS",
  "description": "Three essential automations for pausing, starting, and scaling budgets",
  "campaign_type": "ECOMMERCE",
  "category": "essential",
  "labels": ["ROAS-based", "Quick Start"],
  "icon": "play",
  "template_config": {
    "rules": [
      {
        "name": "Pause Low ROAS",
        "logic_type": "logic1",
        "conditions": {
          "spend": { "operator": ">", "value": 20000 },
          "roas": { "operator": "<", "value": 2.0 }
        },
        "action": "PAUSE"
      },
      {
        "name": "Resume High ROAS",
        "logic_type": "logic3",
        "conditions": {
          "spend": { "operator": ">", "value": 15000 },
          "roas": { "operator": ">=", "value": 2.0 },
          "results": { "operator": ">", "value": 0 }
        },
        "action": "RESUME"
      },
      {
        "name": "Scale Budget",
        "logic_type": "scale",
        "conditions": {
          "roas": { "operator": ">=", "value": 3.0 },
          "spend": { "operator": ">", "value": 10000 }
        },
        "action": "INCREASE_BUDGET",
        "amount_percent": 20
      }
    ]
  }
}
```

### **Template 2: Quick Start CPA (Lead Generation)**

```json
{
  "name": "Quick Start CPA",
  "description": "Three essential automations for pausing, starting, and scaling budgets",
  "campaign_type": "LEAD",
  "category": "essential",
  "labels": ["CPA-based", "Quick Start"],
  "icon": "play",
  "template_config": {
    "rules": [
      {
        "name": "Pause High CPA",
        "logic_type": "logic1",
        "conditions": {
          "spend": { "operator": ">", "value": 20000 },
          "cost_per_lead": { "operator": ">", "value": 15000 }
        },
        "action": "PAUSE"
      },
      {
        "name": "Resume Low CPA",
        "logic_type": "logic3",
        "conditions": {
          "spend": { "operator": ">", "value": 15000 },
          "cost_per_lead": { "operator": "<", "value": 10000 },
          "leads": { "operator": ">", "value": 0 }
        },
        "action": "RESUME"
      },
      {
        "name": "Scale Budget",
        "logic_type": "scale",
        "conditions": {
          "cost_per_lead": { "operator": "<", "value": 8000 },
          "spend": { "operator": ">", "value": 10000 }
        },
        "action": "INCREASE_BUDGET",
        "amount_percent": 20
      }
    ]
  }
}
```

---

## 🎯 NEXT STEPS

1. ✅ Tạo nhiều templates sẵn hơn (dựa trên Meta Ads)
2. ✅ Thêm UI section vào dashboard
3. ✅ Tạo template cards với preview
4. ✅ Apply template với customization
5. ✅ Quản lý applied templates

---

**Bạn muốn tôi implement UI này không? 🚀**

