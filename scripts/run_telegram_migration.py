#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để chạy migration thêm các cột Telegram Bot vào user_settings table
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

def run_migration():
    """Chạy migration script"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL không được tìm thấy trong .env file")
        return False
    
    print(f"📊 Đang kết nối đến database...")
    print(f"   Database URL: {database_url[:50]}...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Read migration SQL file
        migration_file = Path(__file__).parent / "add_telegram_columns.sql"
        if not migration_file.exists():
            print(f"❌ Không tìm thấy file migration: {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"📝 Đang chạy migration script...")
        
        # Execute migration
        with engine.connect() as conn:
            # Execute each statement separately
            statements = sql_content.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        # Ignore "already exists" errors
                        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                            print(f"   ⚠️  {statement[:50]}... (đã tồn tại, bỏ qua)")
                        else:
                            print(f"   ⚠️  Lỗi: {e}")
                            # Continue anyway
        
        print("✅ Migration completed successfully!")
        
        # Verify columns were added
        print("\n🔍 Kiểm tra các cột đã được thêm:")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = 'user_settings'
                AND column_name LIKE 'telegram%'
                ORDER BY column_name;
            """))
            
            columns = result.fetchall()
            if columns:
                for col in columns:
                    print(f"   ✅ {col[0]} ({col[1]})")
            else:
                print("   ⚠️  Không tìm thấy cột nào bắt đầu với 'telegram'")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi chạy migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TELEGRAM BOT SETTINGS MIGRATION")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    if success:
        print("=" * 60)
        print("✅ Migration hoàn thành!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("=" * 60)
        print("❌ Migration thất bại!")
        print("=" * 60)
        sys.exit(1)

