# 🎯 PROJECT SCOPE - PHẠM VI DỰ ÁN

## ✅ MỤC TIÊU CHÍNH

### **1. AUTOMATION ADS (Tự động hóa quảng cáo)**

Hệ thống tự động tắt/bật quảng cáo Facebook dựa trên các logic rules:

#### **Logic Rules:**
- **Logic 1:** Tắt adset nếu:
  - Chi tiêu > ngưỡng (ví dụ: 15,000 VND)
  - Kết quả = 0
  
- **Logic 2:** Tắt adset nếu:
  - Chi tiêu > ngưỡng (ví dụ: 20,000 VND)
  - Giá DATA > ngưỡng (ví dụ: 15,000 VND)
  
- **Logic 3:** Bật lại adset nếu:
  - Đã tắt trước đó
  - Đáp ứng điều kiện bật lại (ví dụ: chi tiêu < ngưỡng, có kết quả...)

#### **Tính năng:**
- ✅ Tự động lấy dữ liệu từ Facebook API
- ✅ Kiểm tra logic rules từ Google Sheets (LogicRules)
- ✅ Tự động tắt/bật adsets theo logic
- ✅ Gửi thông báo qua Telegram khi có hành động
- ✅ Hỗ trợ nhiều account và prefix
- ✅ Time window (chỉ chạy trong giờ cho phép: 6h-23h)
- ✅ Enable/Disable từng account|prefix
- ✅ Cooldown period (tránh toggle quá nhiều)

---

### **2. BÁO CÁO (Reports)**

Gửi báo cáo tự động qua Telegram Bot:

#### **Báo cáo cuối ngày:**
- Tổng chi tiêu
- Tổng tương tác
- Tổng kết quả (Results)
- Giá DATA trung bình
- SĐT (checkout)
- Giá SĐT
- Tỷ lệ SĐT/Tương tác

#### **Báo cáo theo account:**
- Chi tiết từng account
- Chi tiết từng prefix
- So sánh performance

#### **Commands Telegram:**
- `/report` - Báo cáo cuối ngày
- `/statusads` - Trạng thái adsets
- `/status` - Trạng thái automation
- `/enable <account_id> <prefix>` - Bật automation
- `/disable <account_id> <prefix>` - Tắt automation
- `/enable_all` - Bật tất cả
- `/disable_all` - Tắt tất cả

---

## ❌ KHÔNG BAO GỒM (Sẽ update sau nếu có khả năng)

### **Dashboard/Website:**
- ❌ Web interface
- ❌ Dashboard visualization
- ❌ Real-time charts
- ❌ User management
- ❌ Login/Authentication

### **Advanced Features:**
- ❌ A/B testing
- ❌ Campaign optimization
- ❌ Budget allocation
- ❌ Multi-user collaboration
- ❌ API for third-party integration

---

## 🚀 MIGRATION TỪ GOOGLE APPS SCRIPT

### **Files cần migrate:**

#### **1. Automation Logic:**
- `Code.gs` → `app/services/automation.py`
  - `runAutomation()` → `run_automation()`
  - `kiemTraVaTatQuangCao()` → `check_and_toggle_ads()`
  - `testRunAutomation()` → `test_run_automation()`

#### **2. Facebook API:**
- `Facebook API.gs` → `app/services/facebook_api.py`
  - `pullFacebookData()` → `pull_facebook_data()`
  - `goiFacebookAPIDeTatNhieuAdset()` → `pause_adsets()`
  - `goiFacebookAPIDeBatNhieuAdset()` → `resume_adsets()`
  - `getDailyBreakdownData()` → `get_daily_breakdown_data()`

#### **3. Logic Rules:**
- `Logics.gs` → `app/services/logics.py`
  - `buildLogicMap()` → `build_logic_map()`
  - `taoLogicRulesMau()` → `create_logic_rules_template()`
  - Các hàm logic check → `check_logic_1()`, `check_logic_2()`, etc.

#### **4. Telegram Bot:**
- `Telegram.gs` → `app/services/telegram_bot.py`
  - `guiThongBaoTelegram()` → `send_telegram_message()`
  - `handleTelegramMessage()` → `handle_telegram_message()`
  - Các command handlers → `handle_report_command()`, `handle_status_command()`, etc.

#### **5. Reporting:**
- `Code.gs` (tongKetCuoiNgay) → `app/services/reporting.py`
  - `tongKetCuoiNgay()` → `generate_daily_report()`
  - `generateSummaryReport()` → `generate_summary_report()`

#### **6. Database:**
- Google Sheets → PostgreSQL
  - `Data_FB` sheet → `ads_metrics` table
  - `LogicRules` sheet → `logic_rules` table
  - `CaiDat` sheet → `settings` table

---

## 📋 PROJECT STRUCTURE

```
facebook-ads-automation/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── config.py           # Configuration
│   │   ├── database.py         # Database connection
│   │   └── security.py         # Security utilities
│   ├── services/
│   │   ├── automation.py       # Automation logic
│   │   ├── facebook_api.py     # Facebook API integration
│   │   ├── telegram_bot.py     # Telegram Bot
│   │   ├── logics.py           # Logic rules
│   │   └── reporting.py        # Reporting functions
│   ├── models/
│   │   ├── ad_metrics.py       # Ad metrics model
│   │   ├── logic_rule.py       # Logic rule model
│   │   └── setting.py          # Setting model
│   ├── schemas/
│   │   ├── ad_metrics.py       # Ad metrics schema
│   │   ├── logic_rule.py       # Logic rule schema
│   │   └── report.py           # Report schema
│   └── api/
│       ├── routes/
│       │   ├── automation.py   # Automation endpoints
│       │   ├── reports.py      # Report endpoints
│       │   └── webhook.py      # Telegram webhook
│       └── dependencies.py     # API dependencies
├── alembic/                    # Database migrations
├── tests/                      # Tests
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore
├── README.md                  # Documentation
└── deploy.sh                  # Deployment script
```

---

## 🎯 PRIORITIES

### **Phase 1: Core Automation (Ưu tiên cao)**
1. ✅ Migrate Facebook API integration
2. ✅ Migrate Automation logic
3. ✅ Migrate Logic rules
4. ✅ Setup PostgreSQL database
5. ✅ Deploy on VPS

### **Phase 2: Telegram Bot (Ưu tiên cao)**
1. ✅ Migrate Telegram Bot
2. ✅ Migrate Commands
3. ✅ Migrate Notifications
4. ✅ Setup Webhook

### **Phase 3: Reporting (Ưu tiên trung bình)**
1. ✅ Migrate Daily Report
2. ✅ Migrate Summary Report
3. ✅ Optimize Report Generation

### **Phase 4: Future (Sẽ update sau)**
1. ⏸️ Dashboard/Website (nếu có khả năng)
2. ⏸️ Advanced features (nếu có khả năng)
3. ⏸️ Multi-user support (nếu có khả năng)

---

## 📝 NOTES

- **Focus:** Automation và Reporting qua Telegram
- **Simple:** Không cần web interface phức tạp
- **Scalable:** Có thể mở rộng sau nếu cần
- **Maintainable:** Code rõ ràng, dễ maintain

---

**Chúc bạn migration thành công! 🚀**

