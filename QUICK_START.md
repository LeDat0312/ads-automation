# 🚀 AdStudio Quick Start Guide

## TL;DR - Chạy ngay trong 3 bước

### Bước 1: Migration
```bash
python -m migrations.add_ad_studio_tables
```

### Bước 2: Cấu hình Apify Key
```bash
# Thêm vào .env
echo "APIFY_DEFAULT_KEY=your_apify_api_key" >> .env
```

### Bước 3: Test API
```bash
# Start server
uvicorn app.main:app --reload

# Test endpoint (tab khác)
curl -X POST http://localhost:8000/api/tiktok/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@username/video/1234567890"}'
```

---

## 📋 Checklist đầy đủ

- [ ] Đã có Python virtual environment activated
- [ ] Đã cài dependencies: `pip install sqlalchemy fastapi pydantic requests`
- [ ] Đã có DATABASE_URL trong .env
- [ ] Đã chạy migration: `python -m migrations.add_ad_studio_tables`
- [ ] Đã cấu hình Apify API key (qua /settings hoặc .env)
- [ ] Server đang chạy: `uvicorn app.main:app --reload`
- [ ] Frontend đã có component `AdStudioCard.tsx`

---

## 🧪 Test nhanh

### Test 1: Verify endpoints
```bash
curl http://localhost:8000/docs
# Mở browser → tìm /api/tiktok/scrape, /api/posts/schedule
```

### Test 2: Scrape TikTok video
```bash
curl -X POST http://localhost:8000/api/tiktok/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@beautysalon/video/7123456789",
    "note": "Video test"
  }'
```

**Expected response:**
```json
{
  "id": "uuid-here",
  "platform": "tiktok",
  "videoUrl": "https://...",
  "thumbnailUrl": "https://...",
  "captionOriginal": "Caption từ TikTok..."
}
```

### Test 3: Schedule post
```bash
curl -X POST http://localhost:8000/api/posts/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "Khuyến mãi lớn!",
    "language": "la",
    "ctaText": "Nhắn tin ngay",
    "pageIds": ["123456789"],
    "scheduleMode": "NOW",
    "thumbnailSource": "FRAME"
  }'
```

**Expected response:**
```json
{
  "ok": true,
  "id": "uuid-here",
  "message": "Đã lưu lịch đăng bài thành công..."
}
```

---

## ⚠️ Troubleshooting

### ❌ "Apify API key chưa được cấu hình"

**Giải pháp:**
```bash
# Option 1: Thêm vào .env
echo "APIFY_DEFAULT_KEY=apify_api_xxxxxxxxxxxxx" >> .env

# Option 2: Vào /settings trên web UI
# Admin → Settings → Apify API Key → Save
```

### ❌ "No module named 'sqlalchemy'"

**Giải pháp:**
```bash
# Activate venv
venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install sqlalchemy fastapi pydantic requests
```

### ❌ "Table ad_studio_assets does not exist"

**Giải pháp:**
```bash
python -m migrations.add_ad_studio_tables
```

---

## 📱 Frontend Integration

Frontend `AdStudioCard.tsx` đã sẵn sàng. Import vào page:

```tsx
// pages/ContentStudioPage.tsx
import AdStudioCard from '../components/AdStudioCard';

export default function ContentStudioPage() {
  return (
    <div className="container mx-auto p-6">
      <AdStudioCard />
    </div>
  );
}
```

**Hoặc thêm vào router:**
```tsx
// Router.tsx
import AdStudioCard from './components/AdStudioCard';

<Route path="/content-studio" element={<AdStudioCard />} />
```

---

## 🎯 Workflow đầy đủ

1. **User mở AdStudio tab** → "Thu thập link"
2. **Dán TikTok URL** → Click "Lấy video TikTok"
3. **Frontend gọi** `POST /api/tiktok/scrape`
4. **Backend**:
   - Lấy Apify key từ DB/env
   - Gọi Apify TikTok actor
   - Parse kết quả
   - Lưu vào `ad_studio_assets`
   - Trả về Asset
5. **Frontend hiển thị** video preview + caption
6. **User chỉnh caption** → Chọn fanpage → Chọn lịch đăng
7. **Click "Lưu vào lịch đăng"**
8. **Frontend gọi** `POST /api/posts/schedule`
9. **Backend**:
   - Tính schedule_time (NOW/RANDOM_2H/EXACT_TIME)
   - Lưu vào `ad_studio_scheduled_posts`
   - Trả về success
10. **Frontend chuyển tab** → "Quản lý bài đăng"
11. **User xem lịch** đã lưu

---

## 🔗 Links tham khảo

- **API Docs:** http://localhost:8000/docs
- **Main README:** `AD_STUDIO_BACKEND_README.md`
- **Summary:** `ADSTUDIO_IMPLEMENTATION_SUMMARY.md`
- **Frontend:** `frontend/src/components/AdStudioCard.tsx`

---

**🎉 Chúc bạn triển khai thành công!**
