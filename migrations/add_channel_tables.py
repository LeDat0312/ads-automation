"""
Migration script để tạo bảng cho Channel Management
- facebook_pages: Danh sách Facebook Pages đã kết nối
- channel_groups: Nhóm kênh
- channel_group_items: Liên kết group ↔ pages
- auto_comment_schedules: Lịch auto comment

Usage:
    python -m migrations.add_channel_tables
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, init_db, get_db_session
from app.models.channel import FacebookPage, ChannelGroup, ChannelGroupItem, AutoCommentSchedule


def run_migration():
    """Run migration to create Channel Management tables"""
    print("🚀 Starting Channel Management migration...")
    
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
    print("   - facebook_pages")
    print("   - channel_groups")
    print("   - channel_group_items")
    print("   - auto_comment_schedules")


if __name__ == "__main__":
    run_migration()


