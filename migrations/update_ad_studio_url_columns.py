"""
Migration: Update AdStudio URL columns to TEXT
NOTE: added for AdStudio only

Fix issue: video_url and thumbnail_url being truncated due to VARCHAR length limit.
Change columns to TEXT to support long Apify URLs.
"""

import logging
from sqlalchemy import text
from app.core.database import engine

logger = logging.getLogger(__name__)


def run_migration():
    """
    Migrate ad_studio_assets columns to TEXT type for long URLs
    """
    logger.info("🚀 Starting AdStudio URL columns migration...")
    
    try:
        with engine.connect() as conn:
            # PostgreSQL syntax - change columns to TEXT type
            logger.info("Altering video_url column to TEXT...")
            conn.execute(text(
                "ALTER TABLE ad_studio_assets ALTER COLUMN video_url TYPE TEXT;"
            ))
            
            logger.info("Altering thumbnail_url column to TEXT...")
            conn.execute(text(
                "ALTER TABLE ad_studio_assets ALTER COLUMN thumbnail_url TYPE TEXT;"
            ))
            
            logger.info("Altering source_url column to TEXT...")
            conn.execute(text(
                "ALTER TABLE ad_studio_assets ALTER COLUMN source_url TYPE TEXT;"
            ))
            
            conn.commit()
            
        logger.info("✅ AdStudio URL columns successfully migrated to TEXT.")
        print("\n✅ Migration completed successfully!")
        print("   - video_url: VARCHAR → TEXT")
        print("   - thumbnail_url: VARCHAR → TEXT")
        print("   - source_url: VARCHAR → TEXT")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}", exc_info=True)
        print(f"\n❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migration()
