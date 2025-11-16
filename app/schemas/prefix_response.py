# -*- coding: utf-8 -*-
"""
Enhanced Prefix Response Schemas & Management
Prefix matching, pattern testing, campaign mapping
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re


class PrefixCategoryEnum(str, Enum):
    """Prefix categories"""
    PRODUCT_LINE = "PRODUCT_LINE"
    REGION = "REGION"
    SERVICE = "SERVICE"
    CAMPAIGN_STAGE = "CAMPAIGN_STAGE"
    CUSTOMER_SEGMENT = "CUSTOMER_SEGMENT"
    CHANNEL = "CHANNEL"
    OTHER = "OTHER"


class PatternTypeEnum(str, Enum):
    """Pattern matching types"""
    EXACT = "EXACT"                    # Exact match
    CONTAINS = "CONTAINS"              # Contains substring
    STARTS_WITH = "STARTS_WITH"        # Starts with
    ENDS_WITH = "ENDS_WITH"            # Ends with
    REGEX = "REGEX"                    # Regex pattern


class PatternTestResult(BaseModel):
    """Pattern test result"""
    pattern: str = Field(..., description="Pattern được test")
    pattern_type: PatternTypeEnum
    test_strings: List[str] = Field(..., description="Strings được test")
    matches: List[str] = Field(..., description="Strings match")
    non_matches: List[str] = Field(..., description="Strings không match")
    match_rate: float = Field(..., description="Tỷ lệ match (%)")
    
    class Config:
        from_attributes = True


class CampaignMatch(BaseModel):
    """Campaign matched by prefix"""
    campaign_id: str
    campaign_name: str
    account_id: str
    account_name: Optional[str]
    status: str
    spend: float
    
    class Config:
        from_attributes = True


class EnhancedPrefixResponse(BaseModel):
    """Enhanced prefix response"""
    # Basic info
    id: int
    prefix: str = Field(..., description="Prefix code (FL, PX, etc)")
    prefix_name: Optional[str] = Field(None, description="Tên hiển thị")
    enabled: bool = Field(True, description="Bật/tắt prefix")
    
    # Pattern matching
    pattern_type: PatternTypeEnum = Field(PatternTypeEnum.EXACT, description="Kiểu matching")
    pattern: Optional[str] = Field(None, description="Pattern for matching (nếu khác prefix)")
    
    # Categorization
    category: PrefixCategoryEnum = Field(PrefixCategoryEnum.OTHER, description="Phân loại prefix")
    
    # Display
    color: Optional[str] = Field(None, description="Color code (hex) cho UI")
    icon: Optional[str] = Field(None, description="Icon name")
    
    # Statistics
    total_accounts_linked: int = Field(0, description="Tổng accounts link")
    total_campaigns_matched: int = Field(0, description="Tổng campaigns match")
    active_campaigns: int = Field(0, description="Campaigns đang chạy")
    
    # Recent activity
    last_used: Optional[datetime] = Field(None, description="Lần sử dụng cuối")
    matched_campaigns: List[CampaignMatch] = Field(default_factory=list, description="Recent matched campaigns")
    
    # Configuration
    description: Optional[str] = Field(None, description="Mô tả chi tiết")
    test_strings: List[str] = Field(default_factory=list, description="Test strings for pattern")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dữ liệu khác")
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PrefixCreateRequest(BaseModel):
    """Create/Update prefix"""
    prefix: str = Field(..., min_length=1, max_length=50, description="Prefix code")
    prefix_name: Optional[str] = Field(None, description="Tên hiển thị")
    pattern_type: PatternTypeEnum = Field(PatternTypeEnum.EXACT)
    pattern: Optional[str] = Field(None, description="Custom pattern if different from prefix")
    category: PrefixCategoryEnum = Field(PrefixCategoryEnum.OTHER)
    color: Optional[str] = Field(None, description="Hex color")
    icon: Optional[str] = Field(None, description="Icon name")
    description: Optional[str] = Field(None)
    test_strings: List[str] = Field(default_factory=list)
    enabled: bool = Field(True)
    
    @validator('pattern_type')
    def validate_pattern_type(cls, v):
        """Validate pattern type"""
        if v not in [e.value for e in PatternTypeEnum]:
            raise ValueError(f"Invalid pattern_type: {v}")
        return v
    
    @validator('pattern')
    def validate_pattern(cls, v, values):
        """Validate regex pattern if needed"""
        if v and values.get('pattern_type') == PatternTypeEnum.REGEX:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {str(e)}")
        return v


class PrefixFilterRequest(BaseModel):
    """Prefix filter parameters"""
    category: Optional[str] = Field(None)
    enabled_only: bool = Field(False)
    search: Optional[str] = Field(None, description="Search by prefix or name")
    min_campaigns: Optional[int] = Field(None)
    sort_by: str = Field("updated_at", description="Sort field")
    sort_order: str = Field("desc", description="asc hoặc desc")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedPrefixResponse(BaseModel):
    """Paginated prefix response"""
    items: List[EnhancedPrefixResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PrefixBulkOperationRequest(BaseModel):
    """Bulk operation on prefixes"""
    prefix_ids: List[int] = Field(..., description="Prefix IDs")
    operation: str = Field(..., description="enable, disable, delete")
    confirm: bool = Field(False)


class PrefixMatchTestRequest(BaseModel):
    """Test prefix pattern matching"""
    pattern: str
    pattern_type: PatternTypeEnum
    test_strings: List[str]


class PrefixAutoSuggestRequest(BaseModel):
    """Auto-suggest prefixes from campaign names"""
    campaigns: List[Dict[str, str]] = Field(..., description="[{campaign_id, campaign_name}, ...]")
    min_frequency: int = Field(2, ge=1, description="Min campaigns with same prefix")
