"""
Modern Facebook Ads Dashboard - Completely redesigned
Đồng bộ với style hiện tại, tích hợp sâu với Settings
"""
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, distinct, case
from dataclasses import dataclass
import pytz

from app.core.database import get_db, AdMetrics
from app.models.account_prefix import Account, Prefix, AccountPrefix
from app.api.routes.auth import get_current_user_optional
from app.models.user import User
from app.models.user_settings import UserSettings
from app.core.ui_helpers import get_account_locked_message
from app.services.facebook_api import pull_facebook_data, fetch_adset_statuses, pause_adsets, resume_adsets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Timezone Hồ Chí Minh
HCM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Cache in-memory cho Facebook API data (TTL 60s)
@dataclass
class CachedResult:
    timestamp: datetime
    data: List[Dict[str, Any]]

# Global cache dict: key = (view_mode, date_from, date_to, tuple(sorted(account_ids))), value = CachedResult
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
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Lấy insights từ Facebook API với cache (TTL 60s) - Async version
    Key cache: (date_from, date_to, tuple(sorted(account_ids)))
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
                # Xóa cache cũ
                del _insights_cache[cache_key]
    
    # Gọi Facebook API (async để chạy song song các accounts)
    logger.info(f"📥 Gọi Facebook API (cache miss hoặc expired)...")
    from app.services.facebook_api import pull_facebook_data_async
    
    all_data = await pull_facebook_data_async(
        access_token, 
        ad_account_ids, 
        date_preset=None,  # Không dùng preset nếu có custom range
        date_from=date_from,
        date_to=date_to
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
    max_results: int = 5000,  # Giới hạn số lượng để tránh quá tải
    use_cache: bool = True
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
        use_cache=use_cache
    )


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
        
        # Kiểm tra token (field name là facebook_token_encrypted)
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


@router.get("/", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Modern Facebook Ads Dashboard - Redesigned to match current style"""
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
        
        # Modern dashboard HTML đồng bộ với style hiện tại
        html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Dashboard - Facebook Ads Automation</title>
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            width: 100%;
            margin: 0;
            padding: 20px;
        }}
        
        /* Header - giống Settings page */
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 30px;
            padding: 0 10px;
        }}
        
        .header-left {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .header-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            color: white;
            font-size: 32px;
            font-weight: 700;
        }}
        
        .settings-link {{
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            font-size: 16px;
            padding: 8px 16px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }}
        
        .settings-link:hover {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }}
        
        .back-btn {{
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            font-size: 16px;
            padding: 8px 16px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        
        .back-btn:hover {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }}
        
        /* Settings Status */
        .settings-status {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .settings-status.complete {{
            background: rgba(34, 197, 94, 0.1);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.2);
        }}
        
        .settings-status.incomplete {{
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }}
        
        /* Compact Filters Bar (Madgicx Style) */
        .filters-bar {{
            background: white;
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }}
        
        .filters-bar-left {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        
        .filters-bar-right {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .view-mode {{
            display: flex;
            gap: 4px;
        }}
        
        .view-btn {{
            padding: 6px 14px;
            border: 1px solid #e5e7eb;
            background: white;
            color: #6b7280;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 13px;
            transition: all 0.2s ease;
        }}
        
        .view-btn.active {{
            background: #6366f1;
            color: white;
            border-color: #6366f1;
        }}
        
        .filters-btn {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border: 1px solid #d1d5db;
            background: white;
            color: #374151;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 13px;
            position: relative;
        }}
        
        .filters-btn:hover {{
            background: #f9fafb;
        }}
        
        .filter-badge {{
            background: #ef4444;
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .date-range-picker {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border: 1px solid #d1d5db;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            color: #374151;
        }}
        
        .date-range-picker:hover {{
            background: #f9fafb;
        }}
        
        .preset-select {{
            padding: 6px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
            font-size: 13px;
            color: #374151;
            min-width: 160px;
        }}
        
        .refresh-btn-compact {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background: #6366f1;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .refresh-btn-compact:hover {{
            background: #5856eb;
        }}
        
        .refresh-btn-compact.loading .icon {{
            opacity: 0.6;
        }}
        
        /* Filter Panel Modal */
        .filter-panel-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }}
        
        .filter-panel-overlay.open {{
            display: block;
        }}
        
        .filter-panel {{
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            z-index: 1001;
            overflow: hidden;
        }}
        
        .filter-panel.open {{
            display: block;
        }}
        
        .filter-panel-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .filter-panel-header h3 {{
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }}
        
        .close-btn {{
            background: none;
            border: none;
            font-size: 24px;
            color: #6b7280;
            cursor: pointer;
            padding: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
        }}
        
        .close-btn:hover {{
            background: #f3f4f6;
        }}
        
        .filter-panel-content {{
            padding: 24px;
            overflow-y: auto;
            max-height: calc(80vh - 180px);
        }}
        
        .selected-filters-section {{
            margin-bottom: 24px;
        }}
        
        .selected-filters-section h4 {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #374151;
        }}
        
        .selected-filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .filter-tag {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: #f3f4f6;
            border-radius: 6px;
            font-size: 13px;
        }}
        
        .filter-tag-remove {{
            cursor: pointer;
            color: #6b7280;
        }}
        
        .filter-options {{
            margin-bottom: 24px;
        }}
        
        .filter-option-group {{
            margin-bottom: 16px;
        }}
        
        .filter-option-group label {{
            display: block;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
            color: #374151;
        }}
        
        .filter-select {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
            font-size: 14px;
        }}
        
        .filter-suggestions h4 {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #374151;
        }}
        
        .suggestion-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .suggestion-tag {{
            padding: 6px 12px;
            background: #f3f4f6;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .suggestion-tag:hover {{
            background: #e5e7eb;
        }}
        
        .filter-panel-footer {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 12px;
            padding: 16px 24px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .btn-clear, .btn-save, .btn-apply {{
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: all 0.2s ease;
        }}
        
        .btn-clear {{
            background: white;
            color: #6b7280;
            border: 1px solid #d1d5db;
        }}
        
        .btn-save {{
            background: #f3f4f6;
            color: #374151;
        }}
        
        .btn-apply {{
            background: #6366f1;
            color: white;
        }}
        
        .btn-apply:hover {{
            background: #5856eb;
        }}
        
        /* Date Picker Modal - Madgicx Style */
        .date-picker-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 2000;
        }}
        
        .date-picker-overlay.open {{
            display: block;
        }}
        
        .date-picker-modal {{
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            max-width: 900px;
            max-height: 85vh;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            z-index: 2001;
            overflow: hidden;
            flex-direction: column;
        }}
        
        .date-picker-modal.open {{
            display: flex;
        }}
        
        .date-picker-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px;
            border-bottom: 1px solid #e5e7eb;
            flex-shrink: 0;
        }}
        
        .date-picker-header h3 {{
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
        }}
        
        .date-picker-content {{
            display: flex;
            flex: 1;
            overflow: hidden;
        }}
        
        /* Quick Select Sidebar */
        .date-quick-select {{
            width: 220px;
            border-right: 1px solid #e5e7eb;
            padding: 16px;
            overflow-y: auto;
            flex-shrink: 0;
        }}
        
        .quick-select-title {{
            font-size: 13px;
            font-weight: 600;
            color: #6b7280;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .quick-select-item {{
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            color: #374151;
            margin-bottom: 4px;
            transition: all 0.2s ease;
        }}
        
        .quick-select-item:hover {{
            background: #f3f4f6;
        }}
        
        .quick-select-item.active {{
            background: #ede9fe;
            color: #6366f1;
            font-weight: 500;
        }}
        
        .quick-select-divider {{
            height: 1px;
            background: #e5e7eb;
            margin: 12px 0;
        }}
        
        /* Calendar Section */
        .date-calendar-section {{
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
            overflow-y: auto;
        }}
        
        .calendar-container {{
            display: flex;
            gap: 24px;
            margin-bottom: 20px;
        }}
        
        .calendar-month {{
            flex: 1;
        }}
        
        .calendar-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }}
        
        .calendar-month-title {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
        }}
        
        .calendar-nav {{
            display: flex;
            gap: 8px;
        }}
        
        .calendar-nav-btn {{
            width: 28px;
            height: 28px;
            border: 1px solid #d1d5db;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            color: #374151;
            transition: all 0.2s ease;
        }}
        
        .calendar-nav-btn:hover {{
            background: #f9fafb;
            border-color: #9ca3af;
        }}
        
        .calendar-weekdays {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
            margin-bottom: 8px;
        }}
        
        .calendar-weekday {{
            text-align: center;
            font-size: 12px;
            font-weight: 600;
            color: #6b7280;
            padding: 8px 4px;
        }}
        
        .calendar-days {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
        }}
        
        .calendar-day {{
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            color: #374151;
            transition: all 0.2s ease;
            position: relative;
        }}
        
        .calendar-day:hover {{
            background: #f3f4f6;
        }}
        
        .calendar-day.other-month {{
            color: #d1d5db;
        }}
        
        .calendar-day.selected {{
            background: #6366f1;
            color: white;
            font-weight: 600;
        }}
        
        .calendar-day.in-range {{
            background: #ede9fe;
            color: #6366f1;
        }}
        
        .calendar-day.today {{
            border: 2px solid #6366f1;
        }}
        
        /* Date Inputs Footer */
        .date-picker-footer {{
            padding: 16px 20px;
            border-top: 1px solid #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }}
        
        .date-inputs-footer {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        
        .date-input-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .date-input-group label {{
            font-size: 13px;
            font-weight: 500;
            color: #6b7280;
        }}
        
        .date-input-footer {{
            padding: 6px 10px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 13px;
            width: 120px;
        }}
        
        .date-input-clear {{
            width: 20px;
            height: 20px;
            border: none;
            background: none;
            cursor: pointer;
            color: #9ca3af;
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
        }}
        
        .date-input-clear:hover {{
            color: #ef4444;
        }}
        
        .timezone-info {{
            font-size: 12px;
            color: #9ca3af;
            margin-top: 8px;
        }}
        
        .date-picker-actions {{
            display: flex;
            gap: 8px;
        }}
        
        .btn-cancel {{
            padding: 8px 16px;
            border: 1px solid #d1d5db;
            background: white;
            color: #374151;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .btn-cancel:hover {{
            background: #f9fafb;
        }}
        
        .btn-update {{
            padding: 8px 16px;
            border: none;
            background: #6366f1;
            color: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .btn-update:hover {{
            background: #5856eb;
        }}
        
        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        /* Overview Cards */
        .overview-grid {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }}
        
        @media (max-width: 1400px) {{
            .overview-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
        }}
        
        @media (max-width: 768px) {{
            .overview-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 480px) {{
            .overview-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .overview-card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease;
        }}
        
        .overview-card:hover {{
            transform: translateY(-2px);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }}
        
        .card-title {{
            font-size: 14px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .card-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: white;
        }}
        
        .card-icon.spend {{ background: #6366f1; }}
        .card-icon.leads {{ background: #22c55e; }}
        .card-icon.gia {{ background: #f59e0b; }}
        .card-icon.adsets {{ background: #8b5cf6; }}
        .card-icon.ads {{ background: #ef4444; }}
        .card-icon.purchase {{ background: #06b6d4; }}
        
        .card-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 8px;
        }}
        
        .card-subtitle {{
            font-size: 14px;
            color: #6b7280;
        }}
        
        /* Data Table */
        .table-container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .table-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .table-title-section {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .table-title {{
            font-size: 18px;
            font-weight: 700;
            color: #1f2937;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .level-tabs {{
            display: flex;
            gap: 8px;
        }}
        
        .level-tab {{
            padding: 6px 16px;
            border: 1px solid #e5e7eb;
            background: white;
            color: #6b7280;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s ease;
        }}
        
        .level-tab:hover {{
            background: #f9fafb;
            border-color: #d1d5db;
        }}
        
        .level-tab.active {{
            background: #6366f1;
            color: white;
            border-color: #6366f1;
        }}
        
        .table-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .search-box {{
            position: relative;
            display: flex;
            align-items: center;
        }}
        
        .search-input {{
            padding: 8px 12px 8px 36px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            width: 320px;
            font-size: 14px;
        }}
        
        .search-icon {{
            position: absolute;
            left: 12px;
            color: #9ca3af;
            pointer-events: none;
        }}
        
        .bulk-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
            opacity: 0;
            transition: all 0.3s ease;
        }}
        
        .bulk-actions.visible {{
            opacity: 1;
        }}
        
        .bulk-btn {{
            padding: 6px 12px;
            border: 1px solid #d1d5db;
            background: white;
            color: #374151;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .bulk-btn.play {{ color: #22c55e; border-color: #22c55e; }}
        .bulk-btn.pause {{ color: #ef4444; border-color: #ef4444; }}
        
        /* Table Styles */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .data-table th,
        .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #f3f4f6;
        }}
        
        .data-table th {{
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
            font-size: 14px;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        .data-table tbody tr:hover {{
            background: #f9fafb;
        }}
        
        .data-table td {{
            font-size: 14px;
            color: #1f2937;
        }}
        
        /* Status indicators */
        .status-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }}
        
        .status-dot.active {{ background: #22c55e; }}
        .status-dot.paused {{ background: #ef4444; }}
        .status-dot.error {{ background: #d1d5db; }}
        
        .toggle-btn {{
            width: 40px;
            height: 20px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            position: relative;
            transition: all 0.3s ease;
        }}
        
        .toggle-btn.active {{
            background: #22c55e;
        }}
        
        .toggle-btn.paused {{
            background: #ef4444;
        }}
        
        .toggle-btn::after {{
            content: '';
            position: absolute;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: white;
            top: 2px;
            left: 2px;
            transition: all 0.3s ease;
        }}
        
        .toggle-btn.active::after {{
            left: 22px;
        }}
        
        /* Checkbox styles */
        .checkbox {{
            width: 16px;
            height: 16px;
            border: 2px solid #d1d5db;
            border-radius: 4px;
            cursor: pointer;
            position: relative;
        }}
        
        .checkbox.checked {{
            background: #6366f1;
            border-color: #6366f1;
        }}
        
        .checkbox.checked::after {{
            content: '✓';
            position: absolute;
            top: -2px;
            left: 2px;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
        
        /* Utility classes */
        .text-right {{ text-align: right; }}
        .text-center {{ text-align: center; }}
        .font-medium {{ font-weight: 500; }}
        .font-semibold {{ font-weight: 600; }}
        .font-bold {{ font-weight: 700; }}
        .text-green {{ color: #22c55e; }}
        .text-red {{ color: #ef4444; }}
        .text-blue {{ color: #6366f1; }}
        .text-gray {{ color: #6b7280; }}
        .hidden {{ display: none; }}
        
        /* Loading states */
        .loading {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            color: #6b7280;
        }}
        
        .spinner {{
            width: 24px;
            height: 24px;
            border: 2px solid #f3f4f6;
            border-top: 2px solid #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 12px;
        }}
        
        /* Empty state */
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #6b7280;
        }}
        
        .empty-icon {{
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }}
        
        /* Responsive adjustments */
        @media (max-width: 1024px) {{
            .overview-grid {{
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 16px;
            }}
            
            .control-row {{
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }}
            
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div class="header-left">
                <div class="header-title">
                    <span>🚀</span>
                    <span>Facebook Ads Automation - Dashboard</span>
                </div>
                <div class="settings-status" id="settingsStatus">
                    <span class="spinner"></span>
                    <span>Đang tải...</span>
                </div>
            </div>
            <div class="header-right">
                <a href="/settings" class="settings-link">⚙️ Cài Đặt</a>
                <a href="/" class="back-btn">← Về Trang Chủ</a>
            </div>
        </header>
        
        <!-- Compact Filters Bar (Madgicx Style) -->
        <div class="filters-bar">
            <div class="filters-bar-left">
                <!-- View Mode -->
                <div class="view-mode">
                    <button class="view-btn active" data-mode="ecommerce" onclick="switchViewMode('ecommerce')">
                        🛒 E-Commerce
                    </button>
                    <button class="view-btn" data-mode="lead" onclick="switchViewMode('lead')">
                        📋 Lead Generation
                    </button>
                </div>
                
                <!-- Filters Button -->
                <button class="filters-btn" id="filtersBtn" onclick="toggleFilterPanel()">
                    <span>Filters</span>
                    <span class="filter-badge" id="filterBadge" style="display: none;">0</span>
                </button>
                
                <!-- Date Range Picker -->
                <div class="date-range-picker" id="dateRangePicker" onclick="openDatePicker()">
                    <span class="date-icon">📅</span>
                    <span id="dateRangeText">7 ngày qua</span>
                </div>
                
                <!-- Load Filter Preset -->
                <select class="preset-select" id="presetSelect" onchange="loadPreset()">
                    <option value="">Load filter preset</option>
                    <option value="active">Active Ad Sets</option>
                    <option value="paused">Paused Ad Sets</option>
                    <option value="all">All Ad Sets</option>
                </select>
            </div>
            
            <div class="filters-bar-right">
                <!-- Refresh Button -->
                <button class="refresh-btn-compact" id="refreshBtn" onclick="refreshData()" title="Làm mới">
                    <span class="icon">🔄</span>
                </button>
            </div>
        </div>
        
        <!-- Filter Panel Modal -->
        <div class="filter-panel-overlay" id="filterPanelOverlay" onclick="closeFilterPanel()"></div>
        <div class="filter-panel" id="filterPanel" onclick="event.stopPropagation()">
            <div class="filter-panel-header">
                <h3>Filters</h3>
                <button class="close-btn" onclick="event.stopPropagation(); closeFilterPanel();">✕</button>
            </div>
            
            <div class="filter-panel-content">
                <!-- Selected Filters -->
                <div class="selected-filters-section">
                    <h4>Selected Filters</h4>
                    <div class="selected-filters" id="selectedFilters">
                        <!-- Active filters will be shown here -->
                    </div>
                </div>
                
                <!-- Filter Options -->
                <div class="filter-options">
                    <div class="filter-option-group">
                        <label>Tài khoản:</label>
                        <select class="filter-select" id="accountFilter" onchange="updateFilters()">
                            <option value="">Tất cả tài khoản</option>
                        </select>
                    </div>
                    
                    <div class="filter-option-group">
                        <label>Prefix:</label>
                        <select class="filter-select" id="prefixFilter" onchange="updateFilters()">
                            <option value="">Tất cả prefix</option>
                        </select>
                    </div>
                    
                    <div class="filter-option-group">
                        <label>Trạng thái:</label>
                        <select class="filter-select" id="statusFilter" onchange="updateFilters()">
                            <option value="">Tất cả</option>
                            <option value="ACTIVE">Hoạt động</option>
                            <option value="PAUSED">Tạm dừng</option>
                        </select>
                    </div>
                </div>
                
                <!-- Suggestions -->
                <div class="filter-suggestions">
                    <h4>Suggestions</h4>
                    <div class="suggestion-tags">
                        <span class="suggestion-tag" onclick="applySuggestion('active')">Active Ad Sets</span>
                        <span class="suggestion-tag" onclick="applySuggestion('paused')">Paused Ad Sets</span>
                        <span class="suggestion-tag" onclick="applySuggestion('today')">Today</span>
                        <span class="suggestion-tag" onclick="applySuggestion('last7days')">Last 7 Days</span>
                    </div>
                </div>
            </div>
            
            <div class="filter-panel-footer">
                <button class="btn-clear" onclick="clearAllFilters()">Clear All Filters</button>
                <button class="btn-save" onclick="saveFilterPreset()">Save Filters</button>
                <button class="btn-apply" onclick="applyFilters()">Apply</button>
            </div>
        </div>
        
        <!-- Date Picker Modal - Madgicx Style -->
        <div class="date-picker-overlay" id="datePickerOverlay" onclick="if(typeof window.closeDatePicker === 'function') window.closeDatePicker();"></div>
        <div class="date-picker-modal" id="datePickerModal" onclick="event.stopPropagation()">
            <div class="date-picker-header">
                <h3>Chọn khoảng thời gian</h3>
                <button class="close-btn" onclick="event.stopPropagation(); event.preventDefault(); if(typeof window.closeDatePicker === 'function') window.closeDatePicker(); return false;">✕</button>
            </div>
            <div class="date-picker-content">
                <!-- Quick Select Sidebar -->
                <div class="date-quick-select">
                    <div class="quick-select-title">Đã dùng mới đây</div>
                    <div class="quick-select-item" data-preset="today" onclick="selectQuickDate('today')">Hôm nay</div>
                    <div class="quick-select-item" data-preset="yesterday" onclick="selectQuickDate('yesterday')">Hôm qua</div>
                    <div class="quick-select-item" data-preset="last3days" onclick="selectQuickDate('last3days')">3 ngày qua</div>
                    <div class="quick-select-item" data-preset="last7days" onclick="selectQuickDate('last7days')">7 ngày qua</div>
                    <div class="quick-select-item" data-preset="last14days" onclick="selectQuickDate('last14days')">14 ngày qua</div>
                    <div class="quick-select-item" data-preset="last28days" onclick="selectQuickDate('last28days')">28 ngày qua</div>
                    <div class="quick-select-item" data-preset="last30days" onclick="selectQuickDate('last30days')">30 ngày qua</div>
                    <div class="quick-select-divider"></div>
                    <div class="quick-select-item" data-preset="thisWeek" onclick="selectQuickDate('thisWeek')">Tuần này</div>
                    <div class="quick-select-item" data-preset="lastWeek" onclick="selectQuickDate('lastWeek')">Tuần trước</div>
                    <div class="quick-select-item" data-preset="thisMonth" onclick="selectQuickDate('thisMonth')">Tháng này</div>
                    <div class="quick-select-item" data-preset="lastMonth" onclick="selectQuickDate('lastMonth')">Tháng trước</div>
                </div>
                
                <!-- Calendar Section -->
                <div class="date-calendar-section">
                    <div class="calendar-container">
                        <!-- First Calendar Month -->
                        <div class="calendar-month" id="calendarMonth1">
                            <div class="calendar-header">
                                <span class="calendar-month-title" id="monthTitle1"></span>
                                <div class="calendar-nav">
                                    <button class="calendar-nav-btn" onclick="navigateCalendar(-1)">‹</button>
                                    <button class="calendar-nav-btn" onclick="navigateCalendar(1)">›</button>
                                </div>
                            </div>
                            <div class="calendar-weekdays">
                                <div class="calendar-weekday">CN</div>
                                <div class="calendar-weekday">T2</div>
                                <div class="calendar-weekday">T3</div>
                                <div class="calendar-weekday">T4</div>
                                <div class="calendar-weekday">T5</div>
                                <div class="calendar-weekday">T6</div>
                                <div class="calendar-weekday">T7</div>
                            </div>
                            <div class="calendar-days" id="calendarDays1"></div>
                        </div>
                        
                        <!-- Second Calendar Month -->
                        <div class="calendar-month" id="calendarMonth2">
                            <div class="calendar-header">
                                <span class="calendar-month-title" id="monthTitle2"></span>
                                <div class="calendar-nav">
                                    <button class="calendar-nav-btn" onclick="navigateCalendar(-1)">‹</button>
                                    <button class="calendar-nav-btn" onclick="navigateCalendar(1)">›</button>
                                </div>
                            </div>
                            <div class="calendar-weekdays">
                                <div class="calendar-weekday">CN</div>
                                <div class="calendar-weekday">T2</div>
                                <div class="calendar-weekday">T3</div>
                                <div class="calendar-weekday">T4</div>
                                <div class="calendar-weekday">T5</div>
                                <div class="calendar-weekday">T6</div>
                                <div class="calendar-weekday">T7</div>
                            </div>
                            <div class="calendar-days" id="calendarDays2"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer with Date Inputs -->
            <div class="date-picker-footer">
                <div>
                    <div class="date-inputs-footer">
                        <div class="date-input-group">
                            <label>Từ:</label>
                            <input type="text" id="dateFromFooter" class="date-input-footer" readonly>
                            <button class="date-input-clear" onclick="clearDate('from')" title="Xóa">✕</button>
                        </div>
                        <div class="date-input-group">
                            <label>Đến:</label>
                            <input type="text" id="dateToFooter" class="date-input-footer" readonly>
                            <button class="date-input-clear" onclick="clearDate('to')" title="Xóa">✕</button>
                        </div>
                    </div>
                    <div class="timezone-info">Ngày hiển thị theo Giờ TP Hồ Chí Minh</div>
                </div>
                <div class="date-picker-actions">
                    <button class="btn-cancel" onclick="event.stopPropagation(); event.preventDefault(); if(typeof window.closeDatePicker === 'function') window.closeDatePicker(); return false;">Hủy</button>
                    <button class="btn-update" onclick="event.stopPropagation(); event.preventDefault(); applyDateRange(); return false;">Cập nhật</button>
                </div>
            </div>
        </div>
        
        <!-- Overview Cards -->
        <div class="overview-grid" id="overviewGrid">
            <!-- Cards sẽ được tạo bởi JavaScript -->
        </div>
        
        <!-- Data Table -->
        <div class="table-container">
            <div class="table-header">
                <div class="table-title-section">
                    <div class="table-title">
                        <span id="tableIcon">📊</span>
                        <span id="tableTitle">Chi Tiết Quảng Cáo E-Commerce</span>
                    </div>
                    <!-- Level Tabs -->
                    <div class="level-tabs">
                        <button class="level-tab active" data-level="campaign" onclick="switchLevel('campaign')">Chiến Dịch</button>
                        <button class="level-tab" data-level="adset" onclick="switchLevel('adset')">Nhóm Quảng Cáo</button>
                        <button class="level-tab" data-level="ad" onclick="switchLevel('ad')">Quảng Cáo</button>
                    </div>
                </div>
                <div class="table-actions">
                    <!-- Bulk Actions -->
                    <div class="bulk-actions" id="bulkActions">
                        <span id="selectedCount">0 đã chọn</span>
                        <button class="bulk-btn play" onclick="bulkAction('activate')">▶️ Bật</button>
                        <button class="bulk-btn pause" onclick="bulkAction('pause')">⏸️ Tắt</button>
                    </div>
                    
                    <!-- Search Box -->
                    <div class="search-box">
                        <div class="search-icon">🔍</div>
                        <input type="text" class="search-input" id="searchInput" placeholder="Tìm kiếm tên/ID chiến dịch, nhóm quảng cáo, quảng cáo...">
                    </div>
                </div>
            </div>
            
            <div style="overflow-x: auto; max-height: 600px; overflow-y: auto;">
                <table class="data-table" id="dataTable">
                    <thead id="tableHead">
                        <!-- Headers sẽ được tạo bởi JavaScript -->
                    </thead>
                    <tbody id="tableBody">
                        <tr>
                            <td colspan="20" class="loading">
                                <div class="spinner"></div>
                                <span>Đang tải dữ liệu...</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        // Global variables
        let currentViewMode = 'ecommerce';
        let currentLevel = 'adset'; // campaign, adset, or ad
        let currentPage = 1;
        let pageSize = 50;
        let currentFilters = {{
            account: '',
            prefix: '',
            dateRange: 'today',
            search: ''
        }};
        let selectedItems = new Set();
        let isLoading = false;
        let settingsData = null;
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {{
            // Load saved filters from localStorage
            loadSavedFilters();
            
            // Setup event listeners
            setupEventListeners();
            
            // Load initial data
            checkSettingsStatus();
            loadFilters();
            loadData();
        }});
        
        // Setup event listeners
        function setupEventListeners() {{
            // Search input with debouncing
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {{
                let searchTimeout;
                searchInput.addEventListener('input', function() {{
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {{
                        currentFilters.search = this.value;
                        currentPage = 1; // Reset to first page when searching
                        saveFilters();
                        loadData();
                    }}, 500);
                }});
            }}
            
            // Handle page refresh - restore filters
            window.addEventListener('beforeunload', function() {{
                saveFilters();
            }});
        }}
        
        // Save/load filters to localStorage
        function saveFilters() {{
            localStorage.setItem('dashboard_filters', JSON.stringify({{
                ...currentFilters,
                viewMode: currentViewMode,
                level: currentLevel,
                page: currentPage
            }}));
        }}
        
        function loadSavedFilters() {{
            const saved = localStorage.getItem('dashboard_filters');
            if (saved) {{
                const filters = JSON.parse(saved);
                currentFilters = {{
                    account: filters.account || '',
                    prefix: filters.prefix || '',
                    dateRange: filters.dateRange || 'today',
                    dateFrom: filters.dateFrom || '',
                    dateTo: filters.dateTo || '',
                    status: filters.status || '',
                    search: filters.search || ''
                }};
                
                if (filters.viewMode) {{
                    currentViewMode = filters.viewMode;
                    // Update view mode buttons
                    document.querySelectorAll('.view-btn').forEach(btn => {{
                        btn.classList.toggle('active', btn.dataset.mode === currentViewMode);
                    }});
                }}
                
                if (filters.level) {{
                    currentLevel = filters.level;
                    // Update level tabs
                    document.querySelectorAll('.level-tab').forEach(tab => {{
                        tab.classList.toggle('active', tab.dataset.level === currentLevel);
                    }});
                }}
                
                if (filters.page) {{
                    currentPage = filters.page;
                }}
                
                // Restore filter values
                if (document.getElementById('accountFilter')) {{
                    document.getElementById('accountFilter').value = currentFilters.account;
                }}
                if (document.getElementById('prefixFilter')) {{
                    document.getElementById('prefixFilter').value = currentFilters.prefix;
                }}
                if (document.getElementById('statusFilter')) {{
                    document.getElementById('statusFilter').value = currentFilters.status;
                }}
                if (document.getElementById('searchInput')) {{
                    document.getElementById('searchInput').value = currentFilters.search || '';
                }}
                
                // Restore date range text
                if (currentFilters.dateRange === 'custom' && currentFilters.dateFrom && currentFilters.dateTo) {{
                    const fromDate = new Date(currentFilters.dateFrom);
                    const toDate = new Date(currentFilters.dateTo);
                    const dateText = formatDateRangeText(fromDate, toDate);
                    if (document.getElementById('dateRangeText')) {{
                        document.getElementById('dateRangeText').textContent = dateText;
                    }}
                }} else {{
                    const rangeTexts = {{
                        'today': 'Hôm nay',
                        'yesterday': 'Hôm qua',
                        'last7days': '7 ngày qua',
                        'last30days': '30 ngày qua'
                    }};
                    if (document.getElementById('dateRangeText')) {{
                        document.getElementById('dateRangeText').textContent = rangeTexts[currentFilters.dateRange] || 'Hôm nay';
                    }}
                }}
                
                // Update filter badge and selected filters after a short delay (to ensure DOM is ready)
                setTimeout(() => {{
                    updateFilterBadge();
                    updateSelectedFilters();
                }}, 100);
            }}
        }}
        
        // Authentication helper
        function getAuthToken() {{
            return localStorage.getItem('access_token') || '';
        }}
        
        // Check settings status
        async function checkSettingsStatus() {{
            try {{
                const response = await fetch('/dashboard/settings-status', {{
                    headers: {{
                        'Authorization': 'Bearer ' + getAuthToken()
                    }}
                }});
                
                if (response.ok) {{
                    const status = await response.json();
                    updateSettingsStatus(status);
                }}
            }} catch (error) {{
                console.error('Error checking settings status:', error);
                updateSettingsStatus({{settings_complete: false}});
            }}
        }}
        
        // Update settings status indicator
        function updateSettingsStatus(status) {{
            const statusElement = document.getElementById('settingsStatus');
            
            if (status.settings_complete) {{
                statusElement.className = 'settings-status complete';
                statusElement.innerHTML = `
                    <span>✅</span>
                    <span>Sẵn sàng ({{status.accounts_count}} accounts, {{status.prefixes_count}} prefixes)</span>
                `;
            }} else {{
                statusElement.className = 'settings-status incomplete';
                let message = 'Cần cấu hình';
                if (!status.has_token) message = 'Thiếu token - Cần cài đặt';
                else if (status.accounts_count === 0) message = 'Chưa có accounts - Cần thêm';
                else if (status.prefixes_count === 0) message = 'Chưa có prefixes - Cần thêm';
                
                statusElement.innerHTML = `
                    <span>⚠️</span>
                    <span>${{message}}</span>
                `;
            }}
        }}
        
        // Load available filters from settings
        async function loadFilters() {{
            try {{
                console.log('Loading filters from settings...');
                const response = await fetch('/dashboard/filters', {{
                    headers: {{
                        'Authorization': 'Bearer ' + getAuthToken()
                    }}
                }});
                
                if (response.ok) {{
                    settingsData = await response.json();
                    console.log('Filters loaded:', settingsData);
                    // Populate immediately if DOM is ready, otherwise wait
                    if (document.getElementById('accountFilter')) {{
                        populateFilterDropdowns();
                    }} else {{
                        setTimeout(() => {{
                            populateFilterDropdowns();
                        }}, 200);
                    }}
                }} else {{
                    console.error('Failed to load filters:', response.status, await response.text());
                }}
            }} catch (error) {{
                console.error('Error loading filters:', error);
            }}
        }}
        
        // Populate filter dropdowns
        function populateFilterDropdowns() {{
            if (!settingsData) {{
                console.warn('settingsData is null, cannot populate dropdowns. Loading filters...');
                loadFilters();
                return;
            }}
            
            console.log('Populating filter dropdowns...', settingsData);
            
            // Populate account filter
            const accountSelect = document.getElementById('accountFilter');
            if (accountSelect) {{
                accountSelect.innerHTML = '<option value="">Tất cả tài khoản</option>';
                if (settingsData.accounts && settingsData.accounts.length > 0) {{
                    settingsData.accounts.forEach(acc => {{
                        const option = document.createElement('option');
                        option.value = acc.id;
                        option.textContent = `${{acc.name || acc.id}}` + (acc.type ? ` (${{acc.type}})` : '');
                        accountSelect.appendChild(option);
                    }});
                    console.log(`Populated ${{settingsData.accounts.length}} accounts`);
                }} else {{
                    console.warn('No accounts found in settingsData');
                }}
                if (currentFilters.account) {{
                    accountSelect.value = currentFilters.account;
                }}
            }} else {{
                console.warn('accountFilter element not found');
            }}
            
            // Populate prefix filter
            const prefixSelect = document.getElementById('prefixFilter');
            if (prefixSelect) {{
                prefixSelect.innerHTML = '<option value="">Tất cả prefix</option>';
                if (settingsData.prefixes && settingsData.prefixes.length > 0) {{
                    settingsData.prefixes.forEach(prefix => {{
                        const option = document.createElement('option');
                        option.value = prefix.id;
                        option.textContent = prefix.name || prefix.id;
                        prefixSelect.appendChild(option);
                    }});
                    console.log(`Populated ${{settingsData.prefixes.length}} prefixes`);
                }} else {{
                    console.warn('No prefixes found in settingsData');
                }}
                if (currentFilters.prefix) {{
                    prefixSelect.value = currentFilters.prefix;
                }}
            }} else {{
                console.warn('prefixFilter element not found');
            }}
        }}
        
        // Switch view mode
        function switchViewMode(mode) {{
            currentViewMode = mode;
            
            // Update button states
            document.querySelectorAll('.view-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.mode === mode);
            }});
            
            // Update table title
            const title = mode === 'ecommerce' ? 'Chi Tiết Quảng Cáo E-Commerce' : 'Chi Tiết Quảng Cáo Lead Generation';
            const icon = mode === 'ecommerce' ? '🛒' : '📋';
            document.getElementById('tableTitle').textContent = title;
            document.getElementById('tableIcon').textContent = icon;
            
            // Save and reload data
            saveFilters();
            loadData();
        }}
        
        // Switch level (campaign/adset/ad)
        function switchLevel(level) {{
            currentLevel = level;
            
            // Update tab states
            document.querySelectorAll('.level-tab').forEach(tab => {{
                tab.classList.toggle('active', tab.dataset.level === level);
            }});
            
            // Reset page to 1 when switching level
            currentPage = 1;
            selectedItems.clear();
            
            // Save and reload data
            saveFilters();
            loadData();
        }}
        
        // Filter Panel Functions
        function toggleFilterPanel() {{
            const panel = document.getElementById('filterPanel');
            const overlay = document.getElementById('filterPanelOverlay');
            const isOpening = !panel.classList.contains('open');
            
            // QUAN TRỌNG: Nếu đang mở filter panel, đóng date picker trước
            if (isOpening) {{
                if (typeof window.closeDatePicker === 'function') {{
                    window.closeDatePicker();
                }}
            }}
            
            panel.classList.toggle('open');
            overlay.classList.toggle('open');
            
            // If opening panel and filters not loaded yet, load them
            if (isOpening && !settingsData) {{
                loadFilters();
            }} else if (isOpening) {{
                // Ensure dropdowns are populated when opening panel
                populateFilterDropdowns();
            }}
        }}
        
        function closeFilterPanel() {{
            try {{
                const panel = document.getElementById('filterPanel');
                const overlay = document.getElementById('filterPanelOverlay');
                if (panel) panel.classList.remove('open');
                if (overlay) overlay.classList.remove('open');
            }} catch (e) {{
                console.error('Error closing filter panel:', e);
            }}
        }}
        
        function openFilterPanel() {{
            // QUAN TRỌNG: Đóng date picker trước khi mở filter panel
            if (typeof window.closeDatePicker === 'function') {{
                window.closeDatePicker();
            }}
            
            const panel = document.getElementById('filterPanel');
            const overlay = document.getElementById('filterPanelOverlay');
            
            if (!panel || !overlay) {{
                console.error('Filter panel elements not found');
                return;
            }}
            
            // Load filters nếu chưa load
            if (!settingsData) {{
                loadFilters();
            }}
            
            panel.classList.add('open');
            overlay.classList.add('open');
        }}
        
        // Date Picker Functions - Madgicx Style
        let currentCalendarMonth = new Date();
        let selectedDateFrom = null;
        let selectedDateTo = null;
        let isSelectingRange = false;
        
        const monthNames = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 
                           'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'];
        const monthNamesShort = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'];
        
        function openDatePicker() {{
            // QUAN TRỌNG: Đóng filter panel trước khi mở date picker
            if (typeof closeFilterPanel === 'function') {{
                closeFilterPanel();
            }}
            
            const modal = document.getElementById('datePickerModal');
            const overlay = document.getElementById('datePickerOverlay');
            
            if (!modal || !overlay) {{
                console.error('Date picker elements not found');
                return;
            }}
            
            // Initialize calendar with current date range
            if (currentFilters.dateFrom && currentFilters.dateTo) {{
                selectedDateFrom = new Date(currentFilters.dateFrom);
                selectedDateTo = new Date(currentFilters.dateTo);
            }} else {{
                // Default to last 7 days
                const today = new Date();
                selectedDateTo = new Date(today);
                selectedDateFrom = new Date(today);
                selectedDateFrom.setDate(today.getDate() - 6);
            }}
            
            currentCalendarMonth = new Date(selectedDateFrom);
            renderCalendars();
            updateDateInputs();
            updateQuickSelectActive();
            
            modal.classList.add('open');
            overlay.classList.add('open');
        }}
        
        // Đảm bảo function closeDatePicker được định nghĩa global
        window.closeDatePicker = function() {{
            console.log('closeDatePicker called');
            try {{
                const modal = document.getElementById('datePickerModal');
                const overlay = document.getElementById('datePickerOverlay');
                console.log('Modal:', modal, 'Overlay:', overlay);
                if (modal) {{
                    modal.classList.remove('open');
                    console.log('Removed open class from modal');
                }}
                if (overlay) {{
                    overlay.classList.remove('open');
                    console.log('Removed open class from overlay');
                }}
            }} catch (e) {{
                console.error('Error closing date picker:', e);
            }}
        }};
        
        // Alias để đảm bảo tương thích
        function closeDatePicker() {{
            window.closeDatePicker();
        }}
        
        // Đảm bảo date picker có thể đóng bằng ESC key
        // Sử dụng window.addEventListener để đảm bảo event listener được thêm đúng cách
        if (typeof window !== 'undefined') {{
            window.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{
                    const dateModal = document.getElementById('datePickerModal');
                    const filterPanel = document.getElementById('filterPanel');
                    if (dateModal && dateModal.classList.contains('open')) {{
                        if (typeof window.closeDatePicker === 'function') {{
                            window.closeDatePicker();
                        }}
                    }} else if (filterPanel && filterPanel.classList.contains('open')) {{
                        if (typeof closeFilterPanel === 'function') {{
                            closeFilterPanel();
                        }}
                    }}
                }}
            }});
        }}
        
        function renderCalendars() {{
            // Render first calendar (current month)
            const month1 = new Date(currentCalendarMonth);
            renderCalendar('calendarMonth1', 'monthTitle1', 'calendarDays1', month1);
            
            // Render second calendar (next month)
            const month2 = new Date(month1);
            month2.setMonth(month2.getMonth() + 1);
            renderCalendar('calendarMonth2', 'monthTitle2', 'calendarDays2', month2);
        }}
        
        function renderCalendar(monthId, titleId, daysId, date) {{
            const year = date.getFullYear();
            const month = date.getMonth();
            
            // Set month title
            document.getElementById(titleId).textContent = `${{monthNames[month]}} ${{year}}`;
            
            // Get first day of month and number of days
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const daysInMonth = lastDay.getDate();
            const startingDayOfWeek = firstDay.getDay(); // 0 = Sunday
            
            // Clear previous days
            const daysContainer = document.getElementById(daysId);
            daysContainer.innerHTML = '';
            
            // Add empty cells for days before month starts
            for (let i = 0; i < startingDayOfWeek; i++) {{
                const emptyDay = document.createElement('div');
                emptyDay.className = 'calendar-day other-month';
                daysContainer.appendChild(emptyDay);
            }}
            
            // Add days of month
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            for (let day = 1; day <= daysInMonth; day++) {{
                const dayDate = new Date(year, month, day);
                const dayElement = document.createElement('div');
                dayElement.className = 'calendar-day';
                dayElement.textContent = day;
                dayElement.dataset.date = formatDateForAPI(dayDate);
                
                // Check if today
                if (dayDate.getTime() === today.getTime()) {{
                    dayElement.classList.add('today');
                }}
                
                // Check if selected
                if (selectedDateFrom && dayDate.getTime() === selectedDateFrom.getTime()) {{
                    dayElement.classList.add('selected');
                }}
                if (selectedDateTo && dayDate.getTime() === selectedDateTo.getTime()) {{
                    dayElement.classList.add('selected');
                }}
                
                // Check if in range
                if (selectedDateFrom && selectedDateTo) {{
                    if (dayDate > selectedDateFrom && dayDate < selectedDateTo) {{
                        dayElement.classList.add('in-range');
                    }}
                }}
                
                dayElement.onclick = () => selectDate(dayDate);
                daysContainer.appendChild(dayElement);
            }}
        }}
        
        function selectDate(date) {{
            if (!selectedDateFrom || (selectedDateFrom && selectedDateTo)) {{
                // Start new selection
                selectedDateFrom = new Date(date);
                selectedDateTo = null;
                isSelectingRange = true;
            }} else {{
                // Complete selection
                if (date < selectedDateFrom) {{
                    selectedDateTo = new Date(selectedDateFrom);
                    selectedDateFrom = new Date(date);
                }} else {{
                    selectedDateTo = new Date(date);
                }}
                isSelectingRange = false;
            }}
            
            renderCalendars();
            updateDateInputs();
        }}
        
        function navigateCalendar(direction) {{
            currentCalendarMonth.setMonth(currentCalendarMonth.getMonth() + direction);
            renderCalendars();
        }}
        
        function selectQuickDate(preset) {{
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            // Remove active class from all items
            document.querySelectorAll('.quick-select-item').forEach(item => {{
                item.classList.remove('active');
            }});
            
            // Add active class to selected item
            const selectedItem = document.querySelector(`[data-preset="${{preset}}"]`);
            if (selectedItem) {{
                selectedItem.classList.add('active');
            }}
            
            switch(preset) {{
                case 'today':
                    selectedDateFrom = new Date(today);
                    selectedDateTo = new Date(today);
                    break;
                case 'yesterday':
                    const yesterday = new Date(today);
                    yesterday.setDate(yesterday.getDate() - 1);
                    selectedDateFrom = yesterday;
                    selectedDateTo = yesterday;
                    break;
                case 'last3days':
                    selectedDateTo = new Date(today);
                    selectedDateFrom = new Date(today);
                    selectedDateFrom.setDate(today.getDate() - 2);
                    break;
                case 'last7days':
                    selectedDateTo = new Date(today);
                    selectedDateFrom = new Date(today);
                    selectedDateFrom.setDate(today.getDate() - 6);
                    break;
                case 'last14days':
                    selectedDateTo = new Date(today);
                    selectedDateFrom = new Date(today);
                    selectedDateFrom.setDate(today.getDate() - 13);
                    break;
                case 'last28days':
                    selectedDateTo = new Date(today);
                    selectedDateFrom = new Date(today);
                    selectedDateFrom.setDate(today.getDate() - 27);
                    break;
                case 'last30days':
                    selectedDateTo = new Date(today);
                    selectedDateFrom = new Date(today);
                    selectedDateFrom.setDate(today.getDate() - 29);
                    break;
                case 'thisWeek':
                    const thisWeekStart = new Date(today);
                    thisWeekStart.setDate(today.getDate() - today.getDay());
                    selectedDateFrom = thisWeekStart;
                    selectedDateTo = new Date(today);
                    break;
                case 'lastWeek':
                    const lastWeekEnd = new Date(today);
                    lastWeekEnd.setDate(today.getDate() - today.getDay() - 1);
                    const lastWeekStart = new Date(lastWeekEnd);
                    lastWeekStart.setDate(lastWeekEnd.getDate() - 6);
                    selectedDateFrom = lastWeekStart;
                    selectedDateTo = lastWeekEnd;
                    break;
                case 'thisMonth':
                    selectedDateFrom = new Date(today.getFullYear(), today.getMonth(), 1);
                    selectedDateTo = new Date(today);
                    break;
                case 'lastMonth':
                    const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);
                    const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                    selectedDateFrom = lastMonthStart;
                    selectedDateTo = lastMonthEnd;
                    break;
            }}
            
            renderCalendars();
            updateDateInputs();
        }}
        
        function updateDateInputs() {{
            if (selectedDateFrom) {{
                document.getElementById('dateFromFooter').value = formatDateDisplay(selectedDateFrom);
            }}
            if (selectedDateTo) {{
                document.getElementById('dateToFooter').value = formatDateDisplay(selectedDateTo);
            }}
        }}
        
        function updateQuickSelectActive() {{
            // Clear all active
            document.querySelectorAll('.quick-select-item').forEach(item => {{
                item.classList.remove('active');
            }});
            
            // Check if current selection matches any preset
            if (selectedDateFrom && selectedDateTo) {{
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                const from = new Date(selectedDateFrom);
                from.setHours(0, 0, 0, 0);
                const to = new Date(selectedDateTo);
                to.setHours(0, 0, 0, 0);
                
                // Check each preset
                if (from.getTime() === today.getTime() && to.getTime() === today.getTime()) {{
                    document.querySelector('[data-preset="today"]')?.classList.add('active');
                }} else if (to.getTime() === today.getTime() && (to - from) === 6 * 24 * 60 * 60 * 1000) {{
                    document.querySelector('[data-preset="last7days"]')?.classList.add('active');
                }}
                // Add more checks as needed
            }}
        }}
        
        function clearDate(type) {{
            if (type === 'from') {{
                selectedDateFrom = null;
            }} else {{
                selectedDateTo = null;
            }}
            updateDateInputs();
            renderCalendars();
        }}
        
        function applyDateRange() {{
            if (selectedDateFrom && selectedDateTo) {{
                currentFilters.dateRange = 'custom';
                currentFilters.dateFrom = formatDateForAPI(selectedDateFrom);
                currentFilters.dateTo = formatDateForAPI(selectedDateTo);
                
                // Update date range text
                const dateText = formatDateRangeText(selectedDateFrom, selectedDateTo);
                const dateTextElement = document.getElementById('dateRangeText');
                if (dateTextElement) {{
                    dateTextElement.textContent = dateText;
                }}
                
                saveFilters();
                loadData();
                
                // QUAN TRỌNG: Đóng date picker sau khi apply
                if (typeof window.closeDatePicker === 'function') {{
                    window.closeDatePicker();
                }}
            }}
        }}
        
        function formatDateRangeText(from, to) {{
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            const fromDate = new Date(from);
            fromDate.setHours(0, 0, 0, 0);
            const toDate = new Date(to);
            toDate.setHours(0, 0, 0, 0);
            
            // Check if it's today
            if (fromDate.getTime() === today.getTime() && toDate.getTime() === today.getTime()) {{
                return 'Hôm nay';
            }}
            
            // Format dates
            const fromStr = formatDateDisplay(fromDate);
            const toStr = formatDateDisplay(toDate);
            
            return `${{fromStr}} - ${{toStr}}`;
        }}
        
        function formatDateDisplay(date) {{
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${{day}}/${{month}}/${{year}}`;
        }}
        
        function formatDateForAPI(date) {{
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${{year}}-${{month}}-${{day}}`;
        }}
        
        // Load Preset
        function loadPreset() {{
            const preset = document.getElementById('presetSelect').value;
            if (!preset) return;
            
            if (preset === 'active') {{
                document.getElementById('statusFilter').value = 'ACTIVE';
            }} else if (preset === 'paused') {{
                document.getElementById('statusFilter').value = 'PAUSED';
            }} else if (preset === 'all') {{
                document.getElementById('statusFilter').value = '';
            }}
            
            updateFilters();
            document.getElementById('presetSelect').value = '';
        }}
        
        // Apply Suggestion
        function applySuggestion(suggestion) {{
            if (suggestion === 'active') {{
                document.getElementById('statusFilter').value = 'ACTIVE';
            }} else if (suggestion === 'paused') {{
                document.getElementById('statusFilter').value = 'PAUSED';
            }} else if (suggestion === 'today') {{
                const today = new Date();
                const todayStr = formatDateForAPI(today);
                document.getElementById('dateFrom').value = todayStr;
                document.getElementById('dateTo').value = todayStr;
                currentFilters.dateRange = 'custom';
                currentFilters.dateFrom = todayStr;
                currentFilters.dateTo = todayStr;
                document.getElementById('dateRangeText').textContent = 'Hôm nay';
            }} else if (suggestion === 'last7days') {{
                currentFilters.dateRange = 'last7days';
                document.getElementById('dateRangeText').textContent = '7 ngày qua';
            }}
            
            updateFilters();
        }}
        
        // Update filters
        function updateFilters() {{
            currentFilters.account = document.getElementById('accountFilter').value;
            currentFilters.prefix = document.getElementById('prefixFilter').value;
            const statusFilter = document.getElementById('statusFilter');
            if (statusFilter) {{
                currentFilters.status = statusFilter.value;
            }}
            
            // Update filter badge
            updateFilterBadge();
            
            // Update selected filters display
            updateSelectedFilters();
            
            saveFilters();
        }}
        
        function applyFilters() {{
            updateFilters();
            loadData();
            closeFilterPanel();
        }}
        
        function clearAllFilters() {{
            document.getElementById('accountFilter').value = '';
            document.getElementById('prefixFilter').value = '';
            if (document.getElementById('statusFilter')) {{
                document.getElementById('statusFilter').value = '';
            }}
            currentFilters.account = '';
            currentFilters.prefix = '';
            currentFilters.status = '';
            currentFilters.dateRange = 'today';
            document.getElementById('dateRangeText').textContent = 'Hôm nay';
            
            updateFilterBadge();
            updateSelectedFilters();
            saveFilters();
            loadData();
        }}
        
        function saveFilterPreset() {{
            // TODO: Implement save preset functionality
            alert('Chức năng lưu preset sẽ được thêm sau');
        }}
        
        function updateFilterBadge() {{
            const badge = document.getElementById('filterBadge');
            let count = 0;
            
            if (currentFilters.account) count++;
            if (currentFilters.prefix) count++;
            if (currentFilters.status) count++;
            if (currentFilters.dateRange && currentFilters.dateRange !== 'today') count++;
            
            if (count > 0) {{
                badge.textContent = count;
                badge.style.display = 'inline-block';
            }} else {{
                badge.style.display = 'none';
            }}
        }}
        
        function updateSelectedFilters() {{
            const container = document.getElementById('selectedFilters');
            const filters = [];
            
            if (currentFilters.account) {{
                const accountSelect = document.getElementById('accountFilter');
                const accountText = accountSelect.options[accountSelect.selectedIndex].text;
                filters.push({{key: 'account', label: `Tài khoản: ${{accountText}}`, value: currentFilters.account}});
            }}
            
            if (currentFilters.prefix) {{
                const prefixSelect = document.getElementById('prefixFilter');
                const prefixText = prefixSelect.options[prefixSelect.selectedIndex].text;
                filters.push({{key: 'prefix', label: `Prefix: ${{prefixText}}`, value: currentFilters.prefix}});
            }}
            
            if (currentFilters.status) {{
                const statusText = currentFilters.status === 'ACTIVE' ? 'Hoạt động' : 'Tạm dừng';
                filters.push({{key: 'status', label: `Trạng thái: ${{statusText}}`, value: currentFilters.status}});
            }}
            
            if (filters.length === 0) {{
                container.innerHTML = '<span style="color: #9ca3af; font-size: 13px;">Chưa có filter nào được chọn</span>';
            }} else {{
                container.innerHTML = filters.map(f => `
                    <div class="filter-tag">
                        <span>${{f.label}}</span>
                        <span class="filter-tag-remove" onclick="removeFilter('${{f.key}}')">✕</span>
                    </div>
                `).join('');
            }}
        }}
        
        function removeFilter(key) {{
            if (key === 'account') {{
                document.getElementById('accountFilter').value = '';
                currentFilters.account = '';
            }} else if (key === 'prefix') {{
                document.getElementById('prefixFilter').value = '';
                currentFilters.prefix = '';
            }} else if (key === 'status') {{
                document.getElementById('statusFilter').value = '';
                currentFilters.status = '';
            }}
            
            updateFilterBadge();
            updateSelectedFilters();
            saveFilters();
        }}
        
        // Refresh data
        function refreshData() {{
            const refreshBtn = document.getElementById('refreshBtn');
            refreshBtn.classList.add('loading');
            
            loadData().finally(() => {{
                refreshBtn.classList.remove('loading');
            }});
        }}
        
        // Load dashboard data
        async function loadData() {{
            if (isLoading) return;
            
            isLoading = true;
            
            try {{
                // Load overview cards from /dashboard/summary
                await loadOverviewCards();
                
                // Load table data from /dashboard/details
                await loadTableData();
                
            }} catch (error) {{
                console.error('Error loading data:', error);
                showError('Lỗi tải dữ liệu: ' + error.message);
            }} finally {{
                isLoading = false;
            }}
        }}
        
        // Load overview cards
        async function loadOverviewCards() {{
            try {{
                const params = buildSummaryParams();
                const response = await fetch(`/dashboard/summary?${{params}}`, {{
                    headers: {{
                        'Authorization': 'Bearer ' + getAuthToken()
                    }}
                }});
                
                if (!response.ok) {{
                    throw new Error('Failed to load overview');
                }}
                
                const overview = await response.json();
                updateOverviewCards(overview);
                
            }} catch (error) {{
                console.error('Error loading overview:', error);
                updateOverviewCards({{}});
            }}
        }}
        
        // Load table data
        async function loadTableData() {{
            try {{
                const params = buildDetailsParams();
                const response = await fetch(`/dashboard/details?${{params}}`, {{
                    headers: {{
                        'Authorization': 'Bearer ' + getAuthToken()
                    }}
                }});
                
                if (!response.ok) {{
                    throw new Error('Failed to load table data');
                }}
                
                const data = await response.json();
                console.log('📊 Table data received:', data); // Debug log
                updateTable(data.data || [], data.total || 0);
                
            }} catch (error) {{
                console.error('Error loading table data:', error);
                updateTable([], 0);
            }}
        }}
        
        // Build API parameters for summary
        function buildSummaryParams() {{
            const params = new URLSearchParams({{
                view_mode: currentViewMode
            }});
            
            // Add filters
            if (currentFilters.account) params.append('account_id', currentFilters.account);
            if (currentFilters.prefix) params.append('prefix', currentFilters.prefix);
            
            // Date range
            const dateRange = getDateRange();
            if (dateRange.from) params.append('date_from', dateRange.from);
            if (dateRange.to) params.append('date_to', dateRange.to);
            
            return params.toString();
        }}
        
        // Build API parameters for details
        function buildDetailsParams() {{
            const params = new URLSearchParams({{
                view_mode: currentViewMode,
                level: currentLevel || 'adset',
                page: currentPage || 1,
                pageSize: pageSize || 50
            }});
            
            // Add filters
            if (currentFilters.account) params.append('account_id', currentFilters.account);
            if (currentFilters.prefix) params.append('prefix', currentFilters.prefix);
            if (currentFilters.status) params.append('status', currentFilters.status);
            if (currentFilters.search) params.append('search', currentFilters.search);
            
            // Date range
            const dateRange = getDateRange();
            if (dateRange.from) params.append('date_from', dateRange.from);
            if (dateRange.to) params.append('date_to', dateRange.to);
            
            return params.toString();
        }}
        
        // Get date range from filter
        // Tính toán date dựa trên timezone UTC+7 (Asia/Ho_Chi_Minh) để đồng bộ với server
        function getDateRange() {{
            const range = currentFilters.dateRange || 'today';
            
            // Lấy ngày hôm nay theo timezone UTC+7
            const now = new Date();
            const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
            const hcmTime = new Date(utc + (7 * 3600000)); // UTC+7
            const today = new Date(hcmTime);
            today.setHours(23, 59, 59, 999);
            
            let from, to;
            
            if (range === 'today') {{
                from = new Date(hcmTime);
                from.setHours(0, 0, 0, 0);
                to = new Date(hcmTime);
                to.setHours(23, 59, 59, 999);
            }} else if (range === 'yesterday') {{
                from = new Date(hcmTime);
                from.setDate(from.getDate() - 1);
                from.setHours(0, 0, 0, 0);
                to = new Date(hcmTime);
                to.setDate(to.getDate() - 1);
                to.setHours(23, 59, 59, 999);
            }} else if (range === 'last7days') {{
                from = new Date(hcmTime);
                from.setDate(from.getDate() - 6);
                from.setHours(0, 0, 0, 0);
                to = new Date(hcmTime);
                to.setHours(23, 59, 59, 999);
            }} else if (range === 'last30days') {{
                from = new Date(hcmTime);
                from.setDate(from.getDate() - 29);
                from.setHours(0, 0, 0, 0);
                to = new Date(hcmTime);
                to.setHours(23, 59, 59, 999);
            }} else {{
                // Custom range - use saved dates or default to today
                if (currentFilters.dateFrom && currentFilters.dateTo) {{
                    from = new Date(currentFilters.dateFrom + 'T00:00:00+07:00');
                    to = new Date(currentFilters.dateTo + 'T23:59:59+07:00');
                }} else {{
                    from = new Date(hcmTime);
                    from.setHours(0, 0, 0, 0);
                    to = new Date(hcmTime);
                    to.setHours(23, 59, 59, 999);
                }}
            }}
            
            return {{
                from: formatDateForAPI(from),
                to: formatDateForAPI(to)
            }};
        }}
        
        // Format date for API (YYYY-MM-DD)
        function formatDateForAPI(date) {{
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${{year}}-${{month}}-${{day}}`;
        }}
        
        // Update overview cards based on view mode
        function updateOverviewCards(overview) {{
            const grid = document.getElementById('overviewGrid');
            
            if (currentViewMode === 'ecommerce') {{
                grid.innerHTML = `
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Tổng Chi Tiêu</div>
                            <div class="card-icon spend">💰</div>
                        </div>
                        <div class="card-value" id="totalSpend">${{formatCurrency(overview.totalSpend || 0)}}</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">% ADS</div>
                            <div class="card-icon ads">📈</div>
                        </div>
                        <div class="card-value" id="adsPercent">${{formatPercentage(overview.adsPercent || 0)}}%</div>
                        <div class="card-subtitle">Chi tiêu / Giá trị chuyển đổi</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Giá Trị Chuyển Đổi</div>
                            <div class="card-icon purchase">🛒</div>
                        </div>
                        <div class="card-value" id="purchaseValue">${{formatCurrency(overview.purchaseValue || 0)}}</div>
                        <div class="card-subtitle">Tổng từ lượt mua</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Adsets Hoạt Động</div>
                            <div class="card-icon adsets">▶️</div>
                        </div>
                        <div class="card-value" id="activeAdsets">${{formatNumber(overview.activeAdsets || 0)}}</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Adsets Đã Tạm Dừng</div>
                            <div class="card-icon adsets">⏸️</div>
                        </div>
                        <div class="card-value" id="pausedAdsets">${{formatNumber(overview.pausedAdsets || 0)}}</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Tổng Adsets</div>
                            <div class="card-icon adsets">📊</div>
                        </div>
                        <div class="card-value" id="totalAdsets">${{formatNumber(overview.totalAdsets || 0)}}</div>
                    </div>
                `;
            }} else {{
                // Lead Generation view
                grid.innerHTML = `
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Tổng Chi Tiêu</div>
                            <div class="card-icon spend">💰</div>
                        </div>
                        <div class="card-value" id="totalSpend">${{formatCurrency(overview.totalSpend || 0)}}</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Tổng Lead</div>
                            <div class="card-icon leads">📋</div>
                        </div>
                        <div class="card-value" id="totalLeads">${{formatNumber(overview.totalLeads || 0)}}</div>
                        <div class="card-subtitle">Bình luận + Tin nhắn</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Giá Data TB</div>
                            <div class="card-icon gia">🎯</div>
                        </div>
                        <div class="card-value" id="avgGiaData">${{formatCurrency(overview.avgGiaData || 0)}}</div>
                        <div class="card-subtitle">Chi phí trên mỗi lượt bắt đầu thanh toán</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Adsets Hoạt Động</div>
                            <div class="card-icon adsets">▶️</div>
                        </div>
                        <div class="card-value" id="activeAdsets">${{formatNumber(overview.activeAdsets || 0)}}</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Adsets Đã Tạm Dừng</div>
                            <div class="card-icon adsets">⏸️</div>
                        </div>
                        <div class="card-value" id="pausedAdsets">${{formatNumber(overview.pausedAdsets || 0)}}</div>
                    </div>
                    
                    <div class="overview-card">
                        <div class="card-header">
                            <div class="card-title">Tổng Adsets</div>
                            <div class="card-icon adsets">📊</div>
                        </div>
                        <div class="card-value" id="totalAdsets">${{formatNumber(overview.totalAdsets || 0)}}</div>
                    </div>
                `;
            }}
        }}
        
        // Update data table
        function updateTable(rows, total) {{
            const tableHead = document.getElementById('tableHead');
            const tableBody = document.getElementById('tableBody');
            
            // Define headers based on view mode
            let headers;
            if (currentViewMode === 'ecommerce') {{
                headers = [
                    'Chọn', 'Bật/Tắt', 'Tên', 'Phân Phối', 'Ngân Sách', 'Chi Tiêu', '% ADS', 
                    'Kết Quả', 'Giá DATA', 'TLC', 'Bắt Đầu TT', 'Lượt Mua', 'Giá Trị CV',
                    'CPM', 'Hiển Thị', 'Tiếp Cận', 'Tần Suất', 'Nhấp', 'CTR', 'CPC'
                ];
            }} else {{
                headers = [
                    'Chọn', 'Bật/Tắt', 'Tên', 'Phân Phối', 'Ngân Sách', 'Chi Tiêu',
                    'Kết Quả', 'Giá DATA', 'Chi Phí/Bắt Đầu TT', 'Bắt Đầu TT', 'Lượt Mua',
                    'CPM', 'Hiển Thị', 'Tiếp Cận', 'Tần Suất', 'Nhấp', 'CTR', 'CPC'
                ];
            }}
            
            // Update table headers
            tableHead.innerHTML = `
                <tr>
                    ${{headers.map(header => `<th>${{header}}</th>`).join('')}}
                </tr>
            `;
            
            // Update table body
            if (rows.length === 0) {{
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="${{headers.length}}" class="empty-state">
                            <div class="empty-icon">📊</div>
                            <div>Không có dữ liệu</div>
                            <div style="font-size: 12px; margin-top: 8px;">Thử điều chỉnh bộ lọc hoặc khoảng thời gian</div>
                        </td>
                    </tr>
                `;
                return;
            }}
            
            tableBody.innerHTML = rows.map(row => {{
                const isSelected = selectedItems.has(row.id);
                const status = (row.status || 'UNKNOWN').toUpperCase();
                const statusClass = status === 'ACTIVE' ? 'active' : (status === 'PAUSED' ? 'paused' : 'error');
                
                if (currentViewMode === 'ecommerce') {{
                    return `
                        <tr>
                            <td><div class="checkbox ${{isSelected ? 'checked' : ''}}" onclick="toggleSelection('${{row.id}}')"></div></td>
                            <td><button class="toggle-btn ${{statusClass}}" onclick="toggleStatus('${{row.id}}', '${{status}}')"></button></td>
                            <td>
                                <div class="font-semibold">${{row.name || '-'}}</div>
                                <div class="text-gray" style="font-size: 12px;">ID: ${{row.id}}</div>
                            </td>
                            <td><span class="status-dot ${{statusClass}}"></span></td>
                            <td class="text-right">${{formatCurrency(0)}}</td>
                            <td class="text-right font-semibold">${{formatCurrency(row.spend || 0)}}</td>
                            <td class="text-right">${{formatPercentage(row.ads_percent || 0)}}%</td>
                            <td class="text-right">${{formatNumber(row.results || 0)}}</td>
                            <td class="text-right">${{formatCurrency(row.gia_data || 0)}}</td>
                            <td class="text-right">${{formatPercentage(row.tlc || 0)}}%</td>
                            <td class="text-right">${{formatNumber(row.checkout_starts || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.purchases || 0)}}</td>
                            <td class="text-right">${{formatCurrency(row.purchase_value || 0)}}</td>
                            <td class="text-right">${{formatCurrency(row.cpm || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.impressions || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.reach || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.frequency || 0, 2)}}</td>
                            <td class="text-right">${{formatNumber(row.clicks || 0)}}</td>
                            <td class="text-right">${{formatPercentage(row.ctr || 0)}}%</td>
                            <td class="text-right">${{formatCurrency(row.cpc || 0)}}</td>
                        </tr>
                    `;
                }} else {{
                    return `
                        <tr>
                            <td><div class="checkbox ${{isSelected ? 'checked' : ''}}" onclick="toggleSelection('${{row.id}}')"></div></td>
                            <td><button class="toggle-btn ${{statusClass}}" onclick="toggleStatus('${{row.id}}', '${{status}}')"></button></td>
                            <td>
                                <div class="font-semibold">${{row.name || '-'}}</div>
                                <div class="text-gray" style="font-size: 12px;">ID: ${{row.id}}</div>
                            </td>
                            <td><span class="status-dot ${{statusClass}}"></span></td>
                            <td class="text-right">${{formatCurrency(0)}}</td>
                            <td class="text-right font-semibold">${{formatCurrency(row.spend || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.results || 0)}}</td>
                            <td class="text-right">${{formatCurrency(row.gia_data || 0)}}</td>
                            <td class="text-right">${{formatCurrency(row.cost_per_checkout_start || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.checkout_starts || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.purchases || 0)}}</td>
                            <td class="text-right">${{formatCurrency(row.cpm || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.impressions || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.reach || 0)}}</td>
                            <td class="text-right">${{formatNumber(row.frequency || 0, 2)}}</td>
                            <td class="text-right">${{formatNumber(row.clicks || 0)}}</td>
                            <td class="text-right">${{formatPercentage(row.ctr || 0)}}%</td>
                            <td class="text-right">${{formatCurrency(row.cpc || 0)}}</td>
                        </tr>
                    `;
                }}
            }}).join('');
            
            updateBulkActions();
        }}
        
        // Selection functions
        function toggleSelection(id) {{
            if (selectedItems.has(id)) {{
                selectedItems.delete(id);
            }} else {{
                selectedItems.add(id);
            }}
            
            // Update checkbox visual state
            const checkbox = event.target;
            checkbox.classList.toggle('checked');
            
            updateBulkActions();
        }}
        
        function updateBulkActions() {{
            const bulkActions = document.getElementById('bulkActions');
            const selectedCount = document.getElementById('selectedCount');
            
            const count = selectedItems.size;
            selectedCount.textContent = `${{count}} đã chọn`;
            
            if (count > 0) {{
                bulkActions.classList.add('visible');
            }} else {{
                bulkActions.classList.remove('visible');
            }}
        }}
        
        // Action functions
        async function toggleStatus(id, currentStatus) {{
            const action = currentStatus === 'ACTIVE' ? 'pause' : 'activate';
            
            try {{
                const response = await fetch(`/dashboard/action/${{action}}/${{id}}`, {{
                    method: 'POST',
                    headers: {{
                        'Authorization': 'Bearer ' + getAuthToken(),
                        'Content-Type': 'application/json'
                    }}
                }});
                
                if (response.ok) {{
                    showSuccess(`Đã ${{action === 'pause' ? 'tắt' : 'bật'}} thành công`);
                    loadData(); // Refresh data
                }} else {{
                    throw new Error(`Failed to ${{action}} item`);
                }}
            }} catch (error) {{
                showError('Lỗi: ' + error.message);
            }}
        }}
        
        async function bulkAction(action) {{
            if (selectedItems.size === 0) return;
            
            const items = Array.from(selectedItems);
            const actionText = action === 'pause' ? 'tắt' : 'bật';
            
            if (!confirm(`Bạn có chắc muốn ${{actionText}} ${{items.length}} mục đã chọn?`)) {{
                return;
            }}
            
            try {{
                const promises = items.map(id => 
                    fetch(`/dashboard/action/${{action}}/${{id}}`, {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + getAuthToken(),
                            'Content-Type': 'application/json'
                        }}
                    }})
                );
                
                await Promise.all(promises);
                
                showSuccess(`Đã ${{actionText}} ${{items.length}} mục thành công`);
                selectedItems.clear();
                loadData(); // Refresh data
                
            }} catch (error) {{
                showError('Lỗi bulk action: ' + error.message);
            }}
        }}
        
        // Utility functions
        function formatCurrency(value) {{
            if (!value) return '0đ';
            return new Intl.NumberFormat('vi-VN', {{
                style: 'currency',
                currency: 'VND',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }}).format(value);
        }}
        
        function formatNumber(value, decimals = 0) {{
            if (!value) return '0';
            return new Intl.NumberFormat('vi-VN', {{
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            }}).format(value);
        }}
        
        function formatPercentage(value) {{
            return (value || 0).toFixed(2);
        }}
        
        function showSuccess(message) {{
            // Simple alert for now - can be improved with toast notifications
            console.log('Success:', message);
            // alert(message);
        }}
        
        function showError(message) {{
            console.error('Error:', message);
            alert(message);
        }}
    </script>
</body>
</html>
"""
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error in dashboard page: {e}")
        return HTMLResponse(content=f"<div>Error: {str(e)}</div>", status_code=500)


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
    """Get dashboard data based on view mode and filters"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get user's accounts and prefixes
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db)
        
        if not user_account_ids and not user_prefixes:
            return JSONResponse({
                "overview": {},
                "ads": [],
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
            # Default to last 7 days
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Build query - AdMetrics uses 'date' field, not 'date_start'/'date_stop'
        query = db.query(AdMetrics).filter(
            func.date(AdMetrics.date) >= start_date.date(),
            func.date(AdMetrics.date) <= end_date.date()
        )
        
        # Filter by user's accounts and prefixes
        account_prefix_filter = []
        if user_account_ids:
            account_prefix_filter.append(AdMetrics.account_id.in_(user_account_ids))
        if user_prefixes:
            # Filter by prefix in ad name
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
                "overview": {},
                "ads": [],
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
                    'budget': 0,
                    'spend': 0,
                    'impressions': 0,
                    'clicks': 0,
                    'reach': 0,
                    'results': 0,
                    'link_clicks': 0,
                    'post_engagement': 0,
                    'video_views': 0,
                    'checkout_started': 0,
                    'purchases': 0,
                    'purchase_value': 0,
                    'leads': 0,
                    'comments': 0,
                    'messages': 0
                }
            
            # Aggregate metrics
            data = adset_data[adset_id]
            data['spend'] += float(metric.spend or 0)
            data['impressions'] += int(metric.impressions or 0)
            data['clicks'] += int(metric.clicks or 0)
            data['reach'] += int(metric.reach or 0)
            
            # Add action metrics
            if hasattr(metric, 'post_engagements'):
                data['post_engagement'] += int(metric.post_engagements or 0)
            if hasattr(metric, 'video_p25_watched_actions'):
                data['video_views'] += int(metric.video_p25_watched_actions or 0)
            
            # Purchase/conversion metrics
            if hasattr(metric, 'offsite_conversion_fb_pixel_initiate_checkout'):
                data['checkout_started'] += int(metric.offsite_conversion_fb_pixel_initiate_checkout or 0)
            if hasattr(metric, 'offsite_conversion_fb_pixel_purchase'):
                data['purchases'] += int(metric.offsite_conversion_fb_pixel_purchase or 0)
            if hasattr(metric, 'offsite_conversion_fb_pixel_purchase_value'):
                data['purchase_value'] += float(metric.offsite_conversion_fb_pixel_purchase_value or 0)
            
            # Lead metrics
            if hasattr(metric, 'onsite_conversion_messaging_conversation_started_7d'):
                data['messages'] += int(metric.onsite_conversion_messaging_conversation_started_7d or 0)
            if hasattr(metric, 'post_comments'):
                data['comments'] += int(metric.post_comments or 0)
        
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
        
        # Calculate overview metrics
        total_spend = sum(ad['spend'] for ad in processed_ads)
        total_impressions = sum(ad['impressions'] for ad in processed_ads)
        total_purchases = sum(ad['purchases'] for ad in processed_ads)
        total_purchase_value = sum(ad['purchase_value'] for ad in processed_ads)
        total_leads = sum(ad.get('leads', 0) for ad in processed_ads)
        
        active_adsets = len([ad for ad in processed_ads if ad['status'] == 'ACTIVE'])
        paused_adsets = len([ad for ad in processed_ads if ad['status'] in ['PAUSED', 'ARCHIVED']])
        total_adsets = len(processed_ads)
        
        if view_mode == "ecommerce":
            overview = {
                'totalSpend': total_spend,
                'adsPercent': (total_spend / total_purchase_value * 100) if total_purchase_value > 0 else 0,
                'purchaseValue': total_purchase_value,
                'activeAdsets': active_adsets,
                'pausedAdsets': paused_adsets,
                'totalAdsets': total_adsets
            }
        else:
            overview = {
                'totalSpend': total_spend,
                'totalLeads': total_leads,
                'avgGiaData': total_spend / total_leads if total_leads > 0 else 0,
                'activeAdsets': active_adsets,
                'pausedAdsets': paused_adsets,
                'totalAdsets': total_adsets
            }
        
        # Sort ads by spend (descending)
        processed_ads.sort(key=lambda x: x['spend'], reverse=True)
        
        return JSONResponse({
            "overview": overview,
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


@router.post("/action/{action}/{item_id}")
async def dashboard_action(
    request: Request,
    action: str,
    item_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Perform action on campaign/adset/ad (activate/pause)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if action not in ["activate", "pause"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    try:
        # Get user's Facebook access token
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(status_code=400, detail="Facebook access token not found. Please configure in Settings.")
        
        # Determine item type by checking if it's campaign, adset, or ad
        # For now, assume it's an adset (most common case)
        # TODO: Add logic to detect item type (campaign ID vs adset ID vs ad ID format)
        
        # Get user's enabled accounts to verify access
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db, enabled_only=True)
        
        # Verify user has access (check in recent data or make API call)
        # For simplicity, we'll just call the API - if it fails, user doesn't have access
        
        # Call Facebook API to perform action
        # For adset/ad: use pause_adsets/resume_adsets
        # For campaign: need to detect and handle differently (TODO: add campaign pause/resume)
        if action == "pause":
            result = pause_adsets([item_id], access_token, delay_ms=0)
            if result.get("success", 0) > 0:
                new_status = "PAUSED"
            else:
                error_details = result.get('errorDetails', [])
                error_msg = error_details[0].get('error', 'Unknown error') if error_details else 'Unknown error'
                raise HTTPException(status_code=400, detail=f"Failed to pause: {error_msg}")
        else:  # activate
            result = resume_adsets([item_id], access_token, delay_ms=0)
            if result.get("success", 0) > 0:
                new_status = "ACTIVE"
            else:
                error_details = result.get('errorDetails', [])
                error_msg = error_details[0].get('error', 'Unknown error') if error_details else 'Unknown error'
                raise HTTPException(status_code=400, detail=f"Failed to activate: {error_msg}")
        
        logger.info(f"Action {action} performed on {item_id} by user {current_user.id} - Status: {new_status}")
        
        return JSONResponse({
            "success": True,
            "action": action,
            "item_id": item_id,
            "new_status": new_status,
            "message": f"Item {action}d successfully"
        })
        
    except Exception as e:
        logger.error(f"Error performing action {action} on {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error performing action: {str(e)}")


@router.get("/health")
async def dashboard_health():
    """Health check endpoint for dashboard"""
    return JSONResponse({
        "status": "healthy",
        "service": "dashboard",
        "timestamp": datetime.now(HCM_TZ).isoformat()
    })


@router.get("/summary")
async def get_dashboard_summary(
    request: Request,
    view_mode: str = Query("ecommerce", description="View mode: ecommerce or lead"),
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get Overview Cards summary - Gọi trực tiếp từ Facebook API"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get user's enabled accounts and prefixes
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db, enabled_only=True)
        
        if not user_account_ids:
            # Return empty summary if no accounts
            if view_mode == "ecommerce":
                return JSONResponse({
                    "totalSpend": 0,
                    "adsPercent": 0,
                    "purchaseValue": 0,
                    "activeAdsets": 0,
                    "pausedAdsets": 0,
                    "totalAdsets": 0
                })
            else:  # lead
                return JSONResponse({
                    "totalSpend": 0,
                    "totalLeads": 0,
                    "avgGiaData": 0,
                    "activeAdsets": 0,
                    "pausedAdsets": 0,
                    "totalAdsets": 0
                })
        
        # Get access token
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(status_code=400, detail="Facebook access token not found. Please configure in Settings.")
        
        # Filter accounts nếu có account_id filter
        if account_id:
            if account_id not in user_account_ids:
                raise HTTPException(status_code=403, detail="Access denied to this account")
            user_account_ids = [account_id]
        
        # Gọi Facebook API trực tiếp (async với cache)
        logger.info(f"📥 Đang lấy dữ liệu từ Facebook API cho {len(user_account_ids)} tài khoản...")
        all_data = await pull_facebook_data_with_date_range_async(
            access_token,
            user_account_ids,
            date_from=date_from,
            date_to=date_to,
            max_results=5000,  # Giới hạn để tránh quá tải
            use_cache=True  # Dùng cache để tránh gọi 2 lần
        )
        
        # Filter theo prefix nếu có
        if prefix and all_data:
            all_data = [row for row in all_data if row.get('prefix') == prefix]
        
        # Filter theo view mode (campaign type)
        # Note: detect_campaign_type returns 'LEAD' not 'LEAD_GENERATION'
        if view_mode == "ecommerce":
            all_data = [row for row in all_data if row.get('campaign_type') == 'ECOMMERCE']
        elif view_mode == "lead":
            all_data = [row for row in all_data if row.get('campaign_type') == 'LEAD']
        
        # Lấy status của adsets từ Facebook API
        adset_ids = list(set([row.get('adset_id') for row in all_data if row.get('adset_id')]))
        if adset_ids:
            logger.info(f"📊 Đang lấy status cho {len(adset_ids)} adsets...")
            adset_statuses_map = fetch_adset_statuses(adset_ids, access_token)
            # Update status trong data
            for row in all_data:
                adset_id = row.get('adset_id')
                if adset_id and adset_id in adset_statuses_map:
                    row['adset_status'] = adset_statuses_map[adset_id]
                    row['effective_status'] = adset_statuses_map[adset_id]
        
        # Aggregate metrics
        total_spend = sum(float(row.get('spend', 0) or 0) for row in all_data)
        total_purchases = sum(int(row.get('purchases', 0) or 0) for row in all_data)
        total_purchase_value = sum(float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0) for row in all_data)
        
        # Calculate leads (comments + messages)
        total_leads = sum(
            int(row.get('post_comments', 0) or 0) + int(row.get('messaging_conversations_started', 0) or 0)
            for row in all_data
        )
        
        # Count unique adsets by status
        adset_statuses = {}
        for row in all_data:
            adset_id = row.get('adset_id')
            if adset_id:
                status = (row.get('adset_status') or 'UNKNOWN').upper()
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading summary: {str(e)}")


@router.get("/details")
async def get_dashboard_details(
    request: Request,
    view_mode: str = Query("ecommerce", description="View mode: ecommerce or lead"),
    level: str = Query("adset", description="Level: campaign, adset, or ad"),
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID (for drill-down)"),
    adset_id: Optional[str] = Query(None, description="Filter by adset ID (for drill-down)"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=10, le=500),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get detailed table data for Campaign/Adset/Ad - Gọi trực tiếp từ Facebook API"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get user's enabled accounts and prefixes
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db, enabled_only=True)
        
        if not user_account_ids:
            return JSONResponse({
                "data": [],
                "total": 0,
                "page": page,
                "pageSize": pageSize
            })
        
        # Get access token
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(status_code=400, detail="Facebook access token not found. Please configure in Settings.")
        
        # Filter accounts nếu có account_id filter
        if account_id:
            if account_id not in user_account_ids:
                raise HTTPException(status_code=403, detail="Access denied to this account")
            user_account_ids = [account_id]
        
        # Gọi Facebook API trực tiếp (async với cache)
        logger.info(f"📥 Đang lấy dữ liệu chi tiết từ Facebook API cho {len(user_account_ids)} tài khoản...")
        logger.info(f"   Filters: view_mode={view_mode}, level={level}, account_id={account_id}, prefix={prefix}, status={status}, date_from={date_from}, date_to={date_to}, search={search}, campaign_id={campaign_id}, adset_id={adset_id}")
        all_data = await pull_facebook_data_with_date_range_async(
            access_token,
            user_account_ids,
            date_from=date_from,
            date_to=date_to,
            max_results=10000,  # Giới hạn để tránh quá tải
            use_cache=True  # Dùng cache để tránh gọi 2 lần (summary và details dùng chung cache)
        )
        logger.info(f"   ✅ Đã lấy được {len(all_data)} rows từ Facebook API")
        
        # Filter by prefix nếu có
        if prefix and all_data:
            all_data = [row for row in all_data if row.get('prefix') == prefix]
        
        # Filter by view mode (campaign type)
        # Note: detect_campaign_type_from_objective returns 'LEAD' not 'LEAD_GENERATION'
        before_view_filter = len(all_data)
        if view_mode == "ecommerce":
            all_data = [row for row in all_data if row.get('campaign_type') == 'ECOMMERCE']
        elif view_mode == "lead":
            all_data = [row for row in all_data if row.get('campaign_type') == 'LEAD']
        logger.info(f"   📊 Sau filter view_mode ({view_mode}): {len(all_data)}/{before_view_filter} rows")
        
        # Lấy status của adsets từ Facebook API (chỉ khi cần thiết)
        adset_ids = list(set([row.get('adset_id') for row in all_data if row.get('adset_id')]))
        if adset_ids:
            logger.info(f"📊 Đang lấy status cho {len(adset_ids)} adsets...")
            adset_statuses_map = fetch_adset_statuses(adset_ids, access_token)
            # Update status trong data
            for row in all_data:
                adset_id = row.get('adset_id')
                if adset_id and adset_id in adset_statuses_map:
                    row['adset_status'] = adset_statuses_map[adset_id]
                    row['effective_status'] = adset_statuses_map[adset_id]
        
        # Drill-down filter: Filter by campaign_id or adset_id
        # CHỈ filter nếu param thực sự được truyền (không phải None hoặc "None")
        if campaign_id and campaign_id != "None" and all_data:
            all_data = [row for row in all_data if row.get('campaign_id') == campaign_id]
            logger.info(f"   📊 Sau filter campaign_id ({campaign_id}): {len(all_data)} rows")
        
        if adset_id and adset_id != "None" and all_data:
            all_data = [row for row in all_data if row.get('adset_id') == adset_id]
            logger.info(f"   📊 Sau filter adset_id ({adset_id}): {len(all_data)} rows")
        
        # Status filter
        if status and all_data:
            all_data = [row for row in all_data if (row.get('adset_status') or 'UNKNOWN').upper() == status.upper()]
        
        # Search filter - search by name or ID
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
        
        # Group by level và aggregate
        grouped_data = {}
        
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
            
            # Initialize group if not exists
            if entity_key not in grouped_data:
                grouped_data[entity_key] = {
                    'id': entity_id,
                    'name': entity_name,
                    'account_id': row.get('account_id', ''),
                    'prefix': row.get('prefix', ''),
                    'status': (row.get('adset_status') or 'UNKNOWN').upper(),
                    'spend': 0,
                    'impressions': 0,
                    'clicks': 0,
                    'reach': 0,
                    'post_comments': 0,
                    'messaging_conversations_started': 0,
                    'purchases': 0,
                    'gia_tri_chuyen_doi_tu_luot_mua': 0,
                    'checkout_initiated': 0,
                    'campaign_id': row.get('campaign_id', ''),
                    'campaign_name': row.get('campaign_name', ''),
                    'adset_id': row.get('adset_id', ''),
                    'adset_name': row.get('adset_name', ''),
                }
            
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
            
            # Update status if available
            if row.get('adset_status'):
                group['status'] = row.get('adset_status').upper()
        
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
            
            # Calculate results (comments + messages)
            results = post_comments + messages
            
            # Calculate derived metrics
            gia_data = (spend / results) if results > 0 else 0
            cpm = (spend / impressions * 1000) if impressions > 0 else 0
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            cpc = (spend / clicks) if clicks > 0 else 0
            frequency = (impressions / reach) if reach > 0 else 0
            
            row_data = {
                "id": group['id'],
                "name": group['name'] or "-",
                "account_id": group['account_id'],
                "prefix": group['prefix'] or "-",
                "status": group['status'],
                "spend": round(spend, 2),
                "results": results,
                "gia_data": round(gia_data, 2),
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpm": round(cpm, 2),
                "reach": reach,
                "frequency": round(frequency, 2),
            }
            
            if level == "adset" or level == "ad":
                row_data["campaign_id"] = group['campaign_id']
                row_data["campaign_name"] = group['campaign_name'] or "-"
            
            if level == "ad":
                row_data["adset_id"] = group['adset_id']
                row_data["adset_name"] = group['adset_name'] or "-"
            
            if view_mode == "ecommerce":
                ads_percent = (spend / purchase_value * 100) if purchase_value > 0 else 0
                tlc = (purchases / results) if results > 0 else 0
                row_data.update({
                    "ads_percent": round(ads_percent, 2),
                    "tlc": round(tlc, 2),
                    "checkout_starts": checkout_starts,
                    "purchases": purchases,
                    "purchase_value": round(purchase_value, 2)
                })
            else:  # lead
                cost_per_checkout_start = (spend / checkout_starts) if checkout_starts > 0 else 0
                row_data.update({
                    "leads": results,
                    "cost_per_checkout_start": round(cost_per_checkout_start, 2),
                    "checkout_starts": checkout_starts,
                    "purchases": purchases
                })
            
            rows.append(row_data)
        
        # Get total count
        total = len(rows)
        
        # Apply pagination
        offset = (page - 1) * pageSize
        paginated_rows = rows[offset:offset + pageSize]
        
        logger.info(f"   ✅ Trả về {len(paginated_rows)} rows (page {page}/{((total-1)//pageSize)+1}, total: {total})")
        
        return JSONResponse({
            "data": paginated_rows,
            "total": total,
            "page": page,
            "pageSize": pageSize
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading details: {str(e)}")