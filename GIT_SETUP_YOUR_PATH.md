# 🚀 GIT SETUP - ĐƯỜNG DẪN CỦA BẠN

## 📁 Đường dẫn project:
```
C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds
```

## 👤 GitHub Username: `LeDat0312`

---

## 📋 BƯỚC 1: CÀI GIT (NẾU CHƯA CÓ)

### **Download và Install:**

1. **Download Git:**
   - https://git-scm.com/download/win
   - Click "Download for Windows"

2. **Install:**
   - Chạy file `.exe` vừa download
   - Click "Next" → "Next" → ... → "Install"
   - Mất khoảng 2-3 phút

3. **Verify:**
   ```powershell
   git --version
   # Nên thấy: git version 2.x.x
   ```

---

## 📋 BƯỚC 2: SETUP GIT TRÊN MÁY LOCAL

### **Mở PowerShell hoặc CMD:**

```powershell
# Navigate đến thư mục project
cd "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"

# Verify đang ở đúng thư mục
pwd
# Hoặc
Get-Location
```

### **Configure Git (nếu chưa có):**

```powershell
git config --global user.name "LeDat0312"
git config --global user.email "your.email@example.com"
# Thay your.email@example.com bằng email thực tế của bạn
```

### **Initialize repository:**

```powershell
# Initialize Git
git init

# Check status
git status

# Add tất cả files
git add .

# Commit lần đầu
git commit -m "Initial commit: Facebook Ads Automation System"
```

---

## 🌐 BƯỚC 3: TẠO REPOSITORY TRÊN GITHUB

### **1. Truy cập GitHub:**

- URL: https://github.com/new
- Hoặc: https://github.com → Click "New repository"

### **2. Điền thông tin:**

- **Repository name:** `ads-automation` (hoặc `PythonUpdateMetaAds`)
- **Description:** `Facebook Ads Automation System`
- **Visibility:** 
  - ✅ **Private** (khuyến nghị)
- **KHÔNG** check "Initialize with README"
- Click **"Create repository"**

### **3. Copy repository URL:**

Sau khi tạo, GitHub sẽ hiển thị URL:
```
https://github.com/LeDat0312/ads-automation.git
```
Hoặc nếu đặt tên `PythonUpdateMetaAds`:
```
https://github.com/LeDat0312/PythonUpdateMetaAds.git
```

---

## 📤 BƯỚC 4: PUSH CODE LÊN GITHUB

### **Trên máy local (PowerShell):**

```powershell
# Đảm bảo đang ở đúng thư mục
cd "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"

# Thêm remote (thay tên repository nếu khác)
git remote add origin https://github.com/LeDat0312/ads-automation.git

# Check remote
git remote -v

# Rename branch to main
git branch -M main

# Push code
git push -u origin main
```

**Sẽ hỏi:**
- **Username:** `LeDat0312`
- **Password:** GitHub Personal Access Token (KHÔNG dùng password)

---

## 🔐 BƯỚC 5: TẠO PERSONAL ACCESS TOKEN

### **Nếu GitHub hỏi password:**

1. **Vào GitHub:**
   - https://github.com/settings/tokens
   - Hoặc: Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Click "Generate new token (classic)"**

3. **Điền:**
   - **Note:** `ads-automation`
   - **Expiration:** Chọn thời hạn (ví dụ: 90 days)
   - **Scopes:** Check `repo` (tất cả quyền repo)

4. **Click "Generate token"**

5. **Copy token** (chỉ hiện 1 lần - lưu lại!)

6. **Dùng token này** thay cho password khi push

---

## 📥 BƯỚC 6: CLONE VỀ VPS

### **Trên VPS:**

```bash
# Install Git (nếu chưa có)
sudo apt update
sudo apt install git -y

# Clone repository
cd ~
git clone https://github.com/LeDat0312/ads-automation.git ~/ads-automation

# Navigate vào thư mục
cd ~/ads-automation

# Verify
ls -la
```

**Kết quả mong đợi:**
```
app/
scripts/
requirements.txt
env.example
.gitignore
```

---

## ⚙️ BƯỚC 7: SETUP SAU KHI CLONE

### **Trên VPS:**

```bash
cd ~/ads-automation

# Tạo .env từ env.example
cp env.example .env

# Edit .env
nano .env
# Điền các giá trị:
# - DATABASE_URL
# - ACCESS_TOKEN
# - TELEGRAM_BOT_TOKEN
# - etc.

# Tạo venv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py
```

---

## 🔄 UPDATE CODE SAU NÀY

### **Trên máy local:**

```powershell
# Navigate đến thư mục project
cd "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"

# Make changes to files
# ...

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push origin main
```

### **Trên VPS:**

```bash
cd ~/ads-automation

# Pull latest changes
git pull origin main

# Restart services (nếu cần)
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker:*
```

---

## ✅ CHECKLIST

- [ ] Cài Git trên máy local
- [ ] Navigate đến: `C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds`
- [ ] Configure Git: `git config --global user.name "LeDat0312"`
- [ ] Initialize: `git init`
- [ ] Add files: `git add .`
- [ ] Commit: `git commit -m "Initial commit"`
- [ ] Tạo GitHub repository
- [ ] Tạo Personal Access Token
- [ ] Push: `git push -u origin main`
- [ ] Test clone về VPS: `git clone https://github.com/LeDat0312/ads-automation.git`

---

## 🎯 QUICK COMMANDS

### **Trên máy local (PowerShell):**

```powershell
# Navigate
cd "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"

# Initialize (chỉ làm 1 lần)
git init
git add .
git commit -m "Initial commit"

# Push (lần đầu)
git remote add origin https://github.com/LeDat0312/ads-automation.git
git branch -M main
git push -u origin main

# Update sau này
git add .
git commit -m "Update"
git push
```

### **Trên VPS:**

```bash
# Clone (chỉ làm 1 lần)
git clone https://github.com/LeDat0312/ads-automation.git ~/ads-automation

# Update sau này
cd ~/ads-automation
git pull origin main
```

---

**Bây giờ hãy chạy các lệnh ở Bước 2! 🚀**

