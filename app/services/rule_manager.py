"""
Rule Manager Service
Quản lý logic rules một cách linh hoạt
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.logic_rule import LogicRule
from app.schemas.logic_rule import LogicRuleCreate, LogicRuleUpdate
import logging

logger = logging.getLogger(__name__)


class RuleManager:
    """Service để quản lý logic rules"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_rule(self, rule_data: LogicRuleCreate) -> LogicRule:
        """Tạo rule mới"""
        try:
            rule = LogicRule(
                name=rule_data.name,
                folder=rule_data.folder or "General",
                account_ids=rule_data.account_ids or [],
                prefixes=rule_data.prefixes or [],
                conditions=rule_data.conditions.dict(),
                action=rule_data.action,
                action_params=rule_data.action_params or {},
                schedule=rule_data.schedule or {},
                filters=rule_data.filters or {},
                enabled=rule_data.enabled,
                status=rule_data.status,
                description=rule_data.description
            )
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            logger.info(f"✅ Created rule: {rule.name} (ID: {rule.id})")
            return rule
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating rule: {e}")
            raise
    
    def get_rule(self, rule_id: int) -> Optional[LogicRule]:
        """Lấy rule theo ID"""
        return self.db.query(LogicRule).filter(LogicRule.id == rule_id).first()
    
    def list_rules(
        self,
        folder: Optional[str] = None,
        account_id: Optional[str] = None,
        prefix: Optional[str] = None,
        enabled: Optional[bool] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LogicRule]:
        """List rules với filters"""
        query = self.db.query(LogicRule)
        
        if folder:
            query = query.filter(LogicRule.folder == folder)
        
        if account_id:
            # Filter: account_ids contains account_id OR account_ids is empty (all accounts)
            query = query.filter(
                or_(
                    LogicRule.account_ids.contains([account_id]),
                    LogicRule.account_ids == []
                )
            )
        
        if prefix:
            # Filter: prefixes contains prefix OR prefixes contains None (all prefixes)
            query = query.filter(
                or_(
                    LogicRule.prefixes.contains([prefix]),
                    LogicRule.prefixes.contains([None])
                )
            )
        
        if enabled is not None:
            query = query.filter(LogicRule.enabled == enabled)
        
        if status:
            query = query.filter(LogicRule.status == status.upper())
        
        return query.offset(skip).limit(limit).all()
    
    def update_rule(self, rule_id: int, rule_data: LogicRuleUpdate) -> Optional[LogicRule]:
        """Cập nhật rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        try:
            update_data = rule_data.dict(exclude_unset=True)
            
            # Handle conditions separately (convert to dict)
            if 'conditions' in update_data and update_data['conditions']:
                update_data['conditions'] = update_data['conditions'].dict()
            
            for key, value in update_data.items():
                setattr(rule, key, value)
            
            rule.version += 1
            self.db.commit()
            self.db.refresh(rule)
            logger.info(f"✅ Updated rule: {rule.name} (ID: {rule.id}, version: {rule.version})")
            return rule
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error updating rule {rule_id}: {e}")
            raise
    
    def delete_rule(self, rule_id: int) -> bool:
        """Xóa rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return False
        
        try:
            self.db.delete(rule)
            self.db.commit()
            logger.info(f"✅ Deleted rule: {rule.name} (ID: {rule_id})")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error deleting rule {rule_id}: {e}")
            raise
    
    def toggle_rule(self, rule_id: int) -> Optional[LogicRule]:
        """Bật/tắt rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        try:
            rule.enabled = not rule.enabled
            rule.version += 1
            self.db.commit()
            self.db.refresh(rule)
            logger.info(f"✅ Toggled rule: {rule.name} (ID: {rule_id}, enabled: {rule.enabled})")
            return rule
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error toggling rule {rule_id}: {e}")
            raise
    
    def get_rules_for_account_prefix(
        self,
        account_id: str,
        prefix: Optional[str] = None
    ) -> List[LogicRule]:
        """
        Lấy rules áp dụng cho account_id và prefix
        Dùng trong automation để check logic
        """
        query = self.db.query(LogicRule).filter(
            LogicRule.enabled == True,
            LogicRule.status == "LIVE"
        )
        
        # Filter by account_id
        # account_ids contains account_id OR account_ids is empty (all accounts)
        query = query.filter(
            or_(
                LogicRule.account_ids.contains([account_id]),
                LogicRule.account_ids == []
            )
        )
        
        # Filter by prefix
        if prefix:
            # prefixes contains prefix OR prefixes contains None (all prefixes)
            query = query.filter(
                or_(
                    LogicRule.prefixes.contains([prefix]),
                    LogicRule.prefixes.contains([None])
                )
            )
        
        return query.all()
    
    def get_rules_by_folder(self, folder: str) -> List[LogicRule]:
        """Lấy tất cả rules trong folder"""
        return self.db.query(LogicRule).filter(LogicRule.folder == folder).all()
    
    def count_rules(
        self,
        folder: Optional[str] = None,
        enabled: Optional[bool] = None,
        status: Optional[str] = None
    ) -> int:
        """Đếm số lượng rules"""
        query = self.db.query(LogicRule)
        
        if folder:
            query = query.filter(LogicRule.folder == folder)
        if enabled is not None:
            query = query.filter(LogicRule.enabled == enabled)
        if status:
            query = query.filter(LogicRule.status == status.upper())
        
        return query.count()

