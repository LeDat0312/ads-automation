"""
Rule Template Model
Cho phép tạo và quản lý rule templates tương tự Madgicx
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from datetime import datetime
from app.core.database import Base


class RuleTemplate(Base):
    """Model cho bảng rule_templates"""
    __tablename__ = "rule_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    campaign_type = Column(String)  # 'ECOMMERCE', 'LEAD', 'BOTH', 'UNKNOWN'
    
    # Template configuration (JSON)
    template_config = Column(JSON)  # {
    #   "conditions": {...},
    #   "action": "PAUSE" | "RESUME",
    #   "logic_type": "logic1" | "logic2" | "logic3"
    # }
    
    # Metadata
    enabled = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)  # Số lần được sử dụng
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

