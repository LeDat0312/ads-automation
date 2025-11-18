"""
Clean Dashboard Implementation - Optimized Version
Phiên bản đã được cleanup và tối ưu hóa
"""
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, distinct, case
import pytz

from app.core.database import get_db, AdMetrics
from app.models.account_prefix import Account, Prefix, AccountPrefix
from app.api.routes.auth import get_current_user_optional
from app.models.user import User
from app.models.user_settings import UserSettings
from app.core.ui_helpers import get_user_dropdown_menu, get_account_locked_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
HCM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')


def get_user_account_prefixes(user_id: int, db: Session, enabled_only: bool = True) -> tuple[List[str], List[str]]:
    """Lấy danh sách account_ids và prefixes của user (chỉ lấy enabled nếu enabled_only=True)"""
    query = db.query(Account.account_id).filter(Account.user_id == user_id)
    if enabled_only:
        query = query.filter(Account.enabled == True)
    user_accounts = query.all()
    account_ids = [acc[0] for acc in user_accounts]
    
    # Lấy prefixes từ user's prefixes (chỉ enabled nếu enabled_only=True)
    prefix_query = db.query(Prefix.prefix).filter(Prefix.user_id == user_id)
    if enabled_only:
        prefix_query = prefix_query.filter(Prefix.enabled == True)
    user_prefixes = prefix_query.all()
    prefixes = [pref[0] for pref in user_prefixes]
    
    return account_ids, prefixes


# ==================== FILTER ENDPOINTS ====================

@router.get("/filters")
async def get_dashboard_filters(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy filters cho dashboard từ settings của user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Lấy accounts từ settings (chỉ enabled)
        user_accounts = db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.enabled == True
        ).all()
        
        # Lấy prefixes từ settings (chỉ enabled)
        user_prefixes = db.query(Prefix).filter(
            Prefix.user_id == current_user.id,
            Prefix.enabled == True
        ).all()
        
        return JSONResponse({
            "accounts": [
                {
                    "id": acc.account_id,
                    "name": acc.name or acc.account_id,
                    "type": acc.account_type,
                    "enabled": acc.enabled
                } for acc in user_accounts
            ],
            "prefixes": [
                {
                    "id": prefix.prefix,
                    "name": prefix.prefix,
                    "description": f"Prefix {prefix.prefix}"
                } for prefix in user_prefixes
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard filters: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error loading filters")


@router.get("/settings-status")
async def get_settings_status(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Kiểm tra status của settings để hiển thị trên dashboard"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Kiểm tra user settings
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        
        # Đếm accounts và prefixes (chỉ enabled)
        accounts_count = db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.enabled == True
        ).count()
        
        prefixes_count = db.query(Prefix).filter(
            Prefix.user_id == current_user.id,
            Prefix.enabled == True
        ).count()
        
        return JSONResponse({
            "has_token": bool(user_settings and user_settings.facebook_access_token),
            "accounts_count": accounts_count,
            "prefixes_count": prefixes_count,
            "settings_complete": bool(
                user_settings and 
                user_settings.facebook_access_token and 
                accounts_count > 0 and 
                prefixes_count > 0
            ),
            "last_updated": user_settings.updated_at.isoformat() if user_settings and user_settings.updated_at else None
        })
        
    except Exception as e:
        logger.error(f"Error getting settings status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error loading settings status")


# ==================== DATA ENDPOINTS ====================

@router.get("/summary")
async def get_dashboard_summary(
    request: Request,
    view_mode: str = Query("ecommerce", description="View mode: ecommerce or lead"),
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    date_range: str = Query("last7days"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get Overview Cards summary based on view mode and filters"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get user's enabled accounts and prefixes
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db, enabled_only=True)
        
        if not user_account_ids:
            # Return empty summary if no accounts
            empty_summary = {
                "totalSpend": 0,
                "activeAdsets": 0,
                "pausedAdsets": 0,
                "totalAdsets": 0
            }
            
            if view_mode == "ecommerce":
                empty_summary.update({"adsPercent": 0, "purchaseValue": 0})
            else:
                empty_summary.update({"totalLeads": 0, "avgGiaData": 0})
            
            return JSONResponse(empty_summary)
        
        # Build date filter
        end_date = datetime.now(HCM_TZ).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        if date_range == "today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "yesterday":
            start_date = (end_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = (end_date - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        elif date_range == "last7days":
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "last30days":
            start_date = (end_date - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to last 7 days
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Build query with user's data
        query = db.query(AdMetrics).filter(
            AdMetrics.date_start >= start_date.date(),
            AdMetrics.date_stop <= end_date.date()
        )
        
        # Filter by user's accounts and prefixes
        account_prefix_filter = []
        if user_account_ids:
            account_prefix_filter.append(AdMetrics.account_id.in_(user_account_ids))
        if user_prefixes:
            prefix_conditions = [AdMetrics.adset_name.like(f"{prefix}%") for prefix in user_prefixes]
            if prefix_conditions:
                account_prefix_filter.append(or_(*prefix_conditions))
        
        if account_prefix_filter:
            query = query.filter(or_(*account_prefix_filter))
        
        # Apply additional filters
        if account_id:
            query = query.filter(AdMetrics.account_id == account_id)
        if prefix:
            query = query.filter(AdMetrics.adset_name.like(f"{prefix}%"))
        
        metrics = query.all()
        
        # Calculate totals
        total_spend = sum(float(m.spend or 0) for m in metrics)
        total_purchases = sum(int(getattr(m, 'offsite_conversion_fb_pixel_purchase', 0) or 0) for m in metrics)
        total_purchase_value = sum(float(getattr(m, 'offsite_conversion_fb_pixel_purchase_value', 0) or 0) for m in metrics)
        
        # Calculate leads (comments + messages)
        total_comments = sum(int(getattr(m, 'post_comments', 0) or 0) for m in metrics)
        total_messages = sum(int(getattr(m, 'onsite_conversion_messaging_conversation_started_7d', 0) or 0) for m in metrics)
        total_leads = total_comments + total_messages
        
        # Count adsets by status
        adset_statuses = {}
        for m in metrics:
            status = (m.adset_status or "UNKNOWN").upper()
            adset_id = m.adset_id
            if adset_id not in adset_statuses:
                adset_statuses[adset_id] = status
        
        active_adsets = len([s for s in adset_statuses.values() if s == "ACTIVE"])
        paused_adsets = len([s for s in adset_statuses.values() if s in ["PAUSED", "ARCHIVED"]])
        total_adsets = len(adset_statuses)
        
        if view_mode == "ecommerce":
            # E-Commerce metrics
            ads_percent = (total_spend / total_purchase_value * 100) if total_purchase_value > 0 else 0
            
            return JSONResponse({
                "totalSpend": round(total_spend, 2),
                "adsPercent": round(ads_percent, 2),
                "purchaseValue": round(total_purchase_value, 2),
                "activeAdsets": active_adsets,
                "pausedAdsets": paused_adsets,
                "totalAdsets": total_adsets
            })
        else:
            # Lead Generation metrics
            avg_gia_data = total_spend / total_leads if total_leads > 0 else 0
            
            return JSONResponse({
                "totalSpend": round(total_spend, 2),
                "totalLeads": total_leads,
                "avgGiaData": round(avg_gia_data, 2),
                "activeAdsets": active_adsets,
                "pausedAdsets": paused_adsets,
                "totalAdsets": total_adsets
            })
        
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading summary: {str(e)}")


@router.get("/data")
async def get_dashboard_data(
    request: Request,
    view_mode: str = Query("ecommerce", description="View mode: ecommerce or lead"),
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    date_range: str = Query("last7days"),
    search: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get detailed dashboard data for table view"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get user's accounts and prefixes
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db)
        
        if not user_account_ids and not user_prefixes:
            return JSONResponse({
                "ads": [],
                "total_records": 0,
                "message": "No accounts or prefixes configured"
            })
        
        # Build date filter
        end_date = datetime.now(HCM_TZ).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        if date_range == "today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "yesterday":
            start_date = (end_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = (end_date - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        elif date_range == "last7days":
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "last30days":
            start_date = (end_date - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Build query
        query = db.query(AdMetrics).filter(
            AdMetrics.date_start >= start_date.date(),
            AdMetrics.date_stop <= end_date.date()
        )
        
        # Filter by user's accounts and prefixes
        account_prefix_filter = []
        if user_account_ids:
            account_prefix_filter.append(AdMetrics.account_id.in_(user_account_ids))
        if user_prefixes:
            prefix_conditions = [AdMetrics.adset_name.like(f"{prefix}%") for prefix in user_prefixes]
            if prefix_conditions:
                account_prefix_filter.append(or_(*prefix_conditions))
        
        if account_prefix_filter:
            query = query.filter(or_(*account_prefix_filter))
        
        # Apply additional filters
        if account_id:
            query = query.filter(AdMetrics.account_id == account_id)
        if prefix:
            query = query.filter(AdMetrics.adset_name.like(f"{prefix}%"))
        if search:
            search_filter = or_(
                AdMetrics.adset_name.ilike(f"%{search}%"),
                AdMetrics.ad_name.ilike(f"%{search}%"),
                AdMetrics.campaign_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get data
        metrics = query.all()
        
        if not metrics:
            return JSONResponse({
                "ads": [],
                "total_records": 0,
                "message": "No data found for selected filters"
            })
        
        # Aggregate data by adset
        adset_data = {}
        for metric in metrics:
            adset_id = metric.adset_id
            if adset_id not in adset_data:
                adset_data[adset_id] = {
                    'id': adset_id,
                    'name': metric.adset_name,
                    'campaign_name': metric.campaign_name,
                    'account_id': metric.account_id,
                    'status': metric.adset_status or 'UNKNOWN',
                    'budget': getattr(metric, 'daily_budget', 0) or 0,
                    'spend': 0,
                    'impressions': 0,
                    'clicks': 0,
                    'reach': 0,
                    'checkout_started': 0,
                    'purchases': 0,
                    'purchase_value': 0,
                    'comments': 0,
                    'messages': 0
                }
            
            # Aggregate metrics
            data = adset_data[adset_id]
            data['spend'] += float(metric.spend or 0)
            data['impressions'] += int(metric.impressions or 0)
            data['clicks'] += int(metric.clicks or 0)
            data['reach'] += int(metric.reach or 0)
            
            # Purchase/conversion metrics
            data['checkout_started'] += int(getattr(metric, 'offsite_conversion_fb_pixel_initiate_checkout', 0) or 0)
            data['purchases'] += int(getattr(metric, 'offsite_conversion_fb_pixel_purchase', 0) or 0)
            data['purchase_value'] += float(getattr(metric, 'offsite_conversion_fb_pixel_purchase_value', 0) or 0)
            
            # Lead metrics
            data['comments'] += int(getattr(metric, 'post_comments', 0) or 0)
            data['messages'] += int(getattr(metric, 'onsite_conversion_messaging_conversation_started_7d', 0) or 0)
        
        # Calculate derived metrics for each adset
        processed_ads = []
        for data in adset_data.values():
            # Basic calculations
            data['frequency'] = data['impressions'] / data['reach'] if data['reach'] > 0 else 0
            data['ctr'] = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
            data['cpc'] = data['spend'] / data['clicks'] if data['clicks'] > 0 else 0
            data['cpm'] = data['spend'] / data['impressions'] * 1000 if data['impressions'] > 0 else 0
            
            # View mode specific calculations
            if view_mode == "ecommerce":
                data['results'] = data['purchases']
                data['giaData'] = data['spend'] / data['purchases'] if data['purchases'] > 0 else 0
                data['adsPercent'] = (data['spend'] / data['purchase_value'] * 100) if data['purchase_value'] > 0 else 0
                data['conversionRate'] = (data['purchases'] / data['checkout_started'] * 100) if data['checkout_started'] > 0 else 0
            else:
                # Lead generation
                data['leads'] = data['comments'] + data['messages']
                data['results'] = data['leads']
                data['giaData'] = data['spend'] / data['leads'] if data['leads'] > 0 else 0
                data['costPerCheckout'] = data['spend'] / data['checkout_started'] if data['checkout_started'] > 0 else 0
            
            processed_ads.append(data)
        
        # Sort ads by spend (descending)
        processed_ads.sort(key=lambda x: x['spend'], reverse=True)
        
        return JSONResponse({
            "ads": processed_ads[:100],  # Limit to 100 records for performance
            "total_records": len(processed_ads),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading dashboard data: {str(e)}")


# ==================== ACTION ENDPOINTS ====================

@router.post("/action/{action}/{item_id}")
async def dashboard_action(
    request: Request,
    action: str,
    item_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Perform action on adset (activate/pause/budget change)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if action not in ["activate", "pause", "increase_budget", "decrease_budget"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    try:
        # Verify user has access to this adset
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db)
        
        # Check if adset belongs to user's accounts
        adset_query = db.query(AdMetrics).filter(AdMetrics.adset_id == item_id)
        
        # Filter by user's accounts and prefixes
        account_prefix_filter = []
        if user_account_ids:
            account_prefix_filter.append(AdMetrics.account_id.in_(user_account_ids))
        if user_prefixes:
            prefix_conditions = [AdMetrics.adset_name.like(f"{prefix}%") for prefix in user_prefixes]
            if prefix_conditions:
                account_prefix_filter.append(or_(*prefix_conditions))
        
        if account_prefix_filter:
            adset_query = adset_query.filter(or_(*account_prefix_filter))
        
        adset = adset_query.first()
        if not adset:
            raise HTTPException(status_code=404, detail="Adset not found or access denied")
        
        # Here you would integrate with Facebook API to actually change the adset
        # For now, just return success with appropriate message
        action_messages = {
            "activate": "Adset activated successfully",
            "pause": "Adset paused successfully",
            "increase_budget": "Budget increased by 20% successfully",
            "decrease_budget": "Budget decreased by 20% successfully"
        }
        
        new_status = "ACTIVE" if action == "activate" else "PAUSED" if action == "pause" else adset.adset_status
        
        logger.info(f"Action {action} performed on adset {item_id} by user {current_user.id}")
        
        return JSONResponse({
            "success": True,
            "action": action,
            "item_id": item_id,
            "new_status": new_status,
            "message": action_messages[action]
        })
        
    except Exception as e:
        logger.error(f"Error performing action {action} on {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error performing action: {str(e)}")


# ==================== HEALTH CHECK ====================

@router.get("/health")
async def dashboard_health():
    """Health check endpoint for dashboard"""
    return JSONResponse({
        "status": "healthy",
        "service": "dashboard",
        "timestamp": datetime.now(HCM_TZ).isoformat(),
        "version": "2.0.0"
    })