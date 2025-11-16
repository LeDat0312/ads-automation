# 🔧 FIX WORKER JOB TYPES

## ❌ VẤN ĐỀ

Tất cả jobs đều fail ngay lập tức vì worker chỉ xử lý `telegram_command`, không xử lý `send_message`.

**Logs cho thấy:**
- Jobs `send_message` fail ngay
- Jobs `telegram_command` fail ngay
- Worker không có handler cho `send_message`

---

## ✅ ĐÃ SỬA

Đã sửa `process_job()` để xử lý cả 2 loại jobs:
1. ✅ `send_message` - Gửi message đơn giản
2. ✅ `telegram_command` - Xử lý lệnh nặng

---

## 🚀 CẬP NHẬT TRÊN VPS

### **BƯỚC 1: Pull code mới:**

```bash
cd ~/ads-automation
git stash  # Nếu có conflict
git pull origin main
```

### **BƯỚC 2: Xóa Python cache:**

```bash
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

### **BƯỚC 3: Restart workers:**

```bash
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

### **BƯỚC 4: Check worker logs:**

```bash
sudo tail -f /var/log/ads-automation/worker.out.log
```

**Phải thấy:**
```
🚀 Starting Telegram worker: worker-00
🚀 Starting Telegram worker: worker-01
```

### **BƯỚC 5: Test bot:**

1. Gửi `/start` trong Telegram
2. Bot phải phản hồi ngay
3. Check logs để verify jobs được xử lý

---

## ✅ VERIFY

```bash
# Check worker status
sudo supervisorctl status

# Check worker logs
sudo tail -50 /var/log/ads-automation/worker.out.log

# Test bot (gửi /start trong Telegram)
# Phải thấy jobs được xử lý thành công
```

---

**Bây giờ hãy pull code và restart workers! 🚀**


