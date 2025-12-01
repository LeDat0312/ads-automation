# HƯỚNG DẪN PULL CODE VỀ VPS - Facebook Via Token Management

## 📦 Bước 1: Commit và Push từ máy local

**Windows PowerShell:**
```powershell
cd "C:\Users\Foxy\Downloads\File 5h_4_11\MetaUpdate"

# Stage tất cả file mới
git add frontend/src/api/base.ts
git add frontend/src/api/facebookVia.ts
git add frontend/src/api/facebookChannels.ts
git add "frontend/src/pages/settings/FacebookViaPage.tsx"
git add frontend/src/components/ConnectFacebookPageModal.tsx
git add frontend/src/pages/Settings/ChannelsSettingsPage.tsx
git add frontend/src/Router.tsx
git add frontend/src/components/SettingsLayout.tsx
git add FRONTEND_SETUP_INSTRUCTIONS.md

# Commit
git commit -m "feat: Complete Facebook Via Token Management frontend

- Added Via management page (/settings/facebook-via)
- Added 2-step Facebook Page connection modal
- Created API layer (base.ts, facebookVia.ts, facebookChannels.ts)
- Updated routing and navigation
- All UI in Vietnamese with TypeScript types
- 900+ lines of production-ready code"

# Push lên GitHub
git push origin main
```

**Hoặc dùng Git Bash (nếu có):**
```bash
bash push_frontend_updates.sh
```

---

## 🌐 Bước 2: Pull code về VPS

**SSH vào VPS:**
```bash
ssh root@your-vps-ip
# hoặc
ssh your-username@your-vps-ip
```

**Chuyển vào thư mục project:**
```bash
cd /home/adsuser/ads-automation
```

**Pull code mới nhất:**
```bash
# Stash local changes (nếu có)
git stash

# Pull từ GitHub
git pull origin main

# Nếu có conflict, resolve và:
# git stash pop
```

**ONE-LINE COMMAND (copy & paste):**
```bash
cd /home/adsuser/ads-automation && git stash && git pull origin main && cd frontend && npm install @headlessui/react react-toastify dayjs
```

---

## 📦 Bước 3: Cài packages cho frontend

```bash
cd frontend

# Cài 3 packages mới
npm install @headlessui/react react-toastify dayjs

# Kiểm tra đã cài thành công
npm list @headlessui/react react-toastify dayjs
```

**Output mong đợi:**
```
├── @headlessui/react@X.X.X
├── react-toastify@X.X.X
└── dayjs@X.X.X
```

---

## 🔨 Bước 4: Build frontend (Production)

**Nếu đang chạy development mode:**
```bash
npm run dev
```

**Nếu production (build static files):**
```bash
npm run build

# Output sẽ trong thư mục dist/
```

---

## 🔄 Bước 5: Restart services

**Nếu dùng systemd service:**
```bash
sudo systemctl restart ads-automation
sudo systemctl status ads-automation
```

**Nếu dùng PM2:**
```bash
pm2 restart ads-automation
pm2 logs ads-automation --lines 50
```

**Nếu dùng Supervisor:**
```bash
sudo supervisorctl restart ads-automation
sudo supervisorctl status ads-automation
```

**Nếu dùng nginx + gunicorn:**
```bash
# Restart backend
sudo systemctl restart gunicorn-ads-automation

# Restart nginx
sudo systemctl restart nginx

# Check logs
sudo journalctl -u gunicorn-ads-automation -n 50 --no-pager
```

---

## 🧪 Bước 6: Kiểm tra frontend

**Truy cập các route mới:**
- `https://your-domain.com/settings/facebook-via` - Quản lý Via
- `https://your-domain.com/settings/channels` - Kênh (modal mới)

**Kiểm tra console logs:**
```bash
# Chrome DevTools > Console
# Không có lỗi "Cannot find module"
# API calls thành công (200/201)
```

**Test flow:**
1. Login vào hệ thống
2. Vào Settings > 🔑 Quản lý Via Facebook
3. Thêm Via mới (cần token thật từ Facebook Graph API Explorer)
4. Verify token
5. Vào Settings > Kênh đã kết nối
6. Click "➕ Thêm kênh" → modal 2 bước hiện ra
7. Chọn Via → Tải danh sách Fanpage
8. Kết nối Fanpage

---

## 🐛 Troubleshooting VPS

### Lỗi: "Cannot find module '@headlessui/react'"
```bash
cd frontend
npm install @headlessui/react react-toastify dayjs --force
npm run build
```

### Lỗi: Git pull conflict
```bash
# Xem file conflicts
git status

# Option 1: Giữ local changes
git stash
git pull origin main
git stash pop

# Option 2: Force pull (MẤT local changes)
git fetch --all
git reset --hard origin/main
```

### Lỗi: Build frontend failed
```bash
# Xóa node_modules và rebuild
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Lỗi: Permission denied
```bash
# Fix ownership
sudo chown -R adsuser:adsuser /home/adsuser/ads-automation

# Fix permissions
sudo chmod -R 755 /home/adsuser/ads-automation
```

### Lỗi: Port 5173 already in use (dev mode)
```bash
# Kill process
lsof -ti:5173 | xargs kill -9

# Hoặc đổi port trong vite.config.ts:
# server: { port: 5174 }
```

---

## 📋 Summary of Files Changed

**New Files (5):**
- `frontend/src/api/base.ts` (32 lines) - Axios instance
- `frontend/src/api/facebookVia.ts` (50 lines) - Via API
- `frontend/src/api/facebookChannels.ts` (27 lines) - Channel API
- `frontend/src/pages/settings/FacebookViaPage.tsx` (260+ lines) - Via UI
- `frontend/src/components/ConnectFacebookPageModal.tsx` (300+ lines) - Modal

**Modified Files (3):**
- `frontend/src/Router.tsx` - Added route
- `frontend/src/components/SettingsLayout.tsx` - Added menu item
- `frontend/src/pages/Settings/ChannelsSettingsPage.tsx` - Integrated modal

**Total: 900+ lines production-ready code**

---

## ✅ Verification Checklist

- [ ] Code pushed lên GitHub thành công
- [ ] SSH vào VPS thành công
- [ ] `git pull origin main` không có lỗi
- [ ] `npm install @headlessui/react react-toastify dayjs` thành công
- [ ] `npm run build` (nếu production) thành công
- [ ] Service restart thành công
- [ ] Frontend truy cập được (no 502/404)
- [ ] Route `/settings/facebook-via` hiện trang
- [ ] Route `/settings/channels` hiện modal mới
- [ ] API calls backend thành công (200/201)
- [ ] Toast notifications hoạt động
- [ ] TypeScript compile không lỗi

---

## 🚀 Quick Commands (Copy & Paste)

**LOCAL (Windows PowerShell):**
```powershell
cd "C:\Users\Foxy\Downloads\File 5h_4_11\MetaUpdate"; git add .; git commit -m "feat: Facebook Via frontend complete"; git push origin main
```

**VPS (Linux - ONE LINE):**
```bash
cd /home/adsuser/ads-automation && git pull origin main && cd frontend && npm install @headlessui/react react-toastify dayjs && npm run build && cd .. && sudo systemctl restart ads-automation
```

**VPS (Check Status):**
```bash
sudo systemctl status ads-automation && sudo journalctl -u ads-automation -n 30 --no-pager
```

---

📞 **Need help?** Check logs:
```bash
# Backend logs
sudo journalctl -u ads-automation -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Frontend build logs
cd frontend && npm run build 2>&1 | tee build.log
```
