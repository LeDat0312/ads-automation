"""
Modern Facebook Ads Dashboard API - Backend Only (No UI)
Refactored for React/SPA frontend
"""
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dataclasses import dataclass
import pytz
from pydantic import BaseModel

from app.core.database import get_db
from app.models.account_prefix import Account
from app.api.routes.auth import get_current_user_optional
from app.models.user import User
from app.models.user_settings import UserSettings
from app.services.facebook_api import (
    pull_facebook_data_async,
    fetch_adset_statuses,
    pause_adsets,
    resume_adsets,
    update_adset_budget,
    update_campaign_budget
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Timezone Hồ Chí Minh
HCM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Cache for Facebook API data (TTL 60s)
@dataclass
class CachedResult:
    timestamp: datetime
    data: List[Dict[str, Any]]

_insights_cache: Dict[Tuple, CachedResult] = {}
CACHE_TTL_SECONDS = 60


# ============================================================================
# Helper Functions - Token & Account Management
# ============================================================================

def get_user_access_token(user_id: int, db: Session) -> Optional[str]:
    """Get Facebook access token from UserSettings (decrypt if needed)"""
    from app.core.security import decrypt_token
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if user_settings and user_settings.facebook_token_encrypted:
        try:
            token = decrypt_token(user_settings.facebook_token_encrypted)
            return token
        except Exception as e:
            logger.error(f"Error decrypting token for user {user_id}: {e}")
            return None
    return None


def get_user_accounts_by_view_mode(
    user_id: int, 
    db: Session, 
    view_mode: str, 
    enabled_only: bool = True
) -> Dict[str, str]:
    """
    Get account_type_map for user filtered by view_mode
    
    Returns:
        Dict[account_id, account_type] - clean account ID (without 'act_' prefix)
    """
    query = db.query(Account.account_id, Account.account_type).filter(
        Account.user_id == user_id
    )
    
    if enabled_only:
        query = query.filter(Account.enabled == True)
    
    if view_mode == "lead":
        query = query.filter(Account.account_type == "LEAD_GENERATION")
    elif view_mode == "ecommerce":
        query = query.filter(Account.account_type == "E-COMMERCE")
    
    account_type_map = {}
    for acc_id, acc_type in query.all():
        clean_id = acc_id.replace('act_', '')
        account_type_map[clean_id] = acc_type
    
    logger.info(f"📋 account_type_map for view_mode={view_mode}: {len(account_type_map)} accounts")
    return account_type_map


# ============================================================================
# Helper Functions - Facebook API with Cache
# ============================================================================

async def get_insights_cached(
    access_token: str,
    account_ids: List[str],
    date_from: Optional[str],
    date_to: Optional[str],
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Get insights from Facebook API with cache (TTL 60s)
    """
    cache_key = (
        date_from or '',
        date_to or '',
        tuple(sorted(account_ids))
    )
    
    if use_cache:
        now = datetime.now()
        cached = _insights_cache.get(cache_key)
        if cached:
            age_seconds = (now - cached.timestamp).total_seconds()
            if age_seconds < CACHE_TTL_SECONDS:
                logger.info(f"✅ Cache hit! Age: {age_seconds:.1f}s")
                return cached.data
            else:
                logger.info(f"⏰ Cache expired (age: {age_seconds:.1f}s)")
                del _insights_cache[cache_key]
    
    logger.info(f"📥 Fetching from Facebook API...")
    all_data = await pull_facebook_data_async(
        access_token,
        account_ids,
        date_preset=None,
        date_from=date_from,
        date_to=date_to,
        account_type_map=None  # Don't filter here, we'll filter after
    )
    
    # Cache result
    _insights_cache[cache_key] = CachedResult(
        timestamp=datetime.now(),
        data=all_data
    )
    
    logger.info(f"✅ Fetched {len(all_data)} rows from Facebook API")
    return all_data


# ============================================================================
# Helper Functions - Build Adset Map (Core Logic)
# ============================================================================

def build_adset_map(
    raw_rows: List[dict],
    statuses: Dict[str, dict],
    view_mode: str
) -> Dict[str, dict]:
    """
    Group data by adset_id and calculate all metrics for both Lead & E-Commerce
    
    Args:
        raw_rows: Raw data from Facebook API (may have multiple ads per adset)
        statuses: {adset_id: {configured_status, effective_status, ...}}
        view_mode: "lead" or "ecommerce"
    
    Returns:
        Dict[adset_id, adset_data] - One entry per unique adset
    """
    adset_map = {}
    
    for row in raw_rows:
        adset_id = row.get('adset_id')
        if not adset_id:
            continue
        
        if adset_id not in adset_map:
            # Initialize adset entry
            adset = {
                # Basic info
                'adset_id': adset_id,
                'adset_name': row.get('adset_name', ''),
                'campaign_id': row.get('campaign_id', ''),
                'campaign_name': row.get('campaign_name', ''),
                'account_id': row.get('account_id', ''),
                'prefix': row.get('prefix'),
                'budget': float(row.get('daily_budget', 0) or 0),
                'currency': row.get('account_currency', 'VND'),
                
                # Common metrics
                'spend': 0.0,
                'impressions': 0,
                'clicks': 0,
                'reach': 0,
                
                # Lead metrics
                'comments': 0,  # Post comments
                'messages': 0,  # Messaging conversations started
                'checkouts': 0,  # Checkouts initiated
                'purchase_count': 0,  # Purchases
                'purchase_value': 0.0,  # Purchase value
                
                # Status (from statuses dict)
                'configured_status': 'UNKNOWN',
                'effective_status': 'UNKNOWN',
                'campaign_configured_status': 'UNKNOWN',
                'campaign_effective_status': 'UNKNOWN',
                'ran_today': False,
                'is_active_now': False,
            }
            adset_map[adset_id] = adset
        
        # Aggregate metrics
        adset = adset_map[adset_id]
        adset['spend'] += float(row.get('spend', 0) or 0)
        adset['impressions'] += int(row.get('impressions', 0) or 0)
        adset['clicks'] += int(row.get('clicks', 0) or 0)
        adset['reach'] += int(row.get('reach', 0) or 0)
        
        # Parse actions for Lead metrics
        actions = row.get('actions') or []
        action_values = {}
        
        for action in actions:
            action_type = action.get('action_type', '')
            value = float(action.get('value', 0) or 0)
            action_values[action_type] = action_values.get(action_type, 0) + value
        
        # Comments: post_comment or comment
        adset['comments'] += action_values.get('post_comment', 0)
        adset['comments'] += action_values.get('comment', 0)
        
        # Messages: messaging conversation started
        adset['messages'] += action_values.get('onsite_conversion.messaging_conversation_started_7d', 0)
        adset['messages'] += action_values.get('messaging_conversation_started', 0)
        
        # Checkouts: initiate checkout
        adset['checkouts'] += action_values.get('offsite_conversion.fb_pixel_initiate_checkout', 0)
        adset['checkouts'] += action_values.get('initiate_checkout', 0)
        
        # Purchases
        adset['purchase_count'] += action_values.get('purchase', 0)
        adset['purchase_count'] += action_values.get('offsite_conversion.fb_pixel_purchase', 0)
        
        # Purchase value
        purchase_value = 0.0
        action_value_objs = row.get('action_values') or []
        for av in action_value_objs:
            if 'purchase' in av.get('action_type', '').lower():
                purchase_value += float(av.get('value', 0) or 0)
        adset['purchase_value'] += purchase_value
    
    # Update status from statuses dict
    for adset_id, adset in adset_map.items():
        status_info = statuses.get(adset_id, {})
        adset['configured_status'] = status_info.get('configured_status', 'UNKNOWN')
        adset['effective_status'] = status_info.get('effective_status', 'UNKNOWN')
        adset['campaign_configured_status'] = status_info.get('campaign_configured_status', 'UNKNOWN')
        adset['campaign_effective_status'] = status_info.get('campaign_effective_status', 'UNKNOWN')
        
        # Calculate flags
        adset['ran_today'] = adset['impressions'] > 0 or adset['spend'] > 0
        adset['is_active_now'] = adset['effective_status'] == 'ACTIVE'
        
        # Calculate derived metrics
        adset['results'] = adset['comments'] + adset['messages']  # DATA = comments + messages
        adset['data_cost'] = adset['spend'] / adset['results'] if adset['results'] > 0 else 0.0
        adset['cost_per_checkout_initiated'] = adset['spend'] / adset['checkouts'] if adset['checkouts'] > 0 else 0.0
        adset['cost_per_purchase'] = adset['spend'] / adset['purchase_count'] if adset['purchase_count'] > 0 else 0.0
        
        # E-Commerce specific
        if view_mode == "ecommerce":
            adset['ads_percent'] = (adset['spend'] / adset['purchase_value'] * 100) if adset['purchase_value'] > 0 else 0.0
        
        # Additional metrics
        adset['cpm'] = (adset['spend'] / adset['impressions'] * 1000) if adset['impressions'] > 0 else 0.0
        adset['ctr'] = (adset['clicks'] / adset['impressions'] * 100) if adset['impressions'] > 0 else 0.0
        adset['cpc'] = (adset['spend'] / adset['clicks']) if adset['clicks'] > 0 else 0.0
        
        # TLC (Total Lead Cost) for E-Commerce - optional metric
        if view_mode == "ecommerce":
            total_leads = adset['checkouts'] + adset['purchase_count']
            adset['tlc'] = adset['spend'] / total_leads if total_leads > 0 else 0.0
    
    logger.info(f"📊 Built adset_map: {len(adset_map)} unique adsets from {len(raw_rows)} rows")
    return adset_map


# ============================================================================
# Helper Functions - Summary Calculation
# ============================================================================

def build_lead_summary(adsets: Dict[str, dict]) -> dict:
    """
    Build summary for Lead Generation view
    
    Summary includes:
    - Tổng Chi Tiêu (total spend)
    - Tổng DATA (comments + messages)
    - Chi phí/DATA (cost per DATA)
    - Bắt Đầu Thanh Toán (checkouts initiated)
    - Lượt Mua (purchases)
    - Chi phí/Lượt Mua (cost per purchase)
    - Adsets counts
    """
    total_spend = sum(a['spend'] for a in adsets.values())
    total_data = sum(a['results'] for a in adsets.values())  # comments + messages
    total_checkouts = sum(a['checkouts'] for a in adsets.values())
    total_purchases = sum(a['purchase_count'] for a in adsets.values())
    
    cost_per_data = total_spend / total_data if total_data > 0 else 0.0
    cost_per_checkout = total_spend / total_checkouts if total_checkouts > 0 else 0.0
    cost_per_purchase = total_spend / total_purchases if total_purchases > 0 else 0.0
    
    total_adsets = len(adsets)
    active_adsets = sum(1 for a in adsets.values() if a['is_active_now'])
    paused_adsets = total_adsets - active_adsets
    ran_today_count = sum(1 for a in adsets.values() if a['ran_today'])
    
    logger.info(
        f"📊 LEAD SUMMARY | adsets={total_adsets}, ran_today={ran_today_count}, "
        f"active={active_adsets}, paused={paused_adsets}, spend={total_spend:.2f}, data={total_data}"
    )
    
    return {
        "totalSpend": round(total_spend, 2),
        "totalData": total_data,
        "costPerData": round(cost_per_data, 2),
        "totalCheckouts": total_checkouts,
        "costPerCheckout": round(cost_per_checkout, 2),
        "totalPurchases": total_purchases,
        "costPerPurchase": round(cost_per_purchase, 2),
        "activeAdsets": active_adsets,
        "pausedAdsets": paused_adsets,
        "totalAdsets": total_adsets,
        "adsetsRanToday": ran_today_count
    }


def build_ecommerce_summary(adsets: Dict[str, dict]) -> dict:
    """
    Build summary for E-Commerce view
    
    Summary includes:
    - Tổng Chi Tiêu (total spend)
    - Giá trị chuyển đổi (purchase value)
    - % ADS (spend / purchase value * 100)
    - Bắt Đầu Thanh Toán (checkouts)
    - Lượt Mua (purchases)
    - Chi phí/Lượt Mua (cost per purchase)
    - Adsets counts
    """
    total_spend = sum(a['spend'] for a in adsets.values())
    total_purchase_value = sum(a['purchase_value'] for a in adsets.values())
    total_checkouts = sum(a['checkouts'] for a in adsets.values())
    total_purchases = sum(a['purchase_count'] for a in adsets.values())
    
    ads_percent = (total_spend / total_purchase_value * 100) if total_purchase_value > 0 else 0.0
    cost_per_purchase = total_spend / total_purchases if total_purchases > 0 else 0.0
    
    total_adsets = len(adsets)
    active_adsets = sum(1 for a in adsets.values() if a['is_active_now'])
    paused_adsets = total_adsets - active_adsets
    ran_today_count = sum(1 for a in adsets.values() if a['ran_today'])
    
    logger.info(
        f"📊 ECOMMERCE SUMMARY | adsets={total_adsets}, ran_today={ran_today_count}, "
        f"active={active_adsets}, paused={paused_adsets}, spend={total_spend:.2f}, "
        f"purchase_value={total_purchase_value:.2f}, ads%={ads_percent:.2f}"
    )
    
    return {
        "totalSpend": round(total_spend, 2),
        "purchaseValue": round(total_purchase_value, 2),
        "adsPercent": round(ads_percent, 2),
        "totalCheckouts": total_checkouts,
        "totalPurchases": total_purchases,
        "costPerPurchase": round(cost_per_purchase, 2),
        "activeAdsets": active_adsets,
        "pausedAdsets": paused_adsets,
        "totalAdsets": total_adsets,
        "adsetsRanToday": ran_today_count
    }


# ============================================================================
# Helper Functions - Table Filtering & Sorting
# ============================================================================

def filter_table_adsets(
    adsets: List[dict],
    prefix: Optional[str],
    status: Optional[str],
    search: Optional[str],
    campaign_id: Optional[str],
    adset_id: Optional[str]
) -> List[dict]:
    """
    Filter adsets for table display
    
    Filters:
    - prefix: Filter by prefix (FL, PX, TL, NM...)
    - status: ACTIVE / PAUSED / RAN_TODAY / None (all)
    - search: Search in adset_name, campaign_name, or IDs
    - campaign_id: Filter by campaign (drill-down)
    - adset_id: Filter by specific adset (drill-down, NOT for debug)
    """
    rows = adsets
    
    # 1. Prefix filter
    if prefix:
        rows = [a for a in rows if (a.get('prefix') or '').startswith(prefix)]
        logger.info(f"   Filter prefix={prefix}: {len(rows)} rows")
    
    # 2. Status filter
    if status:
        if status == "ACTIVE":
            rows = [a for a in rows if a.get('is_active_now')]
        elif status == "PAUSED":
            rows = [a for a in rows if not a.get('is_active_now')]
        elif status == "RAN_TODAY":
            rows = [a for a in rows if a.get('ran_today')]
        logger.info(f"   Filter status={status}: {len(rows)} rows")
    
    # 3. Search filter
    if search:
        search_lower = search.lower()
        rows = [
            a for a in rows
            if search_lower in (a.get('adset_name') or '').lower()
            or search_lower in (a.get('campaign_name') or '').lower()
            or search_lower in str(a.get('adset_id') or '')
            or search_lower in str(a.get('campaign_id') or '')
        ]
        logger.info(f"   Filter search='{search}': {len(rows)} rows")
    
    # 4. Campaign drill-down
    if campaign_id:
        rows = [a for a in rows if a.get('campaign_id') == campaign_id]
        logger.info(f"   Filter campaign_id={campaign_id}: {len(rows)} rows")
    
    # 5. Adset drill-down (NOT for debug)
    if adset_id:
        rows = [a for a in rows if str(a.get('adset_id')) == str(adset_id)]
        logger.info(f"   Filter adset_id={adset_id}: {len(rows)} rows")
    
    return rows


def sort_table_adsets(
    rows: List[dict],
    sort_by: Optional[str],
    sort_dir: Optional[str]
) -> List[dict]:
    """
    Sort adsets for table display
    
    Args:
        sort_by: Field name (spend, results, cost_per_purchase, etc.)
        sort_dir: "asc" or "desc"
    """
    if not sort_by:
        return rows
    
    reverse = (sort_dir == "desc")
    
    def get_sort_key(adset: dict):
        value = adset.get(sort_by)
        return value if value is not None else 0
    
    sorted_rows = sorted(rows, key=get_sort_key, reverse=reverse)
    logger.info(f"   Sorted by {sort_by} ({sort_dir}): {len(sorted_rows)} rows")
    
    return sorted_rows


def paginate(
    rows: List[dict],
    page: int,
    page_size: int
) -> Tuple[List[dict], dict]:
    """
    Paginate rows and return pagination info
    
    Returns:
        (page_rows, pagination_info)
    """
    total_rows = len(rows)
    total_pages = (total_rows + page_size - 1) // page_size if page_size > 0 else 1
    
    start = (page - 1) * page_size
    end = start + page_size
    page_rows = rows[start:end]
    
    pagination = {
        "page": page,
        "page_size": page_size,
        "total_rows": total_rows,
        "total_pages": total_pages
    }
    
    logger.info(f"   Pagination: page {page}/{total_pages}, showing {len(page_rows)}/{total_rows} rows")
    
    return page_rows, pagination


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/data")
async def get_dashboard_data(
    view_mode: str = Query("ecommerce", description="View mode: ecommerce or lead"),
    level: str = Query("adset", description="Level: adset only (campaign/ad not supported yet)"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs (optional)"),
    prefix: Optional[str] = Query(None, description="Filter by prefix (FL, PX, TL, NM...)"),
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, PAUSED, RAN_TODAY, or None"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in names or IDs"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID (drill-down)"),
    adset_id: Optional[str] = Query(None, description="Filter by adset ID (drill-down, NOT for debug)"),
    sort_by: Optional[str] = Query(None, description="Sort field (spend, results, cost_per_purchase, etc.)"),
    sort_dir: Optional[str] = Query("desc", description="Sort direction: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(50, ge=10, le=500, description="Page size"),
    force_refresh: int = Query(0, ge=0, le=1, description="0=use cache, 1=force refresh"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Main dashboard endpoint - Returns summary + table data
    
    Response:
    {
        "summary": {
            "totalSpend": float,
            "totalData": int (Lead only),
            "costPerData": float (Lead only),
            "purchaseValue": float (Ecom only),
            "adsPercent": float (Ecom only),
            "totalCheckouts": int,
            "totalPurchases": int,
            "costPerPurchase": float,
            "activeAdsets": int,
            "pausedAdsets": int,
            "totalAdsets": int,
            "adsetsRanToday": int
        },
        "details": {
            "level": "adset",
            "rows": [adset_data...],
            "pagination": {
                "page": int,
                "page_size": int,
                "total_rows": int,
                "total_pages": int
            }
        }
    }
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # 1. Get user's accounts filtered by view_mode
        account_type_map = get_user_accounts_by_view_mode(
            current_user.id, db, view_mode, enabled_only=True
        )
        
        if not account_type_map:
            # Return empty response
            empty_summary = {
                "totalSpend": 0,
                "totalData": 0 if view_mode == "lead" else None,
                "costPerData": 0 if view_mode == "lead" else None,
                "purchaseValue": 0 if view_mode == "ecommerce" else None,
                "adsPercent": 0 if view_mode == "ecommerce" else None,
                "totalCheckouts": 0,
                "totalPurchases": 0,
                "costPerPurchase": 0,
                "activeAdsets": 0,
                "pausedAdsets": 0,
                "totalAdsets": 0,
                "adsetsRanToday": 0
            }
            return JSONResponse({
                "summary": empty_summary,
                "details": {
                    "level": level,
                    "rows": [],
                    "pagination": {
                        "page": page,
                        "page_size": pageSize,
                        "total_rows": 0,
                        "total_pages": 0
                    }
                }
            })
        
        # 2. Filter accounts if account_ids specified
        user_account_ids = list(account_type_map.keys())
        if account_ids:
            requested_ids = [aid.strip() for aid in account_ids.split(',') if aid.strip()]
            for aid in requested_ids:
                if aid not in user_account_ids:
                    raise HTTPException(status_code=403, detail=f"Access denied to account {aid}")
            user_account_ids = requested_ids
        
        # 3. Get access token
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="Facebook access token not found. Please configure in Settings."
            )
        
        # 4. Get insights from Facebook API (with cache)
        use_cache = (force_refresh == 0)
        logger.info(
            f"📥 Fetching data for {len(user_account_ids)} accounts | "
            f"view_mode={view_mode}, date_from={date_from}, date_to={date_to}, use_cache={use_cache}"
        )
        
        raw_data = await get_insights_cached(
            access_token,
            user_account_ids,
            date_from,
            date_to,
            use_cache
        )
        
        # 5. Filter by account_type_map (view_mode)
        filtered_data = [
            row for row in raw_data
            if str(row.get('account_id')).replace('act_', '') in account_type_map
        ]
        logger.info(f"   Filtered by view_mode: {len(filtered_data)}/{len(raw_data)} rows")
        
        # 6. Get adset statuses from Facebook
        adset_ids = list(set([row.get('adset_id') for row in filtered_data if row.get('adset_id')]))
        adset_statuses = {}
        
        if adset_ids:
            logger.info(f"📊 Fetching statuses for {len(adset_ids)} adsets...")
            adset_statuses = fetch_adset_statuses(adset_ids, access_token, use_cache=use_cache)
        
        # 7. Build adset_map (group by adset_id)
        adset_map = build_adset_map(filtered_data, adset_statuses, view_mode)
        
        # 8. Build summary (GLOBAL - no UI filters applied)
        if view_mode == "lead":
            summary = build_lead_summary(adset_map)
        else:  # ecommerce
            summary = build_ecommerce_summary(adset_map)
        
        # 9. Filter adsets for table (apply UI filters)
        adset_list = list(adset_map.values())
        filtered_adsets = filter_table_adsets(
            adset_list,
            prefix=prefix,
            status=status,
            search=search,
            campaign_id=campaign_id,
            adset_id=adset_id
        )
        
        # 10. Sort adsets
        sorted_adsets = sort_table_adsets(filtered_adsets, sort_by, sort_dir)
        
        # 11. Paginate
        page_rows, pagination = paginate(sorted_adsets, page, pageSize)
        
        # 12. Return response
        return JSONResponse({
            "summary": summary,
            "details": {
                "level": level,
                "rows": page_rows,
                "pagination": pagination
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_dashboard_data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters")
async def get_filter_options(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get available filter options (prefixes, accounts, etc.)
    
    Response:
    {
        "prefixes": ["FL", "PX", "TL", "NM", ...],
        "accounts": [
            {"id": "123", "name": "Account Name", "type": "E-COMMERCE"},
            ...
        ]
    }
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get user's accounts
        accounts = db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.enabled == True
        ).all()
        
        # Extract unique prefixes from Settings
        # TODO: Get from Prefix model or account mappings
        prefixes = ["FL", "PX", "TL", "NM"]  # Placeholder
        
        account_list = [
            {
                "id": acc.account_id.replace('act_', ''),
                "name": acc.account_name or acc.account_id,
                "type": acc.account_type
            }
            for acc in accounts
        ]
        
        return JSONResponse({
            "prefixes": prefixes,
            "accounts": account_list
        })
        
    except Exception as e:
        logger.error(f"❌ Error in get_filter_options: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings-status")
async def get_settings_status(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Check if user has configured necessary settings
    
    Response:
    {
        "hasAccounts": bool,
        "hasFacebookToken": bool,
        "hasTelegramToken": bool,
        "accountsCount": int
    }
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Check accounts
        accounts_count = db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.enabled == True
        ).count()
        
        # Check tokens
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == current_user.id
        ).first()
        
        has_fb_token = bool(user_settings and user_settings.facebook_token_encrypted)
        has_tg_token = bool(user_settings and user_settings.telegram_bot_token)
        
        return JSONResponse({
            "hasAccounts": accounts_count > 0,
            "hasFacebookToken": has_fb_token,
            "hasTelegramToken": has_tg_token,
            "accountsCount": accounts_count
        })
        
    except Exception as e:
        logger.error(f"❌ Error in get_settings_status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Budget & Status Update Endpoints
# ============================================================================

class BudgetOperation(BaseModel):
    level: str  # CAMPAIGN or ADSET
    id: str  # campaign_id or adset_id
    new_budget: float  # VND / day (exact value, no rounding)
    reason: Optional[str] = None


class BudgetUpdateRequest(BaseModel):
    operations: List[BudgetOperation]
    view_mode: Optional[str] = "ecommerce"


@router.post("/budget/update")
async def update_budget_endpoint(
    request: BudgetUpdateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Update budget for multiple adsets/campaigns
    
    IMPORTANT: Budget calculation must preserve precision
    Example: original=78910, percent=30% -> new=102583 (NOT 79*1.3)
    
    Request:
    {
        "operations": [
            {"level": "ADSET", "id": "123", "new_budget": 102583.0},
            ...
        ],
        "view_mode": "ecommerce"
    }
    
    Response:
    {
        "success": true,
        "results": [
            {"id": "123", "level": "ADSET", "old_budget": 78910, "new_budget": 102583, "status": "ok"},
            ...
        ],
        "message": "Updated 5 adsets"
    }
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="Facebook access token not found"
            )
        
        results = []
        
        for op in request.operations:
            try:
                if op.level == "ADSET":
                    result = update_adset_budget(
                        op.id,
                        op.new_budget,
                        access_token
                    )
                elif op.level == "CAMPAIGN":
                    result = update_campaign_budget(
                        op.id,
                        op.new_budget,
                        access_token
                    )
                else:
                    result = {"error": f"Invalid level: {op.level}"}
                
                results.append({
                    "id": op.id,
                    "level": op.level,
                    "new_budget": op.new_budget,
                    "status": "ok" if result.get("success") else "error",
                    "error": result.get("error")
                })
                
            except Exception as e:
                logger.error(f"Error updating {op.level} {op.id}: {e}")
                results.append({
                    "id": op.id,
                    "level": op.level,
                    "status": "error",
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["status"] == "ok")
        
        return JSONResponse({
            "success": success_count > 0,
            "results": results,
            "message": f"Updated {success_count}/{len(results)} items"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in update_budget: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class StatusUpdateItem(BaseModel):
    id: str  # adset_id or campaign_id
    new_status: str  # ACTIVE or PAUSED


class StatusUpdateRequest(BaseModel):
    level: str  # CAMPAIGN, ADSET, or AD
    items: List[StatusUpdateItem]


@router.post("/status/update")
async def update_status_endpoint(
    request: StatusUpdateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Update status (pause/resume) for adsets/campaigns
    
    Request:
    {
        "level": "ADSET",
        "items": [
            {"id": "123", "new_status": "PAUSED"},
            {"id": "456", "new_status": "ACTIVE"},
            ...
        ]
    }
    
    Response:
    {
        "success": true,
        "message": "Updated 5 adsets",
        "results": [...]
    }
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="Facebook access token not found"
            )
        
        results = []
        
        for item in request.items:
            try:
                if request.level == "ADSET":
                    if item.new_status == "PAUSED":
                        result = pause_adsets([item.id], access_token)
                    elif item.new_status == "ACTIVE":
                        result = resume_adsets([item.id], access_token)
                    else:
                        result = {"error": f"Invalid status: {item.new_status}"}
                else:
                    result = {"error": f"Level {request.level} not supported yet"}
                
                results.append({
                    "id": item.id,
                    "status": "ok" if result.get("success") else "error",
                    "error": result.get("error")
                })
                
            except Exception as e:
                logger.error(f"Error updating status for {item.id}: {e}")
                results.append({
                    "id": item.id,
                    "status": "error",
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["status"] == "ok")
        
        return JSONResponse({
            "success": success_count > 0,
            "message": f"Updated {success_count}/{len(results)} items",
            "results": results
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in update_status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return JSONResponse({
        "status": "ok",
        "service": "dashboard-api",
        "version": "2.0-refactored"
    })
