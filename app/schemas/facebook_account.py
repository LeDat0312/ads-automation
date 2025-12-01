"""
Facebook Account Pydantic Schemas
Validation and serialization for Facebook Account (Via) management
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models.facebook_account import FacebookAccountType


class FacebookAccountBase(BaseModel):
    """Base schema for Facebook Account"""
    name: str = Field(..., min_length=1, max_length=200, description="Display name for this Via")
    token_type: FacebookAccountType = Field(default=FacebookAccountType.FANPAGE, description="Token type: fanpage, ads, or both")
    

class FacebookAccountCreate(FacebookAccountBase):
    """Schema for creating a Facebook Account"""
    access_token: str = Field(..., min_length=10, description="Facebook access token")
    facebook_user_id: Optional[str] = Field(None, description="Facebook user ID")
    facebook_user_name: Optional[str] = Field(None, description="Facebook user name")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")


class FacebookAccountUpdate(BaseModel):
    """Schema for updating a Facebook Account"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    access_token: Optional[str] = Field(None, min_length=10)
    token_type: Optional[FacebookAccountType] = None
    is_active: Optional[bool] = None
    facebook_user_id: Optional[str] = None
    facebook_user_name: Optional[str] = None
    expires_at: Optional[datetime] = None


class FacebookAccountRead(FacebookAccountBase):
    """Schema for reading a Facebook Account (without exposing full token)"""
    id: int
    user_id: int
    facebook_user_id: Optional[str] = None
    facebook_user_name: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: bool
    last_verified_at: Optional[datetime] = None
    last_error: Optional[str] = Field(None, description="Last error message from Facebook API")
    created_at: datetime
    updated_at: datetime
    
    # Masked token for display (first 10 + last 4 chars)
    access_token_preview: Optional[str] = Field(None, description="Masked token preview")
    
    class Config:
        from_attributes = True


class FacebookPageSimple(BaseModel):
    """Simple schema for Facebook Page list with permission info"""
    id: str = Field(..., description="Facebook Page ID")
    name: str = Field(..., description="Page name")
    picture_url: Optional[str] = Field(None, description="Page avatar URL")
    category: Optional[str] = Field(None, description="Page category")
    access_token: Optional[str] = Field(None, description="Page-specific access token")
    
    # Permission flags
    tasks: list[str] = Field(default_factory=list, description="Facebook Page tasks/permissions (app-level)")
    perms: list[str] = Field(default_factory=list, description="Facebook Page perms/permissions (user-level)")
    is_admin: bool = Field(default=False, description="Via có quyền Quản trị viên VÀ app có đủ quyền automation")
    can_publish: bool = Field(default=False, description="Có thể đăng bài")
    can_moderate: bool = Field(default=False, description="Có thể quản lý bình luận")
    warning_message: Optional[str] = Field(None, description="Cảnh báo nếu thiếu quyền")


class FacebookChannelFromAccount(BaseModel):
    """Schema for creating channels from saved Facebook Account"""
    facebook_account_id: int = Field(..., description="ID of saved Facebook Account (Via)")
    page_ids: list[str] = Field(..., min_items=1, description="List of Facebook Page IDs to connect")
    
    @validator('page_ids')
    def validate_page_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Phải chọn ít nhất một Fanpage")
        # Remove duplicates
        return list(set(v))


class ManualFacebookChannelCreateV2(BaseModel):
    """Schema for manually adding a Facebook channel (Version 2)"""
    page_id: str = Field(..., description="Facebook Page ID")
    facebook_account_id: Optional[int] = Field(None, description="Use token from saved account (optional)")
    page_name_override: Optional[str] = Field(None, description="Override page name if desired")
    
    @validator('page_id')
    def validate_page_id(cls, v):
        if not v or not v.strip():
            raise ValueError("ID Trang không được để trống")
        return v.strip()
