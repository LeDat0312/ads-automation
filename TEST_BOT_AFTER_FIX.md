# ✅ TEST BOT SAU KHI FIX

## 🎉 WORKERS ĐÃ CHẠY THÀNH CÔNG!

```
ads-automation-worker:ads-automation-worker_00   RUNNING   pid 419793
ads-automation-worker:ads-automation-worker_01   RUNNING   pid 419794
```

---

## 🧪 TEST BOT

### **BƯỚC 1: Gửi lệnh trong Telegram**

Gửi bất kỳ lệnh nào:
- `/start`
- `/help`
- `/myid`
- `/statusads`

### **BƯỚC 2: Check logs real-time**

```bash
# Check worker output logs
sudo tail -f /var/log/ads-automation/worker.out.log

# Hoặc check error logs
sudo tail -f /var/log/ads-automation/worker.err.log
```

**Phải thấy:**
- Jobs được xử lý
- Messages được gửi
- Không có lỗi

### **BƯỚC 3: Check jobs trong database**

```bash
cd ~/ads-automation
source venv/bin/activate

python -c "
from app.core.database import get_db_session
from app.models.job import Job, JobStatus
db = get_db_session()
jobs = db.query(Job).order_by(Job.id.desc()).limit(5).all()
for job in jobs:
    print(f'Job {job.id}: {job.job_type} - {job.status} - {job.created_at}')
db.close()
"
```

**Phải thấy jobs mới được tạo và xử lý!**

---

## 🔍 NẾU BOT VẪN KHÔNG PHẢN HỒI

### **Check webhook:**

```bash
curl -X POST https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/getWebhookInfo
```

**Phải thấy:**
- `url`: `https://updatemetaads.site/api/telegram/webhook`
- `pending_update_count`: 0 (hoặc số nhỏ)

### **Check API endpoint:**

```bash
curl https://updatemetaads.site/api/telegram/webhook -X POST -H "Content-Type: application/json" -d '{"test": true}'
```

**Phải trả về 200 OK hoặc 400 Bad Request (không phải 500)!**

### **Check API logs:**

```bash
sudo tail -f /var/log/ads-automation/api.out.log
```

---

## ✅ SAU KHI TEST THÀNH CÔNG

### **Commit và push thay đổi lên GitHub:**

```bash
cd ~/ads-automation
git add app/core/database.py
git commit -m "Fix: Remove top-level Job import to resolve circular import"
git push origin main
```

**Hoặc nếu không muốn commit (vì đã xóa dòng):**

```bash
# Pull lại code từ GitHub (có thể sẽ conflict)
git checkout app/core/database.py
git pull origin main
```

---

**Bây giờ hãy test bot và báo lại kết quả! 🚀**


