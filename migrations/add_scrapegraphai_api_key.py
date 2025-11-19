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

# Thêm project root vào PYTHONPATH và set working directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Đảm bảo working directory là project root để .env được load đúng
os.chdir(project_root)

from sqlalchemy import text, create_engine
from app.core.config import get_settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate():
    """Thêm các columns cho ScrapeGraphAI API key"""
    try:
        # Kiểm tra DATABASE_URL trước
        try:
            settings = get_settings()
            database_url = settings.DATABASE_URL
            if not database_url:
                raise ValueError("DATABASE_URL không được tìm thấy trong .env file")
            logger.info(f"✅ Đã load DATABASE_URL từ .env (length: {len(database_url)})")
        except Exception as e:
            logger.error(f"❌ Không thể load DATABASE_URL: {e}")
            logger.error(f"📁 Current working directory: {os.getcwd()}")
            logger.error(f"📁 Project root: {project_root}")
            logger.error(f"📁 .env file exists: {os.path.exists(os.path.join(project_root, '.env'))}")
            raise ValueError(f"Không thể load DATABASE_URL từ .env. Kiểm tra file .env ở {project_root}")
        
        # Tạo engine trực tiếp từ DATABASE_URL (đơn giản và đáng tin cậy hơn)
        logger.info("🔄 Đang tạo database engine trực tiếp...")
        try:
            db_engine = create_engine(database_url, pool_pre_ping=True)
            # Test connection
            with db_engine.connect() as test_conn:
                test_conn.execute(text("SELECT 1"))
            logger.info("✅ Database engine đã được tạo và test thành công")
        except Exception as e:
            logger.error(f"❌ Lỗi khi tạo database engine: {e}", exc_info=True)
            raise ValueError(f"Không thể tạo database engine. Kiểm tra DATABASE_URL và kết nối database: {e}")
        
        with db_engine.connect() as conn:
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
