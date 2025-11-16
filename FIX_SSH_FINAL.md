# 🔐 FIX SSH - GIẢI PHÁP CUỐI CÙNG

## 🔍 KIỂM TRA LẠI

### **BƯỚC 1: Check SSH config đã được sửa chưa:**

```bash
# Check các dòng quan trọng
sudo grep -E "^PasswordAuthentication|^PubkeyAuthentication" /etc/ssh/sshd_config
```

**Nếu vẫn thấy `#` ở đầu** → Chưa được uncomment

### **BƯỚC 2: Sửa lại đúng cách:**

```bash
# Backup
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Uncomment và set đúng giá trị
sudo sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Nếu không có dòng PasswordAuthentication, thêm vào
if ! grep -q "^PasswordAuthentication" /etc/ssh/sshd_config; then
    echo "PasswordAuthentication yes" | sudo tee -a /etc/ssh/sshd_config
fi

# Verify
sudo grep -E "^PasswordAuthentication|^PubkeyAuthentication" /etc/ssh/sshd_config
```

**Kết quả phải thấy (KHÔNG có # ở đầu):**
```
PubkeyAuthentication yes
PasswordAuthentication yes
```

### **BƯỚC 3: Restart SSH:**

```bash
# Test config
sudo sshd -t

# Nếu OK, restart
sudo systemctl restart sshd

# Verify
sudo systemctl status sshd
```

---

## 🚀 GIẢI PHÁP NHANH NHẤT: COPY SSH KEY

Nếu vẫn không work, dùng SSH key (chắc chắn work):

### **BƯỚC 1: Copy SSH key từ ubuntu:**

```bash
# Tạo .ssh directory
sudo mkdir -p /home/adsuser/.ssh

# Copy authorized_keys
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
total 8
drwx------ 2 adsuser adsuser 4096 Nov 11 15:30 .
drwxr-xr-x 3 adsuser adsuser 4096 Nov 11 15:30 ..
-rw------- 1 adsuser adsuser  400 Nov 11 15:30 authorized_keys
```

### **BƯỚC 2: Login MobaXterm với SSH key:**

1. **Tạo SSH session mới:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - ✅ **Use private key:** Chọn file `.pem` từ Lightsail
     - File này thường ở: `C:\Users\Foxy\Downloads\` hoặc nơi bạn đã download từ Lightsail
     - Tên file thường là: `LightsailDefaultKey-ap-southeast-1.pem` hoặc tương tự

2. **Login** → Sẽ không hỏi password, login trực tiếp

---

## 🔍 TÌM FILE .PEM

### **Trên Windows:**

1. **Mở File Explorer**
2. **Search:** `*.pem` trong Downloads
3. **Hoặc check Lightsail console:**
   - Vào Lightsail → Account → SSH keys
   - Download key nếu chưa có

### **Hoặc tạo SSH key mới:**

```bash
# Trên server (với ubuntu user)
# Tạo SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/adsuser_key -N ""

# Copy public key
cat ~/.ssh/adsuser_key.pub | sudo tee -a /home/adsuser/.ssh/authorized_keys
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys

# Download private key về máy local
# (Copy nội dung ~/.ssh/adsuser_key và lưu thành file .pem)
```

---

## ✅ KHUYẾN NGHỊ

**Dùng SSH key (copy từ ubuntu)** vì:
- ✅ Chắc chắn work
- ✅ Không cần enable password auth
- ✅ Bảo mật hơn
- ✅ Nhanh hơn

**Sau khi copy SSH key:**
1. Tìm file `.pem` từ Lightsail
2. Login MobaXterm với:
   - Username: `adsuser`
   - ✅ Use private key: Chọn file `.pem`

---

## 📝 TÓM TẮT

**Option 1: Copy SSH key (KHUYẾN NGHỊ)**
```bash
sudo mkdir -p /home/adsuser/.ssh
sudo cp /home/ubuntu/.ssh/authorized_keys /home/adsuser/.ssh/
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys
```

**Option 2: Enable password auth (nếu muốn)**
```bash
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

---

**Chạy lệnh copy SSH key ở trên, sau đó login MobaXterm với SSH key! 🚀**

