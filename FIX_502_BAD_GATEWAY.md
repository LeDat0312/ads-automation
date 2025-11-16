# 🔧 FIX 502 BAD GATEWAY

## ❌ VẤN ĐỀ

```
502 Bad Gateway
```

**Nguyên nhân:** Nginx không thể kết nối với FastAPI backend (port 8000).

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Check API server có đang chạy không**

```bash
sudo supervisorctl status
```

**Phải thấy:**
```
ads-automation-api                  RUNNING   pid ..., uptime ...
```

**Nếu thấy `STOPPED` hoặc `FATAL`, cần restart!**

### **BƯỚC 2: Check port 8000 có đang listen không**

```bash
sudo netstat -tlnp | grep 8000
# Hoặc
sudo ss -tlnp | grep 8000
```

**Phải thấy:**
```
tcp  0  0  0.0.0.0:8000  0.0.0.0:*  LISTEN  <pid>/python
```

**Nếu không có kết quả, API không chạy!**

### **BƯỚC 3: Test API trực tiếp (bypass Nginx)**

```bash
curl http://localhost:8000/health
```

**Kết quả mong đợi:**
```json
{"status":"healthy"}
```

**Nếu lỗi, API có vấn đề!**

### **BƯỚC 4: Restart API**

```bash
# Restart API
sudo supervisorctl restart ads-automation-api

# Check status
sudo supervisorctl status

# Check logs
sudo tail -50 /var/log/ads-automation/api.err.log
sudo tail -50 /var/log/ads-automation/api.out.log
```

### **BƯỚC 5: Test lại HTTPS**

```bash
# Test health check
curl https://updatemetaads.site/health

# Kết quả mong đợi:
# {"status":"healthy"}
```

---

## 🔍 NẾU VẪN LỖI

### **Check Nginx error logs:**

```bash
sudo tail -50 /var/log/nginx/updatemetaads.error.log
```

**Sẽ thấy lỗi chi tiết!**

### **Check API logs:**

```bash
sudo tail -50 /var/log/ads-automation/api.err.log
```

**Sẽ thấy lỗi nếu API có vấn đề!**

### **Check Nginx config:**

```bash
sudo nginx -t
```

**Phải thấy:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

## 📋 CHECKLIST

- [ ] Check API status: `sudo supervisorctl status`
- [ ] Check port 8000: `sudo netstat -tlnp | grep 8000`
- [ ] Test API trực tiếp: `curl http://localhost:8000/health`
- [ ] Restart API: `sudo supervisorctl restart ads-automation-api`
- [ ] Test HTTPS: `curl https://updatemetaads.site/health`
- [ ] Check logs nếu vẫn lỗi

---

**Bây giờ hãy check API status và restart nếu cần! 🚀**


