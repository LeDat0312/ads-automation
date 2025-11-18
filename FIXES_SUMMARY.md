# Tổng hợp các fixes cần thực hiện

## 1. Đổi default date range về today
- File: `app/services/facebook_api.py`
- Thay đổi: Đổi default `date_preset` từ `"yesterday"` sang `"today"` và xử lý logic để dùng `date_preset=today` thay vì `yesterday`

## 2. Lấy budget từ Facebook API
- File: `app/services/facebook_api.py`, `app/api/routes/dashboard.py`
- Thay đổi: 
  - Tạo hàm `fetch_adset_budgets()` để lấy budget từ adset objects
  - Thêm budget vào response của `/dashboard/details`

## 3. Implement drill-down filtering
- File: `app/api/routes/dashboard.py`
- Thay đổi:
  - Thêm `campaign_id` và `adset_id` filters vào `/dashboard/details`
  - Filter data theo campaign_id khi level=adset hoặc level=ad
  - Filter data theo adset_id khi level=ad

## 4. Tối ưu tốc độ
- File: `app/api/routes/dashboard.py`
- Thay đổi:
  - Cache data trong memory (optional)
  - Giảm số lần gọi API bằng cách batch requests

## 5. Sửa endpoint action để bật/tắt
- File: `app/api/routes/dashboard.py`
- Thay đổi:
  - Sửa `/dashboard/action/{action}/{item_id}` để gọi Facebook API thực sự
  - Hỗ trợ campaign, adset, và ad
  - Sử dụng `pause_adsets()`, `resume_adsets()`, `pause_campaign()`, etc.

## 6. Cải thiện error logging
- File: `app/services/facebook_api.py`
- Thay đổi:
  - Log response body từ Facebook API khi có lỗi
  - Thêm chi tiết hơn trong error messages



