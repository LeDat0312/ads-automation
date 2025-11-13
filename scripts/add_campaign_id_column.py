#!/usr/bin/env python3
"""
Script để thêm cột campaign_id vào bảng ads_metrics
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import init_db, engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_campaign_id_column():
    """Thêm cột campaign_id vào bảng ads_metrics nếu chưa có"""
    # Khởi tạo database trước
    init_db()
    
    if engine is None:
        raise ValueError("Database engine chưa được khởi tạo")
    
    try:
        with engine.begin() as conn:  # Dùng begin() để tự động commit/rollback
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
            
            # Thêm cột campaign_id (nếu chưa có)
            logger.info("📝 Đang thêm cột campaign_id vào bảng ads_metrics...")
            alter_query = text("""
                ALTER TABLE ads_metrics 
                ADD COLUMN IF NOT EXISTS campaign_id VARCHAR
            """)
            try:
                conn.execute(alter_query)
            except Exception as e:
                # Nếu lỗi do cú pháp IF NOT EXISTS không hỗ trợ, thử cách khác
                if "IF NOT EXISTS" in str(e):
                    # PostgreSQL không hỗ trợ IF NOT EXISTS trong ALTER TABLE ADD COLUMN
                    # Thử thêm trực tiếp và bỏ qua lỗi nếu đã tồn tại
                    try:
                        alter_query2 = text("""
                            ALTER TABLE ads_metrics 
                            ADD COLUMN campaign_id VARCHAR
                        """)
                        conn.execute(alter_query2)
                    except Exception as e2:
                        if "already exists" in str(e2).lower() or "duplicate" in str(e2).lower():
                            logger.info("⚠️ Cột campaign_id đã tồn tại, bỏ qua...")
                        else:
                            raise
                else:
                    raise
            
            # Thêm index cho campaign_id (nếu chưa có)
            logger.info("📝 Đang thêm index cho campaign_id...")
            index_query = text("""
                CREATE INDEX IF NOT EXISTS ix_ads_metrics_campaign_id 
                ON ads_metrics(campaign_id)
            """)
            try:
                conn.execute(index_query)
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    logger.info("⚠️ Index đã tồn tại, bỏ qua...")
                else:
                    raise
            
            logger.info("✅ Đã thêm cột campaign_id và index thành công!")
            
    except Exception as e:
        logger.error(f"❌ Lỗi khi thêm cột campaign_id: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    add_campaign_id_column()
    print("\n✅ Migration hoàn thành!")

