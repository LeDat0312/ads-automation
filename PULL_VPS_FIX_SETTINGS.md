# 🔧 PULL CODE LÊN VPS - FIX SETTINGS

## 📋 TÓM TẮT THAY ĐỔI

### ✅ Đã sửa:
1. **Thêm nút xóa token** - Cho phép xóa token đã lưu
2. **Hiển thị token đã lưu** - Hiển thị token đã lưu (masked) và cho phép update
3. **Fix lỗi JSON parsing** - Cải thiện error handling để tránh lỗi "Unexpected token 'I'"
4. **Fix authentication** - Thêm Request parameter vào tất cả endpoints để check cookie đúng cách

### 📝 Files đã sửa:
- `app/api/routes/settings.py` - Thêm delete token endpoint, cải thiện UI và error handling

---

## 🚀 QUICK PULL COMMANDS

```bash
cd ~/ads-automation && \
source venv/bin/activate && \
git pull origin main && \
sudo supervisorctl restart ads-automation-api
```

---

## 📋 CÁC BƯỚC CHI TIẾT

### BƯỚC 1: Pull code
```bash
cd ~/ads-automation
source venv/bin/activate
git pull origin main
```

### BƯỚC 2: Restart API service
```bash
sudo supervisorctl restart ads-automation-api
```

### BƯỚC 3: Check status
```bash
sudo supervisorctl status
```

### BƯỚC 4: Check logs (nếu có lỗi)
```bash
sudo tail -50 /var/log/ads-automation/api.err.log
```

---

## ✅ KIỂM TRA

1. Truy cập: `https://updatemetaads.site/settings`
2. Kiểm tra:
   - ✅ Token section hiển thị token đã lưu (masked) nếu có
   - ✅ Có nút "Xóa Token" khi đã có token
   - ✅ Có thể update token bằng cách nhập token mới và click "Cập Nhật Token"
   - ✅ Accounts và Prefixes load được không còn lỗi JSON

---

## 🐛 NẾU VẪN CÒN LỖI

### Lỗi: "Internal Server Error" hoặc JSON parsing error
- Kiểm tra logs: `sudo tail -f /var/log/ads-automation/api.err.log`
- Có thể do database chưa có table `user_settings`
- Chạy: `python -c "from app.core.database import init_db; init_db()"`

### Lỗi: "Column 'user_id' does not exist"
- Cần migrate database (xem PULL_VPS_SETTINGS.md)

---

**Sau khi pull, test lại tại `https://updatemetaads.site/settings`** 🎉

