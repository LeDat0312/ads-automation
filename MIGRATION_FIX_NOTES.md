# 🔧 Migration Script Fix Notes

## Vấn đề gặp phải

Migration script bị lỗi: `'NoneType' object has no attribute 'connect'`

**Nguyên nhân:** 
- `engine` trong `app.core.database` được khởi tạo là `None` ban đầu
- Chỉ được khởi tạo khi gọi `init_db()`
- Migration script import `engine` trực tiếp nhưng chưa gọi `init_db()`

## Giải pháp

1. **Sửa migration script** để gọi `init_db()` trước khi sử dụng `engine`
2. **Sửa competitor_research.py** để thêm `db` dependency

## Cách chạy migration sau khi fix

```bash
cd ~/ads-automation
source venv/bin/activate
export PYTHONPATH=/home/adsuser/ads-automation:$PYTHONPATH
python migrations/add_scrapegraphai_api_key.py
```

## Về React cho Competitor Research

**Câu hỏi:** Có cần dùng React + Vite cho trang Competitor Research không?

**Trả lời:**
- **Hiện tại:** Trang đang dùng HTML thuần, đơn giản và đủ dùng
- **Nếu muốn nhất quán:** Có thể chuyển sang React để giống với Dashboard
- **Khuyến nghị:** 
  - Nếu trang này chỉ có form đơn giản → **Giữ HTML thuần** (nhẹ, nhanh)
  - Nếu cần nhiều tính năng phức tạp (filter, table, real-time updates) → **Chuyển sang React**

**Kết luận:** HTML thuần hiện tại là đủ, không cần thiết phải chuyển sang React trừ khi cần thêm nhiều tính năng phức tạp.

