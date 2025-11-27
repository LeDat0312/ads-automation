# AdStudio Backend Implementation

## 📋 Tổng quan

Backend API cho hệ thống **AdStudio** - Quản lý nội dung quảng cáo (Thu thập video từ TikTok/Facebook, lên lịch đăng bài).

**NOTE: added for AdStudio only** - Code này được thêm riêng cho module AdStudio, KHÔNG ảnh hưởng đến code hiện tại.

## 🗂️ Files đã tạo

### 1. **Schemas/Models**
- `app/schemas/ad_studio.py` - Pydantic models cho request/response
  - `ScrapeRequest` - Request body khi scrape TikTok/Facebook
  - `Asset` - Response chứa video, thumbnail, caption
  - `SchedulePayload` - Request body khi lên lịch đăng bài
  - `ScheduleResponse` - Response sau khi schedule thành công

### 2. **Database Models**
- `app/models/ad_studio.py` - SQLAlchemy models
  - `AdStudioAsset` - Bảng lưu assets đã fetch
  - `AdStudioScheduledPost` - Bảng lưu lịch đăng bài

### 3. **Services**
- `app/services/apify_helper.py` - Helper lấy Apify API key
  - Priority 1: Database (`SystemSetting.key = 'apify_api_key'`)
  - Priority 2: Environment variable (`APIFY_DEFAULT_KEY`)

### 4. **API Routes**
- `app/api/routes/ad_studio.py` - 3 endpoints chính:
  - `POST /api/tiktok/scrape` - Lấy video từ TikTok qua Apify
  - `POST /api/facebook/scrape` - Stub cho Facebook (chưa implement)
  - `POST /api/posts/schedule` - Lưu lịch đăng bài

### 5. **Migration**
- `migrations/add_ad_studio_tables.py` - Script tạo bảng và setting

## 🚀 Cài đặt

### 1. Chạy migration để tạo bảng

```bash
# Activate virtual environment
venv\Scripts\Activate.ps1

# Run migration
python -m migrations.add_ad_studio_tables
```

### 2. Cấu hình Apify API Key

**Option A: Qua giao diện web (Khuyến nghị)**
1. Đăng nhập vào hệ thống
2. Vào `/settings`
3. Tìm mục "Cấu hình Apify API key"
4. Nhập API key và lưu

**Option B: Qua biến môi trường**
```env
# Thêm vào file .env
APIFY_DEFAULT_KEY=your_apify_api_key_here
```

## 🔐 Bảo mật Apify API Key

**QUAN TRỌNG:**
- ✅ Frontend KHÔNG BAO GIỜ biết hoặc lưu trữ Apify API key
- ✅ Admin cấu hình key tại `/settings` (lưu trong DB)
- ✅ Nếu DB không có → fallback sang `.env`
- ✅ Backend dùng key này để gọi Apify actors

**Luồng hoạt động:**
```
User (Frontend)
  ↓ POST /api/tiktok/scrape { url, note }
Backend
  ↓ get_apify_api_key(db) → Lấy từ DB/env
  ↓ Gọi Apify TikTok Data Extractor actor
  ↓ Parse kết quả → Asset { videoUrl, thumbnailUrl, caption, ... }
  ↓ Lưu vào ad_studio_assets
Frontend
  ↓ Nhận Asset, hiển thị preview
```

## 📡 API Endpoints

### 1. POST /api/tiktok/scrape

Lấy video + caption từ TikTok.

**Request:**
```json
{
  "url": "https://www.tiktok.com/@user/video/1234567890",
  "note": "Video hay về skincare"
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "platform": "tiktok",
  "sourceUrl": "https://www.tiktok.com/@user/video/1234567890",
  "videoUrl": "https://download.url/video.mp4",
  "thumbnailUrl": "https://thumbnail.url/cover.jpg",
  "captionOriginal": "สวัสดีค่ะ! วันนี้มาแชร์เคล็ดลับดูแลผิว...",
  "note": "Video hay về skincare",
  "duration": 45,
  "hashtags": ["skincare", "beauty", "thailand"]
}
```

### 2. POST /api/facebook/scrape

Stub tạm thời - chưa implement.

**Response:**
```json
{
  "message": "Facebook scraping chưa được triển khai..."
}
```

### 3. POST /api/posts/schedule

Lưu lịch đăng bài.

**Request:**
```json
{
  "assetId": "uuid-of-asset",
  "caption": "Khuyến mãi lớn! Giảm giá 50%...",
  "language": "la",
  "ctaText": "Nhắn tin ngay",
  "targetUrl": "https://facebook.com/page",
  "pageIds": ["page_id_1", "page_id_2"],
  "scheduleMode": "RANDOM_2H",
  "thumbnailSource": "FRAME"
}
```

**Schedule Modes:**
- `NOW` - Đăng ngay
- `RANDOM_2H` - Random trong 2 giờ tới
- `EXACT_TIME` - Đúng thời gian (cần `scheduleTime`)

**Response:**
```json
{
  "ok": true,
  "id": "scheduled-post-uuid",
  "message": "Đã lưu lịch đăng bài thành công. Sẽ đăng vào 2025-11-27 15:30:00 UTC"
}
```

## 🗄️ Database Schema

### Bảng: `ad_studio_assets`

| Column | Type | Description |
|--------|------|-------------|
| id | String (PK) | UUID |
| platform | String | 'tiktok', 'facebook', 'other' |
| source_url | Text | URL gốc |
| video_url | Text | Link video đã download |
| thumbnail_url | Text | Link thumbnail |
| caption_original | Text | Caption gốc |
| note | Text | Ghi chú của user |
| duration | Integer | Độ dài video (giây) |
| hashtags | JSON | Danh sách hashtags |
| created_at | DateTime | Thời gian tạo |

### Bảng: `ad_studio_scheduled_posts`

| Column | Type | Description |
|--------|------|-------------|
| id | String (PK) | UUID |
| asset_id | String | FK đến assets |
| caption | Text | Nội dung đăng |
| language | String | 'la', 'vi', 'th' |
| cta_text | String | Call-to-action |
| target_url | Text | Link đích |
| page_ids | JSON | Danh sách fanpage IDs |
| schedule_mode | String | 'NOW', 'RANDOM_2H', 'EXACT_TIME' |
| schedule_time | DateTime | Thời gian đăng (đã tính toán) |
| status | String | 'SCHEDULED', 'PUBLISHED', etc. |
| created_at | DateTime | Thời gian tạo |

## 🧪 Testing

### Test Apify API key helper

```python
from app.services.apify_helper import get_apify_api_key
from app.core.database import get_db_session

db = get_db_session()
try:
    key = get_apify_api_key(db)
    print(f"✅ Apify key: {key[:10]}...")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
```

### Test TikTok scrape endpoint

```bash
curl -X POST http://localhost:8000/api/tiktok/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@user/video/1234567890",
    "note": "Test video"
  }'
```

### Test schedule endpoint

```bash
curl -X POST http://localhost:8000/api/posts/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "Test post",
    "language": "la",
    "ctaText": "Nhắn tin ngay",
    "pageIds": ["123456"],
    "scheduleMode": "NOW",
    "thumbnailSource": "FRAME"
  }'
```

## 📝 Notes

1. **Apify Actor ID**: Hiện tại dùng `clockworks/free-tiktok-scraper`. Nếu cần đổi actor, update `TIKTOK_ACTOR_ID` trong `ad_studio.py`.

2. **Facebook Implementation**: Endpoint `/api/facebook/scrape` là stub. Cần implement khi có Apify actor cho Facebook.

3. **Worker cho Publishing**: Bảng `ad_studio_scheduled_posts` lưu lịch đăng. Cần tạo worker riêng (Celery/APScheduler) để đọc bảng này và post lên Facebook theo `schedule_time`.

4. **Frontend Integration**: Frontend `AdStudioCard.tsx` đã sẵn sàng, chỉ cần backend chạy là có thể test luôn.

## 🔄 Future Enhancements

- [ ] Implement Facebook scraping với Apify actor
- [ ] Tạo background worker để auto-post lên Facebook
- [ ] Thêm retry logic cho failed posts
- [ ] Thêm analytics/tracking cho posts
- [ ] Hỗ trợ multiple languages cho AI rewrite caption
- [ ] Webhook callback khi post thành công/failed

## 👨‍💻 Code Structure

Tất cả code AdStudio được đánh dấu với comment:
```python
# NOTE: added for AdStudio only
```

Giúp dễ dàng tracking và không nhầm lẫn với code hiện tại của hệ thống.
