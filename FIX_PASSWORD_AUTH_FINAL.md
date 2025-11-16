# 🔐 FIX PASSWORD AUTHENTICATION - KIỂM TRA KỸ

## 🔍 VẤN ĐỀ

Vẫn gặp lỗi "No supported authentication methods available (server sent: publickey)" dù đã enable `PasswordAuthentication yes`.

**Nguyên nhân có thể:**
1. SSH config chưa được reload đúng
2. Có setting khác override
3. UsePAM chưa được enable

---

## ✅ KIỂM TRA CHI TIẾT

### **BƯỚC 1: Check toàn bộ SSH config:**

```bash
# Check tất cả settings liên quan
sudo grep -i "password\|authentication\|pam" /etc/ssh/sshd_config | grep -v "^#"
```

### **BƯỚC 2: Check UsePAM:**

```bash
# Check UsePAM
sudo grep -i "UsePAM" /etc/ssh/sshd_config
```

**Phải thấy:** `UsePAM yes` (nếu không có, cần thêm)

### **BƯỚC 3: Check có dòng nào override không:**

```bash
# Check xem có dòng nào disable password auth không
sudo grep -i "PasswordAuthentication" /etc/ssh/sshd_config
```

**Phải thấy:** `PasswordAuthentication yes` (KHÔNG có `no`)

---

## 🔧 SỬA LẠI ĐÚNG CÁCH

### **BƯỚC 1: Edit SSH config:**

```bash
sudo nano /etc/ssh/sshd_config
```

### **BƯỚC 2: Tìm và sửa/thêm các dòng:**

**Đảm bảo có các dòng sau (KHÔNG có # ở đầu):**

```bash
UsePAM yes
PasswordAuthentication yes
PubkeyAuthentication yes
```

**Nếu không có, thêm vào cuối file:**

```bash
# Allow password authentication
UsePAM yes
PasswordAuthentication yes
PubkeyAuthentication yes
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **BƯỚC 3: Đảm bảo không có dòng nào override:**

```bash
# Check xem có dòng PasswordAuthentication no không
sudo grep "PasswordAuthentication no" /etc/ssh/sshd_config

# Nếu có, xóa hoặc comment
sudo sed -i 's/^PasswordAuthentication no/#PasswordAuthentication no/' /etc/ssh/sshd_config
```

---

## ⚡ QUICK FIX - TẤT CẢ TRONG MỘT LẦN:

```bash
# Backup
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Disable tất cả PasswordAuthentication no
sudo sed -i 's/^PasswordAuthentication no/#PasswordAuthentication no/' /etc/ssh/sshd_config

# Enable UsePAM
sudo sed -i 's/^#UsePAM yes/UsePAM yes/' /etc/ssh/sshd_config
sudo sed -i 's/^UsePAM no/UsePAM yes/' /etc/ssh/sshd_config

# Enable PasswordAuthentication
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
if ! grep -q "^PasswordAuthentication yes" /etc/ssh/sshd_config; then
    echo "" | sudo tee -a /etc/ssh/sshd_config
    echo "UsePAM yes" | sudo tee -a /etc/ssh/sshd_config
    echo "PasswordAuthentication yes" | sudo tee -a /etc/ssh/sshd_config
fi

# Verify
echo "=== UsePAM ==="
sudo grep -i "^UsePAM" /etc/ssh/sshd_config | grep -v "^#"

echo "=== PasswordAuthentication ==="
sudo grep -i "^PasswordAuthentication" /etc/ssh/sshd_config | grep -v "^#"

echo "=== PubkeyAuthentication ==="
sudo grep -i "^PubkeyAuthentication" /etc/ssh/sshd_config | grep -v "^#"
```

**Kết quả mong đợi:**
```
UsePAM yes
PasswordAuthentication yes
PubkeyAuthentication yes
```

### **BƯỚC 4: Test và restart SSH:**

```bash
# Test config
sudo sshd -t

# Nếu OK, restart SSH
sudo systemctl restart sshd

# Verify SSH đang chạy
sudo systemctl status sshd

# Check SSH process
ps aux | grep sshd
```

---

## 🔍 DEBUG CHI TIẾT

### **Check SSH logs khi login:**

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

---

## 🧪 TEST LOGIN

### **Sau khi fix:**

1. **Đảm bảo đã set password:**
   ```bash
   sudo passwd adsuser
   ```

2. **Tạo SSH session mới trong MobaXterm:**
   - Remote host: `your-server-ip`
   - Username: `adsuser`
   - Port: `22`
   - **Bỏ chọn** "Use private key"

3. **Login** → Sẽ hỏi password → Nhập password

---

## 🔧 NẾU VẪN KHÔNG WORK

### **Option 1: Check PAM configuration:**

```bash
# Check PAM config
sudo grep -i "password" /etc/pam.d/sshd
```

### **Option 2: Restart SSH service force:**

```bash
# Stop SSH
sudo systemctl stop sshd

# Start SSH
sudo systemctl start sshd

# Verify
sudo systemctl status sshd
```

### **Option 3: Check có process SSH nào đang chạy không:**

```bash
# Check SSH processes
ps aux | grep sshd

# Kill và restart
sudo pkill sshd
sudo systemctl start sshd
```

---

## ✅ CHECKLIST

- [ ] Backup SSH config
- [ ] Enable `UsePAM yes`
- [ ] Enable `PasswordAuthentication yes`
- [ ] Disable/comment `PasswordAuthentication no`
- [ ] Test config: `sudo sshd -t`
- [ ] Restart SSH: `sudo systemctl restart sshd`
- [ ] Verify: `sudo systemctl status sshd`
- [ ] Set password: `sudo passwd adsuser`
- [ ] Test login với MobaXterm

---

**Chạy lệnh Quick Fix ở trên, sau đó verify và thử login lại! 🚀**

