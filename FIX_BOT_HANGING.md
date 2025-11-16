# 🔧 FIX BOT BỊ TREO

## ❌ VẤN ĐỀ

Bot hiển thị "Đang xử lý..." nhưng không phản hồi.

**Nguyên nhân có thể:**
- Workers không xử lý được jobs
- Jobs bị stuck trong queue
- Command processor có lỗi
- Workers không chạy đúng

---

## 🔍 KIỂM TRA

### **BƯỚC 1: Check worker logs**

```bash
sudo tail -50 /var/log/ads-automation/worker.out.log
sudo tail -50 /var/log/ads-automation/worker.err.log
```

**Sẽ thấy lỗi nếu workers có vấn đề!**

### **BƯỚC 2: Check worker status**

```bash
sudo supervisorctl status
```

**Phải thấy workers đang RUNNING!**

### **BƯỚC 3: Check jobs trong database**

```bash
cd ~/ads-automation
source venv/bin/activate

python -c "
from app.services.job_queue import JobQueue
from app.models.job import JobStatus
queue = JobQueue()
pending = queue.db.query(queue.db.query.__self__.Job).filter(
    queue.db.query.__self__.Job.status.in_([JobStatus.PENDING, JobStatus.PROCESSING])
).all()
print(f'Pending jobs: {len(pending)}')
for job in pending[:5]:
    print(f'  - Job {job.id}: {job.job_type}, status: {job.status}, created: {job.created_at}')
"
```

**Hoặc đơn giản hơn:**

```bash
psql -U adsuser -d ads_automation -h localhost -c "SELECT id, job_type, status, created_at FROM jobs WHERE status IN ('pending', 'processing') ORDER BY created_at DESC LIMIT 10;"
```

---

## 🔧 CÁCH SỬA

### **Option 1: Restart workers**

```bash
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

### **Option 2: Check và fix jobs bị stuck**

```bash
# Nếu có jobs bị stuck, reset chúng
psql -U adsuser -d ads_automation -h localhost -c "UPDATE jobs SET status = 'retry' WHERE status = 'processing' AND created_at < NOW() - INTERVAL '10 minutes';"
```

### **Option 3: Test worker manually**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test worker import
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker OK')"

# Test chạy worker (sẽ chạy vô hạn, dừng bằng Ctrl+C sau 5 giây)
timeout 5 python -m app.workers.telegram_worker 00 2>&1 || true
```

---

## ✅ VERIFY

```bash
# Check worker status
sudo supervisorctl status

# Check worker logs
sudo tail -f /var/log/ads-automation/worker.out.log

# Test bot (gửi /start trong Telegram)
# Phải thấy worker xử lý job trong logs
```

---

**Bây giờ hãy check worker logs và status! 🚀**


