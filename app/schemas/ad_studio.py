"""
Ad Studio Pydantic Schemas
NOTE: added for AdStudio only
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, HttpUrl

# Type aliases
Platform = Literal["tiktok", "facebook", "other"]
Language = Literal["la", "vi", "th"]
ScheduleMode = Literal["NOW", "RANDOM_2H", "EXACT_TIME"]
ThumbnailSource = Literal["FRAME", "UPLOAD"]


class ScrapeRequest(BaseModel):
    """Request body khi frontend gửi URL để scrape"""
    url: HttpUrl
    note: Optional[str] = None


class ScrapeResponse(BaseModel):
    """
    Response từ /tiktok/scrape endpoint
    Không raise exception 500, luôn trả JSON với success flag
    """
    success: bool
    code: Literal["OK", "INVALID_URL", "UPSTREAM_ERROR", "PRIVATE_VIDEO", "UNKNOWN_ERROR"]
    message: str
    data: Optional['Asset'] = None


class Asset(BaseModel):
    """
    Schema Asset mà frontend AdStudioCard.tsx đang expect.
    Backend phải trả về đúng format này.
    """
    id: str
    platform: Platform
    sourceUrl: str
    videoUrl: str
    thumbnailUrl: str
    captionOriginal: str
    note: Optional[str] = None
    duration: Optional[int] = None
    hashtags: Optional[List[str]] = None


class SchedulePayload(BaseModel):
    """
    Payload frontend gửi khi user bấm "Lưu vào lịch đăng".
    Tương ứng với form trong Tab 2 - Step 2 của AdStudioCard.
    """
    assetId: Optional[str] = None
    sourceUrl: Optional[str] = None
    caption: str
    language: Language
    ctaText: str
    targetUrl: Optional[str] = None
    pageIds: List[str]
    scheduleMode: ScheduleMode
    scheduleTime: Optional[str] = None  # ISO datetime string
    thumbnailSource: ThumbnailSource


class ScheduleResponse(BaseModel):
    """Response sau khi schedule thành công"""
    ok: bool
    id: str
    message: Optional[str] = "Đã lưu vào lịch đăng thành công"


# Rebuild model để resolve forward references
ScrapeResponse.model_rebuild()
