# -*- coding: utf-8 -*-
"""
User Model for Authentication
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, default="User")
    avatar = Column(String, default="default_avatar.png")
    role = Column(String, default="user")  # "admin" or "user"
    is_active = Column(Boolean, default=True)
    facebook_id = Column(String, unique=True, index=True, nullable=True)  # Facebook user ID for OAuth

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

