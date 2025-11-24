"""
Content Studio SQLAlchemy Models
Database models cho module Content Studio
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class ContentSourceType(str, enum.Enum):
    FACEBOOK_ADS_LIBRARY = "facebook_ads_library"
    FACEBOOK_POST = "facebook_post"
    TIKTOK = "tiktok"
    COLLECTION = "collection"
    MANUAL_UPLOAD = "manual_upload"


class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MediaAsset(Base):
    """Media files (images/videos)"""
    __tablename__ = "cs_media_assets"

    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    type = Column(SQLEnum(MediaType), nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # Seconds for videos
    size = Column(Integer, nullable=True)  # Bytes
    filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentSource(Base):
    """Nguồn nội dung (TikTok, Facebook, Ads Library, etc.)"""
    __tablename__ = "cs_content_sources"

    id = Column(String, primary_key=True)
    source_type = Column(SQLEnum(ContentSourceType), nullable=False)
    source_url = Column(String, nullable=True)
    source_id = Column(String, nullable=True)  # External ID (TikTok video ID, FB post ID)
    caption = Column(Text, nullable=False)
    caption_lao = Column(Text, nullable=True)
    media = Column(JSON, nullable=True)  # List of media asset IDs
    author_name = Column(String, nullable=True)
    author_avatar = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    views = Column(Integer, nullable=True)
    likes = Column(Integer, nullable=True)
    comments = Column(Integer, nullable=True)
    shares = Column(Integer, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="content_sources")


class Collection(Base):
    """Bộ sưu tập nội dung"""
    __tablename__ = "cs_collections"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    cover_image = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="collections")
    items = relationship("CollectionItem", back_populates="collection", cascade="all, delete-orphan")


class CollectionItem(Base):
    """Item trong bộ sưu tập"""
    __tablename__ = "cs_collection_items"

    id = Column(String, primary_key=True)
    collection_id = Column(String, ForeignKey("cs_collections.id"), nullable=False)
    source_id = Column(String, ForeignKey("cs_content_sources.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    collection = relationship("Collection", back_populates="items")
    source = relationship("ContentSource")


class ContentVariant(Base):
    """Phiên bản nội dung đã biên tập"""
    __tablename__ = "cs_content_variants"

    id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey("cs_content_sources.id"), nullable=False)
    title = Column(String, nullable=False)
    caption = Column(Text, nullable=False)
    caption_lao = Column(Text, nullable=False)
    hashtags = Column(JSON, nullable=True, default=list)  # List of strings
    call_to_action = Column(String, nullable=True)
    media = Column(JSON, nullable=True)  # List of media asset IDs
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source = relationship("ContentSource")
    scheduled_posts = relationship("ScheduledPost", back_populates="content_variant")


class FacebookPageCS(Base):
    """Facebook Pages for Content Studio (separate from main User model)"""
    __tablename__ = "cs_facebook_pages"

    id = Column(String, primary_key=True)  # Facebook Page ID
    name = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    followers = Column(Integer, nullable=True)
    category = Column(String, nullable=True)
    group_tag = Column(String, nullable=True)  # Nhóm fanpage
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="cs_facebook_pages")
    scheduled_posts = relationship("ScheduledPost", back_populates="page")


class ScheduledPost(Base):
    """Bài đăng đã lên lịch"""
    __tablename__ = "cs_scheduled_posts"

    id = Column(String, primary_key=True)
    content_variant_id = Column(String, ForeignKey("cs_content_variants.id"), nullable=False)
    page_id = Column(String, ForeignKey("cs_facebook_pages.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    published_at = Column(DateTime, nullable=True)
    status = Column(SQLEnum(PostStatus), nullable=False, default=PostStatus.SCHEDULED)
    error = Column(Text, nullable=True)
    fb_post_id = Column(String, nullable=True)  # Facebook post ID sau khi đăng
    fb_post_url = Column(String, nullable=True)
    reach = Column(Integer, nullable=True)
    engagement = Column(Integer, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content_variant = relationship("ContentVariant", back_populates="scheduled_posts")
    page = relationship("FacebookPageCS", back_populates="scheduled_posts")
    creator = relationship("User")


# Add relationships to User model (update in app/models/user.py)
# user.content_sources = relationship("ContentSource", back_populates="user")
# user.collections = relationship("Collection", back_populates="user")
# user.cs_facebook_pages = relationship("FacebookPageCS", back_populates="user")
