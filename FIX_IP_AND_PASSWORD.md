# 🔧 FIX IP ADDRESS VÀ PASSWORD

## 🌐 PUBLIC IP VS PRIVATE IP

### **Private IP (172.26.10.102):**
- ✅ Chỉ dùng trong mạng nội bộ (VPS)
- ✅ Dùng cho: `localhost`, `127.0.0.1`, hoặc `172.26.10.102` (trên cùng server)
- ❌ KHÔNG thể truy cập từ internet

### **Public IP (54.179.208.122):**
- ✅ Có thể truy cập từ internet
- ✅ Dùng cho: WEBHOOK_URL (Telegram cần gọi từ internet)
- ✅ Dùng cho: Domain (nếu có)

---

## 📝 CẦN SỬA

### **1. WEBHOOK_URL trong .env:**

```bash
cd ~/ads-automation
nano .env
```

**Tìm dòng:**
```bash
WEBHOOK_URL=https://172.26.10.122/api/telegram/webhook
```

**Thay thành:**
```bash
WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🔐 FIX PASSWORD AUTHENTICATION

### **VẤN ĐỀ:**

Lỗi: "password authentication failed for user adsuser"

**Nguyên nhân:** Password trong .env có thể không đúng hoặc user chưa được set password.

### **BƯỚC 1: Kiểm tra password trong .env:**

```bash
grep DATABASE_URL .env
```

**Phải thấy:**
```
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
```

### **BƯỚC 2: Test password:**

```bash
# Test với password
psql -U adsuser -d ads_automation -h localhost
# Nhập password: @Levandat0312
```

### **BƯỚC 3: Nếu không vào được, reset password:**

```bash
# Reset password cho adsuser
sudo -u postgres psql << EOF
ALTER USER adsuser WITH PASSWORD '@Levandat0312';
\q
EOF
```

### **BƯỚC 4: Test lại:**

```bash
psql -U adsuser -d ads_automation -h localhost
# Nhập password: @Levandat0312
```

### **BƯỚC 5: Nếu vẫn không được, check PostgreSQL config:**

```bash
# Check pg_hba.conf
sudo grep -E "local|host" /etc/postgresql/*/main/pg_hba.conf
```

**Phải thấy:**
```
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

### **BƯỚC 6: Restart PostgreSQL:**

```bash
sudo systemctl restart postgresql
```

---

## ✅ CÁCH KHÁC: DÙNG TRUST (CHỈ CHO LOCALHOST)

### **Nếu muốn không cần password (chỉ cho localhost):**

```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

**Tìm dòng:**
```
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
```

**Đổi thành:**
```
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Reload PostgreSQL:**
```bash
sudo systemctl reload postgresql
```

**Test:**
```bash
psql -U adsuser -d ads_automation -h localhost
# Không cần password
```

---

## 📋 TÓM TẮT - CẦN SỬA

### **1. WEBHOOK_URL trong .env:**
```bash
WEBHOOK_URL=https://54.179.208.122/api/telegram/webhook
```

### **2. Fix password authentication:**
- Reset password: `ALTER USER adsuser WITH PASSWORD '@Levandat0312';`
- Hoặc dùng trust cho localhost

---

## ✅ CHECKLIST

- [ ] Update WEBHOOK_URL với Public IP: `54.179.208.122`
- [ ] Test password: `psql -U adsuser -d ads_automation -h localhost`
- [ ] Reset password nếu cần
- [ ] Test database connection từ Python

---

**Bây giờ hãy sửa WEBHOOK_URL và fix password! 🚀**


