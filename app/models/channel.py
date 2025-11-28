"""
Channel Management Models
Quản lý Facebook Pages, Channel Groups và Auto Comment

NOTE: Không đụng vào Ad Studio models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class FacebookPage(Base):
    """
    Bảng lưu danh sách Facebook Pages đã kết nối qua OAuth
    """
    __tablename__ = "facebook_pages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    page_id = Column(String, nullable=False, index=True)  # Facebook Page ID
    page_name = Column(String, nullable=False)
    page_avatar = Column(Text, nullable=True)  # URL to avatar
    access_token = Column(Text, nullable=False)  # Encrypted page access token
    category = Column(String, nullable=True)  # Page category
    connected_at = Column(DateTime, default=datetime.utcnow)
    enabled = Column(Boolean, default=True, index=True)
    
    # Relationships
    group_items = relationship("ChannelGroupItem", back_populates="page", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FacebookPage(id={self.id}, page_id={self.page_id}, name={self.page_name})>"


class ChannelGroup(Base):
    """
    Bảng lưu các nhóm kênh (group các fanpage lại)
    """
    __tablename__ = "channel_groups"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False, default="#3B82F6")  # Hex color
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    items = relationship("ChannelGroupItem", back_populates="group", cascade="all, delete-orphan")
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChannelGroup(id={self.id}, name={self.name}, color={self.color})>"


class ChannelGroupItem(Base):
    """
    Bảng liên kết giữa ChannelGroup và FacebookPage
    """
    __tablename__ = "channel_group_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("channel_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id = Column(String, ForeignKey("facebook_pages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relationships
    group = relationship("ChannelGroup", back_populates="items")
    page = relationship("FacebookPage", back_populates="group_items")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChannelGroupItem(id={self.id}, group_id={self.group_id}, page_id={self.page_id})>"


class AutoCommentSchedule(Base):
    """
    Bảng lưu lịch auto comment
    """
    __tablename__ = "auto_comment_schedules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    group_id = Column(String, ForeignKey("channel_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Post to comment on
    post_id = Column(String, nullable=False, index=True)  # Facebook post ID
    
    # Comment content
    comment_text = Column(Text, nullable=False)  # Multi-line comment text
    media_url = Column(Text, nullable=True)  # Optional media URL
    
    # Schedule
    scheduled_at = Column(DateTime, nullable=False, index=True)
    posted_at = Column(DateTime, nullable=True)  # When actually posted
    
    # Status
    status = Column(String, default="PENDING", index=True)  # PENDING, PROCESSING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    
    # Retry
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AutoCommentSchedule(id={self.id}, group_id={self.group_id}, status={self.status})>"

