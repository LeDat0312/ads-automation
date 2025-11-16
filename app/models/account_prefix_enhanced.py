# -*- coding: utf-8 -*-
"""
Enhanced models cho Account và Prefix
Thêm chi tiết thông tin, stats, và tracking
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class AccountTypeEnum(str, enum.Enum):
    """Account Types"""
    UNKNOWN = "UNKNOWN"
    E_COMMERCE = "E-COMMERCE"
    LEAD_GENERATION = "LEAD_GENERATION"
    MOBILE_APP = "MOBILE_APP"
    BRAND_AWARENESS = "BRAND_AWARENESS"


class PrefixCategoryEnum(str, enum.Enum):
    """Prefix Categories"""
    PRODUCT_LINE = "PRODUCT_LINE"
    REGION = "REGION"
    SERVICE = "SERVICE"
    CAMPAIGN_STAGE = "CAMPAIGN_STAGE"
    CUSTOMER_SEGMENT = "CUSTOMER_SEGMENT"
    OTHER = "OTHER"


class PatternTypeEnum(str, enum.Enum):
    """Pattern matching types"""
    EXACT = "EXACT"
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    REGEX = "REGEX"


# Cập nhật Account Model
class AccountEnhanced:
    """
    Enhanced Account Model
    Thêm thông tin chi tiết về tài khoản quảng cáo
    """
    
    # Hiện tại có
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    account_id = Column(String(50))
    account_name = Column(String(255))
    account_type = Column(SQLEnum(AccountTypeEnum), default=AccountTypeEnum.UNKNOWN)
    currency = Column(String(10), default="USD")
    timezone = Column(String(50), default="Asia/Ho_Chi_Minh")
    enabled = Column(Boolean, default=True)
    status = Column(String(20), default="ACTIVE")  # "ACTIVE" | "PAUSED" | "ARCHIVED"
    last_30_days_spend = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # MỚI THÊM:
    # Account Info
    account_owner = Column(String(255), nullable=True)  # Tên chủ tài khoản
    is_personal = Column(Boolean, default=False)  # Tài khoản cá nhân?
    business_name = Column(String(255), nullable=True)  # Tên doanh nghiệp
    has_2fa = Column(Boolean, default=False)  # Có 2FA không
    
    # Campaign Stats
    total_campaigns = Column(Integer, default=0)
    active_campaigns = Column(Integer, default=0)
    paused_campaigns = Column(Integer, default=0)
    archived_campaigns = Column(Integer, default=0)
    
    # Tracking
    last_synced = Column(DateTime, nullable=True)  # Lần cuối sync từ FB API
    token_last_checked = Column(DateTime, nullable=True)
    last_modified_by = Column(String(255), nullable=True)  # User nào sửa cuối cùng
    
    # Notes
    notes = Column(Text, nullable=True)  # Ghi chú về account
    
    # Metadata
    metadata = Column(String(2000), nullable=True)  # JSON string để lưu extra info


# Cập nhật Prefix Model
class PrefixEnhanced:
    """
    Enhanced Prefix Model
    Thêm pattern matching, category, color, stats
    """
    
    # Hiện tại có
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    prefix = Column(String(50))
    prefix_name = Column(String(255))
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # MỚI THÊM:
    # Basic Info
    description = Column(Text, nullable=True)  # Chi tiết mục đích
    category = Column(SQLEnum(PrefixCategoryEnum), default=PrefixCategoryEnum.OTHER)
    
    # Pattern Matching
    pattern_type = Column(SQLEnum(PatternTypeEnum), default=PatternTypeEnum.EXACT)
    pattern = Column(String(500), nullable=True)  # Regex hoặc pattern
    
    # Visualization
    color = Column(String(10), default="#667eea")  # Hex color
    icon = Column(String(50), nullable=True)  # Icon name hoặc emoji
    
    # Stats
    total_accounts_linked = Column(Integer, default=0)
    total_campaigns_matched = Column(Integer, default=0)
    
    # Tracking
    last_used = Column(DateTime, nullable=True)
    last_matched_count = Column(Integer, default=0)  # Số campaigns matched lần cuối
    
    # Testing
    test_strings = Column(Text, nullable=True)  # JSON array of test strings


# Enhanced TelegramSettings
class TelegramSettingsEnhanced:
    """
    Enhanced Telegram Bot Settings
    Thêm notification preferences, schedule, language
    """
    
    # Hiện tại có
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    telegram_bot_token_encrypted = Column(String(500))
    telegram_chat_id = Column(String(50))
    telegram_bot_status = Column(String(20), default="NOT_SET")
    telegram_bot_last_checked = Column(DateTime, nullable=True)
    
    # MỚI THÊM:
    # Bot Info
    bot_name = Column(String(255), nullable=True)  # Tên bot
    chat_name = Column(String(255), nullable=True)  # Tên group/user
    
    # Notification Preferences
    notify_on_campaign_paused = Column(Boolean, default=True)
    notify_on_campaign_resumed = Column(Boolean, default=True)
    notify_on_budget_changed = Column(Boolean, default=True)
    notify_on_low_roas = Column(Boolean, default=True)
    notify_on_daily_summary = Column(Boolean, default=False)
    notify_on_rule_executed = Column(Boolean, default=True)
    
    # Schedule
    daily_summary_time = Column(String(10), default="09:00")  # Format: "HH:MM"
    quiet_hours_start = Column(String(10), default="22:00")  # Không gửi tin từ
    quiet_hours_end = Column(String(10), default="08:00")    # Đến
    
    # Language
    language = Column(String(10), default="vi")  # "vi" | "en"
    
    # Stats
    total_messages_sent = Column(Integer, default=0)
    last_message_sent = Column(DateTime, nullable=True)
    last_message_status = Column(String(20), nullable=True)  # "SUCCESS" | "FAILED"


# Enhanced Facebook Token
class FacebookTokenEnhanced:
    """
    Enhanced Facebook Token Info
    Thêm permission details, expiry, owner info
    """
    
    # Cơ bản
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    facebook_token_encrypted = Column(String(1000))
    token_status = Column(String(20), default="NOT_CHECKED")  # "VALID" | "EXPIRED" | "REVOKED"
    token_last_checked = Column(DateTime, nullable=True)
    
    # MỚI THÊM:
    # Token Owner Info
    token_owner_name = Column(String(255), nullable=True)  # Tên người tạo token
    token_owner_id = Column(String(50), nullable=True)  # FB ID của owner
    
    # Token Timeline
    token_created_at = Column(DateTime, nullable=True)  # Khi token được tạo
    token_expires_at = Column(DateTime, nullable=True)  # Ngày hết hạn
    
    # Permissions
    permissions = Column(Text, nullable=True)  # JSON string
    required_permissions = Column(Text, nullable=True)  # JSON string
    missing_permissions = Column(Text, nullable=True)  # JSON string
    
    # Account Access
    accessible_accounts_count = Column(Integer, default=0)
    total_accounts_available = Column(Integer, default=0)
    
    # Activity
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)

