# 🔧 FIX GIT CONFLICT

## ❌ VẤN ĐỀ

```
error: Your local changes to the following files would be overwritten by merge:
        app/core/database.py
```

## ✅ GIẢI PHÁP

### **Cách 1: Stash local changes (khuyến nghị)**

```bash
# Stash local changes
git stash

# Pull code mới
git pull origin main

# Nếu cần, apply lại local changes (thường không cần)
# git stash pop
```

### **Cách 2: Commit local changes**

```bash
# Commit local changes
git add app/core/database.py
git commit -m "Local changes to database.py"

# Pull code mới
git pull origin main

# Nếu có conflict, resolve và commit lại
```

### **Cách 3: Discard local changes (nếu không quan trọng)**

```bash
# Xem local changes
git diff app/core/database.py

# Nếu không quan trọng, discard
git checkout -- app/core/database.py

# Pull code mới
git pull origin main
```

## 🎯 KHUYẾN NGHỊ

Dùng **Cách 1 (stash)** vì:
- Giữ lại local changes nếu cần
- Dễ rollback nếu có vấn đề
- Không tạo commit không cần thiết

