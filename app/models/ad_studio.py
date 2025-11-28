"""
Ad Studio SQLAlchemy Models
NOTE: added for AdStudio only

Models cho hệ thống quản lý nội dung quảng cáo (AdStudio)
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, BigInteger
from datetime import datetime
from app.core.database import Base


class AdStudioAsset(Base):
    """
    Bảng lưu trữ assets (video + content) đã fetch từ TikTok/Facebook.
    Tương đương với type Asset trong frontend.
    """
    __tablename__ = "ad_studio_assets"
    
    # NOTE: added for AdStudio only
    id = Column(String, primary_key=True)
    platform = Column(String, nullable=False)  # 'tiktok', 'facebook', 'other'
    source_url = Column(Text, nullable=False)
    video_url = Column(Text, nullable=False)  # Apify URL (fallback)
    thumbnail_url = Column(Text, nullable=False)  # Apify URL (fallback)
    caption_original = Column(Text, nullable=False)
    note = Column(Text, nullable=True)
    
    # NOTE: AdStudio - Local media storage (after download from Apify)
    local_video_path = Column(Text, nullable=True)        # Relative path: "media/ad_studio/{id}.mp4"
    local_thumbnail_path = Column(Text, nullable=True)    # Relative path: "media/ad_studio/{id}.jpg"
    video_size_bytes = Column(BigInteger, nullable=True)  # File size for UI display
    video_mime_type = Column(String(100), nullable=True)  # e.g., "video/mp4"
    
    # Optional metadata
    duration = Column(Integer, nullable=True)  # seconds
    hashtags = Column(JSON, nullable=True)  # List[str]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdStudioScheduledPost(Base):
    """
    Bảng lưu trữ lịch đăng bài.
    Tương đương với SchedulePayload trong frontend.
    """
    __tablename__ = "ad_studio_scheduled_posts"
    
    # NOTE: added for AdStudio only
    id = Column(String, primary_key=True)
    
    # Asset reference (optional - user có thể dùng asset hoặc upload riêng)
    asset_id = Column(String, nullable=True)
    source_url = Column(Text, nullable=True)
    
    # Content
    caption = Column(Text, nullable=False)
    language = Column(String, nullable=False)  # 'la', 'vi', 'th'
    cta_text = Column(String, nullable=False)
    target_url = Column(Text, nullable=True)
    
    # Publishing config
    page_ids = Column(JSON, nullable=False)  # List[str] - danh sách fanpage IDs
    schedule_mode = Column(String, nullable=False)  # 'NOW', 'RANDOM_2H', 'EXACT_TIME'
    schedule_time = Column(DateTime, nullable=False)  # Thời gian đăng đã tính toán
    thumbnail_source = Column(String, nullable=False)  # 'FRAME', 'UPLOAD'
    
    # Status tracking
    status = Column(String, nullable=False, default="SCHEDULED")  # SCHEDULED, PUBLISHING, PUBLISHED, FAILED, CANCELLED
    error = Column(Text, nullable=True)
    
    # Facebook post tracking (sau khi đăng)
    fb_post_ids = Column(JSON, nullable=True)  # Dict[page_id, post_id]
    published_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
