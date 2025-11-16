# 📋 HƯỚNG DẪN COPY CODE VÀ PUSH LÊN GITHUB

## ⚠️ VẤN ĐỀ

Code mới đang ở thư mục: `Code 18h 4-11 bản 3 sheet`
Cần copy sang thư mục Git: `PythonUpdateMetaAds`

---

## 🔧 CÁCH 1: Copy thủ công (Đơn giản nhất)

### **Bước 1: Mở 2 cửa sổ File Explorer**

1. Cửa sổ 1: `C:\Users\Foxy\Downloads\File 5h_4-11\Code 18h 4-11 bản 3 sheet\app`
2. Cửa sổ 2: `C:\Users\Foxy\Downloads\File 5h_4-11\PythonUpdateMetaAds\app`

### **Bước 2: Copy các file**

**Copy file 1:**
- Từ: `Code 18h 4-11 bản 3 sheet\app\services\command_processor.py`
- Đến: `PythonUpdateMetaAds\app\services\command_processor.py`
- **Ghi đè nếu hỏi**

**Copy file 2:**
- Từ: `Code 18h 4-11 bản 3 sheet\app\workers\telegram_worker.py`
- Đến: `PythonUpdateMetaAds\app\workers\telegram_worker.py`
- **Ghi đè nếu hỏi**

**Copy file 3:**
- Từ: `Code 18h 4-11 bản 3 sheet\app\api\routes\telegram.py`
- Đến: `PythonUpdateMetaAds\app\api\routes\telegram.py`
- **Ghi đè nếu hỏi**

---

## 🔧 CÁCH 2: Dùng PowerShell (Nếu copy thủ công không được)

Mở PowerShell và chạy từng lệnh:

```powershell
# Vào thư mục Git
cd "C:\Users\Foxy\Downloads\File 5h_4-11\PythonUpdateMetaAds"

# Copy file 1
Copy-Item "..\Code 18h 4-11 bản 3 sheet\app\services\command_processor.py" -Destination "app\services\command_processor.py" -Force

# Copy file 2
Copy-Item "..\Code 18h 4-11 bản 3 sheet\app\workers\telegram_worker.py" -Destination "app\workers\telegram_worker.py" -Force

# Copy file 3
Copy-Item "..\Code 18h 4-11 bản 3 sheet\app\api\routes\telegram.py" -Destination "app\api\routes\telegram.py" -Force

# Check status
git status
```

---

## 📤 BƯỚC 3: Commit và Push

Sau khi copy xong:

```powershell
# Vào thư mục Git
cd "C:\Users\Foxy\Downloads\File 5h_4-11\PythonUpdateMetaAds"

# Add các file
git add app/services/command_processor.py
git add app/workers/telegram_worker.py
git add app/api/routes/telegram.py

# Check status
git status

# Commit
git commit -m "Add progress updates and error logging for commands"

# Push
git push origin main
```

**Sẽ hỏi username/password:**
- Username: `LeDat0312`
- Password: Nhập password GitHub

---

## ✅ BƯỚC 4: Verify

1. **Trên GitHub:**
   - Mở: `https://github.com/LeDat0312/ads-automation`
   - Check commit mới nhất
   - Check file `app/services/command_processor.py` - tìm `progress_callback`

2. **Trên VPS:**
   ```bash
   cd ~/ads-automation
   git pull origin main
   grep -n "progress_callback" app/services/command_processor.py
   ```

---

**Làm theo các bước trên! 🚀**


