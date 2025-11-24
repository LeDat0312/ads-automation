"""
Content Studio Pydantic Schemas
Request/Response schemas cho API
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class ContentSourceType(str, Enum):
    FACEBOOK_ADS_LIBRARY = "facebook_ads_library"
    FACEBOOK_POST = "facebook_post"
    TIKTOK = "tiktok"
    COLLECTION = "collection"
    MANUAL_UPLOAD = "manual_upload"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"


class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduleType(str, Enum):
    NOW = "now"
    FIXED = "fixed"
    RANDOM = "random"


class AiRewriteMode(str, Enum):
    TRANSLATE = "translate"
    REWRITE_SALON_STYLE = "rewrite_salon_style"
    GENERATE_VARIANTS = "generate_variants"


# ==================== BASE SCHEMAS ====================

class MediaAssetSchema(BaseModel):
    id: str
    url: str
    thumbnail_url: Optional[str] = None
    type: MediaType
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    size: Optional[int] = None
    filename: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ContentSourceSchema(BaseModel):
    id: str
    source_type: ContentSourceType
    source_url: Optional[str] = None
    source_id: Optional[str] = None
    caption: str
    caption_lao: Optional[str] = None
    media: List[MediaAssetSchema] = []
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    platform: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    fetched_at: datetime
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class CollectionSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    item_count: int = 0
    cover_image: Optional[str] = None
    is_default: bool = False
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class ContentVariantSchema(BaseModel):
    id: str
    source_id: str
    title: str
    caption: str
    caption_lao: str
    hashtags: List[str] = []
    call_to_action: Optional[str] = None
    media: List[MediaAssetSchema] = []
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacebookPageSchema(BaseModel):
    id: str
    name: str
    access_token: str
    avatar: Optional[str] = None
    followers: Optional[int] = None
    category: Optional[str] = None
    group_tag: Optional[str] = None
    is_active: bool = True
    last_sync_at: Optional[datetime] = None
    user_id: int

    class Config:
        from_attributes = True


class ScheduledPostSchema(BaseModel):
    id: str
    content_variant_id: str
    page_id: str
    scheduled_at: datetime
    published_at: Optional[datetime] = None
    status: PostStatus
    error: Optional[str] = None
    fb_post_id: Optional[str] = None
    fb_post_url: Optional[str] = None
    reach: Optional[int] = None
    engagement: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    # Populated fields
    content_variant: Optional[ContentVariantSchema] = None
    page: Optional[FacebookPageSchema] = None

    class Config:
        from_attributes = True


# ==================== REQUEST SCHEMAS ====================

class SearchContentRequest(BaseModel):
    query: Optional[str] = None
    source_type: Optional[ContentSourceType] = None
    urls: Optional[List[str]] = None
    page: int = 1
    page_size: int = 20


class FetchUrlsRequest(BaseModel):
    urls: List[str] = Field(..., min_items=1)


class CreateCollectionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class AddToCollectionRequest(BaseModel):
    source_ids: List[str] = Field(..., min_items=1)
    collection_id: Optional[str] = None


class CreateContentVariantRequest(BaseModel):
    source_id: str
    title: str = Field(..., min_length=1)
    caption: str
    caption_lao: str
    hashtags: List[str] = []
    call_to_action: Optional[str] = None


class UpdateContentVariantRequest(BaseModel):
    title: Optional[str] = None
    caption: Optional[str] = None
    caption_lao: Optional[str] = None
    hashtags: Optional[List[str]] = None
    call_to_action: Optional[str] = None
    is_active: Optional[bool] = None


class AiRewriteRequest(BaseModel):
    source_caption: str = Field(..., min_length=1)
    source_lang: str = "vi"
    target_lang: str = "lo"
    mode: AiRewriteMode
    custom_prompt: Optional[str] = None


class SchedulePostRequest(BaseModel):
    content_variant_id: str
    page_ids: List[str] = Field(..., min_items=1)
    schedule_type: ScheduleType
    fixed_time: Optional[datetime] = None
    random_range_minutes: Optional[int] = Field(default=120, ge=15, le=480)


class UpdateScheduledPostRequest(BaseModel):
    caption: Optional[str] = None
    caption_lao: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[PostStatus] = None


# ==================== RESPONSE SCHEMAS ====================

class SearchContentResponse(BaseModel):
    items: List[ContentSourceSchema]
    total: int
    page: int
    page_size: int
    has_more: bool


class AiRewriteResponse(BaseModel):
    original_caption: str
    rewritten_caption: str
    variants: Optional[List[str]] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None


class SchedulePostResponse(BaseModel):
    success: bool
    scheduled_posts: List[ScheduledPostSchema]
    errors: Optional[List[dict]] = None


class PostsListResponse(BaseModel):
    items: List[ScheduledPostSchema]
    total: int
    page: int
    page_size: int


class DashboardStatsResponse(BaseModel):
    posts_today: int
    posts_scheduled: int
    posts_published_today: int
    posts_failed_today: int


class DailyStatsSchema(BaseModel):
    date: str
    posts_count: int
    published_count: int
    failed_count: int


class Stats7DaysResponse(BaseModel):
    days: List[DailyStatsSchema]
    total: int


class UploadMediaResponse(BaseModel):
    sources: List[ContentSourceSchema]
    errors: Optional[List[dict]] = None
