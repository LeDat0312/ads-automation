"""
Migration script to create facebook_accounts table
Stores Facebook access tokens (Via) for reuse across features

Table: facebook_accounts
- Stores user's Facebook access tokens with metadata
- Types: FANPAGE (for page management), ADS (for ad optimization), BOTH
- Enables token reuse instead of manual copy-paste

Usage:
    python -m migrations.add_facebook_accounts_table
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, init_db, get_db_session
from app.models.facebook_account import FacebookAccount


def run_migration():
    """Run migration to create facebook_accounts table"""
    print("🚀 Starting facebook_accounts migration...")
    
    # Initialize database connection FIRST
    init_db()
    
    # Get engine from get_db_session() (already created by init_db)
    print("🔧 Getting database engine...")
    db = get_db_session()
    try:
        engine = db.get_bind()
        if engine is None:
            raise RuntimeError("Database engine is None. Please check DATABASE_URL in .env")
    finally:
        db.close()
    
    # Create table
    print("📦 Creating facebook_accounts table...")
    Base.metadata.create_all(bind=engine, tables=[FacebookAccount.__table__])
    print("✅ Table created successfully")
    
    print("\n✅ Migration completed successfully!")
    print("\n📝 Created table: facebook_accounts")
    print("   - Stores Facebook access tokens (Via)")
    print("   - Types: FANPAGE, ADS, BOTH")
    print("   - Enables token reuse across features")
    print("\n📌 Next steps:")
    print("   1. Users can save tokens in /settings")
    print("   2. Reuse tokens in channel management (no copy-paste)")
    print("   3. Supports both Fanpage and Ads use cases")


if __name__ == "__main__":
    run_migration()
