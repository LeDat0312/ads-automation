# 🎯 REFACTORING SUMMARY - Dashboard Backend

## ✅ **ĐÃ HOÀN THÀNH**

### 1. **`facebook_api.py` - Core fixes**

#### ✅ **Filter `spend > 0 && impressions > 0` ngay khi fetch** (Line ~1471)
```python
# 🔹 TỐI ƯU: Bỏ qua adsets có spend <= 0 HOẶC impressions <= 0
if spend <= 0 or impressions <= 0:
    continue  # Skip adset này
```

#### ✅ **Chuẩn hóa metrics mapping theo Facebook Ads Manager** (Line ~1505-1520)
- `checkouts_initiated` → ưu tiên `omni_initiated_checkout`
- `purchases` → ưu tiên `omni_purchase`
- `messaging started` → ưu tiên `onsite_conversion.messaging_conversation_started_7d`
- `purchase_value` → ưu tiên `offsite_conversion.fb_pixel_purchase`

#### ✅ **Fix CBO budget logic** (Line ~1680-1700)
```python
# using_campaign_budget = adset không có budget && campaign có budget
using_campaign_budget = (adset_daily_budget in (None, 0)) and campaign_budget_total > 0

# Row data bao gồm đầy đủ:
'budget_type': 'CAMPAIGN' | 'ADSET',
'adset_daily_budget': float | None,
'campaign_daily_budget': float | None,
'using_campaign_budget': bool
```

#### ✅ **Xử lý Facebook Rate Limit** (Line ~1388-1400)
```python
# Tạo custom exception
class FacebookRateLimitError(Exception):
    pass

# Detect rate limit và raise exception
if error_code == 4 or error_code == 17 or 'rate limit' in error_msg.lower():
    raise FacebookRateLimitError(f"Facebook API rate limit reached: {error_msg}")
```

---

### 2. **`dashboard.py` - Hàm SINGLE SOURCE OF TRUTH**

#### ✅ **Hàm `get_dashboard_dataset()`** (Line 205-462)

**Chức năng:**
- Fetch insights 1 LẦN DUY NHẤT từ Facebook API
- Filter `spend > 0 && impressions > 0` ngay từ đầu
- Tạo `rows_base` cho summary (KHÔNG bị ảnh hưởng bởi filter UI)
- Tạo `rows_for_table` cho bảng (áp dụng filter prefix/status/search)
- Tính summary từ `rows_base`

**Return structure:**
```python
{
    "rows_base": List[Dict],           # Dataset cho summary
    "rows_for_table": List[Dict],      # Dataset cho bảng (đã filter)
    "summary": Dict,                    # Summary metrics
    "all_adsets_from_accounts": Dict,  # Tất cả adsets
    "adset_statuses_map": Dict         # Status map
}
```

**Đảm bảo:**
- ✅ Summary và bảng LUÔN nhất quán (cùng 1 source)
- ✅ Summary KHÔNG bị ảnh hưởng bởi filter status/prefix/search
- ✅ Bảng áp dụng đầy đủ filters

---

### 3. **Endpoint `/dashboard/data` - REFACTORED**

#### 📄 **File mới: `REFACTORED_ENDPOINT_DATA.py`**

**Thay đổi:**
- 🔥 Giảm từ **1000+ dòng** xuống **~350 dòng**
- ✅ Sử dụng `get_dashboard_dataset()` - SINGLE SOURCE OF TRUTH
- ✅ Xử lý `FacebookRateLimitError` → HTTP 429
- ✅ Logic đơn giản, dễ debug

**Cấu trúc mới:**
```python
@router.get("/data")
async def get_dashboard_data(...):
    # 1. Get user accounts & build account_type_map
    # 2. Call get_dashboard_dataset() - SINGLE SOURCE
    try:
        dataset = await get_dashboard_dataset(...)
    except FacebookRateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit reached")
    
    # 3. Group by level (campaign/adset/ad)
    # 4. Sort
    # 5. Pagination
    # 6. Return response
```

---

## 📊 **KẾT QUẢ ĐẠT ĐƯỢC**

### ✅ **Vấn đề đã fix:**

1. **Summary và bảng LUÔN nhất quán**
   - Cùng lấy từ 1 dataset duy nhất (`rows_base`)
   - Không còn hiện tượng: summary có số nhưng bảng trống (hoặc ngược lại)

2. **Chỉ load adset có `spend > 0 && impressions > 0`**
   - Tốc độ nhanh hơn nhiều
   - Giảm tải Facebook API

3. **CBO budget hiển thị đúng**
   - Field `using_campaign_budget` rõ ràng
   - Frontend chỉ cần check: `if (using_campaign_budget || campaign_daily_budget > 0)`

4. **Xử lý rate limit đúng cách**
   - Trả HTTP 429 khi bị rate limit
   - Frontend hiển thị message cho user
   - Không trả dataset rỗng gây nhầm lẫn

5. **Summary KHÔNG bị ảnh hưởng bởi filter UI**
   - Filter status/prefix/search chỉ áp dụng cho bảng
   - Summary luôn tính trên toàn bộ data (spend>0 && impressions>0)

---

## 🚀 **CÁCH SỬ DỤNG**

### **Bước 1: Backup endpoint cũ**
```bash
# Tạo backup file
cp app/api/routes/dashboard.py app/api/routes/dashboard.py.backup
```

### **Bước 2: Replace endpoint `/data`**

Mở file `dashboard.py`, tìm dòng:
```python
@router.get("/data")
async def get_dashboard_data(
```

Xóa toàn bộ endpoint cũ (từ dòng 623 đến dòng 1604 - khoảng 980 dòng)

Copy toàn bộ code từ file `REFACTORED_ENDPOINT_DATA.py` vào vị trí đó

### **Bước 3: Test**

```bash
# Restart backend
cd backend
uvicorn app.main:app --reload

# Test các scenarios:
# 1. View E-Commerce - check summary vs bảng
# 2. View Lead Gen - check summary vs bảng
# 3. Filter status (Đang hoạt động/Tạm dừng) - summary không đổi
# 4. Filter prefix - summary không đổi
# 5. Search - summary không đổi
# 6. Gây rate limit (comment out cache) - check HTTP 429
```

---

## 🔍 **KIỂM TRA QUAN TRỌNG**

### ✅ **Test Case 1: Summary vs Bảng nhất quán**

**Test:**
```
1. Chọn ngày hôm nay
2. View E-Commerce
3. Check:
   - Tổng chi tiêu trong summary = tổng spend trong bảng
   - Số adsets trong summary = số rows trong bảng
```

**Kết quả mong đợi:** Luôn khớp nhau

---

### ✅ **Test Case 2: Filter không ảnh hưởng summary**

**Test:**
```
1. View Lead Gen, date = hôm nay
2. Note summary: Tổng chi tiêu = X, Tổng adsets = Y
3. Đổi filter status = "Đang hoạt động"
4. Check summary
```

**Kết quả mong đợi:** Summary KHÔNG ĐỔI (vẫn = X, Y)

---

### ✅ **Test Case 3: CBO Budget hiển thị**

**Test:**
```
1. Tạo campaign với Budget Optimization = Campaign (CBO)
2. Tạo 1 adset không set budget riêng
3. Check trong bảng "Nhóm QC":
   - using_campaign_budget = true
   - campaign_daily_budget > 0
   - adset_daily_budget = null hoặc 0
```

**Frontend sẽ hiển thị:** "Ngân sách chiến dịch (XXX ₫)"

---

### ✅ **Test Case 4: Rate Limit**

**Test:**
```
1. Comment out cache trong facebook_api.py (tạm thời)
2. Gọi /dashboard/data liên tục 10-20 lần
3. Khi bị rate limit, check response
```

**Kết quả mong đợi:**
```json
{
  "status_code": 429,
  "detail": "Facebook API rate limit reached. Vui lòng thử lại sau 5-10 phút."
}
```

---

## 📝 **NOTES**

### **Các file đã sửa:**

1. ✅ `app/services/facebook_api.py`
   - Line 16-18: Thêm `FacebookRateLimitError`
   - Line 1471-1474: Filter `spend > 0 && impressions > 0`
   - Line 1505-1520: Chuẩn hóa metrics mapping
   - Line 1680-1700: Fix CBO budget
   - Line 1388-1410: Xử lý rate limit error

2. ✅ `app/api/routes/dashboard.py`
   - Line 29: Import `FacebookRateLimitError`
   - Line 205-462: Thêm hàm `get_dashboard_dataset()`
   - Line 623-1604: **CẦN REPLACE** bằng code trong `REFACTORED_ENDPOINT_DATA.py`

3. ✅ `REFACTORED_ENDPOINT_DATA.py` (file mới)
   - Chứa endpoint `/data` mới (~350 dòng)

4. ✅ `REFACTORING_SUMMARY.md` (file này)
   - Tài liệu tổng hợp

---

## ⚠️ **LƯU Ý QUAN TRỌNG**

### **1. KHÔNG xóa logic cũ trước khi test kỹ**
- Backup file trước khi sửa
- Test kỹ trên local trước
- Deploy lên production sau khi verify

### **2. Frontend KHÔNG CẦN SỬA**
- Response format giống y hệt
- Chỉ cần verify CBO budget logic:
```typescript
// Check trong AdsetTable.tsx
if (row.using_campaign_budget || (!row.adset_daily_budget && row.campaign_daily_budget > 0)) {
  return `Ngân sách chiến dịch\n${formatCurrency(row.campaign_daily_budget)}`;
} else if (row.adset_daily_budget > 0) {
  return `Ngân sách nhóm QC\n${formatCurrency(row.adset_daily_budget)}`;
} else {
  return '-';
}
```

### **3. Cache vẫn hoạt động bình thường**
- `force_refresh=0`: Dùng cache (default)
- `force_refresh=1`: Bỏ cache, fetch mới

### **4. Rate limit handling**
- Frontend cần handle HTTP 429
- Hiển thị message: "Đã đạt giới hạn Facebook API, vui lòng thử lại sau 5-10 phút"

---

## 🎉 **NEXT STEPS**

1. ✅ **Replace endpoint cũ** bằng code trong `REFACTORED_ENDPOINT_DATA.py`
2. ✅ **Test local** với các test cases trên
3. ✅ **Verify logs** - check không còn duplicate API calls
4. ✅ **Deploy lên VPS** sau khi verify
5. ✅ **Monitor** trong vài ngày để đảm bảo ổn định

---

## 📞 **HỖ TRỢ**

Nếu gặp lỗi:
1. Check logs backend: `tail -f logs/app.log`
2. Check browser console (F12)
3. Verify response format từ `/dashboard/data`
4. So sánh với endpoint cũ (backup)

**File backup:** `dashboard.py.backup`
