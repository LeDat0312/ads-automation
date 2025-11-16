# ✅ TEST CONFIG FIX

## 🔧 ĐÃ SỬA

- ✅ Đổi `AD_ACCOUNT_IDS` type từ `Union[str, List[str]]` thành `str`
- ✅ Xóa `@validator` decorator (gây conflict với Pydantic)
- ✅ Chuyển `parse_ad_account_ids` thành method thông thường
- ✅ Sửa `ad_account_ids_list` property để luôn parse từ string

---

## 🚀 TEST TRÊN VPS

### **BƯỚC 1: Pull code mới:**

```bash
cd ~/ads-automation
git pull origin main
```

### **BƯỚC 2: Xóa Python cache:**

```bash
cd ~/ads-automation
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

### **BƯỚC 3: Test load settings:**

```bash
source venv/bin/activate

# Unset env vars trước
unset AD_ACCOUNT_IDS 2>/dev/null || true

# Test
python -c "
from app.core.config import get_settings
settings = get_settings()
print(f'✅ AD_ACCOUNT_IDS: {settings.AD_ACCOUNT_IDS}')
print(f'✅ Type: {type(settings.AD_ACCOUNT_IDS)}')
print(f'✅ ad_account_ids_list: {settings.ad_account_ids_list}')
"
```

**Kết quả mong đợi:**
```
✅ AD_ACCOUNT_IDS: act_723686686812438,act_2827767517395636
✅ Type: <class 'str'>
✅ ad_account_ids_list: ['act_723686686812438', 'act_2827767517395636']
```

### **BƯỚC 4: Test worker:**

```bash
# Test import worker
python -c "from app.workers.telegram_worker import worker_loop; print('✅ Worker import OK')"

# Test chạy worker
timeout 5 python -m app.workers.telegram_worker 00 2>&1 || true
```

**Kết quả mong đợi:**
```
🚀 Starting Telegram worker: 00
(đợi 5 giây, không có lỗi)
```

### **BƯỚC 5: Restart workers:**

```bash
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

**Kết quả mong đợi:**
```
ads-automation-api                  RUNNING   pid ..., uptime ...
ads-automation-worker:ads-automation-worker_00   RUNNING   pid ..., uptime ...
ads-automation-worker:ads-automation-worker_01   RUNNING   pid ..., uptime ...
```

---

## ✅ VERIFY

### **Check logs:**

```bash
# Check worker logs
sudo tail -50 /var/log/ads-automation/worker.out.log

# Phải thấy:
# 🚀 Starting Telegram worker: worker-00
# 🚀 Starting Telegram worker: worker-01
```

---

## 📋 CHECKLIST

- [ ] Pull code mới
- [ ] Xóa Python cache
- [ ] Test load settings
- [ ] Test worker import
- [ ] Test worker chạy
- [ ] Restart workers
- [ ] Check status và logs

---

**Bây giờ hãy pull code và test! 🚀**


