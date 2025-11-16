# 🔐 ENABLE PASSWORD LOGIN CHO SSH

## 🎯 MỤC TIÊU

Enable password authentication để login bằng username + password thay vì SSH key.

---

## ✅ CÁCH ENABLE PASSWORD AUTHENTICATION

### **BƯỚC 1: Backup SSH config:**

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
```

### **BƯỚC 2: Edit SSH config:**

```bash
sudo nano /etc/ssh/sshd_config
```

### **BƯỚC 3: Tìm và sửa các dòng:**

**Tìm các dòng này (có thể có # ở đầu):**

```bash
#PubkeyAuthentication yes
#PasswordAuthentication no
#ChallengeResponseAuthentication no
```

**Đổi thành (bỏ # và set đúng giá trị):**

```bash
PubkeyAuthentication yes
PasswordAuthentication yes
ChallengeResponseAuthentication yes
```

**Hoặc thêm vào cuối file nếu không tìm thấy:**

```bash
# Allow password authentication
PasswordAuthentication yes
PubkeyAuthentication yes
ChallengeResponseAuthentication yes
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## ⚡ QUICK FIX - TỰ ĐỘNG

### **Chạy các lệnh sau:**

```bash
# Backup
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Uncomment và enable PubkeyAuthentication
sudo sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^PubkeyAuthentication no/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Uncomment và enable PasswordAuthentication
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Enable ChallengeResponseAuthentication
sudo sed -i 's/^#ChallengeResponseAuthentication yes/ChallengeResponseAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^ChallengeResponseAuthentication no/ChallengeResponseAuthentication yes/' /etc/ssh/sshd_config

# Nếu không có dòng PasswordAuthentication, thêm vào
if ! grep -q "^PasswordAuthentication" /etc/ssh/sshd_config; then
    echo "" | sudo tee -a /etc/ssh/sshd_config
    echo "# Allow password authentication" | sudo tee -a /etc/ssh/sshd_config
    echo "PasswordAuthentication yes" | sudo tee -a /etc/ssh/sshd_config
fi

# Verify
sudo grep -E "^PasswordAuthentication|^PubkeyAuthentication|^ChallengeResponseAuthentication" /etc/ssh/sshd_config | grep -v "^#"
```

**Kết quả mong đợi:**
```
PubkeyAuthentication yes
PasswordAuthentication yes
ChallengeResponseAuthentication yes
```

### **BƯỚC 4: Test SSH config:**

```bash
# Test config (không restart)
sudo sshd -t
```

**Nếu không có lỗi** → OK

### **BƯỚC 5: Restart SSH service:**

```bash
# Restart SSH
sudo systemctl restart sshd

# Verify SSH đang chạy
sudo systemctl status sshd
```

**Kết quả mong đợi:**
```
Active: active (running)
```

---

## 🔐 ĐẢM BẢO USER ADSUSER CÓ PASSWORD

### **Set password cho adsuser (nếu chưa có):**

```bash
# Set password cho adsuser
sudo passwd adsuser
```

**Nhập password mới 2 lần** (ví dụ: `MySecurePass123!`)

---

## 🧪 TEST LOGIN

### **Sau khi enable password auth:**

1. **Tạo SSH session mới trong MobaXterm:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - **Bỏ chọn** "Use private key" (hoặc không chọn file .pem)

2. **Login** → Sẽ hỏi password → Nhập password của `adsuser`

3. **Nếu thành công:** Prompt sẽ là `adsuser@ip-172-26-10-102:~$`

---

## 🔍 VERIFY CẤU HÌNH

### **Check SSH config:**

```bash
# Check các settings quan trọng
sudo grep -E "^PasswordAuthentication|^PubkeyAuthentication|^ChallengeResponseAuthentication" /etc/ssh/sshd_config | grep -v "^#"
```

**Phải thấy:**
```
PasswordAuthentication yes
PubkeyAuthentication yes
ChallengeResponseAuthentication yes
```

### **Check PAM (nếu cần):**

```bash
# Check UsePAM
sudo grep -i "UsePAM" /etc/ssh/sshd_config
# Nên thấy: UsePAM yes
```

---

## ⚠️ LƯU Ý BẢO MẬT

Sau khi enable password authentication:

1. **Đảm bảo password mạnh:**
   - Tối thiểu 12 ký tự
   - Có chữ hoa, chữ thường, số, ký tự đặc biệt

2. **Có thể disable root login (nếu muốn):**
   ```bash
   # Trong /etc/ssh/sshd_config
   PermitRootLogin no
   ```

3. **Giới hạn login attempts (nếu cần):**
   ```bash
   # Install fail2ban
   sudo apt install fail2ban -y
   ```

---

## 🔧 NẾU VẪN KHÔNG WORK

### **Check SSH logs:**

```bash
# Xem SSH logs
sudo tail -f /var/log/auth.log
# Hoặc
sudo journalctl -u sshd -f
```

**Trong khi đó, thử login từ MobaXterm** → Sẽ thấy log lỗi chi tiết.

### **Check firewall:**

```bash
# Check UFW
sudo ufw status
# Đảm bảo port 22 được allow
sudo ufw allow 22/tcp
```

### **Test local:**

```bash
# Test login từ server
ssh adsuser@localhost
# Nhập password khi hỏi
```

---

## ✅ CHECKLIST

- [ ] Backup SSH config
- [ ] Enable `PasswordAuthentication yes`
- [ ] Enable `PubkeyAuthentication yes`
- [ ] Enable `ChallengeResponseAuthentication yes`
- [ ] Test config: `sudo sshd -t`
- [ ] Restart SSH: `sudo systemctl restart sshd`
- [ ] Set password cho adsuser: `sudo passwd adsuser`
- [ ] Test login với MobaXterm (bỏ chọn "Use private key")

---

**Chạy các lệnh Quick Fix ở trên, sau đó set password cho adsuser và thử login lại! 🚀**

