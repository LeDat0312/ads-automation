# 🚀 HƯỚNG DẪN PULL CODE VỀ VPS

## ✅ Code đã được push lên GitHub thành công!

**Repository:** https://github.com/LeDat0312/ads-automation.git  
**Branch:** main  
**Commit:** FIX: All dashboard bugs

---

## 📋 CÁC LỆNH PULL VỀ VPS

### Option 1️⃣: Dùng Script Tự Động (KHUYẾN NGHỊ)

```bash
# SSH vào VPS
ssh root@your-vps-ip

# Vào thư mục project
cd /root/ads-automation

# Pull code mới
git pull origin main

# Chạy script tự động
chmod +x PULL_VPS_FIX_ALL_BUGS.sh
./PULL_VPS_FIX_ALL_BUGS.sh
```

### Option 2️⃣: Pull Thủ Công (Từng Bước)

```bash
# 1. SSH vào VPS
ssh root@your-vps-ip

# 2. Vào thư mục project
cd /root/ads-automation

# 3. Stash changes hiện tại (nếu có)
git stash

# 4. Pull code mới
git pull origin main --rebase

# 5. Xem các thay đổi
git log --oneline -5

# 6. Rebuild frontend (nếu cần)
cd frontend
npm install  # Chỉ chạy nếu có dependencies mới
npm run build

# 7. Restart backend service
cd ..
sudo systemctl restart ads-automation

# 8. Restart nginx (nếu cần)
sudo systemctl restart nginx

# 9. Kiểm tra status
sudo systemctl status ads-automation
```

---

## 🔍 KIỂM TRA SAU KHI PULL

### 1. Kiểm tra Service đang chạy:
```bash
sudo systemctl status ads-automation
```

### 2. Xem logs:
```bash
# Backend logs
sudo journalctl -u ads-automation -f

# Hoặc xem log file
tail -f /root/ads-automation/logs/app.log
```

### 3. Test Dashboard:
- Mở trình duyệt: `http://your-vps-ip/dashboard`
- Kiểm tra các bug đã fix:
  - ✅ Toggle ON/OFF campaign
  - ✅ Cột ngân sách (CBO/ABO)
  - ✅ % ADS, Giá DATA, TLC
  - ✅ Bảng Lead Generation không rỗng

---

## 🛠️ TROUBLESHOOTING

### Nếu có lỗi khi pull:
```bash
# Reset về trạng thái clean
git reset --hard origin/main

# Hoặc clone lại từ đầu
cd /root
rm -rf ads-automation
git clone https://github.com/LeDat0312/ads-automation.git
cd ads-automation
```

### Nếu service không start:
```bash
# Xem chi tiết lỗi
sudo journalctl -u ads-automation -n 50 --no-pager

# Kiểm tra dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart lại
sudo systemctl restart ads-automation
```

### Nếu frontend không hiển thị:
```bash
# Rebuild frontend
cd /root/ads-automation/frontend
npm install
npm run build

# Restart nginx
sudo systemctl restart nginx
```

---

## 📊 CÁC FILE QUAN TRỌNG ĐÃ THAY ĐỔI

**Backend:**
- `app/api/routes/dashboard.py` - Fix metrics calculation
- `app/services/facebook_api.py` - Add derived metrics

**Frontend:**
- `frontend/src/components/AdsetTable.tsx` - Fix toggle & budget display
- `frontend/src/components/BudgetModal.tsx` - Fix preview calculation
- `frontend/src/App.tsx` - Fix budget update handlers

**Documentation:**
- `FIX_SUMMARY_BUGS.md` - Chi tiết tất cả thay đổi

---

## 💡 LƯU Ý

1. **Không cần cài lại dependencies** nếu không có thay đổi trong `requirements.txt` hoặc `package.json`
2. **Chỉ cần restart service** nếu chỉ sửa code Python backend
3. **Phải rebuild frontend** nếu có thay đổi trong `frontend/src/`
4. **Restart nginx** chỉ khi có thay đổi cấu hình hoặc static files

---

## 🎉 DONE!

Sau khi pull và restart, dashboard sẽ hoạt động với tất cả các bugs đã được fix!

**Questions?** Check `FIX_SUMMARY_BUGS.md` để biết chi tiết các thay đổi.
