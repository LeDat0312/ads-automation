"""
Logic Rules Service
Thay thế cho Logics.gs từ Google Apps Script
"""
import re
import logging
from typing import Dict, Any, List, Optional
from app.core.database import get_db_session, LogicRule

logger = logging.getLogger(__name__)


def get_prefix_from_name(campaign_name: str) -> str:
    """
    Lấy prefix từ campaign name
    Thay thế cho hàm getPrefixTuTen() từ Logics.gs
    """
    if not campaign_name:
        return "DEFAULT"
    
    name_upper = campaign_name.upper().strip()
    parts = re.split(r'[\s\-_]+', name_upper)
    prefix = parts[0] if parts else ""
    
    # Nếu prefix quá dài, thử loại bỏ phần số ở cuối
    if len(prefix) > 6:
        prefix_without_numbers = re.sub(r'\d+$', '', prefix)
        if len(prefix_without_numbers) >= 3 and len(prefix_without_numbers) < len(prefix):
            prefix = prefix_without_numbers
    
    return prefix or "DEFAULT"


def build_logic_map() -> Dict[str, Dict[str, Any]]:
    """
    Xây dựng một Map tra cứu logic từ database
    Thay thế cho hàm buildLogicMap() từ Logics.gs
    
    Returns:
        Dict { "account_id|prefix": { "SL_1_SPEND": 50000, ... }, ... }
    """
    from app.core.database import get_db_session
    db = get_db_session()
    logic_map = {}
    
    try:
        # Lấy tất cả logic rules từ database
        logic_rules = db.query(LogicRule).filter(LogicRule.enabled == True).all()
        
        for rule in logic_rules:
            # Tạo key: "account_id|prefix" hoặc "DEFAULT|DEFAULT"
            if rule.account_id and rule.prefix:
                rule_key = f"{rule.account_id}|{rule.prefix}"
            else:
                rule_key = "DEFAULT|DEFAULT"
            
            if rule_key not in logic_map:
                logic_map[rule_key] = {}
            
            # Thêm các điều kiện logic
            if rule.logic_type == "logic1":
                logic_map[rule_key]["SL_1_SPEND"] = rule.condition_spend
                logic_map[rule_key]["SL_1_KET_QUA"] = rule.condition_results
            elif rule.logic_type == "logic2":
                logic_map[rule_key]["SL_2_SPEND"] = rule.condition_spend
                logic_map[rule_key]["SL_2_GIA_DATA"] = rule.condition_gia_data
            elif rule.logic_type == "logic3":
                logic_map[rule_key]["SL_3_SPEND"] = rule.condition_spend
                logic_map[rule_key]["SL_3_KET_QUA"] = rule.condition_results
        
        logger.info(f"✅ Đã xây dựng logic map với {len(logic_map)} rules")
    except Exception as e:
        logger.error(f"🚨 Lỗi khi xây dựng logic map: {e}")
    finally:
        db.close()
    
    return logic_map


def check_logic_1(
    spend: float,
    results: int,
    logic_map: Dict[str, Dict[str, Any]],
    account_id: str,
    prefix: str
) -> bool:
    """
    Kiểm tra Logic 1: Tắt nếu spend > ngưỡng và results = 0
    """
    rule_key = f"{account_id}|{prefix}"
    logic = logic_map.get(rule_key) or logic_map.get("DEFAULT|DEFAULT", {})
    
    sl_1_spend = logic.get("SL_1_SPEND", 0)
    sl_1_ket_qua = logic.get("SL_1_KET_QUA", 0)
    
    if spend > sl_1_spend and results <= sl_1_ket_qua:
        return True
    
    return False


def check_logic_2(
    spend: float,
    gia_data: float,
    logic_map: Dict[str, Dict[str, Any]],
    account_id: str,
    prefix: str
) -> bool:
    """
    Kiểm tra Logic 2: Tắt nếu spend > ngưỡng và gia_data > ngưỡng
    """
    rule_key = f"{account_id}|{prefix}"
    logic = logic_map.get(rule_key) or logic_map.get("DEFAULT|DEFAULT", {})
    
    sl_2_spend = logic.get("SL_2_SPEND", 0)
    sl_2_gia_data = logic.get("SL_2_GIA_DATA", 0)
    
    if spend > sl_2_spend and gia_data > sl_2_gia_data:
        return True
    
    return False


def check_logic_3(
    spend: float,
    results: int,
    logic_map: Dict[str, Dict[str, Any]],
    account_id: str,
    prefix: str
) -> bool:
    """
    Kiểm tra Logic 3: Bật lại nếu đáp ứng điều kiện
    """
    rule_key = f"{account_id}|{prefix}"
    logic = logic_map.get(rule_key) or logic_map.get("DEFAULT|DEFAULT", {})
    
    sl_3_spend = logic.get("SL_3_SPEND", 0)
    sl_3_ket_qua = logic.get("SL_3_KET_QUA", 0)
    
    if spend <= sl_3_spend and results >= sl_3_ket_qua:
        return True
    
    return False

