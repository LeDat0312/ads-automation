# 🔧 FIX PERMISSIONS - THƯ MỤC ADSUSER

## 🔍 VẤN ĐỀ

Lỗi "Permission denied" khi upload files qua SFTP vào `/home/adsuser`.

**Nguyên nhân:** Thư mục home của `adsuser` không có quyền đúng.

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Kiểm tra quyền hiện tại:**

```bash
# Check permissions
ls -la /home/adsuser
```

### **BƯỚC 2: Fix permissions:**

```bash
# Fix ownership (đảm bảo adsuser sở hữu thư mục)
sudo chown -R adsuser:adsuser /home/adsuser

# Fix permissions (755 cho directories, 644 cho files)
sudo chmod 755 /home/adsuser
sudo find /home/adsuser -type d -exec chmod 755 {} \;
sudo find /home/adsuser -type f -exec chmod 644 {} \;

# Đặc biệt: .ssh directory cần 700
sudo chmod 700 /home/adsuser/.ssh 2>/dev/null || true
sudo chmod 600 /home/adsuser/.ssh/authorized_keys 2>/dev/null || true
```

### **BƯỚC 3: Verify:**

```bash
# Check lại
ls -la /home/adsuser
```

**Kết quả mong đợi:**
```
drwxr-xr-x  adsuser adsuser  ...
```

---

## 📁 TẠO THƯ MỤC PROJECT

### **Option 1: Tạo trong /home/adsuser (Khuyến nghị):**

```bash
# Tạo thư mục với quyền đúng
mkdir -p ~/ads-automation
chmod 755 ~/ads-automation

# Verify
ls -ld ~/ads-automation
# Nên thấy: drwxr-xr-x adsuser adsuser
```

### **Option 2: Tạo trong /opt (nếu cần):**

```bash
# Tạo thư mục
sudo mkdir -p /opt/ads-automation
sudo chown -R adsuser:adsuser /opt/ads-automation
sudo chmod 755 /opt/ads-automation

# Sử dụng
cd /opt/ads-automation
```

---

## 📤 UPLOAD FILES

### **Sau khi fix permissions:**

1. **Mở MobaXterm File Manager**
2. **Navigate đến:** `/home/adsuser/ads-automation`
3. **Upload files** - Bây giờ sẽ không còn lỗi permission

### **Hoặc dùng SCP từ terminal:**

```bash
# Từ máy local (Windows PowerShell hoặc CMD)
scp -r "C:\path\to\project\*" adsuser@your-server-ip:~/ads-automation/
```

---

## 🔍 KIỂM TRA CHI TIẾT

### **Check user và group:**

```bash
# Check current user
whoami
# Nên thấy: adsuser

# Check groups
groups
# Nên thấy: adsuser sudo (hoặc tương tự)

# Check home directory
echo $HOME
# Nên thấy: /home/adsuser
```

### **Check permissions chi tiết:**

```bash
# Check home directory
ls -ld ~
# Nên thấy: drwxr-xr-x

# Check project directory
ls -ld ~/ads-automation 2>/dev/null || echo "Directory not exists"
```

---

## 🛠️ NẾU VẪN GẶP LỖI

### **Option 1: Tạo user mới với quyền đúng:**

```bash
# Tạo user mới
sudo adduser adsuser2
sudo usermod -aG sudo adsuser2

# Set password
sudo passwd adsuser2

# Fix permissions
sudo chown -R adsuser2:adsuser2 /home/adsuser2
sudo chmod 755 /home/adsuser2
```

### **Option 2: Dùng user ubuntu (nếu có):**

```bash
# Switch sang user ubuntu
su - ubuntu

# Tạo project directory
mkdir -p ~/ads-automation
cd ~/ads-automation
```

### **Option 3: Upload vào /tmp rồi move:**

```bash
# Upload vào /tmp (có quyền write)
# Sau đó move
sudo mv /tmp/ads-automation/* ~/ads-automation/
sudo chown -R adsuser:adsuser ~/ads-automation
```

---

## ✅ QUICK FIX (Tất cả trong một lệnh):

```bash
# Fix tất cả permissions
sudo chown -R adsuser:adsuser /home/adsuser
sudo chmod 755 /home/adsuser
sudo find /home/adsuser -type d -exec chmod 755 {} \;
sudo find /home/adsuser -type f -exec chmod 644 {} \;

# Tạo project directory
mkdir -p ~/ads-automation
chmod 755 ~/ads-automation

# Verify
ls -ld ~/ads-automation
```

---

## 📝 SAU KHI FIX

1. ✅ **Thử upload lại** qua MobaXterm File Manager
2. ✅ **Verify files:**
   ```bash
   ls -la ~/ads-automation
   ```
3. ✅ **Tiếp tục setup** theo `SETUP_NEXT_STEPS.md`

---

**Chạy các lệnh fix permissions ở trên, sau đó thử upload lại! 🚀**

