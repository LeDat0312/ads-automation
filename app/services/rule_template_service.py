"""
Rule Template Service
Quản lý và apply rule templates tương tự Madgicx
"""
import logging
from typing import Dict, Any, List, Optional
from app.core.database import get_db_session
from app.models.logic_rule import LogicRule
from app.models.rule_template import RuleTemplate

logger = logging.getLogger(__name__)


def get_all_templates(campaign_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lấy tất cả rule templates
    Filter theo campaign_type nếu có
    """
    db = get_db_session()
    try:
        query = db.query(RuleTemplate).filter(RuleTemplate.enabled == True)
        
        if campaign_type:
            query = query.filter(
                (RuleTemplate.campaign_type == campaign_type) |
                (RuleTemplate.campaign_type == 'BOTH')
            )
        
        templates = query.all()
        
        result = []
        for template in templates:
            result.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "campaign_type": template.campaign_type,
                "template_config": template.template_config,
                "usage_count": template.usage_count
            })
        
        return result
    finally:
        db.close()


def apply_template(
    template_id: int,
    account_id: str,
    prefix: str,
    custom_values: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Apply template cho account/prefix
    Tạo LogicRule từ template
    
    Args:
        template_id: ID của template
        account_id: Account ID
        prefix: Prefix
        custom_values: Custom values để override template (optional)
    
    Returns:
        True nếu thành công
    """
    db = get_db_session()
    try:
        # Lấy template
        template = db.query(RuleTemplate).filter_by(id=template_id).first()
        if not template:
            logger.error(f"Template {template_id} not found")
            return False
        
        config = template.template_config or {}
        conditions = config.get('conditions', {})
        action = config.get('action', 'PAUSE')
        logic_type = config.get('logic_type', 'logic1')
        
        # Apply custom values nếu có
        if custom_values:
            for key, value in custom_values.items():
                if key in conditions:
                    conditions[key]['value'] = value
        
        # Tạo LogicRule từ template
        rule = LogicRule(
            account_id=account_id,
            prefix=prefix,
            giai_doan=config.get('giai_doan', 'GĐ1'),
            logic_type=logic_type,
            action=action,
            enabled=True
        )
        
        # Set conditions
        if 'spend' in conditions:
            rule.condition_spend = conditions['spend'].get('value', 0)
        if 'results' in conditions:
            rule.condition_results = conditions['results'].get('value', 0)
        if 'gia_data' in conditions:
            rule.condition_gia_data = conditions['gia_data'].get('value', 0)
        if 'roas' in conditions:
            # Lưu vào condition_gia_data nếu cần (hoặc tạo field mới)
            rule.condition_gia_data = conditions['roas'].get('value', 0)
        
        db.add(rule)
        
        # Update usage count
        template.usage_count = (template.usage_count or 0) + 1
        
        db.commit()
        logger.info(f"✅ Applied template {template_id} to {account_id}|{prefix}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"🚨 Error applying template: {e}")
        return False
    finally:
        db.close()


def create_template_from_config(config: Dict[str, Any]) -> Optional[int]:
    """
    Tạo template mới từ config
    """
    db = get_db_session()
    try:
        template = RuleTemplate(
            name=config.get('name', 'Untitled Template'),
            description=config.get('description', ''),
            campaign_type=config.get('campaign_type', 'BOTH'),
            template_config=config.get('template_config', {}),
            enabled=True
        )
        
        db.add(template)
        db.commit()
        
        logger.info(f"✅ Created template: {template.name} (ID: {template.id})")
        return template.id
        
    except Exception as e:
        db.rollback()
        logger.error(f"🚨 Error creating template: {e}")
        return None
    finally:
        db.close()


def initialize_default_templates():
    """
    Khởi tạo các template mặc định
    Chạy một lần khi setup
    """
    default_templates = [
        {
            "name": "E-commerce: Tắt khi chi tiêu cao, ROAS thấp",
            "description": "Tắt adset khi chi tiêu > 20,000 và ROAS < 2.0",
            "campaign_type": "ECOMMERCE",
            "template_config": {
                "conditions": {
                    "spend": {"operator": ">", "value": 20000},
                    "roas": {"operator": "<", "value": 2.0}
                },
                "action": "PAUSE",
                "logic_type": "logic1"
            }
        },
        {
            "name": "E-commerce: Tắt khi chi tiêu cao, không có purchase",
            "description": "Tắt adset khi chi tiêu > 15,000 và purchases = 0",
            "campaign_type": "ECOMMERCE",
            "template_config": {
                "conditions": {
                    "spend": {"operator": ">", "value": 15000},
                    "results": {"operator": "==", "value": 0}
                },
                "action": "PAUSE",
                "logic_type": "logic1"
            }
        },
        {
            "name": "Lead: Tắt khi chi tiêu cao, không có lead",
            "description": "Tắt adset khi chi tiêu > 15,000 và leads = 0",
            "campaign_type": "LEAD",
            "template_config": {
                "conditions": {
                    "spend": {"operator": ">", "value": 15000},
                    "results": {"operator": "==", "value": 0}
                },
                "action": "PAUSE",
                "logic_type": "logic1"
            }
        },
        {
            "name": "Lead: Tắt khi chi tiêu cao, giá DATA cao",
            "description": "Tắt adset khi chi tiêu > 20,000 và giá DATA > 15,000",
            "campaign_type": "LEAD",
            "template_config": {
                "conditions": {
                    "spend": {"operator": ">", "value": 20000},
                    "gia_data": {"operator": ">", "value": 15000}
                },
                "action": "PAUSE",
                "logic_type": "logic2"
            }
        }
    ]
    
    db = get_db_session()
    try:
        for template_config in default_templates:
            # Kiểm tra xem đã có chưa
            existing = db.query(RuleTemplate).filter_by(
                name=template_config['name']
            ).first()
            
            if not existing:
                template = RuleTemplate(**template_config)
                db.add(template)
        
        db.commit()
        logger.info("✅ Initialized default templates")
    except Exception as e:
        db.rollback()
        logger.error(f"🚨 Error initializing templates: {e}")
    finally:
        db.close()

