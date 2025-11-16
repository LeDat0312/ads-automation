# 🔐 FIX SSH KEY - KIỂM TRA VÀ SỬA

## 🔍 VẤN ĐỀ

Cả `adsuser` và `ubuntu` đều không login được với file `.pem`.

**Nguyên nhân có thể:**
1. SSH key chưa được copy đúng
2. Permissions không đúng
3. Public key không match với private key

---

## ✅ KIỂM TRA VÀ SỬA

### **BƯỚC 1: Kiểm tra ubuntu user (để đảm bảo ubuntu vẫn login được):**

```bash
# Check .ssh của ubuntu
ls -la /home/ubuntu/.ssh/

# Check authorized_keys
cat /home/ubuntu/.ssh/authorized_keys
```

### **BƯỚC 2: Kiểm tra adsuser:**

```bash
# Check .ssh của adsuser
ls -la /home/adsuser/.ssh/

# Check authorized_keys (nếu có)
cat /home/adsuser/.ssh/authorized_keys 2>/dev/null || echo "File not exists"
```

### **BƯỚC 3: Copy SSH key đúng cách:**

```bash
# Đảm bảo .ssh directory tồn tại
sudo mkdir -p /home/adsuser/.ssh

# Copy authorized_keys từ ubuntu
sudo cp /home/ubuntu/.ssh/authorized_keys /home/adsuser/.ssh/authorized_keys

# Fix ownership
sudo chown -R adsuser:adsuser /home/adsuser/.ssh

# Fix permissions (QUAN TRỌNG)
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys

# Verify
ls -la /home/adsuser/.ssh/
```

**Kết quả mong đợi:**
```
total 8
drwx------ 2 adsuser adsuser 4096 Nov 11 15:30 .
drwxr-xr-x 3 adsuser adsuser 4096 Nov 11 15:30 ..
-rw------- 1 adsuser adsuser  400 Nov 11 15:30 authorized_keys
```

### **BƯỚC 4: Verify public key:**

```bash
# So sánh public key giữa ubuntu và adsuser
echo "=== Ubuntu ==="
cat /home/ubuntu/.ssh/authorized_keys

echo "=== Adsuser ==="
cat /home/adsuser/.ssh/authorized_keys

# Phải giống nhau
```

---

## 🔧 NẾU VẪN KHÔNG WORK

### **Option 1: Tạo SSH key mới cho adsuser:**

```bash
# Tạo SSH key pair trên server
sudo -u adsuser ssh-keygen -t rsa -b 4096 -f /home/adsuser/.ssh/id_rsa -N ""

# Copy public key vào authorized_keys
sudo -u adsuser cat /home/adsuser/.ssh/id_rsa.pub >> /home/adsuser/.ssh/authorized_keys

# Fix permissions
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys
sudo chmod 600 /home/adsuser/.ssh/id_rsa
sudo chmod 644 /home/adsuser/.ssh/id_rsa.pub

# Download private key về máy local
sudo cat /home/adsuser/.ssh/id_rsa
# Copy output này và lưu thành file adsuser_key.pem trên máy local
```

**Sau đó dùng file `adsuser_key.pem` mới này để login.**

### **Option 2: Verify file .pem có đúng không:**

**Trên máy local (Windows PowerShell):**

```powershell
# Check file .pem
Get-Content "C:\path\to\your\key.pem" | Select-Object -First 5

# Nên thấy:
# -----BEGIN RSA PRIVATE KEY-----
# hoặc
# -----BEGIN OPENSSH PRIVATE KEY-----
```

### **Option 3: Extract public key từ .pem:**

**Trên máy local (nếu có OpenSSH):**

```powershell
# Extract public key từ private key
ssh-keygen -y -f "C:\path\to\your\key.pem" > public_key.pub

# Copy nội dung public_key.pub
Get-Content public_key.pub
```

**Trên server:**

```bash
# Thêm public key vào authorized_keys
sudo -u adsuser bash -c "echo 'PASTE_PUBLIC_KEY_HERE' >> /home/adsuser/.ssh/authorized_keys"
sudo chmod 600 /home/adsuser/.ssh/authorized_keys
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

## 🔍 DEBUG CHI TIẾT

### **Check SSH logs:**

```bash
# Xem SSH logs
sudo tail -f /var/log/auth.log
# Hoặc
sudo journalctl -u sshd -f
```

**Trong khi đó, thử login từ MobaXterm** → Sẽ thấy log lỗi chi tiết.

### **Check SSH config:**

```bash
# Check config
sudo sshd -T | grep -E "authorizedkeysfile|pubkeyauthentication"
```

---

## ✅ QUICK FIX - TẤT CẢ TRONG MỘT LẦN:

```bash
# Fix adsuser SSH
sudo mkdir -p /home/adsuser/.ssh
sudo cp /home/ubuntu/.ssh/authorized_keys /home/adsuser/.ssh/authorized_keys
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys

# Verify
ls -la /home/adsuser/.ssh/
cat /home/adsuser/.ssh/authorized_keys

# Test từ server
sudo -u adsuser ssh adsuser@localhost
# Nếu hỏi password → OK (có thể login)
```

---

## 🎯 KHUYẾN NGHỊ

**Nếu vẫn không work, thử:**

1. **Login với ubuntu user trước** (để đảm bảo file .pem đúng)
2. **Sau đó copy key sang adsuser**
3. **Hoặc tạo SSH key mới cho adsuser**

---

**Chạy lệnh Quick Fix ở trên, sau đó verify và thử login lại! 🚀**

