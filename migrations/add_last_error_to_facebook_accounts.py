"""
Migration: Add last_error column to facebook_accounts table

Usage:
    python -m migrations.add_last_error_to_facebook_accounts
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, get_db_session
from sqlalchemy import text


def run_migration():
    """Add last_error column to facebook_accounts table"""
    print("🚀 Starting migration: Add last_error to facebook_accounts...")
    
    # Initialize database connection
    init_db()
    
    # Get database session
    db = get_db_session()
    
    try:
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='facebook_accounts' 
            AND column_name='last_error'
        """)
        
        result = db.execute(check_query).fetchone()
        
        if result:
            print("✅ Column 'last_error' already exists in facebook_accounts table")
            return
        
        # Add last_error column
        print("📝 Adding last_error column to facebook_accounts...")
        alter_query = text("""
            ALTER TABLE facebook_accounts 
            ADD COLUMN last_error TEXT DEFAULT NULL
        """)
        
        db.execute(alter_query)
        db.commit()
        
        print("✅ Successfully added last_error column to facebook_accounts")
        print("   - Type: TEXT")
        print("   - Default: NULL")
        print("   - Purpose: Store last error message from Facebook API")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        db.close()
    
    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
