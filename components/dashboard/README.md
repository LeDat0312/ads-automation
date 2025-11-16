# Dashboard Components

Các component React/TypeScript cho Dashboard với style Soft UI (gradient tím hồng) và UX giống Madgicx/Ads Manager 2.0.

## Components

### 1. AdsControlsBar
Thanh điều khiển chính phía trên bảng Ads, bao gồm:
- Nút Filters với badge số lượng filter đang active
- Ô Search
- Dropdown Load filter preset
- Nút Refresh
- Date Range Picker
- View Dropdown
- Nút Settings

### 2. FilterDrawer
Panel filter mở ra từ dưới thanh controls, hiển thị:
- Search bar và preset dropdown (giống controls bar)
- Suggestions grid với các filter gợi ý
- Active filters display
- Buttons Close và Apply

### 3. FilterPresetDropdown
Dropdown để chọn preset filter:
- Only Acquisition
- Only Retargeting & Retention
- Active Ad Sets

### 4. DateRangePickerPopover
Popover hiển thị 2 calendar và quick ranges:
- 2 calendar cạnh nhau (tháng hiện tại và tháng sau)
- Quick ranges: Hôm nay, Hôm qua, 3/7/14/30 ngày qua
- Date inputs với timezone info
- Buttons Cancel và Update

## Installation

Cần cài đặt các dependencies:

```bash
npm install lucide-react date-fns
```

## Usage

Xem file `DashboardOverview.tsx` để biết cách sử dụng các components.

## Styling

Tất cả components sử dụng Tailwind CSS với:
- Background gradient: `bg-gradient-to-br from-purple-50 via-pink-50 to-purple-100`
- Cards: `bg-white rounded-2xl shadow-sm border border-slate-200`
- Buttons: Soft UI style với `rounded-xl`, `border`, hover effects
- Colors: Purple/Pink gradient cho primary actions

## TypeScript Types

Tất cả components đều có type definitions đầy đủ trong file.

