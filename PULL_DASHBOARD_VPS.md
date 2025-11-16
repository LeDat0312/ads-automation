# Hướng Dẫn Pull Code Dashboard Lên VPS

## Cách 1: Sử dụng Script Tự Động (Khuyến nghị)

### Bước 1: Upload script lên VPS
```bash
# Từ máy local, upload script lên VPS
scp PULL_DASHBOARD_VPS.sh root@your-vps-ip:/root/
```

### Bước 2: Chạy script trên VPS
```bash
# SSH vào VPS
ssh root@your-vps-ip

# Cấp quyền thực thi
chmod +x /root/PULL_DASHBOARD_VPS.sh

# Chạy script
bash /root/PULL_DASHBOARD_VPS.sh
```

## Cách 2: Chạy Lệnh Thủ Công

### SSH vào VPS
```bash
ssh root@your-vps-ip
```

### Di chuyển vào thư mục project
```bash
cd /root/PythonUpdateMetaAds  # Hoặc đường dẫn thực tế của bạn
```

### Pull code từ GitHub
```bash
# Stash các thay đổi local (nếu có)
git stash

# Pull code mới nhất
git pull origin main

# Nếu có conflict, reset về main
# git fetch origin main
# git reset --hard origin/main
```

### Kiểm tra syntax Python
```bash
python3 -m py_compile app/api/routes/dashboard.py app/core/ui_helpers.py app/api/routes/home.py
```

### Restart services
```bash
# Restart API service
sudo supervisorctl restart api

# Restart Worker service (nếu có)
sudo supervisorctl restart worker

# Kiểm tra status
sudo supervisorctl status
```

## Kiểm Tra Sau Khi Pull

1. **Kiểm tra services đang chạy:**
   ```bash
   sudo supervisorctl status
   ```

2. **Kiểm tra logs nếu có lỗi:**
   ```bash
   # Logs API
   sudo supervisorctl tail -f api
   
   # Logs Worker
   sudo supervisorctl tail -f worker
   ```

3. **Kiểm tra website:**
   - Trang chủ: https://updatemetaads.site/
   - Dashboard: https://updatemetaads.site/dashboard/

## Lưu Ý

- **Đường dẫn project:** Đảm bảo `PROJECT_DIR` trong script khớp với đường dẫn thực tế trên VPS
- **GitHub credentials:** Script đã có sẵn token, không cần nhập lại
- **Backup:** Nên backup database trước khi pull nếu có thay đổi schema
- **Dependencies:** Nếu có thêm package mới, uncomment phần cài đặt dependencies trong script

## Troubleshooting

### Lỗi: "Thư mục project không tồn tại"
- Kiểm tra đường dẫn `PROJECT_DIR` trong script
- Hoặc chạy lệnh thủ công với đường dẫn đúng

### Lỗi: "Permission denied"
```bash
chmod +x PULL_DASHBOARD_VPS.sh
```

### Lỗi: "Git pull failed"
```bash
git fetch origin main
git reset --hard origin/main
```

### Service không restart được
```bash
# Kiểm tra logs
sudo supervisorctl tail -f api

# Restart lại supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart api
```


