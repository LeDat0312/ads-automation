# Hoàn thiện xử lý Token hết hạn cho Via Facebook

## Tổng quan

Chức năng "Tải danh sách Fanpage" giờ đây xử lý hoàn chỉnh trường hợp token hết hạn, với:
- ✅ Tự động phát hiện và đánh dấu token hết hạn
- ✅ Lưu lỗi vào database để tracking
- ✅ Hiển thị message tiếng Việt rõ ràng
- ✅ Cảnh báo user trước khi họ gặp lỗi
- ✅ Tự động clear error khi token hoạt động lại

---

## Các thay đổi

### 1. DATABASE

#### Thêm column `last_error` vào bảng `facebook_accounts`

```sql
ALTER TABLE facebook_accounts 
ADD COLUMN last_error TEXT DEFAULT NULL;
```

**Mục đích:**
- Lưu message lỗi cuối cùng từ Facebook API
- Giúp user và admin biết chính xác vấn đề là gì
- Tracking lịch sử lỗi

**Migration:** `migrations/add_last_error_to_facebook_accounts.py`

---

### 2. BACKEND

#### A. Model `FacebookAccount`

Thêm field:
```python
last_error = Column(Text, nullable=True)  # Last error message from Facebook API
```

#### B. Schema `FacebookAccountRead`

Thêm field:
```python
last_error: Optional[str] = Field(None, description="Last error message from Facebook API")
```

#### C. Service `FacebookAccountService.get_pages_with_permissions()`

**Xử lý error code 190 (Token expired):**
```python
if error_code == 190:
    # Update account status in DB
    account.is_active = False
    account.last_error = error_message
    account.last_verified_at = datetime.utcnow()
    self.db.commit()
    
    # Return user-friendly Vietnamese message
    raise HTTPException(
        status_code=400,
        detail="Token Facebook của Via này đã hết hạn. Vui lòng cập nhật lại token trong 'Quản lý Via Facebook' trước khi tải danh sách Fanpage."
    )
```

**Xử lý error code 200 (Permissions):**
```python
elif error_code == 200:
    account.last_error = error_message
    account.last_verified_at = datetime.utcnow()
    self.db.commit()
    
    raise HTTPException(
        status_code=400,
        detail="Token không có đủ quyền để lấy danh sách Fanpage..."
    )
```

**Clear error khi token OK:**
```python
if account.last_error or not account.is_active:
    account.is_active = True
    account.last_error = None
    account.last_verified_at = datetime.utcnow()
    self.db.commit()
```

#### D. Service `FacebookAccountService.verify_token()`

Xử lý tương tự `get_pages_with_permissions()`:
- Error code 190 → set `is_active=False`, lưu `last_error`
- Success → set `is_active=True`, clear `last_error`

---

### 3. FRONTEND

#### A. Type `FacebookAccount`

Thêm field:
```typescript
last_error?: string;
```

#### B. Modal `ConnectFacebookPageModal`

**Hiển thị trạng thái trong dropdown:**
```tsx
<option key={via.id} value={via.id}>
  {via.name} {!via.is_active ? " (Token hết hạn)" : ""}
</option>
```

**Cảnh báo khi chọn Via không hoạt động:**
```tsx
{selectedViaId && viaAccounts.find(v => v.id === selectedViaId)?.is_active === false && (
  <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded">
    <p className="text-sm text-yellow-800">
      ⚠️ Token của Via này đã hết hạn. Vui lòng cập nhật lại token trong "Quản lý Via Facebook" trước khi tải danh sách Fanpage.
    </p>
  </div>
)}
```

**Hiển thị last_error:**
```tsx
{selectedViaId && viaAccounts.find(v => v.id === selectedViaId)?.last_error && (
  <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded">
    <p className="text-sm text-red-800">
      ❌ Lỗi: {viaAccounts.find(v => v.id === selectedViaId)?.last_error}
    </p>
  </div>
)}
```

**Xử lý error từ backend:**
```tsx
try {
  const res = await getPagesOfFacebookAccount(selectedViaId);
  setPages(res.data);
  toast.success(`Đã tải ${res.data.length} Fanpage từ Via.`);
} catch (e: any) {
  const errorDetail = e?.response?.data?.detail;
  if (errorDetail) {
    toast.error(errorDetail);  // Hiển thị message tiếng Việt từ backend
  } else {
    toast.error("Không thể tải danh sách Fanpage. Vui lòng kiểm tra lại Via.");
  }
}
```

---

## Flow hoàn chỉnh

### Scenario 1: Token hết hạn

1. **User chọn Via có token hết hạn**
   - Dropdown hiển thị: "Via Phi (Cầm Page) (Token hết hạn)"
   - Cảnh báo màu vàng xuất hiện

2. **User bấm "Tải danh sách Fanpage"**
   - Frontend gọi: `GET /api/facebook-accounts/1/pages`
   - Backend gọi Graph API: `GET /me/accounts`
   - Facebook trả về: `400 Bad Request, code=190`

3. **Backend xử lý:**
   ```python
   account.is_active = False
   account.last_error = "Error validating access token: Session has expired..."
   account.last_verified_at = datetime.utcnow()
   db.commit()
   
   raise HTTPException(
       status_code=400,
       detail="Token Facebook của Via này đã hết hạn. Vui lòng cập nhật lại token trong 'Quản lý Via Facebook' trước khi tải danh sách Fanpage."
   )
   ```

4. **Frontend hiển thị:**
   - Toast error: "Token Facebook của Via này đã hết hạn..."
   - Via được đánh dấu "(Token hết hạn)" trong dropdown
   - Hiển thị last_error nếu có

5. **User cập nhật token:**
   - Vào Settings → Facebook Via
   - Cập nhật token mới
   - Bấm "Xác thực token"
   - Backend verify → set `is_active=True`, clear `last_error`

### Scenario 2: Token OK

1. **User chọn Via hoạt động**
   - Dropdown hiển thị: "Via Phi (Cầm Page)"
   - Không có cảnh báo

2. **User bấm "Tải danh sách Fanpage"**
   - Backend gọi Graph API → 200 OK
   - Parse danh sách pages với quyền

3. **Backend clear error (nếu có):**
   ```python
   if account.last_error or not account.is_active:
       account.is_active = True
       account.last_error = None
       account.last_verified_at = datetime.utcnow()
       db.commit()
   ```

4. **Frontend hiển thị:**
   - Toast success: "Đã tải X Fanpage từ Via."
   - List pages với badge quyền

---

## Deploy lên VPS

### Cách 1: Script tự động (Khuyến nghị)

```bash
cd /home/adsuser/ads-automation && \
git pull origin main && \
chmod +x VPS_DEPLOY_TOKEN_FIX.sh && \
./VPS_DEPLOY_TOKEN_FIX.sh
```

### Cách 2: Từng bước

```bash
# 1. Pull code
cd /home/adsuser/ads-automation
git pull origin main

# 2. Kích hoạt venv
source venv/bin/activate

# 3. Chạy migrations
python -m migrations.add_color_hex_to_channel_groups
python -m migrations.add_last_error_to_facebook_accounts

# 4. Rebuild frontend
cd frontend
npm run build
cd ..

# 5. Restart services
sudo systemctl restart ads-automation
sudo systemctl restart nginx
```

### Cách 3: One-liner

```bash
cd /home/adsuser/ads-automation && git pull origin main && source venv/bin/activate && python -m migrations.add_color_hex_to_channel_groups && python -m migrations.add_last_error_to_facebook_accounts && cd frontend && npm run build && cd .. && sudo systemctl restart ads-automation && sudo systemctl restart nginx && echo "✅ Deploy hoàn tất!"
```

---

## Kiểm tra sau khi deploy

### 1. Kiểm tra migrations

```bash
# Kết nối database
psql -U adsuser -d ads_automation

# Kiểm tra column color_hex
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name='channel_groups' AND column_name='color_hex';

# Kiểm tra column last_error
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name='facebook_accounts' AND column_name='last_error';

# Exit
\q
```

### 2. Kiểm tra chức năng

**Test token hết hạn:**
1. Vào Settings → Facebook Via
2. Chọn Via có token hết hạn
3. Vào Settings → Channels
4. Bấm "Kết nối Fanpage"
5. Chọn Via đó → Bấm "Tải danh sách Fanpage"
6. Xem toast hiển thị: "Token Facebook của Via này đã hết hạn..."
7. Via được đánh dấu "(Token hết hạn)" trong dropdown

**Test token OK:**
1. Cập nhật token mới cho Via
2. Bấm "Xác thực token" → Thành công
3. Bấm "Tải danh sách Fanpage"
4. Xem list pages hiển thị với badge quyền

### 3. Xem logs

```bash
# Backend logs
sudo journalctl -u ads-automation -f

# Tìm log liên quan
sudo journalctl -u ads-automation | grep "Failed to get pages"
sudo journalctl -u ads-automation | grep "Token expired"
```

---

## Rollback nếu cần

```bash
cd /home/adsuser/ads-automation

# Rollback code
git reset --hard HEAD~1

# Xóa columns (nếu cần)
psql -U adsuser -d ads_automation -c "ALTER TABLE channel_groups DROP COLUMN IF EXISTS color_hex;"
psql -U adsuser -d ads_automation -c "ALTER TABLE facebook_accounts DROP COLUMN IF EXISTS last_error;"

# Rebuild và restart
cd frontend && npm run build && cd ..
sudo systemctl restart ads-automation
sudo systemctl restart nginx
```

---

## Lợi ích

### Trước khi fix:
❌ User bấm "Tải danh sách Fanpage" → 400 Bad Request
❌ Không biết lý do tại sao
❌ Tưởng là bug của hệ thống
❌ Không biết phải làm gì

### Sau khi fix:
✅ User thấy cảnh báo trước khi bấm
✅ Toast hiển thị: "Token đã hết hạn. Vui lòng cập nhật..."
✅ Via được đánh dấu "(Token hết hạn)"
✅ Biết chính xác phải làm gì: Cập nhật token
✅ Hệ thống tự động track trạng thái token
✅ Admin có thể xem last_error để debug

---

## Technical Details

### Error Codes từ Facebook

- **190**: Invalid OAuth 2.0 Access Token
  - Token hết hạn
  - Token bị thu hồi
  - Token không hợp lệ
  
- **200**: Permissions error
  - Thiếu quyền `pages_show_list`
  - Thiếu quyền `pages_read_engagement`
  
- **401**: Unauthorized
  - Token không được cấp quyền

### Database Schema

```sql
-- facebook_accounts table
CREATE TABLE facebook_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    access_token TEXT NOT NULL,
    token_type VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_error TEXT DEFAULT NULL,  -- NEW
    last_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### API Response Examples

**Token hết hạn:**
```json
{
  "detail": "Token Facebook của Via này đã hết hạn. Vui lòng cập nhật lại token trong 'Quản lý Via Facebook' trước khi tải danh sách Fanpage."
}
```

**Thiếu quyền:**
```json
{
  "detail": "Token không có đủ quyền để lấy danh sách Fanpage (thiếu pages_show_list hoặc pages_read_engagement). Vui lòng cấp lại quyền."
}
```

---

## Commit History

- `c00b249`: Feature: Hoàn thiện xử lý token hết hạn cho Via Facebook
- `b71d6a7`: Add: Hướng dẫn fix hoàn chỉnh cho VPS
- `9faeb7a`: Fix: Thêm migration cho column color_hex
- `e1c98e7`: Add: Script và hướng dẫn pull fix Fanpage về VPS
- `588c033`: Fix: Sửa lỗi kết nối Fanpage Facebook

---

## Support

Nếu gặp vấn đề:
1. Kiểm tra logs: `sudo journalctl -u ads-automation -f`
2. Kiểm tra database: `psql -U adsuser -d ads_automation`
3. Kiểm tra migrations đã chạy chưa
4. Rollback nếu cần
