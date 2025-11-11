"""
LogicRule Model - LINH HOẠT với JSON fields
Thay thế cho LogicRules sheet với cấu trúc linh hoạt hơn
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from datetime import datetime
from app.core.database import Base


class LogicRule(Base):
    """
    Model cho logic rules - LINH HOẠT với JSON fields
    
    Thay thế cho LogicRules sheet với:
    - Conditions là JSON (dễ thêm/sửa)
    - Account IDs và Prefixes là arrays
    - Schedule và Filters là JSON
    """
    __tablename__ = "logic_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)  # "Increase budget", "Decrease budget"
    folder = Column(String, default="General", index=True)  # "Scale Ad Sets", "General"
    
    # Account & Prefix (có thể nhiều)
    account_ids = Column(JSON, default=list)  # ["act_123", "act_456"] hoặc [] = all accounts
    prefixes = Column(JSON, default=list)     # ["FL", "PX"] hoặc [null] = all prefixes
    
    # Conditions (LINH HOẠT - JSON)
    # Format:
    # {
    #   "AND": [
    #     {"metric": "spend", "timeframe": "today", "operator": ">", "value": 300},
    #     {"metric": "cpl", "timeframe": "today", "operator": "<", "value": {"multiplier": 0.8, "base_metric": "cpl", "base_timeframe": "last_3days"}}
    #   ],
    #   "OR": [...]
    # }
    conditions = Column(JSON, nullable=False)
    
    # Action
    action = Column(String, nullable=False)  # "INCREASE_BUDGET", "DECREASE_BUDGET", "PAUSE", "RESUME"
    action_params = Column(JSON, default=dict)  # {"percent": 20, "frequency": "once_a_day"}
    
    # Schedule
    # Format:
    # {
    #   "type": "interval",  # "interval" | "specific"
    #   "interval_minutes": 60,
    #   "specific_times": ["09:00", "14:00"],
    #   "timezone": "Asia/Ho_Chi_Minh"
    # }
    schedule = Column(JSON, default=dict)
    
    # Filters
    # Format:
    # {
    #   "adset_status": ["ACTIVE"],
    #   "campaign_types": ["ECOMMERCE", "LEAD"],
    #   "min_spend": 1000
    # }
    filters = Column(JSON, default=dict)
    
    # Status
    enabled = Column(Boolean, default=True, index=True)
    status = Column(String, default="DRAFT", index=True)  # "DRAFT", "LIVE", "PAUSED"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String)
    version = Column(Integer, default=1)
    
    # Description (optional)
    description = Column(Text)
    
    def __repr__(self):
        return f"<LogicRule(id={self.id}, name='{self.name}', folder='{self.folder}', enabled={self.enabled})>"

