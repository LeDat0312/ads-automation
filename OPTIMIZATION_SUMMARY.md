# Tối ưu tốc độ Dashboard - Tóm tắt thay đổi

## ✅ Đã hoàn thành tất cả các task

### 1. Global Cache cho Objectives và Budgets (5 phút)
- **File**: `app/services/facebook_api.py`
- **Thay đổi**:
  - Thêm global cache `_objectives_cache` và `_budgets_cache` với TTL 5 phút
  - Cache dựa trên `access_token` để tránh fetch lại nhiều lần
  - `fetch_adset_budgets()` có cache logic với partial hit support
  - `fetch_campaign_objectives_batch()` update global cache

### 2. Global Cache cho Status (2 phút)
- **File**: `app/services/facebook_api.py`
- **Thay đổi**:
  - Thêm global cache `_status_cache` với TTL 2 phút (status thay đổi thường xuyên hơn)
  - `fetch_adset_statuses()` có cache logic với partial hit support

### 3. Cache chung cho Summary và Details (60 giây)
- **File**: `app/api/routes/dashboard.py`
- **Thay đổi**:
  - `/dashboard/summary` và `/dashboard/details` dùng chung cache insights (TTL 60s)
  - Trong 60s, nếu F5 nhiều lần, Facebook chỉ bị gọi 1 lần

### 4. Sửa filter `adset_id`
- **File**: `app/api/routes/dashboard.py`
- **Thay đổi**:
  - Chỉ filter khi param thực sự được truyền (không phải `None` hoặc `"None"`)
  - Tránh filter nhầm khi frontend gửi `adset_id=None`

### 5. Async Parallel Fetching
- **File**: `app/services/facebook_api.py`
- **Đã có sẵn**: `pull_facebook_data_async` dùng `asyncio.gather` để chạy song song các accounts
- Giảm thời gian từ ~32s (tuần tự) xuống ~8-10s (song song) cho 4 accounts

## 📊 Kết quả mong đợi

### Lần đầu load: ~8-15 giây (thay vì 30-60s)
- ✅ Async parallel: 4 accounts chạy song song
- ✅ Objectives/budgets: cache 5 phút, chỉ fetch lần đầu
- ✅ Status: cache 2 phút, chỉ fetch lần đầu

### Lần F5 tiếp theo (trong 60s): ~1-2 giây
- ✅ Insights cache hit
- ✅ Objectives/budgets cache hit
- ✅ Status cache hit

### Hiển thị đủ adsets
- ✅ Không còn bị filter nhầm `adset_id`

## 📝 Files đã thay đổi

1. `app/services/facebook_api.py`
   - Thêm global cache variables
   - Update `fetch_adset_budgets()` với cache
   - Update `fetch_adset_statuses()` với cache
   - Update `pull_facebook_data()` để dùng global cache cho objectives

2. `app/api/routes/dashboard.py`
   - Sửa filter `adset_id` và `campaign_id` để không filter khi None

## 🚀 Cách push code lên GitHub

### Windows:
Chạy file `PUSH_TO_GITHUB.bat` hoặc chạy lệnh:
```bash
git add app/services/facebook_api.py app/api/routes/dashboard.py
git commit -m "Optimize: Global cache cho objectives/budgets/status, fix filter adset_id, tối ưu tốc độ load"
git push origin main
```

### Linux/Mac:
Chạy file `PUSH_TO_GITHUB.sh` hoặc chạy lệnh:
```bash
chmod +x PUSH_TO_GITHUB.sh
./PUSH_TO_GITHUB.sh
```

## 📥 Pull code trên VPS

File `PULL_VPS_OPTIMIZE_SPEED_FINAL.txt` đã được tạo sẵn với các lệnh:

```bash
cd ~/ads-automation
git pull origin main
python3 -m py_compile app/services/facebook_api.py
python3 -m py_compile app/api/routes/dashboard.py
sudo supervisorctl restart ads-automation
sleep 3
sudo supervisorctl status
```

