# 🔐 GITHUB CLONE - XÁC THỰC

## 📝 THÔNG TIN CẦN NHẬP

### **Username:**
```
LeDat0312
```

### **Password:**
**KHÔNG dùng password GitHub thông thường!**

**Dùng:** GitHub Personal Access Token

---

## 🔑 TẠO PERSONAL ACCESS TOKEN

### **Nếu chưa có token:**

1. **Truy cập GitHub:**
   - https://github.com/settings/tokens
   - Hoặc: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Click "Generate new token (classic)"**

3. **Điền:**
   - **Note:** `ads-automation-vps`
   - **Expiration:** Chọn thời hạn (ví dụ: 90 days hoặc No expiration)
   - **Scopes:** Check `repo` (tất cả quyền repo)

4. **Click "Generate token"**

5. **Copy token** (chỉ hiện 1 lần - lưu lại!)

6. **Dùng token này** thay cho password

---

## 📥 CLONE VỚI TOKEN

### **Trên VPS:**

```bash
# Clone (sẽ hỏi username và password)
git clone https://github.com/LeDat0312/ads-automation.git ~/ads-automation
```

**Khi hỏi:**
- **Username:** `LeDat0312`
- **Password:** `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (Personal Access Token)

---

## 🔒 CÁCH AN TOÀN HƠN: DÙNG SSH

### **Nếu muốn không phải nhập token mỗi lần:**

1. **Tạo SSH key trên VPS:**

```bash
# Tạo SSH key
ssh-keygen -t ed25519 -C "adsuser@vps" -f ~/.ssh/id_ed25519

# Không cần passphrase (Enter 2 lần)
```

2. **Copy public key:**

```bash
# Hiển thị public key
cat ~/.ssh/id_ed25519.pub
```

3. **Thêm vào GitHub:**
   - Truy cập: https://github.com/settings/keys
   - Click "New SSH key"
   - **Title:** `VPS - adsuser`
   - **Key:** Paste nội dung từ `cat ~/.ssh/id_ed25519.pub`
   - Click "Add SSH key"

4. **Clone bằng SSH:**

```bash
# Clone bằng SSH (không cần nhập password)
git clone git@github.com:LeDat0312/ads-automation.git ~/ads-automation
```

---

## ⚡ QUICK ANSWER

### **Ngay bây giờ:**

1. **Username:** Nhập `LeDat0312` và Enter

2. **Password:** 
   - Nếu đã có token → Nhập token
   - Nếu chưa có → Tạo token trên máy local (theo hướng dẫn trên), sau đó nhập token

---

## ✅ SAU KHI CLONE THÀNH CÔNG

```bash
# Navigate vào thư mục
cd ~/ads-automation

# Verify
ls -la

# Kết quả mong đợi:
# app/
# scripts/
# requirements.txt
# env.example
```

---

**Ngay bây giờ: Nhập `LeDat0312` và Enter, sau đó nhập Personal Access Token! 🔐**


