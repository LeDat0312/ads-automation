# 🔍 DEBUG ENV LOADING

## ❌ VẤN ĐỀ

Vẫn lỗi validation mặc dù đã sửa `.env`. Có thể:
1. File `.env` chưa được update đúng
2. Environment variable đang override
3. File `.env` không được load

---

## 🔍 KIỂM TRA

### **BƯỚC 1: Check file `.env` thực tế:**

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

### **BƯỚC 2: Check environment variables:**

```bash
# Check có env var đang set không
env | grep AD_ACCOUNT_IDS

# Nếu có, unset nó
unset AD_ACCOUNT_IDS
```

### **BƯỚC 3: Check file `.env` có được load không:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test load trực tiếp từ file
python -c "
import os
from dotenv import load_dotenv
load_dotenv('.env')
print('AD_ACCOUNT_IDS from .env:', repr(os.getenv('AD_ACCOUNT_IDS')))
"
```

### **BƯỚC 4: Test với explicit env file:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test với explicit env_file
python -c "
from pydantic_settings import BaseSettings
from typing import Union, List
from pydantic import Field

class TestSettings(BaseSettings):
    AD_ACCOUNT_IDS: Union[str, List[str]] = Field(..., env='AD_ACCOUNT_IDS')
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

try:
    settings = TestSettings()
    print(f'✅ AD_ACCOUNT_IDS: {settings.AD_ACCOUNT_IDS}')
    print(f'✅ Type: {type(settings.AD_ACCOUNT_IDS)}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

---

## 🔧 FIX

### **Option 1: Recreate file `.env` hoàn toàn:**

```bash
cd ~/ads-automation

# Backup
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Xóa file cũ
rm .env

# Tạo file mới (copy-paste từ hướng dẫn)
cat > .env << 'EOF'
# ===== Database =====
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
REDIS_URL=redis://localhost:6379/0

# ===== Facebook API =====
ACCESS_TOKEN=EAAcklZAcKeSIBPyZBpHIu0ZA87Xq9l0H1EOLr4ZClU0vKrCSHMkMG4IwfCytqWLDxjVTIZBTHUzHpXBfm1qSSk7NrqKyoHju7TZAqThz9fdyoKsKZCIRFjCgJkt3lwm9Myv6J0hODnZA4nT9lxPwlXQZA822QVpXzbomf9eS3UncLcLOC3WIOJcr94WUr2BoK
AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636
DATA_DATE_PRESET=today

# ===== Telegram =====
TELEGRAM_BOT_TOKEN=8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k
TELEGRAM_CHAT_ID=-1003433325208
TELEGRAM_AUTHORIZED_CHAT_ID=-1003433325208
TELEGRAM_WEBHOOK_SECRET=bac722f5ee22f178b4c1304e1a70293547706dbed02f7159e8fba75fba30791d
WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook

# ===== Automation =====
RUN_WINDOW_START_HOUR=6
RUN_WINDOW_END_HOUR=23
DELAY_KHI_TAT_BATCH=1000
NOTIFY_NO_VIOLATION_MINUTES=30

# ===== Server =====
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=961197b8cca6e1468b412b1e98fda145d19d9cb73ef4bcf1429e8da2e26b9083

# ===== Job Queue =====
JOB_QUEUE_WORKERS=2
JOB_RATE_LIMIT_SECONDS=30
JOB_MAX_ATTEMPTS=3
EOF

# Set permissions
chmod 600 .env

# Verify
cat .env | grep "AD_ACCOUNT_IDS"
```

### **Option 2: Check và unset environment variables:**

```bash
# Check tất cả env vars liên quan
env | grep -E "AD_ACCOUNT|DATABASE|TELEGRAM|SECRET"

# Unset nếu có
unset AD_ACCOUNT_IDS
unset DATABASE_URL
# ... (unset các biến khác nếu cần)

# Test lại
cd ~/ads-automation
source venv/bin/activate
python -c "from app.core.config import get_settings; s = get_settings(); print('✅ OK')"
```

### **Option 3: Check file `config.py` có đúng không:**

```bash
cd ~/ads-automation
grep -A 3 "AD_ACCOUNT_IDS" app/core/config.py
```

**Phải thấy:**
```python
AD_ACCOUNT_IDS: Union[str, List[str]] = Field(..., env="AD_ACCOUNT_IDS")
```

---

## ✅ TEST SAU KHI FIX

```bash
cd ~/ads-automation
source venv/bin/activate

# Unset env vars trước
unset AD_ACCOUNT_IDS 2>/dev/null || true

# Test
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'✅ AD_ACCOUNT_IDS: {settings.AD_ACCOUNT_IDS}')
print(f'✅ Type: {type(settings.AD_ACCOUNT_IDS)}')
print(f'✅ ad_account_ids_list: {settings.ad_account_ids_list}')
"
```

---

**Bây giờ hãy check file `.env` và environment variables! 🚀**


