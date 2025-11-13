# 📥 HƯỚNG DẪN PULL CODE VỀ VPS

## ✅ Đã hoàn thành

1. ✅ Tích hợp Logic 7 Ngày vào website rules_ui_v2 (tab riêng)
2. ✅ Tối ưu `/run-7days` để tự động lấy config từ database
3. ✅ Hỗ trợ args: `/run-7days [account_id] [prefix]`
4. ✅ API CRUD cho Logic 7 Days Config
5. ✅ UI quản lý config trên website

## 🚀 CÁCH PULL CODE VỀ VPS

```bash
# 1. SSH vào VPS
ssh adsuser@your-vps-ip

# 2. Vào thư mục project
cd ~/ads-automation

# 3. Activate virtual environment
source venv/bin/activate

# 4. Stash local changes nếu có (nếu có conflict)
git stash

# 5. Pull code mới
git pull origin main

# 6. Nếu có stash, apply lại (thường không cần)
# git stash pop

# 7. Kiểm tra import
python -c "from app.main import app; print('✅ Import OK')"

# 8. Nếu import OK, restart services
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker:*

# 9. Kiểm tra status
sudo supervisorctl status

# 10. Kiểm tra logs nếu có lỗi
sudo tail -50 /var/log/ads-automation/api.err.log
sudo tail -50 /var/log/ads-automation/worker.err.log
```

## 📋 CÁC TÍNH NĂNG MỚI

### 1. Website Rules Management (`/rules-v2/`)
- **Tab Logic Rules**: Quản lý logic rules như cũ
- **Tab Logic 7 Ngày**: Quản lý config cho logic lọc 7 ngày
  - Tạo/sửa/xóa config theo account + prefix
  - Cấu hình ngưỡng chi tiêu, giá DATA, cost_per_purchase, số ngày
  - Để trống account/prefix = áp dụng cho tất cả

### 2. Command `/run-7days`
- **Không có args**: Chạy cho tất cả accounts/prefixes có config enabled
- **Có account_id**: `/run-7days 2827767517395636` → Chạy cho account đó (tất cả prefixes)
- **Có account_id + prefix**: `/run-7days 2827767517395636 FL` → Chạy cho account + prefix cụ thể

### 3. API Endpoints
- `GET /api/logic-7days-config/` - List configs
- `POST /api/logic-7days-config/` - Tạo config
- `GET /api/logic-7days-config/{id}` - Lấy config theo ID
- `PUT /api/logic-7days-config/{id}` - Cập nhật config
- `DELETE /api/logic-7days-config/{id}` - Xóa config
- `POST /automation/run-7days` - Chạy logic 7 ngày qua API

## 🔧 CẤU HÌNH LOGIC 7 NGÀY

### Các ngưỡng có thể cấu hình:
1. **Ngưỡng chi tiêu** (spend_threshold): Mặc định 100,000₫
2. **Ngưỡng giá DATA** (gia_data_threshold): 0 = dùng từ SL_2_GIA_DATA trong Logic Rules
3. **Ngưỡng giữ lại Cost/Purchase** (cost_per_purchase_keep_threshold): Mặc định 150,000₫
4. **Số ngày lọc** (days): Mặc định 7 ngày

### Logic hoạt động:
- **Điều kiện 1**: `impressions > 0`, `spend > ngưỡng`, `gia_data > ngưỡng`
  - Ngoại lệ: `cost_per_purchase < ngưỡng_giữ_lại` → giữ lại
  - Ngoại lệ: `gia_data >= 2x ngưỡng` → tắt bất kể cost_per_purchase
- **Điều kiện 2**: `impressions > 0`, `spend > ngưỡng`, `results = 0` → tắt

### Xử lý tắt:
- Campaign có nhiều adsets → chỉ tắt adset vi phạm
- Campaign chỉ có 1 adset → tắt campaign

## ⚠️ LƯU Ý

1. **Database Migration**: Bảng `logic_7days_config` sẽ được tạo tự động khi API start
2. **Config Priority**: Tìm config theo thứ tự:
   - account_id + prefix (chính xác nhất)
   - account_id + null (tất cả prefixes)
   - null + prefix (tất cả accounts)
   - null + null (default)
3. **Default Config**: Nếu không có config nào, dùng giá trị mặc định:
   - spend_threshold: 100,000₫
   - gia_data_threshold: 0 (dùng từ Logic Rules)
   - cost_per_purchase_keep_threshold: 150,000₫
   - days: 7

## 🧪 TEST

1. Truy cập website: `http://your-domain/rules-v2/`
2. Chuyển sang tab "🔍 Logic 7 Ngày"
3. Chọn account/prefix từ tree view
4. Tạo config mới
5. Test command: `/run-7days` hoặc `/run-7days account_id prefix`

## 📝 LOGS

Nếu có lỗi, check logs:
```bash
# API logs
sudo tail -f /var/log/ads-automation/api.err.log

# Worker logs
sudo tail -f /var/log/ads-automation/worker.err.log

# Supervisor status
sudo supervisorctl status
```
