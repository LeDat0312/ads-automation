"""
Migration: Add ScrapeGraphAI API Key fields to UserSettings
Chạy script này để thêm các columns mới vào bảng user_settings
"""
from sqlalchemy import text
from app.core.database import engine
import logging

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
            conn.execute(text("""
                ALTER TABLE user_settings 
                ADD COLUMN scrapegraphai_api_key_encrypted TEXT,
                ADD COLUMN scrapegraphai_api_key_status VARCHAR(50) DEFAULT 'NOT_SET',
                ADD COLUMN scrapegraphai_api_key_last_checked TIMESTAMP
            """))
            
            conn.commit()
            logger.info("✅ Đã thêm columns ScrapeGraphAI API key thành công")
            
    except Exception as e:
        logger.error(f"❌ Lỗi khi migrate: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    migrate()

