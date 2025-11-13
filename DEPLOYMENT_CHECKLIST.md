# ✅ Deployment Checklist - Birch UI

## 📋 Trước Khi Pull Code Về VPS

### 1. Kiểm Tra Code Local

```bash
# Kiểm tra import
python -c "from app.api.routes import rules_ui_birch; print('✅ Import OK')"

# Kiểm tra main.py
python -c "from app.main import app; print('✅ Main OK')"
```

### 2. Commit và Push Code

```bash
git add .
git commit -m "Add Birch/Madgicx style UI with strategy cards and form builder"
git push origin main
```

## 🚀 Trên VPS

### 1. Pull Code

```bash
cd ~/ads-automation
source venv/bin/activate
git pull origin main
```

### 2. Kiểm Tra Import

```bash
python -c "from app.main import app; print('✅ Import OK')"
```

Nếu có lỗi, kiểm tra:
- `ImportError`: Kiểm tra imports trong `rules_ui_birch.py`
- `SyntaxError`: Kiểm tra f-strings và nested quotes
- `AttributeError`: Kiểm tra model fields

### 3. Restart Services

```bash
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

### 4. Kiểm Tra Logs

```bash
# API logs
sudo tail -50 /var/log/ads-automation/api.err.log

# Worker logs
sudo tail -50 /var/log/ads-automation/worker.err.log
```

### 5. Test Giao Diện

1. Truy cập: `http://your-domain/rules/`
2. Kiểm tra:
   - Trang chủ hiển thị đúng
   - Strategy cards hiển thị
   - Click "Show all strategies" → chuyển trang
   - Click "Create rule" → chuyển trang
   - Click strategy card → chuyển đến detail page
   - Form builder hoạt động (thêm/xóa conditions)
   - Preview hoạt động
   - Lưu rule thành công

## 🐛 Troubleshooting

### Lỗi 1: ImportError

```python
# Kiểm tra imports
from app.api.routes import rules_ui_birch  # OK?
from app.models.logic_rule import LogicRule  # OK?
from app.models.account_prefix import Account, Prefix  # OK?
```

### Lỗi 2: SyntaxError trong f-string

- Đã fix: Tách nested f-strings ra ngoài
- Đã fix: Build operator options trước khi đưa vào f-string

### Lỗi 3: 502 Bad Gateway

- Kiểm tra API có chạy không: `sudo supervisorctl status`
- Kiểm tra port 8000: `sudo lsof -i :8000`
- Kiểm tra nginx config: `sudo nginx -t`

### Lỗi 4: Database Error

- Kiểm tra connection: `psql -U adsuser -d ads_automation -c "SELECT 1;"`
- Kiểm tra tables: `\dt` trong psql

## ✅ Checklist

- [x] Code không có lỗi syntax
- [x] Tất cả imports đúng
- [x] Routes đã được thêm vào main.py
- [x] Form builder hoạt động
- [x] API integration hoàn chỉnh
- [x] Real-time logs streaming
- [x] Mobile responsive
- [x] Style theo Birch/Madgicx

## 📝 Các Routes Mới

1. `GET /rules/` - Trang chủ với strategy cards
2. `GET /rules/all` - Tất cả strategies theo categories
3. `GET /rules/strategy/{strategy_id}` - Chi tiết strategy với form builder
4. `GET /rules/create` - Tạo rule mới

## 🎯 Tính Năng Chính

1. **Strategy Cards**: Hiển thị strategies với icons, badges, metrics, benefits
2. **Form Builder**: Tạo rule với conditions động
3. **Real-time Preview**: Xem rule trước khi lưu
4. **Automation Runner**: Chạy automation với logs real-time
5. **Categories & Filters**: Lọc strategies theo category và campaign type

## 📞 Support

Nếu có vấn đề, kiểm tra:
1. Logs trong `/var/log/ads-automation/`
2. Database connection
3. API endpoints (`/api/rules/`)
4. Browser console (F12) để xem JavaScript errors

