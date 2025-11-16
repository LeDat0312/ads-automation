# 🎨 DASHBOARD OVERVIEW - HƯỚNG DẪN

## 📋 TỔNG QUAN

Dashboard Automation Overview cho phép xem và filter dữ liệu quảng cáo Facebook tương tự Madgicx.

## 🚀 TRUY CẬP DASHBOARD

### **URL:**
```
http://localhost:8000/api/dashboard/
```

Hoặc nếu deploy trên VPS:
```
http://your-domain.com/api/dashboard/
```

## 🎯 TÍNH NĂNG

### **1. Filters (Bộ lọc):**
- ✅ **Account ID:** Lọc theo account
- ✅ **Prefix:** Lọc theo prefix (PX, TL, FL, NM, etc.)
- ✅ **Status:** Lọc theo trạng thái (Active, Paused)
- ✅ **Date Range:** Lọc theo khoảng thời gian
- ✅ **Apply Filters:** Áp dụng bộ lọc
- ✅ **Export CSV:** Xuất dữ liệu ra file CSV

### **2. Statistics (Thống kê):**
- ✅ **Total Spend:** Tổng chi tiêu
- ✅ **Total Results:** Tổng kết quả
- ✅ **Avg Giá DATA:** Giá DATA trung bình
- ✅ **Active Adsets:** Số adsets đang active
- ✅ **Paused Adsets:** Số adsets đã paused
- ✅ **Total Ads:** Tổng số ads

### **3. Ads Performance Table:**
- ✅ Hiển thị danh sách ads với các metrics:
  - Adset ID
  - Adset Name
  - Campaign Name
  - Prefix
  - Status
  - Spend
  - Results
  - Giá DATA
  - Impressions
  - Clicks
  - CTR
  - CPC

### **4. Pagination:**
- ✅ Phân trang dữ liệu (50 ads/page)
- ✅ Điều hướng giữa các trang

### **5. Export:**
- ✅ Xuất dữ liệu ra CSV
- ✅ Áp dụng filters khi export

## 📊 SO SÁNH VỚI MADGICX

### **✅ CÓ THỂ LÀM:**
- ✅ Xem tổng quan performance
- ✅ Filter theo account, prefix, status, date
- ✅ Xem chi tiết từng ad
- ✅ Export dữ liệu ra CSV
- ✅ Real-time stats
- ✅ Pagination

### **⏸️ CHƯA CÓ (CÓ THỂ THÊM SAU):**
- ⏸️ Charts/Graphs (biểu đồ)
- ⏸️ Real-time updates (WebSocket)
- ⏸️ Advanced filters (nhiều điều kiện)
- ⏸️ Custom date ranges (presets)
- ⏸️ Compare periods
- ⏸️ Alerts/Notifications
- ⏸️ User management
- ⏸️ Multiple views (campaign, adset, ad level)

## 🔧 CẤU TRÚC

### **Backend API:**
- `GET /api/dashboard/` - Serve HTML page
- `GET /api/dashboard/stats` - Get statistics
- `GET /api/dashboard/ads` - Get ads data (with pagination)
- `GET /api/dashboard/filters` - Get filter options
- `GET /api/dashboard/export` - Export to CSV

### **Frontend:**
- HTML/CSS/JavaScript (single page)
- No framework needed (vanilla JS)
- Responsive design
- Modern UI

## 🚀 DEPLOYMENT

### **1. Chạy ứng dụng:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **2. Truy cập dashboard:**
```
http://localhost:8000/api/dashboard/
```

### **3. Với Nginx (production):**
```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 📝 NOTES

### **Dữ liệu:**
- Dữ liệu được lấy từ PostgreSQL database
- Cần chạy `pull_facebook_data()` trước để có dữ liệu
- Dữ liệu được cập nhật mỗi khi chạy automation

### **Performance:**
- Pagination để tránh load quá nhiều dữ liệu
- Index trên các cột thường dùng để filter
- Có thể cache stats nếu cần

### **Security:**
- Trong production nên thêm authentication
- Giới hạn CORS origins
- Rate limiting cho API

## 🔄 MỞ RỘNG

### **Có thể thêm:**
1. **Charts:** Dùng Chart.js hoặc D3.js
2. **Real-time:** WebSocket hoặc Server-Sent Events
3. **Advanced Filters:** Nhiều điều kiện phức tạp hơn
4. **Export Formats:** Excel, PDF
5. **Scheduled Reports:** Tự động gửi báo cáo
6. **Alerts:** Cảnh báo khi có vấn đề
7. **User Management:** Nhiều user, phân quyền
8. **Custom Views:** Tùy chỉnh hiển thị

---

**Chúc bạn sử dụng dashboard thành công! 🚀**

