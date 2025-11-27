"""
Migration script để tạo bảng cho AdStudio và thêm Apify API key setting
NOTE: added for AdStudio only

Chạy script này để:
1. Tạo bảng ad_studio_assets
2. Tạo bảng ad_studio_scheduled_posts
3. Thêm setting apify_api_key vào system_settings (nếu chưa có)

Usage:
    python -m migrations.add_ad_studio_tables
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, init_db, get_db_session
from app.models.ad_studio import AdStudioAsset, AdStudioScheduledPost
from app.core.database import SystemSetting


def run_migration():
    """Run migration to create AdStudio tables"""
    print("🚀 Starting AdStudio migration...")
    
    # Initialize database connection
    init_db()
    
    # Create tables
    print("📦 Creating AdStudio tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
    
    # Add Apify API key setting if not exists
    print("🔑 Checking Apify API key setting...")
    db = get_db_session()
    
    try:
        existing_setting = (
            db.query(SystemSetting)
            .filter(SystemSetting.key == "apify_api_key")
            .first()
        )
        
        if not existing_setting:
            # Create placeholder setting
            new_setting = SystemSetting(
                key="apify_api_key",
                value=""  # Admin cần cấu hình tại /settings
            )
            db.add(new_setting)
            db.commit()
            print("✅ Created apify_api_key setting (empty - admin cần cấu hình tại /settings)")
        else:
            print("ℹ️  apify_api_key setting đã tồn tại")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding setting: {e}")
    finally:
        db.close()
    
    print("\n✅ Migration completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Admin cấu hình Apify API key tại /settings")
    print("   2. Hoặc thêm APIFY_DEFAULT_KEY vào file .env")
    print("   3. Test API: POST /api/tiktok/scrape với TikTok URL")


if __name__ == "__main__":
    run_migration()
