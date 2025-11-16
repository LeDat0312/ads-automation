# 🔍 DEBUG WORKER SPAWN ERROR

## ❌ VẤN ĐỀ

- Bot không phản hồi
- `tail -f worker.out.log` bị treo (không có output mới)
- Workers có lỗi "spawn error"

---

## 🔍 KIỂM TRA

### **BƯỚC 1: Check worker error logs**

```bash
sudo tail -50 /var/log/ads-automation/worker.err.log
```

**Sẽ thấy lỗi chi tiết về spawn error!**

### **BƯỚC 2: Check worker status**

```bash
sudo supervisorctl status
```

**Nếu thấy `BACKOFF` hoặc `FATAL`, workers không chạy được!**

### **BƯỚC 3: Test worker manually**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker import OK')"

# Test chạy worker (sẽ chạy vô hạn, dừng bằng Ctrl+C sau 5 giây)
timeout 5 python -m app.workers.telegram_worker 00 2>&1 || true
```

**Sẽ thấy lỗi cụ thể nếu có!**

### **BƯỚC 4: Check Supervisor config**

```bash
cat /etc/supervisor/conf.d/ads-automation.conf | grep -A 10 "ads-automation-worker"
```

**Phải thấy:**
```ini
command=/home/adsuser/ads-automation/venv/bin/python -m app.workers.telegram_worker %(process_num)02d
```

---

## 🔧 CÁC LỖI THƯỜNG GẶP

### **Lỗi 1: Import error**

Nếu thấy `ImportError`, có thể do:
- Circular import
- Missing dependencies
- Python cache

### **Lỗi 2: Config error**

Nếu thấy `ValidationError`, có thể do:
- `.env` file sai
- Environment variables override

### **Lỗi 3: Database error**

Nếu thấy database error, check database connection.

---

## ✅ SAU KHI FIX

### **Restart workers:**

```bash
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

### **Test bot:**

1. Gửi `/start` trong Telegram
2. Check logs:
   ```bash
   sudo tail -f /var/log/ads-automation/worker.out.log
   ```
3. Phải thấy jobs được xử lý

---

**Bây giờ hãy check worker error logs để xem lỗi cụ thể! 🚀**


