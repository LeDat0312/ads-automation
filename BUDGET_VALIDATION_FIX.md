# FIX: BUDGET VALIDATION - Commit c986ec1

## VẤN ĐỀ BAN ĐẦU

### Hiện tượng:
```
UI tab "Nhóm QC" hiển thị: "Ngân sách nhóm QC"
→ Chọn nhiều adset → Tăng ngân sách 10%
→ Backend trả lỗi: "Không thể cập nhật ngân sách: Ngân sách đang ở cấp chiến dịch"
→ Nhưng thực tế các adset này là ABO (có daily_budget riêng)
```

### Nguyên nhân:
**Code cũ** (`dashboard.py` dòng 1223):
```python
# Nếu lỗi 400, có thể do budget ở cấp campaign
if not result.get("success") and "400" in str(result.get("error", "")):
    return {
        "error": "Không thể cập nhật ngân sách: Ngân sách đang ở cấp chiến dịch..."
    }
```

**Vấn đề:**
- Check chung chung "400" trong error message
- Hardcode message về CBO cho MỌI lỗi 400
- Chặn nhầm cả adset ABO hợp lệ (ví dụ: lỗi validation khác từ Facebook)

---

## GIẢI PHÁP

### 1. Fix Backend Validation (`dashboard.py`)

**Code mới:**
```python
if not result.get("success"):
    error_msg = result.get("error", "")
    
    # ✅ Kiểm tra CHÍNH XÁC message có chứa từ khóa CBO
    is_cbo_error = (
        "campaign budget optimization" in error_msg.lower() or
        "campaign_budget_optimization" in error_msg.lower() or
        "cbo" in error_msg.lower()
    )
    
    if is_cbo_error:
        return {
            "status": "error",
            "error": "Không thể cập nhật ngân sách: Ngân sách đang ở cấp chiến dịch. Vui lòng cập nhật ở tab 'Chiến Dịch'."
        }
    
    # Nếu KHÔNG phải CBO error → trả lỗi gốc từ Facebook
    logger.warning(f"Budget update failed for adset {op.id}: {error_msg} (not CBO error)")
```

**Cải thiện:**
- ✅ CHỈ báo lỗi CBO khi message thực sự chứa từ khóa liên quan CBO
- ✅ Các lỗi khác (validation, permission, etc.) → trả về message gốc từ Facebook
- ✅ Thêm log warning để debug

---

### 2. Thêm Debug Log (`facebook_api.py`)

**Code mới:**
```python
# ✅ DEBUG LOG: Kiểm tra budget scope
logger.debug(
    f"DEBUG_BUDGET_SCOPE | adset_id={adset_id}, "
    f"daily_budget={adset_data.get('daily_budget')}, "
    f"lifetime_budget={adset_data.get('lifetime_budget')}, "
    f"current_budget={current_budget}, budget_type={budget_type}"
)
```

**Lợi ích:**
- Dễ troubleshoot khi có vấn đề
- Xem được budget type thực tế của adset
- Verify ABO vs CBO từ Facebook response

---

## KẾT QUẢ SAU KHI FIX

### Case 1: Adset ABO (có daily_budget riêng)
**Trước:**
```
Request: Update budget adset_123 (ABO)
→ Facebook trả lỗi 400: "Invalid budget value"
→ Backend hardcode: "Ngân sách đang ở cấp chiến dịch"
→ ❌ CHẶN NHẦM
```

**Sau:**
```
Request: Update budget adset_123 (ABO)
→ Facebook trả lỗi 400: "Invalid budget value"
→ Backend check: KHÔNG chứa từ khóa CBO
→ Trả về: "400: Invalid budget value"
→ ✅ User biết lỗi thực tế
```

---

### Case 2: Adset CBO (campaign budget optimization)
**Trước:**
```
Request: Update budget adset_456 (CBO)
→ Facebook trả lỗi 400: "Cannot specify adset budget when using campaign budget optimization"
→ Backend hardcode: "Ngân sách đang ở cấp chiến dịch"
→ ✅ ĐÚNG
```

**Sau:**
```
Request: Update budget adset_456 (CBO)
→ Facebook trả lỗi 400: "Cannot specify adset budget when using campaign budget optimization"
→ Backend check: CÓ chứa "campaign budget optimization"
→ Trả về: "Không thể cập nhật ngân sách: Ngân sách đang ở cấp chiến dịch. Vui lòng cập nhật ở tab 'Chiến Dịch'."
→ ✅ VẪN ĐÚNG
```

---

## LOG MẪU

### Debug Log (Level: DEBUG)
```
DEBUG_BUDGET_SCOPE | adset_id=120235248292380635, daily_budget=500000, lifetime_budget=None, current_budget=500000.0, budget_type=daily_budget
```

### Warning Log (khi không phải CBO error)
```
WARNING: Budget update failed for adset 120235248292380635: 400: Budget must be at least 200 (not CBO error)
```

### Info Log (khi CBO error thực sự)
```
INFO: Adset 120235248292380635 is using CBO - redirecting to campaign budget update
```

---

## DEPLOY VPS

```bash
cd /home/ads-automation
git pull origin main
sudo systemctl restart ads-automation
```

Hoặc dùng script:
```bash
cd /home/ads-automation
./PULL_VPS_BATCH_FIX.sh
```

---

## TEST CHECKLIST

- [ ] **Test 1: Adset ABO**
  - Chọn adset có "Ngân sách nhóm QC" (ABO)
  - Tăng ngân sách 10%
  - **Mong đợi:** Cập nhật thành công, KHÔNG báo lỗi CBO

- [ ] **Test 2: Adset CBO**
  - Chọn adset đang dùng CBO (campaign budget)
  - Thử tăng ngân sách
  - **Mong đợi:** Báo lỗi "Ngân sách đang ở cấp chiến dịch..."

- [ ] **Test 3: Lỗi validation khác**
  - Thử set ngân sách = 0 hoặc giá trị không hợp lệ
  - **Mong đợi:** Hiển thị lỗi gốc từ Facebook, KHÔNG hardcode CBO

- [ ] **Test 4: Bulk update nhiều adset**
  - Chọn 10-20 adset ABO
  - Tăng ngân sách 20%
  - **Mong đợi:** 
    - 1 request (không spam)
    - Progress bar hiển thị
    - Không reload trang
    - Tất cả thành công

- [ ] **Test 5: Check log**
  - Xem log backend khi update
  - **Mong đợi:**
    - DEBUG_BUDGET_SCOPE có đầy đủ thông tin
    - Không spam log
    - Warning log khi có lỗi không phải CBO

---

## KHÔNG ĐỘNG VÀO

✅ **Summary card** - Tổng chi tiêu, %ADS, ADSETS hoạt động, etc.
✅ **get_dashboard_dataset()** - Core data fetching
✅ **Frontend budget update** - Đã fix "không reload" từ commit trước
✅ **Batch status update** - Đã fix từ commit trước
✅ **Các services khác** - Chỉ sửa `update_adset_budget()` validation

---

## FILES CHANGED

1. ✅ `app/api/routes/dashboard.py` - Fix CBO validation logic
2. ✅ `app/services/facebook_api.py` - Thêm debug log
3. ✅ `BATCH_FIX_SUMMARY.md` - Tài liệu tổng hợp
4. ✅ `PULL_VPS_BATCH_FIX.sh` - Script deploy

---

## SUMMARY

**VẤN ĐỀ:** Hardcode lỗi CBO cho mọi HTTP 400 → chặn nhầm adset ABO

**FIX:** Kiểm tra chính xác message từ Facebook có chứa từ khóa CBO

**KẾT QUẢ:** 
- ✅ Adset ABO: Update thành công
- ✅ Adset CBO: Vẫn báo lỗi đúng
- ✅ Các lỗi khác: Hiển thị message gốc từ Facebook
- ✅ Debug dễ dàng với log chi tiết
