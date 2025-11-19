# 🔧 Fix 502 Bad Gateway Error - VPS Troubleshooting Guide

## ❌ Lỗi hiện tại:
```
502 Bad Gateway
nginx/1.18.0 (Ubuntu)
```

**Nguyên nhân:** Nginx không kết nối được với Backend (Python/FastAPI)

---

## 📋 Các bước chẩn đoán theo thứ tự:

### **Bước 1: Pull code mới nhất từ GitHub**

```bash
# SSH vào VPS
ssh user@your-vps-ip

# Di chuyển vào thư mục project
cd /path/to/ads-automation

# Pull code
git pull origin main
```

---

### **Bước 2: Kiểm tra Backend có chạy không**

```bash
# Kiểm tra process uvicorn/python
ps aux | grep uvicorn
ps aux | grep python

# Kiểm tra port 8000
sudo netstat -tulpn | grep :8000
# HOẶC
sudo ss -tulpn | grep :8000
```

**Kết quả mong đợi:**
```
tcp  0  0  0.0.0.0:8000  0.0.0.0:*  LISTEN  12345/python
```

**Nếu KHÔNG thấy** → Backend đã crash, chuyển sang Bước 3

---

### **Bước 3: Xem log Backend để tìm lỗi**

#### **A. Nếu dùng systemd service:**

```bash
# Xem 100 dòng log cuối
sudo journalctl -u your-backend-service -n 100 --no-pager

# Xem log realtime
sudo journalctl -u your-backend-service -f
```

#### **B. Nếu dùng PM2:**

```bash
# Xem log
pm2 logs app --lines 100

# Xem status
pm2 status
```

#### **C. Nếu chạy thủ công:**

```bash
# Xem log file
tail -f /path/to/logs/uvicorn.log
tail -f /path/to/logs/app.log
```

**Tìm các lỗi phổ biến:**
- ❌ `SyntaxError: invalid syntax` → Lỗi code Python
- ❌ `ImportError: No module named 'xxx'` → Thiếu package
- ❌ `IndentationError` → Lỗi thụt lề
- ❌ `ModuleNotFoundError` → Import sai
- ❌ `Address already in use` → Port 8000 bị chiếm
- ❌ `FileNotFoundError` → Thiếu file config

---

### **Bước 4: Kiểm tra log Nginx**

```bash
# Error log
sudo tail -f /var/log/nginx/error.log

# Access log
sudo tail -f /var/log/nginx/access.log
```

**Lỗi thường gặp:**
```
[error] connect() failed (111: Connection refused) while connecting to upstream
```
→ Backend không chạy hoặc sai port

---

### **Bước 5: Kiểm tra cấu hình Nginx**

```bash
# Test cấu hình
sudo nginx -t

# Xem file config
sudo cat /etc/nginx/sites-enabled/ads-automation.conf
# HOẶC
sudo cat /etc/nginx/sites-enabled/default
```

**Cấu hình đúng phải có:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Dashboard
    location /dashboard {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend static files (nếu có)
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

**Nếu sai cấu hình:**
```bash
sudo nano /etc/nginx/sites-enabled/ads-automation.conf
# Chỉnh sửa, sau đó:
sudo nginx -t
sudo systemctl reload nginx
```

---

### **Bước 6: Khởi động lại Backend**

#### **A. Nếu dùng systemd:**

```bash
sudo systemctl restart your-backend-service
sudo systemctl status your-backend-service
```

#### **B. Nếu dùng PM2:**

```bash
pm2 restart app
pm2 status
pm2 logs app --lines 50
```

#### **C. Nếu chạy thủ công:**

```bash
# Stop backend cũ (nếu có)
pkill -f uvicorn

# Di chuyển vào thư mục project
cd /path/to/ads-automation

# Activate virtualenv (nếu có)
source venv/bin/activate

# Cài đặt dependencies (nếu cần)
pip install -r requirements.txt

# Chạy backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

# Kiểm tra
tail -f backend.log
```

---

### **Bước 7: Test Backend trực tiếp**

```bash
# Test từ VPS
curl http://localhost:8000/api/health
curl http://localhost:8000/dashboard/health

# Nếu trả về JSON → Backend OK
# Nếu lỗi "Connection refused" → Backend chưa chạy
```

---

### **Bước 8: Restart Nginx**

```bash
sudo systemctl restart nginx
sudo systemctl status nginx
```

---

## 🐛 **Lỗi Backend thường gặp sau khi pull code:**

### **Lỗi 1: SyntaxError hoặc IndentationError**

**Nguyên nhân:** File `dashboard.py` có lỗi syntax

**Giải pháp:**
```bash
cd /path/to/ads-automation

# Kiểm tra syntax Python
python3 -m py_compile app/api/routes/dashboard.py

# Nếu lỗi, xem chi tiết:
python3 app/api/routes/dashboard.py
```

**Nếu lỗi indentation (thụt lề):**
```bash
# Sử dụng dashboardnew.py thay vì dashboard.py
cd /path/to/ads-automation/app/api/routes

# Backup file cũ
cp dashboard.py dashboard_old_with_error.py

# Sử dụng file mới (đã refactor, không có HTML)
cp dashboardnew.py dashboard.py

# Restart backend
sudo systemctl restart your-backend-service
```

---

### **Lỗi 2: ImportError - Thiếu package**

**Nguyên nhân:** Thiếu dependencies sau khi pull code

**Giải pháp:**
```bash
cd /path/to/ads-automation
source venv/bin/activate  # Nếu dùng virtualenv
pip install -r requirements.txt
sudo systemctl restart your-backend-service
```

---

### **Lỗi 3: Port 8000 đã được sử dụng**

**Nguyên nhân:** Process cũ vẫn chạy

**Giải pháp:**
```bash
# Tìm process đang dùng port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# HOẶC kill tất cả uvicorn
pkill -f uvicorn

# Chạy lại
sudo systemctl restart your-backend-service
```

---

## ✅ **Checklist sau khi fix:**

- [ ] Backend đang chạy (`ps aux | grep uvicorn`)
- [ ] Port 8000 đang listen (`netstat -tulpn | grep :8000`)
- [ ] Log backend không có lỗi (`journalctl -u service -n 50`)
- [ ] Nginx config đúng (`sudo nginx -t`)
- [ ] Test API thành công (`curl http://localhost:8000/api/health`)
- [ ] Website không còn lỗi 502

---

## 📊 **Script tổng hợp để chẩn đoán:**

Tạo file `diagnose_502.sh`:

```bash
#!/bin/bash
echo "=== 502 Bad Gateway Diagnostic ==="
echo ""

echo "1. Backend Process:"
ps aux | grep uvicorn | grep -v grep
echo ""

echo "2. Port 8000:"
sudo netstat -tulpn | grep :8000
echo ""

echo "3. Backend Logs (last 20 lines):"
sudo journalctl -u your-backend-service -n 20 --no-pager
echo ""

echo "4. Nginx Error Log (last 10 lines):"
sudo tail -10 /var/log/nginx/error.log
echo ""

echo "5. Test Backend:"
curl -s http://localhost:8000/api/health || echo "Backend not responding"
echo ""

echo "6. Nginx Status:"
sudo systemctl status nginx --no-pager | head -5
echo ""
```

**Chạy:**
```bash
chmod +x diagnose_502.sh
./diagnose_502.sh
```

---

## 🚀 **Sau khi fix xong:**

```bash
# Test lại website
curl https://your-domain.com
curl https://your-domain.com/api/health
curl https://your-domain.com/dashboard/

# Kiểm tra log realtime
sudo journalctl -u your-backend-service -f
```

---

## 📞 **Cần thêm thông tin gì?**

Gửi cho tôi output của các lệnh sau:

```bash
# 1. Backend process
ps aux | grep uvicorn

# 2. Backend logs
sudo journalctl -u your-backend-service -n 50 --no-pager

# 3. Nginx error log
sudo tail -50 /var/log/nginx/error.log

# 4. Python errors
python3 -m py_compile app/api/routes/dashboard.py
```

Tôi sẽ giúp bạn fix cụ thể!
