# 👤 SETUP USER ADSUSER

## 🎯 MỤC TIÊU

1. Tạo user `adsuser` (nếu chưa có)
2. Set password cho `adsuser`
3. Nâng quyền `adsuser` lên sudo (root)
4. Login MobaXterm bằng `adsuser`

---

## 🔧 BƯỚC 1: TẠO USER ADSUSER

### **1.1. Kiểm tra user đã tồn tại chưa:**

```bash
# Check user adsuser
id adsuser
# Nếu thấy: "id: 'adsuser': no such user" → chưa có
# Nếu thấy thông tin user → đã có
```

### **1.2. Tạo user mới (nếu chưa có):**

```bash
# Tạo user adsuser
sudo adduser adsuser
```

**Sẽ hỏi:**
- `Enter new UNIX password:` → Nhập password cho adsuser
- `Retype new UNIX password:` → Nhập lại password
- `Full Name []:` → Enter (hoặc điền tên)
- `Room Number []:` → Enter
- `Work Phone []:` → Enter
- `Home Phone []:` → Enter
- `Other []:` → Enter
- `Is the information correct? [Y/n]` → Y

**Ví dụ:**
```
Enter new UNIX password: MySecurePass123!
Retype new UNIX password: MySecurePass123!
```

### **1.3. Nếu user đã tồn tại, chỉ cần set password:**

```bash
# Set password cho adsuser
sudo passwd adsuser
```

**Nhập password mới 2 lần.**

---

## 🔐 BƯỚC 2: NÂNG QUYỀN SUDO CHO ADSUSER

```bash
# Thêm adsuser vào sudo group
sudo usermod -aG sudo adsuser

# Verify
groups adsuser
# Nên thấy: adsuser sudo
```

### **Test quyền sudo:**

```bash
# Switch sang adsuser
su - adsuser

# Test sudo
sudo whoami
# Nên trả về: root

# Nếu hỏi password, nhập password của adsuser
```

---

## 🏠 BƯỚC 3: SETUP HOME DIRECTORY

```bash
# Fix permissions cho home directory
sudo chown -R adsuser:adsuser /home/adsuser
sudo chmod 755 /home/adsuser

# Tạo project directory
sudo mkdir -p /home/adsuser/ads-automation
sudo chown -R adsuser:adsuser /home/adsuser/ads-automation
sudo chmod 755 /home/adsuser/ads-automation
```

---

## 🔌 BƯỚC 4: LOGIN MOBAXTERM VỚI ADSUSER

### **4.1. Tạo SSH Session mới:**

1. **Mở MobaXterm**
2. **Click "Session"** → **"SSH"**
3. **Điền thông tin:**
   - **Remote host:** `your-server-ip` (giống như trước)
   - **Username:** `adsuser` (thay vì `ubuntu`)
   - **Port:** `22`
   - **Advanced SSH settings:**
     - ✅ Use private key: Bỏ chọn (nếu dùng password)
     - Hoặc giữ private key nếu đã setup SSH key
4. **Click "OK"**

### **4.2. Lần đầu login:**

- Sẽ hỏi password → Nhập password của `adsuser`
- Nếu hỏi "Are you sure you want to continue connecting?" → **Yes**

### **4.3. Verify:**

Sau khi login, prompt sẽ là:
```
adsuser@ip-172-26-10-102:~$
```

---

## 📤 BƯỚC 5: UPLOAD FILES VỚI ADSUSER

### **5.1. Tạo thư mục project:**

```bash
mkdir -p ~/ads-automation
cd ~/ads-automation
```

### **5.2. Upload files qua MobaXterm:**

1. **Mở File Manager** (icon bên trái)
2. **Navigate đến:** `/home/adsuser/ads-automation`
3. **Upload:**
   - Kéo thả `app/` folder
   - Kéo thả `scripts/` folder
   - Kéo thả `requirements.txt`
   - Kéo thả `env.example`

### **5.3. Verify:**

```bash
cd ~/ads-automation
ls -la
# Nên thấy: app/, scripts/, requirements.txt, env.example
```

---

## 🔄 BƯỚC 6: CHUYỂN DỮ LIỆU TỪ UBUNTU SANG ADSUSER (NẾU CẦN)

Nếu bạn đã upload files vào `/home/ubuntu/ads-automation`, có thể copy sang:

```bash
# Copy từ ubuntu sang adsuser
sudo cp -r /home/ubuntu/ads-automation/* /home/adsuser/ads-automation/
sudo chown -R adsuser:adsuser /home/adsuser/ads-automation
```

---

## ✅ CHECKLIST

- [ ] Tạo user `adsuser` với password
- [ ] Thêm `adsuser` vào sudo group
- [ ] Fix permissions cho `/home/adsuser`
- [ ] Tạo SSH session mới trong MobaXterm với `adsuser`
- [ ] Login thành công với `adsuser`
- [ ] Tạo thư mục `~/ads-automation`
- [ ] Upload files vào `/home/adsuser/ads-automation`
- [ ] Verify files đã upload

---

## 🔍 VERIFY SETUP

```bash
# Check user
whoami
# Nên thấy: adsuser

# Check groups
groups
# Nên thấy: adsuser sudo

# Check home directory
echo $HOME
# Nên thấy: /home/adsuser

# Check project directory
ls -la ~/ads-automation
```

---

## 📝 LƯU Ý

1. **Password:** Ghi nhớ password của `adsuser` để login
2. **SSH Key:** Nếu muốn dùng SSH key thay vì password:
   ```bash
   # Copy SSH key từ ubuntu
   sudo cp -r /home/ubuntu/.ssh /home/adsuser/
   sudo chown -R adsuser:adsuser /home/adsuser/.ssh
   sudo chmod 700 /home/adsuser/.ssh
   sudo chmod 600 /home/adsuser/.ssh/authorized_keys
   ```
3. **Database user:** Database user vẫn là `adsuser` với password `@Levandat0312` (không đổi)

---

**Bây giờ hãy tạo user adsuser và login lại với MobaXterm! 🚀**

