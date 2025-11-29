"""
Channel Management Models - Generic platform support
Quản lý kênh đa nền tảng (Facebook, TikTok, Instagram, YouTube)

NOTE: Separate from existing channel.py models for backward compatibility
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
import enum


class PlatformType(enum.Enum):
    """Supported social media platforms"""
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"


class ScheduleType(enum.Enum):
    """Auto-comment schedule types"""
    IMMEDIATE = "IMMEDIATE"
    DELAYED = "DELAYED"
    AFTER_X_MINUTES = "AFTER_X_MINUTES"
    CUSTOM = "CUSTOM"


class Channel(Base):
    """
    Represents a connected social channel (Facebook Page, TikTok account, etc.)
    Generic model that supports multiple platforms
    """
    __tablename__ = "channels"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Platform information
    platform = Column(String, nullable=False, index=True)  # "facebook", "tiktok", etc.
    
    # Platform-specific identifiers
    page_id = Column(String, nullable=False, index=True)  # Facebook Page ID, TikTok username, etc.
    page_name = Column(String, nullable=False)  # Display name
    page_username = Column(Text, nullable=True)  # Vanity name / handle (e.g., @username)
    avatar_url = Column(Text, nullable=True)  # Profile picture URL
    access_token_encrypted = Column(Text, nullable=True)  # Encrypted platform token
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    group_memberships = relationship("ChannelGroupMembership", back_populates="channel", cascade="all, delete-orphan")
    posting_settings = relationship("PostingSettings", back_populates="channel", uselist=False, cascade="all, delete-orphan")
    auto_comment_templates = relationship("AutoCommentTemplate", back_populates="channel", cascade="all, delete-orphan")
    
    # Unique constraint: one channel per user/platform/page_id combination
    __table_args__ = (
        UniqueConstraint('user_id', 'platform', 'page_id', name='uq_user_platform_page'),
        Index('ix_channels_user_platform', 'user_id', 'platform'),
    )
    
    def __repr__(self):
        return f"<Channel(id={self.id}, platform={self.platform}, page_id={self.page_id}, name={self.page_name})>"


class ChannelGroup(Base):
    """
    Logical group of channels (e.g., "Phun Xăm", "Nâng Mũi")
    Used for organizing channels in the UI
    """
    __tablename__ = "channel_groups"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String, nullable=False)
    color_hex = Column(String, nullable=True)  # Hex color like "#22c55e"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    memberships = relationship("ChannelGroupMembership", back_populates="group", cascade="all, delete-orphan")
    
    # Unique constraint: one group name per user
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_group_name'),
    )
    
    def __repr__(self):
        return f"<ChannelGroup(id={self.id}, name={self.name}, color={self.color_hex})>"


class ChannelGroupMembership(Base):
    """
    Many-to-many relationship between Channel and ChannelGroup
    """
    __tablename__ = "channel_group_memberships"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("channel_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_id = Column(String, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    group = relationship("ChannelGroup", back_populates="memberships")
    channel = relationship("Channel", back_populates="group_memberships")
    
    # Unique constraint: one membership per group/channel pair
    __table_args__ = (
        UniqueConstraint('group_id', 'channel_id', name='uq_group_channel'),
    )
    
    def __repr__(self):
        return f"<ChannelGroupMembership(id={self.id}, group_id={self.group_id}, channel_id={self.channel_id})>"


class PostingSettings(Base):
    """
    Per-channel posting settings: default signature & auto-comment master switch
    One settings row per channel
    """
    __tablename__ = "posting_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_id = Column(String, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Settings
    default_signature = Column(Text, nullable=True)  # Appended at the end of post content
    auto_comment_enabled = Column(Boolean, default=False, nullable=False)
    auto_comment_delay_seconds = Column(Integer, nullable=True)  # Delay for first auto comment (e.g., 60)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    channel = relationship("Channel", back_populates="posting_settings")
    
    def __repr__(self):
        return f"<PostingSettings(id={self.id}, channel_id={self.channel_id}, auto_comment_enabled={self.auto_comment_enabled})>"


class AutoCommentTemplate(Base):
    """
    A "bulk comment" template used after posts are published
    Templates are reusable comment definitions per channel
    """
    __tablename__ = "auto_comment_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_id = Column(String, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Content
    content = Column(Text, nullable=False)  # Comment text (can include placeholders later)
    media_url = Column(Text, nullable=True)  # URL to image/video to attach
    
    # Schedule
    schedule_type = Column(String, nullable=False, default="IMMEDIATE")  # "IMMEDIATE", "DELAYED", "AFTER_X_MINUTES", "CUSTOM"
    delay_minutes = Column(Integer, nullable=True)  # For delayed comments
    
    # Status & ordering
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)  # For ordering templates in UI
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    channel = relationship("Channel", back_populates="auto_comment_templates")
    
    # Index for common queries
    __table_args__ = (
        Index('ix_templates_channel_active', 'channel_id', 'is_active', 'sort_order'),
    )
    
    def __repr__(self):
        return f"<AutoCommentTemplate(id={self.id}, channel_id={self.channel_id}, schedule_type={self.schedule_type})>"

