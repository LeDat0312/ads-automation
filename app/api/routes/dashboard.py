"""
Dashboard Backend API - Clean version
Chỉ chứa backend logic, không có HTML/CSS/JS
Tương thích 100% với React frontend
"""
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from dataclasses import dataclass
from collections import defaultdict
import pytz
import os

from app.core.database import get_db
from app.models.account_prefix import Account, Prefix
from app.api.routes.auth import get_current_user_optional
from app.models.user import User
from app.models.user_settings import UserSettings
from app.core.ui_helpers import get_account_locked_message
from app.services.facebook_api import (
    fetch_adset_statuses, 
    pause_adsets, 
    resume_adsets, 
    update_adset_budget, 
    update_campaign_budget,
    normalize_status
)
from pydantic import BaseModel
from typing import Literal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Timezone Hồ Chí Minh
HCM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Cache in-memory cho Facebook API data (TTL 60s)
@dataclass
class CachedResult:
    timestamp: datetime
    data: List[Dict[str, Any]]

# Global cache dict: key = (date_from, date_to, tuple(sorted(account_ids))), value = CachedResult
_insights_cache: Dict[Tuple, CachedResult] = {}
CACHE_TTL_SECONDS = 60  # Cache 60 giây


def get_user_access_token(user_id: int, db: Session) -> Optional[str]:
    """Lấy Facebook access token từ UserSettings (decrypt nếu cần)"""
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


async def get_insights_cached_async(
    access_token: str,
    ad_account_ids: List[str],
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 5000,
    use_cache: bool = True,
    account_type_map: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Lấy insights từ Facebook API với cache (TTL 60s) - Async version
    Key cache: (date_from, date_to, tuple(sorted(account_ids)))
    
    Args:
        account_type_map: Dict mapping account_id → account_type (E-COMMERCE/LEAD_GENERATION)
    """
    # Tạo cache key
    cache_key = (
        date_from or '',
        date_to or '',
        tuple(sorted(ad_account_ids))
    )
    
    # Check cache nếu use_cache = True
    if use_cache:
        now = datetime.now()
        cached = _insights_cache.get(cache_key)
        if cached:
            age_seconds = (now - cached.timestamp).total_seconds()
            if age_seconds < CACHE_TTL_SECONDS:
                logger.info(f"✅ Cache hit! Dùng dữ liệu từ cache (age: {age_seconds:.1f}s)")
                return cached.data
            else:
                logger.info(f"⏰ Cache expired (age: {age_seconds:.1f}s), gọi lại Facebook API")
                del _insights_cache[cache_key]
    
    # Gọi Facebook API (async để chạy song song các accounts)
    logger.info(f"📥 Gọi Facebook API (cache miss hoặc expired)...")
    from app.services.facebook_api import pull_facebook_data_async
    
    all_data = await pull_facebook_data_async(
        access_token, 
        ad_account_ids, 
        date_preset=None,
        date_from=date_from,
        date_to=date_to,
        account_type_map=account_type_map
    )
    
    # Giới hạn số lượng để tránh quá tải
    if len(all_data) > max_results:
        logger.warning(f"Giới hạn kết quả từ {len(all_data)} xuống {max_results} để tránh quá tải")
        all_data = all_data[:max_results]
    
    # Lưu vào cache
    if use_cache:
        _insights_cache[cache_key] = CachedResult(
            timestamp=datetime.now(),
            data=all_data
        )
        logger.info(f"💾 Đã lưu {len(all_data)} rows vào cache")
    
    return all_data


async def pull_facebook_data_with_date_range_async(
    access_token: str,
    ad_account_ids: List[str],
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 5000,
    use_cache: bool = True,
    account_type_map: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Gọi Facebook API với custom date range (wrapper với cache) - Async version
    """
    return await get_insights_cached_async(
        access_token,
        ad_account_ids,
        date_from=date_from,
        date_to=date_to,
        max_results=max_results,
        use_cache=use_cache,
        account_type_map=account_type_map
    )


def get_user_account_prefixes(user_id: int, db: Session, enabled_only: bool = True) -> tuple[List[str], List[str]]:
    """Lấy danh sách account_ids và prefixes của user"""
    query = db.query(Account.account_id).filter(Account.user_id == user_id)
    if enabled_only:
        query = query.filter(Account.enabled == True)
    user_accounts = query.all()
    account_ids = [acc[0] for acc in user_accounts]
    
    prefix_query = db.query(Prefix.prefix).filter(Prefix.user_id == user_id)
    if enabled_only:
        prefix_query = prefix_query.filter(Prefix.enabled == True)
    user_prefixes = prefix_query.all()
    prefixes = [pref[0] for pref in user_prefixes]
    
    return account_ids, prefixes


def get_user_account_prefixes_filtered_by_view_mode(
    user_id: int, db: Session, view_mode: str, enabled_only: bool = True
) -> tuple[List[str], List[str]]:
    """
    Lấy danh sách account_ids và prefixes của user - LỌC theo view_mode
    - view_mode='ecommerce': Chỉ lấy accounts có account_type='E-COMMERCE'
    - view_mode='lead': Chỉ lấy accounts có account_type='LEAD_GENERATION'
    """
    query = db.query(Account.account_id).filter(Account.user_id == user_id)
    if enabled_only:
        query = query.filter(Account.enabled == True)
    
    if view_mode == "ecommerce":
        query = query.filter(Account.account_type == "E-COMMERCE")
    elif view_mode == "lead":
        query = query.filter(Account.account_type == "LEAD_GENERATION")
    
    user_accounts = query.all()
    account_ids = [acc[0] for acc in user_accounts]
    
    prefix_query = db.query(Prefix.prefix).filter(Prefix.user_id == user_id)
    if enabled_only:
        prefix_query = prefix_query.filter(Prefix.enabled == True)
    user_prefixes = prefix_query.all()
    prefixes = [pref[0] for pref in user_prefixes]
    
    return account_ids, prefixes


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Dashboard page - Serve React app
    Redirects to login if not authenticated, otherwise serves React app
    """
    logger.info("Dashboard page accessed")
    
    try:
        if not current_user:
            return HTMLResponse(content="""
            <script>
                window.location.href = '/auth/login';
            </script>
            """)
        
        if not current_user.is_active:
            return HTMLResponse(content=get_account_locked_message())
        
        # Serve React app from frontend/dist
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        frontend_dist = os.path.join(project_root, "frontend", "dist", "index.html")
        
        if os.path.exists(frontend_dist):
            return FileResponse(frontend_dist)
        else:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard - React App Not Built</title>
            </head>
            <body>
                <h1>Dashboard</h1>
                <p>React frontend chưa được build. Vui lòng chạy:</p>
                <pre>cd frontend && npm run build</pre>
            </body>
            </html>
            """)
        
    except Exception as e:
        logger.error(f"Error in dashboard page: {e}")
        return HTMLResponse(content=f"<div>Error: {str(e)}</div>", status_code=500)


@router.get("/filters")
async def get_dashboard_filters(
    request: Request,
    view_mode: Optional[str] = Query(None, description="Filter accounts by view mode: ecommerce or lead"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy filters cho dashboard từ settings của user - CHỈ accounts thuộc view_mode được chọn"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Lấy accounts từ settings (chỉ enabled) - FILTER theo view_mode
        query = db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.enabled == True
        )
        
        if view_mode == "ecommerce":
            query = query.filter(Account.account_type == "E-COMMERCE")
        elif view_mode == "lead":
            query = query.filter(Account.account_type == "LEAD_GENERATION")
        
        user_accounts = query.all()
        
        # Lấy prefixes từ settings (chỉ enabled)
        user_prefixes = db.query(Prefix).filter(
            Prefix.user_id == current_user.id,
            Prefix.enabled == True
        ).all()
        
        return JSONResponse({
            "accounts": [
                {
                    "id": acc.account_id,
                    "name": acc.account_name or acc.account_id,
                    "type": acc.account_type,
                    "enabled": acc.enabled
                } for acc in user_accounts
            ],
            "prefixes": [
                {
                    "id": prefix.prefix,
                    "name": prefix.prefix_name or prefix.prefix,
                    "description": prefix.description or f"Prefix {prefix.prefix}"
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
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        
        accounts_count = db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.enabled == True
        ).count()
        
        prefixes_count = db.query(Prefix).filter(
            Prefix.user_id == current_user.id,
            Prefix.enabled == True
        ).count()
        
        has_token = bool(user_settings and user_settings.facebook_token_encrypted)
        
        return JSONResponse({
            "has_token": has_token,
            "accounts_count": accounts_count,
            "prefixes_count": prefixes_count,
            "settings_complete": bool(
                has_token and 
                accounts_count > 0 and 
                prefixes_count > 0
            ),
            "last_updated": user_settings.updated_at.isoformat() if user_settings and hasattr(user_settings, 'updated_at') and user_settings.updated_at else None
        })
        
    except Exception as e:
        logger.error(f"Error getting settings status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error loading settings status")


@router.get("/health")
async def dashboard_health():
    """Health check endpoint for dashboard"""
    return JSONResponse({
        "status": "healthy",
        "service": "dashboard",
        "timestamp": datetime.now(HCM_TZ).isoformat()
    })


@router.get("/data")
async def get_dashboard_data(
    request: Request,
    view_mode: str = Query("ecommerce", description="View mode: ecommerce or lead"),
    level: str = Query("adset", description="Level: campaign, adset, or ad"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs (optional)"),
    prefix: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID (for drill-down)"),
    adset_id: Optional[str] = Query(None, description="Filter by adset ID (for drill-down) - CHỈ dùng khi user click vào 1 adset cụ thể"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=10, le=500),
    force_refresh: int = Query(0, ge=0, le=1, description="0=use cache, 1=force refresh from Facebook API"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Unified endpoint: Get both summary cards and detailed table data
    - force_refresh=0: Use cache (fast, default)
    - force_refresh=1: Force refresh from Facebook API (realtime)
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get user's enabled accounts and prefixes - FILTER theo view_mode
        user_account_ids, user_prefixes = get_user_account_prefixes_filtered_by_view_mode(
            current_user.id, db, view_mode, enabled_only=True
        )
        
        # Build account_type_map để truyền vào Facebook API pull
        account_query = db.query(Account.account_id, Account.account_type).filter(
            Account.user_id == current_user.id,
            Account.enabled == True
        )
        if view_mode == "ecommerce":
            account_query = account_query.filter(Account.account_type == "E-COMMERCE")
        elif view_mode == "lead":
            account_query = account_query.filter(Account.account_type == "LEAD_GENERATION")
        
        account_type_map = {}
        for acc_id, acc_type in account_query.all():
            clean_id = acc_id.replace('act_', '')
            account_type_map[clean_id] = acc_type
        
        logger.info(f"📋 Built account_type_map: {account_type_map}")
        
        if not user_account_ids:
            empty_summary = {
                "totalSpend": 0,
                "totalData": 0 if view_mode == "lead" else None,
                "avgGiaData": 0 if view_mode == "lead" else None,
                "totalLead": 0 if view_mode == "lead" else None,
                "adsPercent": 0 if view_mode == "ecommerce" else None,
                "purchaseValue": 0 if view_mode == "ecommerce" else None,
                "activeAdsets": 0,
                "pausedAdsets": 0,
                "totalAdsets": 0
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
        
        # Filter accounts nếu có account_ids filter
        if account_ids:
            requested_ids = [aid.strip() for aid in account_ids.split(',') if aid.strip()]
            for aid in requested_ids:
                if aid not in user_account_ids:
                    raise HTTPException(status_code=403, detail=f"Access denied to account {aid}")
            user_account_ids = requested_ids
        
        # Get access token
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(status_code=400, detail="Facebook access token not found. Please configure in Settings.")
        
        # Gọi Facebook API (với force_refresh control)
        use_cache = (force_refresh == 0)
        logger.info(f"📥 Đang lấy dữ liệu từ Facebook API cho {len(user_account_ids)} tài khoản... (force_refresh={force_refresh}, use_cache={use_cache})")
        logger.info(f"   Filters: view_mode={view_mode}, level={level}, account_ids={account_ids}, prefix={prefix}, status={status}, date_from={date_from}, date_to={date_to}, search={search}, campaign_id={campaign_id}, adset_id={adset_id}")
        
        all_data = await pull_facebook_data_with_date_range_async(
            access_token,
            user_account_ids,
            date_from=date_from,
            date_to=date_to,
            max_results=10000,
            use_cache=use_cache,
            account_type_map=account_type_map
        )
        logger.info(f"   ✅ Đã lấy được {len(all_data)} rows từ Facebook API")
        
        # Filter by prefix nếu có
        if prefix and all_data:
            all_data = [row for row in all_data if row.get('prefix') == prefix]
        
        # Filter by view mode (campaign type)
        before_view_filter = len(all_data)
        if view_mode == "ecommerce":
            all_data = [row for row in all_data if row.get('campaign_type') == 'ECOMMERCE']
        elif view_mode == "lead":
            all_data = [row for row in all_data if row.get('campaign_type') == 'LEAD']
        logger.info(f"   📊 Sau filter view_mode ({view_mode}): {len(all_data)}/{before_view_filter} rows")
        
        # Lấy status của adsets từ Facebook API
        adset_ids = list(set([row.get('adset_id') for row in all_data if row.get('adset_id')]))
        if adset_ids:
            logger.info(f"📊 Đang lấy status cho {len(adset_ids)} adsets...")
            adset_statuses_map = fetch_adset_statuses(adset_ids, access_token, use_cache=use_cache)
            # Update status trong data
            for row in all_data:
                row_adset_id = row.get('adset_id')
                if row_adset_id and row_adset_id in adset_statuses_map:
                    status_info = adset_statuses_map[row_adset_id]
                    row['effective_status'] = status_info.get('effective_status', 'UNKNOWN')
                    row['delivery'] = normalize_status(row['effective_status'])
                else:
                    row['effective_status'] = 'UNKNOWN'
                    row['delivery'] = 'UNKNOWN'
        
        # ===== BUILD SUMMARY (dùng data có impressions>0) =====
        all_data_for_summary = [row for row in all_data if int(row.get('impressions', 0) or 0) > 0]
        logger.info(f"   📊 Summary sẽ tổng kết {len(all_data_for_summary)} rows (impressions>0)")
        
        # Aggregate metrics for summary
        total_spend = sum(float(row.get('spend', 0) or 0) for row in all_data_for_summary)
        total_purchases = sum(int(row.get('purchases', 0) or 0) for row in all_data_for_summary)
        total_purchase_value = sum(float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0) for row in all_data_for_summary)
        
        # Metrics cho Lead Generation
        total_data = sum(
            int(row.get('post_comments', 0) or 0) + int(row.get('messaging_conversations_started', 0) or 0)
            for row in all_data_for_summary
        )
        total_checkouts = sum(int(row.get('checkout_initiated', 0) or 0) for row in all_data_for_summary)
        
        # Count unique adsets by status
        adset_statuses = {}
        for row in all_data_for_summary:
            row_adset_id = row.get('adset_id')
            if row_adset_id:
                row_status = (row.get('effective_status') or row.get('adset_status') or 'UNKNOWN').upper()
                if row_adset_id not in adset_statuses:
                    adset_statuses[row_adset_id] = row_status
        
        active_adsets = len([s for s in adset_statuses.values() if normalize_status(s) == "ACTIVE"])
        paused_adsets = len([s for s in adset_statuses.values() if normalize_status(s) == "PAUSED"])
        total_adsets = len(adset_statuses)
        
        # Build summary response
        if view_mode == "ecommerce":
            ads_percent = (total_spend / total_purchase_value * 100) if total_purchase_value > 0 else 0
            cost_per_checkout = total_spend / total_checkouts if total_checkouts > 0 else 0
            cost_per_purchase = total_spend / total_purchases if total_purchases > 0 else 0
            summary = {
                "totalSpend": round(total_spend, 2),
                "adsPercent": round(ads_percent, 2),
                "purchaseValue": round(total_purchase_value, 2),
                "totalCheckouts": total_checkouts,
                "costPerCheckout": round(cost_per_checkout, 2),
                "totalPurchases": total_purchases,
                "costPerPurchase": round(cost_per_purchase, 2),
                "activeAdsets": active_adsets,
                "pausedAdsets": paused_adsets,
                "totalAdsets": total_adsets
            }
        else:  # lead
            avg_gia_data = total_spend / total_data if total_data > 0 else 0
            cost_per_checkout = total_spend / total_checkouts if total_checkouts > 0 else 0
            cost_per_purchase = total_spend / total_purchases if total_purchases > 0 else 0
            summary = {
                "totalSpend": round(total_spend, 2),
                "totalData": total_data,
                "avgGiaData": round(avg_gia_data, 2),
                "totalCheckouts": total_checkouts,
                "costPerCheckout": round(cost_per_checkout, 2),
                "totalPurchases": total_purchases,
                "costPerPurchase": round(cost_per_purchase, 2),
                "activeAdsets": active_adsets,
                "pausedAdsets": paused_adsets,
                "totalAdsets": total_adsets
            }
        
        # ===== BUILD DETAILS (filter và group theo level) =====
        # Filter campaign_id nếu có
        if campaign_id and campaign_id != "None" and all_data:
            all_data = [row for row in all_data if row.get('campaign_id') == campaign_id]
            logger.info(f"   📊 Sau filter campaign_id ({campaign_id}): {len(all_data)} rows")
        
        # Filter adset_id nếu có (chỉ khi user thực sự click drill-down)
        original_adset_id = adset_id
        should_filter_adset = False
        filter_adset_id_value = None
        
        if original_adset_id:
            if isinstance(original_adset_id, str):
                adset_id_clean = original_adset_id.strip()
                if adset_id_clean and adset_id_clean.lower() != "none":
                    should_filter_adset = True
                    filter_adset_id_value = adset_id_clean
        
        if should_filter_adset and filter_adset_id_value:
            all_data = [row for row in all_data if row.get('adset_id') == filter_adset_id_value]
            logger.info(f"   📊 Sau filter adset_id ({filter_adset_id_value}): {len(all_data)} rows")
        
        # ===== FILTER IMPRESSIONS + STATUS (optional) =====
        status_filter = None
        if status and isinstance(status, str) and status.strip():
            status_upper = status.upper().strip()
            if status_upper in ['ACTIVE', 'PAUSED', 'ARCHIVED', 'DELETED']:
                # KHÔNG normalize để giữ nguyên ARCHIVED/DELETED
                status_filter = status_upper
                logger.info(f"   🔍 DEBUG - Sẽ filter theo status: {status_filter}")
        
        # Filter chỉ theo impressions>0 (và status nếu có)
        before_filter = len(all_data)
        filtered_data = []
        status_count = {}
        
        for row in all_data:
            # Lấy status gốc (không normalize) để so sánh với filter
            original_status = (row.get('effective_status') or row.get('adset_status') or 'UNKNOWN').upper()
            normalized_status = normalize_status(original_status)
            status_count[normalized_status] = status_count.get(normalized_status, 0) + 1
            
            impressions = int(row.get('impressions', 0) or 0)
            if impressions == 0:
                continue
            
            if status_filter is not None:
                # So sánh với original status để filter chính xác ARCHIVED/DELETED
                if original_status != status_filter:
                    continue
            
            filtered_data.append(row)
        
        logger.info(f"   🔍 DEBUG - Status distribution: {status_count}")
        if status_filter:
            logger.info(f"   📊 Sau filter impressions>0 + status={status_filter}: {len(filtered_data)}/{before_filter} rows")
        else:
            logger.info(f"   📊 Sau filter impressions>0 (TẤT CẢ status): {len(filtered_data)}/{before_filter} rows")
        
        all_data = filtered_data
        
        # Search filter
        if search and all_data:
            search_lower = search.lower()
            all_data = [row for row in all_data if (
                (row.get('campaign_name', '') or '').lower().find(search_lower) >= 0 or
                (row.get('adset_name', '') or '').lower().find(search_lower) >= 0 or
                (row.get('ad_name', '') or '').lower().find(search_lower) >= 0 or
                (row.get('campaign_id', '') or '').lower().find(search_lower) >= 0 or
                (row.get('adset_id', '') or '').lower().find(search_lower) >= 0 or
                (row.get('ad_id', '') or '').lower().find(search_lower) >= 0
            )]
        
        # Group by level và aggregate (dùng defaultdict để optimize)
        grouped_data = defaultdict(lambda: {
            'spend': 0, 'impressions': 0, 'clicks': 0, 'reach': 0,
            'post_comments': 0, 'messaging_conversations_started': 0,
            'purchases': 0, 'gia_tri_chuyen_doi_tu_luot_mua': 0, 'checkout_initiated': 0
        })
        
        for row in all_data:
            # Determine entity key based on level
            if level == "campaign":
                entity_key = row.get('campaign_id')
                entity_id = row.get('campaign_id')
                entity_name = row.get('campaign_name', '')
            elif level == "adset":
                entity_key = row.get('adset_id')
                entity_id = row.get('adset_id')
                entity_name = row.get('adset_name', '')
            else:  # ad
                entity_key = row.get('ad_id')
                entity_id = row.get('ad_id')
                entity_name = row.get('ad_name', '')
            
            if not entity_key:
                continue
            
            # Initialize group nếu chưa tồn tại (defaultdict tự động init metrics)
            if entity_key not in grouped_data or 'id' not in grouped_data[entity_key]:
                # Chỉ set metadata lần đầu
                grouped_data[entity_key].update({
                    'id': entity_id,
                    'name': entity_name,
                    'account_id': row.get('account_id', ''),
                    'account_name': row.get('account_name', ''),
                    'prefix': row.get('prefix', ''),
                    'status': normalize_status((row.get('effective_status') or row.get('adset_status') or 'UNKNOWN').upper()),
                    'delivery': normalize_status((row.get('effective_status') or row.get('adset_status') or 'UNKNOWN').upper()),
                    'budget': row.get('budget', 0.0) or 0.0,
                    'budget_level': row.get('budget_level', 'ADSET'),
                    'currency': 'VND',
                    'campaign_id': row.get('campaign_id', ''),
                    'campaign_name': row.get('campaign_name', ''),
                    'adset_id': row.get('adset_id', ''),
                    'adset_name': row.get('adset_name', ''),
                })
            
            # Aggregate metrics
            group = grouped_data[entity_key]
            group['spend'] += float(row.get('spend', 0) or 0)
            group['impressions'] += int(row.get('impressions', 0) or 0)
            group['clicks'] += int(row.get('clicks', 0) or 0)
            group['reach'] += int(row.get('reach', 0) or 0)
            group['post_comments'] += int(row.get('post_comments', 0) or 0)
            group['messaging_conversations_started'] += int(row.get('messaging_conversations_started', 0) or 0)
            group['purchases'] += int(row.get('purchases', 0) or 0)
            group['gia_tri_chuyen_doi_tu_luot_mua'] += float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0)
            group['checkout_initiated'] += int(row.get('checkout_initiated', 0) or 0)
            
            # Update status
            effective_status = row.get('effective_status') or row.get('adset_status')
            if effective_status:
                group['status'] = normalize_status(effective_status.upper())
                group['delivery'] = group['status']
        
        # Convert to list and calculate derived metrics
        rows = []
        for group in grouped_data.values():
            spend = group['spend']
            impressions = group['impressions']
            clicks = group['clicks']
            reach = group['reach']
            post_comments = group['post_comments']
            messages = group['messaging_conversations_started']
            purchases = group['purchases']
            purchase_value = group['gia_tri_chuyen_doi_tu_luot_mua']
            checkout_starts = group['checkout_initiated']
            budget = group['budget']
            budget_level = group['budget_level']
            
            # Calculate results (comments + messages)
            results = post_comments + messages
            
            # Calculate derived metrics
            gia_data = (spend / results) if results > 0 else 0
            cpm = (spend / impressions * 1000) if impressions > 0 else 0
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            cpc = (spend / clicks) if clicks > 0 else 0
            frequency = (impressions / reach) if reach > 0 else 0
            
            row_data = {
                "level": level,  # ← Thêm level để frontend biết đây là campaign/adset/ad
                "account_id": group['account_id'],
                "account_name": group.get('account_name', ''),
                "campaign_id": group['campaign_id'],
                "campaign_name": group['campaign_name'] or "-",
                "adset_id": group['adset_id'],
                "adset_name": group['adset_name'] or "-",
                "id": group['id'],
                "name": group['name'] or "-",
                "delivery": group['delivery'],
                "budget": round(budget, 2),
                "budget_level": budget_level,
                "currency": group['currency'],
                "spend": round(spend, 2),
                "results": results,
                "total_leads": results,
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpm": round(cpm, 2),
                "reach": reach,
                "frequency": round(frequency, 2),
                "view_mode": view_mode
            }
            
            if view_mode == "ecommerce":
                ads_percent = (spend / purchase_value * 100) if purchase_value > 0 else 0
                tlc = (purchases / results * 100) if results > 0 else 0
                row_data.update({
                    "%ads": round(ads_percent, 2),
                    "data_cost": round(gia_data, 2),
                    "tlc": round(tlc, 2),
                    "initiated_checkout": checkout_starts,
                    "purchases": purchases,
                    "purchase_value": round(purchase_value, 2)
                })
            else:  # lead
                cost_per_checkout_start = (spend / checkout_starts) if checkout_starts > 0 else 0
                row_data.update({
                    "data_cost": round(gia_data, 2),
                    "cost_per_checkout_initiated": round(cost_per_checkout_start, 2),
                    "initiated_checkout": checkout_starts,
                    "purchases": purchases
                })
            
            rows.append(row_data)
        
        # Pagination
        total_rows = len(rows)
        total_pages = ((total_rows - 1) // pageSize) + 1 if total_rows > 0 else 0
        offset = (page - 1) * pageSize
        paginated_rows = rows[offset:offset + pageSize]
        
        logger.info(f"   ✅ Trả về {len(paginated_rows)} rows (page {page}/{total_pages}, total: {total_rows})")
        
        return JSONResponse({
            "summary": summary,
            "details": {
                "level": level,
                "rows": paginated_rows,
                "pagination": {
                    "page": page,
                    "page_size": pageSize,
                    "total_rows": total_rows,
                    "total_pages": total_pages
                }
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


# Pydantic models
class StatusUpdateItem(BaseModel):
    id: str
    new_status: Literal["ACTIVE", "PAUSED", "DELETED"]

class StatusUpdateRequest(BaseModel):
    level: Literal["CAMPAIGN", "ADSET", "AD"]
    items: List[StatusUpdateItem]

class BudgetOperation(BaseModel):
    level: Literal["CAMPAIGN", "ADSET"]
    id: str
    new_budget: float
    reason: Optional[str] = None

class BudgetUpdateRequest(BaseModel):
    operations: List[BudgetOperation]
    view_mode: Optional[str] = None


@router.post("/status/update")
async def update_status_endpoint(
    request: Request,
    payload: StatusUpdateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Update status for campaigns, adsets, or ads
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(status_code=400, detail="Facebook access token not found. Please configure in Settings.")
        
        results = []
        errors = []
        
        for item in payload.items:
            try:
                if payload.level == "ADSET" or payload.level == "AD":
                    if item.new_status == "PAUSED":
                        result = pause_adsets([item.id], access_token, delay_ms=0)
                    elif item.new_status == "ACTIVE":
                        result = resume_adsets([item.id], access_token, delay_ms=0)
                    else:
                        errors.append({
                            "id": item.id,
                            "error": f"Unsupported status for ADSET/AD: {item.new_status}"
                        })
                        continue
                    
                    if result.get("success", 0) > 0:
                        results.append({
                            "id": item.id,
                            "new_status": item.new_status
                        })
                        # Clear status cache
                        from app.services.facebook_api import _status_cache, _cache_timestamps
                        if access_token in _status_cache:
                            _status_cache[access_token].pop(item.id, None)
                        cache_key = f"status_{access_token[:20]}"
                        _cache_timestamps.pop(cache_key, None)
                    else:
                        error_details = result.get('errorDetails', [])
                        error_msg = error_details[0].get('error', 'Unknown error') if error_details else 'Unknown error'
                        errors.append({
                            "id": item.id,
                            "error": error_msg
                        })
                        
                elif payload.level == "CAMPAIGN":
                    # For campaigns, use the same functions
                    if item.new_status == "PAUSED":
                        result = pause_adsets([item.id], access_token, delay_ms=0)
                    elif item.new_status == "ACTIVE":
                        result = resume_adsets([item.id], access_token, delay_ms=0)
                    else:
                        errors.append({
                            "id": item.id,
                            "error": f"Unsupported status for CAMPAIGN: {item.new_status}"
                        })
                        continue
                    
                    if result.get("success", 0) > 0:
                        results.append({
                            "id": item.id,
                            "new_status": item.new_status
                        })
                        # Clear status cache
                        from app.services.facebook_api import _status_cache, _cache_timestamps
                        if access_token in _status_cache:
                            _status_cache[access_token].pop(item.id, None)
                        cache_key = f"status_{access_token[:20]}"
                        _cache_timestamps.pop(cache_key, None)
                    else:
                        error_details = result.get('errorDetails', [])
                        error_msg = error_details[0].get('error', 'Unknown error') if error_details else 'Unknown error'
                        errors.append({
                            "id": item.id,
                            "error": error_msg
                        })
                else:
                    errors.append({
                        "id": item.id,
                        "error": f"Invalid level: {payload.level}"
                    })
                    continue
                    
            except Exception as e:
                logger.error(f"Error updating status for {payload.level} {item.id}: {e}", exc_info=True)
                errors.append({
                    "id": item.id,
                    "error": str(e)
                })
        
        if errors and not results:
            raise HTTPException(status_code=400, detail=f"All operations failed: {errors}")
        
        return JSONResponse({
            "success": True,
            "results": results,
            "errors": errors if errors else None,
            "message": f"Updated {len(results)} status(es) successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in status update endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")


@router.post("/budget/update")
async def update_budget_endpoint(
    request: Request,
    payload: BudgetUpdateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Update budget for campaigns or adsets
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(status_code=400, detail="Facebook access token not found. Please configure in Settings.")
        
        results = []
        errors = []
        
        for op in payload.operations:
            try:
                if op.level == "ADSET":
                    result = update_adset_budget(
                        adset_id=op.id,
                        access_token=access_token,
                        new_budget=op.new_budget
                    )
                elif op.level == "CAMPAIGN":
                    result = update_campaign_budget(
                        campaign_id=op.id,
                        access_token=access_token,
                        new_budget=op.new_budget
                    )
                else:
                    errors.append({
                        "id": op.id,
                        "level": op.level,
                        "error": f"Invalid level: {op.level}"
                    })
                    continue
                
                if result.get("success"):
                    results.append({
                        "id": op.id,
                        "level": op.level,
                        "old_budget": result.get("old_budget"),
                        "new_budget": result.get("new_budget"),
                        "budget_type": result.get("budget_type")
                    })
                    # Clear budget cache
                    from app.services.facebook_api import _budgets_cache, _cache_timestamps
                    if access_token in _budgets_cache:
                        _budgets_cache[access_token].pop(op.id, None)
                    cache_key = f"budgets_{access_token[:20]}"
                    _cache_timestamps.pop(cache_key, None)
                else:
                    errors.append({
                        "id": op.id,
                        "level": op.level,
                        "error": result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                logger.error(f"Error updating budget for {op.level} {op.id}: {e}", exc_info=True)
                errors.append({
                    "id": op.id,
                    "level": op.level,
                    "error": str(e)
                })
        
        if errors and not results:
            raise HTTPException(status_code=400, detail=f"All operations failed: {errors}")
        
        return JSONResponse({
            "success": True,
            "results": results,
            "errors": errors if errors else None,
            "message": f"Updated {len(results)} budget(s) successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in budget update endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating budget: {str(e)}")


# Legacy endpoint đã bị xóa - Frontend sử dụng /dashboard/status/update (bulk update)
