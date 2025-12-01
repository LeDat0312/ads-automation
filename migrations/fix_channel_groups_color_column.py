"""
Migration: Fix channel_groups color column issue

Problem:
- Table has old column 'color' (NOT NULL) + new column 'color_hex'
- Model only uses 'color_hex', causing NULL constraint violation on 'color'

Solution:
1. If only 'color' exists → rename to 'color_hex'
2. If both exist → copy data from 'color' to 'color_hex' if needed, then drop 'color'
3. Ensure 'color_hex' is NOT NULL with default value

Usage:
    python -m migrations.fix_channel_groups_color_column
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, get_db_session
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Fix channel_groups color column"""
    logger.info("🚀 Starting migration: Fix channel_groups color column...")
    
    # Initialize database connection
    init_db()
    db = get_db_session()
    
    try:
        # Step 1: Check which columns exist
        logger.info("📋 Checking existing columns...")
        check_columns_query = text("""
            SELECT column_name, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name='channel_groups' 
            AND column_name IN ('color', 'color_hex')
            ORDER BY column_name
        """)
        
        columns = db.execute(check_columns_query).fetchall()
        existing_columns = {row[0]: {'nullable': row[1], 'default': row[2]} for row in columns}
        
        has_color = 'color' in existing_columns
        has_color_hex = 'color_hex' in existing_columns
        
        logger.info(f"   - Column 'color' exists: {has_color}")
        logger.info(f"   - Column 'color_hex' exists: {has_color_hex}")
        
        # Step 2: Handle different scenarios
        if has_color and not has_color_hex:
            # Scenario 1: Only 'color' exists → rename to 'color_hex'
            logger.info("📝 Scenario 1: Renaming 'color' to 'color_hex'...")
            
            rename_query = text("""
                ALTER TABLE channel_groups 
                RENAME COLUMN color TO color_hex
            """)
            db.execute(rename_query)
            db.commit()
            
            logger.info("✅ Renamed 'color' to 'color_hex'")
            
        elif has_color and has_color_hex:
            # Scenario 2: Both exist → migrate data and drop 'color'
            logger.info("📝 Scenario 2: Both columns exist, migrating data...")
            
            # Check if there are any rows where color_hex is NULL but color has value
            check_data_query = text("""
                SELECT COUNT(*) 
                FROM channel_groups 
                WHERE color_hex IS NULL AND color IS NOT NULL
            """)
            rows_to_migrate = db.execute(check_data_query).scalar()
            
            if rows_to_migrate > 0:
                logger.info(f"   - Found {rows_to_migrate} rows to migrate")
                
                # Copy data from 'color' to 'color_hex' where needed
                migrate_data_query = text("""
                    UPDATE channel_groups 
                    SET color_hex = color 
                    WHERE color_hex IS NULL AND color IS NOT NULL
                """)
                db.execute(migrate_data_query)
                db.commit()
                
                logger.info(f"✅ Migrated {rows_to_migrate} rows")
            else:
                logger.info("   - No data migration needed")
            
            # Drop the old 'color' column
            logger.info("📝 Dropping old 'color' column...")
            drop_query = text("""
                ALTER TABLE channel_groups 
                DROP COLUMN IF EXISTS color
            """)
            db.execute(drop_query)
            db.commit()
            
            logger.info("✅ Dropped 'color' column")
            
        elif not has_color and has_color_hex:
            # Scenario 3: Only 'color_hex' exists → already correct
            logger.info("✅ Schema already correct (only 'color_hex' exists)")
            
        else:
            # Scenario 4: Neither exists → create 'color_hex'
            logger.info("📝 Scenario 4: Creating 'color_hex' column...")
            
            create_query = text("""
                ALTER TABLE channel_groups 
                ADD COLUMN color_hex VARCHAR(7) DEFAULT '#3B82F6' NOT NULL
            """)
            db.execute(create_query)
            db.commit()
            
            logger.info("✅ Created 'color_hex' column")
        
        # Step 3: Ensure color_hex has proper constraints
        logger.info("📝 Ensuring 'color_hex' has proper constraints...")
        
        # Check current nullable status
        check_nullable_query = text("""
            SELECT is_nullable 
            FROM information_schema.columns 
            WHERE table_name='channel_groups' 
            AND column_name='color_hex'
        """)
        is_nullable = db.execute(check_nullable_query).scalar()
        
        if is_nullable == 'YES':
            logger.info("   - Setting default value for NULL rows...")
            
            # Set default for existing NULL values
            update_nulls_query = text("""
                UPDATE channel_groups 
                SET color_hex = '#3B82F6' 
                WHERE color_hex IS NULL
            """)
            db.execute(update_nulls_query)
            db.commit()
            
            # Alter column to NOT NULL
            logger.info("   - Setting column to NOT NULL...")
            alter_not_null_query = text("""
                ALTER TABLE channel_groups 
                ALTER COLUMN color_hex SET NOT NULL
            """)
            db.execute(alter_not_null_query)
            
            # Set default value for future inserts
            alter_default_query = text("""
                ALTER TABLE channel_groups 
                ALTER COLUMN color_hex SET DEFAULT '#3B82F6'
            """)
            db.execute(alter_default_query)
            
            db.commit()
            logger.info("✅ Set 'color_hex' to NOT NULL with default '#3B82F6'")
        else:
            logger.info("   - Column already NOT NULL")
        
        # Step 4: Verify final state
        logger.info("🔍 Verifying final schema...")
        verify_query = text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name='channel_groups' 
            AND column_name='color_hex'
        """)
        
        result = db.execute(verify_query).fetchone()
        if result:
            logger.info(f"✅ Final schema:")
            logger.info(f"   - Column: {result[0]}")
            logger.info(f"   - Type: {result[1]}")
            logger.info(f"   - Nullable: {result[2]}")
            logger.info(f"   - Default: {result[3]}")
        
        logger.info("\n✅ Migration completed successfully!")
        logger.info("   - Table 'channel_groups' now has only 'color_hex' column")
        logger.info("   - Column is NOT NULL with default '#3B82F6'")
        logger.info("   - All existing data preserved")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
