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
    pause_campaign,
    resume_campaign,
    pause_single_adset,
    resume_single_adset,
    pause_single_adset_async,
    resume_single_adset_async,
    update_adset_budget, 
    update_campaign_budget,
    update_adsets_budget_batch,
    normalize_status,
    fetch_campaign_budgets_batch,
    FacebookRateLimitError,
    _normalize_budget
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
# SINGLE SOURCE OF TRUTH - Core Data Function
# ============================================================================

async def get_dashboard_dataset(
    access_token: str,
    user_account_ids: List[str],
    account_type_map: Dict[str, str],
    view_mode: str,
    date_from: str,
    date_to: str,
    level: str,  # ✅ FIX: Thêm level parameter
    use_cache: bool = True,
    # Filters cho bảng (KHÔNG ảnh hưởng summary)
    prefix: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    campaign_id: Optional[str] = None,
    adset_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    🎯 SINGLE SOURCE OF TRUTH: Hàm trung tâm fetch và xử lý dữ liệu dashboard
    
    ✅ FIX LOGIC:
    - CHỈ lọc theo account_type (từ DB) - KHÔNG lọc theo view_mode từ data
    - Tất cả ads từ E-Commerce accounts → E-Commerce view (không cần purchase > 0)
    - Tất cả ads từ Lead Gen accounts → Lead Gen view (không cần messaging > 0)
    - adset_id filter CHỈ áp dụng khi level='ad' (drill-down)
    - Summary tính từ rows_base (KHÔNG bị ảnh hưởng UI filters)
    
    Trả về:
    {
        "rows_base": List[Dict],      # Dataset cho summary (chỉ filter spend>0 && impressions>0)
        "rows_for_table": List[Dict],  # Dataset cho bảng (rows_base + UI filters)
        "summary": Dict,                # Summary metrics tính từ rows_base
        "all_adsets_from_accounts": Dict  # Tất cả adsets từ accounts
    }
    """
    logger.info(f"📊 get_dashboard_dataset() START | view={view_mode}, level={level}, accounts={len(user_account_ids)}, date={date_from} to {date_to}")
    
    # ===== BƯỚC 1: Fetch insights từ Facebook API (1 LẦN DUY NHẤT) =====
    logger.info(f"   📥 Fetching insights from Facebook API...")
    all_data = await pull_facebook_data_with_date_range_async(
        access_token,
        user_account_ids,
        date_from=date_from,
        date_to=date_to,
        max_results=10000,
        use_cache=use_cache,
        account_type_map=account_type_map
    )
    logger.info(f"   ✅ Fetched {len(all_data)} rows from Facebook API")
    
    # ===== BƯỚC 2: Filter spend > 0 && impressions > 0 (ĐIỀU KIỆN BẮT BUỘC) =====
    # 🔹 Theo yêu cầu: facebook_api.py đã filter spend>0 && impressions>0, nhưng đảm bảo lại ở đây
    before_filter = len(all_data)
    all_data = [
        row for row in all_data
        if (float(row.get('spend', 0) or 0) > 0) and (int(row.get('impressions', 0) or 0) > 0)
    ]
    logger.info(f"   📊 After filter spend>0 && impressions>0: {len(all_data)}/{before_filter} rows")
    
    # ===== BƯỚC 3: rows_base = SINGLE SOURCE OF TRUTH =====
    # ✅ LOGIC MỚI: CHỈ lọc theo account_type từ DB, KHÔNG lọc theo metrics
    # - E-Commerce accounts → trả TẤT CẢ adsets (không cần purchase > 0)
    # - Lead Gen accounts → trả TẤT CẢ adsets (không cần messaging > 0)
    # - user_account_ids đã được lọc theo Account.account_type từ get_user_account_prefixes_filtered_by_view_mode()
    # - KHÔNG CẦN filter thêm theo campaign_type, objective, metrics
    
    rows_base = all_data.copy()  # Giữ TOÀN BỘ data sau filter spend>0 && impressions>0
    logger.info(f"   ✅ rows_base created (for summary): {len(rows_base)} rows - NO view_mode filter, trust account_type from DB")
    
    # ===== BƯỚC 4: Fetch adset statuses từ Facebook API =====
    adset_ids_base = list(set([row.get('adset_id') for row in rows_base if row.get('adset_id')]))
    adset_statuses_map = {}
    if adset_ids_base:
        logger.info(f"   📥 Fetching status for {len(adset_ids_base)} adsets...")
        adset_statuses_map = fetch_adset_statuses(adset_ids_base, access_token, use_cache=use_cache)
        logger.info(f"   ✅ Fetched status for {len(adset_statuses_map)} adsets")
        
        # Update status trong rows_base
        for row in rows_base:
            row_adset_id = row.get('adset_id')
            if row_adset_id and row_adset_id in adset_statuses_map:
                status_info = adset_statuses_map[row_adset_id]
                row['effective_status'] = status_info.get('effective_status', 'UNKNOWN')
                row['delivery'] = normalize_status(row['effective_status'])
                # Lưu thêm configured_status để dùng cho nút toggle
                row['configured_status'] = status_info.get('configured_status', 'UNKNOWN')
            else:
                row['effective_status'] = 'UNKNOWN'
                row['delivery'] = 'UNKNOWN'
                row['configured_status'] = 'UNKNOWN'
    
    # ===== BƯỚC 5: Tính SUMMARY từ rows_base (SINGLE SOURCE OF TRUTH) =====
    logger.info(f"   📊 Computing summary from rows_base ({len(rows_base)} rows)...")
    
    # Group rows_base theo adset_id để tính summary (vì insights có thể có nhiều rows cho 1 adset)
    adset_summary_map = defaultdict(lambda: {
        'spend': 0.0, 'impressions': 0, 'clicks': 0, 'reach': 0,
        'post_comments': 0, 'messaging_conversations_started': 0,
        'checkouts_initiated': 0, 'onsite_conversion_post_save': 0,
        'purchases': 0, 'purchase_value': 0.0,
        'effective_status': 'UNKNOWN'
    })
    
    for row in rows_base:
        adset_id = row.get('adset_id')
        if not adset_id:
            continue
        
        adset_summary = adset_summary_map[adset_id]
        adset_summary['spend'] += float(row.get('spend', 0) or 0)
        adset_summary['impressions'] += int(row.get('impressions', 0) or 0)
        adset_summary['clicks'] += int(row.get('clicks', 0) or 0)
        adset_summary['reach'] += int(row.get('reach', 0) or 0)
        adset_summary['post_comments'] += int(row.get('post_comments', 0) or 0)
        adset_summary['messaging_conversations_started'] += int(row.get('messaging_conversations_started', 0) or 0)
        adset_summary['checkouts_initiated'] += int(row.get('checkouts_initiated', 0) or 0)
        adset_summary['onsite_conversion_post_save'] += int(row.get('onsite_conversion_post_save', 0) or 0)
        adset_summary['purchases'] += int(row.get('purchases', 0) or 0)
        adset_summary['purchase_value'] += float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0)
        # Update status
        if row.get('effective_status'):
            adset_summary['effective_status'] = row.get('effective_status')
    
    # Tất cả adsets trong map đều đã được filter spend>0 && impressions>0
    eligible_adsets = list(adset_summary_map.values())
    
    # Tính metrics từ eligible_adsets
    total_spend = sum(adset.get('spend', 0) or 0 for adset in eligible_adsets)
    total_data = sum(
        (adset.get('post_comments', 0) or 0) + (adset.get('messaging_conversations_started', 0) or 0)
        for adset in eligible_adsets
    )
    
    # 🔹 Tính total_checkouts đúng theo view_mode (theo yêu cầu spec)
    if view_mode == "lead":
        # Lead Gen: ưu tiên onsite_conversion_post_save
        total_checkouts = sum(
            (adset.get('onsite_conversion_post_save', 0) or 0) or 
            (adset.get('checkouts_initiated', 0) or 0)
            for adset in eligible_adsets
        )
    else:
        # E-Commerce: ưu tiên checkouts_initiated
        total_checkouts = sum(adset.get('checkouts_initiated', 0) or 0 for adset in eligible_adsets)
    
    total_purchases = sum(adset.get('purchases', 0) or 0 for adset in eligible_adsets)
    total_purchase_value = sum(adset.get('purchase_value', 0) or 0 for adset in eligible_adsets)
    
    # 🔹 Tính totalLead cho Lead Generation theo yêu cầu spec
    # totalLead = Checkouts Initiated (omni_initiated_checkout)
    total_lead = sum(adset.get('checkouts_initiated', 0) or 0 for adset in eligible_adsets)
    
    # Đếm adsets theo status
    active_adsets = 0
    paused_adsets = 0
    total_adsets = len(eligible_adsets)
    
    for adset in eligible_adsets:
        effective_status = normalize_status(adset.get('effective_status', 'UNKNOWN').upper())
        if effective_status == 'ACTIVE':
            active_adsets += 1
        elif effective_status in ['PAUSED', 'ARCHIVED']:
            paused_adsets += 1
    
    # Build summary object
    if view_mode == "ecommerce":
        # 🔹 FIX % ADS: Công thức đúng = (total_spend / total_purchase_value * 100)
        # Không nhân 100 lần nữa ở bất kỳ chỗ nào khác
        ads_percent = (total_spend / total_purchase_value * 100.0) if total_purchase_value > 0 else 0.0
        logger.info(f"   📊 % ADS calculation: spend={total_spend:.2f}, purchaseValue={total_purchase_value:.2f}, adsPercent={ads_percent:.2f}%")
        summary = {
            "totalSpend": round(total_spend, 2),
            "adsPercent": round(ads_percent, 2),  # FIX: Đã nhân 100, frontend chỉ cần hiển thị
            "purchaseValue": round(total_purchase_value, 2),
            "totalCheckouts": total_checkouts,
            "totalPurchases": total_purchases,
            "activeAdsets": active_adsets,
            "pausedAdsets": paused_adsets,
            "totalAdsets": total_adsets,
            "currency": "VND"
        }
    else:  # lead
        avg_gia_data = (total_spend / total_data) if total_data > 0 else 0
        summary = {
            "totalSpend": round(total_spend, 2),
            "totalData": total_data,  # Post comments + Messaging conversations started
            "avgGiaData": round(avg_gia_data, 2),
            "totalLead": total_lead,  # ✅ FIXED: Checkouts Initiated (omni_initiated_checkout)
            "totalCheckouts": total_checkouts,
            "totalPurchases": total_purchases,
            "activeAdsets": active_adsets,
            "pausedAdsets": paused_adsets,
            "totalAdsets": total_adsets,
            "currency": "VND"
        }
    
    logger.info(f"   ✅ SUMMARY computed: spend={total_spend:.2f}, active={active_adsets}, paused={paused_adsets}, total={total_adsets}")
    
    # ===== BƯỚC 6: Build rows_for_table (áp dụng filters prefix/status/search) =====
    rows_for_table = rows_base.copy()
    logger.info(f"   📊 rows_for_table initial (from rows_base): {len(rows_for_table)} rows")
    
    # Filter by prefix (chỉ áp dụng cho bảng)
    if prefix and rows_for_table:
        rows_for_table = [row for row in rows_for_table if row.get('prefix') == prefix]
        logger.info(f"   📊 After filter prefix ({prefix}): {len(rows_for_table)} rows")
    
    # Filter by campaign_id (chỉ khi drill-down vào campaign hoặc đang ở level adset/ad)
    if campaign_id and campaign_id != "None" and campaign_id.lower() != "null" and rows_for_table:
        rows_for_table = [row for row in rows_for_table if row.get('campaign_id') == campaign_id]
        logger.info(f"   📊 After filter campaign_id ({campaign_id}): {len(rows_for_table)} rows")
    
    # ✅ FIX LỖI 4: Filter by adset_id CHỈ KHI drill-down từ campaign → ads
    # KHÔNG filter khi đang ở level=adset (xem tổng quan adsets)
    # KHÔNG log warning nữa để tránh spam log
    if adset_id and isinstance(adset_id, str):
        adset_id_clean = adset_id.strip()
        # Chỉ filter nếu có giá trị hợp lệ VÀ đang drill-down vào ads
        if adset_id_clean and adset_id_clean.lower() not in ("none", "null", "undefined", "") and level == "ad":
            before_adset_filter = len(rows_for_table)
            rows_for_table = [row for row in rows_for_table if row.get('adset_id') == adset_id_clean]
            logger.info(f"   📊 Drill-down filter adset_id ({adset_id_clean}): {len(rows_for_table)}/{before_adset_filter} ads")
    
    # Filter by status (chỉ áp dụng cho bảng)
    if status and isinstance(status, str) and status.strip():
        status_upper = status.upper().strip()
        if status_upper in ['ACTIVE', 'PAUSED', 'ARCHIVED', 'DELETED']:
            before_status_filter = len(rows_for_table)
            if status_upper == 'ACTIVE':
                rows_for_table = [
                    row for row in rows_for_table
                    if (row.get('effective_status') or 'UNKNOWN').upper() == 'ACTIVE'
                ]
            elif status_upper == 'PAUSED':
                rows_for_table = [
                    row for row in rows_for_table
                    if (row.get('effective_status') or 'UNKNOWN').upper() in ('PAUSED', 'INACTIVE')
                ]
            else:
                rows_for_table = [
                    row for row in rows_for_table
                    if (row.get('effective_status') or 'UNKNOWN').upper() == status_upper
                ]
            logger.info(f"   📊 After filter status={status_upper}: {len(rows_for_table)}/{before_status_filter} rows")
    
    # Filter by search
    if search and rows_for_table:
        search_lower = search.lower()
        rows_for_table = [row for row in rows_for_table if (
            (row.get('campaign_name', '') or '').lower().find(search_lower) >= 0 or
            (row.get('adset_name', '') or '').lower().find(search_lower) >= 0 or
            (row.get('ad_name', '') or '').lower().find(search_lower) >= 0 or
            (row.get('campaign_id', '') or '').lower().find(search_lower) >= 0 or
            (row.get('adset_id', '') or '').lower().find(search_lower) >= 0 or
            (row.get('ad_id', '') or '').lower().find(search_lower) >= 0
        )]
        logger.info(f"   📊 After filter search ({search}): {len(rows_for_table)} rows")
    
    # ===== BƯỚC 7: Fetch all adsets from accounts (để đếm đúng nếu cần) =====
    from app.services.facebook_api import fetch_all_adsets_from_accounts
    logger.info(f"   📥 Fetching all adsets from {len(user_account_ids)} accounts...")
    all_adsets_from_accounts = fetch_all_adsets_from_accounts(
        user_account_ids,
        access_token,
        view_mode=view_mode,
        account_type_map=account_type_map,
        use_cache=use_cache
    )
    logger.info(f"   ✅ Fetched {len(all_adsets_from_accounts)} adsets from accounts")
    
    logger.info(f"   ✅ get_dashboard_dataset() DONE | rows_base={len(rows_base)}, rows_for_table={len(rows_for_table)}, summary={summary}")
    
    return {
        "rows_base": rows_base,
        "rows_for_table": rows_for_table,
        "summary": summary,
        "all_adsets_from_accounts": all_adsets_from_accounts,
        "adset_statuses_map": adset_statuses_map
    }


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

"""
🎯 REFACTORED /dashboard/data ENDPOINT - SINGLE SOURCE OF TRUTH

Copy endpoint này vào dashboard.py thay thế cho endpoint cũ (từ dòng 623 đến 1604)

Thay đổi chính:
1. ✅ Sử dụng get_dashboard_dataset() - SINGLE SOURCE OF TRUTH
2. ✅ Summary và bảng luôn lấy từ cùng 1 dataset
3. ✅ Xử lý FacebookRateLimitError - trả HTTP 429
4. ✅ Giảm từ 1000 dòng xuống ~250 dòng
5. ✅ Dễ debug và maintain hơn nhiều
"""

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
    adset_id: Optional[str] = Query(None, description="Filter by adset ID (for drill-down)"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=10, le=500),
    sort_by: Optional[str] = Query(None, description="Column to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order: 'asc' or 'desc'"),
    force_refresh: int = Query(0, ge=0, le=1, description="0=use cache, 1=force refresh"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    🎯 REFACTORED: Unified endpoint sử dụng get_dashboard_dataset()
    
    - Summary và bảng luôn nhất quán (cùng 1 source)
    - Xử lý rate limit đúng cách (HTTP 429)
    - Chỉ load spend > 0 && impressions > 0
    - CBO budget hiển thị đúng
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # FIX LỖI 4: Loại bỏ adset_id khi level != adset để tránh filter không cần thiết
        if level != "ad":
            adset_id = None
        
        logger.info(f"📊 /dashboard/data START | view={view_mode}, level={level}, date_from={date_from}, date_to={date_to}")
        if adset_id:  # Chỉ log khi thực sự có adset_id filter
            logger.info(f"🔎 Filter params received | prefix={prefix}, status={status}, search={search}, campaign_id={campaign_id}, adset_id={adset_id}")
        else:
            logger.info(f"🔎 Filter params received | prefix={prefix}, status={status}, search={search}, campaign_id={campaign_id}")
        
        # ===== BƯỚC 1: Get user accounts & build account_type_map =====
        user_account_ids, user_prefixes = get_user_account_prefixes_filtered_by_view_mode(
            current_user.id, db, view_mode, enabled_only=True
        )
        
        # Build account_type_map
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
        
        # Empty state
        if not user_account_ids:
            logger.warning("⚠️ No accounts found for user")
            empty_summary = {
                "totalSpend": 0,
                "totalData": 0 if view_mode == "lead" else None,
                "totalLead": 0 if view_mode == "lead" else None,
                "adsPercent": 0 if view_mode == "ecommerce" else None,
                "purchaseValue": 0 if view_mode == "ecommerce" else None,
                "totalCheckouts": 0,
                "activeAdsets": 0,
                "pausedAdsets": 0,
                "totalAdsets": 0,
                "currency": "VND"
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
        
        # Filter accounts if account_ids filter is provided
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
        
        # ===== BƯỚC 2: Gọi get_dashboard_dataset() - SINGLE SOURCE OF TRUTH =====
        use_cache = (force_refresh == 0)
        logger.info(f"📥 Calling get_dashboard_dataset() | use_cache={use_cache}")
        
        try:
            dataset = await get_dashboard_dataset(
                access_token=access_token,
                user_account_ids=user_account_ids,
                account_type_map=account_type_map,
                view_mode=view_mode,
                date_from=date_from or datetime.now(HCM_TZ).strftime('%Y-%m-%d'),
                date_to=date_to or datetime.now(HCM_TZ).strftime('%Y-%m-%d'),
                level=level,  # ✅ FIX: Truyền level parameter
                use_cache=use_cache,
                # Filters chỉ áp dụng cho bảng (KHÔNG ảnh hưởng summary)
                prefix=prefix,
                status=status,
                search=search,
                campaign_id=campaign_id,
                adset_id=adset_id
            )
        except FacebookRateLimitError as e:
            logger.error(f"⚠️ Facebook rate limit reached: {e}")
            raise HTTPException(
                status_code=429,
                detail="Facebook API rate limit reached. Vui lòng thử lại sau 5-10 phút."
            )
        
        # Extract data from dataset
        rows_for_table = dataset["rows_for_table"]
        summary = dataset["summary"]
        
        logger.info(f"✅ Dataset received | rows_for_table={len(rows_for_table)}, summary={summary}")
        
        # ===== BƯỚC 3: Group by level (nếu cần) =====
        # Logic group by level tùy vào level được chọn (campaign / adset / ad)
        # Hiện tại get_dashboard_dataset() đã trả về data ở ad level
        # Cần group lại nếu level = "campaign" hoặc "adset"
        
        if level == "adset":
            # Group theo adset_id
            grouped_data = defaultdict(lambda: {
                'spend': 0.0, 'impressions': 0, 'clicks': 0, 'reach': 0,
                'post_comments': 0, 'messaging_conversations_started': 0,
                'checkouts_initiated': 0, 'onsite_conversion_post_save': 0,
                'purchases': 0, 'purchase_value': 0.0
            })
            
            for row in rows_for_table:
                adset_id = row.get('adset_id')
                if not adset_id:
                    continue
                
                group = grouped_data[adset_id]
                
                # Aggregate metrics
                group['spend'] += float(row.get('spend', 0) or 0)
                group['impressions'] += int(row.get('impressions', 0) or 0)
                group['clicks'] += int(row.get('clicks', 0) or 0)
                group['reach'] += int(row.get('reach', 0) or 0)
                group['post_comments'] += int(row.get('post_comments', 0) or 0)
                group['messaging_conversations_started'] += int(row.get('messaging_conversations_started', 0) or 0)
                group['checkouts_initiated'] += int(row.get('checkouts_initiated', 0) or 0)
                group['onsite_conversion_post_save'] += int(row.get('onsite_conversion_post_save', 0) or 0)
                group['purchases'] += int(row.get('purchases', 0) or 0)
                group['purchase_value'] += float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0)
                
                # Keep first occurrence info (name, status, budget...)
                if 'adset_id' not in group:
                    group['adset_id'] = adset_id
                    group['adset_name'] = row.get('adset_name', '')
                    group['campaign_id'] = row.get('campaign_id', '')
                    group['campaign_name'] = row.get('campaign_name', '')
                    group['prefix'] = row.get('prefix', '')
                    group['effective_status'] = row.get('effective_status', 'UNKNOWN')
                    group['configured_status'] = row.get('configured_status', 'UNKNOWN')
                    group['delivery'] = row.get('delivery', 'UNKNOWN')
                    # 🔹 CBO Budget fields
                    group['adset_daily_budget'] = row.get('adset_daily_budget')
                    group['adset_lifetime_budget'] = row.get('adset_lifetime_budget')
                    group['campaign_daily_budget'] = row.get('campaign_daily_budget')
                    group['campaign_lifetime_budget'] = row.get('campaign_lifetime_budget')
                    group['using_campaign_budget'] = row.get('using_campaign_budget', False)
                    group['budget_type'] = row.get('budget_type', 'ADSET')
            
            # Convert to list và tính derived metrics
            rows = []
            for adset_id, group in grouped_data.items():
                spend = group['spend']
                checkouts = group['checkouts_initiated']
                purchases = group['purchases']
                purchase_value = group['purchase_value']
                data = group['post_comments'] + group['messaging_conversations_started']
                impressions = group['impressions']
                reach = group['reach']
                clicks = group['clicks']
                
                # 🔹 FIX E-COMMERCE METRICS: Tính đầy đủ các metrics theo spec
                group['results'] = data
                # FIX: Giá DATA = spend / (post_comments + messaging_conversations_started)
                group['gia_data'] = (spend / data) if data > 0 else 0
                group['data_cost'] = group['gia_data']  # Alias
                # FIX: Cost per checkout - ưu tiên từ API, fallback tính từ spend
                group['cost_per_checkout_initiated'] = group.get('cost_per_checkout_initiated', 0) or ((spend / checkouts) if checkouts > 0 else 0)
                # FIX: Cost per purchase - ưu tiên từ API, fallback tính từ spend
                group['cost_per_purchase'] = group.get('cost_per_purchase', 0) or ((spend / purchases) if purchases > 0 else 0)
                # FIX: % ADS = (spend / purchase_value) * 100
                group['ads_percent'] = (spend / purchase_value * 100) if purchase_value > 0 else 0
                # FIX: TLC (tỷ lệ chốt) = (purchases / messaging_conversations_started) * 100
                msg_started = group['messaging_conversations_started']
                group['tlc'] = (purchases / msg_started * 100) if msg_started > 0 else 0
                # FIX: Frequency = impressions / reach
                group['frequency'] = (impressions / reach) if reach > 0 else 0
                # Các metrics khác
                group['cpm'] = (spend / impressions * 1000) if impressions > 0 else 0
                group['ctr'] = (clicks / impressions * 100) if impressions > 0 else 0
                group['cpc'] = (spend / clicks) if clicks > 0 else 0
                # FIX: Thêm alias purchase_value từ gia_tri_chuyen_doi_tu_luot_mua
                group['purchase_value'] = purchase_value
                
                rows.append(group)
        
        elif level == "campaign":
            # Group theo campaign_id
            grouped_data = defaultdict(lambda: {
                'spend': 0.0, 'impressions': 0, 'clicks': 0, 'reach': 0,
                'post_comments': 0, 'messaging_conversations_started': 0,
                'checkouts_initiated': 0, 'onsite_conversion_post_save': 0,
                'purchases': 0, 'purchase_value': 0.0
            })
            
            for row in rows_for_table:
                campaign_id = row.get('campaign_id')
                if not campaign_id:
                    continue
                
                group = grouped_data[campaign_id]
                
                # Aggregate metrics
                group['spend'] += float(row.get('spend', 0) or 0)
                group['impressions'] += int(row.get('impressions', 0) or 0)
                group['clicks'] += int(row.get('clicks', 0) or 0)
                group['reach'] += int(row.get('reach', 0) or 0)
                group['post_comments'] += int(row.get('post_comments', 0) or 0)
                group['messaging_conversations_started'] += int(row.get('messaging_conversations_started', 0) or 0)
                group['checkouts_initiated'] += int(row.get('checkouts_initiated', 0) or 0)
                group['onsite_conversion_post_save'] += int(row.get('onsite_conversion_post_save', 0) or 0)
                group['purchases'] += int(row.get('purchases', 0) or 0)
                group['purchase_value'] += float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0)
                
                # Keep first occurrence info
                if 'campaign_id' not in group:
                    group['campaign_id'] = campaign_id
                    group['campaign_name'] = row.get('campaign_name', '')
                    group['prefix'] = row.get('prefix', '')
                    group['campaign_daily_budget'] = row.get('campaign_daily_budget')
                    group['campaign_lifetime_budget'] = row.get('campaign_lifetime_budget')
                    group['budget_type'] = 'CAMPAIGN'
                    group['budget_level'] = 'CAMPAIGN'
                    # 🔹 FIX: Lưu status cho campaign
                    group['effective_status'] = row.get('effective_status', 'UNKNOWN')
                    group['configured_status'] = row.get('configured_status', 'UNKNOWN')
                    group['delivery'] = row.get('delivery', 'UNKNOWN')
                    # 🔹 FIX: Lưu budget info cho campaign
                    group['using_campaign_budget'] = True  # Campaign luôn dùng campaign budget
                    group['adset_daily_budget'] = None  # Campaign không có adset budget
            
            # Convert to list và tính derived metrics
            rows = []
            for campaign_id, group in grouped_data.items():
                spend = group['spend']
                checkouts = group['checkouts_initiated']
                purchases = group['purchases']
                purchase_value = group['purchase_value']
                data = group['post_comments'] + group['messaging_conversations_started']
                impressions = group['impressions']
                reach = group['reach']
                clicks = group['clicks']
                
                # 🔹 FIX E-COMMERCE METRICS: Tính đầy đủ các metrics theo spec
                group['results'] = data
                # FIX: Giá DATA = spend / (post_comments + messaging_conversations_started)
                group['gia_data'] = (spend / data) if data > 0 else 0
                group['data_cost'] = group['gia_data']  # Alias
                # FIX: Cost per checkout - ưu tiên từ API, fallback tính từ spend
                group['cost_per_checkout_initiated'] = group.get('cost_per_checkout_initiated', 0) or ((spend / checkouts) if checkouts > 0 else 0)
                # FIX: Cost per purchase - ưu tiên từ API, fallback tính từ spend
                group['cost_per_purchase'] = group.get('cost_per_purchase', 0) or ((spend / purchases) if purchases > 0 else 0)
                # FIX: % ADS = (spend / purchase_value) * 100
                group['ads_percent'] = (spend / purchase_value * 100) if purchase_value > 0 else 0
                # FIX: TLC (tỷ lệ chốt) = (purchases / messaging_conversations_started) * 100
                msg_started = group['messaging_conversations_started']
                group['tlc'] = (purchases / msg_started * 100) if msg_started > 0 else 0
                # FIX: Frequency = impressions / reach
                group['frequency'] = (impressions / reach) if reach > 0 else 0
                # Các metrics khác
                group['cpm'] = (spend / impressions * 1000) if impressions > 0 else 0
                group['ctr'] = (clicks / impressions * 100) if impressions > 0 else 0
                group['cpc'] = (spend / clicks) if clicks > 0 else 0
                # FIX: Thêm alias purchase_value
                group['purchase_value'] = purchase_value
                
                rows.append(group)
        
        else:  # level == "ad"
            # Không cần group, dùng rows_for_table trực tiếp
            rows = rows_for_table
        
        # ===== BƯỚC 4: Sort =====
        if sort_by and rows:
            reverse = (sort_order == "desc")
            try:
                rows.sort(key=lambda x: float(x.get(sort_by, 0) or 0), reverse=reverse)
            except (ValueError, TypeError):
                # Fallback: sort by string
                rows.sort(key=lambda x: str(x.get(sort_by, '')), reverse=reverse)
        
        # ===== BƯỚC 4.5: Thêm metadata budget_type + current_budget =====
        for row in rows:
            # 1. Lấy nguyên liệu (convert None thành 0)
            adset_daily = row.get('adset_daily_budget') or 0
            adset_lifetime = row.get('adset_lifetime_budget') or 0
            campaign_daily = row.get('campaign_daily_budget') or 0
            campaign_lifetime = row.get('campaign_lifetime_budget') or 0
            
            # 2. Ưu tiên ngân sách theo thứ tự: adset daily → adset lifetime → campaign daily → campaign lifetime
            current_budget = 0
            budget_type = None
            budget_edit_level = None
            budget_edit_reason = "OK"
            
            # (a) Nếu adset dùng ngân sách NGÀY
            if adset_daily > 0:
                current_budget = int(adset_daily)
                budget_type = "DAILY"
                budget_edit_level = "ADSET"
            
            # (b) Nếu adset dùng ngân sách TRỌN ĐỜI
            elif adset_lifetime > 0:
                current_budget = int(adset_lifetime)
                budget_type = "LIFETIME"
                budget_edit_level = "ADSET"
            
            # (c) Nếu campaign dùng ngân sách NGÀY (CBO daily)
            elif campaign_daily > 0:
                current_budget = int(campaign_daily)
                budget_type = "DAILY"
                budget_edit_level = "CAMPAIGN"
            
            # (d) Nếu campaign dùng ngân sách TRỌN ĐỜI (CBO lifetime)
            elif campaign_lifetime > 0:
                current_budget = int(campaign_lifetime)
                budget_type = "LIFETIME"
                budget_edit_level = "CAMPAIGN"
            
            # (e) Không có budget nào (dự phòng)
            else:
                current_budget = 0
                budget_type = "DAILY"
                budget_edit_level = "ADSET"
                budget_edit_reason = "NO_BUDGET"
            
            # 3. Gán vào row
            row['current_budget'] = current_budget
            row['budget_type'] = budget_type
            row['budget_edit_level'] = budget_edit_level
            row['budget_edit_reason'] = budget_edit_reason
        
        # ===== BƯỚC 5: Pagination =====
        total_rows = len(rows)
        total_pages = ((total_rows - 1) // pageSize) + 1 if total_rows > 0 else 0
        offset = (page - 1) * pageSize
        paginated_rows = rows[offset:offset + pageSize]
        
        logger.info(f"✅ /dashboard/data DONE | rows={len(paginated_rows)}/{total_rows}, page={page}/{total_pages}")
        
        # ===== BƯỚC 6: Return response =====
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
        
    except FacebookRateLimitError:
        # Already handled above
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in /dashboard/data: {e}", exc_info=True)
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
    ✅ FIX: Batch update status - gom tất cả IDs và xử lý 1 lần
    Trả về: total, success_count, failed_count, success_ids, failed_ids
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(status_code=400, detail="Facebook access token not found. Please configure in Settings.")
        
        total = len(payload.items)
        results = []
        errors = []
        success_ids = []
        failed_ids = []
        
        # ✅ XỬ LÝ SONG SONG với asyncio.gather - Nhanh hơn 5-10x
        # Mỗi adset gọi async API với retry thông minh
        if payload.level == "ADSET" or payload.level == "AD":
            # Tạo tasks cho asyncio.gather
            tasks = []
            for item in payload.items:
                if item.new_status == "PAUSED":
                    tasks.append(pause_single_adset_async(item.id, access_token))
                elif item.new_status == "ACTIVE":
                    tasks.append(resume_single_adset_async(item.id, access_token))
                else:
                    # Invalid status - add to failed immediately
                    failed_ids.append(item.id)
                    errors.append({
                        "id": item.id,
                        "error": f"Unsupported status: {item.new_status}"
                    })
            
            # Chạy song song tất cả tasks
            if tasks:
                logger.info(f"🚀 Starting parallel status update for {len(tasks)} adsets")
                task_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Xử lý kết quả
                for i, result in enumerate(task_results):
                    if isinstance(result, Exception):
                        # Exception occurred
                        item_id = payload.items[i].id
                        failed_ids.append(item_id)
                        errors.append({"id": item_id, "error": str(result)})
                        logger.error(f"Exception for adset {item_id}: {result}", exc_info=True)
                    elif result.get("success", False):
                        # Success
                        item_id = result["adset_id"]
                        success_ids.append(item_id)
                        results.append({"id": item_id, "new_status": payload.items[i].new_status})
                        # Clear cache
                        from app.services.facebook_api import _status_cache, _cache_timestamps
                        if access_token in _status_cache:
                            _status_cache[access_token].pop(item_id, None)
                        cache_key = f"status_{access_token[:20]}"
                        _cache_timestamps.pop(cache_key, None)
                    else:
                        # Failed
                        item_id = result.get("adset_id") or payload.items[i].id
                        failed_ids.append(item_id)
                        error_info = {"id": item_id, "error": result.get("error", "Unknown error")}
                        # Thêm chi tiết error nếu có
                        if "error_code" in result:
                            error_info["error_code"] = result["error_code"]
                        if "error_subcode" in result:
                            error_info["error_subcode"] = result["error_subcode"]
                        if "fbtrace_id" in result:
                            error_info["fbtrace_id"] = result["fbtrace_id"]
                        errors.append(error_info)
                
                logger.info(f"✅ Parallel status update completed: {len(success_ids)} success, {len(failed_ids)} failed")
                        
        elif payload.level == "CAMPAIGN":
            # ✅ CAMPAIGN: Xử lý từng cái (vì API không hỗ trợ batch campaign)
            for item in payload.items:
                try:
                    if item.new_status == "PAUSED":
                        result = pause_campaign(item.id, access_token)
                    elif item.new_status == "ACTIVE":
                        result = resume_campaign(item.id, access_token)
                    else:
                        failed_ids.append(item.id)
                        errors.append({
                            "id": item.id,
                            "error": f"Unsupported status for CAMPAIGN: {item.new_status}"
                        })
                        continue
                    
                    if result.get("success", False):
                        success_ids.append(item.id)
                        results.append({"id": item.id, "new_status": item.new_status})
                        # Clear cache
                        from app.services.facebook_api import _status_cache, _cache_timestamps
                        if access_token in _status_cache:
                            _status_cache[access_token].pop(item.id, None)
                        cache_key = f"status_{access_token[:20]}"
                        _cache_timestamps.pop(cache_key, None)
                    else:
                        failed_ids.append(item.id)
                        errors.append({
                            "id": item.id,
                            "error": result.get('error', 'Unknown error')
                        })
                except Exception as e:
                    logger.error(f"Error updating campaign {item.id}: {e}", exc_info=True)
                    failed_ids.append(item.id)
                    errors.append({"id": item.id, "error": str(e)})
        else:
            raise HTTPException(status_code=400, detail=f"Invalid level: {payload.level}")
        
        success_count = len(success_ids)
        failed_count = len(failed_ids)
        
        # ✅ KHÔNG raise 400 nếu có partial success - chỉ raise nếu lỗi thật sự từ backend
        # Frontend sẽ dựa vào success_count/failed_count để hiển thị kết quả
        
        # ✅ Response format mới với total, counts, và danh sách IDs
        return JSONResponse({
            "success": True,
            "total": total,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_ids": success_ids,
            "failed_ids": failed_ids,
            "results": results,
            "errors": errors if errors else None,
            "message": f"Updated {success_count}/{total} status(es) successfully"
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
    🚀 PRODUCTION GRADE: Async parallel budget update với retry thông minh
    
    - NO Facebook Batch API (unreliable for budget updates)
    - Async parallel execution với asyncio.gather
    - Retry logic với exponential backoff
    - Xử lý 4 loại budget: ABO Daily, ABO Lifetime, CBO Daily, CBO Lifetime
    - Detailed logging: error_code, error_subcode, fbtrace_id
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(status_code=400, detail="Facebook access token not found. Please configure in Settings.")
        
        total_requested = len(payload.operations)
        logger.info(f"🚀 Budget update: {total_requested} operations")
        
        # ✅ TẠO ASYNC TASKS CHO TẤT CẢ OPERATIONS
        tasks = []
        for op in payload.operations:
            normalized_budget = _normalize_budget(op.new_budget)
            
            # Lấy metadata từ frontend
            edit_level = getattr(op, 'budget_edit_level', op.level)
            budget_type = getattr(op, 'budget_type', 'DAILY')  # DAILY hoặc LIFETIME
            campaign_id = getattr(op, 'campaign_id', None)
            
            # Xác định level và object_id
            if edit_level == "ADSET":
                object_id = op.id
                level = "ADSET"
            elif edit_level == "CAMPAIGN":
                object_id = campaign_id if campaign_id else op.id
                level = "CAMPAIGN"
            else:
                # Fallback
                object_id = op.id
                level = "ADSET"
            
            # Import async function
            from app.services.facebook_api import update_single_budget_async
            
            # Tạo task
            task = update_single_budget_async(
                object_id=object_id,
                access_token=access_token,
                new_budget=normalized_budget,
                budget_type=budget_type,
                level=level
            )
            tasks.append(task)
        
        # ✅ CHẠY SONG SONG TẤT CẢ TASKS
        logger.info(f"⚡ Running {len(tasks)} budget updates in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # ✅ XỬ LÝ KẾT QUẢ
        all_results = []
        all_errors = []
        
        for i, result in enumerate(results):
            op = payload.operations[i]
            
            # Handle exceptions
            if isinstance(result, Exception):
                logger.error(f"❌ Exception for operation {i}: {result}", exc_info=result)
                all_errors.append({
                    "id": op.id,
                    "level": getattr(op, 'budget_edit_level', op.level),
                    "status": "error",
                    "error": str(result)
                })
                continue
            
            # Handle success/failure
            if result.get("success"):
                all_results.append({
                    "id": result['object_id'],
                    "level": result['level'],
                    "status": "ok",
                    "old_budget": result.get('old_budget'),
                    "new_budget": result.get('new_budget'),
                    "budget_type": result.get('budget_type'),
                    "budget_field": result.get('budget_field')
                })
                
                # Clear cache
                from app.services.facebook_api import _budgets_cache, _cache_timestamps
                if access_token in _budgets_cache:
                    _budgets_cache[access_token].pop(result['object_id'], None)
            else:
                error_detail = {
                    "id": result['object_id'],
                    "level": result['level'],
                    "status": "error",
                    "error": result.get('error', 'Unknown error')
                }
                
                # Thêm Facebook error details nếu có
                if result.get('error_code'):
                    error_detail['error_code'] = result['error_code']
                if result.get('error_subcode'):
                    error_detail['error_subcode'] = result['error_subcode']
                if result.get('fbtrace_id'):
                    error_detail['fbtrace_id'] = result['fbtrace_id']
                
                all_errors.append(error_detail)
        
        success_count = len(all_results)
        failed_count = len(all_errors)
        
        # ✅ Clear batch cache nếu có thành công
        if success_count > 0:
            from app.services.facebook_api import _cache_timestamps
            cache_key = f"budgets_{access_token[:20]}"
            _cache_timestamps.pop(cache_key, None)
        
        # ✅ Log tổng kết
        logger.info(
            f"✅ Budget update done: success={success_count}/{total_requested}, "
            f"failed={failed_count}"
        )
        
        # Response chi tiết
        return JSONResponse({
            "success": True,
            "total": total_requested,
            "success_count": success_count,
            "failed_count": failed_count,
            "results": all_results,
            "errors": all_errors if all_errors else None,
            "message": (
                f"Updated {success_count}/{total_requested} items" +
                (f", {failed_count} errors" if failed_count > 0 else "")
            )
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in budget update endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating budget: {str(e)}")


# Legacy endpoint đã bị xóa - Frontend sử dụng /dashboard/status/update (bulk update)
