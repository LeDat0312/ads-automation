# 🔧 FIX AD_ACCOUNT_IDS VALIDATION ERROR

## ❌ VẤN ĐỀ

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
AD_ACCOUNT_IDS
  Input should be a valid string [type=string_type, input_value=['act_723686686812438', 'act_2827767517395636'], input_type=list]
```

**Nguyên nhân:** `AD_ACCOUNT_IDS` trong `.env` đang là list Python thay vì string.

---

## ✅ GIẢI PHÁP

### **BƯỚC 1: Check file `.env`:**

```bash
cd ~/ads-automation
grep "AD_ACCOUNT_IDS" .env
```

**Nếu thấy:**
```env
AD_ACCOUNT_IDS=['act_723686686812438', 'act_2827767517395636']
```

**Cần sửa thành:**
```env
AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636
```

### **BƯỚC 2: Sửa file `.env`:**

```bash
cd ~/ads-automation
nano .env
```

**Tìm dòng `AD_ACCOUNT_IDS` và sửa:**

**❌ SAI:**
```env
AD_ACCOUNT_IDS=['act_723686686812438', 'act_2827767517395636']
```

**✅ ĐÚNG:**
```env
AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636
```

**Lưu:** `Ctrl+X`, `Y`, `Enter`

### **BƯỚC 3: Verify:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test load settings
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'✅ AD_ACCOUNT_IDS: {settings.AD_ACCOUNT_IDS}')
print(f'✅ ad_account_ids_list: {settings.ad_account_ids_list}')
"
```

**Kết quả mong đợi:**
```
✅ AD_ACCOUNT_IDS: act_723686686812438,act_2827767517395636
✅ ad_account_ids_list: ['act_723686686812438', 'act_2827767517395636']
```

### **BƯỚC 4: Test worker:**

```bash
# Test import worker
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker import OK')"

# Test chạy worker
timeout 5 python -m app.workers.telegram_worker 00 2>&1 || true
```

### **BƯỚC 5: Restart workers:**

```bash
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

---

## 🚀 QUICK FIX

### **Sửa bằng sed:**

```bash
cd ~/ads-automation

# Backup
cp .env .env.backup

# Sửa AD_ACCOUNT_IDS
sed -i "s/AD_ACCOUNT_IDS=\['.*'\]/AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636/" .env

# Hoặc nếu format khác
sed -i "s/AD_ACCOUNT_IDS=.*/AD_ACCOUNT_IDS=act_723686686812438,act_2827767517395636/" .env

# Verify
grep "AD_ACCOUNT_IDS" .env
```

---

## ✅ VERIFY

```bash
# Check .env
grep "AD_ACCOUNT_IDS" ~/ads-automation/.env

# Test settings
cd ~/ads-automation
source venv/bin/activate
python -c "from app.core.config import get_settings; s = get_settings(); print('✅ OK:', s.ad_account_ids_list)"
```

---

## 📋 CHECKLIST

- [ ] Check file `.env`
- [ ] Sửa `AD_ACCOUNT_IDS` thành string format
- [ ] Verify settings load OK
- [ ] Test worker import
- [ ] Test worker chạy
- [ ] Restart workers
- [ ] Check status

---

**Bây giờ hãy sửa file `.env`! 🚀**


