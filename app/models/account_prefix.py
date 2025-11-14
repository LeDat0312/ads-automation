"""
Account and Prefix Management Models
Quản lý accounts và prefixes động thay vì hardcode
Mỗi user có accounts và prefixes riêng
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from datetime import datetime
from app.core.database import Base


class Account(Base):
    """Model cho quản lý Facebook Ad Accounts - Mỗi user có accounts riêng"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # User sở hữu account
    account_id = Column(String, nullable=False, index=True)  # act_123456789 (không unique nữa, unique per user)
    account_name = Column(String)  # Tên hiển thị
    account_type = Column(String, default="UNKNOWN")  # E-COMMERCE, LEAD_GENERATION, MOBILE_APP
    timezone = Column(String, default="Asia/Ho_Chi_Minh")  # Timezone của account
    enabled = Column(Boolean, default=True)  # Bật/tắt account
    status = Column(String, default="ACTIVE")  # ACTIVE, PAUSED, ARCHIVED
    last_30_days_spend = Column(Float, default=0.0)  # Chi tiêu 30 ngày qua (USD)
    description = Column(Text)  # Mô tả
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Note: account_id không unique globally, nhưng nên unique per user
    # Có thể thêm unique constraint sau nếu cần: UniqueConstraint('user_id', 'account_id')
    
    def __repr__(self):
        return f"<Account(id={self.id}, user_id={self.user_id}, account_id='{self.account_id}', name='{self.account_name}')>"


class Prefix(Base):
    """Model cho quản lý Prefixes - Mỗi user có prefixes riêng"""
    __tablename__ = "prefixes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # User sở hữu prefix
    prefix = Column(String, nullable=False, index=True)  # FL, PX, TL, NM, etc. (không unique nữa, unique per user)
    prefix_name = Column(String)  # Tên hiển thị (VD: "Fashion Line", "Pixel")
    enabled = Column(Boolean, default=True)  # Bật/tắt prefix
    description = Column(Text)  # Mô tả
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Prefix(id={self.id}, user_id={self.user_id}, prefix='{self.prefix}', name='{self.prefix_name}')>"


class AccountPrefix(Base):
    """Model liên kết Account với Prefix - 1 Account có thể có nhiều Prefix"""
    __tablename__ = "account_prefixes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    prefix_id = Column(Integer, ForeignKey("prefixes.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<AccountPrefix(account_id={self.account_id}, prefix_id={self.prefix_id})>"

