# Dashboard Refactor - Facebook Ads Manager Style

## Tóm tắt thay đổi

1. ✅ Header: Chỉ 1 nút Làm mới
2. 🔄 Sticky Filter Bar: Gọn nhẹ, luôn hiển thị trên desktop
3. 🔄 LocalStorage: Lưu filter state, restore khi F5
4. 🔄 Date Range: Fix until exclusive (until=date+1) cho Facebook API
5. 🔄 Layout: Chi Tiết Quảng Cáo lên trước Tổng Quan Theo Prefix
6. 🔄 Toggle Switch: Bật/tắt adset trực tiếp trong bảng
7. 🔄 Budget Editor: Inline editor với +/- shortcuts
8. 🔄 Skeleton Loading: Cải thiện UX

## Files cần sửa

- `app/api/routes/dashboard.py`: HTML/CSS/JS cho dashboard
- `app/services/facebook_api.py`: Thêm hàm `pull_facebook_data_with_time_range` với until exclusive

