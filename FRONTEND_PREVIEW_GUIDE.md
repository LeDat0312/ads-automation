# 🎨 HƯỚNG DẪN XEM TRƯỚC FRONTEND (KHÔNG CẦN BACKEND)

## ✅ CÁCH 1: SỬ DỤNG MOCK DATA (KHUYẾN NGHỊ)

Frontend đã được tích hợp sẵn mock data để bạn test mà không cần backend!

### Bước 1: Bật Mock Mode

Mở file `frontend/src/services/api.ts` và thay đổi:

```typescript
// Dòng 11
const USE_MOCK_DATA = true; // ✅ Đổi từ false → true
```

### Bước 2: Chạy Frontend

```bash
cd frontend
npm install
npm run dev
```

### Bước 3: Mở Browser

Truy cập: **http://localhost:3000/dashboard/**

### ✨ Bạn sẽ thấy:

**Lead Generation View:**
- 📊 Tổng chi tiêu: 15,000,000 VND
- 💬 Tổng DATA: 850
- 📈 Giá DATA TB: 17,647 VND
- 🛒 Tổng Lead: 120
- 📋 3 adsets mẫu với đầy đủ metrics

**E-Commerce View:**
- 💰 Tổng chi tiêu: 25,000,000 VND
- 💵 Giá trị chuyển đổi: 150,000,000 VND
- 📈 % ADS: 16.67%
- 📋 3 adsets mẫu với metrics khác

### 🎯 Test Features:

✅ **Switch View Mode**
- Click "Lead Generation" / "E-Commerce"
- Cards và columns sẽ thay đổi

✅ **Status Chips**
- Click "Tất cả", "Đã chạy hôm nay", "Đang hoạt động", "Tạm dừng"
- Dữ liệu sẽ filter (client-side)

✅ **Date Picker**
- Click date picker
- Chọn preset hoặc custom range
- UI sẽ update (data mock không thay đổi)

✅ **Table Interactions**
- Sort columns (click header)
- Select rows (checkbox)
- Click budget → Opens BudgetEditor
- Toggle status (Lead: switch, Ecom: chip)

✅ **Bulk Actions**
- Select multiple rows
- Click "Điều chỉnh ngân sách" → Opens BudgetModal
- Try percent mode (-20%, +20%, etc.)
- Try manual mode
- Preview changes
- Click "Áp dụng" (console log only, no API call)

✅ **Pagination**
- Change page size (10, 25, 50, 100, 200)
- Mock data chỉ có 3 rows nên sẽ show page 1/1

✅ **Drill-down**
- Click campaign name → Navigate to campaign drill-down
- Breadcrumb shows path
- Click "← Quay lại" to go back

### 📝 Mock Data Details:

**File:** `frontend/src/services/mockData.ts`

**Bạn có thể:**
- Thêm/sửa mock adsets
- Thay đổi summary metrics
- Customize data theo ý muốn

**Example - Thêm adset mới:**
```typescript
{
  id: 'adset_4',
  adset_id: '123456792',
  adset_name: 'Your Custom Adset Name',
  campaign_id: 'campaign_003',
  campaign_name: 'Your Campaign',
  // ... các fields khác
}
```

### ⚠️ Lưu ý:

Khi `USE_MOCK_DATA = true`:
- ✅ Tất cả API calls sẽ return mock data
- ✅ Không cần backend server
- ✅ Không có network requests thật
- ⚠️ Bulk actions (budget update, status update) chỉ log ra console
- ⚠️ Không lưu được thay đổi (refresh là mất)

---

## 🚀 CÁCH 2: CHẠY VỚI BACKEND THẬT

### Bước 1: Đảm bảo Backend đang chạy

```bash
# Terminal 1 - Backend
cd "c:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Kiểm tra: http://localhost:8000/docs

### Bước 2: Tắt Mock Mode

```typescript
// frontend/src/services/api.ts - Dòng 11
const USE_MOCK_DATA = false; // ✅ Đảm bảo = false
```

### Bước 3: Cấu hình .env

```bash
cd frontend
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000
```

### Bước 4: Chạy Frontend

```bash
# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### Bước 5: Mở Browser

**http://localhost:3000/dashboard/**

### ✨ Bạn sẽ thấy:

- Dữ liệu THẬT từ Facebook API
- Tất cả actions (budget update, status toggle) sẽ gọi API thật
- Thay đổi được lưu vào database

### ⚠️ Lưu ý:

- ❗ Backend cần có token Facebook hợp lệ
- ❗ Cần có accounts được config trong Settings
- ❗ API endpoint `/dashboard/data` phải trả đúng format

**Nếu gặp lỗi:**
```
Error: Facebook access token not found
```

→ Vào Settings, config Facebook token trước!

---

## 🔍 SO SÁNH 2 CÁCH

| Feature | Mock Data | Backend Thật |
|---------|-----------|--------------|
| **Cần backend** | ❌ Không | ✅ Cần |
| **Dữ liệu** | 3 adsets mẫu | Dữ liệu thật từ FB |
| **Tốc độ** | ⚡ Nhanh | 🐢 Phụ thuộc API |
| **Bulk actions** | ❌ Chỉ UI | ✅ Thực thi thật |
| **Phù hợp cho** | UI/UX testing | Integration testing |
| **Chỉnh sửa data** | ✅ Dễ (edit mockData.ts) | ❌ Qua backend |

---

## 🎯 KHUYẾN NGHỊ

### Để xem trước UI/UX:
→ **Dùng Mock Data** (Cách 1)
- Nhanh, đơn giản
- Không cần config backend
- Tập trung vào UI/UX

### Để test tích hợp:
→ **Dùng Backend Thật** (Cách 2)
- Test API integration
- Verify data flow
- Test error handling

---

## 📸 Screenshots Expected

### Lead Generation View:
```
┌─────────────────────────────────────────┐
│ 📋 Lead Generation  🛒 E-Commerce     │
├─────────────────────────────────────────┤
│ [Campaign] [Adset] [Ad]                │
├─────────────────────────────────────────┤
│ 📊 Tất cả  🔥 Đã chạy  ✅ Hoạt động   │
├─────────────────────────────────────────┤
│ [📅 Date Picker] [🔍 Filters] [🔄]    │
├─────────────────────────────────────────┤
│                                         │
│  💰 Tổng Chi Tiêu    💬 Tổng DATA     │
│     15,000,000          850            │
│                                         │
│  📊 Giá DATA TB      🛒 Tổng Lead     │
│     17,647              120            │
├─────────────────────────────────────────┤
│  ✅ 45  ⏸️ 23  📊 68                   │
├─────────────────────────────────────────┤
│ [TABLE WITH 3 ADSETS]                  │
│ ☑️ Status | Name | Budget | Spend ... │
└─────────────────────────────────────────┘
```

### E-Commerce View:
```
┌─────────────────────────────────────────┐
│ 📋 Lead Generation  🛒 E-Commerce     │ ← Active
├─────────────────────────────────────────┤
│  💰 Tổng Chi Tiêu    💵 Giá trị CV    │
│     25,000,000        150,000,000      │
│                                         │
│  📈 % ADS                              │
│     16.67%                             │
├─────────────────────────────────────────┤
│  ✅ 38  ⏸️ 17  📊 55                   │
├─────────────────────────────────────────┤
│ [TABLE WITH 3 ECOM ADSETS]             │
│ ☑️ Chip | Name | Budget | % ADS ...   │
└─────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Mock data không hiển thị:
- Kiểm tra `USE_MOCK_DATA = true` trong `api.ts`
- Check console for errors
- Verify `mockData.ts` file exists

### Backend connection lỗi:
- Verify backend đang chạy: `curl http://localhost:8000/dashboard/health`
- Check `.env`: `VITE_API_URL=http://localhost:8000`
- Check CORS settings

### Không thấy dữ liệu:
- Mở DevTools (F12) → Console
- Check Network tab
- Xem error messages

---

## ✅ Kết luận

**KHUYẾN NGHỊ: Dùng Mock Data để xem trước!**

```bash
# 1 lệnh duy nhất:
cd frontend
npm install

# Edit api.ts: USE_MOCK_DATA = true

npm run dev

# Mở: http://localhost:3000/dashboard/
```

**Xong! Enjoy testing! 🎉**
