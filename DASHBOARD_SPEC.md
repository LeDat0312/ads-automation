# Dashboard UI Specification - Detailed Requirements

## Phase 0 - Technical Foundation ✅ (Completed)

### API Layer
- ✅ Service calls `/dashboard/data?view_mode=...`
- ✅ Response mapping → `AdsetRow`, `SummaryMetrics` types
- ✅ Proper TypeScript interfaces in `types/dashboard.ts`

### State Management
- ✅ `viewMode`: 'lead' | 'ecommerce'
- ✅ `filters`: date_from, date_to, status, prefix, search
- ✅ `pagination`: page, pageSize
- ✅ `sort`: column + direction (asc/desc)
- ✅ Loading states (skeleton/spinner)
- ✅ Error handling (timeout, token expired...)

---

## Phase 1 - Core UI (In Progress)

### 1. FiltersBar Component

**Required Features:**
- [x] ViewMode switch: 📋 Lead Generation / 🛒 E-Commerce
- [x] Date picker with presets (Hôm nay, 7 ngày qua, 30 ngày qua, Tháng này, Tháng trước)
- [ ] **Status chips**: 
  - Tất cả
  - Đã chạy hôm nay (`ran_today === true`)
  - Đang hoạt động (`is_active_now === true`)
  - Đã tạm dừng (`is_active_now === false`)
- [ ] **Prefix filter**: PX, TL, NM, FL... (dropdown from backend)
- [x] **Search**: By adset_name, adset_id, campaign_id
- [ ] **URL sync**: Filters persist in query string (e.g., `?view=lead&status=ACTIVE&prefix=PX&from=2025-11-01&to=2025-11-19`)

**Implementation Notes:**
- Use `useSearchParams` from react-router-dom for URL sync
- Debounce search input (300ms)
- Clear individual filters with × button
- Active filter count badge

---

### 2. Summary Cards - **CRITICAL: Different for Lead vs Ecom**

#### **Lead Generation View (6 cards):**

1. **Tổng Chi Tiêu** 💰
   - Formula: `sum(spend)` across all adsets
   - Format: VND/USD with thousands separator

2. **Tổng DATA** 💬
   - Formula: `sum(post_comments + messaging_conversations_started)`
   - Subtitle: "Bình luận + Nhắn tin"

3. **Chi phí / DATA** 📊
   - Formula: `totalSpend / totalData`
   - Format: Currency per unit

4. **Bắt Đầu Thanh Toán** 🛒
   - Formula: `sum(checkout_initiated)`
   - Subtitle: "Checkouts Initiated"

5. **Lượt Mua** 💵
   - Formula: `sum(purchases)`

6. **Chi phí / Lượt Mua** 📈
   - Formula: `totalSpend / totalPurchases`
   - Format: Currency per purchase

**Bottom Section (not cards):**
- Adsets Hoạt Động: `count(is_active_now === true)`
- Adsets Đã Tạm Dừng: `totalAdsets - activeAdsets`
- Tổng Adsets: `len(adset_map)`

#### **E-Commerce View (6 cards):**

1. **Tổng Chi Tiêu** 💰
   - Same as Lead

2. **Giá trị chuyển đổi từ lượt mua** 💵
   - Formula: `sum(purchase_value)`
   - This is revenue/ROAS base

3. **% ADS** 📈
   - Formula: `(totalSpend / purchaseValue) * 100`
   - Format: Percentage with 2 decimals
   - **ONLY shown in E-Commerce view**

4. **Bắt Đầu Thanh Toán** 🛒
   - Same as Lead

5. **Lượt Mua** 💵
   - Same as Lead

6. **Chi phí / Lượt Mua** 📊
   - Same as Lead

**Bottom Section:**
- Same as Lead

**Currency Handling:**
- Detect from `adset.currency` field
- Format VND: No decimals, dot separator (e.g., `1.234.567`)
- Format USD: 2 decimals, comma separator (e.g., `$1,234.56`)
- Format THB: Same as VND

---

### 3. AdsetTable - Different Columns per View

#### **Lead Generation Columns (in order):**

1. **☑️** - Checkbox (fixed left)
2. **Trạng thái** - Icon: ✅ active / ⏸️ paused (color coded)
3. **Tên nhóm quảng cáo** (fixed left, min-width: 250px)
   - Main text: `adset_name`
   - Subtitle (small gray): `prefix` | `account_name`
4. **Ngân sách** - Format: currency
5. **Chi tiêu** - Sortable ✅
6. **DATA** - `post_comments + messages` (Sortable ✅)
7. **Giá DATA** - `spend / DATA` (Sortable ✅)
8. **Bắt đầu TT** - `checkout_initiated`
9. **Lượt mua** - `purchases` (Sortable ✅)
10. **Chi phí/Lượt mua** - (Sortable ✅)
11. **Impressions** - Optional, can hide in dropdown

#### **E-Commerce Columns (in order):**

1-3. Same as Lead
4. **Ngân sách**
5. **Chi tiêu** (Sortable ✅)
6. **Giá trị mua** - `purchase_value` (Sortable ✅)
7. **% ADS** - `(spend / purchase_value) * 100` (Sortable ✅) **⚠️ ONLY in Ecom**
8. **Bắt đầu TT**
9. **Lượt mua** (Sortable ✅)
10. **Chi phí/Lượt mua** (Sortable ✅)

**Table Features:**
- [x] Fixed left columns (checkbox + status + name) on horizontal scroll
- [ ] Right-align numeric columns
- [x] Sort by clicking column header (↑↓ icons)
- [ ] Resize columns (optional, or set reasonable widths)
- [x] Row selection with checkboxes
- [ ] Hover effect on rows
- [ ] Pagination controls (10/20/50/100 rows per page)

**Column Width Recommendations:**
- Checkbox: 40px
- Status: 60px
- Adset Name: 250-350px (flexible)
- Numeric columns: 100-120px each
- Total table: ~1400px min-width

---

## Phase 2 - Actions (Partially Done)

### 1. Budget Modal ⚠️ **CRITICAL FIX NEEDED**

**Current Issue:** Code is rounding `original_budget` before calculating percentage increase.

**Correct Formula:**
```typescript
// ❌ WRONG (current)
const rounded = Math.round(originalBudget);
const newBudget = rounded * (1 + percent / 100);

// ✅ CORRECT
const newBudget = originalBudget * (1 + percent / 100);
// Only round when displaying
```

**Quick Percent Buttons:**
- [ ] +10%, +20%, +30%, +50%, +100%
- [ ] -10%, -20%, -30% (for budget decrease)

**Preview Display:**
```
Trước: 78.910 VND
Sau:  102.583 VND (+30%)
```

**Validation:**
- Min budget: 20.000 VND (Facebook minimum)
- Show warning if new budget < min

---

### 2. Status Update (Pause/Resume)

- [x] Bulk select → single API call
- [x] Optimistic UI update (instant feedback)
- [ ] Refetch `/dashboard/data` after success
- [ ] Loading spinner during update
- [ ] Toast notification: "Đã cập nhật 5 adsets"

---

### 3. Bulk Actions Bar

When `selectedIds.size > 0`:
- [x] Show sticky bar at top
- [x] Display count: "Đã chọn 5 nhóm quảng cáo"
- [x] Buttons: Điều chỉnh ngân sách | ▶️ Kích hoạt | ⏸️ Tạm dừng | ✖️ Bỏ chọn

---

## Phase 3 - Advanced Features (TODO)

### 1. Filter Presets
- [ ] Save filter combinations with custom names
- [ ] Examples:
  - "Lead – Hôm nay – PX – Đang chạy"
  - "Ecom – 7 ngày – TL – Tất cả"
- [ ] Dropdown to quick-select saved presets
- [ ] Store in localStorage or backend

### 2. Export CSV
- [ ] Export current filtered + sorted data
- [ ] Include columns matching current view (Lead vs Ecom)
- [ ] Filename: `dashboard_lead_2025-11-19.csv`
- [ ] Options: Current page only / All pages

### 3. Real-time Updates
- [ ] Polling every 30-60 seconds (configurable in settings)
- [ ] Update:
  - Summary cards
  - Status icons (if adset paused/resumed)
  - Spend/conversions
- [ ] Visual indicator: "Updated 2 minutes ago"
- [ ] Pause auto-refresh if user is editing

---

## Critical Fixes Needed (Priority Order)

1. **❗ BudgetModal**: Fix rounding bug (use original budget for % calculation)
2. **❗ SummaryCards**: Show correct 6 cards per view (currently showing wrong metrics)
3. **❗ AdsetTable**: Different columns for Lead vs Ecom
4. **❗ FiltersBar**: Add status chips (Tất cả, Đã chạy hôm nay, Đang hoạt động, Tạm dừng)
5. **❗ URL Sync**: Persist filters in query string

---

## Data Flow Diagram

```
User Action (e.g., change filter)
         ↓
Update filters state
         ↓
Sync to URL (query string)
         ↓
Call API: GET /dashboard/data?view_mode=lead&status=ACTIVE&from=2025-11-15
         ↓
Backend aggregates adset_map
         ↓
Returns: { summary: {...}, details: { rows: [...] } }
         ↓
Frontend:
  - SummaryCards renders from summary (GLOBAL, not filtered)
  - AdsetTable renders from details.rows (FILTERED by table filters)
         ↓
User sees updated UI
```

**Important:** `summary` is GLOBAL (all adsets in adset_map), while `details.rows` is FILTERED by table-level filters (prefix, status, search).

---

## Notes

- **Currency**: Detect from first adset's `currency` field, default to VND
- **Number Format**: Use `Intl.NumberFormat` for locale-aware formatting
- **Date Format**: Use `date-fns` for consistent date handling
- **Icons**: Emoji or Heroicons (prefer emoji for simplicity)
- **Colors**: Match existing purple/indigo gradient theme
- **Responsive**: Desktop-first (table may scroll on mobile)

