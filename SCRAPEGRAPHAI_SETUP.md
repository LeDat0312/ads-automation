# 🔍 Hướng dẫn tích hợp ScrapeGraphAI

## ⚠️ Lưu ý quan trọng

- **CHỈ DÙNG CHO HỆ THỐNG NỘI BỘ**
- Việc scraping Facebook có thể vi phạm Terms of Service của Facebook
- Sử dụng có trách nhiệm và tuân thủ rate limiting
- Cache dữ liệu để tránh scrape quá thường xuyên

## 📋 Cấu hình

### 1. Lấy API Key từ ScrapeGraphAI

1. Đăng ký tài khoản tại https://dashboard.scrapegraphai.com/
2. Lấy API key từ dashboard
3. Lưu API key vào environment variable:

```bash
# Linux/Mac
export SCRAPEGRAPHAI_API_KEY="your_api_key_here"

# Windows PowerShell
$env:SCRAPEGRAPHAI_API_KEY="your_api_key_here"

# Hoặc thêm vào .env file
SCRAPEGRAPHAI_API_KEY=your_api_key_here
```

### 2. Cập nhật API Base URL (nếu cần)

Nếu ScrapeGraphAI sử dụng URL khác, cập nhật trong `app/services/scrapegraphai_service.py`:

```python
SCRAPEGRAPHAI_BASE_URL = "https://api.scrapegraphai.com/v1"  # Cập nhật URL thực tế
```

## 🚀 Sử dụng API

### 1. Scrape một quảng cáo cụ thể

```bash
POST /competitor/scrape/ad
Content-Type: application/json

{
  "ad_url": "https://www.facebook.com/ads/library/?id=123456789",
  "use_cache": true
}
```

### 2. Scrape tất cả quảng cáo của đối thủ

```bash
POST /competitor/scrape/competitor
Content-Type: application/json

{
  "page_id": "123456789012345",
  "limit": 50,
  "use_cache": true
}
```

### 3. Tìm kiếm quảng cáo theo keyword

```bash
POST /competitor/search/ads
Content-Type: application/json

{
  "keyword": "điện thoại",
  "limit": 20,
  "use_cache": true
}
```

### 4. Health check

```bash
GET /competitor/health
```

## 📊 Response Format

### Scrape Ad Response

```json
{
  "success": true,
  "data": {
    "ad_id": "123456789",
    "ad_text": "Nội dung quảng cáo...",
    "ad_image_url": "https://...",
    "ad_video_url": null,
    "page_name": "Tên Page",
    "page_id": "123456789012345",
    "impressions": 10000,
    "engagement": 500,
    "created_time": "2024-01-01T00:00:00",
    "ad_type": "IMAGE",
    "landing_page_url": "https://...",
    "scraped_at": "2024-01-01T12:00:00"
  }
}
```

### Scrape Competitor Response

```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "ad_id": "123456789",
      "ad_text": "...",
      ...
    }
  ]
}
```

## 🔧 Tích hợp vào Frontend

### 1. Thêm service vào `frontend/src/services/api.ts`

```typescript
export async function scrapeCompetitorAd(adUrl: string, useCache: boolean = true) {
  const response = await api.post('/competitor/scrape/ad', {
    ad_url: adUrl,
    use_cache: useCache
  });
  return response.data;
}

export async function scrapeCompetitorAds(pageId: string, limit: number = 50) {
  const response = await api.post('/competitor/scrape/competitor', {
    page_id: pageId,
    limit: limit,
    use_cache: true
  });
  return response.data;
}

export async function searchCompetitorAds(keyword: string, limit: number = 20) {
  const response = await api.post('/competitor/search/ads', {
    keyword: keyword,
    limit: limit,
    use_cache: true
  });
  return response.data;
}
```

### 2. Tạo component React để hiển thị

Tạo file `frontend/src/components/CompetitorResearch.tsx`:

```typescript
import React, { useState } from 'react';
import { scrapeCompetitorAd, searchCompetitorAds } from '@/services/api';

export const CompetitorResearch: React.FC = () => {
  const [keyword, setKeyword] = useState('');
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const result = await searchCompetitorAds(keyword, 20);
      setAds(result.data);
    } catch (error) {
      console.error('Error searching ads:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="Nhập keyword tìm kiếm..."
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Đang tìm...' : 'Tìm kiếm'}
      </button>
      
      <div>
        {ads.map((ad) => (
          <div key={ad.ad_id}>
            <h3>{ad.page_name}</h3>
            <p>{ad.ad_text}</p>
            {ad.ad_image_url && <img src={ad.ad_image_url} alt="Ad" />}
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 🛡️ Best Practices

1. **Rate Limiting**: 
   - Cache dữ liệu ít nhất 1 giờ (đã cấu hình sẵn)
   - Không scrape quá 100 requests/phút

2. **Error Handling**:
   - Luôn check `success` field trong response
   - Handle timeout và network errors

3. **Privacy**:
   - Chỉ lưu dữ liệu cần thiết
   - Xóa dữ liệu cũ định kỳ
   - Không chia sẻ dữ liệu ra ngoài hệ thống nội bộ

4. **Monitoring**:
   - Log tất cả requests
   - Monitor API usage và costs
   - Set up alerts cho errors

## 🔍 Debugging

### Kiểm tra API key

```bash
curl http://localhost:8000/competitor/health
```

### Test scrape một ad

```bash
curl -X POST http://localhost:8000/competitor/scrape/ad \
  -H "Content-Type: application/json" \
  -d '{"ad_url": "https://www.facebook.com/ads/library/?id=123456789"}'
```

## 📝 Notes

- API endpoints có thể thay đổi tùy theo ScrapeGraphAI documentation
- Cần xác nhận URL và format chính xác từ ScrapeGraphAI
- Có thể cần điều chỉnh timeout và retry logic tùy theo performance

