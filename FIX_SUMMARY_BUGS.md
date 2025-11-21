# TÓM TẮT CÁC THAY ĐỔI - BUGS FIXED

**Ngày:** 22/11/2025
**Project:** ads-automation (FastAPI + React Dashboard)

---

## ✅ CÁC BUGS ĐÃ SỬA

### 1. BUG TAB "CHIẾN DỊCH" ✅

#### 1.1. Nút bật/tắt chiến dịch hiển thị sai ✅
**File đã sửa:** `frontend/src/components/AdsetTable.tsx`

**Thay đổi:**
- Sửa logic đọc status từ `configured_status` (ưu tiên cao nhất) thay vì chỉ dùng `effective_status`
- Đảm bảo toggle switch hiển thị đúng trạng thái ACTIVE/PAUSED theo `configured_status`
- Code hiện tại (dòng ~296 & ~494):
  ```tsx
  checked={(() => {
    const status = (row.configured_status || row.effective_status || row.delivery || 'UNKNOWN').toUpperCase();
    return status === 'ACTIVE';
  })()}
  ```

**Backend support:**
- `facebook_api.py` đã fetch cả `configured_status` và `effective_status`
- `dashboard.py` đã truyền cả 2 fields trong response

#### 1.2. Cột "Ngân sách" của chiến dịch hiển thị sai ✅
**File đã sửa:** `frontend/src/components/AdsetTable.tsx`

**Thay đổi:**
- Sửa logic hiển thị ngân sách phân biệt "Ngân sách chiến dịch" vs "Ngân sách nhóm QC"
- Dựa trên `using_campaign_budget` và `budget_level`:
  - Nếu `budget_level === 'CAMPAIGN'` hoặc `using_campaign_budget === true` → "Ngân sách chiến dịch"
  - Nếu không → "Ngân sách nhóm QC"
- Code hiện tại (dòng ~343-384 & ~543-584):
  ```tsx
  if (isCampaignLevel && row.budget_level === 'CAMPAIGN') {
    budgetDisplay = `Ngân sách chiến dịch\n(${formatCurrency(budgetValue, ...)})`;
  } else if (usingCampaignBudget && budgetValue) {
    budgetDisplay = `Ngân sách chiến dịch\n(${formatCurrency(budgetValue, ...)})`;
  } else if (row.budget_level === 'ADSET' && currentLevel === 'campaign' && budgetValue) {
    budgetDisplay = `Ngân sách nhóm QC\n(${formatCurrency(budgetValue, ...)})`;
  }
  ```

**Backend support:**
- `facebook_api.py` đã tính đúng `using_campaign_budget`, `budget_type`, `budget_level`
- Mapping đúng `campaign_daily_budget` và `adset_daily_budget`

---

### 2. BUG ĐIỀU CHỈNH NGÂN SÁCH ✅

**File đã sửa:**
- `frontend/src/components/BudgetModal.tsx`
- `frontend/src/App.tsx`

**Thay đổi:**

#### 2.1. Preview tính đúng budget hiện tại ✅
- Thêm helper function `getCurrentBudget()` để xác định budget đúng:
  ```tsx
  const getCurrentBudget = (row: AdsetRow): number => {
    if (currentLevel === 'campaign' && row.budget_level === 'CAMPAIGN') {
      return row.campaign_daily_budget || row.budget || 0;
    }
    if (row.using_campaign_budget && row.campaign_daily_budget) {
      return row.campaign_daily_budget;
    }
    if (row.adset_daily_budget) {
      return row.adset_daily_budget;
    }
    return row.budget || 0;
  };
  ```

#### 2.2. Gửi API đúng level (CAMPAIGN vs ADSET) ✅
- Thêm helper function `getRowId()` để lấy đúng ID (campaign_id vs adset_id)
- Trong `App.tsx` (dòng ~253-280):
  ```tsx
  const operations = changes.map(change => {
    const row = data?.details.rows.find(r => 
      r.id === change.id || r.adset_id === change.id || r.campaign_id === change.id
    );
    
    let opLevel: 'CAMPAIGN' | 'ADSET' = 'ADSET';
    if (row) {
      if (row.budget_level === 'CAMPAIGN' || row.using_campaign_budget) {
        opLevel = 'CAMPAIGN';
      }
    }
    
    return { level: opLevel, id: change.id, new_budget: change.new_budget };
  });
  ```

#### 2.3. Single budget edit (BudgetEditor) ✅
- App.tsx `handleBudgetUpdateSingle()` (dòng ~382-406):
  ```tsx
  if (row.budget_level === 'CAMPAIGN' || row.using_campaign_budget) {
    const campaignId = row.campaign_id || targetId;
    await updateBudget({
      operations: [{ level: 'CAMPAIGN', id: campaignId, new_budget: newBudget }],
      view_mode: viewMode,
    });
  } else {
    await updateBudget({
      operations: [{ level: 'ADSET', id: targetId, new_budget: newBudget }],
      view_mode: viewMode,
    });
  }
  ```

---

### 3. BUG VIEW "E-COMMERCE" – METRICS SAI ✅

**File đã sửa:**
- `app/api/routes/dashboard.py`
- `app/services/facebook_api.py`

**Các metrics đã sửa:**

#### 3.1. % ADS ✅
**Công thức:** `(spend / purchase_value) * 100`
- Backend:
  - Summary (dashboard.py dòng ~182-183):
    ```python
    ads_percent = (total_spend / total_purchase_value * 100.0) if total_purchase_value > 0 else 0.0
    ```
  - Từng row (dashboard.py dòng ~816 & ~886):
    ```python
    group['ads_percent'] = (spend / purchase_value * 100) if purchase_value > 0 else 0
    ```
  - Facebook API (facebook_api.py dòng ~1234):
    ```python
    derived_ads_percent = (spend / purchase_value * 100) if purchase_value > 0 else 0
    ```
- Frontend: Không cần sửa, đã nhận đúng % từ backend (đã nhân 100)

#### 3.2. Giá DATA ✅
**Công thức:** `spend / (post_comments + messaging_conversations_started)`
- Backend:
  - Từng row (dashboard.py dòng ~811 & ~881):
    ```python
    group['gia_data'] = (spend / data) if data > 0 else 0
    group['data_cost'] = group['gia_data']  # Alias
    ```
  - Facebook API (facebook_api.py dòng ~1226):
    ```python
    derived_gia_data = (spend / results) if results > 0 else 0
    row['gia_data'] = derived_gia_data
    row['data_cost'] = derived_gia_data  # Alias
    ```

#### 3.3. TLC (Tỷ lệ chốt) ✅
**Công thức:** `(purchases / messaging_conversations_started) * 100`
- Backend:
  - Từng row (dashboard.py dòng ~820 & ~890):
    ```python
    msg_started = group['messaging_conversations_started']
    group['tlc'] = (purchases / msg_started * 100) if msg_started > 0 else 0
    ```
  - Facebook API (facebook_api.py dòng ~1228):
    ```python
    derived_tlc = (purchases / messages * 100) if messages > 0 else 0
    row['tlc'] = derived_tlc
    ```

#### 3.4. Tần Suất (Frequency) ✅
**Công thức:** `impressions / reach`
- Backend:
  - Từng row (dashboard.py dòng ~822 & ~892):
    ```python
    group['frequency'] = (impressions / reach) if reach > 0 else 0
    ```
  - Facebook API (facebook_api.py dòng ~1230-1232):
    ```python
    reach_val = int(item.get('reach', 0) or 0)
    derived_frequency = (impressions / reach_val) if reach_val > 0 else 0
    row['frequency'] = derived_frequency
    ```

#### 3.5. Chi phí/Bắt Đầu TT (cost_per_checkout_initiated) ✅
- Backend:
  - Từng row (dashboard.py dòng ~813 & ~883):
    ```python
    # Ưu tiên từ API, fallback tính từ spend
    group['cost_per_checkout_initiated'] = group.get('cost_per_checkout_initiated', 0) or ((spend / checkouts) if checkouts > 0 else 0)
    ```

#### 3.6. Chi phí/Lượt Mua (cost_per_purchase) ✅
- Backend:
  - Từng row (dashboard.py dòng ~815 & ~885):
    ```python
    # Ưu tiên từ API, fallback tính từ spend
    group['cost_per_purchase'] = group.get('cost_per_purchase', 0) or ((spend / purchases) if purchases > 0 else 0)
    ```

#### 3.7. purchase_value alias ✅
- Backend:
  - Từng row (dashboard.py dòng ~827 & ~897):
    ```python
    group['purchase_value'] = purchase_value
    ```
  - Facebook API (facebook_api.py dòng ~1255):
    ```python
    row['purchase_value'] = purchase_value  # Alias cho frontend
    ```

---

### 4. BUG VIEW "LEAD GENERATION" – BẢNG TRỐNG ✅

**Nguyên nhân:** Filter `adset_id` bị áp dụng sai khi ở level='adset'

**File đã sửa:** `app/api/routes/dashboard.py`

**Thay đổi (dòng ~119-130):**
```python
# ✅ FIX: Filter by adset_id CHỈ KHI thực sự drill-down (level=ad hoặc level=campaign)
# Không áp dụng khi đang ở level=adset (xem tổng quan adsets)
if adset_id and isinstance(adset_id, str):
    adset_id_clean = adset_id.strip()
    if adset_id_clean and adset_id_clean.lower() not in ("none", "null", "undefined", ""):
        logger.info(f"   🔎 adset_id param received: '{adset_id_clean}' (current level: {level})")
        # Chỉ áp dụng filter khi level != adset (tức là đang drill-down vào ads)
        if level == "ad":
            before_adset_filter = len(rows_for_table)
            rows_for_table = [row for row in rows_for_table if row.get('adset_id') == adset_id_clean]
            logger.info(f"   📊 After filter adset_id ({adset_id_clean}): {len(rows_for_table)}/{before_adset_filter} rows [level=ad, drill-down]")
        else:
            logger.info(f"   ⚠️ Ignoring adset_id filter because level={level} (not drilling down)")
```

**Giải thích:**
- Trước đây: Filter `adset_id` áp dụng cho tất cả levels → bảng Lead Gen bị rỗng
- Sau khi sửa: Chỉ áp dụng filter `adset_id` khi `level='ad'` (drill-down vào ads)
- Khi `level='adset'`: Hiển thị tất cả adsets (không filter theo adset_id)

---

## 📊 SUMMARY OF CHANGES

### Backend Changes:
1. ✅ `app/api/routes/dashboard.py`:
   - Sửa công thức % ADS trong summary
   - Sửa công thức Giá DATA, TLC, Frequency cho adset & campaign level
   - Sửa filter adset_id chỉ áp dụng khi drill-down (level=ad)

2. ✅ `app/services/facebook_api.py`:
   - Thêm derived metrics: `derived_gia_data`, `derived_tlc`, `derived_frequency`, `derived_ads_percent`
   - Thêm aliases: `data_cost`, `initiated_checkout`, `tlc`, `ads_percent`

### Frontend Changes:
1. ✅ `frontend/src/components/AdsetTable.tsx`:
   - Sửa logic toggle switch dùng `configured_status`
   - Sửa hiển thị cột Ngân sách phân biệt CBO/ABO
   - Đã có sẵn helper `canEditBudget()` để xác định chính xác

2. ✅ `frontend/src/components/BudgetModal.tsx`:
   - Thêm `getCurrentBudget()` để lấy đúng budget (campaign vs adset)
   - Thêm `getRowId()` để lấy đúng ID tương ứng
   - Preview tính đúng tổng budget hiện tại, mới, chênh lệch

3. ✅ `frontend/src/App.tsx`:
   - Sửa `handleBudgetUpdate()` để xác định level đúng (CAMPAIGN vs ADSET)
   - Sửa `handleBudgetUpdateSingle()` tương tự
   - Sửa `handleStatusToggle()` dùng `configured_status`

---

## 🧪 TESTING CHECKLIST

### Tab Chiến dịch:
- [ ] Toggle ON/OFF hiển thị đúng trạng thái ACTIVE/PAUSED
- [ ] Cột Ngân sách hiển thị "Ngân sách chiến dịch" cho CBO
- [ ] Cột Ngân sách hiển thị "Ngân sách nhóm QC" cho ABO
- [ ] Click vào budget có thể edit (nếu là CBO ở tab campaign)

### Tab Nhóm Quảng Cáo (E-Commerce):
- [ ] % ADS hiển thị đúng (không quá lớn, ví dụ 5-20%)
- [ ] Giá DATA = Chi tiêu / (Bình luận + Tin nhắn)
- [ ] TLC = Lượt mua / Tin nhắn * 100
- [ ] Tần Suất = Hiển thị / Tiếp cận
- [ ] Chi phí/BĐTT và Chi phí/LM hiển thị đúng
- [ ] Summary card % ADS khớp với tổng trong bảng

### Tab Nhóm Quảng Cáo (Lead Generation):
- [ ] Bảng hiển thị danh sách adsets (không rỗng nếu summary có số)
- [ ] Summary "Tổng DATA" và "Tổng LEAD" khớp với bảng

### Popup Điều chỉnh Ngân sách:
- [ ] Preview "Tổng hiện tại" hiển thị đúng
- [ ] Preview "Tổng mới" tính đúng theo %
- [ ] Preview "Chênh lệch" = Mới - Hiện tại
- [ ] Gửi API thành công và refresh data

---

## 🔧 KHÔNG THAY ĐỔI (GIỮ NGUYÊN)

### Backend:
- ✅ Không đổi `get_dashboard_dataset()` structure
- ✅ Không đổi logic cache
- ✅ Không đổi filter `spend > 0 && impressions > 0`
- ✅ Không đổi endpoint `/dashboard/data` API signature
- ✅ Không đổi cách tổng hợp summary (trừ % ADS)

### Frontend:
- ✅ Không đổi component structure
- ✅ Không đổi UI/UX layout
- ✅ Không tạo file mới (chỉ sửa file cũ)

---

## 📝 NOTES

1. **% ADS Calculation:**
   - Backend đã nhân 100 (`(spend / purchase_value) * 100`)
   - Frontend chỉ cần hiển thị (`{summary.adsPercent.toFixed(2)}%`)
   - **KHÔNG được nhân 100 lần nữa ở frontend**

2. **Budget Level:**
   - `budget_level = 'CAMPAIGN'` → CBO (Campaign Budget Optimization)
   - `budget_level = 'ADSET'` → ABO (Adset Budget Optimization)
   - `using_campaign_budget = true` → Adset đang dùng campaign budget (CBO)

3. **Status Fields:**
   - `configured_status`: Trạng thái do user set (ACTIVE/PAUSED) → Dùng cho toggle switch
   - `effective_status`: Trạng thái thực tế trên Facebook (ACTIVE, CAMPAIGN_PAUSED, ...) → Dùng để biết có đang phân phối
   - `delivery`: Normalized status (ACTIVE/PAUSED/DELETED) → Dùng để filter

4. **Derived Metrics:**
   - Tất cả metrics phức tạp (%, cost per...) đã được tính ở backend
   - Frontend chỉ format và hiển thị
   - **Không tính lại ở frontend để tránh sai lệch**

---

**Người thực hiện:** GitHub Copilot (Claude Sonnet 4.5)
**Trạng thái:** ✅ HOÀN THÀNH - Đã sửa tất cả bugs theo yêu cầu
