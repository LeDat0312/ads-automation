# Hướng Dẫn Kiểm Tra Lỗi Website

## 1. Kiểm Tra Lỗi Trong Browser (Khuyến nghị)

### Bước 1: Mở Developer Console
- **Chrome/Edge**: Nhấn `F12` hoặc `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
- **Firefox**: Nhấn `F12` hoặc `Ctrl+Shift+K` (Windows) / `Cmd+Option+K` (Mac)

### Bước 2: Kiểm Tra Console Tab
1. Vào tab **Console**
2. Reload trang `/settings` (F5)
3. Xem các thông báo:
   - 🔴 **Đỏ**: Lỗi JavaScript
   - 🟡 **Vàng**: Cảnh báo
   - 🔵 **Xanh**: Thông tin

**Các lỗi thường gặp:**
- `Uncaught TypeError: Cannot read property '...' of null` → Element không tồn tại
- `Failed to fetch` → API request bị lỗi
- `SyntaxError` → Lỗi cú pháp JavaScript

### Bước 3: Kiểm Tra Network Tab
1. Vào tab **Network**
2. Reload trang (F5)
3. Tìm các requests:
   - `/settings/token/status`
   - `/settings/accounts`
   - `/settings/prefixes`
4. Click vào từng request để xem:
   - **Status**: 200 (OK), 401 (Unauthorized), 500 (Server Error), etc.
   - **Response**: Xem nội dung response
   - **Headers**: Xem headers được gửi

**Các status code thường gặp:**
- `200`: OK
- `401`: Chưa đăng nhập hoặc token hết hạn
- `403`: Không có quyền truy cập
- `500`: Lỗi server

### Bước 4: Kiểm Tra Application Tab (Chrome)
1. Vào tab **Application**
2. Xem **Cookies** → `https://updatemetaads.site`
3. Kiểm tra có cookie `access_token` không
4. Xem **Local Storage** → `https://updatemetaads.site`
5. Kiểm tra có `access_token` trong localStorage không

## 2. Kiểm Tra Lỗi Trên VPS

### Kiểm tra logs của API service:
```bash
cd ~/ads-automation
sudo supervisorctl tail -100 ads-automation-api
```

### Kiểm tra logs của nginx:
```bash
sudo tail -50 /var/log/nginx/error.log
```

### Kiểm tra Python syntax:
```bash
cd ~/ads-automation
source venv/bin/activate
python -m py_compile app/api/routes/settings.py
```

### Kiểm tra import:
```bash
python -c "from app.api.routes.settings import router"
```

## 3. Test API Endpoints Trực Tiếp

### Sử dụng curl (trên VPS):
```bash
# Lấy token từ cookie hoặc localStorage
TOKEN="your_access_token_here"

# Test token status endpoint
curl -H "Authorization: Bearer $TOKEN" \
     -H "Cookie: access_token=$TOKEN" \
     https://updatemetaads.site/settings/token/status

# Test accounts endpoint
curl -H "Authorization: Bearer $TOKEN" \
     -H "Cookie: access_token=$TOKEN" \
     https://updatemetaads.site/settings/accounts

# Test prefixes endpoint
curl -H "Authorization: Bearer $TOKEN" \
     -H "Cookie: access_token=$TOKEN" \
     https://updatemetaads.site/settings/prefixes
```

### Sử dụng Python script:
```bash
cd ~/ads-automation
source venv/bin/activate
python scripts/check_settings_endpoints.py
```

## 4. Các Lỗi Thường Gặp và Cách Sửa

### Lỗi: "Đang kiểm tra trạng thái token..." mãi không đổi
**Nguyên nhân:**
- API endpoint `/settings/token/status` trả về lỗi
- JavaScript không xử lý được response
- Element `tokenStatus` không tồn tại

**Cách kiểm tra:**
1. Mở Console, xem có lỗi JavaScript không
2. Vào Network tab, xem request `/settings/token/status` có thành công không
3. Xem Response của request đó

### Lỗi: "Đang tải..." mãi không đổi
**Nguyên nhân:**
- API endpoint `/settings/accounts` hoặc `/settings/prefixes` trả về lỗi
- JavaScript không cập nhật được DOM

**Cách kiểm tra:**
1. Mở Console, xem có lỗi JavaScript không
2. Vào Network tab, xem các requests có thành công không
3. Xem Response của các requests

### Lỗi: 401 Unauthorized
**Nguyên nhân:**
- Chưa đăng nhập
- Token hết hạn
- Cookie không được gửi kèm request

**Cách sửa:**
1. Đăng nhập lại
2. Kiểm tra cookie `access_token` có tồn tại không
3. Kiểm tra localStorage có `access_token` không

### Lỗi: 500 Internal Server Error
**Nguyên nhân:**
- Lỗi trong code Python
- Database connection error
- Missing dependencies

**Cách kiểm tra:**
```bash
sudo supervisorctl tail -100 ads-automation-api
```

## 5. Debug JavaScript Trực Tiếp

Mở Console và chạy các lệnh sau:

```javascript
// Kiểm tra token
localStorage.getItem('access_token')
document.cookie

// Kiểm tra elements
document.getElementById('tokenStatus')
document.getElementById('accountsTable')
document.getElementById('prefixesTable')

// Test load functions
loadTokenStatus()
loadAccounts()
loadPrefixes()

// Kiểm tra getAuthHeaders
getAuthHeaders()
```

## 6. Gửi Thông Tin Lỗi

Khi báo lỗi, vui lòng cung cấp:
1. **Screenshot của Console tab** (F12 → Console)
2. **Screenshot của Network tab** (F12 → Network, sau đó click vào request bị lỗi)
3. **Status code** của các requests
4. **Response** của các requests (nếu có)
5. **Logs từ VPS** (nếu có)

