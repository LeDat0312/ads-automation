# Hệ Thống Via Token - Facebook Account Management

## Tổng Quan

Hệ thống mới cho phép lưu trữ và tái sử dụng Facebook Access Token (Via) thay vì phải copy-paste token thủ công mỗi lần kết nối Fanpage.

### Lợi Ích
✅ **Không cần dán token lần nữa** - Lưu 1 lần, dùng nhiều nơi  
✅ **Tách biệt Via Fanpage vs Via Ads** - Quản lý rõ ràng mục đích sử dụng  
✅ **Bảo mật tốt hơn** - Token được che dấu khi hiển thị  
✅ **Xác thực token** - Kiểm tra token còn hiệu lực trước khi dùng  
✅ **UX tốt hơn** - Modal 2 bước trực quan

---

## 🏗️ Backend Implementation (✅ HOÀN THÀNH 100%)

### 1. Database Layer

**Model: `FacebookAccount`** (`app/models/facebook_account.py`)
```python
class FacebookAccountType(enum.Enum):
    FANPAGE = "fanpage"  # Via cho quản lý Trang
    ADS = "ads"          # Via cho tối ưu quảng cáo
    BOTH = "both"        # Cả hai mục đích

class FacebookAccount:
    id: UUID
    user_id: int                    # Chủ sở hữu
    name: str                       # Tên gợi nhớ (VD: "Via chính TikTok Shop")
    access_token: str               # Token (TODO: cần encrypt)
    token_type: FacebookAccountType # Loại token
    facebook_user_id: str           # FB User ID
    facebook_user_name: str         # Tên Facebook User
    expires_at: datetime            # Thời gian hết hạn
    is_active: bool                 # Còn hoạt động không
    last_verified_at: datetime      # Lần verify cuối
    created_at, updated_at: datetime
```

**Migration**: `migrations/add_facebook_accounts_table.py`
- ✅ Đã chạy thành công
- ✅ Bảng `facebook_accounts` đã được tạo trong database

---

### 2. API Layer

#### **A. Facebook Account Management API**
**File**: `app/api/routes/facebook_accounts.py` (250+ dòng)

**Base URL**: `/api/facebook-accounts`

##### **1. GET /api/facebook-accounts**
Lấy danh sách Via tokens của user hiện tại

**Query Params**:
- `type` (optional): `fanpage` | `ads` | `both` - Lọc theo loại
- `is_active` (optional): `true` | `false` - Lọc theo trạng thái

**Response**:
```json
[
  {
    "id": "uuid",
    "name": "Via TikTok Shop chính",
    "token_type": "fanpage",
    "facebook_user_id": "123456789",
    "facebook_user_name": "John Doe",
    "expires_at": "2024-12-31T23:59:59",
    "is_active": true,
    "last_verified_at": "2024-01-15T10:30:00",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-15T10:30:00",
    "access_token_preview": "EAABsbCS9i...4n8f"  // Masked: first 10 + last 4
  }
]
```

**Logic đặc biệt**:
- `?type=fanpage` → trả về cả `FANPAGE` và `BOTH`
- `?type=ads` → trả về cả `ADS` và `BOTH`

---

##### **2. POST /api/facebook-accounts**
Tạo Via token mới

**Request Body**:
```json
{
  "name": "Via TikTok Shop chính",
  "access_token": "EAABsbCS9iY4BOz...",
  "token_type": "fanpage"  // or "ads" or "both"
}
```

**Response**: Same as GET (single object)

**Validation**:
- ✅ Kiểm tra token hợp lệ bằng Graph API `/me`
- ✅ Lấy `facebook_user_id`, `facebook_user_name`
- ✅ Tự động set `expires_at` (60 ngày từ bây giờ - có thể cập nhật sau)
- ✅ Lỗi nếu token không hợp lệ → 400 Bad Request

---

##### **3. PATCH /api/facebook-accounts/{id}**
Cập nhật Via token

**Request Body** (tất cả optional):
```json
{
  "name": "Via mới",
  "access_token": "EAA...",  // Nếu đổi token
  "token_type": "both",
  "is_active": false         // Vô hiệu hóa
}
```

**Notes**:
- Nếu đổi `access_token` → tự động verify lại và update metadata
- Chỉ owner mới update được

---

##### **4. DELETE /api/facebook-accounts/{id}**
Xóa Via token

**Response**: 204 No Content

---

##### **5. POST /api/facebook-accounts/{id}/verify**
Xác thực token còn hoạt động

**Response**:
```json
{
  "valid": true,
  "facebook_user_id": "123456789",
  "facebook_user_name": "John Doe",
  "message": "Token hợp lệ"
}
```

**Use case**: Kiểm tra trước khi dùng token đã lưu

---

##### **6. GET /api/facebook-accounts/{id}/pages**
Lấy danh sách Fanpage từ Via token

**Response**:
```json
[
  {
    "id": "987654321",
    "name": "Shop Thời Trang ABC",
    "access_token": "EAABsbCS...",  // Page access token
    "category": "Shopping & Retail",
    "tasks": ["MANAGE", "CREATE_CONTENT"],
    "picture_url": "https://..."
  }
]
```

**Graph API Call**: `/me/accounts?fields=id,name,access_token,category,tasks,picture`

**Use case**: Để hiển thị danh sách checkbox trong modal bước 2

---

#### **B. Channel Creation with Via Token**
**File**: `app/api/routes/channels_settings.py` (đã cập nhật)

##### **1. POST /api/channels/facebook/from-saved-account** ✨ MỚI
Tạo nhiều kênh từ danh sách Fanpage (bulk connect)

**Request Body**:
```json
{
  "facebook_account_id": "uuid",
  "page_ids": ["123", "456", "789"]
}
```

**Process**:
1. Lấy Via token từ `facebook_account_id`
2. Với mỗi `page_id`:
   - Gọi Graph API `/page_id?fields=id,name,picture`
   - Tạo/update `Channel` qua `ChannelsService.upsert_manual_facebook_channel()`
   - Subscribe webhook
3. Trả về danh sách channels đã tạo

**Response**: Array of `ChannelRead`

**Error Handling**:
- Nếu 1 page lỗi → ghi log, tiếp tục các page khác
- Nếu tất cả đều lỗi → 400 Bad Request với chi tiết lỗi

---

##### **2. POST /api/channels/facebook/manual-v2** ✨ MỚI
Thêm Fanpage thủ công (nâng cấp từ version cũ)

**Request Body**:
```json
{
  "page_id": "123456789",
  "page_name_override": "Tên tùy chỉnh",  // optional
  "facebook_account_id": "uuid"           // optional
}
```

**Logic**:
- **Nếu có `facebook_account_id`**: Dùng token từ Via đã lưu
- **Nếu không**: Dùng App Token (chỉ lấy được thông tin public)

**Use case**:
- Tab 1 (checkbox list): Dùng endpoint `/from-saved-account`
- Tab 2 (manual ID): Dùng endpoint này với `facebook_account_id`

**Response**: Single `ChannelRead`

---

### 3. Service Layer

**File**: `app/services/facebook_account_service.py` (200+ dòng)

```python
class FacebookAccountService:
    def __init__(self, db: Session, user_id: int)
    
    # CRUD Operations
    def list_accounts(
        self, 
        token_type: Optional[FacebookAccountType] = None,
        is_active: Optional[bool] = None
    ) -> List[FacebookAccount]
    
    def get_account(self, account_id: str) -> Optional[FacebookAccount]
    def create_account(self, account_data: FacebookAccountCreate) -> FacebookAccount
    def update_account(self, account_id: str, account_data: FacebookAccountUpdate) -> FacebookAccount
    def delete_account(self, account_id: str) -> None
    
    # Token Verification
    async def verify_token(self, account_id: str) -> Dict[str, Any]
```

**Key Features**:
- ✅ User ownership check (chỉ owner mới thao tác được)
- ✅ Smart filtering (fanpage query includes BOTH type)
- ✅ Async token verification với Graph API
- ✅ TODO: Encrypt access_token trước khi lưu DB

---

### 4. Schema Layer

**File**: `app/schemas/facebook_account.py`

**7 Schemas**:
1. `FacebookAccountBase` - Base fields
2. `FacebookAccountCreate` - Cho POST
3. `FacebookAccountUpdate` - Cho PATCH
4. `FacebookAccountRead` - Response (với token masking)
5. `FacebookPageSimple` - Cho danh sách pages
6. `FacebookChannelFromAccount` - Bulk connect schema
7. `ManualFacebookChannelCreateV2` - Manual add v2

**Token Masking**:
```python
@field_validator('access_token_preview', mode='before')
def mask_token(cls, v, info):
    token = info.data.get('access_token')
    if not token:
        return ""
    if len(token) <= 14:
        return token
    return f"{token[:10]}...{token[-4:]}"
```

**Validators**:
- `page_ids` → deduplicate
- `page_id` → validate format

---

## 🎨 Frontend Implementation (❌ CHƯA LÀM - TODO)

### Yêu Cầu Chi Tiết

#### **1. Settings Page - Via Management**
**Location**: `/settings` (tab mới hoặc section mới)

**UI Components**:
```
┌─────────────────────────────────────────────────────┐
│ 🔑 Quản Lý Via Token                                │
├─────────────────────────────────────────────────────┤
│                                                      │
│ [+ Thêm Via Mới]                                    │
│                                                      │
│ ┌──────────────────────────────────────────────┐   │
│ │ 📱 Via TikTok Shop chính                      │   │
│ │ Loại: Fanpage | Đang hoạt động                │   │
│ │ Token: EAABsbCS9i...4n8f                      │   │
│ │ FB User: John Doe (ID: 123456789)             │   │
│ │ Hết hạn: 31/12/2024                           │   │
│ │                                                │   │
│ │ [Xác Thực] [Sửa] [Xóa]                        │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ ┌──────────────────────────────────────────────┐   │
│ │ 💰 Via Ads Automation                         │   │
│ │ Loại: Ads | Đang hoạt động                    │   │
│ │ ...                                            │   │
│ └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Actions**:
- **Thêm Via Mới**: Modal với form
  - Tên gợi nhớ (text input)
  - Loại (select: Fanpage / Ads / Cả hai)
  - Access Token (textarea)
  - [Lưu] → POST `/api/facebook-accounts`
  
- **Xác Thực**: POST `/api/facebook-accounts/{id}/verify`
  - Show toast: ✅ Token hợp lệ / ❌ Token hết hạn
  
- **Sửa**: Modal tương tự form thêm (pre-filled)
  - PATCH `/api/facebook-accounts/{id}`
  
- **Xóa**: Confirm dialog → DELETE `/api/facebook-accounts/{id}`

---

#### **2. Channel Management - Manual Add Modal 2 Steps**
**Location**: `/channels` (nút "Thêm Fanpage")

**Step 1: Chọn Via**
```
┌─────────────────────────────────────────────────────┐
│ 🔗 Kết Nối Fanpage - Bước 1/2                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Chọn Via Token:                                     │
│ ┌────────────────────────────────────────────────┐ │
│ │ 📱 Via TikTok Shop chính (Fanpage)            ▼│ │
│ └────────────────────────────────────────────────┘ │
│                                                      │
│                                    [Tiếp Theo →]    │
└─────────────────────────────────────────────────────┘
```

**API Call**: GET `/api/facebook-accounts?type=fanpage`

**State**:
```typescript
const [selectedVia, setSelectedVia] = useState<FacebookAccount | null>(null);
```

---

**Step 2: Chọn Fanpage**

**Tab 1: Chọn Từ Danh Sách** (default)
```
┌─────────────────────────────────────────────────────┐
│ 🔗 Kết Nối Fanpage - Bước 2/2                       │
├─────────────────────────────────────────────────────┤
│ Via: Via TikTok Shop chính                   [← Lùi]│
│                                                      │
│ [Tải Danh Sách Fanpage]  🔄 Đang tải...             │
│                                                      │
│ 🔍 Tìm kiếm: [________________]                      │
│                                                      │
│ ┌──────────────────────────────────────────────┐   │
│ │ [✓] Shop Thời Trang ABC (987654321)          │   │
│ │ [ ] Shop Mỹ Phẩm XYZ (123456789)             │   │
│ │ [✓] Page Test 123 (555555555)                │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ Đã chọn: 2 trang                                    │
│                                                      │
│                      [Hủy] [Kết Nối (2 trang)]      │
└─────────────────────────────────────────────────────┘
```

**API Calls**:
1. `[Tải Danh Sách]` → GET `/api/facebook-accounts/{id}/pages`
2. `[Kết Nối]` → POST `/api/channels/facebook/from-saved-account`
   ```json
   {
     "facebook_account_id": "uuid",
     "page_ids": ["987654321", "555555555"]
   }
   ```

**Features**:
- Checkbox table
- Search/filter by name
- Bulk select all
- Loading state khi fetch pages
- Toast notification on success/error

---

**Tab 2: Nhập ID Thủ Công**
```
┌─────────────────────────────────────────────────────┐
│ 🔗 Kết Nối Fanpage - Bước 2/2                       │
├─────────────────────────────────────────────────────┤
│ Via: Via TikTok Shop chính                   [← Lùi]│
│                                                      │
│ [Chọn Từ Danh Sách] | [Nhập ID Thủ Công] ←──────┐  │
│                                                   │  │
│ ID Trang Facebook:                                │  │
│ ┌────────────────────────────────────────────┐   │  │
│ │ 123456789                                  │   │  │
│ └────────────────────────────────────────────┘   │  │
│                                                   │  │
│ Tên trang (tùy chọn - để trống để tự động lấy): │  │
│ ┌────────────────────────────────────────────┐   │  │
│ │                                            │   │  │
│ └────────────────────────────────────────────┘   │  │
│                                                   │  │
│ [✓] Sử dụng Via để xác thực                      │  │
│                                                   │  │
│                      [Hủy] [Kết Nối]             │  │
└──────────────────────────────────────────────────┘  │
```

**API Call**: POST `/api/channels/facebook/manual-v2`
```json
{
  "page_id": "123456789",
  "page_name_override": "",  // optional
  "facebook_account_id": "uuid"  // if checkbox checked
}
```

**Logic**:
- Nếu checkbox **unchecked**: `facebook_account_id` = null → dùng App Token
- Nếu checkbox **checked**: gửi Via ID → dùng Via token

---

### Frontend Tech Stack
- **React** + **TypeScript**
- **Tailwind CSS** cho styling
- **React Hook Form** cho form validation
- **Axios** cho API calls
- **React Toastify** cho notifications

---

## 📋 Testing Checklist

### Backend ✅
- [x] Migration chạy thành công
- [x] Model FacebookAccount được import đúng
- [x] Service layer hoạt động
- [x] API routes không có lỗi syntax
- [x] Router đã đăng ký trong main.py
- [x] Backend server khởi động thành công

### Frontend ❌ (TODO)
- [ ] UI Settings - Via management
- [ ] Add Via modal
- [ ] Edit Via modal
- [ ] Delete Via confirmation
- [ ] Verify token action
- [ ] Token masking display
- [ ] Channel modal Step 1 (Via selection)
- [ ] Channel modal Step 2 Tab 1 (Page list)
- [ ] Channel modal Step 2 Tab 2 (Manual ID)
- [ ] Load pages button
- [ ] Checkbox table functionality
- [ ] Bulk connect action
- [ ] Toast notifications
- [ ] Error handling
- [ ] Loading states

### Integration ❌ (TODO)
- [ ] End-to-end flow: Add Via → Connect Fanpage (list)
- [ ] End-to-end flow: Add Via → Connect Fanpage (manual)
- [ ] Token expiration handling
- [ ] Invalid token error messages
- [ ] Graph API rate limiting

---

## 🚀 Deployment to VPS

### Bước 1: Deploy Backend
```bash
# Trên VPS
cd /path/to/project
./force_pull.sh  # Hoặc git pull thủ công

# Chạy migration
source venv/bin/activate
python -m migrations.add_facebook_accounts_table

# Restart supervisor
sudo supervisorctl restart backend
```

### Bước 2: Deploy Frontend (sau khi hoàn thành UI)
```bash
# Local
cd frontend
npm run build

# Copy dist to VPS hoặc dùng git
```

### Bước 3: Verify
```bash
# Test API
curl http://your-vps-ip:8000/api/facebook-accounts \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check logs
tail -f /var/log/supervisor/backend.log
```

---

## 📊 Database Schema

```sql
CREATE TABLE facebook_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    token_type VARCHAR(50) NOT NULL,  -- 'fanpage', 'ads', 'both'
    facebook_user_id VARCHAR(255),
    facebook_user_name VARCHAR(255),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_facebook_accounts_user_id ON facebook_accounts(user_id);
CREATE INDEX idx_facebook_accounts_token_type ON facebook_accounts(token_type);
CREATE INDEX idx_facebook_accounts_is_active ON facebook_accounts(is_active);
```

---

## 🔒 Security Considerations

### TODO: Encrypt Access Tokens
**Current**: Tokens lưu plain text trong DB (NGUY HIỂM!)

**Recommended Solution**:
```python
# app/core/security.py
from cryptography.fernet import Fernet

class TokenEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, token: str) -> str:
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()

# .env
ENCRYPTION_KEY=your-secret-key-here
```

**Apply to**:
- `FacebookAccountService.create_account()` → encrypt before save
- `FacebookAccountService.update_account()` → encrypt if token changed
- `FacebookAccountService.get_account()` → decrypt when read
- `GET /api/facebook-accounts/{id}/pages` → decrypt before use

---

## 🎯 Next Steps

### Immediate (Backend - DONE ✅)
- [x] Create FacebookAccount model
- [x] Create schemas
- [x] Create service layer
- [x] Create API routes (6 endpoints)
- [x] Add channel integration endpoints (2 endpoints)
- [x] Register router in main.py
- [x] Create database migration
- [x] Run migration
- [x] Test backend startup

### Short-term (Frontend - TODO ❌)
1. **Settings Page**:
   - [ ] Create Via management UI
   - [ ] Add Via form modal
   - [ ] Edit/Delete actions
   - [ ] Verify token button
   - [ ] Display token masked

2. **Channel Management**:
   - [ ] Redesign "Add Fanpage" modal
   - [ ] Implement 2-step wizard
   - [ ] Step 1: Via dropdown
   - [ ] Step 2 Tab 1: Page list with checkboxes
   - [ ] Step 2 Tab 2: Manual ID input
   - [ ] Load pages button
   - [ ] Bulk connect functionality

3. **Testing**:
   - [ ] Test all user flows
   - [ ] Test error scenarios
   - [ ] Test loading states
   - [ ] Test Vietnamese UI text

### Long-term (Enhancements)
- [ ] **Token Encryption**: Implement `cryptography.fernet`
- [ ] **Auto Token Refresh**: Detect expiration, show warning
- [ ] **Token Usage Analytics**: Track which channels use which Via
- [ ] **Batch Operations**: Delete multiple Vias at once
- [ ] **Export/Import**: Backup Via tokens (encrypted)
- [ ] **Audit Log**: Track Via token usage history

---

## 📞 Support

- **Backend API Docs**: http://localhost:8000/docs
- **Graph API Explorer**: https://developers.facebook.com/tools/explorer/
- **Graph API Docs**: https://developers.facebook.com/docs/graph-api

---

## 📝 Vietnamese UI Text Reference

### Settings Page
- "Quản Lý Via Token"
- "Thêm Via Mới"
- "Tên gợi nhớ"
- "Loại token"
- "Fanpage" / "Quảng cáo" / "Cả hai"
- "Access Token"
- "Đang hoạt động"
- "Hết hạn"
- "Xác Thực"
- "Sửa"
- "Xóa"
- "Bạn có chắc muốn xóa Via này?"

### Channel Modal
- "Kết Nối Fanpage"
- "Bước 1/2"
- "Bước 2/2"
- "Chọn Via Token"
- "Tiếp Theo"
- "Lùi"
- "Tải Danh Sách Fanpage"
- "Đang tải..."
- "Tìm kiếm"
- "Chọn Từ Danh Sách"
- "Nhập ID Thủ Công"
- "ID Trang Facebook"
- "Tên trang (tùy chọn - để trống để tự động lấy)"
- "Sử dụng Via để xác thực"
- "Đã chọn: X trang"
- "Kết Nối"
- "Kết Nối (X trang)"

### Toast Messages
- "✅ Via đã được lưu thành công"
- "✅ Token hợp lệ"
- "❌ Token không hợp lệ hoặc đã hết hạn"
- "✅ Đã kết nối X Fanpage thành công"
- "❌ Không thể kết nối Fanpage. Vui lòng thử lại."
- "⚠️ Một số Fanpage không kết nối được"

---

## 🎉 Summary

**Backend**: ✅ **100% HOÀN THÀNH**
- Model + Migration ✅
- Service layer ✅
- 8 API endpoints ✅
- Router registered ✅
- Database migrated ✅
- Server running ✅

**Frontend**: ❌ **CHƯA BẮT ĐẦU**
- Settings UI: 0%
- Channel Modal: 0%

**Estimated Frontend Work**: 6-8 hours
- Settings Page: 2-3 hours
- Channel Modal: 3-4 hours
- Testing: 1-2 hours

---

**🚀 Ready for Frontend Development!**
