# 📋 DASHBOARD REFACTORING - SUMMARY & TEST GUIDE

## ✅ Completed Changes

### 1. **Backend - Summary Business Rules** (`dashboard.py`)

#### 📋 Lead Generation View
```python
summary = {
    "totalSpend": ...,
    "totalData": total_data,  # ✅ Post comments + Messaging conversations started
    "avgGiaData": ...,
    "totalLead": total_lead,  # ✅ FIXED: Checkouts Initiated (omni_initiated_checkout)
    "totalCheckouts": total_checkouts,
    "totalPurchases": total_purchases,
    "activeAdsets": active_adsets,
    "pausedAdsets": paused_adsets,
    "totalAdsets": total_adsets,
    "currency": "VND"
}
```

**Thay đổi:**
- ✅ `totalData` = comments + messages (Bình luận + Tin nhắn)
- ✅ `totalLead` = Checkouts Initiated (từ `omni_initiated_checkout`)
- ✅ `totalCheckouts` = onsite_conversion_post_save hoặc checkouts_initiated

#### 🛒 E-Commerce View
```python
summary = {
    "totalSpend": ...,
    "adsPercent": ...,  # ✅ totalSpend / purchaseValue * 100
    "purchaseValue": ...,  # ✅ Sum of purchase values
    "totalCheckouts": total_checkouts,  # ✅ checkouts_initiated
    "totalPurchases": total_purchases,
    "activeAdsets": active_adsets,
    "pausedAdsets": paused_adsets,
    "totalAdsets": total_adsets,
    "currency": "VND"
}
```

---

### 2. **Frontend - Summary Cards** (`SummaryCards.tsx`)

#### 📋 Lead Generation Cards
```tsx
{/* Card 2: TỔNG DATA */}
<h3>TỔNG DATA</h3>
<p>{formatNumber(summary.totalData || 0)}</p>
<p>Bình luận + Tin nhắn</p>

{/* Card 3: TỔNG LEAD */}
<h3>TỔNG LEAD</h3>
<p>{formatNumber(summary.totalLead || 0)}</p>
<p>Checkouts Initiated</p>
```

**Thay đổi:**
- ✅ Card "TỔNG DATA" hiển thị `summary.totalData` (comments + messages)
- ✅ Card "TỔNG LEAD" hiển thị `summary.totalLead` (Checkouts Initiated)

---

## 🧪 Testing Instructions

### Step 1: Chạy Backend
```powershell
uvicorn app.main:app --reload
```

### Step 2: Test API Endpoint

#### Test Lead Generation
```bash
GET http://localhost:8000/dashboard/data?view_mode=lead&level=adset&date_from=2024-01-15&date_to=2024-01-15
```

**Expected:**
```json
{
  "summary": {
    "totalSpend": 1500000,
    "totalData": 350,          // ← comments + messages
    "totalLead": 45,            // ← Checkouts Initiated (FIXED!)
    "totalCheckouts": 45,
    "activeAdsets": 12
  },
  "details": {
    "level": "adset",
    "rows": [...],
    "pagination": {...}
  }
}
```

**Verify:**
- ✅ `totalData` = sum(comments + messages)
- ✅ `totalLead` = sum(checkouts_initiated)
- ✅ `totalLead` ≠ `totalData`

#### Test Filter Independence
```bash
# Request 1: Không filter
GET /dashboard/data?view_mode=ecommerce&level=adset&date_from=2024-01-15&date_to=2024-01-15

Response: { "summary": { "totalSpend": 2500000 }, "details": { "rows": [100 items] } }

# Request 2: Filter status=ACTIVE
GET /dashboard/data?view_mode=ecommerce&level=adset&date_from=2024-01-15&date_to=2024-01-15&status=ACTIVE

Response: { "summary": { "totalSpend": 2500000 }, "details": { "rows": [18 items] } }
```

**Verify:**
- ✅ Summary giống nhau
- ✅ Rows khác nhau

---

## 🔍 Troubleshooting

### Issue 1: Summary thay đổi khi filter
**Fix:** Frontend phải dùng `response.summary`, không tự tính từ `rows`

### Issue 2: totalLead = totalData (sai)
**Fix:** Đã sửa trong `dashboard.py` line ~370

### Issue 3: CBO hiển thị "0"
**Fix:** Đã thêm fields `using_campaign_budget`, `campaign_daily_budget` trong response

### Issue 4: Rate limit error (HTTP 429)
**Response:** "Facebook API rate limit reached. Vui lòng thử lại sau 5-10 phút."

---

## 📊 Metrics Mapping Reference

### Lead Generation:
- `totalData` = `post_comments` + `messaging_conversations_started`
- `totalLead` = `checkouts_initiated` (omni_initiated_checkout)

### E-Commerce:
- `totalCheckouts` = `checkouts_initiated` (omni_initiated_checkout)
- `totalPurchases` = `purchases` (omni_purchase)
- `purchaseValue` = purchase values (offsite_conversion.fb_pixel_purchase)

---

## ✅ Checklist

- [x] Backend: Fix summary business rules (totalLead)
- [x] Backend: Verify single source of truth pattern
- [x] Backend: Ensure CBO budget fields in response
- [x] Frontend: Update SummaryCards.tsx
- [x] Frontend: Verify no duplicate API calls
- [ ] **USER: Run test script**
- [ ] **USER: Manual testing**
- [ ] **USER: Deploy to production**

---

**Files Changed:**
- `app/api/routes/dashboard.py` (line ~370: totalLead calculation)
- `frontend/src/components/SummaryCards.tsx` (line ~95-110: Lead Gen cards)
