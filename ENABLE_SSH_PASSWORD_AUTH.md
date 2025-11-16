# 🔐 ENABLE SSH PASSWORD AUTHENTICATION

## 🔍 PHÂN TÍCH

Từ output, tôi thấy:
- `#PubkeyAuthentication yes` - Đang bị comment
- `#PasswordAuthentication yes` - Đang bị comment

**Cần:** Uncomment và enable password authentication.

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Edit SSH config:**

```bash
sudo nano /etc/ssh/sshd_config
```

### **BƯỚC 2: Tìm và sửa các dòng:**

**Tìm dòng:**
```bash
#PubkeyAuthentication yes
```

**Đổi thành:**
```bash
PubkeyAuthentication yes
```

**Tìm dòng:**
```bash
#PasswordAuthentication yes
```

**Đổi thành:**
```bash
PasswordAuthentication yes
```

**Tìm dòng (nếu có):**
```bash
#ChallengeResponseAuthentication no
```

**Đổi thành:**
```bash
ChallengeResponseAuthentication yes
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## ⚡ QUICK FIX - TỰ ĐỘNG

### **Chạy các lệnh sau:**

```bash
# Uncomment và enable PubkeyAuthentication
sudo sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Uncomment và enable PasswordAuthentication
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Enable ChallengeResponseAuthentication (nếu có)
sudo sed -i 's/^#ChallengeResponseAuthentication no/ChallengeResponseAuthentication yes/' /etc/ssh/sshd_config

# Verify
sudo grep -E "^PasswordAuthentication|^PubkeyAuthentication|^ChallengeResponseAuthentication" /etc/ssh/sshd_config
```

**Kết quả mong đợi:**
```
PubkeyAuthentication yes
PasswordAuthentication yes
ChallengeResponseAuthentication yes
```

### **Test config:**

```bash
# Test SSH config
sudo sshd -t
```

**Nếu không có lỗi** → OK

### **Restart SSH:**

```bash
# Restart SSH service
sudo systemctl restart sshd

# Verify
sudo systemctl status sshd
```

**Kết quả mong đợi:**
```
Active: active (running)
```

---

## 🧪 TEST LOGIN

### **Sau khi restart SSH:**

1. **Tạo SSH session mới trong MobaXterm:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - **Bỏ chọn** "Use private key"

2. **Login** → Nhập password của `adsuser`

3. **Nếu thành công:** Prompt sẽ là `adsuser@ip-172-26-10-102:~$`

---

## 🔍 VERIFY CẤU HÌNH

```bash
# Check lại
sudo grep -E "^PasswordAuthentication|^PubkeyAuthentication" /etc/ssh/sshd_config | grep -v "^#"
```

**Phải thấy:**
```
PasswordAuthentication yes
PubkeyAuthentication yes
```

---

## ⚠️ NẾU VẪN KHÔNG WORK

### **Check thêm:**

```bash
# Check tất cả settings liên quan
sudo grep -i password /etc/ssh/sshd_config | grep -v "^#"

# Check PAM
sudo grep -i "UsePAM" /etc/ssh/sshd_config
# Nên thấy: UsePAM yes
```

### **Hoặc dùng SSH key (nhanh hơn):**

```bash
# Copy SSH key từ ubuntu
sudo mkdir -p /home/adsuser/.ssh
sudo cp /home/ubuntu/.ssh/authorized_keys /home/adsuser/.ssh/
sudo chown -R adsuser:adsuser /home/adsuser/.ssh
sudo chmod 700 /home/adsuser/.ssh
sudo chmod 600 /home/adsuser/.ssh/authorized_keys
```

---

## ✅ CHECKLIST

- [ ] Uncomment `PubkeyAuthentication yes`
- [ ] Uncomment `PasswordAuthentication yes`
- [ ] Enable `ChallengeResponseAuthentication yes`
- [ ] Test config: `sudo sshd -t`
- [ ] Restart SSH: `sudo systemctl restart sshd`
- [ ] Verify: `sudo systemctl status sshd`
- [ ] Test login với MobaXterm

---

**Chạy các lệnh Quick Fix ở trên, sau đó restart SSH và thử login lại! 🚀**

