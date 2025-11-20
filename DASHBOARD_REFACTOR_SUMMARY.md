# Dashboard Refactor Summary - Theo Spec Mới

## ✅ Đã Hoàn Thành

### Backend (`app/services/facebook_api.py`)
1. **Fix mapping Facebook API fields theo spec:**
   - Parse `cost_per_action_type` để lấy `cost_per_checkout_initiated` và `cost_per_purchase`
   - Ưu tiên `offsite_conversion.fb_pixel_purchase` cho `purchase_value`
   - Đảm bảo `omni_initiated_checkout` và `omni_purchase` được parse đúng

### Backend (`app/api/routes/dashboard.py`)
1. **Tách biệt summary_adsets và table_adsets:**
   - Summary tính từ `adset_map_summary` (chỉ filter theo date + spend>0 + impressions>0)
   - Table tính từ `adset_map` sau khi áp dụng thêm status/search/prefix filters
   - Summary KHÔNG bị ảnh hưởng bởi filter UI

2. **Fix summary calculation:**
   - Lead Gen: `totalData`, `totalCheckouts`, `totalPurchases`
   - E-Commerce: `adsPercent`, `purchaseValue`, `totalCheckouts`, `totalPurchases`
   - Đếm adsets: `activeAdsets`, `pausedAdsets`, `totalAdsets` từ eligible adsets

3. **Fix cost metrics trong row_data:**
   - Lấy `cost_per_checkout_initiated` và `cost_per_purchase` từ group (đã parse từ cost_per_action_type)
   - Fallback tính từ spend/checkouts hoặc spend/purchases nếu không có

4. **Fix totals calculation:**
   - E-Commerce: `ads_percent = total_spend / total_purchase_value` (KHÔNG nhân 100)
   - Lead Gen: `cost_per_purchase = total_spend / total_purchases` (KHÔNG phải trung bình)

## 🔄 Đang Tiếp Tục

### Frontend
1. **Summary Cards:** ✅ Đã đọc từ `data?.summary` - sẽ tự động đúng từ backend
2. **AdsetTable:** ✅ Đã có các cột đúng cho Lead và E-Commerce
3. **Footer Totals:** ✅ Đã có, cần đảm bảo tính đúng từ `totals` prop
4. **Empty State:** ⏳ Cần cải thiện theo spec (icon chart, text rõ ràng hơn)
5. **Bulk Actions:** ✅ Đã có ConfirmModal, cần đảm bảo progress hiển thị đúng

## 📝 Cần Làm Tiếp

1. **Frontend - Empty State:** Cải thiện empty state với icon chart và text rõ ràng hơn
2. **Frontend - Bulk Actions Progress:** Đảm bảo progress hiển thị đúng % khi xử lý nhiều item
3. **Frontend - Layout:** Đảm bảo thanh bulk actions nằm đúng vị trí (dưới header, trên bảng)
4. **Testing:** Test với Ads Manager để đảm bảo số liệu khớp

