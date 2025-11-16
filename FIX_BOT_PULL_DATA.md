# ✅ FIX BOT - PULL DATA TRƯỚC KHI BÁO CÁO

## 🎯 ĐÃ SỬA

### **1. Webhook GET endpoint**
- ✅ Thêm GET endpoint cho `/api/telegram/webhook` để test
- ✅ Trả về thông tin endpoint (không ảnh hưởng đến Telegram)

### **2. Pull data trước khi báo cáo**
- ✅ `/statusads` - Pull data mới từ Facebook trước khi tạo báo cáo
- ✅ `/report` - Pull data mới từ Facebook trước khi tạo báo cáo
- ✅ Hiển thị thời gian pull và số lượng ads

### **3. Thông tin chi tiết**
- ✅ Hiển thị thời gian pull data
- ✅ Hiển thị số ads mới được pull
- ✅ Hiển thị thời gian xử lý

---

## 🚀 CẬP NHẬT TRÊN VPS

### **BƯỚC 1: Pull code mới nhất**

```bash
cd ~/ads-automation
git pull origin main
```

**Nếu có conflict:**
```bash
git stash
git pull origin main
git stash pop
```

### **BƯỚC 2: Restart workers**

```bash
sudo supervisorctl restart ads-automation-worker:*
sleep 2
sudo supervisorctl status
```

**Phải thấy `RUNNING`!**

### **BƯỚC 3: Test bot**

1. **Test `/statusads`:**
   - Gửi `/statusads` trong Telegram
   - Bot sẽ:
     - Pull data mới từ Facebook (có thể mất 10-30 giây)
     - Hiển thị thông tin pull (số ads, thời gian)
     - Tạo báo cáo từ database mới nhất

2. **Test `/report`:**
   - Gửi `/report` trong Telegram
   - Bot sẽ pull data mới trước khi tạo báo cáo

3. **Check logs:**
   ```bash
   sudo tail -f /var/log/ads-automation/worker.out.log
   ```

---

## 📋 KẾT QUẢ MONG ĐỢI

### **`/statusads` sẽ trả về:**
```
📊 **BÁO CÁO TRẠNG THÁI ADS**

**Dữ liệu mới:**
✅ Đã pull 150 ads (25 mới) trong 12.5s
⏰ Pull lúc: 11/12/2025 17:20:30

**Trạng thái Adsets:**
• ✅ Đang bật: `50`
• ⏸️ Đã tắt: `10`
• 📊 Tổng: `60`

**Tổng quan:**
• 📈 Tổng Ads: `150`
• 💰 Tổng Spend: `1,500,000`
• 🎯 Tổng Results: `500`

_Thời gian báo cáo: 11/12/2025 17:20:35_
```

---

## ⚠️ LƯU Ý

1. **Pull data mất thời gian** - Tùy số lượng ads, có thể mất 10-60 giây
2. **Database được cập nhật** - Dữ liệu mới nhất từ Facebook
3. **Thời gian hiển thị** - User biết khi nào data được pull

---

## 🔍 NẾU VẪN BỊ TREO

### **Check worker logs:**
```bash
sudo tail -50 /var/log/ads-automation/worker.err.log
```

### **Check xem có lỗi gì:**
- Facebook API token hết hạn?
- Database connection error?
- Network timeout?

---

**Chạy các bước trên và test bot! 🚀**


