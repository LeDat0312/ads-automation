# 📥 Câu lệnh Pull Code về VPS

## ✅ Code đã được push lên GitHub thành công!

**Latest commits:**
- ✅ Channel Management backend implementation
- ✅ Frontend API integration
- ✅ VPS deployment scripts

---

## 🚀 Cách 1: Dùng Script Tự Động (Khuyên dùng)

```bash
cd /home/adsuser/ads-automation
chmod +x vps_pull_channel_backend.sh
./vps_pull_channel_backend.sh
```

Script này sẽ tự động:
1. ✅ Backup thay đổi local
2. ✅ Xử lý permissions
3. ✅ Pull code mới
4. ✅ Rebuild frontend
5. ✅ Chạy database migration
6. ✅ Restart services

---

## 🔧 Cách 2: Lệnh Thủ Công (Từng bước)

### Bước 1: Di chuyển vào thư mục project
```bash
cd /home/adsuser/ads-automation
```

### Bước 2: Backup và Pull code
```bash
# Backup thay đổi local (nếu có)
git stash

# Xóa frontend/dist nếu có vấn đề permissions
sudo rm -rf frontend/dist 2>/dev/null || true

# Pull code mới
git fetch origin main
git reset --hard origin/main
git clean -fd
```

### Bước 3: Rebuild Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### Bước 4: Chạy Database Migration
```bash
python3 -m migrations.add_channels_management_tables
```

Hoặc nếu cần chỉ định path:
```bash
PYTHONPATH=/home/adsuser/ads-automation python3 -m migrations.add_channels_management_tables
```

### Bước 5: Restart Services

**Nếu dùng systemd:**
```bash
sudo systemctl restart ads-automation.service
```

**Nếu dùng uwsgi:**
```bash
sudo systemctl restart uwsgi.service
```

**Nếu chạy manual:**
- Tìm process ID: `ps aux | grep uvicorn` hoặc `ps aux | grep python`
- Kill và restart lại process

---

## ⚠️ Nếu Gặp Lỗi Permissions

```bash
# Fix ownership
sudo chown -R adsuser:adsuser /home/adsuser/ads-automation

# Fix frontend/dist permissions
sudo rm -rf frontend/dist
cd frontend
npm run build
cd ..
```

---

## 🗄️ Kiểm Tra Database Migration

Sau khi chạy migration, kiểm tra các bảng đã được tạo:

```bash
# Vào PostgreSQL
psql -U adsuser -d ads_automation_db

# Kiểm tra bảng mới
\dt channels*
\dt channel_group*
\dt posting_settings
\dt auto_comment_templates

# Thoát
\q
```

---

## ✅ Verify Sau Khi Deploy

### 1. Kiểm tra API endpoints:

```bash
# Test channels endpoint (cần token)
curl -X GET http://localhost:8000/api/channels \
  -H "Cookie: access_token=YOUR_TOKEN"
```

### 2. Kiểm tra frontend:

- Mở trình duyệt: `http://your-vps-ip/settings/channels`
- Mở trình duyệt: `http://your-vps-ip/settings/channel-groups`
- Mở trình duyệt: `http://your-vps-ip/settings/posting`

### 3. Kiểm tra logs:

```bash
# Xem logs của service
sudo journalctl -u ads-automation.service -n 100 --no-pager

# Hoặc nếu có log file
tail -f /var/log/ads-automation.log
```

---

## 📋 Checklist Deployment

Sau khi pull và chạy các lệnh trên, kiểm tra:

- [ ] Code đã pull thành công (git log -1)
- [ ] Frontend đã build thành công (kiểm tra frontend/dist/)
- [ ] Database migration đã chạy (kiểm tra bảng trong DB)
- [ ] Services đã restart (kiểm tra status)
- [ ] API endpoints trả về dữ liệu (test với curl)
- [ ] Frontend pages load được (kiểm tra browser)

---

## 🔄 Nếu Cần Rollback

```bash
cd /home/adsuser/ads-automation

# Xem lịch sử commit
git log --oneline -10

# Revert về commit trước
git reset --hard <commit_hash_trước_đây>

# Rebuild frontend
cd frontend && npm run build && cd ..

# Restart services
sudo systemctl restart ads-automation.service
```

---

## 📞 Lỗi Thường Gặp

### Lỗi: "Permission denied" khi pull
```bash
sudo chown -R adsuser:adsuser /home/adsuser/ads-automation
```

### Lỗi: "frontend/dist" không xóa được
```bash
sudo rm -rf frontend/dist
```

### Lỗi: Migration không chạy được
```bash
# Kiểm tra Python path
which python3
python3 --version

# Chạy với đầy đủ path
PYTHONPATH=/home/adsuser/ads-automation python3 -m migrations.add_channels_management_tables
```

### Lỗi: Frontend build failed
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📝 Tóm Tắt Nhanh

**Copy-paste toàn bộ lệnh này vào VPS:**

```bash
cd /home/adsuser/ads-automation && \
git stash && \
sudo rm -rf frontend/dist 2>/dev/null || true && \
git fetch origin main && \
git reset --hard origin/main && \
git clean -fd && \
cd frontend && npm install && npm run build && cd .. && \
python3 -m migrations.add_channels_management_tables && \
sudo systemctl restart ads-automation.service && \
echo "✅ Deployment completed!"
```

