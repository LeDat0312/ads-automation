"""
Account and Prefix Management Models
Quản lý accounts và prefixes động thay vì hardcode
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from app.core.database import Base


class Account(Base):
    """Model cho quản lý Facebook Ad Accounts"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, unique=True, nullable=False, index=True)  # act_123456789
    account_name = Column(String)  # Tên hiển thị
    enabled = Column(Boolean, default=True)  # Bật/tắt account
    description = Column(Text)  # Mô tả
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Account(id={self.id}, account_id='{self.account_id}', name='{self.account_name}')>"


class Prefix(Base):
    """Model cho quản lý Prefixes"""
    __tablename__ = "prefixes"
    
    id = Column(Integer, primary_key=True, index=True)
    prefix = Column(String, unique=True, nullable=False, index=True)  # FL, PX, TL, NM, etc.
    prefix_name = Column(String)  # Tên hiển thị (VD: "Fashion Line", "Pixel")
    enabled = Column(Boolean, default=True)  # Bật/tắt prefix
    description = Column(Text)  # Mô tả
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Prefix(id={self.id}, prefix='{self.prefix}', name='{self.prefix_name}')>"

