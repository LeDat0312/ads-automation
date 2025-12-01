# Sửa lỗi module "Kết nối Fanpage Facebook"

## Tóm tắt các vấn đề đã sửa

### 1. ✅ Sửa lỗi GET `/api/facebook-accounts/{id}/pages` trả về 400

**Vấn đề:**
- Endpoint trả về 400 Bad Request khi gọi
- Tab "Chọn từ danh sách" không load được Fanpage
- Thông báo lỗi không rõ ràng

**Giải pháp:**
- Thêm logging chi tiết cho mỗi bước gọi Graph API
- Map Facebook error codes sang thông báo tiếng Việt rõ ràng:
  - Error code 190: "Token Facebook đã hết hạn hoặc không hợp lệ"
  - Error code 200: "Token không có đủ quyền để lấy danh sách Fanpage"
  - Các lỗi khác: Hiển thị message từ Facebook
- Xử lý đúng response JSON khi có lỗi

**File thay đổi:**
- `app/services/facebook_account_service.py` - Method `get_pages_with_permissions()`

### 2. ✅ Đảm bảo lưu đúng Page Access Token khi kết nối

**Vấn đề:**
- Kết nối thủ công tạo được Channel nhưng không chắc đã lưu Page Access Token
- Không kiểm tra quyền QTV để đăng bài/auto comment
- Không có cảnh báo rõ ràng về quyền

**Giải pháp:**

#### A. Tạo method mới `upsert_facebook_page_channel_from_account()`
- Thay thế method cũ `upsert_facebook_page_channel()`
- Nhận thêm các tham số: `is_admin`, `can_publish`, `can_moderate`
- Log rõ ràng việc lưu token và quyền
- Xử lý trường hợp không có Page Access Token (set None)

**File thay đổi:**
- `app/services/channels_service.py`

#### B. Cải thiện endpoint `/channels/facebook/from-saved-account`
- Gọi `get_pages_with_permissions()` để lấy đầy đủ thông tin quyền
- Lấy Page Access Token từ response của `/me/accounts`
- Truyền các flag quyền vào method upsert
- Subscribe webhook chỉ khi có token và quyền đủ
- Trả về warnings cho từng page nếu thiếu quyền

**File thay đổi:**
- `app/api/routes/channels_settings.py` - Endpoint `/channels/facebook/from-saved-account`

#### C. Cải thiện endpoint `/channels/facebook/manual-v2`
- Nếu có `facebook_account_id`:
  - Tìm page trong `/me/accounts` để lấy Page Access Token
  - Nếu không tìm thấy, thử gọi trực tiếp `/{page_id}?fields=access_token`
  - Kiểm tra và lưu quyền `is_admin`, `can_publish`, `can_moderate`
- Nếu không có `facebook_account_id`:
  - Dùng App Token để lấy thông tin công khai
  - Set tất cả quyền = False
- Trả về `has_page_token` flag để FE biết
- Tạo warning message phù hợp với từng trường hợp

**File thay đổi:**
- `app/api/routes/channels_settings.py` - Endpoint `/channels/facebook/manual-v2`

### 3. ✅ Cải thiện Frontend - Thông báo rõ ràng

**Vấn đề:**
- Toast message chung chung
- Không hiển thị lỗi cụ thể từ backend
- Không cảnh báo khi thiếu quyền

**Giải pháp:**

#### A. Tab "Chọn từ danh sách"
- Hiển thị error detail từ backend khi load pages thất bại
- Toast success khi load thành công
- Kiểm tra `access_token` và `is_admin` của pages đã chọn
- Hiển thị toast warning nếu có page thiếu quyền
- Toast success chỉ khi tất cả pages đều có đủ quyền

#### B. Tab "Nhập ID thủ công"
- Đọc `has_page_token` từ response
- Hiển thị toast phù hợp:
  - Success: Khi có đủ quyền và token
  - Warning: Khi là QTV nhưng không có token
  - Warning: Khi có warning_message từ backend
- Hiển thị error detail từ backend

#### C. Cập nhật TypeScript types
- Thêm `has_page_token: boolean` vào response type của `connectPageManualV2`

**File thay đổi:**
- `frontend/src/components/ConnectFacebookPageModal.tsx`
- `frontend/src/api/facebookChannels.ts`

## Kết quả

### Trước khi sửa:
❌ GET `/api/facebook-accounts/1/pages` → 400 Bad Request (không rõ lý do)
❌ Tab "Chọn từ danh sách" trắng, không load được
❌ Kết nối thủ công tạo được Channel nhưng không chắc có token
❌ Không biết Channel có quyền đăng bài/auto comment không

### Sau khi sửa:
✅ GET `/api/facebook-accounts/1/pages` → 200 với danh sách pages + quyền
✅ Nếu lỗi → 400 với message tiếng Việt rõ ràng (token hết hạn, thiếu quyền, etc.)
✅ Tab "Chọn từ danh sách" hiển thị đầy đủ pages với badge quyền
✅ Kết nối từ danh sách → Lưu đúng Page Access Token + quyền
✅ Kết nối thủ công → Tự động tìm và lưu Page Access Token nếu Via có quyền
✅ Toast message rõ ràng về quyền và khả năng sử dụng tính năng

## Kiểm tra

### 1. Test GET pages từ Via
```bash
# Với token hợp lệ
GET /api/facebook-accounts/1/pages
→ 200 OK, trả về list pages với is_admin, can_publish, can_moderate

# Với token hết hạn
GET /api/facebook-accounts/1/pages
→ 400 Bad Request
→ detail: "Token Facebook đã hết hạn hoặc không hợp lệ. Vui lòng tạo lại token."

# Với token thiếu quyền
GET /api/facebook-accounts/1/pages
→ 400 Bad Request
→ detail: "Token không có đủ quyền để lấy danh sách Fanpage..."
```

### 2. Test kết nối từ danh sách
```bash
POST /api/channels/facebook/from-saved-account
{
  "facebook_account_id": 1,
  "page_ids": ["123456789"]
}

→ 200 OK
→ Channels được tạo với Page Access Token (nếu có)
→ Webhook được subscribe (nếu có quyền)
```

### 3. Test kết nối thủ công
```bash
# Với Via có quyền
POST /api/channels/facebook/manual-v2
{
  "page_id": "123456789",
  "facebook_account_id": 1
}

→ 200 OK
→ {
  "channel": {...},
  "is_admin": true,
  "has_page_token": true,
  "warning_message": null
}

# Với Via không có quyền
→ 200 OK
→ {
  "channel": {...},
  "is_admin": false,
  "has_page_token": false,
  "warning_message": "Via này chưa là Quản trị viên..."
}

# Không dùng Via
POST /api/channels/facebook/manual-v2
{
  "page_id": "123456789"
}

→ 200 OK
→ {
  "channel": {...},
  "is_admin": false,
  "has_page_token": false,
  "warning_message": "Kênh được tạo không có Via quản lý..."
}
```

## Lưu ý

1. **Page Access Token được lưu mã hóa** trong database (field `access_token_encrypted`)
2. **Webhook chỉ subscribe khi:**
   - Có Page Access Token
   - Có quyền `can_publish` hoặc `can_moderate`
3. **Warning messages** giúp user biết cần làm gì để có đủ quyền
4. **Logging chi tiết** giúp debug dễ dàng hơn

## Các file đã thay đổi

1. `app/services/facebook_account_service.py` - Sửa `get_pages_with_permissions()`
2. `app/services/channels_service.py` - Thêm `upsert_facebook_page_channel_from_account()`
3. `app/api/routes/channels_settings.py` - Sửa 2 endpoints kết nối, thêm import httpx
4. `frontend/src/components/ConnectFacebookPageModal.tsx` - Cải thiện UX và error handling
5. `frontend/src/api/facebookChannels.ts` - Cập nhật TypeScript types
