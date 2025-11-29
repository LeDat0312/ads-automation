"""
Migration script để tạo bảng cho Channel Management (new structure)
- channels: Generic channels (facebook, tiktok, instagram, youtube)
- channel_groups: Groups of channels
- channel_group_memberships: Many-to-many between channels and groups
- posting_settings: Per-channel posting settings
- auto_comment_templates: Reusable comment templates

Usage:
    python -m migrations.add_channels_management_tables
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, init_db, get_db_session
from app.models.channels import (
    Channel, ChannelGroup, ChannelGroupMembership,
    PostingSettings, AutoCommentTemplate
)


def run_migration():
    """Run migration to create Channel Management tables"""
    print("🚀 Starting Channel Management migration (new structure)...")
    
    # Initialize database connection FIRST
    init_db()
    
    # Get engine từ get_db_session() (đã được init_db tạo sẵn)
    print("🔧 Getting database engine...")
    db = get_db_session()
    try:
        engine = db.get_bind()
        if engine is None:
            raise RuntimeError("Database engine is None. Vui lòng kiểm tra DATABASE_URL trong .env")
    finally:
        db.close()
    
    # Create tables
    print("📦 Creating Channel Management tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
    
    print("\n✅ Migration completed successfully!")
    print("\n📝 Created tables:")
    print("   - channels (generic platform support)")
    print("   - channel_groups")
    print("   - channel_group_memberships")
    print("   - posting_settings")
    print("   - auto_comment_templates")
    print("\n📌 Note: These are separate from existing facebook_pages table for backward compatibility")


if __name__ == "__main__":
    run_migration()

