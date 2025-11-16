# 🔧 FIX TELEGRAM WEBHOOK 500 ERROR

## ❌ VẤN ĐỀ

```
INFO: 91.108.5.135:0 - "POST /api/telegram/webhook HTTP/1.1" 500 Internal Server Error
```

**Nguyên nhân:** Có lỗi khi xử lý request từ Telegram webhook.

---

## 🔍 KIỂM TRA

### **BƯỚC 1: Check error logs**

```bash
sudo tail -50 /var/log/ads-automation/api.err.log
```

**Sẽ thấy lỗi chi tiết!**

### **BƯỚC 2: Check error logs với traceback**

```bash
sudo tail -100 /var/log/ads-automation/api.err.log | grep -A 20 "Traceback"
```

---

## 🔧 CÁC LỖI THƯỜNG GẶP

### **Lỗi 1: Import error**

Nếu thấy `ImportError`, có thể thiếu dependencies hoặc import sai.

### **Lỗi 2: Database connection error**

Nếu thấy database error, check database connection.

### **Lỗi 3: Config error**

Nếu thấy config error, check `.env` file.

### **Lỗi 4: Command processor error**

Nếu thấy lỗi trong command processor, có thể do logic xử lý command.

---

## ✅ SAU KHI FIX

### **Test lại Telegram bot:**

1. Gửi `/start` trong Telegram
2. Check logs:
   ```bash
   sudo tail -f /var/log/ads-automation/api.out.log
   ```
3. Phải thấy `200 OK` thay vì `500 Internal Server Error`

---

**Bây giờ hãy check error logs để xem lỗi cụ thể! 🚀**


