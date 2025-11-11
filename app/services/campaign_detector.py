"""
Campaign Type Detection Service
Phát hiện loại campaign: E-commerce vs Lead
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def detect_campaign_type_from_objective(objective: str) -> str:
    """
    Phát hiện loại campaign từ Facebook campaign objective
    Thay thế cho việc cấu hình thủ công
    
    Returns:
        'ECOMMERCE', 'LEAD', hoặc 'UNKNOWN'
    """
    if not objective:
        return 'UNKNOWN'
    
    objective_upper = str(objective).upper().strip()
    
    # E-commerce objectives
    ecommerce_objectives = [
        'CONVERSIONS',
        'CATALOG_SALES',
        'PURCHASE',
        'STORE_TRAFFIC',
        'PRODUCT_CATALOG_SALES',
        'OUTCOME_SALES',
        'OUTCOME_LEADS'  # Có thể là lead nhưng cũng có thể là purchase
    ]
    
    # Lead objectives
    lead_objectives = [
        'LEAD_GENERATION',
        'MESSAGES',
        'PHONE_CALLS',
        'ENGAGEMENT',
        'POST_ENGAGEMENT',
        'EVENT_RESPONSES',
        'LOCAL_AWARENESS'
    ]
    
    if objective_upper in ecommerce_objectives:
        return 'ECOMMERCE'
    elif objective_upper in lead_objectives:
        return 'LEAD'
    
    return 'UNKNOWN'


def detect_campaign_type_from_metrics(metrics: Dict[str, Any]) -> str:
    """
    Phát hiện loại campaign từ metrics
    Dùng khi không có campaign objective hoặc để verify
    
    Returns:
        'ECOMMERCE', 'LEAD', hoặc 'UNKNOWN'
    """
    # E-commerce metrics
    purchases = int(metrics.get('purchases', 0) or 0)
    purchase_value = float(metrics.get('purchase_value', 0) or 0)
    revenue = float(metrics.get('revenue', 0) or 0)
    roas = float(metrics.get('roas', 0) or 0)
    
    # Lead metrics
    leads = int(metrics.get('leads', 0) or 0)
    phone_calls = int(metrics.get('phone_calls', 0) or 0)
    messages = int(metrics.get('messaging_conversations_started', 0) or 0)
    comments = int(metrics.get('post_comments', 0) or 0)
    
    # Nếu có purchase hoặc purchase_value → E-commerce
    if purchases > 0 or purchase_value > 0 or revenue > 0:
        return 'ECOMMERCE'
    
    # Nếu có leads, phone calls, hoặc messages → Lead
    if leads > 0 or phone_calls > 0 or messages > 0 or comments > 0:
        return 'LEAD'
    
    return 'UNKNOWN'


def detect_campaign_type_hybrid(
    objective: Optional[str] = None,
    metrics: Optional[Dict[str, Any]] = None
) -> str:
    """
    Phát hiện loại campaign bằng cách kết hợp objective và metrics
    Ưu tiên objective, nếu không có thì dùng metrics
    
    Returns:
        'ECOMMERCE', 'LEAD', hoặc 'UNKNOWN'
    """
    # Ưu tiên objective
    if objective:
        type_from_objective = detect_campaign_type_from_objective(objective)
        if type_from_objective != 'UNKNOWN':
            return type_from_objective
    
    # Nếu objective không rõ, dùng metrics
    if metrics:
        type_from_metrics = detect_campaign_type_from_metrics(metrics)
        if type_from_metrics != 'UNKNOWN':
            return type_from_metrics
    
    return 'UNKNOWN'


def get_campaign_type_for_account_prefix(
    account_id: str,
    prefix: str,
    db_session
) -> str:
    """
    Lấy campaign type từ database (nếu đã được cấu hình)
    Hoặc auto-detect nếu chưa có
    """
    from app.core.database import AutomationStatus
    
    # Kiểm tra trong database
    status = db_session.query(AutomationStatus).filter(
        AutomationStatus.account_id == account_id,
        AutomationStatus.prefix == prefix
    ).first()
    
    if status and hasattr(status, 'campaign_type') and status.campaign_type:
        return status.campaign_type
    
    return 'UNKNOWN'  # Sẽ được auto-detect sau

