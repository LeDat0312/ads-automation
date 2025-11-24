# Content Studio Module - Documentation

## 📋 Tổng quan

Module **Content Studio** là hệ thống quản lý nội dung và lên lịch đăng bài tự động cho Facebook Pages. Module này giúp:

1. **Tìm kiếm** quảng cáo từ TikTok, Facebook, Ads Library
2. **Lưu trữ** nội dung vào bộ sưu tập
3. **Biên tập** và dịch caption bằng AI (Gemini/ChatGPT)
4. **Lên lịch** đăng bài tự động cho nhiều fanpage
5. **Quản lý** và theo dõi bài đăng

---

## 🎯 Tech Stack

### Frontend
- **React** + **TypeScript**
- **TailwindCSS** - styling hiện đại
- **React Query** (khuyến nghị) - data fetching & caching
- **date-fns** - date formatting

### Backend
- **FastAPI** (Python)
- **SQLAlchemy** - ORM
- **PostgreSQL** - database
- **Celery** (để triển khai) - background tasks

---

## 📁 Cấu trúc File

### Frontend

```
frontend/src/
├── types/
│   └── contentStudio.ts          # TypeScript types & interfaces
├── api/
│   └── contentStudio.ts          # API client functions
├── components/
│   └── ContentStudio/
│       ├── SearchPanel.tsx       # Tab 1: Search panel
│       ├── AdCard.tsx            # Card hiển thị quảng cáo
│       ├── AdCardList.tsx        # Grid layout với pagination
│       ├── AiEditor.tsx          # Tab 2: AI editor
│       ├── ScheduleForm.tsx      # Tab 3: Schedule form
│       └── PostManagement.tsx    # Tab 4: Post management table
└── pages/
    └── ContentStudio.tsx         # Main page với tabs
```

### Backend

```
app/
├── models/
│   └── content_studio.py         # SQLAlchemy models
├── schemas/
│   └── content_studio.py         # Pydantic schemas
├── api/routes/
│   └── content_studio.py         # FastAPI routes
└── services/
    ├── content_studio_service.py      # Business logic
    ├── ai_service.py                  # AI integration (TODO)
    └── facebook_scheduler_service.py  # Scheduler logic (TODO)
```

---

## 🔧 Triển khai

### Bước 1: Database Migration

Tạo migration cho các bảng mới:

```bash
# Tạo migration
alembic revision --autogenerate -m "Add Content Studio tables"

# Apply migration
alembic upgrade head
```

### Bước 2: Update User Model

Thêm relationships vào `app/models/user.py`:

```python
from sqlalchemy.orm import relationship

class User(Base):
    # ... existing fields ...
    
    # Content Studio relationships
    content_sources = relationship("ContentSource", back_populates="user")
    collections = relationship("Collection", back_populates="user")
    cs_facebook_pages = relationship("FacebookPageCS", back_populates="user")
```

### Bước 3: Register Router

Thêm vào `app/main.py`:

```python
from app.api.routes import content_studio

app.include_router(content_studio.router)
```

### Bước 4: Frontend Routing

Thêm route vào React Router:

```typescript
import ContentStudioPage from './pages/ContentStudio';

<Route path="/content-studio" element={<ContentStudioPage />} />
```

### Bước 5: Sidebar Navigation

Thêm menu item vào sidebar:

```jsx
<NavLink to="/content-studio">
  <span>🎬</span>
  Content Studio
</NavLink>
```

---

## 🚀 Các tính năng cần implement (TODO)

### 1. Search & Fetch Service

**File**: `app/services/content_studio_service.py`

```python
class ContentStudioService:
    async def search_content(self, user_id, query, source_type):
        """
        TODO:
        - Integrate Facebook Graph API for Ads Library
        - Integrate TikTok API/scraping
        - Implement search logic
        - Cache results
        """
        pass
    
    async def fetch_from_urls(self, user_id, urls):
        """
        TODO:
        - Parse URLs (TikTok, Facebook)
        - Fetch metadata using APIs
        - Download media files
        - Extract captions, stats
        """
        pass
```

**Integration cần thiết:**
- Facebook Graph API: `/ads_archive` endpoint
- TikTok API hoặc scraping service
- Media download & storage (S3/local)

### 2. AI Service

**File**: `app/services/ai_service.py`

```python
class AiService:
    async def rewrite_caption(self, source_caption, mode):
        """
        TODO:
        - Integrate Google Gemini API
        - Integrate OpenAI ChatGPT API
        - Implement 3 modes:
          1. TRANSLATE: Dịch sang tiếng Lào
          2. REWRITE_SALON_STYLE: Viết lại phong cách thẩm mỹ
          3. GENERATE_VARIANTS: Tạo 3 phiên bản
        """
        
        if mode == AiRewriteMode.TRANSLATE:
            prompt = f"""
            Dịch sang tiếng Lào, giữ nguyên ý:
            {source_caption}
            """
        
        elif mode == AiRewriteMode.REWRITE_SALON_STYLE:
            prompt = f"""
            Viết lại theo phong cách thẩm mỹ viện Lào:
            - Nhấn mạnh làm đẹp, chăm sóc da
            - Kêu gọi inbox
            - Thêm emoji phù hợp
            
            Nội dung gốc:
            {source_caption}
            """
        
        # Call Gemini/ChatGPT API
        # response = await gemini_api.generate(prompt)
        
        return response
```

**API Keys cần:**
- Google Gemini API key
- OpenAI API key (backup)

### 3. Facebook Scheduler Service

**File**: `app/services/facebook_scheduler_service.py`

```python
class FacebookSchedulerService:
    async def schedule_posts(self, content_variant_id, page_ids, schedule_type):
        """
        TODO:
        - Calculate scheduled_at based on type:
          * NOW: datetime.now()
          * FIXED: fixed_time
          * RANDOM: now + random(0, random_range)
        - Create ScheduledPost records
        - Queue for background worker (Celery)
        """
        pass
    
    async def publish_to_facebook(self, post_id):
        """
        TODO:
        - Get post & page info
        - Upload media to Facebook
        - Create Facebook post using Graph API
        - Update post status & fb_post_id
        """
        
        # Facebook Graph API
        # POST /{page_id}/photos or /videos
        # POST /{page_id}/feed for text posts
        
        pass
```

**Background Worker (Celery):**

```python
# app/workers/scheduler_worker.py

@celery.task
def process_scheduled_posts():
    """
    Chạy mỗi phút, kiểm tra posts cần đăng
    """
    now = datetime.now()
    posts = db.query(ScheduledPost).filter(
        ScheduledPost.status == PostStatus.SCHEDULED,
        ScheduledPost.scheduled_at <= now
    ).all()
    
    for post in posts:
        publish_to_facebook.delay(post.id)

@celery.task
def publish_to_facebook(post_id):
    """
    Đăng bài lên Facebook
    """
    # Implementation here
    pass
```

### 4. Media Storage

Cấu hình storage cho media files:

```python
# app/core/config.py

MEDIA_STORAGE_TYPE = "s3"  # or "local"
AWS_S3_BUCKET = "your-bucket-name"
LOCAL_MEDIA_PATH = "./storage/media"
```

**S3 Upload:**

```python
import boto3

s3 = boto3.client('s3')

def upload_to_s3(file_path, key):
    s3.upload_file(file_path, AWS_S3_BUCKET, key)
    return f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{key}"
```

---

## 📊 Database Schema

### Tables

1. **cs_content_sources** - Nguồn nội dung
2. **cs_media_assets** - Media files
3. **cs_collections** - Bộ sưu tập
4. **cs_collection_items** - Items trong collection
5. **cs_content_variants** - Phiên bản đã biên tập
6. **cs_facebook_pages** - Facebook pages
7. **cs_scheduled_posts** - Bài đăng đã lên lịch

### Indexes cần tạo

```sql
CREATE INDEX idx_content_sources_user ON cs_content_sources(user_id);
CREATE INDEX idx_content_sources_type ON cs_content_sources(source_type);
CREATE INDEX idx_scheduled_posts_status ON cs_scheduled_posts(status);
CREATE INDEX idx_scheduled_posts_scheduled_at ON cs_scheduled_posts(scheduled_at);
CREATE INDEX idx_scheduled_posts_user ON cs_scheduled_posts(created_by);
```

---

## 🧪 Testing

### Frontend Component Tests

```typescript
// SearchPanel.test.tsx
describe('SearchPanel', () => {
  it('should call onSearch with query and source type', () => {
    const onSearch = jest.fn();
    render(<SearchPanel onSearch={onSearch} />);
    
    const input = screen.getByPlaceholderText('Nhập từ khóa...');
    fireEvent.change(input, { target: { value: 'thẩm mỹ' } });
    
    const button = screen.getByText('Tìm kiếm');
    fireEvent.click(button);
    
    expect(onSearch).toHaveBeenCalledWith('thẩm mỹ', undefined);
  });
});
```

### Backend API Tests

```python
# test_content_studio.py

def test_search_content(client, auth_headers):
    response = client.post(
        "/api/content-studio/search",
        json={"query": "beauty salon", "source_type": "tiktok"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "items" in response.json()
```

---

## 🔒 Security

### Authentication
- Tất cả endpoints require authentication
- Sử dụng `get_current_user_optional` dependency
- Validate user ownership cho mọi resource

### Facebook Access Tokens
- Encrypt tokens trong database
- Refresh tokens định kỳ
- Handle token expiration gracefully

### Rate Limiting
- Implement rate limiting cho AI API calls
- Limit số lượng posts có thể schedule
- Prevent spam/abuse

---

## 📈 Performance Optimization

### Frontend
- Lazy load media thumbnails
- Virtual scrolling cho large lists
- Debounce search input
- Cache API responses với React Query

### Backend
- Database indexes cho query performance
- Cache Facebook API responses
- Batch processing cho multiple posts
- Background jobs cho heavy tasks (AI, publishing)

---

## 🐛 Troubleshooting

### Common Issues

**1. Facebook API Token Expired**
```
Error: "Error validating access token"
Solution: Implement token refresh flow
```

**2. AI API Rate Limit**
```
Error: "Rate limit exceeded"
Solution: Implement retry with exponential backoff
```

**3. Media Upload Fails**
```
Error: "File too large"
Solution: Implement chunked upload or compression
```

---

## 📝 Notes

- Tất cả text hiển thị cho user bằng **TIẾNG VIỆT**
- Code variables/functions bằng **TIẾNG ANH**
- UI design theo style **SO9 LAB** / modern dashboard
- Ưu tiên **user experience** và **performance**

---

## 🎯 Next Steps

1. **Phase 1**: Implement core services (search, fetch, storage)
2. **Phase 2**: Integrate AI services (Gemini/ChatGPT)
3. **Phase 3**: Implement scheduler & publisher
4. **Phase 4**: Add analytics & reporting
5. **Phase 5**: Mobile responsive & PWA

---

**Developed with ❤️ for ads automation**
