# ✅ VERIFY SUPERVISOR STATUS

## 🎉 KẾT QUẢ

- ✅ `ads-automation-api: added process group`
- ✅ `ads-automation-worker: added process group`
- ⚠️ `ads-automation-api: ERROR (already started)` - Process đã được start rồi (không sao)

---

## 🔍 KIỂM TRA STATUS

### **BƯỚC 1: Check status:**

```bash
sudo supervisorctl status
```

**Kết quả mong đợi:**
```
ads-automation-api                  RUNNING   pid 12345, uptime 0:00:05
ads-automation-worker:ads-automation-worker_00   RUNNING   pid 12346, uptime 0:00:05
ads-automation-worker:ads-automation-worker_01   RUNNING   pid 12347, uptime 0:00:05
```

### **BƯỚC 2: Nếu có lỗi, restart:**

```bash
# Restart tất cả
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker:*

# Check status lại
sudo supervisorctl status
```

---

## 🧪 TEST API SERVER

### **Test health check:**

```bash
curl http://localhost:8000/health
```

**Kết quả mong đợi:**
```json
{"status":"healthy"}
```

### **Test root:**

```bash
curl http://localhost:8000/
```

### **Test API endpoints:**

```bash
curl http://localhost:8000/api/rules
curl http://localhost:8000/api/dashboard/stats
```

---

## 📋 CHECK LOGS

### **View API logs:**

```bash
tail -f /var/log/ads-automation/api.out.log
```

### **View worker logs:**

```bash
tail -f /var/log/ads-automation/worker.out.log
```

### **View error logs:**

```bash
tail -f /var/log/ads-automation/api.err.log
tail -f /var/log/ads-automation/worker.err.log
```

---

## 🔧 NẾU SERVICE KHÔNG CHẠY

### **Check logs để tìm lỗi:**

```bash
# View logs
sudo tail -50 /var/log/ads-automation/api.err.log
sudo tail -50 /var/log/ads-automation/api.out.log
```

### **Restart service:**

```bash
# Stop
sudo supervisorctl stop ads-automation-api
sudo supervisorctl stop ads-automation-worker:*

# Start
sudo supervisorctl start ads-automation-api
sudo supervisorctl start ads-automation-worker:*

# Check status
sudo supervisorctl status
```

---

## ✅ CHECKLIST

- [ ] Check status: `sudo supervisorctl status`
- [ ] Test API: `curl http://localhost:8000/health`
- [ ] Check logs: `tail -f /var/log/ads-automation/api.out.log`
- [ ] Setup Nginx (bước tiếp theo)
- [ ] Setup Telegram webhook (bước tiếp theo)

---

**Bây giờ hãy check status và test API! 🚀**

