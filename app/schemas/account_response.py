# -*- coding: utf-8 -*-
"""
Enhanced Account Response Schemas
Trả về thêm thông tin chi tiết cho settings page
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AccountStatusEnum(str, Enum):
    """Account status"""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"


class AccountHealthEnum(str, Enum):
    """Account health status"""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class AccountSpendingTrend(BaseModel):
    """Spending trend data"""
    spend_7days: float = Field(0.0, description="Chi tiêu 7 ngày")
    spend_30days: float = Field(0.0, description="Chi tiêu 30 ngày")
    avg_daily_spend: float = Field(0.0, description="Chi tiêu trung bình mỗi ngày")
    trend_direction: str = Field("STABLE", description="UP, DOWN, STABLE")
    
    class Config:
        from_attributes = True


class AccountCampaignStats(BaseModel):
    """Campaign statistics"""
    total_campaigns: int = Field(0, description="Tổng campaigns")
    active_campaigns: int = Field(0, description="Campaigns đang chạy")
    paused_campaigns: int = Field(0, description="Campaigns tạm dừng")
    archived_campaigns: int = Field(0, description="Campaigns lưu trữ")
    
    class Config:
        from_attributes = True


class AccountHealthStatus(BaseModel):
    """Account health indicator"""
    status: AccountHealthEnum = Field(AccountHealthEnum.UNKNOWN, description="HEALTHY, WARNING, CRITICAL")
    issues: List[str] = Field(default_factory=list, description="Danh sách issues (nếu có)")
    last_check: Optional[datetime] = Field(None, description="Lần kiểm tra cuối")
    
    class Config:
        from_attributes = True


class EnhancedAccountResponse(BaseModel):
    """Enhanced account response - hiển thị trên settings page"""
    # Basic info
    id: int
    account_id: str = Field(..., description="Facebook account ID (act_xxx)")
    account_name: Optional[str] = Field(None, description="Tên tài khoản")
    account_type: str = Field("UNKNOWN", description="E-COMMERCE, LEAD_GENERATION, MOBILE_APP, BRAND_AWARENESS")
    
    # Status & Config
    status: AccountStatusEnum = Field(AccountStatusEnum.ACTIVE)
    enabled: bool = Field(True, description="Bật/tắt logic tự động")
    
    # Location & Currency
    timezone: str = Field("Asia/Ho_Chi_Minh", description="Timezone của account")
    currency: str = Field("USD", description="Đơn vị tiền tệ")
    
    # Spending Info
    last_30_days_spend: float = Field(0.0, description="Chi tiêu 30 ngày")
    spending_trend: AccountSpendingTrend = Field(default_factory=AccountSpendingTrend)
    
    # Campaign Stats
    campaign_stats: AccountCampaignStats = Field(default_factory=AccountCampaignStats)
    
    # Health Status
    health: AccountHealthStatus = Field(default_factory=AccountHealthStatus)
    
    # Sync & Token Info
    last_synced: Optional[datetime] = Field(None, description="Lần đồng bộ cuối")
    token_valid: bool = Field(True, description="Token Facebook còn hợp lệ?")
    token_expires_at: Optional[datetime] = Field(None, description="Ngày hết hạn token")
    
    # Management
    last_modified_by: Optional[str] = Field(None, description="User chỉnh sửa cuối")
    last_modified_at: Optional[datetime] = Field(None, description="Lần chỉnh sửa cuối")
    
    # Prefixes linked
    linked_prefixes: List[str] = Field(default_factory=list, description="Danh sách prefixes")
    
    # Metadata
    notes: Optional[str] = Field(None, description="Ghi chú")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dữ liệu khác")
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AccountFilterRequest(BaseModel):
    """Account filter parameters"""
    status: Optional[str] = Field(None, description="Filter by status")
    account_type: Optional[str] = Field(None, description="Filter by type")
    enabled_only: bool = Field(False, description="Chỉ accounts đang bật?")
    health_status: Optional[str] = Field(None, description="Filter by health")
    search: Optional[str] = Field(None, description="Tìm kiếm theo name/id")
    min_spend: Optional[float] = Field(None, description="Spending tối thiểu 30 ngày")
    max_spend: Optional[float] = Field(None, description="Spending tối đa 30 ngày")
    sort_by: str = Field("updated_at", description="Sort field: spend, updated_at, created_at, name")
    sort_order: str = Field("desc", description="asc hoặc desc")
    page: int = Field(1, ge=1, description="Trang")
    page_size: int = Field(20, ge=1, le=100, description="Kích thước trang")


class PaginatedAccountResponse(BaseModel):
    """Paginated account response"""
    items: List[EnhancedAccountResponse]
    total: int = Field(..., description="Tổng số accounts")
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True


class AccountBulkUpdateRequest(BaseModel):
    """Bulk update accounts"""
    account_ids: List[int] = Field(..., description="Danh sách account IDs")
    updates: Dict[str, Any] = Field(..., description="Fields to update: enabled, timezone, currency, account_type")


class AccountBulkDeleteRequest(BaseModel):
    """Bulk delete accounts"""
    account_ids: List[int] = Field(..., description="Danh sách account IDs cần xóa")
    confirm: bool = Field(False, description="Xác nhận xóa")
