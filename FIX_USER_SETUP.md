# 🔧 FIX USER SETUP - HƯỚNG DẪN CHI TIẾT

## 🎯 VẤN ĐỀ: Thêm user `metaupdateads` vào sudo group

### **BƯỚC 1: KIỂM TRA USER ĐÃ TỒN TẠI CHƯA**

```bash
# Kiểm tra user metaupdateads đã tồn tại chưa
id metaupdateads

# Hoặc
getent passwd metaupdateads

# Hoặc
cat /etc/passwd | grep metaupdateads
```

**Kết quả:**
- ✅ **Nếu thấy thông tin user:** User đã tồn tại, tiếp tục bước 2
- ❌ **Nếu không thấy gì:** User chưa tồn tại, cần tạo user trước

---

### **BƯỚC 2: TẠO USER NẾU CHƯA TỒN TẠI**

```bash
# Chuyển sang root (nếu chưa phải root)
sudo su -

# Hoặc nếu đã là root, bỏ qua lệnh trên

# Tạo user metaupdateads
adduser metaupdateads

# Hệ thống sẽ hỏi:
# - Password: Nhập password mới
# - Retype password: Nhập lại password
# - Full name: (có thể để trống, Enter)
# - Room number: (có thể để trống, Enter)
# - Work phone: (có thể để trống, Enter)
# - Home phone: (có thể để trống, Enter)
# - Other: (có thể để trống, Enter)
```

---

### **BƯỚC 3: THÊM USER VÀO SUDO GROUP**

```bash
# Đảm bảo bạn đang là root hoặc có quyền sudo
# Nếu chưa là root, chạy:
sudo su -

# Thêm user vào sudo group
usermod -aG sudo metaupdateads

# Verify user đã được thêm vào sudo group
groups metaupdateads

# Kết quả mong đợi: metaupdateads : metaupdateads sudo
```

---

### **BƯỚC 4: THÊM USER VÀO DOCKER GROUP (SẼ DÙNG SAU)**

```bash
# Thêm user vào docker group (nếu đã install Docker)
usermod -aG docker metaupdateads

# Verify
groups metaupdateads

# Kết quả mong đợi: metaupdateads : metaupdateads sudo docker
```

**⚠️ LƯU Ý:** Nếu chưa install Docker, bỏ qua bước này. Sẽ thêm sau khi install Docker.

---

### **BƯỚC 5: TEST USER MỚI**

```bash
# Switch sang user metaupdateads
su - metaupdateads

# Test sudo (sẽ hỏi password)
sudo whoami

# Kết quả mong đợi: root

# Test các commands khác
sudo ls /root
sudo apt update
```

---

## 🔍 TROUBLESHOOTING

### **Lỗi 1: "user 'metaupdateads' does not exist"**

**Nguyên nhân:** User chưa được tạo

**Giải pháp:**
```bash
# Tạo user trước
sudo adduser metaupdateads

# Sau đó thêm vào sudo group
sudo usermod -aG sudo metaupdateads
```

---

### **Lỗi 2: "permission denied" hoặc "usermod: cannot lock /etc/passwd"**

**Nguyên nhân:** Không có quyền root

**Giải pháp:**
```bash
# Chuyển sang root
sudo su -

# Hoặc dùng sudo
sudo usermod -aG sudo metaupdateads
```

---

### **Lỗi 3: "group 'sudo' does not exist"**

**Nguyên nhân:** Sudo chưa được install

**Giải pháp:**
```bash
# Install sudo
apt update
apt install sudo -y

# Sau đó thêm user vào sudo group
usermod -aG sudo metaupdateads
```

---

### **Lỗi 4: User không có quyền sudo sau khi thêm**

**Nguyên nhân:** Cần logout và login lại

**Giải pháp:**
```bash
# Logout user hiện tại
exit

# Login lại với user metaupdateads
ssh metaupdateads@your-lightsail-ip

# Test sudo
sudo whoami
```

---

## 📋 CÁC LỆNH ĐẦY ĐỦ (Copy và paste)

### **Nếu bạn đang là root:**

```bash
# 1. Kiểm tra user đã tồn tại chưa
id metaupdateads

# 2. Nếu chưa tồn tại, tạo user
adduser metaupdateads
# Nhập password khi được hỏi

# 3. Thêm user vào sudo group
usermod -aG sudo metaupdateads

# 4. Verify
groups metaupdateads
# Kết quả: metaupdateads : metaupdateads sudo

# 5. Test
su - metaupdateads
sudo whoami
# Kết quả: root
```

### **Nếu bạn đang là user ubuntu (không phải root):**

```bash
# 1. Chuyển sang root
sudo su -

# 2. Kiểm tra user đã tồn tại chưa
id metaupdateads

# 3. Nếu chưa tồn tại, tạo user
adduser metaupdateads
# Nhập password khi được hỏi

# 4. Thêm user vào sudo group
usermod -aG sudo metaupdateads

# 5. Verify
groups metaupdateads
# Kết quả: metaupdateads : metaupdateads sudo

# 6. Test
exit  # Thoát khỏi root
su - metaupdateads
sudo whoami
# Kết quả: root
```

---

## 🎯 HƯỚNG DẪN TỪNG BƯỚC TRONG MOBAXTERM

### **Bước 1: Mở terminal trong MobaXterm**

1. Đăng nhập vào VPS (nếu chưa)
2. Mở terminal (nếu chưa mở)

### **Bước 2: Kiểm tra user hiện tại**

```bash
# Xem bạn đang là user nào
whoami

# Kết quả: ubuntu hoặc root
```

### **Bước 3: Chuyển sang root (nếu cần)**

```bash
# Nếu là ubuntu, chuyển sang root
sudo su -

# Nhập password của ubuntu (nếu được hỏi)
# Kết quả: Bạn sẽ thấy prompt thay đổi thành root@...

# Verify
whoami
# Kết quả: root
```

### **Bước 4: Kiểm tra user metaupdateads**

```bash
# Kiểm tra user đã tồn tại chưa
id metaupdateads
```

**Nếu thấy lỗi "id: 'metaupdateads': no such user":**

```bash
# Tạo user mới
adduser metaupdateads

# Hệ thống sẽ hỏi password:
# New password: [Nhập password mới]
# Retype new password: [Nhập lại password]
# Full name []: [Enter để bỏ qua]
# Room number []: [Enter để bỏ qua]
# Work phone []: [Enter để bỏ qua]
# Home phone []: [Enter để bỏ qua]
# Other []: [Enter để bỏ qua]
# Is the information correct? [Y/n]: Y
```

### **Bước 5: Thêm user vào sudo group**

```bash
# Thêm user vào sudo group
usermod -aG sudo metaupdateads

# Verify
groups metaupdateads

# Kết quả mong đợi:
# metaupdateads : metaupdateads sudo
```

### **Bước 6: Test user mới**

```bash
# Switch sang user metaupdateads
su - metaupdateads

# Bạn sẽ thấy prompt thay đổi thành: metaupdateads@...

# Test sudo
sudo whoami

# Sẽ hỏi password, nhập password của metaupdateads
# Kết quả: root
```

---

## 🔒 SECURITY: SETUP SSH VỚI PASSWORD

### **Bước 1: Enable password authentication**

```bash
# Edit SSH config (vẫn đang là root)
nano /etc/ssh/sshd_config

# Tìm và sửa các dòng sau:
# PasswordAuthentication yes        # Bỏ comment và set = yes
# PermitRootLogin no                # Không cho root login (security)
# PubkeyAuthentication yes          # Vẫn cho phép dùng key

# Save: Ctrl+X, Y, Enter
```

### **Bước 2: Restart SSH**

```bash
# Restart SSH
systemctl restart sshd

# Check status
systemctl status sshd
```

### **Bước 3: Test login với MobaXterm**

1. Tạo session mới trong MobaXterm
2. Chọn "SSH"
3. Remote host: `your-lightsail-ip`
4. Username: `metaupdateads`
5. **Bỏ chọn "Use private key"** (nếu muốn dùng password)
6. Click "OK"
7. Nhập password khi được hỏi

---

## 📝 CHECKLIST

### **✅ SAU KHI HOÀN THÀNH:**

- [ ] Đã kiểm tra user metaupdateads tồn tại
- [ ] Đã tạo user metaupdateads (nếu chưa có)
- [ ] Đã thêm user vào sudo group
- [ ] Đã verify với `groups metaupdateads`
- [ ] Đã test sudo với `sudo whoami`
- [ ] Đã enable password authentication
- [ ] Đã restart SSH
- [ ] Đã test login với MobaXterm

---

## 🎯 CÁC LỆNH QUAN TRỌNG NHẤT

```bash
# 1. Chuyển sang root
sudo su -

# 2. Tạo user (nếu chưa có)
adduser metaupdateads

# 3. Thêm vào sudo group
usermod -aG sudo metaupdateads

# 4. Verify
groups metaupdateads

# 5. Test
su - metaupdateads
sudo whoami
```

---

## 💡 LƯU Ý

1. **Phải là root:** Bạn phải là root hoặc có quyền sudo để thêm user vào group
2. **User phải tồn tại:** User `metaupdateads` phải được tạo trước
3. **Logout/Login:** Sau khi thêm vào group, cần logout và login lại để áp dụng
4. **Password:** Nhớ password của user `metaupdateads` để dùng sau

---

## 🚨 NẾU VẪN GẶP LỖI

**Gửi cho tôi:**
1. Output của lệnh `whoami`
2. Output của lệnh `id metaupdateads`
3. Output của lệnh `groups metaupdateads`
4. Thông báo lỗi cụ thể (nếu có)

**Tôi sẽ giúp bạn debug!**

---

**Chúc bạn setup thành công! 🚀**

