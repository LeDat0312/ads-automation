# 🔍 HƯỚNG DẪN CHECK LOGS KHI BỊ LỖI 502 BAD GATEWAY

## 📋 CÁC LỆNH CHECK LOGS TRÊN VPS

### 1. **Check Service Status**
```bash
sudo supervisorctl status
```

### 2. **Check Logs của ads-automation-api (50 dòng cuối)**
```bash
sudo supervisorctl tail -50 ads-automation-api
```

### 3. **Check Nginx Error Logs**
```bash
sudo tail -50 /var/log/nginx/error.log
```

### 4. **Check Nginx Access Logs**
```bash
sudo tail -20 /var/log/nginx/access.log
```

### 5. **Check Python Syntax Errors**
```bash
cd ~/ads-automation
source venv/bin/activate
python -m py_compile app/api/routes/settings.py
```

### 6. **Check Import Errors**
```bash
python -c "from app.api.routes.settings import router"
```

### 7. **Check Database Connection**
```bash
python -c "from app.core.database import engine; print('OK' if engine else 'FAILED')"
```

### 8. **Check Port 8000 (FastAPI)**
```bash
sudo netstat -tlnp | grep 8000
# hoặc
sudo ss -tlnp | grep 8000
```

### 9. **Check Disk Space**
```bash
df -h
```

---

## 🚀 SỬ DỤNG SCRIPT TỰ ĐỘNG

### **Option 1: Check tất cả logs (chi tiết)**
```bash
cd ~/ads-automation
chmod +x scripts/check_vps_logs.sh
./scripts/check_vps_logs.sh
```

### **Option 2: Quick fix (tự động)**
```bash
cd ~/ads-automation
chmod +x scripts/quick_fix_502.sh
./scripts/quick_fix_502.sh
```

---

## 🔧 CÁC CÁCH FIX THƯỜNG GẶP

### **1. Service không chạy**
```bash
sudo supervisorctl start ads-automation-api
sudo supervisorctl status ads-automation-api
```

### **2. Có syntax errors**
- Check logs để xem lỗi cụ thể
- Sửa code
- Restart service:
```bash
sudo supervisorctl restart ads-automation-api
```

### **3. Có import errors**
- Kiểm tra dependencies:
```bash
cd ~/ads-automation
source venv/bin/activate
pip install -r requirements.txt
```

### **4. Database connection lỗi**
- Kiểm tra `.env` file:
```bash
cat ~/ads-automation/.env | grep DATABASE_URL
```

### **5. Pull code mới và restart**
```bash
cd ~/ads-automation
source venv/bin/activate
git pull origin main
sudo supervisorctl restart ads-automation-api
```

### **6. Restart toàn bộ**
```bash
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker:*
sudo systemctl restart nginx
```

---

## 📝 LỆNH TỔNG HỢP (Copy & Paste)

```bash
# Vào thư mục project
cd ~/ads-automation
source venv/bin/activate

# Check service status
sudo supervisorctl status

# Check logs (50 dòng cuối)
sudo supervisorctl tail -50 ads-automation-api

# Check nginx errors
sudo tail -50 /var/log/nginx/error.log

# Check syntax
python -m py_compile app/api/routes/settings.py

# Check imports
python -c "from app.api.routes.settings import router"

# Restart service
sudo supervisorctl restart ads-automation-api

# Check lại status
sudo supervisorctl status ads-automation-api
```

---

## ⚠️ LƯU Ý

1. **Luôn check logs trước khi fix** để biết nguyên nhân chính xác
2. **Backup code trước khi pull** nếu cần
3. **Check disk space** nếu logs quá lớn
4. **Kiểm tra .env** nếu có lỗi database connection

