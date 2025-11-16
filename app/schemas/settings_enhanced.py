# -*- coding: utf-8 -*-
"""
Enhanced Schemas cho Settings API
Thêm chi tiết fields, validation, response models
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class AccountTypeEnum(str, Enum):
    UNKNOWN = "UNKNOWN"
    E_COMMERCE = "E-COMMERCE"
    LEAD_GENERATION = "LEAD_GENERATION"
    MOBILE_APP = "MOBILE_APP"
    BRAND_AWARENESS = "BRAND_AWARENESS"


class PrefixCategoryEnum(str, Enum):
    PRODUCT_LINE = "PRODUCT_LINE"
    REGION = "REGION"
    SERVICE = "SERVICE"
    CAMPAIGN_STAGE = "CAMPAIGN_STAGE"
    CUSTOMER_SEGMENT = "CUSTOMER_SEGMENT"
    OTHER = "OTHER"


class PatternTypeEnum(str, Enum):
    EXACT = "EXACT"
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    REGEX = "REGEX"


# ===== ACCOUNT SCHEMAS =====

class AccountDetailResponse(BaseModel):
    """Enhanced Account Response với chi tiết đầy đủ"""
    id: int
    account_id: str
    account_name: Optional[str]
    account_owner: Optional[str]
    is_personal: bool
    business_name: Optional[str]
    has_2fa: bool
    
    # Type & Config
    account_type: str
    currency: str
    timezone: str
    enabled: bool
    status: str
    
    # Finances
    last_30_days_spend: float
    
    # Campaign Stats
    total_campaigns: int
    active_campaigns: int
    paused_campaigns: int
    archived_campaigns: int
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_synced: Optional[datetime]
    token_last_checked: Optional[datetime]
    last_modified_by: Optional[str]
    
    # Meta
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class AccountStatsResponse(BaseModel):
    """Account stats mini card"""
    account_id: str
    account_name: Optional[str]
    status: str  # "ACTIVE" | "PAUSED"
    enabled: bool
    
    # Quick stats
    total_campaigns: int
    active_campaigns: int
    last_30_days_spend: float
    currency: str
    
    # Last activity
    last_synced: Optional[datetime]
    last_synced_ago: Optional[str]  # "2 minutes ago"


class AccountUpdate(BaseModel):
    """Update account info"""
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    account_owner: Optional[str] = None
    business_name: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    enabled: Optional[bool] = None
    status: Optional[str] = None
    has_2fa: Optional[bool] = None
    notes: Optional[str] = None


# ===== PREFIX SCHEMAS =====

class PrefixDetailResponse(BaseModel):
    """Enhanced Prefix Response"""
    id: int
    prefix: str
    prefix_name: Optional[str]
    description: Optional[str]
    category: str
    enabled: bool
    
    # Pattern
    pattern_type: str
    pattern: Optional[str]
    
    # Visualization
    color: str
    icon: Optional[str]
    
    # Stats
    total_accounts_linked: int
    total_campaigns_matched: int
    
    # Activity
    last_used: Optional[datetime]
    last_matched_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PrefixTestRequest(BaseModel):
    """Test prefix pattern"""
    test_string: str = Field(..., description="String để test pattern")
    
    @validator('test_string')
    def test_string_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Test string không được để trống')
        return v


class PrefixTestResponse(BaseModel):
    """Kết quả test prefix"""
    pattern: str
    pattern_type: str
    test_string: str
    matched: bool
    message: str


class PrefixCreate(BaseModel):
    """Tạo prefix mới"""
    prefix: str
    prefix_name: Optional[str] = None
    description: Optional[str] = None
    category: str = PrefixCategoryEnum.OTHER
    enabled: bool = True
    pattern_type: str = PatternTypeEnum.EXACT
    pattern: Optional[str] = None
    color: str = "#667eea"
    icon: Optional[str] = None


class PrefixUpdate(BaseModel):
    """Update prefix"""
    prefix_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    enabled: Optional[bool] = None
    pattern_type: Optional[str] = None
    pattern: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


# ===== TELEGRAM SCHEMAS =====

class TelegramSettingsDetailResponse(BaseModel):
    """Enhanced Telegram settings response"""
    status: str  # "NOT_SET" | "VALID" | "FAILED"
    bot_token_set: bool
    chat_id_set: bool
    
    # Bot Info
    bot_name: Optional[str]
    chat_name: Optional[str]
    chat_id: Optional[str]
    bot_token_masked: Optional[str]
    
    # Preferences
    notify_on_campaign_paused: bool = True
    notify_on_campaign_resumed: bool = True
    notify_on_budget_changed: bool = True
    notify_on_low_roas: bool = True
    notify_on_daily_summary: bool = False
    notify_on_rule_executed: bool = True
    
    # Schedule
    daily_summary_time: str
    quiet_hours_start: str
    quiet_hours_end: str
    language: str
    
    # Stats
    total_messages_sent: int
    last_message_sent: Optional[datetime]
    last_message_status: Optional[str]
    
    # Timestamps
    last_checked: Optional[str]  # Formatted string
    
    class Config:
        from_attributes = True


class TelegramSettingsUpdate(BaseModel):
    """Update Telegram settings"""
    notify_on_campaign_paused: Optional[bool] = None
    notify_on_campaign_resumed: Optional[bool] = None
    notify_on_budget_changed: Optional[bool] = None
    notify_on_low_roas: Optional[bool] = None
    notify_on_daily_summary: Optional[bool] = None
    notify_on_rule_executed: Optional[bool] = None
    daily_summary_time: Optional[str] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    language: Optional[str] = None


class TestTelegramMessageRequest(BaseModel):
    """Request để gửi test message"""
    message_type: str = "SIMPLE"  # "SIMPLE" | "SAMPLE_CAMPAIGN_PAUSED"


# ===== TOKEN SCHEMAS =====

class TokenInfoResponse(BaseModel):
    """Chi tiết token info"""
    status: str
    token_owner_name: Optional[str]
    token_owner_id: Optional[str]
    token_created_at: Optional[datetime]
    token_expires_at: Optional[datetime]
    
    # Permissions
    permissions: List[str]
    required_permissions: List[str]
    missing_permissions: List[str]
    has_all_permissions: bool
    
    # Account access
    accessible_accounts_count: int
    total_accounts_available: int
    
    # Activity
    last_used: Optional[datetime]
    usage_count: int
    last_checked: Optional[datetime]


# ===== BATCH OPERATIONS =====

class BulkToggleEnabledRequest(BaseModel):
    """Bulk enable/disable accounts"""
    account_ids: List[int]
    enabled: bool


class BulkUpdateAccountTypeRequest(BaseModel):
    """Bulk update account type"""
    account_ids: List[int]
    account_type: str


class ExportSettingsResponse(BaseModel):
    """Export settings response"""
    success: bool
    message: str
    export_date: datetime
    file_url: Optional[str]
    include_tokens: bool = False  # Không export token cho security


# ===== ERROR RESPONSES =====

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[str] = None
    code: Optional[str] = None

