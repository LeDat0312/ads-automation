"""
Migration: Add local media storage fields to AdStudioAsset
NOTE: added for AdStudio only

Add fields to store downloaded video/thumbnail locally instead of relying on Apify URLs.
This ensures we can publish to Facebook even if Apify KV store expires.
"""

import logging
from sqlalchemy import text, create_engine
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)


def get_engine():
    """Create database engine from DATABASE_URL"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    return create_engine(database_url)


def run_migration():
    """
    Add local media storage fields to ad_studio_assets table
    """
    logger.info("🚀 Adding local media fields to ad_studio_assets...")
    
    try:
        engine = get_engine()
        
        with engine.connect() as conn:
            # Add new columns for local file storage
            logger.info("Adding local_video_path column...")
            conn.execute(text(
                "ALTER TABLE ad_studio_assets "
                "ADD COLUMN IF NOT EXISTS local_video_path TEXT;"
            ))
            
            logger.info("Adding local_thumbnail_path column...")
            conn.execute(text(
                "ALTER TABLE ad_studio_assets "
                "ADD COLUMN IF NOT EXISTS local_thumbnail_path TEXT;"
            ))
            
            logger.info("Adding video_size_bytes column...")
            conn.execute(text(
                "ALTER TABLE ad_studio_assets "
                "ADD COLUMN IF NOT EXISTS video_size_bytes BIGINT;"
            ))
            
            logger.info("Adding video_mime_type column...")
            conn.execute(text(
                "ALTER TABLE ad_studio_assets "
                "ADD COLUMN IF NOT EXISTS video_mime_type VARCHAR(100);"
            ))
            
            conn.commit()
            
        logger.info("✅ Local media fields added successfully")
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print("\nAdded columns to ad_studio_assets:")
        print("  • local_video_path: TEXT")
        print("  • local_thumbnail_path: TEXT")
        print("  • video_size_bytes: BIGINT")
        print("  • video_mime_type: VARCHAR(100)")
        print("\nThese columns allow storing downloaded media locally")
        print("instead of relying on Apify KV store URLs.")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}", exc_info=True)
        print(f"\n❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migration()
