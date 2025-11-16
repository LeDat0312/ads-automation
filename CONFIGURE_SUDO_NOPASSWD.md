# 🔐 CONFIGURE SUDO NO PASSWORD

## 🎯 MỤC TIÊU

Cho phép user `adsuser` chạy `sudo` mà không cần nhập password.

---

## ✅ CÁCH 1: THÊM VÀO SUDOERS (KHUYẾN NGHỊ)

### **BƯỚC 1: Edit sudoers file:**

```bash
sudo visudo
```

**⚠️ LƯU Ý:** Dùng `visudo` (KHÔNG dùng `nano` trực tiếp) để tránh lỗi syntax.

### **BƯỚC 2: Thêm dòng sau vào cuối file:**

```bash
adsuser ALL=(ALL) NOPASSWD: ALL
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Hoặc nếu dùng nano:**
```bash
echo "adsuser ALL=(ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers
```

---

## ✅ CÁCH 2: TẠO FILE RIÊNG (AN TOÀN HƠN)

### **BƯỚC 1: Tạo file config riêng:**

```bash
sudo nano /etc/sudoers.d/adsuser
```

### **BƯỚC 2: Thêm nội dung:**

```bash
adsuser ALL=(ALL) NOPASSWD: ALL
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **BƯỚC 3: Fix permissions:**

```bash
sudo chmod 440 /etc/sudoers.d/adsuser
```

---

## ⚡ QUICK FIX - TẤT CẢ TRONG MỘT LẦN:

```bash
# Tạo file config riêng (an toàn hơn)
echo "adsuser ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/adsuser

# Fix permissions
sudo chmod 440 /etc/sudoers.d/adsuser

# Verify
sudo cat /etc/sudoers.d/adsuser
```

**Kết quả mong đợi:**
```
adsuser ALL=(ALL) NOPASSWD: ALL
```

---

## 🧪 TEST

### **Sau khi config:**

```bash
# Login với adsuser (hoặc switch user)
su - adsuser

# Test sudo không cần password
sudo whoami
# Nên trả về: root (KHÔNG hỏi password)

# Test lệnh khác
sudo ls -la /root
# Nên chạy được (KHÔNG hỏi password)
```

---

## 🔍 VERIFY

### **Check sudoers:**

```bash
# Check file mới tạo
sudo cat /etc/sudoers.d/adsuser

# Check syntax
sudo visudo -c
```

**Nếu không có lỗi** → OK

---

## ⚠️ LƯU Ý BẢO MẬT

### **Cấp quyền hạn chế hơn (nếu muốn):**

Thay vì `ALL`, có thể giới hạn:

```bash
# Chỉ cho phép một số lệnh cụ thể
adsuser ALL=(ALL) NOPASSWD: /usr/bin/systemctl, /usr/bin/apt, /usr/bin/dpkg

# Hoặc chỉ cho phép một số thư mục
adsuser ALL=(ALL) NOPASSWD: /home/adsuser/*
```

### **Ví dụ giới hạn:**

```bash
# Chỉ cho phép restart services
adsuser ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart *, /usr/bin/systemctl start *, /usr/bin/systemctl stop *

# Chỉ cho phép trong thư mục project
adsuser ALL=(ALL) NOPASSWD: /home/adsuser/ads-automation/*
```

---

## 🔧 NẾU GẶP LỖI

### **Lỗi syntax:**

```bash
# Test syntax
sudo visudo -c

# Nếu có lỗi, sửa lại
sudo visudo
```

### **Không work:**

```bash
# Check user có trong sudo group không
groups adsuser
# Nên thấy: adsuser sudo

# Nếu không có, thêm vào
sudo usermod -aG sudo adsuser
```

---

## ✅ CHECKLIST

- [ ] Tạo file `/etc/sudoers.d/adsuser`
- [ ] Thêm dòng: `adsuser ALL=(ALL) NOPASSWD: ALL`
- [ ] Fix permissions: `chmod 440`
- [ ] Test syntax: `sudo visudo -c`
- [ ] Test sudo: `sudo whoami` (không hỏi password)

---

**Chạy lệnh Quick Fix ở trên, sau đó test sudo! 🚀**

