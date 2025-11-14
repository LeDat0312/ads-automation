#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script đơn giản để thêm cột user_id vào các bảng accounts, prefixes, account_prefixes
Sử dụng SQL trực tiếp thay vì SQLAlchemy inspector
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from app.core.database import init_db, engine, SessionLocal
from app.core.config import get_settings
import os
from dotenv import load_dotenv

def add_user_id_columns():
    """Thêm cột user_id vào các bảng nếu thiếu"""
    print("🔍 Đang kiểm tra và thêm cột user_id...")
    
    # Load .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Đã load .env từ {env_path}")
    else:
        print(f"⚠️  Không tìm thấy .env tại {env_path}")
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"⚠️  Lỗi khi khởi tạo database: {e}")
        print("   Đang thử kết nối trực tiếp...")
        # Try to create engine directly
        settings = get_settings()
        if settings.DATABASE_URL:
            global engine
            from sqlalchemy import create_engine
            engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
            print("✅ Đã tạo engine trực tiếp từ DATABASE_URL")
    
    # Ensure engine is initialized
    if engine is None:
        print("❌ Engine chưa được khởi tạo. Vui lòng kiểm tra DATABASE_URL trong .env")
        return False
    
    try:
        with engine.connect() as conn:
            # Check and add user_id to accounts table
            print("\n📋 Kiểm tra bảng 'accounts'...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'accounts' AND column_name = 'user_id'
            """))
            if result.fetchone() is None:
                print("   ⚠️  Thiếu cột 'user_id'! Đang thêm...")
                conn.execute(text("ALTER TABLE accounts ADD COLUMN user_id INTEGER"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts(user_id)"))
                # Check if users table exists before adding foreign key
                result = conn.execute(text("""
                    SELECT 1 FROM information_schema.tables WHERE table_name = 'users'
                """))
                if result.fetchone():
                    try:
                        conn.execute(text("""
                            ALTER TABLE accounts 
                            ADD CONSTRAINT fk_accounts_user_id 
                            FOREIGN KEY (user_id) REFERENCES users(id)
                        """))
                    except Exception as e:
                        print(f"   ⚠️  Không thể thêm foreign key (có thể đã tồn tại): {e}")
                conn.commit()
                print("   ✅ Đã thêm cột 'user_id' vào bảng 'accounts'")
            else:
                print("   ✅ Cột 'user_id' đã tồn tại trong bảng 'accounts'")
            
            # Check and add user_id to prefixes table
            print("\n📋 Kiểm tra bảng 'prefixes'...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'prefixes' AND column_name = 'user_id'
            """))
            if result.fetchone() is None:
                print("   ⚠️  Thiếu cột 'user_id'! Đang thêm...")
                conn.execute(text("ALTER TABLE prefixes ADD COLUMN user_id INTEGER"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_prefixes_user_id ON prefixes(user_id)"))
                # Check if users table exists before adding foreign key
                result = conn.execute(text("""
                    SELECT 1 FROM information_schema.tables WHERE table_name = 'users'
                """))
                if result.fetchone():
                    try:
                        conn.execute(text("""
                            ALTER TABLE prefixes 
                            ADD CONSTRAINT fk_prefixes_user_id 
                            FOREIGN KEY (user_id) REFERENCES users(id)
                        """))
                    except Exception as e:
                        print(f"   ⚠️  Không thể thêm foreign key (có thể đã tồn tại): {e}")
                conn.commit()
                print("   ✅ Đã thêm cột 'user_id' vào bảng 'prefixes'")
            else:
                print("   ✅ Cột 'user_id' đã tồn tại trong bảng 'prefixes'")
            
            # Check and add user_id to account_prefixes table
            print("\n📋 Kiểm tra bảng 'account_prefixes'...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'account_prefixes' AND column_name = 'user_id'
            """))
            if result.fetchone() is None:
                print("   ⚠️  Thiếu cột 'user_id'! Đang thêm...")
                conn.execute(text("ALTER TABLE account_prefixes ADD COLUMN user_id INTEGER"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_account_prefixes_user_id ON account_prefixes(user_id)"))
                # Check if users table exists before adding foreign key
                result = conn.execute(text("""
                    SELECT 1 FROM information_schema.tables WHERE table_name = 'users'
                """))
                if result.fetchone():
                    try:
                        conn.execute(text("""
                            ALTER TABLE account_prefixes 
                            ADD CONSTRAINT fk_account_prefixes_user_id 
                            FOREIGN KEY (user_id) REFERENCES users(id)
                        """))
                    except Exception as e:
                        print(f"   ⚠️  Không thể thêm foreign key (có thể đã tồn tại): {e}")
                conn.commit()
                print("   ✅ Đã thêm cột 'user_id' vào bảng 'account_prefixes'")
            else:
                print("   ✅ Cột 'user_id' đã tồn tại trong bảng 'account_prefixes'")
        
        print("\n✅ Hoàn tất kiểm tra và thêm cột user_id!")
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_user_id_columns()
    sys.exit(0 if success else 1)

