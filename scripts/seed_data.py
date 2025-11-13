#!/usr/bin/env python3
"""
Script để seed accounts, prefixes, và logic rules cho 4 combinations:
- act_2827767517395636|FL
- act_2827767517395636|NM
- act_723686686812438|PX
- act_723686686812438|TL

Và xóa tất cả accounts/prefixes khác.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import get_db_session, init_db
from app.models.account_prefix import Account, Prefix
from app.models.logic_rule import LogicRule
from app.models.logic_7days_config import Logic7DaysConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Định nghĩa 4 combinations
ACCOUNTS = [
    {"account_id": "act_2827767517395636", "account_name": "Account 1"},
    {"account_id": "act_723686686812438", "account_name": "Account 2"},
]

PREFIXES = [
    {"prefix": "FL", "prefix_name": "FL Prefix"},
    {"prefix": "NM", "prefix_name": "NM Prefix"},
    {"prefix": "PX", "prefix_name": "PX Prefix"},
    {"prefix": "TL", "prefix_name": "TL Prefix"},
]

# Logic rules cho từng combination
# TODO: Cập nhật giá trị từ Google Sheet
LOGIC_RULES = {
    "act_2827767517395636|FL": {
        "logic1": {
            "condition_spend": 50000,  # SL_1_SPEND
            "condition_results": 0,    # SL_1_KET_QUA
        },
        "logic2": {
            "condition_spend": 100000,  # SL_2_SPEND
            "condition_gia_data": 50000,  # SL_2_GIA_DATA
        },
        "logic3": {
            "condition_spend": 50000,  # SL_3_SPEND (RESUME_SPEND)
            "condition_results": 1,    # SL_3_KET_QUA (RESUME_DATA)
        },
    },
    "act_2827767517395636|NM": {
        "logic1": {
            "condition_spend": 50000,
            "condition_results": 0,
        },
        "logic2": {
            "condition_spend": 100000,
            "condition_gia_data": 50000,
        },
        "logic3": {
            "condition_spend": 50000,
            "condition_results": 1,
        },
    },
    "act_723686686812438|PX": {
        "logic1": {
            "condition_spend": 50000,
            "condition_results": 0,
        },
        "logic2": {
            "condition_spend": 100000,
            "condition_gia_data": 50000,
        },
        "logic3": {
            "condition_spend": 50000,
            "condition_results": 1,
        },
    },
    "act_723686686812438|TL": {
        "logic1": {
            "condition_spend": 50000,
            "condition_results": 0,
        },
        "logic2": {
            "condition_spend": 100000,
            "condition_gia_data": 50000,
        },
        "logic3": {
            "condition_spend": 50000,
            "condition_results": 1,
        },
    },
}


def seed_data():
    """Seed accounts, prefixes, and logic rules"""
    db = get_db_session()
    
    try:
        # 1. Xóa tất cả accounts và prefixes cũ
        logger.info("🗑️ Xóa tất cả accounts và prefixes cũ...")
        db.query(LogicRule).delete()
        db.query(Logic7DaysConfig).delete()
        db.query(Account).delete()
        db.query(Prefix).delete()
        db.commit()
        logger.info("✅ Đã xóa dữ liệu cũ")
        
        # 2. Tạo accounts
        logger.info("📝 Tạo accounts...")
        for acc_data in ACCOUNTS:
            account = Account(
                account_id=acc_data["account_id"],
                account_name=acc_data["account_name"],
                enabled=True
            )
            db.add(account)
            logger.info(f"  ✅ Đã tạo account: {acc_data['account_id']}")
        db.commit()
        
        # 3. Tạo prefixes
        logger.info("📝 Tạo prefixes...")
        for prefix_data in PREFIXES:
            prefix = Prefix(
                prefix=prefix_data["prefix"],
                prefix_name=prefix_data["prefix_name"],
                enabled=True
            )
            db.add(prefix)
            logger.info(f"  ✅ Đã tạo prefix: {prefix_data['prefix']}")
        db.commit()
        
        # 4. Tạo logic rules
        logger.info("📝 Tạo logic rules...")
        for rule_key, rules in LOGIC_RULES.items():
            account_id, prefix = rule_key.split("|")
            
            # Logic 1: Giai đoạn 1
            if "logic1" in rules:
                logic1 = LogicRule(
                    account_id=account_id,
                    prefix=prefix,
                    logic_type="logic1",
                    condition_spend=rules["logic1"]["condition_spend"],
                    condition_results=rules["logic1"]["condition_results"],
                    enabled=True
                )
                db.add(logic1)
                logger.info(f"  ✅ Đã tạo Logic 1 cho {rule_key}")
            
            # Logic 2: Giai đoạn 2
            if "logic2" in rules:
                logic2 = LogicRule(
                    account_id=account_id,
                    prefix=prefix,
                    logic_type="logic2",
                    condition_spend=rules["logic2"]["condition_spend"],
                    condition_gia_data=rules["logic2"]["condition_gia_data"],
                    enabled=True
                )
                db.add(logic2)
                logger.info(f"  ✅ Đã tạo Logic 2 cho {rule_key}")
            
            # Logic 3: Bật lại
            if "logic3" in rules:
                logic3 = LogicRule(
                    account_id=account_id,
                    prefix=prefix,
                    logic_type="logic3",
                    condition_spend=rules["logic3"]["condition_spend"],
                    condition_results=rules["logic3"]["condition_results"],
                    enabled=True
                )
                db.add(logic3)
                logger.info(f"  ✅ Đã tạo Logic 3 cho {rule_key}")
        
        db.commit()
        logger.info("✅ Đã tạo tất cả logic rules")
        
        # 5. Tạo 7 days config (mặc định)
        logger.info("📝 Tạo 7 days config...")
        for rule_key in LOGIC_RULES.keys():
            account_id, prefix = rule_key.split("|")
            config = Logic7DaysConfig(
                account_id=account_id,
                prefix=prefix,
                spend_threshold=100000,
                gia_data_threshold=0,  # Dùng từ logic_map
                cost_per_purchase_keep_threshold=150000,
                days=7,
                enabled=True
            )
            db.add(config)
            logger.info(f"  ✅ Đã tạo 7 days config cho {rule_key}")
        
        db.commit()
        logger.info("✅ Hoàn thành seed data!")
        
    except Exception as e:
        logger.error(f"❌ Lỗi khi seed data: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Seed data
    seed_data()
    
    print("\n✅ Seed data hoàn thành!")
    print("\n📋 Danh sách accounts và prefixes đã tạo:")
    print("  - act_2827767517395636 (FL, NM)")
    print("  - act_723686686812438 (PX, TL)")
    print("\n💡 Lưu ý: Cần cập nhật giá trị logic rules từ Google Sheet trong file này.")

