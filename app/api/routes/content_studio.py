"""
Content Studio API Routes
FastAPI router cho module Content Studio
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.api.routes.auth import get_current_user_optional
from app.schemas.content_studio import *
from app.services.content_studio_service import ContentStudioService
from app.services.ai_service import AiService
from app.services.facebook_scheduler_service import FacebookSchedulerService

router = APIRouter(prefix="/api/content-studio", tags=["content-studio"])


# ==================== SEARCH & FETCH ====================

@router.post("/search", response_model=SearchContentResponse)
async def search_content(
    request: SearchContentRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Tìm kiếm nội dung từ Facebook Ads Library, TikTok, Facebook Posts
    
    TODO:
    - Implement search logic for each source type
    - Integrate with Facebook Graph API
    - Integrate with TikTok API or scraping service
    - Cache results for performance
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    result = await service.search_content(
        user_id=current_user.id,
        query=request.query,
        source_type=request.source_type,
        page=request.page,
        page_size=request.page_size
    )
    
    return result


@router.post("/fetch-urls")
async def fetch_from_urls(
    request: FetchUrlsRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Lấy nội dung từ danh sách URLs
    
    TODO:
    - Parse URLs to detect platform (TikTok, Facebook, etc.)
    - Fetch content using appropriate API/scraper
    - Extract media, caption, metadata
    - Save to database
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    items = await service.fetch_from_urls(
        user_id=current_user.id,
        urls=request.urls
    )
    
    return {"items": items}


@router.post("/upload")
async def upload_media(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Upload media từ máy tính
    
    TODO:
    - Validate file types (image/video)
    - Upload to storage (S3, local, etc.)
    - Generate thumbnails for videos
    - Create ContentSource records
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    result = await service.upload_media(
        user_id=current_user.id,
        files=files
    )
    
    return result


# ==================== COLLECTIONS ====================

@router.get("/collections")
async def get_collections(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách bộ sưu tập của user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    items = service.get_user_collections(current_user.id)
    
    return {"items": items}


@router.post("/collections", response_model=CollectionSchema)
async def create_collection(
    request: CreateCollectionRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Tạo bộ sưu tập mới"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    collection = service.create_collection(
        user_id=current_user.id,
        name=request.name,
        description=request.description
    )
    
    return collection


@router.post("/collections/add-items")
async def add_to_collection(
    request: AddToCollectionRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Thêm items vào bộ sưu tập"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    service.add_to_collection(
        user_id=current_user.id,
        collection_id=request.collection_id,
        source_ids=request.source_ids
    )
    
    return {"success": True}


# ==================== CONTENT VARIANTS ====================

@router.get("/variants")
async def get_content_variants(
    source_id: Optional[str] = None,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách content variants"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    items = service.get_content_variants(
        user_id=current_user.id,
        source_id=source_id
    )
    
    return {"items": items}


@router.post("/variants", response_model=ContentVariantSchema)
async def create_content_variant(
    request: CreateContentVariantRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Tạo phiên bản nội dung mới"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    variant = service.create_content_variant(
        user_id=current_user.id,
        data=request
    )
    
    return variant


@router.patch("/variants/{variant_id}", response_model=ContentVariantSchema)
async def update_content_variant(
    variant_id: str,
    request: UpdateContentVariantRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Cập nhật content variant"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    variant = service.update_content_variant(
        user_id=current_user.id,
        variant_id=variant_id,
        data=request
    )
    
    return variant


# ==================== AI SERVICES ====================

@router.post("/ai/rewrite-caption", response_model=AiRewriteResponse)
async def rewrite_caption(
    request: AiRewriteRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Dịch và viết lại caption bằng AI (Gemini/ChatGPT)
    
    TODO:
    - Integrate with Google Gemini API
    - Integrate with OpenAI ChatGPT API
    - Implement different rewrite modes:
      * TRANSLATE: Dịch sang tiếng Lào giữ nguyên ý
      * REWRITE_SALON_STYLE: Viết lại theo phong cách thẩm mỹ viện
      * GENERATE_VARIANTS: Tạo 3 phiên bản khác nhau
    - Track token usage for billing
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    ai_service = AiService()
    result = await ai_service.rewrite_caption(
        source_caption=request.source_caption,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        mode=request.mode,
        custom_prompt=request.custom_prompt
    )
    
    return result


# ==================== FACEBOOK PAGES ====================

@router.get("/facebook/pages")
async def get_facebook_pages(
    group_tag: Optional[str] = None,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách Facebook pages của user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    pages = service.get_facebook_pages(
        user_id=current_user.id,
        group_tag=group_tag
    )
    
    return {"items": pages}


@router.post("/facebook/pages/sync")
async def sync_facebook_pages(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Đồng bộ danh sách pages từ Facebook
    
    TODO:
    - Call Facebook Graph API /me/accounts
    - Update page info (name, followers, avatar)
    - Mark inactive pages
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = ContentStudioService(db)
    pages = await service.sync_facebook_pages(current_user.id)
    
    return {"items": pages}


# ==================== SCHEDULER ====================

@router.post("/scheduler/schedule-post", response_model=SchedulePostResponse)
async def schedule_post(
    request: SchedulePostRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Lên lịch đăng bài
    
    TODO:
    - Create ScheduledPost records for each page
    - Calculate schedule time based on type (now/fixed/random)
    - Queue posts for background worker
    - Return success/error for each page
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    scheduler_service = FacebookSchedulerService(db)
    result = await scheduler_service.schedule_posts(
        user_id=current_user.id,
        content_variant_id=request.content_variant_id,
        page_ids=request.page_ids,
        schedule_type=request.schedule_type,
        fixed_time=request.fixed_time,
        random_range_minutes=request.random_range_minutes
    )
    
    return result


@router.get("/scheduler/posts", response_model=PostsListResponse)
async def get_scheduled_posts(
    status: Optional[PostStatus] = None,
    page_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách bài đăng đã lên lịch"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    scheduler_service = FacebookSchedulerService(db)
    result = scheduler_service.get_scheduled_posts(
        user_id=current_user.id,
        status=status,
        page_id=page_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )
    
    return result


@router.patch("/scheduler/posts/{post_id}", response_model=ScheduledPostSchema)
async def update_scheduled_post(
    post_id: str,
    request: UpdateScheduledPostRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Cập nhật bài đăng đã lên lịch"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    scheduler_service = FacebookSchedulerService(db)
    post = scheduler_service.update_scheduled_post(
        user_id=current_user.id,
        post_id=post_id,
        data=request
    )
    
    return post


@router.delete("/scheduler/posts/{post_id}")
async def delete_scheduled_post(
    post_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa bài đăng đã lên lịch"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    scheduler_service = FacebookSchedulerService(db)
    scheduler_service.delete_scheduled_post(
        user_id=current_user.id,
        post_id=post_id
    )
    
    return {"success": True}


@router.post("/scheduler/posts/{post_id}/publish-now", response_model=ScheduledPostSchema)
async def publish_post_now(
    post_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Đăng bài ngay lập tức
    
    TODO:
    - Update scheduled_at to now
    - Trigger immediate publishing
    - Return updated post
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    scheduler_service = FacebookSchedulerService(db)
    post = await scheduler_service.publish_now(
        user_id=current_user.id,
        post_id=post_id
    )
    
    return post


# ==================== STATS & DASHBOARD ====================

@router.get("/scheduler/stats/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy stats cho dashboard"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    scheduler_service = FacebookSchedulerService(db)
    stats = scheduler_service.get_dashboard_stats(current_user.id)
    
    return stats


@router.get("/scheduler/stats/7d", response_model=Stats7DaysResponse)
async def get_7days_stats(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy stats 7 ngày gần nhất"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    scheduler_service = FacebookSchedulerService(db)
    stats = scheduler_service.get_7days_stats(current_user.id)
    
    return stats
