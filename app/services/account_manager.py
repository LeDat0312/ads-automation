# -*- coding: utf-8 -*-
"""
Account Management Service
Advanced filtering, health checks, batch operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from enum import Enum

from app.models.account_prefix import Account, Prefix, AccountPrefix
from app.schemas.account_response import (
    AccountFilterRequest,
    EnhancedAccountResponse,
    AccountHealthEnum,
    AccountStatusEnum,
    AccountSpendingTrend,
    AccountCampaignStats,
    AccountHealthStatus,
)

logger = logging.getLogger(__name__)


class AccountFilterService:
    """Service để filter, search, sort accounts"""
    
    @staticmethod
    def apply_filters(
        db: Session,
        user_id: int,
        filter_req: AccountFilterRequest
    ) -> Tuple[List[Account], int]:
        """
        Apply filters and return paginated results
        
        Returns:
            (accounts, total_count)
        """
        query = db.query(Account).filter(Account.user_id == user_id)
        
        # Filter by status
        if filter_req.status:
            query = query.filter(Account.status == filter_req.status)
        
        # Filter by account_type
        if filter_req.account_type:
            query = query.filter(Account.account_type == filter_req.account_type)
        
        # Filter by enabled status
        if filter_req.enabled_only:
            query = query.filter(Account.enabled == True)
        
        # Filter by spending range
        if filter_req.min_spend is not None:
            query = query.filter(Account.last_30_days_spend >= filter_req.min_spend)
        if filter_req.max_spend is not None:
            query = query.filter(Account.last_30_days_spend <= filter_req.max_spend)
        
        # Search by name or account_id
        if filter_req.search:
            search_term = f"%{filter_req.search}%"
            query = query.filter(
                or_(
                    Account.account_name.ilike(search_term),
                    Account.account_id.ilike(search_term)
                )
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Sorting
        sort_field = getattr(Account, filter_req.sort_by, Account.updated_at)
        sort_direction = desc if filter_req.sort_order == "desc" else asc
        query = query.order_by(sort_direction(sort_field))
        
        # Pagination
        offset = (filter_req.page - 1) * filter_req.page_size
        accounts = query.offset(offset).limit(filter_req.page_size).all()
        
        return accounts, total
    
    @staticmethod
    def get_account_prefixes(db: Session, account_id: int) -> List[str]:
        """Get prefixes linked to account"""
        prefixes = db.query(Prefix.prefix).join(
            AccountPrefix,
            AccountPrefix.prefix_id == Prefix.id
        ).filter(
            AccountPrefix.account_id == account_id,
            Prefix.enabled == True
        ).all()
        return [p[0] for p in prefixes]


class AccountHealthService:
    """Service để check account health"""
    
    @staticmethod
    def check_account_health(account: Account) -> AccountHealthStatus:
        """
        Check account health status
        
        Rules:
        - HEALTHY: Last synced < 24 hours, token valid, has activity
        - WARNING: Last synced 1-7 days, low spending, or token expiring soon
        - CRITICAL: Last synced > 7 days, token invalid, or no activity
        """
        issues = []
        status = AccountHealthEnum.HEALTHY
        
        # Check sync recency
        if account.updated_at:
            hours_since_sync = (datetime.now() - account.updated_at).total_seconds() / 3600
            if hours_since_sync > 168:  # 7 days
                issues.append(f"Không sync {int(hours_since_sync // 24)} ngày")
                status = AccountHealthEnum.CRITICAL
            elif hours_since_sync > 24:  # 1 day
                issues.append(f"Sync gần đây nhất {int(hours_since_sync)} giờ")
                if status != AccountHealthEnum.CRITICAL:
                    status = AccountHealthEnum.WARNING
        
        # Check if account is paused
        if account.status == AccountStatusEnum.PAUSED.value:
            issues.append("Account tạm dừng")
            if status != AccountHealthEnum.CRITICAL:
                status = AccountHealthEnum.WARNING
        
        # Check spending (if no spend in 7 days)
        if account.last_30_days_spend == 0:
            issues.append("Không có chi tiêu 30 ngày")
            if status == AccountHealthEnum.HEALTHY:
                status = AccountHealthEnum.WARNING
        
        # Check if archived
        if account.status == AccountStatusEnum.ARCHIVED.value:
            issues.append("Account đã lưu trữ")
            status = AccountHealthEnum.CRITICAL
        
        return AccountHealthStatus(
            status=status,
            issues=issues,
            last_check=datetime.now()
        )
    
    @staticmethod
    def calculate_spending_trend(
        account: Account,
        db: Session
    ) -> AccountSpendingTrend:
        """
        Calculate spending trend
        Note: Cần extend Account model để track daily spend history
        Hiện tại chỉ tính từ last_30_days_spend
        """
        spend_30days = account.last_30_days_spend or 0
        
        # Estimate: assume spending is fairly constant
        # In future: fetch from Facebook or calculate from ads_metrics
        avg_daily = spend_30days / 30 if spend_30days > 0 else 0
        spend_7days = avg_daily * 7
        
        # Determine trend
        trend = "STABLE"  # In future: compare with previous period
        
        return AccountSpendingTrend(
            spend_7days=spend_7days,
            spend_30days=spend_30days,
            avg_daily_spend=avg_daily,
            trend_direction=trend
        )
    
    @staticmethod
    def build_campaign_stats(account: Account, db: Session) -> AccountCampaignStats:
        """
        Calculate campaign statistics
        Note: Cần query từ ads_metrics table
        """
        # TODO: Query ads_metrics untuk campaign stats
        return AccountCampaignStats(
            total_campaigns=0,
            active_campaigns=0,
            paused_campaigns=0,
            archived_campaigns=0
        )


class AccountBatchService:
    """Service để batch operations trên accounts"""
    
    @staticmethod
    def bulk_update(
        db: Session,
        user_id: int,
        account_ids: List[int],
        updates: Dict[str, Any]
    ) -> int:
        """
        Bulk update accounts
        
        Returns: số accounts được update
        """
        # Validate: chỉ update accounts của user này
        accounts = db.query(Account).filter(
            Account.user_id == user_id,
            Account.id.in_(account_ids)
        ).all()
        
        if len(accounts) != len(account_ids):
            raise ValueError("Some accounts not found or not owned by user")
        
        # Allowed fields
        allowed_fields = ['enabled', 'timezone', 'currency', 'account_type', 'status', 'description']
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not filtered_updates:
            return 0
        
        # Update each account
        for account in accounts:
            for key, value in filtered_updates.items():
                setattr(account, key, value)
            account.updated_at = datetime.now()
        
        db.commit()
        return len(accounts)
    
    @staticmethod
    def bulk_delete(
        db: Session,
        user_id: int,
        account_ids: List[int]
    ) -> int:
        """
        Bulk delete accounts
        
        Returns: số accounts bị xóa
        """
        # Validate: chỉ delete accounts của user này
        accounts = db.query(Account).filter(
            Account.user_id == user_id,
            Account.id.in_(account_ids)
        ).all()
        
        if len(accounts) != len(account_ids):
            raise ValueError("Some accounts not found or not owned by user")
        
        # Delete linked prefixes
        for account in accounts:
            db.query(AccountPrefix).filter(
                AccountPrefix.account_id == account.id
            ).delete()
        
        # Delete accounts
        for account in accounts:
            db.delete(account)
        
        db.commit()
        return len(accounts)
    
    @staticmethod
    def bulk_enable(db: Session, user_id: int, account_ids: List[int]) -> int:
        """Enable multiple accounts"""
        return AccountBatchService.bulk_update(
            db, user_id, account_ids, {'enabled': True}
        )
    
    @staticmethod
    def bulk_disable(db: Session, user_id: int, account_ids: List[int]) -> int:
        """Disable multiple accounts"""
        return AccountBatchService.bulk_update(
            db, user_id, account_ids, {'enabled': False}
        )


class AccountExportService:
    """Service để export account data"""
    
    @staticmethod
    def export_to_csv(accounts: List[Account]) -> str:
        """
        Export accounts to CSV format
        
        Returns: CSV string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        headers = [
            'Account ID', 'Name', 'Type', 'Status', 'Enabled',
            'Timezone', 'Currency', '30-Day Spend', 'Created', 'Updated'
        ]
        writer.writerow(headers)
        
        # Rows
        for acc in accounts:
            writer.writerow([
                acc.account_id,
                acc.account_name or '',
                acc.account_type,
                acc.status,
                'Yes' if acc.enabled else 'No',
                acc.timezone,
                acc.currency,
                f"{acc.last_30_days_spend:.2f}",
                acc.created_at.isoformat() if acc.created_at else '',
                acc.updated_at.isoformat() if acc.updated_at else ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_to_json(accounts: List[Account], db: Session = None) -> List[Dict[str, Any]]:
        """Export accounts to JSON format"""
        result = []
        for acc in accounts:
            data = {
                'id': acc.id,
                'account_id': acc.account_id,
                'name': acc.account_name,
                'type': acc.account_type,
                'status': acc.status,
                'enabled': acc.enabled,
                'timezone': acc.timezone,
                'currency': acc.currency,
                'spend_30days': acc.last_30_days_spend,
                'created_at': acc.created_at.isoformat() if acc.created_at else None,
                'updated_at': acc.updated_at.isoformat() if acc.updated_at else None,
            }
            if db:
                prefixes = AccountFilterService.get_account_prefixes(db, acc.id)
                data['prefixes'] = prefixes
            result.append(data)
        return result
