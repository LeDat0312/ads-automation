# 🔐 HƯỚNG DẪN SETUP DATABASE PASSWORD

## 📝 GIẢI THÍCH

`'your_secure_password'` là **password cho PostgreSQL user `adsuser`**.

Bạn cần:
1. **Tạo một password mạnh** (tối thiểu 12 ký tự)
2. **Thay thế** `'your_secure_password'` bằng password của bạn
3. **Ghi nhớ** password này để điền vào `.env` file

---

## 🔑 CÁCH TẠO PASSWORD

### **Option 1: Tạo password ngẫu nhiên (Khuyến nghị)**

```bash
# Tạo password ngẫu nhiên 32 ký tự
openssl rand -base64 24

# Hoặc
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

**Ví dụ output:**
```
aB3xY9mK2pL8nQ5rT7vW1zC4dF6gH0j
```

### **Option 2: Tự tạo password**

**Yêu cầu:**
- Tối thiểu 12 ký tự
- Có chữ hoa, chữ thường, số, ký tự đặc biệt
- Không dùng thông tin cá nhân

**Ví dụ:**
```
AdsAuto2024!Secure#Pass
MyAds2024@Singapore$DB
```

---

## 🚀 CÁCH THỰC HIỆN

### **BƯỚC 1: Tạo password**

```bash
# Tạo password ngẫu nhiên
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

**Copy password vừa tạo** (ví dụ: `aB3xY9mK2pL8nQ5rT7vW1zC4dF6gH0j`)

### **BƯỚC 2: Tạo database với password**

```bash
# Thay 'aB3xY9mK2pL8nQ5rT7vW1zC4dF6gH0j' bằng password bạn vừa tạo
sudo -u postgres psql << EOF
CREATE DATABASE ads_automation;
CREATE USER adsuser WITH PASSWORD 'aB3xY9mK2pL8nQ5rT7vW1zC4dF6gH0j';
GRANT ALL PRIVILEGES ON DATABASE ads_automation TO adsuser;
ALTER USER adsuser CREATEDB;
\q
EOF
```

**Lưu ý:** 
- Thay `'aB3xY9mK2pL8nQ5rT7vW1zC4dF6gH0j'` bằng password thực tế của bạn
- Giữ nguyên dấu nháy đơn `'...'`

### **BƯỚC 3: Test connection**

```bash
# Test kết nối (sẽ hỏi password)
psql -U adsuser -d ads_automation -h localhost
# Nhập password bạn vừa tạo
# Nếu vào được psql prompt → OK
# Thoát: \q
```

### **BƯỚC 4: Update .env file**

```bash
cd ~/ads-automation
nano .env
```

**Tìm dòng:**
```bash
DATABASE_URL=postgresql://adsuser:your_secure_password@localhost:5432/ads_automation
```

**Thay thành:**
```bash
DATABASE_URL=postgresql://adsuser:aB3xY9mK2pL8nQ5rT7vW1zC4dF6gH0j@localhost:5432/ads_automation
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 📋 VÍ DỤ HOÀN CHỈNH

### **1. Tạo password:**

```bash
adsuser@ip-172-26-10-102:~$ python3 -c "import secrets; print(secrets.token_urlsafe(24))"
MySecurePass2024!XyZ9aB3c
```

### **2. Tạo database:**

```bash
adsuser@ip-172-26-10-102:~$ sudo -u postgres psql << EOF
> CREATE DATABASE ads_automation;
> CREATE USER adsuser WITH PASSWORD 'MySecurePass2024!XyZ9aB3c';
> GRANT ALL PRIVILEGES ON DATABASE ads_automation TO adsuser;
> ALTER USER adsuser CREATEDB;
> \q
> EOF
CREATE DATABASE
CREATE ROLE
GRANT
ALTER ROLE
```

### **3. Test:**

```bash
adsuser@ip-172-26-10-102:~$ psql -U adsuser -d ads_automation -h localhost
Password: MySecurePass2024!XyZ9aB3c
psql (14.x)
Type "help" for help.

ads_automation=> \q
```

### **4. Update .env:**

```bash
DATABASE_URL=postgresql://adsuser:MySecurePass2024!XyZ9aB3c@localhost:5432/ads_automation
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

1. **Ghi nhớ password:** Bạn sẽ cần password này để:
   - Kết nối database
   - Điền vào `.env` file
   - Sử dụng trong code

2. **Bảo mật:**
   - Không share password
   - Không commit `.env` vào Git
   - Chỉ lưu ở nơi an toàn

3. **Format DATABASE_URL:**
   ```
   postgresql://username:password@host:port/database
   ```
   - Nếu password có ký tự đặc biệt, có thể cần URL encode

---

## 🔧 NẾU QUÊN PASSWORD

```bash
# Reset password
sudo -u postgres psql << EOF
ALTER USER adsuser WITH PASSWORD 'new_password_here';
\q
EOF

# Update .env
nano ~/ads-automation/.env
# Update DATABASE_URL với password mới
```

---

## ✅ CHECKLIST

- [ ] Tạo password mạnh
- [ ] Tạo database với password
- [ ] Test connection thành công
- [ ] Update `.env` file với password
- [ ] Test lại với `python scripts/init_db.py`

---

**Bây giờ bạn có thể chạy lệnh tạo database với password của bạn! 🚀**

