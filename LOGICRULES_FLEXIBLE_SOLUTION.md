# 🎯 GIẢI PHÁP LOGICRULES LINH HOẠT

## 🎨 VẤN ĐỀ HIỆN TẠI

LogicRules sheet hiện tại:
- ❌ Cứng nhắc: Mỗi rule cần nhiều cột (account_id|prefix)
- ❌ Khó mở rộng: Thêm condition mới = thêm cột mới
- ❌ Khó quản lý: Phải edit trực tiếp trong sheet
- ❌ Không có versioning: Không biết rule nào đã thay đổi khi nào

---

## ✅ GIẢI PHÁP ĐỀ XUẤT

### **OPTION 1: Database với JSON Fields (KHUYẾN NGHỊ) ⭐**

**Ưu điểm:**
- ✅ Linh hoạt: Conditions là JSON, dễ thêm/sửa
- ✅ Nhanh: Query database nhanh hơn sheet
- ✅ Versioning: Có thể thêm `version` và `updated_at`
- ✅ Validation: Pydantic schemas đảm bảo data đúng format
- ✅ API: Dễ tạo REST API để quản lý

**Cấu trúc:**

```python
# app/models/logic_rule.py
class LogicRule(Base):
    __tablename__ = "logic_rules"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)  # "Increase budget", "Decrease budget"
    folder = Column(String)  # "Scale Ad Sets", "General"
    
    # Account & Prefix (có thể nhiều)
    account_ids = Column(JSON)  # ["act_123", "act_456"]
    prefixes = Column(JSON)     # ["FL", "PX", null]  # null = all prefixes
    
    # Conditions (LINH HOẠT - JSON)
    conditions = Column(JSON)  # {
    #   "AND": [
    #     {"metric": "spend", "timeframe": "today", "operator": ">", "value": 300},
    #     {"metric": "cpl", "timeframe": "today", "operator": "<", "value": {"multiplier": 0.8, "base": "cpl_3days"}},
    #     {"metric": "cpl", "timeframe": "last_3days", "operator": "<", "value": {"multiplier": 0.9, "base": "cpl_7days"}},
    #     {"metric": "leads", "timeframe": "today", "operator": ">=", "value": 10}
    #   ]
    # }
    
    # Action
    action = Column(String)  # "INCREASE_BUDGET", "DECREASE_BUDGET", "PAUSE", "RESUME"
    action_params = Column(JSON)  # {"percent": 20, "frequency": "once_a_day"}
    
    # Schedule
    schedule = Column(JSON)  # {
    #   "type": "interval",  # "interval" | "specific"
    #   "interval_minutes": 60,
    #   "specific_times": ["09:00", "14:00", "18:00"],
    #   "timezone": "Asia/Ho_Chi_Minh"
    # }
    
    # Filters
    filters = Column(JSON)  # {
    #   "adset_status": ["ACTIVE"],
    #   "campaign_types": ["ECOMMERCE"],
    #   "min_spend": 1000
    # }
    
    # Status
    enabled = Column(Boolean, default=True)
    status = Column(String)  # "DRAFT", "LIVE", "PAUSED"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String)
    version = Column(Integer, default=1)
```

**Ví dụ Rule:**

```json
{
  "name": "Increase ad sets budget",
  "folder": "Scale Ad Sets",
  "account_ids": ["act_2827767517395636"],
  "prefixes": ["FL"],
  "conditions": {
    "AND": [
      {
        "metric": "spend",
        "timeframe": "today",
        "operator": ">",
        "value": 300
      },
      {
        "metric": "cost_per_lead",
        "timeframe": "today",
        "operator": "<",
        "value": {
          "multiplier": 0.8,
          "base_metric": "cost_per_lead",
          "base_timeframe": "last_3days"
        }
      },
      {
        "metric": "cost_per_lead",
        "timeframe": "last_3days",
        "operator": "<",
        "value": {
          "multiplier": 0.9,
          "base_metric": "cost_per_lead",
          "base_timeframe": "last_7days"
        }
      },
      {
        "metric": "leads",
        "timeframe": "today",
        "operator": ">=",
        "value": 10
      }
    ]
  },
  "action": "INCREASE_BUDGET",
  "action_params": {
    "percent": 20,
    "frequency": "once_a_day"
  },
  "schedule": {
    "type": "interval",
    "interval_minutes": 60,
    "timezone": "Asia/Ho_Chi_Minh"
  },
  "filters": {
    "adset_status": ["ACTIVE"],
    "campaign_types": ["LEAD"]
  },
  "enabled": true,
  "status": "DRAFT"
}
```

---

### **OPTION 2: YAML Config Files**

**Ưu điểm:**
- ✅ Dễ đọc: YAML dễ đọc hơn JSON
- ✅ Version control: Git tracking dễ dàng
- ✅ Không cần database: File-based

**Nhược điểm:**
- ❌ Khó query: Phải load tất cả files
- ❌ Không có API: Phải edit file trực tiếp

**Cấu trúc:**

```yaml
# config/rules/scale_ad_sets/increase_budget.yaml
name: "Increase ad sets budget"
folder: "Scale Ad Sets"
account_ids:
  - "act_2827767517395636"
prefixes:
  - "FL"
  - null  # All prefixes

conditions:
  AND:
    - metric: "spend"
      timeframe: "today"
      operator: ">"
      value: 300
    - metric: "cost_per_lead"
      timeframe: "today"
      operator: "<"
      value:
        multiplier: 0.8
        base_metric: "cost_per_lead"
        base_timeframe: "last_3days"

action: "INCREASE_BUDGET"
action_params:
  percent: 20
  frequency: "once_a_day"

schedule:
  type: "interval"
  interval_minutes: 60
  timezone: "Asia/Ho_Chi_Minh"

filters:
  adset_status: ["ACTIVE"]
  campaign_types: ["LEAD"]

enabled: true
status: "DRAFT"
```

---

### **OPTION 3: Hybrid (Database + JSON Config) ⭐⭐**

**Kết hợp tốt nhất:**
- Database lưu rules đang active
- JSON/YAML files lưu templates và backups
- API để quản lý rules
- Import/Export từ files

---

## 🚀 IMPLEMENTATION - OPTION 1 (Database + JSON)

### **1. Model mới:**

```python
# app/models/logic_rule.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from app.core.database import Base

class LogicRule(Base):
    __tablename__ = "logic_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    folder = Column(String, default="General")
    
    # Account & Prefix (JSON arrays)
    account_ids = Column(JSON, default=list)  # ["act_123", "act_456"]
    prefixes = Column(JSON, default=list)     # ["FL", "PX"] hoặc [null] = all
    
    # Conditions (LINH HOẠT)
    conditions = Column(JSON, nullable=False)
    
    # Action
    action = Column(String, nullable=False)  # INCREASE_BUDGET, DECREASE_BUDGET, PAUSE, RESUME
    action_params = Column(JSON, default=dict)
    
    # Schedule
    schedule = Column(JSON, default=dict)
    
    # Filters
    filters = Column(JSON, default=dict)
    
    # Status
    enabled = Column(Boolean, default=True)
    status = Column(String, default="DRAFT")  # DRAFT, LIVE, PAUSED
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String)
    version = Column(Integer, default=1)
    
    # Description (optional)
    description = Column(Text)
```

### **2. Schema validation:**

```python
# app/schemas/logic_rule.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class Condition(BaseModel):
    metric: str
    timeframe: str  # "today", "last_3days", "last_7days"
    operator: str   # ">", "<", ">=", "<=", "==", "!="
    value: Union[float, int, Dict[str, Any]]  # Số hoặc {multiplier, base_metric, base_timeframe}

class ConditionsGroup(BaseModel):
    AND: Optional[List[Condition]] = None
    OR: Optional[List[Condition]] = None

class LogicRuleCreate(BaseModel):
    name: str
    folder: Optional[str] = "General"
    account_ids: List[str] = []
    prefixes: Optional[List[Optional[str]]] = []  # [null] = all prefixes
    conditions: ConditionsGroup
    action: str
    action_params: Dict[str, Any] = {}
    schedule: Dict[str, Any] = {}
    filters: Dict[str, Any] = {}
    enabled: bool = True
    status: str = "DRAFT"
    description: Optional[str] = None

class LogicRuleUpdate(BaseModel):
    name: Optional[str] = None
    folder: Optional[str] = None
    account_ids: Optional[List[str]] = None
    prefixes: Optional[List[Optional[str]]] = None
    conditions: Optional[ConditionsGroup] = None
    action: Optional[str] = None
    action_params: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    status: Optional[str] = None
    description: Optional[str] = None

class LogicRuleResponse(BaseModel):
    id: int
    name: str
    folder: str
    account_ids: List[str]
    prefixes: List[Optional[str]]
    conditions: Dict[str, Any]
    action: str
    action_params: Dict[str, Any]
    schedule: Dict[str, Any]
    filters: Dict[str, Any]
    enabled: bool
    status: str
    created_at: datetime
    updated_at: datetime
    version: int
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
```

### **3. Service để quản lý rules:**

```python
# app/services/rule_manager.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.logic_rule import LogicRule
from app.schemas.logic_rule import LogicRuleCreate, LogicRuleUpdate

class RuleManager:
    def __init__(self, db: Session):
        self.db = db
    
    def create_rule(self, rule_data: LogicRuleCreate) -> LogicRule:
        """Tạo rule mới"""
        rule = LogicRule(**rule_data.dict())
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def get_rule(self, rule_id: int) -> Optional[LogicRule]:
        """Lấy rule theo ID"""
        return self.db.query(LogicRule).filter(LogicRule.id == rule_id).first()
    
    def list_rules(
        self,
        folder: Optional[str] = None,
        account_id: Optional[str] = None,
        enabled: Optional[bool] = None,
        status: Optional[str] = None
    ) -> List[LogicRule]:
        """List rules với filters"""
        query = self.db.query(LogicRule)
        
        if folder:
            query = query.filter(LogicRule.folder == folder)
        if account_id:
            query = query.filter(LogicRule.account_ids.contains([account_id]))
        if enabled is not None:
            query = query.filter(LogicRule.enabled == enabled)
        if status:
            query = query.filter(LogicRule.status == status)
        
        return query.all()
    
    def update_rule(self, rule_id: int, rule_data: LogicRuleUpdate) -> Optional[LogicRule]:
        """Cập nhật rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        update_data = rule_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rule, key, value)
        
        rule.version += 1
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def delete_rule(self, rule_id: int) -> bool:
        """Xóa rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return False
        
        self.db.delete(rule)
        self.db.commit()
        return True
    
    def toggle_rule(self, rule_id: int) -> Optional[LogicRule]:
        """Bật/tắt rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        rule.enabled = not rule.enabled
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def get_rules_for_account_prefix(
        self,
        account_id: str,
        prefix: Optional[str] = None
    ) -> List[LogicRule]:
        """Lấy rules áp dụng cho account_id và prefix"""
        query = self.db.query(LogicRule).filter(
            LogicRule.enabled == True,
            LogicRule.status == "LIVE"
        )
        
        # Filter by account_id
        query = query.filter(
            LogicRule.account_ids.contains([account_id]) |
            LogicRule.account_ids == []  # All accounts
        )
        
        # Filter by prefix
        if prefix:
            query = query.filter(
                LogicRule.prefixes.contains([prefix]) |
                LogicRule.prefixes.contains([None])  # All prefixes
            )
        
        return query.all()
```

### **4. API Endpoints:**

```python
# app/api/routes/rules.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.logic_rule import LogicRuleCreate, LogicRuleUpdate, LogicRuleResponse
from app.services.rule_manager import RuleManager

router = APIRouter(prefix="/api/rules", tags=["rules"])

@router.get("/", response_model=List[LogicRuleResponse])
def list_rules(
    folder: Optional[str] = None,
    account_id: Optional[str] = None,
    enabled: Optional[bool] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List tất cả rules với filters"""
    manager = RuleManager(db)
    return manager.list_rules(folder, account_id, enabled, status)

@router.post("/", response_model=LogicRuleResponse)
def create_rule(rule_data: LogicRuleCreate, db: Session = Depends(get_db)):
    """Tạo rule mới"""
    manager = RuleManager(db)
    return manager.create_rule(rule_data)

@router.get("/{rule_id}", response_model=LogicRuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết rule"""
    manager = RuleManager(db)
    rule = manager.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/{rule_id}", response_model=LogicRuleResponse)
def update_rule(
    rule_id: int,
    rule_data: LogicRuleUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật rule"""
    manager = RuleManager(db)
    rule = manager.update_rule(rule_id, rule_data)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Xóa rule"""
    manager = RuleManager(db)
    success = manager.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted"}

@router.post("/{rule_id}/toggle", response_model=LogicRuleResponse)
def toggle_rule(rule_id: int, db: Session = Depends(get_db)):
    """Bật/tắt rule"""
    manager = RuleManager(db)
    rule = manager.toggle_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule
```

---

## 🎯 CÁCH SỬ DỤNG

### **1. Tạo rule mới qua API:**

```bash
curl -X POST http://localhost:8000/api/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Increase ad sets budget",
    "folder": "Scale Ad Sets",
    "account_ids": ["act_2827767517395636"],
    "prefixes": ["FL"],
    "conditions": {
      "AND": [
        {
          "metric": "spend",
          "timeframe": "today",
          "operator": ">",
          "value": 300
        },
        {
          "metric": "cost_per_lead",
          "timeframe": "today",
          "operator": "<",
          "value": {
            "multiplier": 0.8,
            "base_metric": "cost_per_lead",
            "base_timeframe": "last_3days"
          }
        }
      ]
    },
    "action": "INCREASE_BUDGET",
    "action_params": {
      "percent": 20,
      "frequency": "once_a_day"
    },
    "schedule": {
      "type": "interval",
      "interval_minutes": 60,
      "timezone": "Asia/Ho_Chi_Minh"
    },
    "filters": {
      "adset_status": ["ACTIVE"],
      "campaign_types": ["LEAD"]
    },
    "enabled": true,
    "status": "DRAFT"
  }'
```

### **2. List rules:**

```bash
# Tất cả rules
curl http://localhost:8000/api/rules

# Rules trong folder "Scale Ad Sets"
curl http://localhost:8000/api/rules?folder=Scale%20Ad%20Sets

# Rules cho account cụ thể
curl http://localhost:8000/api/rules?account_id=act_2827767517395636

# Chỉ rules đang enabled
curl http://localhost:8000/api/rules?enabled=true
```

### **3. Update rule:**

```bash
curl -X PUT http://localhost:8000/api/rules/1 \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "status": "PAUSED"
  }'
```

---

## ✅ ƯU ĐIỂM

1. **Linh hoạt:** Conditions là JSON, dễ thêm/sửa
2. **Nhanh:** Query database nhanh hơn sheet
3. **API:** Dễ tạo UI để quản lý
4. **Versioning:** Có version và updated_at
5. **Validation:** Pydantic đảm bảo data đúng format
6. **Scalable:** Dễ mở rộng thêm fields mới

---

**KHUYẾN NGHỊ: Dùng OPTION 1 (Database + JSON) để có tốc độ và linh hoạt tốt nhất! 🚀**

