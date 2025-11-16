# 🔧 FIX PERMISSIONS CHO ADSUSER

## 🔍 VẤN ĐỀ

Lỗi "Permission denied" khi truy cập `/home/adsuser/.ssh/`

**Nguyên nhân:** Permissions của `/home/adsuser` không đúng.

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Fix permissions cho /home/adsuser:**

```bash
# Fix ownership cho toàn bộ /home/adsuser
sudo chown -R adsuser:adsuser /home/adsuser

# Fix permissions cho home directory
sudo chmod 755 /home/adsuser

# Verify
ls -ld /home/adsuser
# Nên thấy: drwxr-xr-x adsuser adsuser
```

### **BƯỚC 2: Tạo .ssh directory với quyền đúng:**

```bash
# Tạo .ssh directory
sudo mkdir -p /home/adsuser/.ssh

# Copy authorized_keys
sudo cp /home/ubuntu/.ssh/authorized_keys /home/adsuser/.ssh/authorized_keys

# Fix ownership
sudo chown -R adsuser:adsuser /home/adsuser/.ssh

# Fix permissions (QUAN TRỌNG)
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys
```

### **BƯỚC 3: Verify với sudo:**

```bash
# Verify với sudo
sudo ls -la /home/adsuser/.ssh/
sudo cat /home/adsuser/.ssh/authorized_keys
```

**Kết quả mong đợi:**
```
total 8
drwx------ 2 adsuser adsuser 4096 Nov 11 15:30 .
drwxr-xr-x 3 adsuser adsuser 4096 Nov 11 15:30 ..
-rw------- 1 adsuser adsuser  400 Nov 11 15:30 authorized_keys
```

---

## 🔍 KIỂM TRA USER ADSUSER

### **Check user adsuser có tồn tại không:**

```bash
# Check user
id adsuser
# Nên thấy: uid=... gid=... groups=...

# Check home directory
ls -ld /home/adsuser
# Nên thấy: drwxr-xr-x adsuser adsuser
```

### **Nếu user chưa tồn tại hoặc home directory không có:**

```bash
# Tạo user (nếu chưa có)
sudo adduser adsuser
# Nhập password khi hỏi

# Hoặc fix home directory
sudo mkdir -p /home/adsuser
sudo chown -R adsuser:adsuser /home/adsuser
sudo chmod 755 /home/adsuser
```

---

## ✅ QUICK FIX - TẤT CẢ TRONG MỘT LẦN:

```bash
# Fix toàn bộ permissions cho adsuser
sudo chown -R adsuser:adsuser /home/adsuser
sudo chmod 755 /home/adsuser

# Tạo .ssh directory
sudo mkdir -p /home/adsuser/.ssh
sudo cp /home/ubuntu/.ssh/authorized_keys /home/adsuser/.ssh/authorized_keys

# Fix ownership và permissions
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys

# Verify với sudo
sudo ls -la /home/adsuser/.ssh/
sudo cat /home/adsuser/.ssh/authorized_keys
```

---

## 🧪 TEST LOGIN

### **Sau khi fix:**

1. **Tạo SSH session mới trong MobaXterm:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - ✅ **Use private key:** Chọn file `.pem`

2. **Login** → Nếu thành công, sẽ không hỏi password

---

## 🔍 NẾU VẪN KHÔNG WORK

### **Check SSH logs:**

```bash
# Xem SSH logs khi login
sudo tail -f /var/log/auth.log
# Hoặc
sudo journalctl -u sshd -f
```

**Trong khi đó, thử login từ MobaXterm** → Sẽ thấy log lỗi chi tiết.

### **Verify public key match:**

```bash
# So sánh public key
echo "=== Ubuntu ==="
sudo cat /home/ubuntu/.ssh/authorized_keys

echo "=== Adsuser ==="
sudo cat /home/adsuser/.ssh/authorized_keys

# Phải giống nhau
```

---

**Chạy lệnh Quick Fix ở trên, sau đó verify và thử login lại! 🚀**

