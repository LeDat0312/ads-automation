# 🚀 QUICK START - PYTHON PROJECT

## 📋 TÓM TẮT

Dự án Python thay thế Google Apps Script với:
- ✅ **FastAPI** - Web framework
- ✅ **PostgreSQL** - Database (thay thế Google Sheets)
- ✅ **SQLAlchemy** - ORM
- ✅ **LogicRules linh hoạt** - JSON fields thay vì sheet cứng nhắc

---

## 🎯 CẤU TRÚC DỰ ÁN

```
app/
├── core/              # Config, Database
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── services/          # Business logic
├── api/routes/        # API endpoints
└── main.py           # Entry point
```

---

## ⚡ QUICK START

### **1. Setup Environment**

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Configure .env**

```bash
# Copy .env.example
cp .env.example .env

# Edit .env
DATABASE_URL=postgresql://user:password@localhost:5432/ads_automation
ACCESS_TOKEN=your_facebook_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
AD_ACCOUNT_IDS=act_123456789,act_987654321
```

### **3. Initialize Database**

```bash
# Tạo database
createdb ads_automation

# Run migrations (hoặc init manually)
python scripts/init_db.py
```

### **4. Run Application**

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📝 API ENDPOINTS

### **Rules Management**

```bash
# List rules
GET /api/rules?folder=Scale%20Ad%20Sets&enabled=true

# Create rule
POST /api/rules
{
  "name": "Increase budget",
  "folder": "Scale Ad Sets",
  "account_ids": ["act_123"],
  "conditions": {
    "AND": [
      {"metric": "spend", "timeframe": "today", "operator": ">", "value": 300}
    ]
  },
  "action": "INCREASE_BUDGET",
  "action_params": {"percent": 20}
}

# Update rule
PUT /api/rules/1
{
  "enabled": false
}

# Toggle rule
POST /api/rules/1/toggle

# Delete rule
DELETE /api/rules/1
```

### **Automation**

```bash
# Run automation
POST /api/automation/run

# Test automation (bỏ qua khung giờ)
POST /api/automation/test
```

---

## 🎨 LOGICRULES LINH HOẠT

### **Cấu trúc Rule:**

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
  "status": "LIVE"
}
```

### **Ưu điểm:**

- ✅ **Linh hoạt:** Conditions là JSON, dễ thêm/sửa
- ✅ **Nhanh:** Query database nhanh hơn sheet
- ✅ **API:** Dễ tạo UI để quản lý
- ✅ **Versioning:** Có version và updated_at
- ✅ **Validation:** Pydantic đảm bảo data đúng format

---

## 🔧 DEVELOPMENT

### **Thêm Model mới:**

```python
# app/models/new_model.py
from app.core.database import Base
from sqlalchemy import Column, Integer, String

class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

### **Thêm API Route:**

```python
# app/api/routes/new_route.py
from fastapi import APIRouter
router = APIRouter(prefix="/api/new", tags=["new"])

@router.get("/")
def list_items():
    return {"items": []}
```

### **Update main.py:**

```python
from app.api.routes import new_route
app.include_router(new_route.router)
```

---

## 📚 DOCUMENTATION

- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc

---

## ✅ NEXT STEPS

1. ✅ Setup database
2. ✅ Test API endpoints
3. ✅ Migrate data từ Google Sheets
4. ✅ Tạo UI để quản lý rules (sau này)

---

**Đã sẵn sàng để chạy! 🚀**

