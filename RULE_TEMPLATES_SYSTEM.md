# 🎨 RULE TEMPLATES SYSTEM - HƯỚNG DẪN

## 🎯 MỤC TIÊU

Tạo hệ thống rule templates tương tự Madgicx, cho phép:
- ✅ Chọn template sẵn (nhanh, dễ)
- ✅ Customize nếu cần
- ✅ Phân chia theo Campaign Type (E-commerce vs Lead)
- ✅ Apply cho nhiều account/prefix cùng lúc

---

## 📋 TEMPLATES CÓ SẴN

### **ECOMMERCE TEMPLATES:**

#### **Template 1: High Spend, Low ROAS**
```json
{
    "name": "E-commerce: Tắt khi chi tiêu cao, ROAS thấp",
    "campaign_type": "ECOMMERCE",
    "description": "Tắt adset khi chi tiêu > 20,000 và ROAS < 2.0",
    "conditions": {
        "spend": { "operator": ">", "value": 20000 },
        "roas": { "operator": "<", "value": 2.0 },
        "purchases": { "operator": ">=", "value": 0 }
    },
    "action": "PAUSE",
    "logic_type": "logic1"
}
```

#### **Template 2: High Spend, No Purchase**
```json
{
    "name": "E-commerce: Tắt khi chi tiêu cao, không có purchase",
    "campaign_type": "ECOMMERCE",
    "description": "Tắt adset khi chi tiêu > 15,000 và purchases = 0",
    "conditions": {
        "spend": { "operator": ">", "value": 15000 },
        "purchases": { "operator": "==", "value": 0 }
    },
    "action": "PAUSE",
    "logic_type": "logic1"
}
```

#### **Template 3: Resume khi có Purchase**
```json
{
    "name": "E-commerce: Bật lại khi có purchase",
    "campaign_type": "ECOMMERCE",
    "description": "Bật lại adset khi có purchase và ROAS >= 2.0",
    "conditions": {
        "purchases": { "operator": ">", "value": 0 },
        "roas": { "operator": ">=", "value": 2.0 }
    },
    "action": "RESUME",
    "logic_type": "logic3"
}
```

---

### **LEAD TEMPLATES:**

#### **Template 4: High Spend, No Leads**
```json
{
    "name": "Lead: Tắt khi chi tiêu cao, không có lead",
    "campaign_type": "LEAD",
    "description": "Tắt adset khi chi tiêu > 15,000 và leads = 0",
    "conditions": {
        "spend": { "operator": ">", "value": 15000 },
        "leads": { "operator": "==", "value": 0 }
    },
    "action": "PAUSE",
    "logic_type": "logic1"
}
```

#### **Template 5: High Spend, High Cost per Lead**
```json
{
    "name": "Lead: Tắt khi chi tiêu cao, giá lead cao",
    "campaign_type": "LEAD",
    "description": "Tắt adset khi chi tiêu > 20,000 và cost per lead > 15,000",
    "conditions": {
        "spend": { "operator": ">", "value": 20000 },
        "cost_per_lead": { "operator": ">", "value": 15000 }
    },
    "action": "PAUSE",
    "logic_type": "logic2"
}
```

#### **Template 6: Resume khi có Lead**
```json
{
    "name": "Lead: Bật lại khi có lead",
    "campaign_type": "LEAD",
    "description": "Bật lại adset khi có lead và cost per lead < 10,000",
    "conditions": {
        "leads": { "operator": ">", "value": 0 },
        "cost_per_lead": { "operator": "<", "value": 10000 }
    },
    "action": "RESUME",
    "logic_type": "logic3"
}
```

---

## 🚀 IMPLEMENTATION

### **1. Database Schema:**

```python
# app/models/rule_template.py
class RuleTemplate(Base):
    __tablename__ = "rule_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    campaign_type = Column(String)  # 'ECOMMERCE', 'LEAD', 'BOTH'
    template_config = Column(JSON)  # JSON config
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

### **2. API Endpoints:**

```python
# app/api/routes/templates.py
@router.get("/templates")
async def get_templates(campaign_type: Optional[str] = None):
    """Get all rule templates"""
    
@router.post("/templates/{template_id}/apply")
async def apply_template(template_id: int, account_id: str, prefix: str):
    """Apply template to account/prefix"""
    
@router.post("/templates")
async def create_template(template: RuleTemplateCreate):
    """Create new template"""
```

### **3. Dashboard UI:**

- Dropdown chọn template
- Preview conditions
- Select account/prefix
- Apply template
- Customize nếu cần

---

## 📝 USAGE

### **1. Chọn Template:**
- Vào Dashboard → Templates
- Chọn template phù hợp (E-commerce hoặc Lead)
- Preview conditions

### **2. Apply Template:**
- Chọn account/prefix
- Click "Apply Template"
- Template sẽ được tạo thành logic rule

### **3. Customize:**
- Edit template sau khi apply
- Hoặc tạo template mới từ template cũ

---

**Bạn muốn tôi implement hệ thống này không? 🚀**

