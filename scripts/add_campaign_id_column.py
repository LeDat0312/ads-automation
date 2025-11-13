#!/usr/bin/env python3
"""
Script để thêm cột campaign_id vào bảng ads_metrics
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_campaign_id_column():
    """Thêm cột campaign_id vào bảng ads_metrics nếu chưa có"""
    try:
        with engine.connect() as conn:
            # Kiểm tra xem cột đã tồn tại chưa
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'ads_metrics' 
                AND column_name = 'campaign_id'
            """)
            result = conn.execute(check_query)
            exists = result.fetchone() is not None
            
            if exists:
                logger.info("✅ Cột campaign_id đã tồn tại")
                return
            
            # Thêm cột campaign_id
            logger.info("📝 Đang thêm cột campaign_id vào bảng ads_metrics...")
            alter_query = text("""
                ALTER TABLE ads_metrics 
                ADD COLUMN campaign_id VARCHAR
            """)
            conn.execute(alter_query)
            conn.commit()
            
            # Thêm index cho campaign_id
            logger.info("📝 Đang thêm index cho campaign_id...")
            index_query = text("""
                CREATE INDEX IF NOT EXISTS ix_ads_metrics_campaign_id 
                ON ads_metrics(campaign_id)
            """)
            conn.execute(index_query)
            conn.commit()
            
            logger.info("✅ Đã thêm cột campaign_id và index thành công!")
            
    except Exception as e:
        logger.error(f"❌ Lỗi khi thêm cột campaign_id: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    add_campaign_id_column()
    print("\n✅ Migration hoàn thành!")

