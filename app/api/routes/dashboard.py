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
    normalize_status,
    fetch_campaign_budgets_batch
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
    sort_by: Optional[str] = Query(None, description="Column to sort by (e.g., 'data_cost', 'spend', 'results')"),
    sort_order: Optional[str] = Query("desc", description="Sort order: 'asc' or 'desc'"),
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
        
        # Filter by view mode (campaign type) - TRƯỚC KHI filter prefix
        before_view_filter = len(all_data)
        if view_mode == "ecommerce":
            all_data = [row for row in all_data if row.get('campaign_type') == 'ECOMMERCE']
        elif view_mode == "lead":
            all_data = [row for row in all_data if row.get('campaign_type') == 'LEAD']
        logger.info(f"   📊 Sau filter view_mode ({view_mode}): {len(all_data)}/{before_view_filter} rows")
        
        # Lưu all_data_trước_khi_filter_prefix để tính summary (KHÔNG bị ảnh hưởng bởi prefix)
        all_data_for_summary = all_data.copy()
        
        # Filter by prefix nếu có (chỉ áp dụng cho bảng, KHÔNG áp dụng cho summary)
        if prefix and all_data:
            all_data = [row for row in all_data if row.get('prefix') == prefix]
            logger.info(f"   📊 Sau filter prefix ({prefix}): {len(all_data)} rows (summary vẫn dùng {len(all_data_for_summary)} rows)")
        
        # Lấy status của adsets từ Facebook API
        adset_ids = list(set([row.get('adset_id') for row in all_data if row.get('adset_id')]))
        adset_statuses_map = {}
        if adset_ids:
            logger.info(f"📊 Đang lấy status cho {len(adset_ids)} adsets...")
            adset_statuses_map = fetch_adset_statuses(adset_ids, access_token, use_cache=use_cache)
            logger.info(f"   ✅ Đã lấy status cho {len(adset_statuses_map)} adsets từ Facebook API")
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
        else:
            logger.warning(f"⚠️ Không có adset_id nào trong data để lấy status")
        
        # Fetch TẤT CẢ adsets structure từ accounts (với đầy đủ fields) để build adset_map đúng
        from app.services.facebook_api import fetch_struct_adsets_from_accounts, fetch_campaign_budgets_batch
        logger.info(f"📊 Đang fetch struct adsets từ {len(user_account_ids)} accounts...")
        struct_adsets = fetch_struct_adsets_from_accounts(
            user_account_ids,
            access_token,
            view_mode=view_mode,
            account_type_map=account_type_map,
            use_cache=use_cache
        )
        logger.info(f"   ✅ Đã fetch {len(struct_adsets)} struct adsets từ accounts")
        
        # Fetch campaign budgets để biết campaign nào dùng CBO
        campaign_ids_from_struct = list(set([s.get('campaign_id') for s in struct_adsets if s.get('campaign_id')]))
        campaign_budgets_map = {}
        if campaign_ids_from_struct:
            logger.info(f"📊 Đang fetch budgets cho {len(campaign_ids_from_struct)} campaigns...")
            campaign_budgets_map = fetch_campaign_budgets_batch(campaign_ids_from_struct, access_token)
            logger.info(f"   ✅ Đã fetch budgets cho {len(campaign_budgets_map)} campaigns")
        
        # ===== TÍNH SUMMARY TỪ TOÀN BỘ ADSETS (TRƯỚC KHI FILTER) =====
        # Summary phải tính từ TOÀN BỘ adsets của view_mode, KHÔNG bị ảnh hưởng bởi search/status/prefix/pagination
        # Chỉ bị ảnh hưởng bởi date_from/date_to (filter thời gian hợp lệ)
        logger.info(f"📊 TÍNH SUMMARY từ {len(struct_adsets)} struct adsets (TRƯỚC KHI FILTER)...")
        
        # Build adset_map_summary từ struct_adsets (toàn bộ, không filter)
        adset_map_summary = {}
        for struct_adset in struct_adsets:
            adset_id = struct_adset.get('id')
            if not adset_id:
                continue
            
            campaign_id = struct_adset.get('campaign_id')
            campaign_info = campaign_budgets_map.get(campaign_id, {}) if campaign_id else {}
            campaign_daily_budget_raw = campaign_info.get('daily_budget') or campaign_info.get('lifetime_budget')
            campaign_daily_budget = float(campaign_daily_budget_raw) if campaign_daily_budget_raw else None
            
            adset_daily_budget_raw = struct_adset.get('adset_budget') or struct_adset.get('daily_budget')
            adset_daily_budget = float(adset_daily_budget_raw) if adset_daily_budget_raw else None
            
            # Khởi tạo adset trong map (chỉ structure, chưa có insights)
            adset_map_summary[adset_id] = {
                'adset_id': adset_id,
                'adset_name': struct_adset.get('name', ''),
                'campaign_id': campaign_id,
                'campaign_name': struct_adset.get('campaign_name', ''),
                'effective_status': struct_adset.get('effective_status', 'UNKNOWN'),
                'spend': 0.0,
                'impressions': 0,
                'clicks': 0,
                'reach': 0,
                'post_comments': 0,
                'messaging_conversations_started': 0,
                'checkouts_initiated': 0,
                'onsite_conversion_post_save': 0,
                'purchases': 0,
                'purchase_value': 0.0,
            }
        
        # Merge insights vào adset_map_summary (từ all_data_for_summary - đã filter theo date nhưng CHƯA filter prefix/search/status)
        # Lưu ý: all_data_for_summary đã được filter theo date_from/date_to, view_mode, nhưng CHƯA filter prefix/search/status
        insights_count = 0
        for row in all_data_for_summary:
            row_adset_id = row.get('adset_id')
            if not row_adset_id or row_adset_id not in adset_map_summary:
                continue
            
            adset = adset_map_summary[row_adset_id]
            insights_count += 1
            
            # Merge metrics từ insights
            adset['spend'] += float(row.get('spend', 0) or 0)
            adset['impressions'] += int(row.get('impressions', 0) or 0)
            adset['clicks'] += int(row.get('clicks', 0) or 0)
            adset['reach'] += int(row.get('reach', 0) or 0)
            adset['post_comments'] += int(row.get('post_comments', 0) or 0)
            adset['messaging_conversations_started'] += int(row.get('messaging_conversations_started', 0) or 0)
            adset['checkouts_initiated'] += int(row.get('checkouts_initiated', 0) or 0)
            adset['onsite_conversion_post_save'] += int(row.get('onsite_conversion_post_save', 0) or 0)
            adset['purchases'] += int(row.get('purchases', 0) or 0)
            adset['purchase_value'] += float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0)
            
            # Update status từ insights (nếu có)
            if row.get('effective_status'):
                adset['effective_status'] = row.get('effective_status')
        
        logger.info(f"   ✅ Đã merge insights vào {insights_count} adsets trong summary map")
        
        # 🔹 FIX SUMMARY: Chỉ tính từ adsets có spend > 0 VÀ impressions > 0
        eligible_adsets = [
            adset for adset in adset_map_summary.values()
            if (adset.get('spend', 0) or 0) > 0 and (adset.get('impressions', 0) or 0) > 0
        ]
        logger.info(f"   📊 SUMMARY_DEBUG view={view_mode} | total_adsets_in_map={len(adset_map_summary)} | eligible_adsets={len(eligible_adsets)}")
        
        # Tính summary từ eligible_adsets (chỉ adsets có spend > 0 và impressions > 0)
        total_spend_summary = sum(adset.get('spend', 0) or 0 for adset in eligible_adsets)
        total_data_summary = sum(
            (adset.get('post_comments', 0) or 0) + (adset.get('messaging_conversations_started', 0) or 0)
            for adset in eligible_adsets
        )
        # Tính total_checkouts_summary đúng theo view_mode
        if view_mode == "lead":
            total_checkouts_summary = sum(
                (adset.get('onsite_conversion_post_save', 0) or 0) or 
                (adset.get('checkouts_initiated', 0) or 0)
                for adset in eligible_adsets
            )
        else:
            total_checkouts_summary = sum(adset.get('checkouts_initiated', 0) or 0 for adset in eligible_adsets)
        total_purchases_summary = sum(adset.get('purchases', 0) or 0 for adset in eligible_adsets)
        total_purchase_value_summary = sum(adset.get('purchase_value', 0) or 0 for adset in eligible_adsets)
        
        # Đếm adsets theo status (chỉ từ eligible_adsets)
        active_adsets_summary = 0
        paused_adsets_summary = 0
        total_adsets_summary = len(eligible_adsets)
        
        for adset in eligible_adsets:
            effective_status = normalize_status(adset.get('effective_status', 'UNKNOWN').upper())
            if effective_status == 'ACTIVE':
                active_adsets_summary += 1
            elif effective_status in ['PAUSED', 'ARCHIVED']:
                paused_adsets_summary += 1
        
        logger.info(f"   📊 SUMMARY_DEBUG view={view_mode} | eligible_adsets={total_adsets_summary} active={active_adsets_summary} paused={paused_adsets_summary}")
        
        # Build summary object
        if view_mode == "ecommerce":
            ads_percent_summary = (total_spend_summary / total_purchase_value_summary) if total_purchase_value_summary > 0 else 0
            summary = {
                "totalSpend": round(total_spend_summary, 2),
                "adsPercent": round(ads_percent_summary, 2),
                "purchaseValue": round(total_purchase_value_summary, 2),
                "activeAdsets": active_adsets_summary,
                "pausedAdsets": paused_adsets_summary,
                "totalAdsets": total_adsets_summary,
                "totalCheckouts": total_checkouts_summary,
                "totalPurchases": total_purchases_summary
            }
        else:  # lead
            avg_gia_data_summary = (total_spend_summary / total_data_summary) if total_data_summary > 0 else 0
            summary = {
                "totalSpend": round(total_spend_summary, 2),
                "totalData": total_data_summary,
                "avgGiaData": round(avg_gia_data_summary, 2),
                "totalLead": total_checkouts_summary,  # Lead Gen: checkouts_initiated = total lead
                "activeAdsets": active_adsets_summary,
                "pausedAdsets": paused_adsets_summary,
                "totalAdsets": total_adsets_summary,
                "totalCheckouts": total_checkouts_summary
            }
        
        logger.info(f"   ✅ SUMMARY: total_spend={total_spend_summary:.2f}, active={active_adsets_summary}, paused={paused_adsets_summary}, total={total_adsets_summary}, checkouts={total_checkouts_summary}")
        
        # Fetch TẤT CẢ adsets từ accounts (không chỉ từ insights) để đếm đúng (giữ lại để backward compatibility)
        from app.services.facebook_api import fetch_all_adsets_from_accounts
        logger.info(f"📊 Đang fetch tất cả adsets từ {len(user_account_ids)} accounts để đếm đúng...")
        all_adsets_from_accounts = fetch_all_adsets_from_accounts(
            user_account_ids,
            access_token,
            view_mode=view_mode,
            account_type_map=account_type_map,
            use_cache=use_cache
        )
        logger.info(f"   ✅ Đã fetch {len(all_adsets_from_accounts)} adsets từ accounts")
        
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
        
        # ===== FILTER STATUS (optional) =====
        # KHÔNG filter impressions>0 ở đây - để hiển thị tất cả adsets kể cả chưa có impressions
        # Chỉ filter theo status nếu user chọn
        status_filter = None
        if status and isinstance(status, str) and status.strip():
            status_upper = status.upper().strip()
            if status_upper in ['ACTIVE', 'PAUSED', 'ARCHIVED', 'DELETED']:
                # KHÔNG normalize để giữ nguyên ARCHIVED/DELETED
                status_filter = status_upper
                logger.info(f"   🔍 DEBUG - Sẽ filter theo status: {status_filter}")
        
        # Filter chỉ theo status nếu có (KHÔNG filter impressions>0)
        before_filter = len(all_data)
        filtered_data = []
        status_count = {}
        
        for row in all_data:
            # Lấy status gốc (không normalize) để so sánh với filter
            original_status = (row.get('effective_status') or row.get('adset_status') or 'UNKNOWN').upper()
            normalized_status = normalize_status(original_status)
            status_count[normalized_status] = status_count.get(normalized_status, 0) + 1
            
            # Chỉ filter theo status nếu có, KHÔNG filter impressions>0
            if status_filter is not None:
                # So sánh với original status để filter chính xác ARCHIVED/DELETED
                if original_status != status_filter:
                    continue
            
            filtered_data.append(row)
        
        logger.info(f"   🔍 DEBUG - Status distribution: {status_count}")
        if status_filter:
            logger.info(f"   📊 Sau filter status={status_filter}: {len(filtered_data)}/{before_filter} rows")
        else:
            logger.info(f"   📊 Không filter status (TẤT CẢ status, kể cả chưa có impressions): {len(filtered_data)}/{before_filter} rows")
        
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
        
        # ===== BUILD ADSET_MAP từ struct_adsets (khi level = adset) =====
        # Đây là cách đúng để đảm bảo không bỏ sót adsets không có insights
        adset_map = {}
        if level == "adset" and struct_adsets:
            logger.info(f"📊 BUILD ADSET_MAP từ {len(struct_adsets)} struct adsets...")
            for struct_adset in struct_adsets:
                adset_id = struct_adset.get('id')
                if not adset_id:
                    continue
                
                campaign_id = struct_adset.get('campaign_id')
                campaign_name = struct_adset.get('campaign_name', '')
                
                # 🔹 FIX CBO BUDGET INHERITANCE: Nếu adset không có budget → kế thừa campaign budget
                # Lấy budget info từ struct_adset và campaign_budgets_map
                adset_daily_budget_raw = struct_adset.get('adset_budget') or struct_adset.get('daily_budget')
                adset_daily_budget = float(adset_daily_budget_raw) if adset_daily_budget_raw else None
                
                campaign_info = campaign_budgets_map.get(campaign_id, {}) if campaign_id else {}
                campaign_daily_budget_raw = campaign_info.get('daily_budget') or campaign_info.get('lifetime_budget')
                campaign_daily_budget = float(campaign_daily_budget_raw) if campaign_daily_budget_raw else None
                
                # Xác định using_campaign_budget và budget
                # 1️⃣ Nếu adset có daily_budget → dùng nó
                if adset_daily_budget and adset_daily_budget > 0:
                    using_campaign_budget = False
                    budget_level = 'ADSET'
                    budget = adset_daily_budget
                    adset_daily_budget_final = adset_daily_budget
                    campaign_daily_budget_final = campaign_daily_budget if campaign_daily_budget and campaign_daily_budget > 0 else None
                # 2️⃣ Nếu không có adset budget → kiểm tra campaign budget
                elif campaign_daily_budget and campaign_daily_budget > 0:
                    using_campaign_budget = True
                    budget_level = 'CAMPAIGN'
                    budget = campaign_daily_budget
                    adset_daily_budget_final = None
                    campaign_daily_budget_final = campaign_daily_budget
                # 3️⃣ Cả 2 đều không có
                else:
                    using_campaign_budget = False
                    budget_level = 'ADSET'
                    budget = None  # KHÔNG set 0, set None để frontend xử lý
                    adset_daily_budget_final = None
                    campaign_daily_budget_final = None
                
                # Khởi tạo adset trong map
                adset_map[adset_id] = {
                    'adset_id': adset_id,
                    'adset_name': struct_adset.get('name', ''),
                    'campaign_id': campaign_id,
                    'campaign_name': campaign_name,
                    'account_id': struct_adset.get('account_id', ''),
                    'effective_status': struct_adset.get('effective_status', 'UNKNOWN'),
                    'configured_status': struct_adset.get('configured_status', 'UNKNOWN'),
                    'adset_daily_budget': adset_daily_budget_final,
                    'campaign_daily_budget': campaign_daily_budget_final,
                    'using_campaign_budget': using_campaign_budget,
                    'budget': budget,
                    'budget_level': budget_level,
                    # Metrics (khởi tạo = 0, sẽ merge từ insights sau)
                    'spend': 0.0,
                    'impressions': 0,
                    'clicks': 0,
                    'reach': 0,
                    'post_comments': 0,  # actions; action_type="comment"
                    'messaging_conversations_started': 0,  # actions; action_type="onsite_conversion.messaging_conversation_started_7d"
                    'checkouts_initiated': 0,  # actions; action_type="omni_initiated_checkout"
                    'onsite_conversion_post_save': 0,  # actions; action_type="onsite_conversion.post_save" (cho Lead Gen)
                    'purchases': 0,  # actions; action_type="omni_purchase"
                    'purchase_value': 0.0,  # action_values; action_type="omni_purchase"
                    'ran_today': False,
                    'is_active_now': struct_adset.get('effective_status', 'UNKNOWN') == 'ACTIVE'
                }
            
            logger.info(f"   ✅ Đã khởi tạo {len(adset_map)} adsets từ struct_adsets")
            
            # Merge insights vào adset_map
            insights_adsets_count = 0
            for row in all_data:
                row_adset_id = row.get('adset_id')
                if not row_adset_id or row_adset_id not in adset_map:
                    continue
                
                adset = adset_map[row_adset_id]
                insights_adsets_count += 1
                
                # Merge metrics từ insights
                adset['spend'] += float(row.get('spend', 0) or 0)
                adset['impressions'] += int(row.get('impressions', 0) or 0)
                adset['clicks'] += int(row.get('clicks', 0) or 0)
                adset['reach'] += int(row.get('reach', 0) or 0)
                
                # Map actions đúng theo spec
                # Comment: actions; action_type="comment"
                adset['post_comments'] += int(row.get('post_comments', 0) or 0)
                # Messages: actions; action_type="onsite_conversion.messaging_conversation_started_7d"
                adset['messaging_conversations_started'] += int(row.get('messaging_conversations_started', 0) or 0)
                # Checkouts: actions; action_type="omni_initiated_checkout"
                # 🔹 FIX: Dùng đúng omni_initiated_checkout từ Facebook API
                adset['checkouts_initiated'] += int(row.get('checkouts_initiated', 0) or 0)
                # Lead Gen: onsite_conversion_post_save (từ actions, không phải pixel)
                adset['onsite_conversion_post_save'] = adset.get('onsite_conversion_post_save', 0) + int(row.get('onsite_conversion_post_save', 0) or 0)
                # Purchases: actions; action_type="omni_purchase"
                adset['purchases'] += int(row.get('purchases', 0) or 0)
                # Purchase value: action_values; action_type="omni_purchase"
                adset['purchase_value'] += float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0)
                
                # Update ran_today
                if adset['impressions'] > 0 or adset['spend'] > 0:
                    adset['ran_today'] = True
                
                # Update status từ insights (nếu có)
                if row.get('effective_status'):
                    adset['effective_status'] = row.get('effective_status')
                    adset['is_active_now'] = normalize_status(adset['effective_status'].upper()) == 'ACTIVE'
            
            logger.info(f"   ✅ Đã merge insights vào {insights_adsets_count} adsets")
            
            # Tính derived metrics sau khi merge
            for adset_id, adset in adset_map.items():
                spend = adset['spend']
                checkouts = adset['checkouts_initiated']
                purchases = adset['purchases']
                purchase_value = adset['purchase_value']
                
                # Tính cost_per_checkout và cost_per_purchase
                adset['cost_per_checkout'] = (spend / checkouts) if checkouts > 0 else None
                adset['cost_per_purchase'] = (spend / purchases) if purchases > 0 else None
                # Tính ads_ratio cho E-Commerce
                adset['ads_ratio'] = (spend / purchase_value) if purchase_value > 0 else None
            
            logger.info(f"   ✅ Đã tính derived metrics cho {len(adset_map)} adsets")
            
            # Summary đã được tính sớm hơn (dòng 522-640), không cần tính lại ở đây
        
        # Group by level và aggregate (dùng defaultdict để optimize)
        # Nếu level = "adset" và đã có adset_map, dùng adset_map thay vì group từ all_data
        if level == "adset" and adset_map:
            logger.info(f"📊 Dùng adset_map ({len(adset_map)} adsets) thay vì group từ all_data")
            # Convert adset_map thành grouped_data format
            grouped_data = {}
            for adset_id, adset in adset_map.items():
                # Apply filters (status, search) nếu có
                should_include = True
                
                # Filter by status
                if status_filter:
                    effective_status = adset.get('effective_status', 'UNKNOWN').upper()
                    if effective_status != status_filter:
                        should_include = False
                
                # Filter by search
                if search and should_include:
                    search_lower = search.lower()
                    adset_name = (adset.get('adset_name', '') or '').lower()
                    campaign_name = (adset.get('campaign_name', '') or '').lower()
                    adset_id_str = (adset_id or '').lower()
                    campaign_id = (adset.get('campaign_id', '') or '').lower()
                    if (search_lower not in adset_name and 
                        search_lower not in campaign_name and 
                        search_lower not in adset_id_str and 
                        search_lower not in campaign_id):
                        should_include = False
                
                if not should_include:
                    continue
                
                # Convert adset_map entry thành grouped_data format
                grouped_data[adset_id] = {
                    'id': adset_id,
                    'name': adset.get('adset_name', ''),
                    'account_id': adset.get('account_id', ''),
                    'account_name': '',  # Sẽ lấy từ insights nếu có
                    'prefix': '',  # Sẽ lấy từ insights nếu có
                    'status': normalize_status(adset.get('effective_status', 'UNKNOWN').upper()),
                    'delivery': normalize_status(adset.get('effective_status', 'UNKNOWN').upper()),
                    'budget': adset.get('budget', 0.0),
                    'budget_level': adset.get('budget_level', 'ADSET'),
                    'adset_daily_budget': adset.get('adset_daily_budget'),
                    'campaign_daily_budget': adset.get('campaign_daily_budget'),
                    'using_campaign_budget': adset.get('using_campaign_budget', False),
                    'currency': 'VND',
                    'campaign_id': adset.get('campaign_id', ''),
                    'campaign_name': adset.get('campaign_name', ''),
                    'adset_id': adset_id,
                    'adset_name': adset.get('adset_name', ''),
                    'effective_status': adset.get('effective_status', 'UNKNOWN'),
                    'spend': adset.get('spend', 0.0),
                    'impressions': adset.get('impressions', 0),
                    'clicks': adset.get('clicks', 0),
                    'reach': adset.get('reach', 0),
                    'post_comments': adset.get('post_comments', 0),
                    'messaging_conversations_started': adset.get('messaging_conversations_started', 0),
                    'purchases': adset.get('purchases', 0),
                    'gia_tri_chuyen_doi_tu_luot_mua': adset.get('purchase_value', 0.0),
                    'checkouts_initiated': adset.get('checkouts_initiated', 0),
                    'checkout_initiated': adset.get('checkouts_initiated', 0),  # Alias
                    'onsite_conversion_post_save': adset.get('onsite_conversion_post_save', 0),  # Lead Gen: từ actions
                    'cost_per_checkout': adset.get('cost_per_checkout'),
                    'cost_per_purchase': adset.get('cost_per_purchase'),
                    'ads_ratio': adset.get('ads_ratio')
                }
            
            logger.info(f"   ✅ Đã convert {len(grouped_data)} adsets từ adset_map sang grouped_data")
        else:
            # Group từ all_data (cho level = campaign hoặc ad)
            grouped_data = defaultdict(lambda: {
                'spend': 0, 'impressions': 0, 'clicks': 0, 'reach': 0,
                'post_comments': 0, 'messaging_conversations_started': 0,
                'purchases': 0, 'gia_tri_chuyen_doi_tu_luot_mua': 0, 
                'checkout_initiated': 0, 'checkouts_initiated': 0, 'onsite_conversion_post_save': 0
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
                    # Xác định budget và budget_level dựa trên level hiện tại
                    # Lấy cả campaign và adset budget từ row (nếu có)
                    campaign_budget = float(row.get('campaign_budget', 0) or 0)
                    adset_budget = float(row.get('adset_budget', 0) or 0)
                    row_budget_level = row.get('budget_level', 'ADSET')
                    
                    if level == "campaign":
                        # Ở level campaign: 
                        # - Nếu campaign có budget → hiển thị campaign budget, budget_level = 'CAMPAIGN'
                        # - Nếu không (campaign_budget = 0) → budget_level = 'ADSET', budget = 0 (vì budget ở cấp adset)
                        if campaign_budget > 0:
                            budget = campaign_budget
                            budget_level = 'CAMPAIGN'
                        else:
                            # Campaign không có budget, budget ở cấp adset
                            budget = 0.0
                            budget_level = 'ADSET'
                    elif level == "adset":
                        # Ở level adset: 
                        # - Nếu adset có budget → hiển thị adset budget, budget_level = 'ADSET'
                        # - Nếu không (adset_budget = 0) nhưng campaign có budget → budget_level = 'CAMPAIGN', budget = campaign_budget (KHÔNG phải 0)
                        if adset_budget > 0:
                            # Adset có budget riêng
                            budget = adset_budget
                            budget_level = 'ADSET'
                        elif campaign_budget > 0:
                            # Campaign có budget, adset không có budget riêng → hiển thị campaign budget
                            budget = campaign_budget
                            budget_level = 'CAMPAIGN'
                        else:
                            # Cả 2 đều = 0
                            budget = 0.0
                            budget_level = 'ADSET'
                    else:  # ad
                        # Ở level ad: budget_level và budget lấy từ adset (vì ad không có budget riêng)
                        budget = adset_budget if adset_budget > 0 else campaign_budget
                        budget_level = row_budget_level
                    
                    # Xác định adset_daily_budget, campaign_daily_budget, using_campaign_budget
                    # Lấy từ row hoặc campaign_budgets_map
                    adset_daily_budget_val = adset_budget if adset_budget > 0 else None
                    campaign_daily_budget_val = campaign_budget if campaign_budget > 0 else None
                    # Nếu không có trong row, thử lấy từ campaign_budgets_map
                    if not campaign_daily_budget_val and row.get('campaign_id'):
                        campaign_info = campaign_budgets_map.get(row.get('campaign_id'), {}) if campaign_budgets_map else {}
                        if campaign_info:
                            campaign_daily_budget_val = float(campaign_info.get('daily_budget', 0) or campaign_info.get('lifetime_budget', 0) or 0)
                            if campaign_daily_budget_val == 0:
                                campaign_daily_budget_val = None
                    
                    using_campaign_budget_val = False
                    if adset_daily_budget_val is None and campaign_daily_budget_val is not None:
                        using_campaign_budget_val = True
                    
                    # Chỉ set metadata lần đầu
                    grouped_data[entity_key].update({
                        'id': entity_id,
                        'name': entity_name,
                        'account_id': row.get('account_id', ''),
                        'account_name': row.get('account_name', ''),
                        'prefix': row.get('prefix', ''),
                        'status': normalize_status((row.get('effective_status') or row.get('adset_status') or 'UNKNOWN').upper()),
                        'delivery': normalize_status((row.get('effective_status') or row.get('adset_status') or 'UNKNOWN').upper()),
                        'budget': budget,
                        'budget_level': budget_level,
                        'adset_daily_budget': adset_daily_budget_val,
                        'campaign_daily_budget': campaign_daily_budget_val,
                        'using_campaign_budget': using_campaign_budget_val,
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
                # Tổng hợp checkout: ưu tiên checkouts_initiated (từ actions), fallback checkout_initiated, onsite_conversion_post_save (cho Lead Gen)
                # QUAN TRỌNG: Với Lead Gen, dùng onsite_conversion_post_save (không dùng pixel checkouts_initiated)
                checkout_val = 0
                if view_mode == "lead":
                    # Lead Gen: ưu tiên onsite_conversion_post_save (từ actions, không phải pixel)
                    checkout_val = int(row.get('onsite_conversion_post_save', 0) or 0) or int(row.get('checkouts_initiated', 0) or 0) or int(row.get('checkout_initiated', 0) or 0)
                else:
                    # Ecommerce: ưu tiên checkouts_initiated (từ actions)
                    checkout_val = int(row.get('checkouts_initiated', 0) or 0) or int(row.get('checkout_initiated', 0) or 0) or int(row.get('onsite_conversion_post_save', 0) or 0)
                
                group['checkout_initiated'] += checkout_val
                group['checkouts_initiated'] += checkout_val
                group['onsite_conversion_post_save'] += int(row.get('onsite_conversion_post_save', 0) or 0)
                
                # Update status
                effective_status = row.get('effective_status') or row.get('adset_status')
                if effective_status:
                    group['status'] = normalize_status(effective_status.upper())
                    group['delivery'] = group['status']
        
        # Convert to list and calculate derived metrics
        # 🔹 CHỈ LẤY ROWS CÓ spend > 0 VÀ impressions > 0 (theo yêu cầu)
        rows = []
        for group in grouped_data.values():
            spend = group['spend']
            impressions = group['impressions']
            
            # Filter: chỉ hiển thị rows có spend > 0 VÀ impressions > 0
            if spend <= 0 or impressions <= 0:
                continue
            clicks = group['clicks']
            reach = group['reach']
            post_comments = group['post_comments']
            messages = group['messaging_conversations_started']
            purchases = group['purchases']
            purchase_value = group['gia_tri_chuyen_doi_tu_luot_mua']
            # Lấy checkout_starts: tùy theo view_mode
            if view_mode == "lead":
                # Lead Gen: ưu tiên onsite_conversion_post_save (từ actions, không phải pixel)
                checkout_starts = (
                    group.get('onsite_conversion_post_save', 0) or
                    group.get('checkouts_initiated', 0) or
                    group.get('checkout_initiated', 0)
                )
            else:
                # Ecommerce: ưu tiên checkouts_initiated (từ actions)
                checkout_starts = (
                    group.get('checkouts_initiated', 0) or
                    group.get('checkout_initiated', 0) or
                    group.get('onsite_conversion_post_save', 0)
                )
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
            
            # Lấy budget info từ group (nếu có từ adset_map)
            adset_daily_budget = group.get('adset_daily_budget')
            campaign_daily_budget = group.get('campaign_daily_budget')
            using_campaign_budget = group.get('using_campaign_budget', False)
            
            # Lấy cost metrics từ group (nếu có từ adset_map)
            cost_per_checkout = group.get('cost_per_checkout')
            cost_per_purchase = group.get('cost_per_purchase')
            ads_ratio = group.get('ads_ratio')
            
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
                "adset_daily_budget": round(adset_daily_budget, 2) if adset_daily_budget is not None else None,
                "campaign_daily_budget": round(campaign_daily_budget, 2) if campaign_daily_budget is not None else None,
                "using_campaign_budget": using_campaign_budget,
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
            
            # Lấy budget info và cost metrics từ group (nếu có từ adset_map)
            adset_daily_budget = group.get('adset_daily_budget')
            campaign_daily_budget = group.get('campaign_daily_budget')
            using_campaign_budget = group.get('using_campaign_budget', False)
            cost_per_checkout_from_map = group.get('cost_per_checkout')
            cost_per_purchase_from_map = group.get('cost_per_purchase')
            ads_ratio_from_map = group.get('ads_ratio')
            
            if view_mode == "ecommerce":
                # Tính % ADS: dùng ads_ratio từ adset_map nếu có, nếu không thì tính từ spend/purchase_value
                if ads_ratio_from_map is not None:
                    ads_percent = ads_ratio_from_map
                else:
                    ads_percent = (spend / purchase_value) if purchase_value > 0 else 0
                tlc = (purchases / results * 100) if results > 0 else 0
                # Dùng cost_per_checkout từ adset_map nếu có, nếu không thì tính từ spend/checkout_starts
                if cost_per_checkout_from_map is not None:
                    cost_per_checkout_start = cost_per_checkout_from_map
                else:
                    cost_per_checkout_start = (spend / checkout_starts) if checkout_starts > 0 else 0
                # Dùng cost_per_purchase từ adset_map nếu có, nếu không thì tính từ spend/purchases
                if cost_per_purchase_from_map is not None:
                    cost_per_purchase = cost_per_purchase_from_map
                else:
                    cost_per_purchase = (spend / purchases) if purchases > 0 else 0
                row_data.update({
                    "ads_percent": round(ads_percent, 2),  # % ADS (chỉ Ecom) - dùng ads_percent thay vì %ads
                    "%ads": round(ads_percent, 2),  # Giữ lại để backward compatibility
                    "ads_ratio": round(ads_percent, 2),  # Alias cho frontend
                    "data_cost": round(gia_data, 2),
                    "tlc": round(tlc, 2),
                    "cost_per_checkout_initiated": round(cost_per_checkout_start, 2),
                    "cost_per_checkout": round(cost_per_checkout_start, 2),  # Alias
                    "initiated_checkout": checkout_starts,
                    "checkouts_initiated": checkout_starts,  # Alias
                    "cost_per_purchase": round(cost_per_purchase, 2),
                    "purchases": purchases,
                    "purchase_value": round(purchase_value, 2)
                })
                # Debug log để kiểm tra % ADS - log cả khi purchase_value = 0 để debug
                if spend > 0:
                    logger.info(f"   🔍 Row {group.get('name', 'N/A')}: spend={spend:.2f}, purchase_value={purchase_value:.2f}, purchases={purchases}, ads_percent={ads_percent:.2f}%")
                    if purchase_value == 0 and purchases > 0:
                        logger.warning(f"   ⚠️ Row {group.get('name', 'N/A')}: purchase_value=0 nhưng purchases={purchases} - có thể do Facebook API không trả về action_values")
            else:  # lead
                # Dùng cost_per_checkout từ adset_map nếu có, nếu không thì tính từ spend/checkout_starts
                if cost_per_checkout_from_map is not None:
                    cost_per_checkout_start = cost_per_checkout_from_map
                else:
                    cost_per_checkout_start = (spend / checkout_starts) if checkout_starts > 0 else None
                # 🔹 FIX: Dùng cost_per_purchase từ adset_map nếu có, nếu không thì tính từ spend/purchases
                # KHÔNG set default là 0 nếu không có dữ liệu; dùng None để frontend hiển thị "0 đ"/"-" cho đẹp
                if cost_per_purchase_from_map is not None:
                    cost_per_purchase = cost_per_purchase_from_map
                else:
                    cost_per_purchase = (spend / purchases) if purchases > 0 else None
                row_data.update({
                    "data_cost": round(gia_data, 2),
                    "cost_per_checkout_initiated": round(cost_per_checkout_start, 2) if cost_per_checkout_start is not None else None,
                    "cost_per_checkout": round(cost_per_checkout_start, 2) if cost_per_checkout_start is not None else None,  # Alias
                    "initiated_checkout": checkout_starts,
                    "checkouts_initiated": checkout_starts,  # Alias
                    "cost_per_purchase": round(cost_per_purchase, 2) if cost_per_purchase is not None else None,
                    "purchases": purchases
                })
            
            rows.append(row_data)
        
        # Sort toàn bộ rows trước khi paginate
        if sort_by:
            reverse_order = (sort_order or 'desc').lower() == 'desc'
            logger.info(f"   📊 Bắt đầu sắp xếp: sort_by={sort_by}, sort_order={sort_order}, reverse_order={reverse_order}")
            try:
                # Map frontend column names to backend field names
                column_map = {
                    'checkouts_initiated': 'initiated_checkout',
                    'cost_per_checkout_initiated': 'cost_per_checkout_initiated',
                    'cost_per_purchase': 'cost_per_purchase',
                    'data_cost': 'data_cost',
                    'spend': 'spend',
                    'results': 'results',
                    'purchases': 'purchases',
                    'purchase_value': 'purchase_value',
                    'ads_percent': 'ads_percent',  # Sửa: dùng ads_percent thay vì %ads
                    'tlc': 'tlc',
                    'impressions': 'impressions',
                    'clicks': 'clicks',
                    'cpm': 'cpm',
                    'ctr': 'ctr',
                    'cpc': 'cpc',
                    'reach': 'reach',
                    'frequency': 'frequency',
                    'budget': 'budget',
                }
                backend_field = column_map.get(sort_by, sort_by)
                logger.info(f"   📊 Mapped {sort_by} -> {backend_field}")
                
                def get_sort_value_safe(row):
                    value = row.get(backend_field)
                    # Handle None hoặc empty string - đặt ở cuối
                    if value is None or value == '':
                        # Dùng một giá trị rất nhỏ (cho desc) hoặc rất lớn (cho asc) để đặt ở cuối
                        return float('-inf') if reverse_order else float('inf')
                    # Convert to number if possible
                    try:
                        num_value = float(value)
                        # Giá trị 0 là hợp lệ, không đặt ở cuối (cho phép sort 0 bình thường)
                        return num_value
                    except (ValueError, TypeError):
                        # Invalid value (không phải số) - đặt ở cuối
                        return float('-inf') if reverse_order else float('inf')
                
                # Sort: valid numbers trước, zeros/invalid ở cuối
                rows.sort(key=get_sort_value_safe, reverse=reverse_order)
                logger.info(f"   📊 Đã sắp xếp {len(rows)} rows theo {sort_by} -> {backend_field} ({sort_order})")
                # Log một vài giá trị đầu tiên để debug
                if rows:
                    sample_values = [row.get(backend_field, 'N/A') for row in rows[:3]]
                    logger.info(f"   📊 Sample values sau sort: {sample_values}")
            except Exception as e:
                logger.error(f"   ⚠️ Lỗi khi sắp xếp theo {sort_by}: {e}", exc_info=True)
        
        # Tính tổng kết và trung bình từ TẤT CẢ rows (trước khi paginate)
        totals = {}
        if rows:
            totals = {
                "spend": sum(r.get('spend', 0) or 0 for r in rows),
                "results": sum(r.get('results', 0) or 0 for r in rows),
                "data_cost": sum(r.get('data_cost', 0) or 0 for r in rows) / len(rows) if rows else 0,
                "impressions": sum(r.get('impressions', 0) or 0 for r in rows),
                "clicks": sum(r.get('clicks', 0) or 0 for r in rows),
                "reach": sum(r.get('reach', 0) or 0 for r in rows),
                "frequency": sum(r.get('frequency', 0) or 0 for r in rows) / len(rows) if rows else 0,
                "ctr": sum(r.get('ctr', 0) or 0 for r in rows) / len(rows) if rows else 0,
                "cpc": sum(r.get('cpc', 0) or 0 for r in rows) / len(rows) if rows else 0,
                "cpm": sum(r.get('cpm', 0) or 0 for r in rows) / len(rows) if rows else 0,
            }
            
            if view_mode == "ecommerce":
                # Tính totals cho E-Commerce
                total_spend_ecom = sum(r.get('spend', 0) or 0 for r in rows)
                total_purchase_value_ecom = sum(r.get('purchase_value', 0) or 0 for r in rows)
                total_purchases_ecom = sum(r.get('purchases', 0) or 0 for r in rows)
                total_checkouts_ecom = sum(r.get('initiated_checkout', 0) or r.get('checkouts_initiated', 0) or 0 for r in rows)
                
                totals.update({
                    # % ADS = tổng spend / tổng purchase_value (KHÔNG nhân 100, giống Google Script)
                    "ads_percent": (total_spend_ecom / total_purchase_value_ecom) if total_purchase_value_ecom > 0 else 0,
                    "%ads": (total_spend_ecom / total_purchase_value_ecom) if total_purchase_value_ecom > 0 else 0,
                    "tlc": sum(r.get('tlc', 0) or 0 for r in rows) / len(rows) if rows else 0,
                    "cost_per_checkout_initiated": (total_spend_ecom / total_checkouts_ecom) if total_checkouts_ecom > 0 else 0,
                    "initiated_checkout": total_checkouts_ecom,
                    "checkouts_initiated": total_checkouts_ecom,
                    "cost_per_purchase": (total_spend_ecom / total_purchases_ecom) if total_purchases_ecom > 0 else 0,
                    "purchases": total_purchases_ecom,
                    "purchase_value": total_purchase_value_ecom,
                })
            else:  # lead
                totals.update({
                    "cost_per_checkout_initiated": sum(r.get('cost_per_checkout_initiated', 0) or 0 for r in rows) / len(rows) if rows else 0,
                    "initiated_checkout": sum(r.get('initiated_checkout', 0) or r.get('checkouts_initiated', 0) or 0 for r in rows),
                    "checkouts_initiated": sum(r.get('checkouts_initiated', 0) or r.get('initiated_checkout', 0) or 0 for r in rows),
                    "cost_per_purchase": sum(r.get('cost_per_purchase', 0) or 0 for r in rows) / len(rows) if rows else 0,
                    "purchases": sum(r.get('purchases', 0) or 0 for r in rows),
                })
            
            # Round tất cả giá trị
            for key in totals:
                if isinstance(totals[key], float):
                    totals[key] = round(totals[key], 2)
        
        # ===== SUMMARY ĐÃ ĐƯỢC TÍNH TỪ ADSET_MAP_RAW (TRƯỚC KHI FILTER) =====
        # Nếu chưa có summary (trường hợp level != "adset" hoặc không có adset_map), khởi tạo mặc định
        if 'summary' not in locals():
            logger.warning("⚠️ Summary chưa được tính từ adset_map_raw, khởi tạo mặc định")
            summary = {
                "totalSpend": 0,
                "totalData": 0 if view_mode == "lead" else None,
                "avgGiaData": 0 if view_mode == "lead" else None,
                "totalLead": 0 if view_mode == "lead" else None,
                "adsPercent": 0 if view_mode == "ecommerce" else None,
                "purchaseValue": 0 if view_mode == "ecommerce" else None,
                "activeAdsets": 0,
                "pausedAdsets": 0,
                "totalAdsets": 0,
                "totalCheckouts": 0,
                "totalPurchases": 0 if view_mode == "ecommerce" else None
            }
        
        # Pagination (sau khi sort)
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
                "totals": totals,  # Thêm totals vào response
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
                # Kiểm tra budget_level trước khi update
                # Nếu level = "ADSET" nhưng budget_level = "CAMPAIGN" → không thể update
                # Cần fetch budget_level từ cache hoặc API
                if op.level == "ADSET":
                    # Kiểm tra xem adset có budget riêng không (hay budget ở cấp campaign)
                    # Tạm thời thử update, nếu lỗi thì sẽ bắt được
                    result = update_adset_budget(
                        adset_id=op.id,
                        access_token=access_token,
                        new_budget=op.new_budget
                    )
                    # Nếu lỗi 400, có thể do budget ở cấp campaign
                    if not result.get("success") and "400" in str(result.get("error", "")):
                        errors.append({
                            "id": op.id,
                            "level": op.level,
                            "error": f"Không thể cập nhật ngân sách: Ngân sách đang ở cấp chiến dịch. Vui lòng cập nhật ở tab 'Chiến Dịch'."
                        })
                        continue
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
                        "new_budget": result.get("new_budget") or op.new_budget,  # Đảm bảo có new_budget
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
