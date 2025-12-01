"""
Migration: Add color_hex column to channel_groups table

Usage:
    python -m migrations.add_color_hex_to_channel_groups
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, get_db_session
from sqlalchemy import text


def run_migration():
    """Add color_hex column to channel_groups table"""
    print("🚀 Starting migration: Add color_hex to channel_groups...")
    
    # Initialize database connection
    init_db()
    
    # Get database session
    db = get_db_session()
    
    try:
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='channel_groups' 
            AND column_name='color_hex'
        """)
        
        result = db.execute(check_query).fetchone()
        
        if result:
            print("✅ Column 'color_hex' already exists in channel_groups table")
            return
        
        # Add color_hex column
        print("📝 Adding color_hex column to channel_groups...")
        alter_query = text("""
            ALTER TABLE channel_groups 
            ADD COLUMN color_hex VARCHAR(7) DEFAULT NULL
        """)
        
        db.execute(alter_query)
        db.commit()
        
        print("✅ Successfully added color_hex column to channel_groups")
        print("   - Type: VARCHAR(7)")
        print("   - Default: NULL")
        print("   - Example values: #22c55e, #3B82F6")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        db.close()
    
    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
