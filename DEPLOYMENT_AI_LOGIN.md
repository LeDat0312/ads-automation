# 🚀 Hướng Dẫn Deploy AI Login Interface

## Bước 1: Push Code Lên GitHub (Windows)

### Cách 1: Sử dụng Script Tự Động
```bash
# Click đúp vào file này để chạy:
PUSH_AI_LOGIN.bat
```

### Cách 2: Chạy Lệnh Thủ Công
```bash
# Mở PowerShell/CMD tại thư mục project
cd "C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet"

# Add file thay đổi
git add app/api/routes/auth.py

# Commit với message
git commit -m "feat: Add AI-powered login interface with mouse tracking"

# Push lên GitHub
git push origin main
```

---

## Bước 2: Pull Code Về VPS

### SSH vào VPS của bạn, sau đó chạy:

```bash
# Di chuyển đến thư mục project
cd /var/www/ads-automation

# Pull code mới từ GitHub
git pull origin main

# Restart service để áp dụng thay đổi
sudo supervisorctl restart ads-automation-production

# Kiểm tra service đã chạy lại chưa
sudo supervisorctl status ads-automation-production
```

### Hoặc sử dụng script update có sẵn:

```bash
sudo bash /var/www/ads-automation/update-vps.sh
```

---

## Bước 3: Kiểm Tra

1. Mở trình duyệt và truy cập: `http://YOUR_VPS_IP/auth/login`
2. Bạn sẽ thấy giao diện mới với AI robot
3. Di chuyển chuột để xem mắt AI theo dõi
4. Click vào ô password để xem AI che mắt

---

## ⚡ Lệnh Nhanh (Copy & Paste)

**Trên VPS:**
```bash
cd /var/www/ads-automation && git pull origin main && sudo supervisorctl restart ads-automation-production
```

**Kiểm tra logs nếu có lỗi:**
```bash
sudo tail -f /var/log/ads-automation-production.log
```

---

## 📝 Nếu Gặp Lỗi Git Conflict

Nếu có conflict khi pull, chạy:
```bash
# Stash local changes
git stash

# Pull mới
git pull origin main

# Apply stash (nếu cần)
git stash pop
```

Hoặc force pull (cẩn thận - sẽ ghi đè local changes):
```bash
git fetch origin
git reset --hard origin/main
```
