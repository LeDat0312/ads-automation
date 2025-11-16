# 🎯 CAMPAIGN TYPE DETECTION - E-COMMERCE VS LEAD

## 📋 VẤN ĐỀ

Cần phân biệt 2 loại campaign:
1. **E-commerce (Bán hàng):** Focus vào Purchase, Revenue, ROAS
2. **Lead (Số điện thoại):** Focus vào Leads, Phone calls, Messages

---

## 🔍 CÁCH PHÁT HIỆN

### **1. Theo Campaign Objective:**

**Facebook Campaign Objectives:**
- **E-commerce:**
  - `CONVERSIONS` - Conversions
  - `CATALOG_SALES` - Catalog sales
  - `PURCHASE` - Purchase
  - `STORE_TRAFFIC` - Store traffic
  
- **Lead:**
  - `LEAD_GENERATION` - Lead generation
  - `MESSAGES` - Messages
  - `PHONE_CALLS` - Phone calls
  - `ENGAGEMENT` - Engagement (comments, messages)

### **2. Theo Metrics:**

**E-commerce Metrics:**
- `purchases`
- `purchase_value`
- `revenue`
- `roas`

**Lead Metrics:**
- `leads`
- `phone_calls`
- `messaging_conversations_started`
- `post_comments`
- `post_reactions`

### **3. Theo Account/Prefix Configuration:**

**Manual Configuration:**
- Thêm cột "Campaign Type" vào LogicRules
- Format: `act_xxx|PREFIX|ECOMMERCE` hoặc `act_xxx|PREFIX|LEAD`

---

## 🚀 IMPLEMENTATION

### **1. Auto-detect từ Campaign:**

```python
# app/services/campaign_detector.py
def detect_campaign_type_from_objective(objective: str) -> str:
    """Detect campaign type from Facebook objective"""
    objective_upper = objective.upper()
    
    ecommerce_objectives = [
        'CONVERSIONS', 'CATALOG_SALES', 'PURCHASE', 
        'STORE_TRAFFIC', 'PRODUCT_CATALOG_SALES'
    ]
    
    lead_objectives = [
        'LEAD_GENERATION', 'MESSAGES', 'PHONE_CALLS',
        'ENGAGEMENT', 'POST_ENGAGEMENT'
    ]
    
    if objective_upper in ecommerce_objectives:
        return 'ECOMMERCE'
    elif objective_upper in lead_objectives:
        return 'LEAD'
    
    return 'UNKNOWN'
```

### **2. Auto-detect từ Metrics:**

```python
def detect_campaign_type_from_metrics(metrics: dict) -> str:
    """Detect campaign type from metrics"""
    purchases = metrics.get('purchases', 0) or 0
    purchase_value = metrics.get('purchase_value', 0) or 0
    leads = metrics.get('leads', 0) or 0
    phone_calls = metrics.get('phone_calls', 0) or 0
    messages = metrics.get('messaging_conversations_started', 0) or 0
    
    # Nếu có purchase hoặc purchase_value → E-commerce
    if purchases > 0 or purchase_value > 0:
        return 'ECOMMERCE'
    
    # Nếu có leads, phone calls, hoặc messages → Lead
    if leads > 0 or phone_calls > 0 or messages > 0:
        return 'LEAD'
    
    return 'UNKNOWN'
```

### **3. Lưu vào Database:**

```python
# Update AdMetrics model
class AdMetrics(Base):
    # ... existing fields ...
    campaign_type = Column(String)  # 'ECOMMERCE', 'LEAD', 'UNKNOWN'
    campaign_objective = Column(String)  # Lưu objective từ Facebook
```

---

## 🎯 ÁP DỤNG RULES THEO TYPE

### **E-commerce Rules:**
- Focus vào: ROAS, Purchase value, Cost per purchase
- Tắt khi: ROAS < 2.0, Cost per purchase > threshold
- Bật lại khi: ROAS >= 2.0, có purchase

### **Lead Rules:**
- Focus vào: Leads, Cost per lead, Phone calls
- Tắt khi: Cost per lead > threshold, không có lead
- Bật lại khi: Cost per lead < threshold, có lead

---

## 📋 CONFIGURATION

### **Option 1: Auto-detect (Recommended)**
- Tự động detect từ campaign objective
- Tự động detect từ metrics
- Lưu vào database

### **Option 2: Manual Configuration**
- Thêm cột vào LogicRules sheet
- Format: `act_xxx|PREFIX|ECOMMERCE`
- Hoặc trong database: `automation_status.campaign_type`

### **Option 3: Hybrid**
- Auto-detect làm mặc định
- Manual override nếu cần

---

**Bạn muốn tôi implement phần này không? 🚀**

