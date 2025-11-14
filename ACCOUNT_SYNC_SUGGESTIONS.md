# 💡 GỢI Ý: Cách Lấy Đúng Tài Khoản Quảng Cáo Hay Sử Dụng

## Vấn Đề Hiện Tại
- Logic đồng bộ hiện tại lấy **TẤT CẢ** tài khoản quảng cáo mà user có quyền
- Không phải tất cả đều là tài khoản hay sử dụng
- Cần cách xác định chính xác tài khoản hay dùng

## Các Phương Án Đề Xuất

### **Phương Án 1: Dùng Activity Log API (Đã Implement)**
**Ưu điểm:**
- Xác định chính xác ai đã thực hiện hành động (token owner hoặc BM)
- Biết được thời gian hoạt động gần đây
- Phù hợp với yêu cầu ban đầu

**Nhược điểm:**
- Cần quyền đặc biệt để xem activity log
- Có thể chậm nếu có nhiều accounts (mỗi account 1 API call)
- Một số accounts có thể không có quyền xem activity log

**Cách cải thiện:**
- Cache kết quả activity check (ví dụ: cache 1 giờ)
- Chỉ check activity cho accounts đã có trong database (không check tất cả accounts từ Facebook)
- Kết hợp với insights data để xác nhận

---

### **Phương Án 2: Dùng Insights Data (Impressions/Spend)**
**Ưu điểm:**
- Nhanh hơn (có thể batch nhiều accounts)
- Không cần quyền đặc biệt
- Dữ liệu chính xác về hoạt động thực tế

**Nhược điểm:**
- Không biết ai đã thực hiện hành động (có thể là người khác, không phải token owner)
- Có thể bao gồm accounts được quản lý bởi người khác

**Logic đề xuất:**
```python
# Lấy insights 7 ngày qua cho tất cả accounts
# Chỉ lấy accounts có:
# - impressions > 0 HOẶC spend > 0 trong 7 ngày qua
# - Và account đó thuộc về user (có trong database của user)
```

---

### **Phương Án 3: Kết Hợp Activity Log + Insights (Khuyến Nghị)**
**Ưu điểm:**
- Chính xác nhất: vừa biết ai thực hiện, vừa biết có hoạt động thực tế
- Có fallback nếu activity log không có quyền

**Logic đề xuất:**
1. **Bước 1:** Lấy tất cả accounts từ Facebook (như hiện tại)
2. **Bước 2:** Filter bằng Insights:
   - Chỉ giữ accounts có impressions > 0 hoặc spend > 0 trong 7 ngày qua
3. **Bước 3:** Xác nhận bằng Activity Log (nếu có quyền):
   - Chỉ giữ accounts có activity từ token owner hoặc BM
4. **Bước 4:** Chỉ sync những accounts đã pass cả 2 bước

**Code mẫu:**
```python
def get_frequently_used_accounts(access_token, token_owner_name):
    # Bước 1: Lấy tất cả accounts
    all_accounts = fetch_facebook_ad_accounts(access_token)
    
    # Bước 2: Filter bằng Insights (nhanh)
    accounts_with_insights = []
    for acc in all_accounts:
        if check_account_has_activity_last_7_days(access_token, acc['account_id']):
            accounts_with_insights.append(acc)
    
    # Bước 3: Xác nhận bằng Activity Log (nếu có quyền)
    frequently_used = []
    for acc in accounts_with_insights:
        try:
            if check_account_has_activity_from_token_owner_or_bm(
                access_token, 
                acc['account_id'], 
                token_owner_name, 
                days=7
            ):
                frequently_used.append(acc)
        except:
            # Nếu không có quyền, vẫn giữ account (fallback)
            frequently_used.append(acc)
    
    return frequently_used
```

---

### **Phương Án 4: User Tự Chọn (Đơn Giản Nhất)**
**Ưu điểm:**
- Đơn giản, không cần logic phức tạp
- User tự quyết định accounts nào hay dùng
- Không phụ thuộc vào API permissions

**Cách thực hiện:**
1. User thêm thủ công các accounts hay dùng
2. Có thể thêm tính năng "Đánh dấu hay dùng" (favorite/star)
3. Có thể thêm tính năng "Gợi ý" dựa trên insights (nhưng user vẫn tự chọn)

---

### **Phương Án 5: Dùng Business Manager API**
**Ưu điểm:**
- Có thể lấy accounts được quản lý bởi BM cụ thể
- Biết được relationship giữa user và accounts

**Nhược điểm:**
- Cần quyền business_management
- Phức tạp hơn

**Logic đề xuất:**
```python
# Lấy BM ID từ token
# Lấy accounts thuộc BM đó
# Filter accounts có activity trong 7 ngày
```

---

## Khuyến Nghị

### **Ngắn Hạn (Hiện Tại):**
- ✅ **Chỉ dùng thêm thủ công** (như user yêu cầu)
- ✅ Accounts thêm thủ công mặc định `enabled=False`
- ✅ User tự quản lý accounts hay dùng

### **Dài Hạn (Khi Cần Sync):**
- ✅ **Phương Án 3: Kết Hợp Activity Log + Insights**
  - Nhanh (insights filter trước)
  - Chính xác (activity log xác nhận)
  - Có fallback nếu không có quyền

### **Tùy Chọn:**
- Thêm tính năng "Gợi ý accounts" dựa trên insights
- User có thể chọn sync hoặc không
- Cache kết quả để tăng tốc độ

---

## Các Cải Tiến Có Thể Thêm

1. **Smart Suggestions:**
   - Khi user click "Thêm Account", hiển thị gợi ý các accounts có activity gần đây
   - User có thể chọn từ danh sách gợi ý

2. **Batch Activity Check:**
   - Thay vì check từng account, có thể batch check nhiều accounts cùng lúc
   - Giảm số lượng API calls

3. **Caching:**
   - Cache kết quả activity check (1-2 giờ)
   - Giảm số lượng API calls khi user refresh

4. **User Preferences:**
   - Cho phép user cấu hình tiêu chí "hay dùng":
     - Số ngày gần đây (7, 14, 30 ngày)
     - Minimum impressions/spend
     - Chỉ token owner hoặc cả BM

