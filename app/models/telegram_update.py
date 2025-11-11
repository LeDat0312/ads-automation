"""
Telegram Update Model - Idempotency
Chống xử lý lặp (duplicate processing)
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.core.database import Base


class TelegramUpdate(Base):
    """
    Model để lưu update_id từ Telegram
    Chống xử lý lặp khi Telegram retry webhook
    """
    __tablename__ = "telegram_updates"
    
    update_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True)
    user_id = Column(String, index=True)
    command = Column(String)  # Lưu command để debug
    processed_at = Column(DateTime, default=datetime.now, index=True)
    processed = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<TelegramUpdate(update_id={self.update_id}, chat_id={self.chat_id}, processed={self.processed})>"

