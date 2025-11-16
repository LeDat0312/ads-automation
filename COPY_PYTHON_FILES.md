# 📋 COPY PYTHON FILES - HƯỚNG DẪN

## 🎯 MỤC TIÊU

Copy chỉ những files cần thiết cho dự án Python, bỏ qua:
- ❌ Files hướng dẫn (.md)
- ❌ Files Google Apps Script (.gs, .html)

---

## ✅ FILES SẼ ĐƯỢC COPY

1. ✅ **app/** (toàn bộ thư mục)
2. ✅ **scripts/** (toàn bộ thư mục)
3. ✅ **requirements.txt**
4. ✅ **env.example**
5. ✅ **.gitignore**

---

## 🚀 CÁCH THỰC HIỆN

### **Option 1: Dùng PowerShell Script (Tự động)**

1. **Lưu script `copy_python_files.ps1` vào máy local**

2. **Chạy script:**
   ```powershell
   # Navigate đến thư mục có script
   cd "C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet"
   
   # Chạy script
   .\copy_python_files.ps1
   ```

3. **Script sẽ tự động copy các files cần thiết**

### **Option 2: Copy thủ công (PowerShell)**

```powershell
# Set paths
$sourceDir = "C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet"
$destDir = "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"

# Create destination if not exists
New-Item -ItemType Directory -Path $destDir -Force

# Copy app/ folder
Copy-Item -Path "$sourceDir\app" -Destination $destDir -Recurse -Force

# Copy scripts/ folder
Copy-Item -Path "$sourceDir\scripts" -Destination $destDir -Recurse -Force

# Copy requirements.txt
Copy-Item -Path "$sourceDir\requirements.txt" -Destination $destDir -Force

# Copy env.example
Copy-Item -Path "$sourceDir\env.example" -Destination $destDir -Force

# Copy .gitignore
Copy-Item -Path "$sourceDir\.gitignore" -Destination $destDir -Force

Write-Host "✅ Copy completed!" -ForegroundColor Green
```

### **Option 3: Copy từng thư mục (File Explorer)**

1. **Mở File Explorer**
2. **Navigate đến:** `C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet`
3. **Copy các thư mục/files sau:**
   - `app/` folder
   - `scripts/` folder
   - `requirements.txt`
   - `env.example`
   - `.gitignore`
4. **Paste vào:** `C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds`

---

## ✅ VERIFY SAU KHI COPY

```powershell
# Navigate đến thư mục đích
cd "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"

# Check files
ls

# Check structure
ls app/
ls scripts/
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

## 📋 SAU KHI COPY

### **1. Initialize Git:**

```powershell
cd "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"

git init
git add .
git commit -m "Initial commit: Facebook Ads Automation System"
```

### **2. Push lên GitHub:**

```powershell
git remote add origin https://github.com/LeDat0312/ads-automation.git
git branch -M main
git push -u origin main
```

---

## ✅ CHECKLIST

- [ ] Copy `app/` folder
- [ ] Copy `scripts/` folder
- [ ] Copy `requirements.txt`
- [ ] Copy `env.example`
- [ ] Copy `.gitignore`
- [ ] Verify files: `ls`
- [ ] Initialize Git: `git init`
- [ ] Commit: `git commit -m "Initial commit"`
- [ ] Push: `git push -u origin main`

---

**Chọn một trong 3 cách trên để copy files! 🚀**


