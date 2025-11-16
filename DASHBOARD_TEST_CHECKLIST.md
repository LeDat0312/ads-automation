# 📋 Dashboard Test Checklist

## ✅ Đã Fix

1. ✅ **Endpoint `/dashboard/pull-data`**
   - Nhận `date_from` và `date_to`
   - Dùng token từ Settings
   - Pull data từ tất cả accounts enabled
   - Lưu vào database với date chính xác

2. ✅ **Hàm `pull_facebook_data_with_time_range`**
   - Hỗ trợ `time_range` với `since`/`until` (inclusive)
   - Timezone Asia/Ho_Chi_Minh (UTC+7)
   - Dùng `breakdown=day` để có `date_start`
   - Parse actions và action_values đầy đủ

3. ✅ **Filter bar luôn hiển thị**
   - CSS: `display: block !important`
   - Không bị ẩn trên desktop

4. ✅ **Layout đúng thứ tự**
   - KPI Cards → Chi Tiết Quảng Cáo → Tổng Quan Theo Prefix

5. ✅ **Nút Làm mới**
   - Pull data từ Facebook trước
   - Sau đó load data từ database
   - Có loading state và toast notification

6. ✅ **Date filtering**
   - Sử dụng `func.date()` cho chính xác
   - Hỗ trợ timezone Asia/Ho_Chi_Minh

## 🧪 Test Cases

### Test 1: Pull Data "Hôm nay"
1. Mở dashboard
2. Kiểm tra console log: "✅ Đã pull dữ liệu: X adsets"
3. Kiểm tra KPI cards có số liệu > 0
4. Kiểm tra bảng "Chi Tiết Quảng Cáo" có dữ liệu

### Test 2: Quick Filters
1. Click "Hôm nay" → Kiểm tra dữ liệu hiển thị
2. Click "Hôm qua" → Kiểm tra dữ liệu hiển thị
3. Click "7 ngày qua" → Kiểm tra dữ liệu hiển thị
4. Click "30 ngày qua" → Kiểm tra dữ liệu hiển thị

### Test 3: Date Range Picker
1. Click vào date picker
2. Chọn date range cụ thể
3. Click "Cập nhật"
4. Kiểm tra dữ liệu được pull và hiển thị đúng

### Test 4: Filter Bar Visibility
1. Scroll trang xuống
2. Kiểm tra filter bar vẫn hiển thị (sticky)
3. Test trên desktop và mobile

### Test 5: Multi-select Filters
1. Click vào Account dropdown
2. Chọn nhiều accounts
3. Kiểm tra text hiển thị "X đã chọn"
4. Kiểm tra dữ liệu được filter đúng

### Test 6: Search Box
1. Nhập tên adset vào search box
2. Kiểm tra kết quả được filter
3. Test debounce (không gọi API quá nhiều)

### Test 7: Nút Làm mới
1. Click nút "🔄 Làm mới"
2. Kiểm tra loading state
3. Kiểm tra toast notification
4. Kiểm tra dữ liệu được cập nhật

### Test 8: Batch Actions
1. Chọn checkbox một vài adsets
2. Kiểm tra batch action bar hiển thị
3. Click "Bật tất cả" hoặc "Tắt tất cả"
4. Kiểm tra kết quả

### Test 9: Layout Order
1. Kiểm tra thứ tự:
   - KPI Cards (trên cùng)
   - Chi Tiết Quảng Cáo (giữa)
   - Tổng Quan Theo Prefix (dưới)

### Test 10: Empty State
1. Chọn date range không có dữ liệu
2. Kiểm tra empty state hiển thị đúng
3. Kiểm tra message gợi ý

## 🔍 Debug Commands

### Kiểm tra logs trên VPS:
```bash
sudo supervisorctl tail -100 ads-automation-api
```

### Kiểm tra database:
```bash
psql -U postgres -d ads_automation -c "SELECT COUNT(*) FROM ads_metrics WHERE date >= CURRENT_DATE - INTERVAL '1 day';"
```

### Test API trực tiếp:
```bash
curl -X POST http://localhost:8000/dashboard/pull-data \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date_from": "2025-01-15", "date_to": "2025-01-15"}'
```

## ⚠️ Common Issues

1. **Dữ liệu = 0:**
   - Kiểm tra token Facebook có hợp lệ không
   - Kiểm tra accounts có được bật trong Settings không
   - Kiểm tra date range có đúng không
   - Kiểm tra logs để xem lỗi từ Facebook API

2. **Filter bar bị ẩn:**
   - Kiểm tra CSS: `display: block !important`
   - Kiểm tra z-index

3. **Layout sai thứ tự:**
   - Kiểm tra HTML: stats-grid → table-container → prefix-summary-section

4. **Pull data không hoạt động:**
   - Kiểm tra endpoint `/dashboard/pull-data` có tồn tại không
   - Kiểm tra token có được decrypt đúng không
   - Kiểm tra accounts có được lấy đúng không

