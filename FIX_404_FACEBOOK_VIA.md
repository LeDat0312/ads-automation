# FIX 404 ERROR - /settings/facebook-via

## ❌ Vấn đề:
Truy cập `https://updatemetaads.site/settings/facebook-via` → lỗi 404

## ✅ Nguyên nhân:
Frontend chưa được rebuild sau khi pull code mới từ GitHub

## 🔧 Cách khắc phục trên VPS:

### Option 1: Rebuild frontend (Recommended)

```bash
# SSH vào VPS
ssh adsuser@your-vps-ip

# Vào thư mục frontend
cd /home/adsuser/ads-automation/frontend

# Rebuild
npm run build

# Restart service
cd ..
sudo systemctl restart ads-automation
```

### Option 2: Rebuild + restart bằng 1 lệnh

```bash
ssh adsuser@your-vps-ip "cd /home/adsuser/ads-automation/frontend && npm run build && cd .. && sudo systemctl restart ads-automation"
```

### Option 3: Nếu dùng PM2

```bash
cd /home/adsuser/ads-automation/frontend
npm run build
pm2 restart ads-automation
```

---

## 🧪 Kiểm tra sau khi rebuild:

1. Truy cập: `https://updatemetaads.site/settings/facebook-via`
2. Sẽ thấy trang "Quản lý Via Facebook"
3. Có thể thêm/sửa/xóa Via
4. Có thể verify token

---

## 🔍 Debug nếu vẫn lỗi:

### Kiểm tra file có tồn tại không:

```bash
ls -la /home/adsuser/ads-automation/frontend/src/pages/settings/FacebookViaPage.tsx
```

**Expect:** File tồn tại

### Kiểm tra build output:

```bash
ls -la /home/adsuser/ads-automation/frontend/dist/
```

**Expect:** Thư mục dist/ có file index.html và assets/

### Kiểm tra nginx serve static files:

```bash
sudo nginx -t
sudo systemctl status nginx
```

### Kiểm tra logs:

```bash
# Backend logs
sudo journalctl -u ads-automation -n 50 --no-pager

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

---

## 📋 Checklist:

- [ ] SSH vào VPS thành công
- [ ] Pull code mới: `git pull origin main`
- [ ] Rebuild frontend: `npm run build`
- [ ] Restart service
- [ ] Test route: `/settings/facebook-via` → OK
- [ ] Test route: `/settings/channels` → OK
- [ ] Test kết nối Fanpage → OK

---

## 🚀 ONE-LINE FIX:

```bash
ssh adsuser@your-vps "cd /home/adsuser/ads-automation && git pull origin main && cd frontend && npm run build && cd .. && sudo systemctl restart ads-automation && echo '✅ Done! Test at: https://updatemetaads.site/settings/facebook-via'"
```

Sau khi chạy xong, refresh trình duyệt và truy cập lại!
