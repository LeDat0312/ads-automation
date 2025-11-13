"""
Logic 7 Days Config Model
Cấu hình logic lọc 7 ngày theo từng account và prefix
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from app.core.database import Base


class Logic7DaysConfig(Base):
    """
    Model cho cấu hình logic lọc 7 ngày
    Mỗi account + prefix có thể có config riêng
    """
    __tablename__ = "logic_7days_config"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Account & Prefix
    account_id = Column(String, index=True, nullable=True)  # null = áp dụng cho tất cả accounts
    prefix = Column(String, index=True, nullable=True)  # null = áp dụng cho tất cả prefixes
    
    # Ngưỡng chi tiêu (VND)
    spend_threshold = Column(Float, default=100000.0)  # Mặc định 100,000₫
    
    # Ngưỡng giá DATA (VND) - từ logic 2 hoặc config riêng
    gia_data_threshold = Column(Float, default=0.0)  # 0 = dùng từ SL_2_GIA_DATA
    
    # Ngưỡng cost_per_purchase để giữ lại (VND)
    cost_per_purchase_keep_threshold = Column(Float, default=150000.0)  # Mặc định 150,000₫
    # Nếu cost_per_purchase < threshold này thì giữ lại dù gia_data > ngưỡng
    
    # Số ngày để lọc (mặc định 7)
    days = Column(Integer, default=7)
    
    # Status
    enabled = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Logic7DaysConfig(id={self.id}, account_id={self.account_id}, prefix={self.prefix}, enabled={self.enabled})>"

