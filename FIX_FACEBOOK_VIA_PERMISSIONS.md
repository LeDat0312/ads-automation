# Fix Facebook Via Permissions Detection

## 🐛 Vấn đề

1. **Tất cả Fanpage đều hiển thị "Không phải QTV"** - Dù user là Quản trị viên
2. **Lỗi 400 Bad Request** - Khi kết nối Fanpage từ danh sách

## 🔍 Nguyên nhân

### Vấn đề 1: Logic check quyền sai

Backend chỉ kiểm tra `tasks` (quyền của app), không kiểm tra `perms` (quyền của user).

**Code cũ (SAI):**
```python
is_admin = "MANAGE" in tasks  # ❌ Chỉ check app permissions
```

**Facebook Graph API thực tế:**
- `perms` = Quyền của USER trên Fanpage (ADMINISTER, EDIT_PROFILE, CREATE_CONTENT, MODERATE)
- `tasks` = Quyền của APP TOKEN trên Fanpage (MANAGE, CREATE_CONTENT, MODERATE, ADVERTISE, ANALYZE)

**Trường hợp phổ biến:**
- User là **Quản trị viên** → `perms` có `ADMINISTER` ✅
- Nhưng token chưa được cấp quyền → `tasks` không có `MANAGE` ❌
- Kết quả: Backend trả `is_admin = false` dù user là QTV

### Vấn đề 2: Thiếu debug logging

Endpoint `/channels/facebook/from-saved-account` không log request payload → Không biết lỗi 400 do đâu.

## ✅ Giải pháp

### 1. Backend: Check cả `perms` VÀ `tasks`

**File: `app/services/facebook_account_service.py`**

```python
# Graph API request - Thêm field "perms"
fields = "id,name,access_token,tasks,perms,category,link,picture{url}"

# Permission detection logic
has_admin_perm = "ADMINISTER" in perms  # User là QTV
has_manage_task = "MANAGE" in tasks     # App có quyền full
has_content_and_moderate = "CREATE_CONTENT" in tasks and "MODERATE" in tasks

# Kết luận: Cần CẢ 2 điều kiện
is_admin_for_app = has_admin_perm and (has_manage_task or has_content_and_moderate)

# Debug logging
logger.info(f"PAGE ROLES: id={page_id} perms={perms} tasks={tasks} is_admin_for_app={is_admin_for_app}")

# Warning messages phân biệt 2 trường hợp
if has_admin_perm and not is_admin_for_app:
    warning_message = "Bạn là QTV nhưng token chưa được cấp đủ quyền MANAGE/CREATE_CONTENT/MODERATE. Thêm lại Via với đủ quyền."
elif not has_admin_perm:
    warning_message = "Via này chưa là QTV của Fanpage"
```

### 2. Schema: Thêm field `perms`

**File: `app/schemas/facebook_account.py`**

```python
class FacebookPageSimple(BaseModel):
    id: str
    name: str
    picture_url: Optional[str] = None
    
    tasks: list[str] = Field(default_factory=list, description="App-level permissions")
    perms: list[str] = Field(default_factory=list, description="User-level permissions")  # ← THÊM
    
    is_admin: bool = Field(
        default=False,
        description="Via có quyền QTV VÀ app có đủ quyền automation"
    )
    can_publish: bool = Field(default=False)
    can_moderate: bool = Field(default=False)
    warning_message: Optional[str] = None
```

### 3. Frontend: TypeScript interface

**File: `frontend/src/api/facebookChannels.ts`**

```typescript
export interface FacebookPageSummary {
  id: string;
  name: string;
  picture_url?: string;
  
  tasks: string[];      // App permissions
  perms: string[];      // ← THÊM - User permissions
  
  is_admin: boolean;
  can_publish: boolean;
  can_moderate: boolean;
  warning_message?: string;
}
```

### 4. UI: Hiển thị 3 trạng thái badge

**File: `frontend/src/components/ConnectFacebookPageModal.tsx`**

```tsx
{page.is_admin ? (
  // ✅ Case 1: User là QTV VÀ app có đủ quyền
  <span className="bg-green-100 text-green-800" title="Via có quyền QTV và app đã được cấp quyền automation đầy đủ">
    ✓ QTV
  </span>
) : page.perms?.includes("ADMINISTER") ? (
  // ⚠️ Case 2: User là QTV NHƯNG app thiếu quyền
  <span className="bg-yellow-100 text-yellow-800" title="Bạn là QTV nhưng token chưa được cấp đủ quyền MANAGE/CREATE_CONTENT/MODERATE">
    ⚠ QTV nhưng app chưa đủ quyền
  </span>
) : (
  // ⚠️ Case 3: User không phải QTV
  <span className="bg-yellow-100 text-yellow-800" title="Via này chưa là QTV của Fanpage">
    ⚠ Không phải QTV
  </span>
)}
```

### 5. Debug logging cho 400 error

**File: `app/api/routes/channels_settings.py`**

```python
@router.post("/channels/facebook/from-saved-account")
async def create_channels_from_saved_account(data: FacebookChannelFromAccount, ...):
    logger.info(f"🔵 Connect pages - facebook_account_id={data.facebook_account_id}, page_ids={data.page_ids}, user_id={current_user.id}")
    # ... rest of code
```

## 🚀 Triển khai trên VPS

### Bước 1: Chạy script tự động

```bash
# Upload và chạy script
scp VPS_FIX_FACEBOOK_VIA_PERMISSIONS.sh root@YOUR_VPS:/root/
ssh root@YOUR_VPS "chmod +x /root/VPS_FIX_FACEBOOK_VIA_PERMISSIONS.sh && /root/VPS_FIX_FACEBOOK_VIA_PERMISSIONS.sh"
```

### Bước 2: Kiểm tra backend logs

```bash
ssh root@YOUR_VPS
sudo tail -f /var/log/supervisor/adstudio-stderr.log | grep -E 'PAGE ROLES|Connect pages'
```

Khi click "Tải danh sách Fanpage", bạn sẽ thấy:
```
PAGE ROLES: id=123456789 perms={'ADMINISTER', 'CREATE_CONTENT', 'MODERATE'} tasks={'CREATE_CONTENT', 'MODERATE'} is_admin_for_app=True
PAGE ROLES: id=987654321 perms={'EDIT_PROFILE'} tasks={'ANALYZE'} is_admin_for_app=False
```

Khi click "Kết nối Fanpage đã chọn":
```
🔵 Connect pages - facebook_account_id=5, page_ids=['123456789', '987654321'], user_id=1
```

### Bước 3: Test UI

1. Vào **Settings → Facebook Via**
2. Click **"Tải danh sách Fanpage"** trên 1 Via
3. Kiểm tra badge hiển thị:
   - 🟢 **"✓ QTV"** - Màu xanh: Bạn là QTV và app có đủ quyền
   - 🟡 **"⚠ QTV nhưng app chưa đủ quyền"** - Màu vàng: Bạn là QTV nhưng token thiếu quyền
   - 🟡 **"⚠ Không phải QTV"** - Màu vàng: Bạn chưa là QTV
4. Chọn Fanpage và click **"Kết nối Fanpage đã chọn"**
5. Không còn lỗi 400 Bad Request

## 📊 So sánh trước/sau

### Trước khi fix

| Trường hợp | perms | tasks | Backend trả | UI hiển thị |
|------------|-------|-------|-------------|-------------|
| User là QTV, app có MANAGE | `ADMINISTER` | `MANAGE` | `is_admin=false` ❌ | ⚠ Không phải QTV |
| User là QTV, app có CREATE+MODERATE | `ADMINISTER` | `CREATE_CONTENT,MODERATE` | `is_admin=false` ❌ | ⚠ Không phải QTV |
| User không phải QTV | `EDIT_PROFILE` | `ANALYZE` | `is_admin=false` ❌ | ⚠ Không phải QTV |

👉 **Tất cả đều hiển thị "Không phải QTV" dù có là QTV thật**

### Sau khi fix

| Trường hợp | perms | tasks | Backend trả | UI hiển thị |
|------------|-------|-------|-------------|-------------|
| User là QTV, app có MANAGE | `ADMINISTER` | `MANAGE` | `is_admin=true` ✅ | ✓ QTV (xanh) |
| User là QTV, app có CREATE+MODERATE | `ADMINISTER` | `CREATE_CONTENT,MODERATE` | `is_admin=true` ✅ | ✓ QTV (xanh) |
| User là QTV, app thiếu quyền | `ADMINISTER` | `ANALYZE` | `is_admin=false` ⚠️ | ⚠ QTV nhưng app chưa đủ quyền (vàng) |
| User không phải QTV | `EDIT_PROFILE` | `ANALYZE` | `is_admin=false` ❌ | ⚠ Không phải QTV (vàng) |

👉 **Phân biệt rõ 3 trạng thái, user biết cần làm gì**

## 🔧 Troubleshooting

### Vẫn hiển thị "Không phải QTV" sau khi fix

1. Kiểm tra backend logs:
```bash
sudo tail -f /var/log/supervisor/adstudio-stderr.log | grep "PAGE ROLES"
```

2. Nếu thấy `perms=set()` (rỗng):
   - Token Via thiếu scope `pages_show_list`
   - Cần xóa Via và thêm lại với đủ permissions

3. Nếu thấy `perms={'ADMINISTER'}` nhưng `is_admin_for_app=False`:
   - Token thiếu `pages_manage_posts` hoặc `pages_manage_engagement`
   - Cần thêm lại Via với đủ quyền

### Badge vẫn hiển thị sai

1. Clear cache trình duyệt (Ctrl+Shift+R)
2. Kiểm tra frontend đã rebuild:
```bash
ssh root@YOUR_VPS
ls -lh /root/ads-automation/frontend/dist/index.html
# Kiểm tra timestamp file, phải mới nhất
```

### Lỗi 400 vẫn xảy ra

1. Xem log chi tiết:
```bash
sudo tail -f /var/log/supervisor/adstudio-stderr.log | grep "🔵 Connect pages"
```

2. Nếu không thấy log → Backend chưa restart:
```bash
sudo supervisorctl restart adstudio
```

3. Nếu thấy `facebook_account_id=None` → Frontend gửi sai field name
4. Nếu thấy `page_ids=[]` → Frontend không chọn Fanpage nào

## 📝 Commit

```bash
git add app/services/facebook_account_service.py app/schemas/facebook_account.py app/api/routes/channels_settings.py frontend/src/api/facebookChannels.ts frontend/src/components/ConnectFacebookPageModal.tsx
git commit -m "fix: Fix Facebook page admin permission detection and add debug logging"
git push origin main
```

## 📚 Tài liệu tham khảo

- [Facebook Graph API - Page Permissions](https://developers.facebook.com/docs/graph-api/reference/page/)
- [Page Tasks vs Permissions](https://developers.facebook.com/docs/pages/overview/permissions-features)
- User `perms`: ADMINISTER, EDIT_PROFILE, CREATE_CONTENT, MODERATE
- App `tasks`: MANAGE, CREATE_CONTENT, MODERATE, ADVERTISE, ANALYZE

---

**Date:** 2025-12-01  
**Status:** ✅ Completed  
**Files Changed:** 5 files (backend service, schema, API route, frontend API, UI component)
