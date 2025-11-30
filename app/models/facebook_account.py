"""
Facebook Account Model
Stores Facebook access tokens (Via) for managing pages and ads
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class FacebookAccountType(str, enum.Enum):
    """Facebook account token type"""
    FANPAGE = "fanpage"  # For managing pages, comments, inbox
    ADS = "ads"  # For reading/optimizing ads
    BOTH = "both"  # Can do both


class FacebookAccount(Base):
    """
    Facebook Account (Via) storage
    Stores access tokens used for managing pages and ads
    """
    __tablename__ = "facebook_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Owner of this account
    
    # Account info
    name = Column(String(200), nullable=False)  # Display name (e.g., "Via chính - Quản lý Pages")
    access_token = Column(Text, nullable=False)  # Facebook access token (should be encrypted)
    token_type = Column(
        SQLEnum(FacebookAccountType, native_enum=False),
        nullable=False,
        default=FacebookAccountType.FANPAGE,
        index=True
    )
    
    # Token metadata
    facebook_user_id = Column(String(100), nullable=True)  # FB user ID who owns this token
    facebook_user_name = Column(String(200), nullable=True)  # FB user name
    expires_at = Column(DateTime, nullable=True)  # Token expiration (if known)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_verified_at = Column(DateTime, nullable=True)  # Last time token was verified
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<FacebookAccount(id={self.id}, name={self.name}, type={self.token_type})>"
