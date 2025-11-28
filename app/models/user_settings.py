# -*- coding: utf-8 -*-
"""
User Settings Model - Lưu cấu hình riêng cho mỗi user
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime
from app.core.database import Base


class UserSettings(Base):
    """Model cho cấu hình riêng của mỗi user"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Facebook Token (encrypted)
    facebook_token_encrypted = Column(Text)  # Token được encrypt
    token_status = Column(String, default="NOT_SET")  # NOT_SET, VALID, INVALID, EXPIRED
    token_last_checked = Column(DateTime)  # Thời gian check token lần cuối
    token_owner_name = Column(String)  # Tên của người tạo token (ví dụ: "Jr Toralba Singson Amer")
    
    # Telegram Bot Settings (encrypted)
    telegram_bot_token_encrypted = Column(Text)  # Bot Token được encrypt
    telegram_chat_id = Column(String)  # Chat ID (Group ID - số âm) để nhận thông báo
    telegram_bot_status = Column(String, default="NOT_SET")  # NOT_SET, VALID, INVALID
    telegram_bot_last_checked = Column(DateTime)  # Thời gian check bot token lần cuối
    
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, token_status='{self.token_status}')>"

