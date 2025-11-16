# 🔧 FIX AD_ACCOUNT_IDS ENV VARIABLE

## ❌ VẤN ĐỀ

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
AD_ACCOUNT_IDS
  Input should be a valid string [type=string_type, input_value=['act_723686686812438', 'act_2827767517395636'], input_type=list]
```

**Nguyên nhân:** Có environment variable đang override hoặc Pydantic đang parse sai.

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Check environment variables**

```bash
# Check có env var đang set không
env | grep AD_ACCOUNT_IDS

# Nếu có, unset nó
unset AD_ACCOUNT_IDS
```

### **BƯỚC 2: Check file `.env`**

```bash
cd ~/ads-automation
cat .env | grep "AD_ACCOUNT_IDS"
```

**Phải thấy:**
```
AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636
```

**KHÔNG phải:**
```
AD_ACCOUNT_IDS=['act_723686686812438', 'act_2827767517395636']
```

### **BƯỚC 3: Check Supervisor config có set env vars không**

```bash
sudo cat /etc/supervisor/conf.d/ads-automation.conf | grep -A 5 "ads-automation-api"
```

**Nếu thấy `environment=AD_ACCOUNT_IDS=...`, cần xóa hoặc sửa!**

### **BƯỚC 4: Restart API với unset env vars**

```bash
# Stop API
sudo supervisorctl stop ads-automation-api

# Unset env vars trong shell hiện tại
unset AD_ACCOUNT_IDS 2>/dev/null || true

# Restart API
sudo supervisorctl start ads-automation-api

# Check status
sudo supervisorctl status
```

### **BƯỚC 5: Hoặc sửa Supervisor config để không set env vars**

```bash
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

**Đảm bảo không có dòng:**
```ini
environment=AD_ACCOUNT_IDS=...
```

**Chỉ nên có:**
```ini
environment=PATH="/home/adsuser/ads-automation/venv/bin"
```

**Sau đó:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ads-automation-api
```

---

## 🧪 TEST

```bash
# Test load settings
cd ~/ads-automation
source venv/bin/activate

# Unset env vars
unset AD_ACCOUNT_IDS 2>/dev/null || true

# Test
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'✅ AD_ACCOUNT_IDS: {settings.AD_ACCOUNT_IDS}')
print(f'✅ Type: {type(settings.AD_ACCOUNT_IDS)}')
"
```

**Kết quả mong đợi:**
```
✅ AD_ACCOUNT_IDS: act_723686686812438,act_2827767517395636
✅ Type: <class 'str'>
```

---

## ✅ VERIFY

```bash
# Check API status
sudo supervisorctl status

# Test API
curl http://localhost:8000/health

# Test Telegram webhook (gửi /start trong Telegram)
# Check logs
sudo tail -f /var/log/ads-automation/api.out.log
```

**Phải thấy `200 OK` thay vì `500 Internal Server Error`!**

---

**Bây giờ hãy check environment variables và Supervisor config! 🚀**


