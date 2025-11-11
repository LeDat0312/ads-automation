"""
Configuration management với Pydantic Settings
Thay thế cho layCaiDatHeThong() và getSettingsSafe_() từ Google Apps Script
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os


class Settings(BaseSettings):
    """Settings class với Pydantic Settings"""
    
    # ===== Database =====
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # ===== Facebook API =====
    ACCESS_TOKEN: str = Field(..., env="ACCESS_TOKEN")
    AD_ACCOUNT_IDS: str = Field(..., env="AD_ACCOUNT_IDS")
    DATA_DATE_PRESET: str = Field(default="yesterday", env="DATA_DATE_PRESET")
    
    # ===== Telegram Bot =====
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = Field(..., env="TELEGRAM_CHAT_ID")
    TELEGRAM_AUTHORIZED_CHAT_ID: Optional[str] = Field(default=None, env="TELEGRAM_AUTHORIZED_CHAT_ID")
    TELEGRAM_WEBHOOK_SECRET: str = Field(..., env="TELEGRAM_WEBHOOK_SECRET")
    WEBHOOK_URL: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    
    # ===== Automation Settings =====
    RUN_WINDOW_START_HOUR: int = Field(default=6, env="RUN_WINDOW_START_HOUR")
    RUN_WINDOW_END_HOUR: int = Field(default=23, env="RUN_WINDOW_END_HOUR")
    DELAY_KHI_TAT_BATCH: int = Field(default=1000, env="DELAY_KHI_TAT_BATCH")
    NOTIFY_NO_VIOLATION_MINUTES: int = Field(default=30, env="NOTIFY_NO_VIOLATION_MINUTES")
    
    # ===== Server =====
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY", min_length=32)
    
    # ===== Job Queue =====
    JOB_QUEUE_WORKERS: int = Field(default=2, env="JOB_QUEUE_WORKERS")
    JOB_RATE_LIMIT_SECONDS: int = Field(default=30, env="JOB_RATE_LIMIT_SECONDS")
    JOB_MAX_ATTEMPTS: int = Field(default=3, env="JOB_MAX_ATTEMPTS")
    
    @validator('AD_ACCOUNT_IDS', pre=True)
    def parse_ad_account_ids(cls, v):
        """Parse AD_ACCOUNT_IDS từ string sang list"""
        if isinstance(v, list):
            return v
        if not v:
            return []
        
        # Hỗ trợ nhiều format: dấu phẩy, chấm phẩy, xuống dòng, khoảng trắng
        v = str(v).replace(";", ",").replace("\n", ",").replace("\r", ",").replace("\t", ",")
        v = v.replace(" ", ",")
        v = ",".join(filter(None, v.split(",")))  # Loại bỏ rỗng và trùng lặp
        
        raw_ids = [id.strip() for id in v.split(",") if id.strip()]
        
        # Tự động thêm "act_" prefix nếu thiếu
        return [
            f"act_{id}" if not id.startswith("act_") else id
            for id in raw_ids
            if len(id) > 4
        ]
    
    @property
    def ad_account_ids_list(self) -> List[str]:
        """Trả về AD_ACCOUNT_IDS dạng list"""
        if isinstance(self.AD_ACCOUNT_IDS, list):
            return self.AD_ACCOUNT_IDS
        return self.parse_ad_account_ids(self.AD_ACCOUNT_IDS)
    
    def get_settings_dict(self) -> dict:
        """Trả về dictionary của settings (tương tự như getSettingsSafe_())"""
        return {
            "ACCESS_TOKEN": self.ACCESS_TOKEN,
            "AD_ACCOUNT_IDS": self.ad_account_ids_list,
            "DATA_DATE_PRESET": self.DATA_DATE_PRESET,
            "TELEGRAM_BOT_TOKEN": self.TELEGRAM_BOT_TOKEN,
            "TELEGRAM_CHAT_ID": self.TELEGRAM_CHAT_ID,
            "TELEGRAM_AUTHORIZED_CHAT_ID": self.TELEGRAM_AUTHORIZED_CHAT_ID,
            "WEBHOOK_URL": self.WEBHOOK_URL,
            "RUN_WINDOW_START_HOUR": self.RUN_WINDOW_START_HOUR,
            "RUN_WINDOW_END_HOUR": self.RUN_WINDOW_END_HOUR,
            "DELAY_KHI_TAT_BATCH": self.DELAY_KHI_TAT_BATCH,
            "NOTIFY_NO_VIOLATION_MINUTES": self.NOTIFY_NO_VIOLATION_MINUTES,
            "DATABASE_URL": self.DATABASE_URL,
        }
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate settings và trả về (is_valid, error_message)"""
        if not self.ACCESS_TOKEN:
            return False, "ACCESS_TOKEN không được để trống"
        
        if not self.ad_account_ids_list:
            return False, "AD_ACCOUNT_IDS không được để trống"
        
        if not self.TELEGRAM_BOT_TOKEN:
            return False, "TELEGRAM_BOT_TOKEN không được để trống"
        
        if not self.TELEGRAM_CHAT_ID:
            return False, "TELEGRAM_CHAT_ID không được để trống"
        
        if len(self.SECRET_KEY) < 32:
            return False, "SECRET_KEY phải có ít nhất 32 ký tự"
        
        return True, None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings instance (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_settings_safe() -> dict:
    """Get settings as dictionary (tương tự getSettingsSafe_() từ Google Apps Script)"""
    return get_settings().get_settings_dict()


def init_db():
    """Initialize database connection"""
    from app.core.database import init_db as _init_db
    _init_db()
