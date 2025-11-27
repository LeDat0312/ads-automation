"""
Apify Helper - Lấy Apify API Key
NOTE: added for AdStudio only

Logic ưu tiên:
1. Đọc từ DB (SystemSetting với key = 'apify_api_key')
2. Nếu không có → fallback sang biến môi trường APIFY_DEFAULT_KEY
3. Nếu cả hai đều trống → raise HTTPException 500
"""

import os
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import SystemSetting


def get_apify_api_key(db: Session) -> str:
    """
    Lấy Apify API key theo thứ tự ưu tiên:
    1. Database (SystemSetting.key = 'APIFY_API_KEY')
    2. Environment variable (APIFY_DEFAULT_KEY)
    
    Args:
        db: Database session
        
    Returns:
        str: Apify API key
        
    Raises:
        HTTPException: Nếu không tìm thấy key ở cả DB và .env
    """
    # Priority 1: Database - NOTE: AdStudio / Apify - Use uppercase key name
    setting = (
        db.query(SystemSetting)
        .filter(SystemSetting.key == "APIFY_API_KEY")
        .first()
    )

    if setting and setting.value and setting.value.strip():
        return setting.value.strip()

    # Priority 2: Environment variable fallback
    env_key = os.getenv("APIFY_DEFAULT_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # Not found anywhere
    # NOTE: AdStudio - Return 400 instead of 500 for missing API key
    raise HTTPException(
        status_code=400,
        detail="APIFY_KEY_MISSING",
    )
