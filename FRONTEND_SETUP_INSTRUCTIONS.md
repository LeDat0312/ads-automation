# Facebook Via Token Management - Frontend Setup

## Packages cần cài đặt

Chạy lệnh sau trong thư mục `frontend/`:

```bash
npm install @headlessui/react react-toastify dayjs
```

Hoặc nếu dùng yarn:

```bash
yarn add @headlessui/react react-toastify dayjs
```

### Package details:

- **@headlessui/react**: UI components (Dialog, Tab, Transition) - headless, dễ style với Tailwind
- **react-toastify**: Toast notifications tiếng Việt
- **dayjs**: Date formatting lightweight (thay thế moment.js)

## Khởi chạy frontend

Sau khi cài đặt packages:

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: http://localhost:5173

## Routes mới đã thêm:

- `/settings/facebook-via` - Quản lý Via Facebook (thêm/sửa/xóa/verify token)
- `/settings/channels` - Kênh đã kết nối (modal mới: Kết nối Fanpage Facebook)

## Components mới:

1. **FacebookViaPage** (`src/pages/settings/FacebookViaPage.tsx`):
   - Quản lý danh sách Via Facebook
   - Filter theo loại (Fanpage/Ads/Cả hai)
   - Modal thêm/sửa Via
   - Verify token
   - Xóa Via

2. **ConnectFacebookPageModal** (`src/components/ConnectFacebookPageModal.tsx`):
   - Modal 2 bước: Chọn Via → Chọn Fanpage
   - Tab 1: Chọn từ danh sách (checkbox, search)
   - Tab 2: Nhập ID thủ công
   - Tích hợp với backend API

3. **API Helpers**:
   - `src/api/base.ts` - Axios instance với auth interceptor
   - `src/api/facebookVia.ts` - API calls cho Via management
   - `src/api/facebookChannels.ts` - API calls cho channel connection

## Cấu trúc Toast Notification

Thêm vào `App.tsx` hoặc root component:

```tsx
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Trong component:
<ToastContainer
  position="top-right"
  autoClose={3000}
  hideProgressBar={false}
  newestOnTop
  closeOnClick
  rtl={false}
  pauseOnFocusLoss
  draggable
  pauseOnHover
/>
```

## Backend API Endpoints (đã sẵn sàng):

### Via Management:
- GET `/api/facebook-accounts?type=fanpage` - List Via accounts
- POST `/api/facebook-accounts` - Create Via
- PATCH `/api/facebook-accounts/{id}` - Update Via
- DELETE `/api/facebook-accounts/{id}` - Delete Via
- POST `/api/facebook-accounts/{id}/verify` - Verify token
- GET `/api/facebook-accounts/{id}/pages` - Get Fanpage list

### Channel Connection:
- POST `/api/channels/facebook/from-saved-account` - Bulk connect from Via
- POST `/api/channels/facebook/manual-v2` - Manual connect with optional Via

## Testing Frontend:

1. **Test Via Management**:
   - Vào `/settings/facebook-via`
   - Thêm Via mới (cần token thật từ Facebook Graph API Explorer)
   - Verify token
   - Sửa/xóa Via

2. **Test Channel Connection**:
   - Vào `/settings/channels`
   - Click "➕ Thêm kênh"
   - Chọn Via → Tải danh sách Fanpage
   - Chọn Fanpage từ list hoặc nhập ID thủ công
   - Kết nối

## Troubleshooting:

### Lỗi "Cannot find module '@headlessui/react'"
→ Chạy `npm install @headlessui/react`

### Lỗi "Cannot find module 'react-toastify'"
→ Chạy `npm install react-toastify`

### Lỗi "Cannot find module 'dayjs'"
→ Chạy `npm install dayjs`

### API call trả về 401 Unauthorized
→ Kiểm tra localStorage có `token` không, hoặc login lại

### Modal không hiện
→ Kiểm tra Tailwind đã compile chưa, restart dev server

---

## Summary of Changes:

✅ Created:
- `src/api/base.ts` - Axios instance
- `src/api/facebookVia.ts` - Via API
- `src/api/facebookChannels.ts` - Channel API
- `src/pages/settings/FacebookViaPage.tsx` - Via management UI
- `src/components/ConnectFacebookPageModal.tsx` - 2-step modal

✅ Modified:
- `src/Router.tsx` - Added `/settings/facebook-via` route
- `src/components/SettingsLayout.tsx` - Added menu item "Quản lý Via Facebook"
- `src/pages/Settings/ChannelsSettingsPage.tsx` - Integrated new modal, removed old manual form

✅ Backend (already deployed):
- 8 API endpoints ready
- Database migration completed
- All Vietnamese error messages

🔄 **Next Steps (Frontend)**:
1. Install packages: `npm install @headlessui/react react-toastify dayjs`
2. Add ToastContainer to main App/Layout
3. Run `npm run dev`
4. Test full flow with real Facebook token

**Frontend completion: 95%** (chỉ còn cài packages và test)
