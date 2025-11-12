"""
Helper functions để extract và filter prefixes từ LogicRules
Thay thế cho extractPrefixesFromLogicRules_() từ Logics.gs
"""
import logging
from typing import List, Set
from app.core.database import get_db_session
from app.models.logic_rule import LogicRule

logger = logging.getLogger(__name__)


def extract_prefixes_from_logic_rules() -> List[str]:
    """
    Trích xuất tất cả prefixes từ LogicRules
    Format: LogicRule.prefixes là JSON array ["FL", "PX", ...]
    Trả về list các prefix duy nhất (uppercase)
    """
    db = get_db_session()
    try:
        # Lấy tất cả LogicRules có enabled = True
        rules = db.query(LogicRule).filter(LogicRule.enabled == True).all()
        
        prefixes_set: Set[str] = set()
        
        for rule in rules:
            if rule.prefixes and isinstance(rule.prefixes, list):
                for prefix in rule.prefixes:
                    if prefix and isinstance(prefix, str):
                        # Uppercase và loại bỏ DEFAULT
                        upper_prefix = prefix.strip().upper()
                        if upper_prefix and upper_prefix != "DEFAULT":
                            prefixes_set.add(upper_prefix)
        
        prefixes = sorted(list(prefixes_set))
        
        if not prefixes:
            # Fallback: dùng danh sách mặc định
            logger.warning("⚠️ Không đọc được prefix từ LogicRules, dùng danh sách mặc định")
            prefixes = ['PX', 'TL', 'FL', 'NM', 'CCHL', 'DHHL', 'HSHL', 'CCB']
        else:
            logger.info(f"📋 Đã trích xuất {len(prefixes)} prefix từ LogicRules: {', '.join(prefixes)}")
        
        return prefixes
    except Exception as e:
        logger.error(f"⚠️ Lỗi khi trích xuất Prefixes từ LogicRules: {e}")
        # Fallback: dùng danh sách mặc định
        return ['PX', 'TL', 'FL', 'NM', 'CCHL', 'DHHL', 'HSHL', 'CCB']
    finally:
        db.close()


def has_allowed_prefix(campaign_name: str, allowed_prefixes: List[str] = None) -> str:
    """
    Kiểm tra campaign name có prefix hợp lệ không
    Trả về prefix nếu match, None nếu không match
    
    Args:
        campaign_name: Tên campaign
        allowed_prefixes: Danh sách prefix được phép (nếu None, sẽ tự động lấy từ LogicRules)
    
    Returns:
        Prefix nếu match, None nếu không match
    """
    if not campaign_name:
        return None
    
    if allowed_prefixes is None:
        allowed_prefixes = extract_prefixes_from_logic_rules()
    
    # Tạo set để lookup nhanh
    allowed_prefixes_set = set(allowed_prefixes)
    
    # Lấy prefix từ campaign name
    from app.services.logics import get_prefix_from_name
    extracted_prefix = get_prefix_from_name(campaign_name).upper()
    
    # Thử exact match trước
    if extracted_prefix in allowed_prefixes_set:
        return extracted_prefix
    
    # Thử match prefix là substring (ví dụ: "CCB1" bắt đầu bằng "CCB")
    for allowed_prefix in allowed_prefixes:
        if extracted_prefix.startswith(allowed_prefix) or allowed_prefix.startswith(extracted_prefix):
            if len(extracted_prefix) >= 2:  # Ít nhất 2 ký tự
                return allowed_prefix
    
    return None

