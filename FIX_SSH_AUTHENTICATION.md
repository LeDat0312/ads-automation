# 🔐 FIX SSH AUTHENTICATION - PASSWORD LOGIN

## 🔍 VẤN ĐỀ

Lỗi: "Server refused our key" và "No supported authentication methods available (server sent: publickey)"

**Nguyên nhân:** Server chỉ cho phép SSH key authentication, không cho phép password.

---

## ✅ GIẢI PHÁP 1: ENABLE PASSWORD AUTHENTICATION (KHUYẾN NGHỊ)

### **BƯỚC 1: Login với ubuntu user (hoặc root):**

Vẫn dùng session hiện tại với `ubuntu` user.

### **BƯỚC 2: Enable password authentication:**

```bash
# Backup config
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Edit SSH config
sudo nano /etc/ssh/sshd_config
```

**Tìm và sửa các dòng:**

```bash
# Tìm dòng này (có thể có # ở đầu)
#PasswordAuthentication no

# Đổi thành:
PasswordAuthentication yes

# Tìm dòng này (nếu có)
#PubkeyAuthentication yes

# Đảm bảo có (hoặc thêm nếu không có):
PubkeyAuthentication yes
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **BƯỚC 3: Restart SSH service:**

```bash
# Test config trước
sudo sshd -t

# Nếu OK, restart SSH
sudo systemctl restart sshd

# Verify
sudo systemctl status sshd
```

### **BƯỚC 4: Test login với adsuser:**

1. **Tạo SSH session mới trong MobaXterm:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - Bỏ chọn "Use private key"

2. **Login** → Nhập password của `adsuser`

---

## ✅ GIẢI PHÁP 2: SETUP SSH KEY CHO ADSUSER

### **BƯỚC 1: Copy SSH key từ ubuntu:**

```bash
# Tạo .ssh directory cho adsuser
sudo mkdir -p /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh

# Copy authorized_keys từ ubuntu
sudo cp /home/ubuntu/.ssh/authorized_keys /home/adsuser/.ssh/
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys
```

### **BƯỚC 2: Login MobaXterm với SSH key:**

1. **Tạo SSH session mới:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - ✅ **Use private key:** Chọn file `.pem` từ Lightsail (giống như khi login ubuntu)

2. **Login** → Sẽ không hỏi password

---

## ✅ GIẢI PHÁP 3: TẠO SSH KEY MỚI CHO ADSUSER

### **BƯỚC 1: Tạo SSH key pair (trên máy local):**

**Windows PowerShell hoặc CMD:**

```powershell
# Tạo SSH key
ssh-keygen -t rsa -b 4096 -C "adsuser@server" -f C:\Users\Foxy\.ssh\adsuser_key

# Sẽ tạo 2 files:
# - C:\Users\Foxy\.ssh\adsuser_key (private key)
# - C:\Users\Foxy\.ssh\adsuser_key.pub (public key)
```

### **BƯỚC 2: Copy public key lên server:**

**Từ máy local:**

```powershell
# Copy public key
type C:\Users\Foxy\.ssh\adsuser_key.pub | ssh ubuntu@your-server-ip "sudo tee -a /home/adsuser/.ssh/authorized_keys"
```

**Hoặc upload file `adsuser_key.pub` qua MobaXterm, rồi:**

```bash
# Trên server (với ubuntu user)
sudo mkdir -p /home/adsuser/.ssh
sudo cat /tmp/adsuser_key.pub >> /home/adsuser/.ssh/authorized_keys
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys
```

### **BƯỚC 3: Login MobaXterm:**

1. **Tạo SSH session:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - ✅ **Use private key:** Chọn `C:\Users\Foxy\.ssh\adsuser_key`

2. **Login** → Sẽ không hỏi password

---

## 🎯 KHUYẾN NGHỊ

**Dùng Giải pháp 1 (Enable password authentication)** vì:
- ✅ Đơn giản nhất
- ✅ Không cần setup SSH key
- ✅ Dễ quản lý

**Sau khi enable password auth, bạn có thể:**
- Login với password
- Hoặc dùng SSH key (nếu muốn)

---

## ⚠️ LƯU Ý BẢO MẬT

Sau khi enable password authentication:
1. **Đảm bảo password mạnh** cho `adsuser`
2. **Có thể disable root login** (nếu muốn):
   ```bash
   # Trong /etc/ssh/sshd_config
   PermitRootLogin no
   ```
3. **Giới hạn login attempts** (nếu cần)

---

## ✅ QUICK FIX (Tất cả trong một lần):

```bash
# Enable password authentication
sudo sed -i 's/#PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Verify
grep PasswordAuthentication /etc/ssh/sshd_config
# Nên thấy: PasswordAuthentication yes

# Restart SSH
sudo systemctl restart sshd

# Verify SSH running
sudo systemctl status sshd
```

---

## 🔍 VERIFY

Sau khi enable password auth:

1. **Tạo SSH session mới trong MobaXterm:**
   - Username: `adsuser`
   - Bỏ chọn "Use private key"
   
2. **Login** → Nhập password

3. **Nếu thành công:** Prompt sẽ là `adsuser@ip-172-26-10-102:~$`

---

**Chạy lệnh enable password authentication ở trên, sau đó thử login lại! 🚀**

