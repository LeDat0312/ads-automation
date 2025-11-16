# 🔐 FIX SSH PASSWORD AUTHENTICATION - CHI TIẾT

## 🔍 KIỂM TRA CẤU HÌNH HIỆN TẠI

### **BƯỚC 1: Check SSH config:**

```bash
# Xem cấu hình hiện tại
sudo grep -E "PasswordAuthentication|PubkeyAuthentication|ChallengeResponseAuthentication" /etc/ssh/sshd_config
```

**Kết quả có thể:**
```
PasswordAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
```

---

## ✅ CÁCH SỬA CHI TIẾT

### **BƯỚC 1: Backup config:**

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
```

### **BƯỚC 2: Edit SSH config:**

```bash
sudo nano /etc/ssh/sshd_config
```

### **BƯỚC 3: Tìm và sửa các dòng sau:**

**Tìm các dòng này (có thể có # ở đầu):**

```bash
#PasswordAuthentication no
#PubkeyAuthentication yes
#ChallengeResponseAuthentication no
```

**Đổi thành (bỏ # và set đúng giá trị):**

```bash
PasswordAuthentication yes
PubkeyAuthentication yes
ChallengeResponseAuthentication yes
```

**Hoặc thêm vào cuối file nếu không có:**

```bash
# Allow password authentication
PasswordAuthentication yes
PubkeyAuthentication yes
ChallengeResponseAuthentication yes
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **BƯỚC 4: Verify config:**

```bash
# Check lại
sudo grep -E "PasswordAuthentication|PubkeyAuthentication" /etc/ssh/sshd_config | grep -v "^#"
```

**Kết quả mong đợi:**
```
PasswordAuthentication yes
PubkeyAuthentication yes
```

### **BƯỚC 5: Test config:**

```bash
# Test SSH config (không restart)
sudo sshd -t
```

**Nếu không có lỗi** → OK

### **BƯỚC 6: Restart SSH:**

```bash
# Restart SSH service
sudo systemctl restart sshd

# Verify SSH đang chạy
sudo systemctl status sshd
```

**Kết quả mong đợi:**
```
Active: active (running)
```

---

## 🔄 GIẢI PHÁP THAY THẾ: COPY SSH KEY

Nếu vẫn không work, dùng SSH key từ ubuntu:

### **BƯỚC 1: Copy SSH key:**

```bash
# Tạo .ssh directory
sudo mkdir -p /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh

# Copy authorized_keys từ ubuntu
sudo cp /home/ubuntu/.ssh/authorized_keys /home/adsuser/.ssh/authorized_keys

# Fix ownership và permissions
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys

# Verify
ls -la /home/adsuser/.ssh/
```

**Kết quả mong đợi:**
```
-rw------- 1 adsuser adsuser ... authorized_keys
```

### **BƯỚC 2: Login MobaXterm với SSH key:**

1. **Tạo SSH session mới:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - ✅ **Use private key:** Chọn file `.pem` từ Lightsail (giống như khi login ubuntu)

2. **Login** → Sẽ không hỏi password

---

## 🧪 TEST PASSWORD AUTHENTICATION

### **Test từ terminal (nếu có SSH client):**

```bash
# Từ máy local
ssh adsuser@your-server-ip
# Nhập password khi hỏi
```

### **Hoặc test từ server:**

```bash
# Test local
ssh adsuser@localhost
# Nhập password
```

---

## 🔧 NẾU VẪN KHÔNG WORK

### **Option 1: Kiểm tra SELinux (nếu có):**

```bash
# Check SELinux
getenforce
# Nếu là "Enforcing", có thể cần:
sudo setsebool -P ssh_password_enabled 1
```

### **Option 2: Check firewall:**

```bash
# Check UFW
sudo ufw status
# Đảm bảo port 22 được allow
sudo ufw allow 22/tcp
```

### **Option 3: Check SSH service logs:**

```bash
# Xem logs
sudo journalctl -u sshd -n 50
# Hoặc
sudo tail -f /var/log/auth.log
```

### **Option 4: Dùng SSH key (nhanh nhất):**

```bash
# Copy key từ ubuntu
sudo cp -r /home/ubuntu/.ssh /home/adsuser/
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys
```

---

## ✅ QUICK FIX - TẤT CẢ TRONG MỘT LẦN:

```bash
# Backup
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Enable password auth
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#*ChallengeResponseAuthentication.*/ChallengeResponseAuthentication yes/' /etc/ssh/sshd_config

# Verify
sudo grep -E "^PasswordAuthentication|^ChallengeResponseAuthentication" /etc/ssh/sshd_config

# Test config
sudo sshd -t

# Restart SSH
sudo systemctl restart sshd

# Verify
sudo systemctl status sshd
```

---

## 🎯 KHUYẾN NGHỊ

**Nếu vẫn không work với password, dùng SSH key (nhanh hơn):**

```bash
# Copy SSH key từ ubuntu
sudo mkdir -p /home/adsuser/.ssh
sudo cp /home/ubuntu/.ssh/authorized_keys /home/adsuser/.ssh/
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys
```

**Sau đó login MobaXterm với:**
- Username: `adsuser`
- ✅ Use private key: Chọn file `.pem` từ Lightsail

---

**Chạy lệnh Quick Fix ở trên, sau đó thử login lại! 🚀**

