# 📊 FACEBOOK ADS METRICS - QUICK REFERENCE

## Action Type Mapping (facebook_api.py)

### 🛒 Checkouts Initiated (Bắt đầu thanh toán)
**Priority Order:**
1. `omni_initiated_checkout` ✅ (highest priority)
2. `initiate_checkout`
3. `offsite_conversion.fb_pixel_initiate_checkout`
4. `onsite_conversion.initiated_checkout`

**Backend field:** `checkouts_initiated`  
**Used in:**
- Lead Gen: `totalLead` = sum(checkouts_initiated)
- E-Commerce: `totalCheckouts` = sum(checkouts_initiated)

---

### 💰 Purchases (Lượt mua)
**Priority Order:**
1. `omni_purchase` ✅ (highest priority)
2. `purchase`
3. `offsite_conversion.fb_pixel_purchase`
4. `onsite_conversion.purchase`

**Backend field:** `purchases`  
**Used in:**
- E-Commerce: `totalPurchases` = sum(purchases)

---

### 💬 Post Comments (Bình luận)
**Priority Order:**
1. `comment`
2. `post_comment` ✅
3. `onsite_conversion.post_comment`

**Backend field:** `post_comments`  
**Used in:**
- Lead Gen: `totalData` = sum(post_comments + messaging_conversations_started)

---

### 📩 Messaging Conversations Started (Tin nhắn)
**Priority Order:**
1. `onsite_conversion.messaging_conversation_started_7d` ✅
2. `onsite_conversion.messaging_conversation_started`
3. `messaging_conversation_started`
4. `messaging_conversation_started_7d_click`
5. `messaging_conversation_started_1d_click`

**Backend field:** `messaging_conversations_started`  
**Used in:**
- Lead Gen: `totalData` = sum(post_comments + messaging_conversations_started)

---

### 💎 Purchase Value (Giá trị chuyển đổi)
**Priority Order (from action_values):**
1. `offsite_conversion.fb_pixel_purchase` ✅ (highest priority)
2. `omni_purchase`
3. `purchase`
4. `onsite_conversion.purchase`

**Backend field:** `purchase_value` (mapped from `action_values`)  
**Used in:**
- E-Commerce: `adsPercent` = (totalSpend / totalPurchaseValue) * 100

---

### 📌 Post Save (Bắt đầu TT - Lead Gen specific)
**Priority Order:**
1. `onsite_conversion.post_save` ✅
2. `post_save`

**Backend field:** `onsite_conversion_post_save`  
**Used in:**
- Lead Gen: `totalCheckouts` = sum(onsite_conversion_post_save OR checkouts_initiated)

---

## Summary Calculations

### 📋 Lead Generation View
```python
totalSpend = sum(spend)  # All adsets with spend > 0 && impressions > 0

totalData = sum(post_comments + messaging_conversations_started)
# = Bình luận + Tin nhắn

totalLead = sum(checkouts_initiated)
# = Checkouts Initiated (omni_initiated_checkout)

totalCheckouts = sum(onsite_conversion_post_save OR checkouts_initiated)
# = Bắt đầu thanh toán (ưu tiên post_save cho Lead Gen)

avgGiaData = totalSpend / totalData
# = Chi phí cho mỗi data (comment + message)

activeAdsets = count(adsets with effective_status=ACTIVE)
pausedAdsets = count(adsets with effective_status=PAUSED/ARCHIVED)
totalAdsets = count(all adsets with spend > 0 && impressions > 0)
```

### 🛒 E-Commerce View
```python
totalSpend = sum(spend)

purchaseValue = sum(purchase_value)
# = Giá trị chuyển đổi từ lượt mua

adsPercent = (totalSpend / purchaseValue) * 100
# = % ADS = Chi tiêu / Giá trị chuyển đổi

totalCheckouts = sum(checkouts_initiated)
# = Checkouts Initiated (omni_initiated_checkout)

totalPurchases = sum(purchases)
# = Lượt mua (omni_purchase)

activeAdsets = count(adsets with effective_status=ACTIVE)
pausedAdsets = count(adsets with effective_status=PAUSED/ARCHIVED)
totalAdsets = count(all adsets with spend > 0 && impressions > 0)
```

---

## Row-level Metrics (Table Columns)

### All Views
```python
# Basic metrics
spend = sum of spend across date range
impressions = sum of impressions
clicks = sum of clicks
reach = sum of reach

# Calculated metrics
cpm = (spend / impressions) * 1000  # Cost per 1000 impressions
ctr = (clicks / impressions) * 100  # Click-through rate
cpc = spend / clicks  # Cost per click
```

### Lead Generation
```python
results = post_comments + messaging_conversations_started
data_cost = spend / results  # Giá DATA
cost_per_checkout_initiated = spend / checkouts_initiated
```

### E-Commerce
```python
results = post_comments + messaging_conversations_started  # Same as Lead Gen
data_cost = spend / results
ads_percent = (spend / purchase_value) * 100  # % ADS for each row
cost_per_checkout_initiated = spend / checkouts_initiated
cost_per_purchase = spend / purchases
```

---

## CBO Budget Detection

### Backend Logic (`facebook_api.py`)
```python
# Fetch campaign budget
campaign_budget = fetch_campaign_budgets_batch([campaign_id])

# Detect if adset uses campaign budget
if adset_daily_budget is None or adset_daily_budget == 0:
    if campaign_budget and campaign_budget > 0:
        using_campaign_budget = True
        budget_type = "CAMPAIGN"
    else:
        using_campaign_budget = False
        budget_type = "ADSET"
else:
    using_campaign_budget = False
    budget_type = "ADSET"
```

### Response Fields
```python
{
    "adset_daily_budget": 200000,        # or null
    "campaign_daily_budget": 500000,     # or null
    "using_campaign_budget": false,      # true/false
    "budget_type": "ADSET"               # "ADSET" or "CAMPAIGN"
}
```

### Frontend Display (`AdsetTable.tsx`)
```tsx
if (using_campaign_budget || (!adset_daily_budget && campaign_daily_budget > 0)) {
  display = "Ngân sách chiến dịch\n(${campaign_daily_budget})"
} else if (adset_daily_budget > 0) {
  display = "${adset_daily_budget}"
} else {
  display = "Ngân sách chiến dịch"  // No amount shown
}
```

---

## Filter Logic

### Backend (`get_dashboard_dataset`)
```python
# Step 1: Fetch from Facebook API (once)
all_data = pull_facebook_data_with_date_range_async(...)

# Step 2: Filter spend > 0 && impressions > 0
all_data = [row for row in all_data if spend > 0 and impressions > 0]

# Step 3: Filter by view_mode
all_data = [row for row in all_data if campaign_type == view_mode]

# Step 4: rows_base = SINGLE SOURCE OF TRUTH (for summary)
rows_base = all_data.copy()

# Step 5: Compute summary from rows_base
summary = compute_summary(rows_base)  # NOT affected by UI filters

# Step 6: Apply UI filters (for table only)
rows_for_table = rows_base.copy()
if prefix:
    rows_for_table = [row for row in rows_for_table if row.prefix == prefix]
if status:
    rows_for_table = [row for row in rows_for_table if row.effective_status == status]
if search:
    rows_for_table = [row for row in rows_for_table if search in row.name]
```

### Key Points
- ✅ Summary computed from `rows_base` (before UI filters)
- ✅ Table shows `rows_for_table` (after UI filters)
- ✅ Summary NEVER changes when user applies filters
- ✅ Only table data changes with filters

---

## Status Normalization

### Facebook Status Values
```python
ACTIVE = "ACTIVE"           # Đang chạy
PAUSED = "PAUSED"           # Tạm dừng
ARCHIVED = "ARCHIVED"       # Lưu trữ
DELETED = "DELETED"         # Đã xóa
```

### Effective Status (from Facebook API)
```python
effective_status = adset['effective_status']
# Can be: ACTIVE, PAUSED, ARCHIVED, CAMPAIGN_PAUSED, ADSET_PAUSED, etc.

# Normalize to simple status
delivery = normalize_status(effective_status)
# Returns: ACTIVE, PAUSED, ARCHIVED, or UNKNOWN
```

### Frontend Display
```tsx
{delivery === 'ACTIVE' ? '▶️ Đang hoạt động' : '⏸️ Tạm dừng'}
```

---

**Last Updated:** 2024-01-15  
**Version:** Post-refactor (Single Source of Truth)
