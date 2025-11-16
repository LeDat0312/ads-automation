# 📁 DANH SÁCH FILES CẦN UPLOAD

## 📋 CẤU TRÚC THƯ MỤC CẦN UPLOAD

```
ads-automation/
├── app/                          # ✅ QUAN TRỌNG - Toàn bộ thư mục app
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/                     # ✅ QUAN TRỌNG
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── models/                   # ✅ QUAN TRỌNG
│   │   ├── __init__.py
│   │   ├── logic_rule.py
│   │   ├── telegram_update.py
│   │   └── job.py
│   │
│   ├── schemas/                  # ✅ QUAN TRỌNG
│   │   ├── __init__.py
│   │   └── logic_rule.py
│   │
│   ├── services/                 # ✅ QUAN TRỌNG
│   │   ├── __init__.py
│   │   ├── automation.py
│   │   ├── facebook_api.py
│   │   ├── logics.py
│   │   ├── telegram_bot.py
│   │   ├── job_queue.py
│   │   └── command_processor.py
│   │
│   ├── api/                      # ✅ QUAN TRỌNG
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── rules.py
│   │       ├── telegram.py
│   │       ├── dashboard.py
│   │       ├── templates.py
│   │       └── templates_ui.py
│   │
│   └── workers/                  # ✅ QUAN TRỌNG
│       ├── __init__.py
│       └── telegram_worker.py
│
├── scripts/                      # ✅ QUAN TRỌNG
│   └── init_db.py
│
├── requirements.txt              # ✅ QUAN TRỌNG
├── env.example                   # ✅ QUAN TRỌNG
└── .gitignore                    # Optional
```

---

## ✅ CHECKLIST - FILES CẦN UPLOAD

### **1. Thư mục `app/` (TOÀN BỘ):**
- [ ] `app/__init__.py`
- [ ] `app/main.py`
- [ ] `app/core/` (toàn bộ)
- [ ] `app/models/` (toàn bộ)
- [ ] `app/schemas/` (toàn bộ)
- [ ] `app/services/` (toàn bộ)
- [ ] `app/api/` (toàn bộ)
- [ ] `app/workers/` (toàn bộ)

### **2. Thư mục `scripts/`:**
- [ ] `scripts/init_db.py`

### **3. Root files:**
- [ ] `requirements.txt`
- [ ] `env.example`

### **4. Optional (nếu có):**
- [ ] `.gitignore`
- [ ] `README.md`
- [ ] `alembic.ini` (nếu dùng migrations)

---

## 🚀 CÁCH UPLOAD

### **Option 1: Upload toàn bộ thư mục (Dễ nhất)**

1. **Mở MobaXterm File Manager**
2. **Navigate đến:** `/home/ubuntu/ads-automation`
3. **Upload:**
   - Kéo thả **toàn bộ thư mục `app/`** vào
   - Kéo thả **toàn bộ thư mục `scripts/`** vào
   - Kéo thả **`requirements.txt`**
   - Kéo thả **`env.example`**

### **Option 2: Upload từng file (nếu cần)**

Upload theo thứ tự:
1. Tạo cấu trúc thư mục trước
2. Upload files vào từng thư mục

---

## 📝 VERIFY SAU KHI UPLOAD

```bash
cd ~/ads-automation

# Check cấu trúc
tree -L 3
# Hoặc
find . -type f -name "*.py" | head -20

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
app/__init__.py
app/main.py
app/core/
app/core/config.py
app/core/database.py
app/models/
app/services/
app/api/
app/workers/
scripts/
scripts/init_db.py
requirements.txt
env.example
```

---

## ⚠️ LƯU Ý

### **KHÔNG upload:**
- ❌ `.env` file (sẽ tạo trên server)
- ❌ `__pycache__/` folders
- ❌ `.pyc` files
- ❌ `venv/` folder (sẽ tạo trên server)
- ❌ Files Google Apps Script (`.gs`, `.html` cho GAS)

### **CHỈ upload Python files:**
- ✅ `.py` files
- ✅ `requirements.txt`
- ✅ `env.example`
- ✅ `scripts/` folder

---

## 🔍 KIỂM TRA SAU KHI UPLOAD

```bash
cd ~/ads-automation

# Check structure
ls -la

# Check app folder
ls -la app/

# Check core
ls -la app/core/

# Check models
ls -la app/models/

# Check services
ls -la app/services/

# Check scripts
ls -la scripts/
```

---

## 📋 TÓM TẮT - FILES TỐI THIỂU

**Bắt buộc phải có:**
1. ✅ `app/` folder (toàn bộ)
2. ✅ `scripts/init_db.py`
3. ✅ `requirements.txt`
4. ✅ `env.example`

**Nếu thiếu bất kỳ file nào, sẽ gặp lỗi khi chạy!**

---

**Upload toàn bộ thư mục `app/` và `scripts/`, cùng với `requirements.txt` và `env.example`! 🚀**

