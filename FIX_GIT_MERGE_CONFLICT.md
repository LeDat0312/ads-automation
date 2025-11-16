# 🔧 FIX GIT MERGE CONFLICT

## 🔍 VẤN ĐỀ

Lỗi: "Your local changes to the following files would be overwritten by merge"

**Nguyên nhân:** File `scripts/init_db.py` đã được sửa trên VPS nhưng chưa commit.

---

## ✅ CÁCH 1: STASH CHANGES (KHUYẾN NGHỊ)

### **Stash local changes, pull, rồi apply lại:**

```bash
cd ~/ads-automation

# Stash local changes
git stash

# Pull latest changes
git pull origin main

# Apply stashed changes (nếu cần)
git stash pop
```

**Nếu có conflict sau `git stash pop`:**
- Giữ version từ GitHub (đã được fix)
- Hoặc merge thủ công

---

## ✅ CÁCH 2: COMMIT LOCAL CHANGES

### **Commit local changes trước:**

```bash
cd ~/ads-automation

# Check changes
git status

# Add changes
git add scripts/init_db.py

# Commit
git commit -m "Fix init_db.py on VPS"

# Pull (sẽ merge hoặc rebase)
git pull origin main
```

**Nếu có conflict:**
- Git sẽ hỏi merge
- Chọn version từ GitHub (đã được fix)

---

## ✅ CÁCH 3: DISCARD LOCAL CHANGES (NẾU KHÔNG CẦN)

### **Bỏ local changes và dùng version từ GitHub:**

```bash
cd ~/ads-automation

# Discard local changes
git checkout -- scripts/init_db.py

# Pull
git pull origin main
```

**⚠️ Lưu ý:** Sẽ mất tất cả thay đổi local trong file này.

---

## 🎯 KHUYẾN NGHỊ

**Dùng Cách 3 (Discard)** vì:
- ✅ Version trên GitHub đã được fix
- ✅ Không cần giữ local changes
- ✅ Nhanh nhất

---

## ⚡ QUICK FIX

```bash
cd ~/ads-automation

# Discard local changes
git checkout -- scripts/init_db.py

# Pull
git pull origin main

# Verify
cat scripts/init_db.py | head -30
```

---

**Chạy lệnh Quick Fix ở trên! 🚀**


