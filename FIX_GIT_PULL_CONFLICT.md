# 🔧 FIX GIT PULL CONFLICT

## ❌ VẤN ĐỀ

```
error: Your local changes to the following files would be overwritten by merge:
        env.example
Please commit your changes or stash them before you merge.
```

**Nguyên nhân:** Có local changes trong `env.example` chưa được commit.

---

## ✅ GIẢI PHÁP

### **Option 1: Stash local changes (khuyên dùng)**

```bash
cd ~/ads-automation

# Stash local changes
git stash

# Pull code mới
git pull origin main

# Nếu cần restore local changes sau
# git stash pop
```

### **Option 2: Commit local changes**

```bash
cd ~/ads-automation

# Commit local changes
git add env.example
git commit -m "Update env.example locally"

# Pull code mới
git pull origin main

# Nếu có conflict, resolve và commit
```

### **Option 3: Discard local changes (nếu không cần)**

```bash
cd ~/ads-automation

# Discard local changes
git checkout -- env.example

# Pull code mới
git pull origin main
```

---

## 🚀 QUICK FIX (Khuyên dùng)

```bash
cd ~/ads-automation

# Stash và pull
git stash
git pull origin main

# Xóa Python cache
find ~/ads-automation -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find ~/ads-automation -name "*.pyc" -delete 2>/dev/null || true

# Test import
source venv/bin/activate
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker import OK')"
```

---

## 📋 CHECKLIST

- [ ] Stash local changes
- [ ] Pull code mới
- [ ] Xóa Python cache
- [ ] Test import worker
- [ ] Restart worker

---

**Bây giờ hãy stash và pull! 🚀**


