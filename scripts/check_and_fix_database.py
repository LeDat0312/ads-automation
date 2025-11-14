#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để kiểm tra và sửa database nếu thiếu cột user_id
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from app.core.database import init_db, engine, SessionLocal
from app.models.account_prefix import Account, Prefix, AccountPrefix
from app.models.user import User
from app.models.user_settings import UserSettings

def check_and_fix_database():
    """Kiểm tra và sửa database nếu thiếu cột user_id"""
    print("🔍 Đang kiểm tra database...")
    
    # Initialize database
    init_db()
    
    # Ensure engine is initialized
    if engine is None:
        print("❌ Engine chưa được khởi tạo. Đang thử lại...")
        init_db()
        if engine is None:
            print("❌ Không thể khởi tạo database engine. Vui lòng kiểm tra DATABASE_URL trong .env")
            return
    
    # Get inspector
    inspector = inspect(engine)
    
    # Check accounts table
    print("\n📋 Kiểm tra bảng 'accounts'...")
    if 'accounts' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('accounts')]
        print(f"   Các cột hiện có: {', '.join(columns)}")
        
        if 'user_id' not in columns:
            print("   ⚠️  Thiếu cột 'user_id'! Đang thêm...")
            try:
                with engine.connect() as conn:
                    # Add user_id column
                    conn.execute(text("ALTER TABLE accounts ADD COLUMN user_id INTEGER"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts(user_id)"))
                    conn.execute(text("ALTER TABLE accounts ADD CONSTRAINT fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES users(id)"))
                    conn.commit()
                print("   ✅ Đã thêm cột 'user_id' vào bảng 'accounts'")
            except Exception as e:
                print(f"   ❌ Lỗi khi thêm cột: {e}")
        else:
            print("   ✅ Cột 'user_id' đã tồn tại")
    else:
        print("   ⚠️  Bảng 'accounts' chưa tồn tại. Sẽ được tạo khi chạy init_db()")
    
    # Check prefixes table
    print("\n📋 Kiểm tra bảng 'prefixes'...")
    if 'prefixes' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('prefixes')]
        print(f"   Các cột hiện có: {', '.join(columns)}")
        
        if 'user_id' not in columns:
            print("   ⚠️  Thiếu cột 'user_id'! Đang thêm...")
            try:
                with engine.connect() as conn:
                    # Add user_id column
                    conn.execute(text("ALTER TABLE prefixes ADD COLUMN user_id INTEGER"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_prefixes_user_id ON prefixes(user_id)"))
                    conn.execute(text("ALTER TABLE prefixes ADD CONSTRAINT fk_prefixes_user_id FOREIGN KEY (user_id) REFERENCES users(id)"))
                    conn.commit()
                print("   ✅ Đã thêm cột 'user_id' vào bảng 'prefixes'")
            except Exception as e:
                print(f"   ❌ Lỗi khi thêm cột: {e}")
        else:
            print("   ✅ Cột 'user_id' đã tồn tại")
    else:
        print("   ⚠️  Bảng 'prefixes' chưa tồn tại. Sẽ được tạo khi chạy init_db()")
    
    # Check account_prefixes table
    print("\n📋 Kiểm tra bảng 'account_prefixes'...")
    if 'account_prefixes' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('account_prefixes')]
        print(f"   Các cột hiện có: {', '.join(columns)}")
        
        if 'user_id' not in columns:
            print("   ⚠️  Thiếu cột 'user_id'! Đang thêm...")
            try:
                with engine.connect() as conn:
                    # Add user_id column
                    conn.execute(text("ALTER TABLE account_prefixes ADD COLUMN user_id INTEGER"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_account_prefixes_user_id ON account_prefixes(user_id)"))
                    conn.execute(text("ALTER TABLE account_prefixes ADD CONSTRAINT fk_account_prefixes_user_id FOREIGN KEY (user_id) REFERENCES users(id)"))
                    conn.commit()
                print("   ✅ Đã thêm cột 'user_id' vào bảng 'account_prefixes'")
            except Exception as e:
                print(f"   ❌ Lỗi khi thêm cột: {e}")
        else:
            print("   ✅ Cột 'user_id' đã tồn tại")
    else:
        print("   ⚠️  Bảng 'account_prefixes' chưa tồn tại. Sẽ được tạo khi chạy init_db()")
    
    # Check users table
    print("\n📋 Kiểm tra bảng 'users'...")
    if 'users' in inspector.get_table_names():
        print("   ✅ Bảng 'users' đã tồn tại")
    else:
        print("   ⚠️  Bảng 'users' chưa tồn tại. Sẽ được tạo khi chạy init_db()")
    
    # Check user_settings table
    print("\n📋 Kiểm tra bảng 'user_settings'...")
    if 'user_settings' in inspector.get_table_names():
        print("   ✅ Bảng 'user_settings' đã tồn tại")
    else:
        print("   ⚠️  Bảng 'user_settings' chưa tồn tại. Sẽ được tạo khi chạy init_db()")
    
    print("\n✅ Hoàn tất kiểm tra database!")

if __name__ == "__main__":
    try:
        check_and_fix_database()
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

