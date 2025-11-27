"""
Ad Studio API Routes
NOTE: added for AdStudio only

Endpoints cho hệ thống quản lý nội dung quảng cáo (AdStudio):
- GET /ad-studio - UI page
- POST /api/tiktok/scrape - Lấy video + caption từ TikTok qua Apify
- POST /api/facebook/scrape - Stub cho Facebook (chưa implement)
- POST /api/posts/schedule - Lưu lịch đăng bài
"""

import random
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Any, Dict, List, Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ad_studio import AdStudioAsset, AdStudioScheduledPost
from app.models.user import User
from app.schemas.ad_studio import ScrapeRequest, Asset, SchedulePayload, ScheduleResponse
from app.services.apify_helper import get_apify_api_key
from app.api.routes.auth import get_current_user_optional
from app.core.ui_helpers import get_user_dropdown_menu, get_account_locked_message

# NOTE: added for AdStudio only
router = APIRouter(tags=["ad-studio"])
api_router = APIRouter(prefix="/api", tags=["ad-studio"])

@router.get("/ad-studio", response_class=HTMLResponse)
async def ad_studio_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Trang Ad Studio - UI cho việc thu thập, quản lý video và lên lịch đăng bài
    NOTE: added for AdStudio only
    """
    # Check if user is locked
    if current_user and not current_user.is_active:
        return HTMLResponse(content=get_account_locked_message())
    
    user_info = get_user_dropdown_menu(current_user) if current_user else ""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ad Studio - Facebook Ads Automation</title>
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            .header {{
                background: white;
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 24px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .header h1 {{
                font-size: 32px;
                font-weight: 700;
                color: #1e293b;
            }}
            
            .btn-home {{
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }}
            
            .btn-home:hover {{
                opacity: 0.9;
            }}
            
            .content {{
                background: white;
                border-radius: 16px;
                padding: 32px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                min-height: 600px;
            }}
            
            #root {{
                width: 100%;
            }}
        </style>
    </head>
    <body>
        {user_info}
        
        <div class="container">
            <div class="header">
                <h1>🎬 Ad Studio</h1>
                <a href="/" class="btn-home">🏠 Về Trang Chủ</a>
            </div>
            
            <div class="content">
                <div id="root"></div>
            </div>
        </div>
        
        <script type="module">
            import {{ createRoot }} from 'https://esm.sh/react-dom@18/client';
            import {{ createElement }} from 'https://esm.sh/react@18';
            
            // Placeholder - trong production sẽ load từ built React app
            const App = () => {{
                return createElement('div', {{ 
                    style: {{ 
                        textAlign: 'center', 
                        padding: '40px',
                        color: '#64748b'
                    }} 
                }}, 
                    createElement('h2', null, '🚧 Ad Studio đang được xây dựng'),
                    createElement('p', null, 'Tính năng này sẽ sớm được hoàn thiện.')
                );
            }};
            
            const root = createRoot(document.getElementById('root'));
            root.render(createElement(App));
        </script>
        
        <script>
            // Authentication check
            function getCookie(name) {{
                const value = \`; $\{{document.cookie}}\`;
                const parts = value.split(\`; $\{{name}}=\`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }}
            
            const token = localStorage.getItem('access_token') || getCookie('access_token');
            if (!token) {{
                window.location.href = '/auth/login';
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Apify constants
APIFY_BASE = "https://api.apify.com/v2"
TIKTOK_ACTOR_ID = "clockworks/free-tiktok-scraper"  # Actor ID cho TikTok Data Extractor


def _map_tiktok_item_to_asset(
    item: Dict[str, Any], 
    source_url: str, 
    note: str | None
) -> Asset:
    """
    Map một item từ dataset TikTok của Apify sang schema Asset mà frontend expect.
    
    Dựa trên JSON structure của TikTok Data Extractor actor:
    - text: Caption
    - mediaUrls[0]: Video URL
    - videoMeta.coverUrl: Thumbnail URL
    - videoMeta.duration: Duration in seconds
    
    Args:
        item: TikTok item từ Apify dataset
        source_url: URL gốc user đã paste
        note: Ghi chú của user (optional)
        
    Returns:
        Asset: Object Asset theo format frontend
    """
    # Extract video URL
    media_urls: List[str] = item.get("mediaUrls") or []
    video_url = media_urls[0] if media_urls else ""
    
    # Extract video metadata
    video_meta = item.get("videoMeta") or {}
    thumbnail_url = video_meta.get("coverUrl") or ""
    duration = video_meta.get("duration") or 0
    
    # Extract caption/text
    caption = item.get("text") or ""
    
    # Extract hashtags (nếu có)
    hashtags_data = item.get("hashtags") or []
    hashtags = [tag.get("name", "") for tag in hashtags_data if isinstance(tag, dict)]
    
    return Asset(
        id=str(uuid4()),
        platform="tiktok",
        sourceUrl=source_url,
        videoUrl=video_url,
        thumbnailUrl=thumbnail_url,
        captionOriginal=caption,
        note=note,
        duration=duration,
        hashtags=hashtags if hashtags else None,
    )


@api_router.post("/tiktok/scrape", response_model=Asset)
def scrape_tiktok(
    body: ScrapeRequest,
    db: Session = Depends(get_db),
):
    """
    Lấy video + caption từ TikTok qua Apify actor.
    
    QUAN TRỌNG - BẢO MẬT:
    - Apify API key được lấy từ DB (admin cấu hình tại /settings)
    - Nếu DB không có → fallback sang biến môi trường APIFY_DEFAULT_KEY
    - Frontend KHÔNG BAO GIỜ biết hoặc lưu trữ Apify API key
    
    Luồng hoạt động:
    1. Lấy Apify API key từ helper (DB → .env)
    2. Gọi Apify actor "TikTok Data Extractor"
    3. Chờ actor chạy xong, lấy dataset
    4. Map kết quả thành Asset object
    5. Lưu vào bảng ad_studio_assets
    6. Trả về Asset cho frontend
    
    Args:
        body: ScrapeRequest chứa URL TikTok và note (optional)
        db: Database session
        
    Returns:
        Asset: Object chứa video URL, thumbnail, caption, etc.
        
    Raises:
        HTTPException 500: Nếu không tìm thấy Apify key hoặc lỗi khi gọi Apify
    """
    # NOTE: added for AdStudio only
    
    # 1. Lấy Apify API key (DB first → .env fallback)
    try:
        apify_key = get_apify_api_key(db)
    except HTTPException as e:
        raise e
    
    # 2. Start actor run trên Apify
    start_run_url = f"{APIFY_BASE}/acts/{TIKTOK_ACTOR_ID}/runs?token={apify_key}"
    
    # Input cho TikTok actor - tuỳ actor có thể khác
    run_input: Dict[str, Any] = {
        "directUrls": [str(body.url)],
        "resultsPerPage": 1,
        "shouldDownloadVideos": True,
        "shouldDownloadCovers": True,
    }
    
    try:
        r = requests.post(start_run_url, json=run_input, timeout=120)
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi kết nối tới Apify TikTok actor: {str(e)}"
        )
    
    if r.status_code >= 300:
        raise HTTPException(
            status_code=500,
            detail=f"Apify TikTok actor trả lỗi {r.status_code}: {r.text}"
        )
    
    run_data = r.json().get("data") or {}
    dataset_id = run_data.get("defaultDatasetId")
    
    if not dataset_id:
        raise HTTPException(
            status_code=500,
            detail="Không lấy được dataset ID từ Apify TikTok actor"
        )
    
    # 3. Lấy dataset items
    dataset_url = f"{APIFY_BASE}/datasets/{dataset_id}/items?token={apify_key}"
    
    try:
        d = requests.get(dataset_url, timeout=120)
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lấy dataset từ Apify: {str(e)}"
        )
    
    if d.status_code >= 300:
        raise HTTPException(
            status_code=500,
            detail=f"Apify dataset trả lỗi {d.status_code}: {d.text}"
        )
    
    items: List[Dict[str, Any]] = d.json()
    
    if not items:
        raise HTTPException(
            status_code=500,
            detail="Dataset TikTok rỗng, không tìm thấy video nào"
        )
    
    item = items[0]
    
    # 4. Map sang schema Asset mà frontend expect
    asset = _map_tiktok_item_to_asset(
        item=item, 
        source_url=str(body.url), 
        note=body.note
    )
    
    # 5. Lưu vào database
    try:
        db_asset = AdStudioAsset(
            id=asset.id,
            platform=asset.platform,
            source_url=asset.sourceUrl,
            video_url=asset.videoUrl,
            thumbnail_url=asset.thumbnailUrl,
            caption_original=asset.captionOriginal,
            note=asset.note,
            duration=asset.duration,
            hashtags=asset.hashtags,
            created_at=datetime.utcnow(),
        )
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lưu asset vào database: {str(e)}"
        )
    
    return asset


@api_router.post("/facebook/scrape")
def scrape_facebook_stub(body: ScrapeRequest):
    """
    Stub tạm thời cho Facebook scraping.
    
    TODO: Implement sau khi có Apify actor cho Facebook Reels/Video/Ad Library.
    Hiện tại chỉ trả về message để frontend không bị lỗi.
    
    Args:
        body: ScrapeRequest chứa URL Facebook
        
    Returns:
        dict: Message thông báo chưa implement
    """
    # NOTE: added for AdStudio only
    return {
        "message": "Facebook scraping chưa được triển khai. Vui lòng sử dụng TikTok hoặc chờ cập nhật.",
        "url": str(body.url),
    }


@api_router.post("/posts/schedule", response_model=ScheduleResponse)
def schedule_post(
    payload: SchedulePayload,
    db: Session = Depends(get_db),
):
    """
    Lưu lịch đăng bài lên fanpage.
    
    Logic schedule time:
    - NOW: Đăng ngay (schedule_time = hiện tại)
    - RANDOM_2H: Random trong 2 giờ tới
    - EXACT_TIME: Dùng thời gian user chọn (payload.scheduleTime)
    
    Worker riêng sẽ xử lý việc đăng bài thật lên Facebook theo schedule_time.
    
    Args:
        payload: SchedulePayload chứa thông tin bài đăng
        db: Database session
        
    Returns:
        ScheduleResponse: Kết quả với ID của scheduled post
        
    Raises:
        HTTPException 400: Nếu thiếu thông tin bắt buộc
        HTTPException 500: Nếu lỗi khi lưu database
    """
    # NOTE: added for AdStudio only
    
    # Validate
    if not payload.caption or not payload.caption.strip():
        raise HTTPException(status_code=400, detail="Caption không được để trống")
    
    if not payload.pageIds or len(payload.pageIds) == 0:
        raise HTTPException(status_code=400, detail="Phải chọn ít nhất 1 fanpage")
    
    # 1. Tính schedule_time dựa vào scheduleMode
    now = datetime.utcnow()
    schedule_time: datetime
    
    if payload.scheduleMode == "NOW":
        schedule_time = now
        
    elif payload.scheduleMode == "RANDOM_2H":
        # Random trong 0 - 7200 giây (2 giờ)
        delay_seconds = random.randint(0, 2 * 60 * 60)
        schedule_time = now + timedelta(seconds=delay_seconds)
        
    elif payload.scheduleMode == "EXACT_TIME":
        if not payload.scheduleTime:
            raise HTTPException(
                status_code=400,
                detail="scheduleTime là bắt buộc khi chọn EXACT_TIME"
            )
        
        try:
            # Parse ISO datetime string
            # Frontend gửi format: "2025-11-27T14:30:00"
            schedule_time = datetime.fromisoformat(payload.scheduleTime.replace("Z", "+00:00"))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Định dạng scheduleTime không hợp lệ: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"scheduleMode không hợp lệ: {payload.scheduleMode}"
        )
    
    # 2. Tạo scheduled post record
    post_id = str(uuid4())
    
    try:
        scheduled_post = AdStudioScheduledPost(
            id=post_id,
            asset_id=payload.assetId,
            source_url=payload.sourceUrl,
            caption=payload.caption.strip(),
            language=payload.language,
            cta_text=payload.ctaText,
            target_url=payload.targetUrl,
            page_ids=payload.pageIds,
            schedule_mode=payload.scheduleMode,
            schedule_time=schedule_time,
            thumbnail_source=payload.thumbnailSource,
            status="SCHEDULED",
            created_at=now,
        )
        
        db.add(scheduled_post)
        db.commit()
        db.refresh(scheduled_post)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lưu lịch đăng bài vào database: {str(e)}"
        )
    
    return ScheduleResponse(
        ok=True,
        id=post_id,
        message=f"Đã lưu lịch đăng bài thành công. Sẽ đăng vào {schedule_time.strftime('%Y-%m-%d %H:%M:%S')} UTC",
    )
