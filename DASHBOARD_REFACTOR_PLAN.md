# Dashboard Refactor Plan - Theo Spec

## Tổng quan
Refactor dashboard theo hướng: Nhẹ, mượt, giống Facebook Ads Manager + Madgicx Ads Manager 2.0

## Các thay đổi cần thực hiện

### 1. Header
- [x] Xóa user dropdown menu
- [ ] Thêm nút "← Trang chủ" bên trái (link về /)
- [ ] Chỉ giữ 1 nút "Làm mới" bên phải
- [ ] Tiêu đề: "📊 Dashboard – Tổng Quan Hiệu Suất"
- [ ] Header fixed, scroll chỉ phần nội dung

### 2. Filter Bar
- [x] Đã có sticky filter bar
- [ ] Fix: Lấy account/prefix từ /dashboard/filters (đã có endpoint)
- [ ] Lưu filter state vào localStorage khi thay đổi
- [ ] Restore filter state khi F5/reload
- [ ] Debounce search 300-500ms
- [ ] Fix date logic với timezone Asia/Ho_Chi_Minh
- [ ] Quick buttons: Hôm nay, Hôm qua, 7/14/30 ngày qua, Tháng này/trước

### 3. Layout Sections (Đảo thứ tự)
- [ ] Filter bar + KPI cards (giữ nguyên)
- [ ] **Chi Tiết Quảng Cáo** (move lên trước)
- [ ] **Tổng Quan Theo Prefix** (move xuống sau)
- [ ] **Biểu Đồ Phân Tích** (chỉ 1 section, xóa duplicate)

### 4. Chi Tiết Quảng Cáo
- [ ] Thêm tabs: Campaign / Adset / Ad
- [ ] Multi-select checkboxes
- [ ] Batch actions: Pause/Start/Increase/Decrease budget
- [ ] Cột hiển thị theo view type (Campaign/Adset/Ad)
- [ ] Footer tổng cộng

### 5. Date Logic & Bug Fix
- [ ] Fix timezone: Asia/Ho_Chi_Minh
- [ ] Fix "Hôm nay" không load được data
- [ ] Quick buttons tính đúng date range
- [ ] Lưu date range vào localStorage

### 6. UX Improvements
- [ ] Pagination hoặc infinite scroll
- [ ] Loading states (skeleton)
- [ ] Responsive mobile
- [ ] Smooth animations

## Thứ tự thực hiện
1. Header (xóa user menu, thêm nút Trang chủ)
2. Filter bar (fix data loading, localStorage)
3. Date logic (timezone, quick buttons)
4. Layout (đảo thứ tự sections, xóa duplicate)
5. Chi Tiết Quảng Cáo (tabs, multi-select, batch actions)
6. Bug fix (data hôm nay)
7. UX improvements

