"""
Migration: Add ScrapeGraphAI API Key fields to UserSettings
Chạy script này để thêm các columns mới vào bảng user_settings

Cách chạy:
    cd ~/ads-automation
    source venv/bin/activate
    PYTHONPATH=/home/adsuser/ads-automation python migrations/add_scrapegraphai_api_key.py
"""
import sys
import os

# Thêm project root vào PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import text
from app.core.database import engine
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate():
    """Thêm các columns cho ScrapeGraphAI API key"""
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='user_settings' 
                AND column_name='scrapegraphai_api_key_encrypted'
            """))
            
            if result.fetchone():
                logger.info("✅ Columns đã tồn tại, bỏ qua migration")
                return
            
            # Add columns
            logger.info("🔄 Đang thêm columns ScrapeGraphAI API key...")
            conn.execute(text("""
                ALTER TABLE user_settings 
                ADD COLUMN IF NOT EXISTS scrapegraphai_api_key_encrypted TEXT,
                ADD COLUMN IF NOT EXISTS scrapegraphai_api_key_status VARCHAR(50) DEFAULT 'NOT_SET',
                ADD COLUMN IF NOT EXISTS scrapegraphai_api_key_last_checked TIMESTAMP
            """))
            
            conn.commit()
            logger.info("✅ Đã thêm columns ScrapeGraphAI API key thành công")
            
    except Exception as e:
        logger.error(f"❌ Lỗi khi migrate: {e}", exc_info=True)
        # Nếu lỗi do columns đã tồn tại, không raise
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            logger.info("⚠️ Columns có thể đã tồn tại, bỏ qua lỗi này")
        else:
            raise

if __name__ == "__main__":
    migrate()

