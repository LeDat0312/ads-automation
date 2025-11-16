# 🔐 FIX SSH CONFIG - FINAL

## 🔍 PHÂN TÍCH

Từ output, tôi thấy:
- ✅ `PubkeyAuthentication yes` - OK
- ✅ `PasswordAuthentication yes` - OK
- ✅ `UsePAM yes` - OK
- ⚠️ `KbdInteractiveAuthentication no` - Có thể gây vấn đề

**Vấn đề có thể:**
1. `KbdInteractiveAuthentication no` có thể block password auth
2. SSH service chưa reload đúng
3. User adsuser chưa có password

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Enable KbdInteractiveAuthentication:**

```bash
# Enable KbdInteractiveAuthentication
sudo sed -i 's/^KbdInteractiveAuthentication no/KbdInteractiveAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#KbdInteractiveAuthentication yes/KbdInteractiveAuthentication yes/' /etc/ssh/sshd_config

# Nếu không có, thêm vào
if ! grep -q "^KbdInteractiveAuthentication" /etc/ssh/sshd_config; then
    echo "KbdInteractiveAuthentication yes" | sudo tee -a /etc/ssh/sshd_config
fi

# Verify
sudo grep -E "^KbdInteractiveAuthentication|^PasswordAuthentication|^UsePAM" /etc/ssh/sshd_config | grep -v "^#"
```

**Kết quả mong đợi:**
```
KbdInteractiveAuthentication yes
PasswordAuthentication yes
UsePAM yes
```

### **BƯỚC 2: Test và restart SSH:**

```bash
# Test config
sudo sshd -t

# Nếu OK, restart SSH (force)
sudo systemctl stop sshd
sudo systemctl start sshd

# Verify
sudo systemctl status sshd
```

**Kết quả mong đợi:**
```
Active: active (running)
```

### **BƯỚC 3: Đảm bảo user adsuser có password:**

```bash
# Set password cho adsuser
sudo passwd adsuser
```

**Nhập password mới 2 lần** (ví dụ: `MySecurePass123!`)

### **BƯỚC 4: Verify user adsuser:**

```bash
# Check user
id adsuser

# Check home directory
ls -ld /home/adsuser

# Check user có thể login không
sudo -u adsuser whoami
```

---

## 🧪 TEST LOGIN

### **Sau khi fix:**

1. **Tạo SSH session mới trong MobaXterm:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - **Bỏ chọn** "Use private key"

2. **Login** → Sẽ hỏi password → Nhập password của `adsuser`

3. **Nếu thành công:** Prompt sẽ là `adsuser@ip-172-26-10-102:~$`

---

## 🔍 DEBUG NẾU VẪN KHÔNG WORK

### **Check SSH logs:**

```bash
# Xem SSH logs real-time
sudo tail -f /var/log/auth.log
# Hoặc
sudo journalctl -u sshd -f
```

**Trong khi đó, thử login từ MobaXterm** → Sẽ thấy log lỗi chi tiết.

### **Test local:**

```bash
# Test login từ server
ssh adsuser@localhost
# Nhập password khi hỏi
```

### **Check PAM:**

```bash
# Check PAM config
sudo grep -i "password" /etc/pam.d/sshd
```

---

## ⚡ QUICK FIX - TẤT CẢ TRONG MỘT LẦN:

```bash
# Enable KbdInteractiveAuthentication
sudo sed -i 's/^KbdInteractiveAuthentication no/KbdInteractiveAuthentication yes/' /etc/ssh/sshd_config

# Verify
sudo grep -E "^KbdInteractiveAuthentication|^PasswordAuthentication|^UsePAM" /etc/ssh/sshd_config | grep -v "^#"

# Test config
sudo sshd -t

# Restart SSH
sudo systemctl stop sshd
sudo systemctl start sshd

# Verify
sudo systemctl status sshd

# Set password cho adsuser
sudo passwd adsuser
```

---

## ✅ CHECKLIST

- [ ] Enable `KbdInteractiveAuthentication yes`
- [ ] Verify `PasswordAuthentication yes`
- [ ] Verify `UsePAM yes`
- [ ] Test config: `sudo sshd -t`
- [ ] Restart SSH: `sudo systemctl restart sshd`
- [ ] Set password: `sudo passwd adsuser`
- [ ] Test login với MobaXterm

---

**Chạy lệnh Quick Fix ở trên, sau đó thử login lại! 🚀**

