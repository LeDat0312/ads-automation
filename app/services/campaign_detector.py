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
        'OUTCOME_SALES'
    ]
    
    # Lead objectives
    lead_objectives = [
        'LEAD_GENERATION',
        'MESSAGES',
        'PHONE_CALLS',
        'ENGAGEMENT',
        'POST_ENGAGEMENT',
        'EVENT_RESPONSES',
        'LOCAL_AWARENESS',
        'OUTCOME_LEADS'  # Facebook's new lead generation objective
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
    purchase_value = float(metrics.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0)
    checkouts = int(metrics.get('checkouts_initiated', 0) or 0)
    
    # Lead metrics
    leads = int(metrics.get('leads', 0) or 0)
    post_save = int(metrics.get('onsite_conversion_post_save', 0) or 0)  # Bắt đầu TT cho Lead
    messages = int(metrics.get('messaging_conversations_started', 0) or 0)
    comments = int(metrics.get('post_comments', 0) or 0)
    
    # Tính tổng engagement (lead indicators)
    total_engagement = messages + comments + post_save
    
    # Nếu có purchase hoặc purchase_value → E-commerce
    if purchases > 0 or purchase_value > 0:
        logger.debug(f"E-commerce detected: purchases={purchases}, value={purchase_value}")
        return 'ECOMMERCE'
    
    # Nếu có engagement nhưng KHÔNG có purchase → Lead
    if total_engagement > 0:
        logger.debug(f"Lead detected: messages={messages}, comments={comments}, post_save={post_save}")
        return 'LEAD'
    
    # Nếu có checkouts nhưng không có purchase → E-commerce (funnel chưa hoàn thành)
    if checkouts > 0:
        logger.debug(f"E-commerce detected from checkouts: {checkouts}")
        return 'ECOMMERCE'
    
    return 'UNKNOWN'


def detect_campaign_type_hybrid(
    objective: Optional[str] = None,
    metrics: Optional[Dict[str, Any]] = None,
    fallback_account_type: Optional[str] = None
) -> str:
    """
    Phát hiện loại campaign bằng cách kết hợp objective, metrics, và account_type
    Priority: objective → metrics → account_type → default ECOMMERCE
    
    Args:
        objective: Campaign objective từ Facebook API
        metrics: Dict chứa metrics (purchases, messages, etc.)
        fallback_account_type: Account type từ database (E-COMMERCE hoặc LEAD_GENERATION)
    
    Returns:
        'ECOMMERCE', 'LEAD', hoặc 'UNKNOWN'
    """
    # Ưu tiên objective
    if objective:
        type_from_objective = detect_campaign_type_from_objective(objective)
        if type_from_objective != 'UNKNOWN':
            logger.debug(f"Detected from objective '{objective}': {type_from_objective}")
            return type_from_objective
    
    # Nếu objective không rõ, dùng metrics
    if metrics:
        type_from_metrics = detect_campaign_type_from_metrics(metrics)
        if type_from_metrics != 'UNKNOWN':
            logger.debug(f"Detected from metrics: {type_from_metrics}")
            return type_from_metrics
    
    # Fallback: Dùng account_type từ database settings
    if fallback_account_type:
        if fallback_account_type == "E-COMMERCE":
            logger.debug(f"Using account_type fallback: ECOMMERCE")
            return 'ECOMMERCE'
        elif fallback_account_type == "LEAD_GENERATION":
            logger.debug(f"Using account_type fallback: LEAD")
            return 'LEAD'
    
    # Mặc định cuối cùng: ECOMMERCE
    logger.debug(f"Could not detect type from objective='{objective}', metrics, or account_type, defaulting to ECOMMERCE")
    return 'ECOMMERCE'


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

