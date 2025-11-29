"""
Pydantic Schemas for Channel Management
Validation and serialization for Channel, ChannelGroup, PostingSettings, AutoCommentTemplate
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== CHANNEL SCHEMAS ====================

class ChannelBase(BaseModel):
    """Base schema for Channel"""
    platform: str = Field(..., description="Platform: facebook, tiktok, instagram, youtube")
    page_id: str = Field(..., description="Platform-specific ID (e.g., Facebook Page ID)")
    page_name: str = Field(..., description="Display name")
    page_username: Optional[str] = Field(None, description="Vanity name / handle")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    is_active: bool = Field(True, description="Active status")
    
    @validator('platform')
    def validate_platform(cls, v):
        allowed = ["facebook", "tiktok", "instagram", "youtube"]
        if v.lower() not in allowed:
            raise ValueError(f"Platform must be one of {allowed}")
        return v.lower()


class ChannelCreate(ChannelBase):
    """Schema for creating a new channel"""
    access_token: Optional[str] = Field(None, description="Access token (will be encrypted before storing)")


class ChannelUpdate(BaseModel):
    """Schema for updating a channel"""
    page_name: Optional[str] = None
    page_username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class ChannelRead(ChannelBase):
    """Schema for reading a channel"""
    id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FacebookPageImport(BaseModel):
    """Schema for importing Facebook pages from OAuth"""
    page_id: str
    name: str
    avatar: Optional[str] = None
    access_token: Optional[str] = None  # Will be encrypted before storing
    category: Optional[str] = None


# ==================== CHANNEL GROUP SCHEMAS ====================

class ChannelGroupBase(BaseModel):
    """Base schema for ChannelGroup"""
    name: str = Field(..., min_length=1, max_length=200, description="Group name")
    color_hex: Optional[str] = Field(None, description="Hex color like #22c55e")
    
    @validator('color_hex')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError("Color must start with #")
        if v and len(v) != 7:
            raise ValueError("Color must be 7 characters (e.g., #22c55e)")
        return v


class ChannelGroupCreate(ChannelGroupBase):
    """Schema for creating a new channel group"""
    channel_ids: Optional[List[str]] = Field(default_factory=list, description="Initial channel IDs to add")


class ChannelGroupUpdate(BaseModel):
    """Schema for updating a channel group"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    color_hex: Optional[str] = None
    channel_ids: Optional[List[str]] = None  # Replace all memberships
    
    @validator('color_hex')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError("Color must start with #")
        if v and len(v) != 7:
            raise ValueError("Color must be 7 characters (e.g., #22c55e)")
        return v


class ChannelGroupRead(ChannelGroupBase):
    """Schema for reading a channel group"""
    id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    channels: List[ChannelRead] = Field(default_factory=list, description="Channels in this group")
    
    class Config:
        from_attributes = True


# ==================== POSTING SETTINGS SCHEMAS ====================

class PostingSettingsBase(BaseModel):
    """Base schema for PostingSettings"""
    default_signature: Optional[str] = Field(None, description="Default signature appended to posts")
    auto_comment_enabled: bool = Field(False, description="Master switch for auto-comments")
    auto_comment_delay_seconds: Optional[int] = Field(None, ge=0, description="Delay in seconds before first auto-comment")


class PostingSettingsUpdate(PostingSettingsBase):
    """Schema for updating posting settings"""
    pass


class PostingSettingsRead(PostingSettingsBase):
    """Schema for reading posting settings"""
    id: str
    user_id: int
    channel_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== AUTO COMMENT TEMPLATE SCHEMAS ====================

class AutoCommentTemplateBase(BaseModel):
    """Base schema for AutoCommentTemplate"""
    content: str = Field(..., min_length=1, description="Comment text")
    media_url: Optional[str] = Field(None, description="Media URL to attach")
    schedule_type: str = Field("IMMEDIATE", description="IMMEDIATE, DELAYED, AFTER_X_MINUTES, CUSTOM")
    delay_minutes: Optional[int] = Field(None, ge=0, description="Delay in minutes for delayed comments")
    is_active: bool = Field(True, description="Active status")
    sort_order: int = Field(0, description="Order for display in UI")
    
    @validator('schedule_type')
    def validate_schedule_type(cls, v):
        allowed = ["IMMEDIATE", "DELAYED", "AFTER_X_MINUTES", "CUSTOM"]
        if v.upper() not in allowed:
            raise ValueError(f"Schedule type must be one of {allowed}")
        return v.upper()


class AutoCommentTemplateCreate(AutoCommentTemplateBase):
    """Schema for creating a new auto-comment template"""
    pass


class AutoCommentTemplateUpdate(BaseModel):
    """Schema for updating an auto-comment template"""
    content: Optional[str] = Field(None, min_length=1)
    media_url: Optional[str] = None
    schedule_type: Optional[str] = None
    delay_minutes: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    
    @validator('schedule_type')
    def validate_schedule_type(cls, v):
        if v:
            allowed = ["IMMEDIATE", "DELAYED", "AFTER_X_MINUTES", "CUSTOM"]
            if v.upper() not in allowed:
                raise ValueError(f"Schedule type must be one of {allowed}")
            return v.upper()
        return v


class AutoCommentTemplateRead(AutoCommentTemplateBase):
    """Schema for reading an auto-comment template"""
    id: str
    user_id: int
    channel_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== COMBINED SCHEMAS FOR POSTING SETTINGS PAGE ====================

class ChannelWithPostingSettings(BaseModel):
    """Combined schema for posting settings page - one channel with its settings and templates"""
    channel: ChannelRead
    settings: Optional[PostingSettingsRead] = None
    auto_comments: List[AutoCommentTemplateRead] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class PostingSettingsBulkUpdate(BaseModel):
    """Schema for updating posting settings + auto-comment templates in one request"""
    default_signature: Optional[str] = None
    auto_comment_enabled: bool = False
    auto_comment_delay_seconds: Optional[int] = Field(None, ge=0)
    auto_comments: List[AutoCommentTemplateCreate] = Field(default_factory=list)


class PostingSettingsBulkUpdateWithIds(BaseModel):
    """Schema for updating posting settings with template IDs (for upsert logic)"""
    default_signature: Optional[str] = None
    auto_comment_enabled: bool = False
    auto_comment_delay_seconds: Optional[int] = Field(None, ge=0)
    auto_comments: List[Dict[str, Any]] = Field(default_factory=list, description="List of templates with optional id for upsert")

