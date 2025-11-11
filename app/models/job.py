"""
Job Model - Job Queue
Hàng đợi để xử lý các task nặng
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Enum
from datetime import datetime
from enum import Enum as PyEnum
from app.core.database import Base


class JobStatus(PyEnum):
    """Job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class JobPriority(PyEnum):
    """Job priority"""
    HIGH = "high"  # Lệnh nhẹ: /help, /myid
    LOW = "low"    # Lệnh nặng: /report, /statusads


class Job(Base):
    """
    Model cho job queue
    Dùng để xử lý các task nặng không đồng bộ
    """
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String, nullable=False, index=True)  # "telegram_command", "automation", etc.
    priority = Column(Enum(JobPriority), default=JobPriority.LOW, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    
    # Job data
    payload = Column(JSON, nullable=False)  # {"command": "/report", "chat_id": "123", ...}
    
    # Processing info
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    error_message = Column(Text)
    
    # Rate limiting
    chat_id = Column(String, index=True)  # Để rate limit per chat
    user_id = Column(String, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status}, priority={self.priority})>"

