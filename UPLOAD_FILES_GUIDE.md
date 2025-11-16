# 📤 HƯỚNG DẪN UPLOAD FILES

## 📁 THƯ MỤC ĐÍCH

```
/home/adsuser/ads-automation/
```

---

## ✅ DANH SÁCH FILES CẦN UPLOAD

### **1. Thư mục `app/` (TOÀN BỘ):**

Upload toàn bộ thư mục `app/` bao gồm:

```
app/
├── __init__.py
├── main.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── database.py
├── models/
│   ├── __init__.py
│   ├── logic_rule.py
│   ├── telegram_update.py
│   ├── job.py
│   └── rule_template.py
├── schemas/
│   ├── __init__.py
│   └── logic_rule.py
├── services/
│   ├── __init__.py
│   ├── automation.py
│   ├── facebook_api.py
│   ├── logics.py
│   ├── telegram_bot.py
│   ├── job_queue.py
│   ├── command_processor.py
│   ├── rule_manager.py
│   └── ... (tất cả files trong services/)
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── rules.py
│       ├── telegram.py
│       ├── dashboard.py
│       ├── templates.py
│       └── templates_ui.py
└── workers/
    ├── __init__.py
    └── telegram_worker.py
```

### **2. Thư mục `scripts/`:**

```
scripts/
└── init_db.py
```

### **3. Root files:**

- `requirements.txt`
- `env.example`

---

## 🚀 CÁCH UPLOAD

### **Option 1: Qua MobaXterm File Manager (Dễ nhất)**

1. **Mở MobaXterm**
2. **Click icon "File manager"** (bên trái)
3. **Navigate đến:** `/home/adsuser/ads-automation`
   - Nếu chưa có thư mục, tạo trước:
     ```bash
     mkdir -p ~/ads-automation
     ```
4. **Upload files:**
   - Kéo thả **toàn bộ thư mục `app/`** từ máy local vào
   - Kéo thả **toàn bộ thư mục `scripts/`** từ máy local vào
   - Kéo thả **`requirements.txt`**
   - Kéo thả **`env.example`**

### **Option 2: Qua SCP (từ máy local)**

**Windows PowerShell:**

```powershell
# Navigate đến thư mục project
cd "C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet"

# Upload app folder
scp -r app adsuser@your-server-ip:~/ads-automation/

# Upload scripts folder
scp -r scripts adsuser@your-server-ip:~/ads-automation/

# Upload files
scp requirements.txt env.example adsuser@your-server-ip:~/ads-automation/
```

---

## ✅ VERIFY SAU KHI UPLOAD

### **Trên server:**

```bash
cd ~/ads-automation

# Check structure
ls -la

# Check app folder
ls -la app/

# Check các files quan trọng
ls -la app/main.py
ls -la app/core/config.py
ls -la app/core/database.py
ls -la requirements.txt
ls -la scripts/init_db.py
```

**Kết quả mong đợi:**
```
app/
scripts/
requirements.txt
env.example
```

### **Check chi tiết:**

```bash
# Check app structure
tree -L 3 app/ 2>/dev/null || find app -type f -name "*.py" | head -20

# Check scripts
ls -la scripts/

# Check root files
ls -la *.txt *.example 2>/dev/null
```

---

## 📋 TÓM TẮT - FILES TỐI THIỂU

**Bắt buộc phải có:**
1. ✅ Toàn bộ thư mục `app/`
2. ✅ Toàn bộ thư mục `scripts/`
3. ✅ `requirements.txt`
4. ✅ `env.example`

**Không cần upload:**
- ❌ Files Google Apps Script (`.gs`, `.html` cho GAS)
- ❌ `.env` (sẽ tạo trên server)
- ❌ `venv/` (sẽ tạo trên server)
- ❌ `__pycache__/` folders
- ❌ `.pyc` files

---

## 🔧 NẾU GẶP LỖI PERMISSION

```bash
# Fix permissions sau khi upload
cd ~/ads-automation
chmod -R 755 app/
chmod -R 755 scripts/
chmod 644 requirements.txt
chmod 644 env.example
```

---

## ✅ CHECKLIST

- [ ] Tạo thư mục: `mkdir -p ~/ads-automation`
- [ ] Upload `app/` folder
- [ ] Upload `scripts/` folder
- [ ] Upload `requirements.txt`
- [ ] Upload `env.example`
- [ ] Verify: `ls -la ~/ads-automation`
- [ ] Check files quan trọng: `ls -la app/main.py`

---

**Bây giờ hãy upload files vào `/home/adsuser/ads-automation/`! 🚀**

