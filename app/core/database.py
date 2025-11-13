"""
Database configuration and connection
Thay thế cho Google Sheets bằng PostgreSQL
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
import os

from app.core.config import get_settings

Base = declarative_base()

# Import all models để Base.metadata có thể tạo tables
# Models được import trong init_db() để tránh circular import


# Models
class AdMetrics(Base):
    """Model cho bảng ads_metrics (thay thế cho Data_FB sheet)"""
    __tablename__ = "ads_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    adset_id = Column(String, index=True)
    ad_id = Column(String, index=True)
    ad_name = Column(String)
    adset_name = Column(String)
    campaign_name = Column(String)
    account_id = Column(String, index=True)
    prefix = Column(String, index=True)
    
    # Metrics
    spend = Column(Float, default=0.0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    results = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)
    cpa = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)
    
    # Data metrics
    gia_data = Column(Float, default=0.0)
    sdt = Column(Integer, default=0)
    gia_sdt = Column(Float, default=0.0)
    ty_le_sdt = Column(Float, default=0.0)
    
    # Status
    adset_status = Column(String, default="ACTIVE")
    effective_status = Column(String)
    
    # Date
    date = Column(DateTime, default=datetime.now, index=True)
    date_preset = Column(String)
    
    # Campaign type
    campaign_type = Column(String)  # 'ECOMMERCE', 'LEAD', 'UNKNOWN'
    campaign_objective = Column(String)  # Lưu objective từ Facebook
    
    # Additional fields for compatibility
    amount_spent = Column(Float, default=0.0)  # Alias for spend
    ket_qua = Column(Integer, default=0)  # Alias for results
    
    # E-commerce specific metrics
    purchases = Column(Integer, default=0)
    purchase_value = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    
    # Lead specific metrics
    leads = Column(Integer, default=0)
    phone_calls = Column(Integer, default=0)
    cost_per_lead = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# LogicRule model được định nghĩa trong app/models/logic_rule.py
# Import ở đây để tránh circular import
# from app.models.logic_rule import LogicRule


class SystemSetting(Base):
    """Model cho bảng system_settings (thay thế cho CaiDat sheet)"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AutomationStatus(Base):
    """Model cho automation status (enable/disable account|prefix)"""
    __tablename__ = "automation_status"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True)
    prefix = Column(String, index=True)
    enabled = Column(Boolean, default=True)
    campaign_type = Column(String)  # 'ECOMMERCE', 'LEAD', 'BOTH', 'UNKNOWN'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# RuleTemplate model được định nghĩa trong app/models/rule_template.py
# Import ở đây để tránh circular import


# Database connection
engine = None
SessionLocal = None


def init_db():
    """Initialize database connection"""
    global engine, SessionLocal
    
    # Import models để Base.metadata có thể tạo tables
    from app.models.telegram_update import TelegramUpdate
    from app.models.job import Job
    from app.models.logic_rule import LogicRule
    from app.models.account_prefix import Account, Prefix  # Import models mới
    
    settings = get_settings()
    database_url = settings.DATABASE_URL
    
    if not database_url:
        raise ValueError("DATABASE_URL không được để trống")
    
    engine = create_engine(database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session (generator for FastAPI dependency)"""
    if SessionLocal is None:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get database session (non-generator version)"""
    if SessionLocal is None:
        init_db()
    
    return SessionLocal()

