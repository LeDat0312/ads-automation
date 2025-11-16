# 🐍 CẤU TRÚC DỰ ÁN PYTHON

## 📁 Cấu trúc thư mục

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   │
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py          # Settings management (thay thế layCaiDatHeThong)
│   │   ├── database.py        # Database models & connection
│   │   └── security.py        # Authentication (nếu cần)
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── ad_metrics.py     # AdMetrics model
│   │   ├── logic_rule.py     # LogicRule model (LINH HOẠT)
│   │   ├── system_setting.py # SystemSetting model
│   │   └── automation_status.py
│   │
│   ├── schemas/                # Pydantic schemas (validation)
│   │   ├── __init__.py
│   │   ├── logic_rule.py      # LogicRule schemas
│   │   ├── ad_metrics.py
│   │   └── automation.py
│   │
│   ├── services/               # Business logic (thay thế .gs files)
│   │   ├── __init__.py
│   │   ├── automation.py      # Code.gs → runAutomation()
│   │   ├── facebook_api.py    # Facebook API.gs
│   │   ├── logics.py          # Logics.gs → buildLogicMap(), checkLogic()
│   │   ├── telegram_bot.py    # Telegram.gs → guiThongBaoTelegram()
│   │   ├── rule_manager.py    # Quản lý rules (NEW - linh hoạt)
│   │   └── reporting.py       # Báo cáo
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── automation.py  # /api/automation/run
│   │   │   ├── rules.py       # /api/rules/* (CRUD rules)
│   │   │   ├── accounts.py    # /api/accounts/*
│   │   │   └── metrics.py     # /api/metrics/*
│   │   └── dependencies.py   # Shared dependencies
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
│
├── migrations/                  # Alembic migrations
│   └── versions/
│
├── scripts/                    # Utility scripts
│   ├── migrate_from_sheets.py # Migrate từ Google Sheets
│   └── init_db.py             # Initialize database
│
├── tests/                      # Tests
│   ├── __init__.py
│   ├── test_automation.py
│   ├── test_logics.py
│   └── test_api.py
│
├── config/                     # Configuration files
│   ├── default_rules.json     # Default rule templates
│   └── rule_schemas.json      # Rule validation schemas
│
├── .env                        # Environment variables
├── .env.example
├── requirements.txt
├── alembic.ini
├── README.md
└── docker-compose.yml          # (Optional) Docker setup
```

---

## 🔄 Mapping từ Google Apps Script → Python

| Google Apps Script | Python | Mô tả |
|-------------------|--------|-------|
| `Code.gs` | `app/services/automation.py` | Hàm runAutomation() |
| `Facebook API.gs` | `app/services/facebook_api.py` | Pull data, pause/resume adsets |
| `Logics.gs` | `app/services/logics.py` | buildLogicMap(), checkLogic() |
| `Telegram.gs` | `app/services/telegram_bot.py` | Gửi thông báo |
| `CaiDat` sheet | `app/core/config.py` + `SystemSetting` model | Settings management |
| `LogicRules` sheet | `LogicRule` model (JSON fields) | Rules linh hoạt |
| `Data_FB` sheet | `AdMetrics` model | Ad metrics data |

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env với các giá trị của bạn
DATABASE_URL=postgresql://user:password@localhost:5432/ads_automation
ACCESS_TOKEN=your_facebook_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
AD_ACCOUNT_IDS=act_123456789,act_987654321
```

### 3. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Hoặc init database manually
python scripts/init_db.py
```

### 4. Run Application

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📝 API Endpoints

### Automation
- `POST /api/automation/run` - Chạy automation
- `GET /api/automation/status` - Trạng thái automation

### Rules Management
- `GET /api/rules` - List tất cả rules
- `GET /api/rules/{rule_id}` - Chi tiết rule
- `POST /api/rules` - Tạo rule mới
- `PUT /api/rules/{rule_id}` - Cập nhật rule
- `DELETE /api/rules/{rule_id}` - Xóa rule
- `POST /api/rules/{rule_id}/toggle` - Bật/tắt rule

### Accounts
- `GET /api/accounts` - List accounts
- `POST /api/accounts` - Thêm account

### Metrics
- `GET /api/metrics` - Lấy metrics với filters
- `POST /api/metrics/pull` - Pull data từ Facebook

---

## 🔧 Development Workflow

1. **Thêm model mới:**
   - Tạo model trong `app/models/`
   - Tạo schema trong `app/schemas/`
   - Tạo migration: `alembic revision --autogenerate -m "add new model"`
   - Apply migration: `alembic upgrade head`

2. **Thêm service mới:**
   - Tạo file trong `app/services/`
   - Import và sử dụng trong `app/api/routes/`

3. **Test:**
   - Chạy tests: `pytest`
   - Test API: `curl http://localhost:8000/api/automation/run`

---

## 📦 Dependencies chính

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **PostgreSQL**: Database
- **Pydantic**: Data validation
- **Alembic**: Database migrations
- **httpx/requests**: HTTP client
- **python-telegram-bot**: Telegram integration

---

**Cấu trúc này cho phép:**
- ✅ Dễ mở rộng
- ✅ Tách biệt concerns (models, services, API)
- ✅ Dễ test
- ✅ Dễ maintain
- ✅ Tương thích với Google Apps Script logic

