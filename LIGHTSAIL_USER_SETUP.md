# 🔐 AWS LIGHTSAIL - SETUP USER VÀ PASSWORD

## 🎯 MỤC TIÊU

1. ✅ Sử dụng quyền root
2. ✅ Tạo user mới với password
3. ✅ Setup SSH với password (hoặc giữ key pem)
4. ✅ Security best practices

---

## 📋 BƯỚC 1: CHUYỂN SANG ROOT USER

### **1.1. Từ user ubuntu (mặc định):**

```bash
# Chuyển sang root
sudo su -

# Hoặc
sudo -i

# Verify bạn đang là root
whoami
# Kết quả: root

# Kiểm tra thư mục hiện tại
pwd
# Kết quả: /root
```

### **1.2. Nếu cần set password cho root:**

```bash
# Set password cho root
sudo passwd root

# Nhập password mới (sẽ không hiện khi gõ)
# Nhập lại password để confirm
```

**⚠️ LƯU Ý:** Không nên dùng root trực tiếp cho security. Tốt hơn là tạo user mới với sudo privileges.

---

## 📋 BƯỚC 2: TẠO USER MỚI VỚI PASSWORD

### **2.1. Tạo user mới:**

```bash
# Tạo user mới (ví dụ: fbads)
adduser fbads

# Hoặc với thông tin đầy đủ
adduser --gecos "Facebook Ads Admin" fbads

# Hệ thống sẽ hỏi:
# - Password: Nhập password mới
# - Retype password: Nhập lại password
# - Full name: (có thể để trống)
# - Room number: (có thể để trống)
# - Work phone: (có thể để trống)
# - Home phone: (có thể để trống)
# - Other: (có thể để trống)
```

### **2.2. Thêm user vào sudo group:**

```bash
# Thêm user vào sudo group
usermod -aG sudo fbads

# Verify
groups fbads
# Kết quả: fbads : fbads sudo
```

### **2.3. Test user mới:**

```bash
# Switch sang user mới
su - fbads

# Test sudo
sudo whoami
# Kết quả: root

# Test password
sudo ls /root
# Sẽ hỏi password, nhập password của user fbads
```

---

## 📋 BƯỚC 3: SETUP SSH VỚI PASSWORD

### **3.1. Enable password authentication (trong SSH config):**

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Tìm và sửa các dòng sau:
# PasswordAuthentication yes        # Bỏ comment và set = yes
# PermitRootLogin no                # Không cho phép root login (security)
# PubkeyAuthentication yes          # Vẫn cho phép dùng key
# AuthorizedKeysFile .ssh/authorized_keys

# Save và exit (Ctrl+X, Y, Enter)
```

### **3.2. Restart SSH service:**

```bash
# Restart SSH
sudo systemctl restart sshd

# Hoặc
sudo service sshd restart

# Check status
sudo systemctl status sshd
```

### **3.3. Test SSH với password:**

**Trong MobaXterm:**
1. Tạo session mới
2. Chọn "SSH"
3. Remote host: `your-lightsail-ip`
4. Username: `fbads`
5. **Bỏ chọn "Use private key"** (nếu muốn dùng password)
6. Click "OK"
7. Nhập password khi được hỏi

---

## 📋 BƯỚC 4: SETUP SSH KEY CHO USER MỚI (Optional)

### **4.1. Tạo SSH key trên máy local (Windows với MobaXterm):**

**Option 1: Dùng MobaXterm built-in:**
1. Mở MobaXterm
2. Tools → MobaKeyGen
3. Generate key
4. Save private key và public key

**Option 2: Dùng Git Bash hoặc WSL:**
```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Chọn location: ~/.ssh/id_rsa
# Nhập passphrase (optional)
```

### **4.2. Copy public key lên VPS:**

```bash
# Trên VPS, tạo .ssh directory cho user mới
sudo mkdir -p /home/fbads/.ssh
sudo chmod 700 /home/fbads/.ssh

# Copy public key từ máy local
# Trên máy local (MobaXterm terminal):
cat ~/.ssh/id_rsa.pub
# Copy toàn bộ nội dung

# Trên VPS:
sudo nano /home/fbads/.ssh/authorized_keys
# Paste public key vào
# Save và exit

# Set permissions
sudo chown -R fbads:fbads /home/fbads/.ssh
sudo chmod 600 /home/fbads/.ssh/authorized_keys
```

### **4.3. Test SSH với key:**

**Trong MobaXterm:**
1. Tạo session mới
2. Chọn "SSH"
3. Remote host: `your-lightsail-ip`
4. Username: `fbads`
5. **Chọn "Use private key"** và chọn file private key
6. Click "OK"
7. Sẽ đăng nhập không cần password

---

## 📋 BƯỚC 5: DISABLE ROOT LOGIN (Security)

### **5.1. Disable root login:**

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Tìm và sửa:
# PermitRootLogin no                # Không cho phép root login
# PasswordAuthentication yes        # Cho phép password (nếu cần)
# PubkeyAuthentication yes          # Cho phép key

# Save và exit
```

### **5.2. Restart SSH:**

```bash
# Restart SSH
sudo systemctl restart sshd

# Test (sẽ không thể login bằng root)
# ssh root@your-ip  # Sẽ bị từ chối
```

---

## 📋 BƯỚC 6: SETUP SUDO KHÔNG CẦN PASSWORD (Optional)

### **6.1. Setup sudo không cần password:**

```bash
# Edit sudoers file
sudo visudo

# Thêm dòng sau (thay fbads bằng username của bạn):
fbads ALL=(ALL) NOPASSWD: ALL

# Hoặc chỉ cho phép một số commands cụ thể:
# fbads ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/systemctl

# Save và exit (Ctrl+X, Y, Enter)
```

### **6.2. Test:**

```bash
# Switch sang user mới
su - fbads

# Test sudo (không cần password)
sudo whoami
# Kết quả: root (không hỏi password)
```

**⚠️ LƯU Ý:** Chỉ làm điều này nếu bạn chắc chắn về security. Tốt hơn là giữ password để bảo mật hơn.

---

## 📋 BƯỚC 7: SETUP FIREWALL

### **7.1. Setup UFW (Uncomplicated Firewall):**

```bash
# Install UFW
sudo apt update
sudo apt install ufw -y

# Allow SSH (quan trọng!)
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### **7.2. Setup Lightsail Firewall (trong Console):**

1. Vào AWS Lightsail Console
2. Chọn instance của bạn
3. Click "Networking" tab
4. Add rules:
   - **SSH (22)** - từ IP của bạn (hoặc từ mọi nơi nếu cần)
   - **HTTP (80)** - từ mọi nơi
   - **HTTPS (443)** - từ mọi nơi

---

## 📋 BƯỚC 8: TEST VÀ VERIFY

### **8.1. Test user mới:**

```bash
# Login với user mới
ssh fbads@your-lightsail-ip

# Hoặc với password
ssh fbads@your-lightsail-ip
# Nhập password

# Test sudo
sudo whoami
# Kết quả: root

# Test các commands
sudo apt update
sudo systemctl status sshd
```

### **8.2. Verify security:**

```bash
# Check users
cat /etc/passwd | grep fbads

# Check sudo groups
groups fbads

# Check SSH config
sudo cat /etc/ssh/sshd_config | grep -E "PasswordAuthentication|PermitRootLogin|PubkeyAuthentication"

# Check firewall
sudo ufw status
```

---

## 🔒 SECURITY BEST PRACTICES

### **1. Không dùng root trực tiếp:**
- ✅ Tạo user mới với sudo privileges
- ✅ Disable root login
- ✅ Dùng user thường để làm việc hàng ngày

### **2. Strong password:**
- ✅ Password dài ít nhất 12 ký tự
- ✅ Có chữ hoa, chữ thường, số, ký tự đặc biệt
- ✅ Không dùng password dễ đoán

### **3. SSH Key vs Password:**
- ✅ **SSH Key:** An toàn hơn (khuyến nghị)
- ⚠️ **Password:** Dễ dùng hơn nhưng kém an toàn
- 💡 **Kết hợp:** Dùng cả hai (key + password)

### **4. Firewall:**
- ✅ Chỉ mở ports cần thiết
- ✅ SSH chỉ từ IP của bạn (nếu có thể)
- ✅ HTTP/HTTPS từ mọi nơi

### **5. Fail2Ban:**
```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Start Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

# Check status
sudo systemctl status fail2ban
```

---

## 📝 TÓM TẮT CÁC LỆNH

### **Tạo user mới:**
```bash
# Tạo user
sudo adduser fbads

# Thêm vào sudo group
sudo usermod -aG sudo fbads

# Test
su - fbads
sudo whoami
```

### **Setup SSH với password:**
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication yes
# PermitRootLogin no

# Restart SSH
sudo systemctl restart sshd
```

### **Setup SSH key:**
```bash
# Tạo .ssh directory
sudo mkdir -p /home/fbads/.ssh
sudo chmod 700 /home/fbads/.ssh

# Copy public key
sudo nano /home/fbads/.ssh/authorized_keys
# Paste public key

# Set permissions
sudo chown -R fbads:fbads /home/fbads/.ssh
sudo chmod 600 /home/fbads/.ssh/authorized_keys
```

### **Setup firewall:**
```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable
sudo ufw enable
```

---

## 🎯 KẾT LUẬN

### **✅ ĐÃ HOÀN THÀNH:**
1. ✅ Chuyển sang root user
2. ✅ Tạo user mới với password
3. ✅ Setup SSH với password
4. ✅ Setup SSH key (optional)
5. ✅ Setup firewall
6. ✅ Security best practices

### **🔒 SECURITY:**
- ✅ Không dùng root trực tiếp
- ✅ Strong password
- ✅ SSH key (khuyến nghị)
- ✅ Firewall enabled
- ✅ Fail2Ban (optional)

### **📋 NEXT STEPS:**
1. Test login với user mới
2. Setup Python, PostgreSQL, Docker
3. Deploy ứng dụng
4. Monitor và maintain

---

**Chúc bạn setup thành công! 🚀**

