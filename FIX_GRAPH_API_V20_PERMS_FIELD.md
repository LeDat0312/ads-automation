# Fix: Graph API v20.0 không còn hỗ trợ field 'perms'

## Vấn đề

### Log lỗi:
```
GET https://graph.facebook.com/v20.0/me/accounts?fields=id,name,access_token,tasks,perms,category,link,picture{url}
→ 400 Bad Request

❌ Failed to get pages: status=400, code=100, type=OAuthException
message=(#100) Tried accessing nonexisting field (perms) on node type (UserAccountsEdgeData)
```

### Nguyên nhân:
- Graph API v20.0+ đã **loại bỏ field `perms`** khỏi endpoint `/me/accounts`
- Code cũ vẫn request field này → gây lỗi 400
- Verify token OK nhưng không tải được danh sách pages

---

## Giải pháp

### 1. Backend: Bỏ field `perms` khỏi Graph API request

**File:** `app/services/facebook_account_service.py`

#### Trước:
```python
response = await client.get(
    f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me/accounts",
    params={
        "access_token": account.access_token,
        "fields": "id,name,access_token,tasks,perms,category,link,picture{url}",  # ❌ perms
        "limit": 100
    }
)
```

#### Sau:
```python
response = await client.get(
    f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me/accounts",
    params={
        "access_token": account.access_token,
        "fields": "id,name,access_token,tasks,category,link,picture{url}",  # ✅ Bỏ perms
        "limit": 100
    }
)
```

### 2. Backend: Xác định quyền chỉ dựa trên `tasks`

#### Logic mới:

```python
# Get raw tasks (perms no longer available in v20.0+)
raw_tasks = page.get("tasks") or []
tasks = {t.upper() for t in raw_tasks}

# Determine admin status based on tasks only
has_manage_task = "MANAGE" in tasks
has_content_and_moderate = "CREATE_CONTENT" in tasks and "MODERATE" in tasks

# User is considered "admin for automation" if they have:
# - MANAGE (full admin rights), OR
# - CREATE_CONTENT + MODERATE (sufficient for automation)
is_admin_for_app = has_manage_task or has_content_and_moderate

# Determine capabilities
can_publish = "CREATE_CONTENT" in tasks or has_manage_task
can_moderate = "MODERATE" in tasks or has_manage_task
```

#### Các tasks quan trọng:

| Task | Ý nghĩa | Quyền |
|------|---------|-------|
| `MANAGE` | Quản trị viên đầy đủ | Đăng bài + Bình luận + Quản lý |
| `CREATE_CONTENT` | Tạo nội dung | Đăng bài |
| `MODERATE` | Quản lý bình luận | Bình luận + Inbox |
| `ANALYZE` | Xem insights | Chỉ xem |

#### Quyền "đủ để automation":
- ✅ `MANAGE` → Đủ quyền
- ✅ `CREATE_CONTENT` + `MODERATE` → Đủ quyền
- ⚠️ Chỉ `CREATE_CONTENT` → Chỉ đăng bài
- ⚠️ Chỉ `MODERATE` → Chỉ bình luận
- ❌ Không có gì → Không đủ quyền

### 3. Backend: Response schema

```python
{
    "id": "123456789",
    "name": "Fanpage Name",
    "picture_url": "https://...",
    "category": "Local Business",
    "access_token": "EAAxxxxx",
    "tasks": ["MANAGE", "CREATE_CONTENT", "MODERATE"],  # ✅ Có data
    "perms": [],  # ✅ Luôn rỗng, giữ lại để backward compatibility
    "is_admin": true,  # ✅ Dựa trên tasks
    "can_publish": true,
    "can_moderate": true,
    "warning_message": null
}
```

### 4. Frontend: Hiển thị badge quyền

#### Badge mới:

| Điều kiện | Badge | Màu | Tooltip |
|-----------|-------|-----|---------|
| `is_admin = true` | ✓ Đủ quyền | Xanh lá | Via có quyền MANAGE hoặc (CREATE_CONTENT + MODERATE) |
| `can_publish && can_moderate` | ✓ Có quyền cơ bản | Xanh dương | Via có quyền đăng bài và quản lý bình luận |
| `can_publish only` | ⚠ Chỉ đăng bài | Vàng | Via có quyền đăng bài nhưng chưa có quyền bình luận |
| `can_moderate only` | ⚠ Chỉ bình luận | Vàng | Via có quyền bình luận nhưng chưa có quyền đăng bài |
| Không có gì | ✗ Không đủ quyền | Đỏ | Via chưa có quyền quản lý Fanpage |

---

## Testing

### 1. Test với token có quyền đầy đủ

```bash
# Request
GET /api/facebook-accounts/1/pages

# Response
[
  {
    "id": "123456789",
    "name": "My Fanpage",
    "tasks": ["MANAGE", "CREATE_CONTENT", "MODERATE"],
    "perms": [],
    "is_admin": true,
    "can_publish": true,
    "can_moderate": true,
    "warning_message": null
  }
]
```

**UI hiển thị:**
- Badge: ✓ Đủ quyền (màu xanh lá)
- Có thể kết nối và sử dụng đầy đủ tính năng

### 2. Test với token chỉ có CREATE_CONTENT

```bash
# Response
[
  {
    "id": "123456789",
    "name": "My Fanpage",
    "tasks": ["CREATE_CONTENT"],
    "perms": [],
    "is_admin": false,
    "can_publish": true,
    "can_moderate": false,
    "warning_message": "Via có quyền đăng bài nhưng chưa có quyền quản lý bình luận..."
  }
]
```

**UI hiển thị:**
- Badge: ⚠ Chỉ đăng bài (màu vàng)
- Tooltip: Via có quyền đăng bài nhưng chưa có quyền quản lý bình luận

### 3. Test với token không có quyền

```bash
# Response
[
  {
    "id": "123456789",
    "name": "My Fanpage",
    "tasks": [],
    "perms": [],
    "is_admin": false,
    "can_publish": false,
    "can_moderate": false,
    "warning_message": "Via này không có quyền quản lý Fanpage..."
  }
]
```

**UI hiển thị:**
- Badge: ✗ Không đủ quyền (màu đỏ)
- Tooltip: Via chưa có quyền quản lý Fanpage này

---

## Deploy

### Script tự động:

```bash
cd /home/adsuser/ads-automation && \
git pull origin main && \
cd frontend && npm run build && cd .. && \
sudo systemctl restart ads-automation && \
sudo systemctl restart nginx && \
echo "✅ Deploy hoàn tất!"
```

### Kiểm tra sau deploy:

1. **Vào Settings → Facebook Via**
2. **Chọn Via → Bấm "Tải danh sách Fanpage"**
3. **Kiểm tra:**
   - ✅ Không còn lỗi 400 với message "perms"
   - ✅ List pages hiển thị với badge quyền
   - ✅ Badge phản ánh đúng quyền của Via

### Xem logs:

```bash
# Backend logs
sudo journalctl -u ads-automation -f | grep "PAGE ROLES"

# Ví dụ output:
# PAGE ROLES: id=123456789 name=My Fanpage tasks=['MANAGE', 'CREATE_CONTENT', 'MODERATE'] 
# is_admin_for_app=True can_publish=True can_moderate=True
```

---

## So sánh trước/sau

### Trước fix:

```
❌ GET /me/accounts?fields=...perms...
→ 400 Bad Request
→ (#100) Tried accessing nonexisting field (perms)
→ User không tải được danh sách pages
```

### Sau fix:

```
✅ GET /me/accounts?fields=...tasks... (không có perms)
→ 200 OK
→ Parse tasks để xác định quyền
→ User thấy list pages với badge quyền rõ ràng
```

---

## Backward Compatibility

### Field `perms` trong response:

- ✅ Vẫn giữ lại field `perms` trong schema
- ✅ Luôn trả về `[]` (mảng rỗng)
- ✅ Frontend cũ vẫn hoạt động (không crash)
- ✅ Logic mới chỉ dùng `tasks`

### Lý do:

- Tránh breaking change với frontend cũ
- Dễ rollback nếu cần
- Có thể migrate dần dần

---

## Notes

### Graph API Version:

- **v19.0 trở xuống**: Có field `perms`
- **v20.0 trở lên**: Không có field `perms`
- **Giải pháp**: Chỉ dùng `tasks` (có ở tất cả versions)

### Tasks vs Perms:

- **perms**: User-level permissions (ADMINISTER, EDIT_PROFILE, etc.)
- **tasks**: App-level permissions (MANAGE, CREATE_CONTENT, MODERATE, etc.)
- **v20.0+**: Chỉ có `tasks`, đủ để xác định quyền automation

### Warning messages:

Tất cả warning messages đều bằng tiếng Việt, giải thích rõ ràng:
- Via cần quyền gì
- Tại sao cần quyền đó
- Làm thế nào để có quyền

---

## Commit

```bash
git add app/services/facebook_account_service.py
git add frontend/src/components/ConnectFacebookPageModal.tsx
git add FIX_GRAPH_API_V20_PERMS_FIELD.md
git commit -m "Fix: Bỏ field 'perms' khỏi Graph API v20.0+ request

- Graph API v20.0+ không còn hỗ trợ field 'perms' trong /me/accounts
- Sửa request: Bỏ 'perms', chỉ dùng 'tasks'
- Logic quyền mới: Dựa trên tasks (MANAGE, CREATE_CONTENT, MODERATE)
- is_admin = MANAGE hoặc (CREATE_CONTENT + MODERATE)
- Frontend: Badge quyền chi tiết hơn (Đủ quyền, Chỉ đăng bài, Chỉ bình luận, Không đủ quyền)
- Backward compatible: Field 'perms' vẫn có trong response (luôn rỗng)

Fix lỗi: (#100) Tried accessing nonexisting field (perms) on node type (UserAccountsEdgeData)"
git push origin main
```

---

## Kết quả

✅ **Không còn lỗi 400 với message "perms"**
✅ **Tải được danh sách pages thành công**
✅ **Badge quyền hiển thị chính xác**
✅ **Warning messages tiếng Việt rõ ràng**
✅ **Backward compatible với code cũ**
