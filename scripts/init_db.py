"""
Initialize Database
Tạo tất cả tables từ models
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings, init_db
from app.core.database import Base, engine
# Import models để đảm bảo chúng được đăng ký với Base
from app.models.telegram_update import TelegramUpdate
from app.models.job import Job
from app.models.logic_rule import LogicRule
from app.core.database import AdMetrics, SystemSetting, AutomationStatus

def main():
    """Initialize database"""
    print("🚀 Initializing database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully!")
        print("\n📋 Created tables:")
        for table in Base.metadata.tables:
            print(f"  - {table}")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

