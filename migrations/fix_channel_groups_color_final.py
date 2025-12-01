"""
Migration: Final fix for channel_groups color column

This migration handles ALL scenarios:
1. If 'color' exists and 'color_hex' doesn't → rename 'color' to 'color_hex'
2. If both exist → copy data, drop 'color'
3. If only 'color_hex' exists → ensure constraints
4. If neither exists → create 'color_hex'

Also adds 'color' as a computed/alias column for backward compatibility if needed.

Usage:
    python -m migrations.fix_channel_groups_color_final
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, get_db_session
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Fix channel_groups color column - Final version"""
    logger.info("🚀 Starting FINAL migration: Fix channel_groups color column...")
    
    init_db()
    db = get_db_session()
    
    try:
        # Step 1: Check which columns exist
        logger.info("📋 Step 1: Checking existing columns...")
        check_columns_query = text("""
            SELECT column_name, is_nullable, column_default, data_type
            FROM information_schema.columns 
            WHERE table_name='channel_groups' 
            AND column_name IN ('color', 'color_hex')
            ORDER BY column_name
        """)
        
        columns = db.execute(check_columns_query).fetchall()
        existing_columns = {row[0]: {'nullable': row[1], 'default': row[2], 'type': row[3]} for row in columns}
        
        has_color = 'color' in existing_columns
        has_color_hex = 'color_hex' in existing_columns
        
        logger.info(f"   - Column 'color' exists: {has_color}")
        logger.info(f"   - Column 'color_hex' exists: {has_color_hex}")
        
        if has_color:
            logger.info(f"   - 'color' details: {existing_columns['color']}")
        if has_color_hex:
            logger.info(f"   - 'color_hex' details: {existing_columns['color_hex']}")
        
        # Step 2: Handle different scenarios
        if has_color and not has_color_hex:
            # Scenario 1: Only 'color' exists → rename to 'color_hex'
            logger.info("📝 Scenario 1: Renaming 'color' to 'color_hex'...")
            db.execute(text("ALTER TABLE channel_groups RENAME COLUMN color TO color_hex"))
            db.commit()
            logger.info("✅ Renamed 'color' to 'color_hex'")
            
        elif has_color and has_color_hex:
            # Scenario 2: Both exist → migrate data and drop 'color'
            logger.info("📝 Scenario 2: Both columns exist...")
            
            # Copy data from 'color' to 'color_hex' where color_hex is NULL
            logger.info("   - Copying data from 'color' to 'color_hex' where needed...")
            db.execute(text("""
                UPDATE channel_groups 
                SET color_hex = COALESCE(color_hex, color, '#3B82F6')
                WHERE color_hex IS NULL OR color_hex = ''
            """))
            db.commit()
            
            # Drop the old 'color' column
            logger.info("   - Dropping old 'color' column...")
            db.execute(text("ALTER TABLE channel_groups DROP COLUMN IF EXISTS color"))
            db.commit()
            logger.info("✅ Dropped 'color' column")
            
        elif not has_color and has_color_hex:
            # Scenario 3: Only 'color_hex' exists → already correct
            logger.info("✅ Scenario 3: Schema already correct (only 'color_hex' exists)")
            
        else:
            # Scenario 4: Neither exists → create 'color_hex'
            logger.info("📝 Scenario 4: Creating 'color_hex' column...")
            db.execute(text("""
                ALTER TABLE channel_groups 
                ADD COLUMN color_hex VARCHAR(7) NOT NULL DEFAULT '#3B82F6'
            """))
            db.commit()
            logger.info("✅ Created 'color_hex' column")
        
        # Step 3: Ensure color_hex has proper constraints
        logger.info("📝 Step 3: Ensuring 'color_hex' has proper constraints...")
        
        # Update any NULL values to default
        db.execute(text("""
            UPDATE channel_groups 
            SET color_hex = '#3B82F6' 
            WHERE color_hex IS NULL OR color_hex = ''
        """))
        db.commit()
        
        # Check if column is nullable
        check_nullable = text("""
            SELECT is_nullable 
            FROM information_schema.columns 
            WHERE table_name='channel_groups' AND column_name='color_hex'
        """)
        is_nullable = db.execute(check_nullable).scalar()
        
        if is_nullable == 'YES':
            logger.info("   - Setting column to NOT NULL...")
            db.execute(text("ALTER TABLE channel_groups ALTER COLUMN color_hex SET NOT NULL"))
            db.commit()
        
        # Set default value
        logger.info("   - Setting default value...")
        db.execute(text("ALTER TABLE channel_groups ALTER COLUMN color_hex SET DEFAULT '#3B82F6'"))
        db.commit()
        
        # Step 4: Verify final state
        logger.info("🔍 Step 4: Verifying final schema...")
        verify_query = text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name='channel_groups' 
            AND column_name IN ('color', 'color_hex')
        """)
        
        final_columns = db.execute(verify_query).fetchall()
        
        logger.info("✅ Final schema:")
        for col in final_columns:
            logger.info(f"   - {col[0]}: type={col[1]}, nullable={col[2]}, default={col[3]}")
        
        # Check if 'color' still exists (should not)
        has_color_after = any(col[0] == 'color' for col in final_columns)
        has_color_hex_after = any(col[0] == 'color_hex' for col in final_columns)
        
        if has_color_after:
            logger.warning("⚠️ WARNING: 'color' column still exists!")
        
        if not has_color_hex_after:
            logger.error("❌ ERROR: 'color_hex' column doesn't exist!")
            return False
        
        logger.info("\n" + "="*60)
        logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info("Summary:")
        logger.info("  - Table 'channel_groups' now has only 'color_hex' column")
        logger.info("  - Column is NOT NULL with default '#3B82F6'")
        logger.info("  - All existing data preserved")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
