# ✅ CHECK VÀ PUSH CODE LÊN GITHUB

## 🔍 BƯỚC 1: Check trạng thái hiện tại

Chạy các lệnh sau trong PowerShell (từng lệnh một):

```powershell
# 1. Vào thư mục Git (nếu chưa ở đó)
cd "C:\Users\Foxy\Downloads\File 5h_4-11\Code 18h 4-11 bản 3 sheet"

# 2. Check status
git status

# 3. Check xem có commit mới chưa push không
git log origin/main..HEAD --oneline

# 4. Check commit gần nhất
git log --oneline -5
```

**Nếu `git log origin/main..HEAD` có output → Có commit chưa push!**

---

## 📤 BƯỚC 2: Push code lên GitHub

Nếu có commit chưa push:

```powershell
# Push lên GitHub
git push origin main
```

**Sẽ hỏi username/password:**
- Username: `LeDat0312`
- Password: Nhập password GitHub của bạn

---

## ✅ BƯỚC 3: Verify trên GitHub

1. Mở trình duyệt: `https://github.com/LeDat0312/ads-automation`
2. Check **Commits** tab - phải thấy commit mới nhất
3. Check file `app/services/command_processor.py`:
   - Click vào file
   - Tìm `progress_callback` hoặc `_pull_and_save_data`
   - Nếu thấy → Code đã được push!

---

## 🔄 BƯỚC 4: Pull về VPS

Trên VPS, chạy:

```bash
cd ~/ads-automation

# Fetch updates
git fetch origin

# Check xem có commit mới không
git log HEAD..origin/main --oneline

# Nếu có, pull về
git pull origin main

# Verify code mới
grep -n "progress_callback" app/services/command_processor.py
```

**Nếu thấy output → Code đã được update!**

---

## 🚨 NẾU CODE CHƯA ĐƯỢC COMMIT

Nếu `git status` cho thấy có file "modified" hoặc "untracked":

```powershell
# Add các file đã sửa
git add app/services/command_processor.py
git add app/workers/telegram_worker.py
git add app/api/routes/telegram.py

# Commit
git commit -m "Add progress updates and error logging for commands"

# Push
git push origin main
```

---

## 📋 CHECKLIST

- [ ] `git status` - không có thay đổi chưa commit
- [ ] `git log origin/main..HEAD` - không có output (đã push hết)
- [ ] Check trên GitHub - thấy commit mới
- [ ] Check file trên GitHub - có code mới
- [ ] Pull về VPS - thành công
- [ ] Verify trên VPS - có code mới

---

**Chạy các bước trên để verify và push code! 🚀**


