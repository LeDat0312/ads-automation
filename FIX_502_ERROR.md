# 🔧 FIX 502 BAD GATEWAY ERROR

## 🐛 NGUYÊN NHÂN

Lỗi 502 Bad Gateway thường xảy ra khi:
1. Backend service (FastAPI) crash hoặc không start được
2. Có lỗi syntax trong code Python
3. Import error (circular import, missing module)
4. Database connection error
5. Missing dependencies

## 🔍 KIỂM TRA LOGS

### Trên VPS, chạy các lệnh sau:

```bash
# 1. Check API service status
sudo supervisorctl status ads-automation-api

# 2. Check error logs
sudo tail -100 /var/log/ads-automation/api.err.log

# 3. Check output logs
sudo tail -100 /var/log/ads-automation/api.out.log

# 4. Test import Python
cd ~/ads-automation
source venv/bin/activate
python -c "from app.main import app; print('✅ Import OK')"
```

## 🔧 CÁC BƯỚC SỬA

### BƯỚC 1: Pull code mới nhất
```bash
cd ~/ads-automation
source venv/bin/activate
git pull origin main
```

### BƯỚC 2: Kiểm tra import
```bash
python -c "
from app.main import app
from app.models.user_settings import UserSettings
from app.models.account_prefix import Account, Prefix, AccountPrefix
from app.services.facebook_token_service import test_facebook_token
from app.api.routes.settings import router
print('✅ All imports OK')
"
```

### BƯỚC 3: Kiểm tra database
```bash
python -c "
from app.core.database import init_db
init_db()
print('✅ Database OK')
"
```

### BƯỚC 4: Install missing dependencies
```bash
pip install cryptography
pip install -r requirements.txt
```

### BƯỚC 5: Restart service
```bash
sudo supervisorctl restart ads-automation-api
sudo supervisorctl status ads-automation-api
```

## ⚠️ CÁC LỖI THƯỜNG GẶP

### Lỗi: "ModuleNotFoundError: No module named 'cryptography'"
```bash
pip install cryptography
```

### Lỗi: "Table 'user_settings' does not exist"
```bash
python -c "from app.core.database import init_db; init_db()"
```

### Lỗi: "Column 'user_id' does not exist"
- Cần migrate database (xem PULL_VPS_SETTINGS.md)

### Lỗi: "ImportError: cannot import name 'X'"
- Có thể do circular import hoặc file chưa được commit
- Kiểm tra: `git status` và `git pull origin main`

## 🚀 QUICK FIX

```bash
cd ~/ads-automation && \
source venv/bin/activate && \
git pull origin main && \
pip install -r requirements.txt && \
python -c "from app.core.database import init_db; init_db()" && \
sudo supervisorctl restart ads-automation-api && \
sleep 3 && \
sudo supervisorctl status ads-automation-api
```

## 📝 KIỂM TRA SAU KHI FIX

1. Check service status: `sudo supervisorctl status`
2. Check logs: `sudo tail -50 /var/log/ads-automation/api.err.log`
3. Test website: `curl https://updatemetaads.site/health`
4. Test settings: `curl https://updatemetaads.site/settings` (sẽ redirect nếu chưa login)

---

**Nếu vẫn còn lỗi, gửi output của `sudo tail -100 /var/log/ads-automation/api.err.log` để debug tiếp!**

