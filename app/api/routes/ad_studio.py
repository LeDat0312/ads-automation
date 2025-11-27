"""
Ad Studio API Routes
NOTE: added for AdStudio only

Endpoints cho hệ thống quản lý nội dung quảng cáo (AdStudio):
- GET /ad-studio - UI page (serve React app)
- POST /api/tiktok/scrape - Lấy video + caption từ TikTok qua Apify
- POST /api/facebook/scrape - Stub cho Facebook (chưa implement)
- POST /api/posts/schedule - Lưu lịch đăng bài
"""

import os
import random
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Any, Dict, List, Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
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
    NOTE: added for AdStudio only - Serve React app
    """
    # Check if user is locked
    if current_user and not current_user.is_active:
        return HTMLResponse(content=get_account_locked_message())
    
    # Redirect to login if not authenticated
    if not current_user:
        return HTMLResponse(content="""
        <script>
            window.location.href = '/auth/login';
        </script>
        """)
    
    # Serve React app from frontend/dist
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    frontend_dist = os.path.join(project_root, "frontend", "dist", "index.html")
    
    if os.path.exists(frontend_dist):
        return FileResponse(frontend_dist)
    else:
        # Fallback nếu React app chưa được build
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ad Studio - React App Not Built</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0;
                }
                .container {
                    background: white;
                    border-radius: 16px;
                    padding: 48px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                    text-align: center;
                    max-width: 600px;
                }
                h1 { color: #1e293b; margin-bottom: 16px; }
                p { color: #64748b; margin-bottom: 24px; }
                pre {
                    background: #f1f5f9;
                    padding: 16px;
                    border-radius: 8px;
                    text-align: left;
                    overflow-x: auto;
                }
                .btn {
                    display: inline-block;
                    margin-top: 16px;
                    padding: 12px 24px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎬 Ad Studio</h1>
                <p>React frontend chưa được build. Vui lòng chạy lệnh sau:</p>
                <pre>cd frontend && npm install && npm run build</pre>
                <a href="/" class="btn">🏠 Về Trang Chủ</a>
            </div>
        </body>
        </html>
        """)


# Apify constants
APIFY_BASE = "https://api.apify.com/v2"
# NOTE: AdStudio - Actor ID format: clockworks/free-tiktok-scraper
# In API URLs, slash must be replaced with tilde: clockworks~free-tiktok-scraper
TIKTOK_ACTOR_ID = "clockworks~free-tiktok-scraper"


def _map_tiktok_item_to_asset(
    item: Dict[str, Any], 
    source_url: str, 
    note: str | None
) -> Asset:
    """
    Map một item từ dataset TikTok của Apify sang schema Asset mà frontend expect.
    
    NOTE: AdStudio - Updated mapping for clockworks/free-tiktok-scraper (TikTok Data Extractor)
    
    Actual dataset structure từ actor:
    {
      "id": "7536470562428800263",
      "text": "caption...",
      "webVideoUrl": "https://www.tiktok.com/@user/video/...",
      "submittedVideoUrl": "https://www.tiktok.com/@user/video/...",
      "mediaUrls": [],  # Empty - actor không download video
      "videoMeta": {
        "height": 1024,
        "width": 576,
        "duration": 12,
        "coverUrl": "https://...image",
        "originalCoverUrl": "https://...image",
        "definition": "540p",
        "format": "mp4"
      },
      "hashtags": [{"id": "...", "name": "muitrunghoa", ...}, ...],
      "authorMeta": {...}
    }
    
    Args:
        item: TikTok item từ Apify dataset
        source_url: URL gốc user đã paste
        note: Ghi chú của user (optional)
        
    Returns:
        Asset: Object Asset theo format frontend
    """
    # NOTE: AdStudio - Extract theo format thực tế của TikTok Data Extractor
    video_meta = item.get("videoMeta") or {}
    
    # Video URL: Actor này không cung cấp direct mp4 link, chỉ có TikTok link
    # Ưu tiên submittedVideoUrl (URL user paste), fallback webVideoUrl
    video_url = item.get("submittedVideoUrl") or item.get("webVideoUrl") or source_url
    
    # Thumbnail: lấy từ videoMeta
    thumbnail_url = video_meta.get("coverUrl") or video_meta.get("originalCoverUrl") or ""
    
    # Caption
    caption = item.get("text") or ""
    
    # Duration (seconds)
    duration = video_meta.get("duration") or 0
    
    # Hashtags: parse từ array of objects
    # NOTE: AdStudio - Actor trả về array of {id, name, title, cover}
    hashtags_data = item.get("hashtags") or []
    hashtags = []
    
    if isinstance(hashtags_data, list):
        for tag in hashtags_data:
            if isinstance(tag, dict) and tag.get("name"):
                hashtags.append(tag["name"])
            elif isinstance(tag, str):
                hashtags.append(tag)
    
    return Asset(
        id=str(uuid4()),
        platform="tiktok",
        sourceUrl=source_url,
        videoUrl=video_url,
        thumbnailUrl=thumbnail_url,
        captionOriginal=caption,
        note=note,
        duration=duration if duration else None,
        hashtags=hashtags if hashtags else None,
    )


@api_router.post("/tiktok/scrape", response_model=Asset)
def scrape_tiktok(
    body: ScrapeRequest,
    db: Session = Depends(get_db),
):
    """
    Lấy video + caption từ TikTok qua Apify actor.
    NOTE: AdStudio - Use run-sync-get-dataset-items for immediate results
    
    QUAN TRỌNG - BẢO MẬT:
    - Apify API key được lấy từ DB (admin cấu hình tại /settings)
    - Nếu DB không có → fallback sang biến môi trường APIFY_DEFAULT_KEY
    - Frontend KHÔNG BAO GIỜ biết hoặc lưu trữ Apify API key
    
    Apify Actor: clockworks/free-tiktok-scraper
    Endpoint: POST /v2/acts/{actorId}/run-sync-get-dataset-items
    Input format: {"postURLs": ["https://tiktok.com/..."], "shouldDownloadVideos": false, ...}
    
    Args:
        body: ScrapeRequest chứa URL TikTok và note (optional)
        db: Database session
        
    Returns:
        Asset: Object chứa video URL, thumbnail, caption, etc.
        
    Raises:
        HTTPException 400: Nếu thiếu Apify key (APIFY_KEY_MISSING)
        HTTPException 502: Nếu lỗi khi gọi Apify (APIFY_SCRAPE_FAILED)
    """
    # NOTE: AdStudio
    import logging
    logger = logging.getLogger(__name__)
    
    # 1. Lấy Apify API key (DB first → .env fallback)
    try:
        apify_key = get_apify_api_key(db)
    except HTTPException as e:
        # Re-raise với detail APIFY_KEY_MISSING
        raise e
    
    # 2. Call Apify synchronously and get dataset items immediately
    # NOTE: AdStudio - Use run-sync-get-dataset-items endpoint (không cần /runs rồi fetch dataset)
    sync_url = f"{APIFY_BASE}/acts/{TIKTOK_ACTOR_ID}/run-sync-get-dataset-items?token={apify_key}"
    
    # Input theo OpenAPI schema của clockworks/free-tiktok-scraper
    # Key field: postURLs (array of strings) - NOT directUrls
    run_input: Dict[str, Any] = {
        "postURLs": [str(body.url)],
        "shouldDownloadVideos": False,  # Không cần download, chỉ lấy metadata + link
        "shouldDownloadCovers": False,  # Không cần download thumbnail
        "shouldDownloadSubtitles": False,
    }
    
    logger.info(f"Calling Apify TikTok scraper for URL: {body.url}")
    
    try:
        # NOTE: AdStudio - Timeout 180s cho sync call (actor cần thời gian scrape)
        r = requests.post(sync_url, json=run_input, timeout=180)
        
        # Log response để debug
        logger.info(f"Apify response status: {r.status_code}")
        
        # NOTE: AdStudio - Apify trả về 200 hoặc 201 (Created) cho run-sync-get-dataset-items
        if r.status_code not in (200, 201):
            logger.error(f"Apify error response: {r.text[:500]}")
            raise HTTPException(
                status_code=502,
                detail="APIFY_SCRAPE_FAILED"
            )
        
        r.raise_for_status()
        
    except requests.exceptions.Timeout:
        logger.error("Apify TikTok scrape timeout after 180s")
        raise HTTPException(
            status_code=504,
            detail="APIFY_SCRAPE_TIMEOUT"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Apify TikTok scrape network error: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="APIFY_SCRAPE_FAILED"
        )
    except Exception as e:
        logger.error(f"Apify TikTok scrape unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail="APIFY_SCRAPE_FAILED"
        )
    
    # 3. Parse dataset items từ response body (run-sync-get-dataset-items trả về trực tiếp array)
    try:
        items: List[Dict[str, Any]] = r.json()
    except Exception as e:
        logger.error(f"Failed to parse Apify response JSON: {str(e)}, body: {r.text[:500]}")
        raise HTTPException(
            status_code=502,
            detail="APIFY_SCRAPE_FAILED"
        )
    
    if not items or len(items) == 0:
        logger.error(f"Empty dataset from Apify for URL: {body.url}")
        raise HTTPException(
            status_code=502,
            detail="APIFY_SCRAPE_FAILED"
        )
    
    item = items[0]
    logger.info(f"Successfully scraped TikTok video, item keys: {list(item.keys())}")
    
    # 4. Map sang schema Asset mà frontend expect
    asset = _map_tiktok_item_to_asset(
        item=item, 
        source_url=str(body.url), 
        note=body.note
    )
    
    # NOTE: AdStudio - Validate asset có đủ dữ liệu để preview
    if not asset.thumbnailUrl or not asset.videoUrl:
        logger.error(
            f"Invalid Apify payload - missing required fields. "
            f"thumbnailUrl: {asset.thumbnailUrl}, videoUrl: {asset.videoUrl}, "
            f"item keys: {list(item.keys())}, "
            f"videoMeta: {item.get('videoMeta', {})}"
        )
        raise HTTPException(
            status_code=502,
            detail="APIFY_SCRAPE_PAYLOAD_INVALID"
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
        logger.info(f"Saved asset to DB: {asset.id}, videoUrl: {asset.videoUrl[:50]}, thumbnailUrl: {asset.thumbnailUrl[:50]}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving asset to DB: {str(e)}", exc_info=True)
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


# ==================== NEW ENDPOINTS FOR AD STUDIO - NOTE: AdStudio ====================

@api_router.post("/facebook/scrape", response_model=Asset)
def scrape_facebook(
    body: ScrapeRequest,
    db: Session = Depends(get_db),
):
    """
    Lấy video + caption từ Facebook qua Apify actor.
    NOTE: AdStudio - Implement Facebook scraping thật
    
    Args:
        body: ScrapeRequest chứa URL Facebook và note (optional)
        db: Database session
        
    Returns:
        Asset: Object chứa video URL, thumbnail, caption, etc.
        
    Raises:
        HTTPException 400: Nếu thiếu Apify key (APIFY_KEY_MISSING)
        HTTPException 502: Nếu lỗi khi gọi Apify (APIFY_SCRAPE_FAILED)
    """
    # NOTE: AdStudio
    import logging
    logger = logging.getLogger(__name__)
    
    # 1. Lấy Apify API key
    try:
        apify_key = get_apify_api_key(db)
    except HTTPException as e:
        # Re-raise với detail APIFY_KEY_MISSING
        raise e
    
    # 2. Lấy Facebook actor ID từ env hoặc setting
    import os
    fb_actor_id = os.getenv("FACEBOOK_SCRAPER_ACTOR_ID", "apify/facebook-posts-scraper")
    
    # 3. Start actor run trên Apify
    start_run_url = f"{APIFY_BASE}/acts/{fb_actor_id}/runs?token={apify_key}"
    
    run_input: Dict[str, Any] = {
        "startUrls": [{"url": str(body.url)}],
        "maxPosts": 1,
    }
    
    try:
        r = requests.post(start_run_url, json=run_input, timeout=120)
        r.raise_for_status()
    except Exception as e:
        logger.error(f"Apify Facebook scrape error: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="APIFY_SCRAPE_FAILED"
        )
    
    run_data = r.json().get("data") or {}
    dataset_id = run_data.get("defaultDatasetId")
    
    if not dataset_id:
        raise HTTPException(
            status_code=502,
            detail="APIFY_SCRAPE_FAILED"
        )
    
    # 4. Lấy dataset items
    dataset_url = f"{APIFY_BASE}/datasets/{dataset_id}/items?token={apify_key}"
    
    try:
        d = requests.get(dataset_url, timeout=120)
        d.raise_for_status()
    except Exception as e:
        logger.error(f"Apify dataset fetch error: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="APIFY_SCRAPE_FAILED"
        )
    
    items: List[Dict[str, Any]] = d.json()
    
    if not items:
        raise HTTPException(
            status_code=502,
            detail="APIFY_SCRAPE_FAILED"
        )
    
    item = items[0]
    
    # 5. Parse Facebook item
    video_url = item.get("videoUrl") or item.get("video") or None
    thumbnail_url = item.get("image") or item.get("imageUrl") or ""
    caption = item.get("text") or item.get("message") or ""
    
    asset = Asset(
        id=str(uuid4()),
        platform="facebook",
        sourceUrl=str(body.url),
        videoUrl=video_url or "",
        thumbnailUrl=thumbnail_url,
        captionOriginal=caption,
        note=body.note,
        duration=None,
        hashtags=None,
    )
    
    # 6. Lưu vào database
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
        logger.error(f"Error saving Facebook asset: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lưu asset vào database: {str(e)}"
        )
    
    return asset


@api_router.get("/ad-studio/pages")
def get_ad_studio_pages(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách Facebook pages cho Ad Studio
    NOTE: AdStudio - Reuse logic from content_studio or settings
    
    Returns:
        List of pages: [{"id": "PAGE_ID", "name": "Page Name", "platform": "facebook"}]
    """
    # NOTE: AdStudio
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Tạm thời trả về từ SystemSetting hoặc mock
    # TODO: Integrate với Facebook Graph API /me/accounts
    from app.core.database import SystemSetting
    
    fb_token_setting = db.query(SystemSetting).filter(
        SystemSetting.key == "facebook_access_token"
    ).first()
    
    if not fb_token_setting or not fb_token_setting.value:
        # Chưa cấu hình token, trả về list rỗng
        return {"items": []}
    
    # Gọi Facebook Graph API để lấy pages
    import requests
    fb_token = fb_token_setting.value
    
    try:
        r = requests.get(
            "https://graph.facebook.com/v18.0/me/accounts",
            params={"access_token": fb_token},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        
        pages = []
        for page in data.get("data", []):
            pages.append({
                "id": page.get("id"),
                "name": page.get("name"),
                "platform": "facebook"
            })
        
        return {"items": pages}
    except Exception as e:
        # Fallback: trả về empty
        import logging
        logging.error(f"Error fetching Facebook pages: {str(e)}")
        return {"items": []}


@api_router.get("/ad-studio/assets")
def get_ad_studio_assets(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách assets đã lưu trong bộ sưu tầm
    NOTE: AdStudio
    """
    # NOTE: AdStudio
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Query all assets, order by created_at desc
    assets = db.query(AdStudioAsset).order_by(
        AdStudioAsset.created_at.desc()
    ).limit(100).all()
    
    result = []
    for asset in assets:
        result.append({
            "id": asset.id,
            "platform": asset.platform,
            "sourceUrl": asset.source_url,
            "videoUrl": asset.video_url,
            "thumbnailUrl": asset.thumbnail_url,
            "captionOriginal": asset.caption_original,
            "note": asset.note,
            "duration": asset.duration,
            "hashtags": asset.hashtags,
            "createdAt": asset.created_at.isoformat() if asset.created_at else None,
        })
    
    return {"items": result}


@api_router.get("/ad-studio/posts")
def get_ad_studio_posts(
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách bài đăng đã lên lịch
    NOTE: AdStudio
    
    Args:
        status: ALL | SCHEDULED | PUBLISHED | FAILED | DRAFT | CANCELLED
        from_date: ISO date string
        to_date: ISO date string
    """
    # NOTE: AdStudio
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    query = db.query(AdStudioScheduledPost)
    
    # Filter by status
    if status and status != "ALL":
        query = query.filter(AdStudioScheduledPost.status == status)
    
    # Filter by date range
    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date)
            query = query.filter(AdStudioScheduledPost.created_at >= from_dt)
        except:
            pass
    
    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date)
            query = query.filter(AdStudioScheduledPost.created_at <= to_dt)
        except:
            pass
    
    posts = query.order_by(AdStudioScheduledPost.created_at.desc()).limit(200).all()
    
    result = []
    for post in posts:
        # Join với asset để lấy thumbnail nếu có
        asset = None
        if post.asset_id:
            asset = db.query(AdStudioAsset).filter(
                AdStudioAsset.id == post.asset_id
            ).first()
        
        result.append({
            "id": post.id,
            "caption": post.caption,
            "channels": ["facebook"],  # Hardcode cho đơn giản
            "scheduleTime": post.schedule_time.isoformat() if post.schedule_time else None,
            "status": post.status,
            "creatorName": "User",  # TODO: join với user table
            "thumbnailUrl": asset.thumbnail_url if asset else "",
            "pageIds": post.page_ids,
            "language": post.language,
            "ctaText": post.cta_text,
            "targetUrl": post.target_url,
        })
    
    return {"items": result}


@api_router.get("/ad-studio/summary")
def get_ad_studio_summary(
    range: str = "7d",
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Lấy summary stats cho Dashboard
    NOTE: AdStudio
    
    Args:
        range: 7d | 30d
    """
    # NOTE: AdStudio
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Calculate date range
    if range == "30d":
        from_date = datetime.utcnow() - timedelta(days=30)
    else:
        from_date = datetime.utcnow() - timedelta(days=7)
    
    # Count posts by status
    total_posts = db.query(AdStudioScheduledPost).filter(
        AdStudioScheduledPost.created_at >= from_date
    ).count()
    
    posted_count = db.query(AdStudioScheduledPost).filter(
        AdStudioScheduledPost.created_at >= from_date,
        AdStudioScheduledPost.status == "PUBLISHED"
    ).count()
    
    scheduled_count = db.query(AdStudioScheduledPost).filter(
        AdStudioScheduledPost.created_at >= from_date,
        AdStudioScheduledPost.status == "SCHEDULED"
    ).count()
    
    draft_count = db.query(AdStudioScheduledPost).filter(
        AdStudioScheduledPost.created_at >= from_date,
        AdStudioScheduledPost.status == "DRAFT"
    ).count()
    
    failed_count = db.query(AdStudioScheduledPost).filter(
        AdStudioScheduledPost.created_at >= from_date,
        AdStudioScheduledPost.status == "FAILED"
    ).count()
    
    return {
        "totalPosts": total_posts,
        "publishedPosts": posted_count,
        "scheduledPosts": scheduled_count,
        "draftPosts": draft_count,
        "failedPosts": failed_count,
    }


@api_router.patch("/ad-studio/posts/{post_id}/cancel")
def cancel_ad_studio_post(
    post_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Huỷ bài đăng đã lên lịch
    NOTE: AdStudio
    """
    # NOTE: AdStudio
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    post = db.query(AdStudioScheduledPost).filter(
        AdStudioScheduledPost.id == post_id
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.status == "PUBLISHED":
        raise HTTPException(status_code=400, detail="Cannot cancel published post")
    
    post.status = "CANCELLED"
    post.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"ok": True, "message": "Post cancelled successfully"}
