"""
Modern Facebook Ads Dashboard - Completely redesigned
Đồng bộ với style hiện tại, tích hợp sâu với Settings
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

# Timezone Hồ Chí Minh
HCM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')


def get_user_account_prefixes(user_id: int, db: Session, enabled_only: bool = True) -> tuple[List[str], List[str]]:
    """Lấy danh sách account_ids và prefixes của user (chỉ lấy enabled nếu enabled_only=True)"""
    query = db.query(Account.account_id).filter(Account.user_id == user_id)
    if enabled_only:
        query = query.filter(Account.enabled == True)
    user_accounts = query.all()
    account_ids = [acc[0] for acc in user_accounts]
    
    # Lấy prefixes từ user's prefixes
    user_prefixes = db.query(Prefix.prefix).filter(Prefix.user_id == user_id).all()
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
        
        # Lấy prefixes từ settings  
        user_prefixes = db.query(Prefix).filter(
            Prefix.user_id == current_user.id
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
            Prefix.user_id == current_user.id
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
            max-width: 1400px;
            margin: 0 auto;
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
            animation: spin 1s linear infinite;
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
        
        /* Date Picker Modal */
        .date-picker-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
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
            max-width: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            z-index: 1001;
        }}
        
        .date-picker-modal.open {{
            display: block;
        }}
        
        .date-picker-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .date-picker-content {{
            padding: 24px;
        }}
        
        .date-inputs {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        
        .date-inputs label {{
            display: block;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
            color: #374151;
        }}
        
        .date-input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
        }}
        
        .date-picker-footer {{
            margin-top: 20px;
            display: flex;
            justify-content: flex-end;
        }}
        
        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        /* Overview Cards */
        .overview-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
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
            width: 250px;
        }}
        
        .search-icon {{
            position: absolute;
            left: 12px;
            color: #9ca3af;
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
            
            .search-input {{
                width: 200px;
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
                {get_user_dropdown_menu(current_user)}
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
        <div class="filter-panel" id="filterPanel">
            <div class="filter-panel-header">
                <h3>Filters</h3>
                <button class="close-btn" onclick="closeFilterPanel()">✕</button>
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
        
        <!-- Date Picker Modal -->
        <div class="date-picker-overlay" id="datePickerOverlay" onclick="closeDatePicker()"></div>
        <div class="date-picker-modal" id="datePickerModal">
            <div class="date-picker-header">
                <h3>Chọn khoảng thời gian</h3>
                <button class="close-btn" onclick="closeDatePicker()">✕</button>
            </div>
            <div class="date-picker-content">
                <div class="date-inputs">
                    <div>
                        <label>Từ ngày:</label>
                        <input type="date" id="dateFrom" class="date-input">
                    </div>
                    <div>
                        <label>Đến ngày:</label>
                        <input type="date" id="dateTo" class="date-input">
                    </div>
                </div>
                <div class="date-picker-footer">
                    <button class="btn-apply" onclick="applyDateRange()">Áp dụng</button>
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
                    
                    <!-- Search -->
                    <div class="search-box">
                        <div class="search-icon">🔍</div>
                        <input type="text" class="search-input" id="searchInput" placeholder="Tìm kiếm...">
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
            dateRange: 'last7days',
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
            let searchTimeout;
            searchInput.addEventListener('input', function() {{
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {{
                    currentFilters.search = this.value;
                    saveFilters();
                    loadData();
                }}, 500);
            }});
            
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
                    dateRange: filters.dateRange || 'last7days',
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
                    document.getElementById('searchInput').value = currentFilters.search;
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
                        document.getElementById('dateRangeText').textContent = rangeTexts[currentFilters.dateRange] || '7 ngày qua';
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
                const response = await fetch('/dashboard/filters', {{
                    headers: {{
                        'Authorization': 'Bearer ' + getAuthToken()
                    }}
                }});
                
                if (response.ok) {{
                    settingsData = await response.json();
                    populateFilterDropdowns();
                }}
            }} catch (error) {{
                console.error('Error loading filters:', error);
            }}
        }}
        
        // Populate filter dropdowns
        function populateFilterDropdowns() {{
            if (!settingsData) return;
            
            // Populate account filter
            const accountSelect = document.getElementById('accountFilter');
            accountSelect.innerHTML = '<option value="">Tất cả tài khoản</option>';
            settingsData.accounts.forEach(acc => {{
                const option = document.createElement('option');
                option.value = acc.id;
                option.textContent = `${{acc.name}} (${{acc.type}})`;
                accountSelect.appendChild(option);
            }});
            accountSelect.value = currentFilters.account;
            
            // Populate prefix filter
            const prefixSelect = document.getElementById('prefixFilter');
            prefixSelect.innerHTML = '<option value="">Tất cả prefix</option>';
            settingsData.prefixes.forEach(prefix => {{
                const option = document.createElement('option');
                option.value = prefix.id;
                option.textContent = prefix.name;
                prefixSelect.appendChild(option);
            }});
            prefixSelect.value = currentFilters.prefix;
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
            panel.classList.toggle('open');
            overlay.classList.toggle('open');
        }}
        
        function closeFilterPanel() {{
            const panel = document.getElementById('filterPanel');
            const overlay = document.getElementById('filterPanelOverlay');
            panel.classList.remove('open');
            overlay.classList.remove('open');
        }}
        
        // Date Picker Functions
        function openDatePicker() {{
            const modal = document.getElementById('datePickerModal');
            const overlay = document.getElementById('datePickerOverlay');
            modal.classList.add('open');
            overlay.classList.add('open');
        }}
        
        function closeDatePicker() {{
            const modal = document.getElementById('datePickerModal');
            const overlay = document.getElementById('datePickerOverlay');
            modal.classList.remove('open');
            overlay.classList.remove('open');
        }}
        
        function applyDateRange() {{
            const dateFrom = document.getElementById('dateFrom').value;
            const dateTo = document.getElementById('dateTo').value;
            
            if (dateFrom && dateTo) {{
                currentFilters.dateRange = 'custom';
                currentFilters.dateFrom = dateFrom;
                currentFilters.dateTo = dateTo;
                
                // Update date range text
                const fromDate = new Date(dateFrom);
                const toDate = new Date(dateTo);
                const dateText = formatDateRangeText(fromDate, toDate);
                document.getElementById('dateRangeText').textContent = dateText;
                
                saveFilters();
                loadData();
                closeDatePicker();
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
            currentFilters.dateRange = 'last7days';
            document.getElementById('dateRangeText').textContent = '7 ngày qua';
            
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
            if (currentFilters.dateRange && currentFilters.dateRange !== 'last7days') count++;
            
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
                updateTable(data.rows || [], data.total || 0);
                
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
                page_size: pageSize || 50
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
        function getDateRange() {{
            const range = currentFilters.dateRange || 'last7days';
            const today = new Date();
            today.setHours(23, 59, 59, 999);
            
            let from, to;
            
            if (range === 'today') {{
                from = new Date(today);
                from.setHours(0, 0, 0, 0);
                to = today;
            }} else if (range === 'yesterday') {{
                from = new Date(today);
                from.setDate(from.getDate() - 1);
                from.setHours(0, 0, 0, 0);
                to = new Date(today);
                to.setDate(to.getDate() - 1);
                to.setHours(23, 59, 59, 999);
            }} else if (range === 'last7days') {{
                from = new Date(today);
                from.setDate(from.getDate() - 6);
                from.setHours(0, 0, 0, 0);
                to = today;
            }} else if (range === 'last30days') {{
                from = new Date(today);
                from.setDate(from.getDate() - 29);
                from.setHours(0, 0, 0, 0);
                to = today;
            }} else {{
                // Custom range - use saved dates or default to today
                from = currentFilters.dateFrom ? new Date(currentFilters.dateFrom) : new Date(today);
                from.setHours(0, 0, 0, 0);
                to = currentFilters.dateTo ? new Date(currentFilters.dateTo) : today;
                to.setHours(23, 59, 59, 999);
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
    """Perform action on adset (activate/pause)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if action not in ["activate", "pause"]:
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
        
        # Here you would integrate with Facebook API to actually change the adset status
        # For now, just return success
        new_status = "ACTIVE" if action == "activate" else "PAUSED"
        
        # In real implementation, you would:
        # 1. Get user's Facebook access token
        # 2. Make API call to Facebook to update adset status
        # 3. Update local database if successful
        
        logger.info(f"Action {action} performed on adset {item_id} by user {current_user.id}")
        
        return JSONResponse({
            "success": True,
            "action": action,
            "item_id": item_id,
            "new_status": new_status,
            "message": f"Adset {action}d successfully"
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


        <link rel="icon" type="image/png" href="/static/favicon.png">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {{
                /* Color System */
                --primary: #1877f2;
                --primary-hover: #166fe5;
                --secondary: #42b883;
                --accent: #f59e0b;
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --info: #3b82f6;
                
                /* Grays */
                --gray-50: #f9fafb;
                --gray-100: #f3f4f6;
                --gray-200: #e5e7eb;
                --gray-300: #d1d5db;
                --gray-400: #9ca3af;
                --gray-500: #6b7280;
                --gray-600: #4b5563;
                --gray-700: #374151;
                --gray-800: #1f2937;
                --gray-900: #111827;
                
                /* Layout */
                --max-width: 1400px;
                --header-height: 4rem;
                --sidebar-width: 16rem;
                
                /* Shadows */
                --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
                --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
                --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
                
                /* Radius */
                --radius-sm: 0.375rem;
                --radius: 0.5rem;
                --radius-md: 0.5rem;
                --radius-lg: 0.75rem;
                --radius-xl: 1rem;
                --radius-2xl: 1.5rem;
                
                /* Animations */
                --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                --transition-fast: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: var(--gray-800);
                line-height: 1.6;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}
            
            /* Layout Components */
            .container {{
                max-width: var(--max-width);
                margin: 0 auto;
                padding: 1.5rem;
                min-height: 100vh;
            }}
            
            /* Header */
            .header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 2rem;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-radius: var(--radius-2xl);
                padding: 1rem 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: var(--shadow-xl);
            }}
            
            .header-left {{
                display: flex;
                align-items: center;
                gap: 1rem;
            }}
            
            .header-title {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
                color: white;
                font-size: 1.5rem;
                font-weight: 700;
            }}
            
            .settings-status {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.375rem 0.75rem;
                background: rgba(255, 255, 255, 0.15);
                border-radius: var(--radius-lg);
                color: white;
                font-size: 0.875rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .settings-status.complete {{
                background: rgba(16, 185, 129, 0.2);
                border-color: rgba(16, 185, 129, 0.3);
            }}
            
            .settings-status.incomplete {{
                background: rgba(239, 68, 68, 0.2);
                border-color: rgba(239, 68, 68, 0.3);
            }}
            
            .header-right {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }}
            
            .btn-settings {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: var(--radius-lg);
                font-weight: 500;
                transition: var(--transition);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            
            .btn-settings:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-1px);
                color: white;
            }}
            
            /* Controls Bar */
            .controls-bar {{
                display: grid;
                grid-template-columns: auto 1fr auto auto auto auto;
                gap: 1rem;
                align-items: center;
                background: white;
                padding: 1rem 1.5rem;
                border-radius: var(--radius-2xl);
                box-shadow: var(--shadow-lg);
                margin-bottom: 2rem;
                border: 1px solid var(--gray-200);
            }}
            
            .filters-section {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }}
            
            .filter-btn {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: var(--gray-50);
                border: 1px solid var(--gray-300);
                border-radius: var(--radius-lg);
                cursor: pointer;
                transition: var(--transition);
                font-weight: 500;
                position: relative;
                white-space: nowrap;
            }}
            
            .filter-btn:hover {{
                background: var(--gray-100);
                border-color: var(--primary);
                transform: translateY(-1px);
            }}
            
            .filter-btn.active {{
                background: var(--primary);
                color: white;
                border-color: var(--primary);
            }}
            
            .filter-badge {{
                position: absolute;
                top: -0.375rem;
                right: -0.375rem;
                background: var(--primary);
                color: white;
                border-radius: 50%;
                width: 1.125rem;
                height: 1.125rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.75rem;
                font-weight: 600;
                border: 2px solid white;
            }}
            
            .search-container {{
                position: relative;
                flex: 1;
                max-width: 400px;
            }}
            
            .search-input {{
                width: 100%;
                padding: 0.5rem 1rem 0.5rem 2.5rem;
                border: 1px solid var(--gray-300);
                border-radius: var(--radius-lg);
                font-size: 0.875rem;
                transition: var(--transition);
                background: var(--gray-50);
            }}
            
            .search-input:focus {{
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(24, 119, 242, 0.1);
                background: white;
            }}
            
            .search-icon {{
                position: absolute;
                left: 0.75rem;
                top: 50%;
                transform: translateY(-50%);
                color: var(--gray-400);
                pointer-events: none;
            }}
            
            .control-group {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            
            .control-btn {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: white;
                border: 1px solid var(--gray-300);
                border-radius: var(--radius-lg);
                cursor: pointer;
                transition: var(--transition);
                font-weight: 500;
                white-space: nowrap;
            }}
            
            .control-btn:hover {{
                background: var(--gray-50);
                border-color: var(--primary);
                transform: translateY(-1px);
            }}
            
            .btn-primary {{
                background: var(--primary);
                color: white;
                border-color: var(--primary);
            }}
            
            .btn-primary:hover {{
                background: var(--primary-hover);
                color: white;
            }}
            
            .btn-refresh.loading {{
                opacity: 0.7;
                pointer-events: none;
            }}
            
            .btn-refresh.loading .fa-sync-alt {{
                animation: spin 1s linear infinite;
            }}
            
            @keyframes spin {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
            
            /* Stats Grid */
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            
            .stat-card {{
                background: white;
                padding: 1.5rem;
                border-radius: var(--radius-2xl);
                box-shadow: var(--shadow-md);
                border: 1px solid var(--gray-200);
                transition: var(--transition);
                position: relative;
                overflow: hidden;
            }}
            
            .stat-card:hover {{
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }}
            
            .stat-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary), var(--secondary));
            }}
            
            .stat-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1rem;
            }}
            
            .stat-title {{
                font-size: 0.875rem;
                font-weight: 600;
                color: var(--gray-600);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stat-icon {{
                width: 2.5rem;
                height: 2.5rem;
                border-radius: var(--radius-lg);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.25rem;
            }}
            
            .stat-icon.spend {{ background: var(--primary); }}
            .stat-icon.results {{ background: var(--success); }}
            .stat-icon.gia {{ background: var(--warning); }}
            .stat-icon.adsets {{ background: var(--info); }}
            
            .stat-value {{
                font-size: 2rem;
                font-weight: 800;
                color: var(--gray-900);
                margin-bottom: 0.5rem;
                line-height: 1;
            }}
            
            .stat-subtitle {{
                font-size: 0.875rem;
                color: var(--gray-600);
                display: flex;
                align-items: center;
                gap: 0.25rem;
            }}
            
            .stat-change {{
                padding: 0.125rem 0.375rem;
                border-radius: var(--radius);
                font-weight: 600;
                font-size: 0.75rem;
            }}
            
            .stat-change.positive {{
                background: rgba(16, 185, 129, 0.1);
                color: var(--success);
            }}
            
            .stat-change.negative {{
                background: rgba(239, 68, 68, 0.1);
                color: var(--danger);
            }}
            
            /* Data Table */
            .table-container {{
                background: white;
                border-radius: var(--radius-2xl);
                box-shadow: var(--shadow-md);
                border: 1px solid var(--gray-200);
                overflow: hidden;
            }}
            
            .table-header {{
                padding: 1.5rem;
                border-bottom: 1px solid var(--gray-200);
                background: var(--gray-50);
            }}
            
            .table-title {{
                font-size: 1.25rem;
                font-weight: 700;
                color: var(--gray-900);
            }}
            
            .table-content {{
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
            }}
            
            .data-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            .data-table th,
            .data-table td {{
                padding: 0.75rem 1rem;
                text-align: left;
                border-bottom: 1px solid var(--gray-200);
                vertical-align: middle;
            }}
            
            .data-table th {{
                background: var(--gray-50);
                font-weight: 600;
                color: var(--gray-700);
                font-size: 0.875rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            
            .data-table tbody tr {{
                transition: var(--transition);
            }}
            
            .data-table tbody tr:hover {{
                background: var(--gray-50);
            }}
            
            /* Status Badges */
            .status-badge {{
                display: inline-flex;
                align-items: center;
                gap: 0.25rem;
                padding: 0.25rem 0.5rem;
                border-radius: var(--radius);
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .status-badge.active {{
                background: rgba(16, 185, 129, 0.1);
                color: var(--success);
            }}
            
            .status-badge.paused {{
                background: rgba(239, 68, 68, 0.1);
                color: var(--danger);
            }}
            
            .status-badge.pending {{
                background: rgba(245, 158, 11, 0.1);
                color: var(--warning);
            }}
            
            /* Action Buttons */
            .action-btn {{
                padding: 0.375rem 0.75rem;
                border: 1px solid var(--gray-300);
                border-radius: var(--radius);
                background: white;
                color: var(--gray-700);
                cursor: pointer;
                transition: var(--transition);
                font-size: 0.75rem;
                font-weight: 500;
            }}
            
            .action-btn:hover {{
                border-color: var(--primary);
                color: var(--primary);
                transform: translateY(-1px);
            }}
            
            .action-btn.danger:hover {{
                border-color: var(--danger);
                color: var(--danger);
                background: rgba(239, 68, 68, 0.05);
            }}
            
            .action-btn.success:hover {{
                border-color: var(--success);
                color: var(--success);
                background: rgba(16, 185, 129, 0.05);
            }}
            
            /* Loading States */
            .loading {{
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 3rem;
                color: var(--gray-500);
            }}
            
            .loading-spinner {{
                animation: spin 1s linear infinite;
                margin-right: 0.5rem;
            }}
            
            /* Empty State */
            .empty-state {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 3rem;
                color: var(--gray-500);
                text-align: center;
            }}
            
            .empty-state-icon {{
                font-size: 3rem;
                margin-bottom: 1rem;
                opacity: 0.5;
            }}
            
            /* Filter Panel */
            .filter-panel {{
                position: fixed;
                top: 0;
                right: -400px;
                width: 400px;
                height: 100vh;
                background: white;
                box-shadow: var(--shadow-xl);
                transition: var(--transition);
                z-index: 1000;
                overflow-y: auto;
            }}
            
            .filter-panel.open {{
                right: 0;
            }}
            
            .filter-panel-header {{
                padding: 1.5rem;
                border-bottom: 1px solid var(--gray-200);
                background: var(--gray-50);
            }}
            
            .filter-panel-title {{
                font-size: 1.25rem;
                font-weight: 700;
                color: var(--gray-900);
            }}
            
            .filter-panel-content {{
                padding: 1.5rem;
            }}
            
            .filter-group {{
                margin-bottom: 1.5rem;
            }}
            
            .filter-label {{
                display: block;
                font-weight: 600;
                color: var(--gray-700);
                margin-bottom: 0.5rem;
            }}
            
            .filter-select {{
                width: 100%;
                padding: 0.5rem 0.75rem;
                border: 1px solid var(--gray-300);
                border-radius: var(--radius-lg);
                background: white;
                transition: var(--transition);
            }}
            
            .filter-select:focus {{
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(24, 119, 242, 0.1);
            }}
            
            /* Overlay */
            .overlay {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                z-index: 999;
                opacity: 0;
                visibility: hidden;
                transition: var(--transition);
            }}
            
            .overlay.open {{
                opacity: 1;
                visibility: visible;
            }}
            
            /* Responsive Design */
            @media (max-width: 1024px) {{
                .controls-bar {{
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }}
                
                .filters-section {{
                    justify-content: center;
                    flex-wrap: wrap;
                }}
                
                .stats-grid {{
                    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                    gap: 1rem;
                }}
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 1rem;
                }}
                
                .header {{
                    flex-direction: column;
                    gap: 1rem;
                    text-align: center;
                }}
                
                .header-left,
                .header-right {{
                    justify-content: center;
                }}
                
                .stats-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .table-content {{
                    max-height: 400px;
                }}
                
                .filter-panel {{
                    width: 100%;
                    right: -100%;
                }}
            }}
            
            /* Dark mode support */
            @media (prefers-color-scheme: dark) {{
                /* Add dark mode styles here if needed */
            }}
            
            /* Animation utilities */
            .fade-in {{
                animation: fadeIn 0.3s ease-in-out;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .slide-in-right {{
                animation: slideInRight 0.3s ease-out;
            }}
            
            @keyframes slideInRight {{
                from {{ transform: translateX(20px); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
            
            /* Utility classes */
            .text-center {{ text-align: center; }}
            .text-right {{ text-align: right; }}
            .font-semibold {{ font-weight: 600; }}
            .font-bold {{ font-weight: 700; }}
            .text-sm {{ font-size: 0.875rem; }}
            .text-xs {{ font-size: 0.75rem; }}
            .text-lg {{ font-size: 1.125rem; }}
            .text-xl {{ font-size: 1.25rem; }}
            .text-2xl {{ font-size: 1.5rem; }}
            .hidden {{ display: none; }}
            .block {{ display: block; }}
            .inline-block {{ display: inline-block; }}
            .flex {{ display: flex; }}
            .inline-flex {{ display: inline-flex; }}
            .grid {{ display: grid; }}
            .relative {{ position: relative; }}
            .absolute {{ position: absolute; }}
            .mb-0 {{ margin-bottom: 0; }}
            .mb-1 {{ margin-bottom: 0.25rem; }}
            .mb-2 {{ margin-bottom: 0.5rem; }}
            .mb-3 {{ margin-bottom: 0.75rem; }}
            .mb-4 {{ margin-bottom: 1rem; }}
            .mb-6 {{ margin-bottom: 1.5rem; }}
            .mt-2 {{ margin-top: 0.5rem; }}
            .mt-4 {{ margin-top: 1rem; }}
            .ml-2 {{ margin-left: 0.5rem; }}
            .mr-2 {{ margin-right: 0.5rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <header class="header fade-in">
                <div class="header-left">
                    <div class="header-title">
                        <i class="fas fa-chart-line"></i>
                        <span>Dashboard</span>
                    </div>
                    <div class="settings-status" id="settingsStatus">
                        <i class="fas fa-cog"></i>
                        <span>Loading...</span>
                    </div>
                </div>
                <div class="header-right">
                    <a href="/settings" class="btn-settings">
                        <i class="fas fa-cog"></i>
                        <span>Settings</span>
                    </a>
                    <a href="/" class="btn-settings">
                        <i class="fas fa-home"></i>
                        <span>Home</span>
                    </a>
                    <!-- Controls Bar -->
            <div class="controls-bar slide-in-right">
                <!-- Filters Section -->
                <div class="filters-section">
                    <button class="filter-btn" id="accountFilter" onclick="toggleAccountDropdown()">
                        <i class="fas fa-user"></i>
                        <span>Account</span>
                        <span class="filter-badge hidden" id="accountBadge">0</span>
                    </button>
                    
                    <button class="filter-btn" id="prefixFilter" onclick="togglePrefixDropdown()">
                        <i class="fas fa-tag"></i>
                        <span>Prefix</span>
                        <span class="filter-badge hidden" id="prefixBadge">0</span>
                    </button>
                    
                    <button class="filter-btn" onclick="openFilterPanel()">
                        <i class="fas fa-filter"></i>
                        <span>More Filters</span>
                        <span class="filter-badge hidden" id="totalFiltersBadge">0</span>
                    </button>
                </div>
                
                <!-- Search -->
                <div class="search-container">
                    <div class="search-icon">
                        <i class="fas fa-search"></i>
                    </div>
                    <input type="text" class="search-input" id="searchInput" placeholder="Search campaigns, adsets, ads...">
                </div>
                
                <!-- View Type -->
                <div class="control-group">
                    <select class="filter-select" id="viewType" onchange="changeViewType()">
                        <option value="adset">Adset View</option>
                        <option value="campaign">Campaign View</option>
                        <option value="ad">Ad View</option>
                    </select>
                </div>
                
                <!-- Date Range -->
                <div class="control-group">
                    <select class="filter-select" id="dateRange" onchange="changeDateRange()">
                        <option value="today">Today</option>
                        <option value="yesterday">Yesterday</option>
                        <option value="last7days">Last 7 Days</option>
                        <option value="last30days">Last 30 Days</option>
                        <option value="custom">Custom Range</option>
                    </select>
                </div>
                
                <!-- Actions -->
                <div class="control-group">
                    <button class="control-btn btn-primary" id="refreshBtn" onclick="refreshData()">
                        <i class="fas fa-sync-alt"></i>
                        <span>Refresh</span>
                    </button>
                </div>
                
            </div>
            
            <!-- Stats Grid -->
            <div class="stats-grid fade-in" id="statsGrid">
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-title">Total Spend</div>
                        <div class="stat-icon spend">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                    </div>
                    <div class="stat-value" id="totalSpend">$0</div>
                    <div class="stat-subtitle">
                        <span id="spendChange" class="stat-change">-</span>
                        <span>vs last period</span>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-title">Results</div>
                        <div class="stat-icon results">
                            <i class="fas fa-chart-line"></i>
                        </div>
                    </div>
                    <div class="stat-value" id="totalResults">0</div>
                    <div class="stat-subtitle">
                        <span id="resultsChange" class="stat-change">-</span>
                        <span>vs last period</span>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-title">Avg Cost per Result</div>
                        <div class="stat-icon gia">
                            <i class="fas fa-target"></i>
                        </div>
                    </div>
                    <div class="stat-value" id="avgGiaData">$0</div>
                    <div class="stat-subtitle">
                        <span id="giaChange" class="stat-change">-</span>
                        <span>vs last period</span>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-title">Active Adsets</div>
                        <div class="stat-icon adsets">
                            <i class="fas fa-play-circle"></i>
                        </div>
                    </div>
                    <div class="stat-value">
                        <span id="activeAdsets">0</span>
                        <span class="text-sm text-gray-500">/ </span>
                        <span id="totalAdsets" class="text-sm text-gray-500">0</span>
                    </div>
                    <div class="stat-subtitle">
                        <span id="adsetsChange" class="stat-change">-</span>
                        <span>adsets total</span>
                    </div>
                </div>
            </div>
            
            <!-- Data Table -->
            <div class="table-container fade-in">
                <div class="table-header">
                    <h2 class="table-title" id="tableTitle">Adsets Performance</h2>
                </div>
                <div class="table-content">
                    <table class="data-table" id="dataTable">
                        <thead id="tableHead">
                            <tr>
                                <th>Status</th>
                                <th>Name</th>
                                <th>Account</th>
                                <th>Prefix</th>
                                <th>Spend</th>
                                <th>Results</th>
                                <th>Cost/Result</th>
                                <th>Impressions</th>
                                <th>Clicks</th>
                                <th>CTR</th>
                                <th>CPC</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody">
                            <tr>
                                <td colspan="12" class="loading">
                                    <i class="fas fa-spinner loading-spinner"></i>
                                    <span>Loading data...</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Pagination -->
            <div id="pagination" class="flex justify-center mt-6 hidden">
                <!-- Pagination will be populated by JavaScript -->
            </div>
        </div>
        
        <!-- Filter Panel -->
        <div class="filter-panel" id="filterPanel">
            <div class="filter-panel-header">
                <h3 class="filter-panel-title">Advanced Filters</h3>
                <button class="control-btn" onclick="closeFilterPanel()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="filter-panel-content">
                <div class="filter-group">
                    <label class="filter-label">Campaign Type</label>
                    <select class="filter-select" id="campaignTypeFilter">
                        <option value="">All Campaign Types</option>
                        <option value="ECOMMERCE">E-commerce</option>
                        <option value="LEAD_GENERATION">Lead Generation</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label">Status</label>
                    <select class="filter-select" id="statusFilter">
                        <option value="">All Statuses</option>
                        <option value="ACTIVE">Active</option>
                        <option value="PAUSED">Paused</option>
                        <option value="ARCHIVED">Archived</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label">Custom Date Range</label>
                    <input type="date" class="filter-select" id="dateFrom" onchange="updateFilters()">
                    <input type="date" class="filter-select mt-2" id="dateTo" onchange="updateFilters()">
                </div>
                
                <div class="filter-group">
                    <button class="control-btn btn-primary" onclick="applyFilters()" style="width: 100%;">
                        <i class="fas fa-filter"></i>
                        <span>Apply Filters</span>
                    </button>
                </div>
                
                <div class="filter-group">
                    <button class="control-btn" onclick="clearFilters()" style="width: 100%;">
                        <i class="fas fa-times"></i>
                        <span>Clear All</span>
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Overlay -->
        <div class="overlay" id="overlay" onclick="closeFilterPanel()"></div>
        
        <script>
            // Global variables
            let currentFilters = {{}};
            let currentPage = 1;
            let pageSize = 50;
            let isLoading = false;
            let settingsData = null;
            
            // Authentication helper
            function getAuthToken() {{
                return localStorage.getItem('access_token') || '';
            }}
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {{
                checkSettingsStatus();
                loadFilters();
                loadData();
                
                // Setup search debouncing
                const searchInput = document.getElementById('searchInput');
                let searchTimeout;
                searchInput.addEventListener('input', function() {{
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {{
                        currentFilters.search = this.value;
                        currentPage = 1;
                        loadData();
                    }}, 500);
                }});
                
                // Auto-refresh every 5 minutes
                setInterval(refreshData, 300000);
            }});
            
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
                }}
            }}
            
            // Update settings status indicator
            function updateSettingsStatus(status) {{
                const statusElement = document.getElementById('settingsStatus');
                const icon = statusElement.querySelector('i');
                const text = statusElement.querySelector('span');
                
                if (status.settings_complete) {{
                    statusElement.className = 'settings-status complete';
                    icon.className = 'fas fa-check-circle';
                    text.textContent = `Ready ({{status.accounts_count}} accounts, {{status.prefixes_count}} prefixes)`;
                }} else {{
                    statusElement.className = 'settings-status incomplete';
                    icon.className = 'fas fa-exclamation-triangle';
                    
                    if (!status.has_token) {{
                        text.textContent = 'Token missing - Configure in Settings';
                    }} else if (status.accounts_count === 0) {{
                        text.textContent = 'No accounts - Add in Settings';
                    }} else if (status.prefixes_count === 0) {{
                        text.textContent = 'No prefixes - Add in Settings';
                    }} else {{
                        text.textContent = 'Setup incomplete - Check Settings';
                    }}
                }}
            }}
            
            // Load available filters from settings
            async function loadFilters() {{
                try {{
                    const response = await fetch('/dashboard/filters', {{
                        headers: {{
                            'Authorization': 'Bearer ' + getAuthToken()
                        }}
                    }});
                    
                    if (response.ok) {{
                        settingsData = await response.json();
                        populateFilterDropdowns();
                    }}
                }} catch (error) {{
                    console.error('Error loading filters:', error);
                }}
            }}
            
            // Populate filter dropdowns
            function populateFilterDropdowns() {{
                if (!settingsData) return;
                
                // Update account filter button text
                const accountBtn = document.getElementById('accountFilter');
                accountBtn.querySelector('span').textContent = `Account ({{settingsData.accounts.length}})`;
                
                // Update prefix filter button text  
                const prefixBtn = document.getElementById('prefixFilter');
                prefixBtn.querySelector('span').textContent = `Prefix ({{settingsData.prefixes.length}})`;
                
                // Populate campaign type filter
                const campaignTypeSelect = document.getElementById('campaignTypeFilter');
                campaignTypeSelect.innerHTML = '<option value="">All Campaign Types</option>';
                settingsData.campaign_types.forEach(type => {{
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type;
                    campaignTypeSelect.appendChild(option);
                }});
            }}
            
            // Load dashboard data
            async function loadData() {{
                if (isLoading) return;
                
                isLoading = true;
                updateLoadingState(true);
                
                try {{
                    const params = buildAPIParams();
                    const response = await fetch(`/dashboard/data?${{params}}`, {{
                        headers: {{
                            'Authorization': 'Bearer ' + getAuthToken()
                        }}
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('Failed to load data');
                    }}
                    
                    const data = await response.json();
                    updateStats(data.stats || {{}});
                    updateTable(data.ads || [], data.total || 0);
                    
                }} catch (error) {{
                    console.error('Error loading data:', error);
                    showError('Failed to load data: ' + error.message);
                }} finally {{
                    isLoading = false;
                    updateLoadingState(false);
                }}
            }}
            
            // Build API parameters
            function buildAPIParams() {{
                const params = new URLSearchParams({{
                    page: currentPage,
                    page_size: pageSize,
                    view_type: document.getElementById('viewType').value
                }});
                
                // Add filters
                Object.keys(currentFilters).forEach(key => {{
                    if (currentFilters[key] && currentFilters[key] !== '') {{
                        params.append(key, currentFilters[key]);
                    }}
                }});
                
                return params.toString();
            }}
            
            // Update stats cards
            function updateStats(stats) {{
                document.getElementById('totalSpend').textContent = formatCurrency(stats.totalSpend || 0);
                document.getElementById('totalResults').textContent = formatNumber(stats.totalResults || 0);
                document.getElementById('avgGiaData').textContent = formatCurrency(stats.avgGiaData || 0);
                document.getElementById('activeAdsets').textContent = formatNumber(stats.activeAdsets || 0);
                document.getElementById('totalAdsets').textContent = formatNumber(stats.totalAdsets || 0);
                
                // Animate counters
                animateCounter('totalSpend', stats.totalSpend || 0, true);
                animateCounter('totalResults', stats.totalResults || 0);
                animateCounter('avgGiaData', stats.avgGiaData || 0, true);
            }}
            
            // Update table
            function updateTable(ads, total) {{
                const tableBody = document.getElementById('tableBody');
                const viewType = document.getElementById('viewType').value;
                
                if (ads.length === 0) {{
                    tableBody.innerHTML = `
                        <tr>
                            <td colspan="12" class="empty-state">
                                <div class="empty-state-icon">
                                    <i class="fas fa-chart-line"></i>
                                </div>
                                <div>No data available</div>
                                <small>Try adjusting your filters or date range</small>
                            </td>
                        </tr>
                    `;
                    return;
                }}
                
                tableBody.innerHTML = ads.map(ad => `
                    <tr>
                        <td>
                            <span class="status-badge ${{ad.adset_status.toLowerCase()}}">
                                <i class="fas fa-${{ad.adset_status === 'ACTIVE' ? 'play' : 'pause'}}"></i>
                                ${{ad.adset_status}}
                            </span>
                        </td>
                        <td>
                            <div class="font-semibold">
                                ${{viewType === 'campaign' ? ad.campaign_name : 
                                  viewType === 'adset' ? ad.adset_name : ad.ad_name}}
                            </div>
                            <div class="text-sm text-gray-500">
                                ID: ${{viewType === 'campaign' ? ad.campaign_id : 
                                      viewType === 'adset' ? ad.adset_id : ad.ad_id}}
                            </div>
                        </td>
                        <td>
                            <span class="text-sm">${{ad.account_id}}</span>
                        </td>
                        <td>
                            <span class="font-semibold">${{ad.prefix || '-'}}</span>
                        </td>
                        <td class="font-semibold">${{formatCurrency(ad.spend)}}</td>
                        <td class="font-semibold">${{formatNumber(ad.results)}}</td>
                        <td>${{formatCurrency(ad.gia_data)}}</td>
                        <td>${{formatNumber(ad.impressions)}}</td>
                        <td>${{formatNumber(ad.clicks)}}</td>
                        <td>${{formatPercentage(ad.ctr)}}%</td>
                        <td>${{formatCurrency(ad.cpc)}}</td>
                        <td>
                            <div class="flex gap-1">
                                <button class="action-btn ${{ad.adset_status === 'ACTIVE' ? 'danger' : 'success'}}" 
                                        onclick="toggleStatus('${{ad.adset_id}}', '${{ad.adset_status}}')">
                                    <i class="fas fa-${{ad.adset_status === 'ACTIVE' ? 'pause' : 'play'}}"></i>
                                </button>
                                <button class="action-btn" onclick="increaseBudget('${{ad.adset_id}}')">
                                    <i class="fas fa-arrow-up"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('');
                
                // Update pagination
                updatePagination(total);
            }}
            
            // Update loading states
            function updateLoadingState(loading) {{
                const refreshBtn = document.getElementById('refreshBtn');
                const refreshIcon = refreshBtn.querySelector('i');
                
                if (loading) {{
                    refreshBtn.classList.add('loading');
                    refreshIcon.classList.add('fa-spin');
                }} else {{
                    refreshBtn.classList.remove('loading');
                    refreshIcon.classList.remove('fa-spin');
                }}
            }}
            
            // Refresh data
            function refreshData() {{
                currentPage = 1;
                loadData();
                checkSettingsStatus();
            }}
            
            // Filter panel functions
            function openFilterPanel() {{
                document.getElementById('filterPanel').classList.add('open');
                document.getElementById('overlay').classList.add('open');
            }}
            
            function closeFilterPanel() {{
                document.getElementById('filterPanel').classList.remove('open');
                document.getElementById('overlay').classList.remove('open');
            }}
            
            // Apply filters
            function applyFilters() {{
                currentFilters.campaign_type = document.getElementById('campaignTypeFilter').value;
                currentFilters.status = document.getElementById('statusFilter').value;
                currentFilters.date_from = document.getElementById('dateFrom').value;
                currentFilters.date_to = document.getElementById('dateTo').value;
                
                currentPage = 1;
                loadData();
                closeFilterPanel();
                updateFilterBadges();
            }}
            
            // Clear filters
            function clearFilters() {{
                currentFilters = {{}};
                document.getElementById('campaignTypeFilter').value = '';
                document.getElementById('statusFilter').value = '';
                document.getElementById('dateFrom').value = '';
                document.getElementById('dateTo').value = '';
                document.getElementById('searchInput').value = '';
                
                currentPage = 1;
                loadData();
                updateFilterBadges();
            }}
            
            // Update filter badges
            function updateFilterBadges() {{
                const activeFilters = Object.values(currentFilters).filter(v => v && v !== '').length;
                const badge = document.getElementById('totalFiltersBadge');
                
                if (activeFilters > 0) {{
                    badge.textContent = activeFilters;
                    badge.classList.remove('hidden');
                }} else {{
                    badge.classList.add('hidden');
                }}
            }}
            
            // Change view type
            function changeViewType() {{
                const viewType = document.getElementById('viewType').value;
                document.getElementById('tableTitle').textContent = 
                    viewType.charAt(0).toUpperCase() + viewType.slice(1) + 's Performance';
                
                currentPage = 1;
                loadData();
            }}
            
            // Change date range
            function changeDateRange() {{
                const range = document.getElementById('dateRange').value;
                const today = new Date();
                let dateFrom, dateTo;
                
                switch(range) {{
                    case 'today':
                        dateFrom = dateTo = today.toISOString().split('T')[0];
                        break;
                    case 'yesterday':
                        const yesterday = new Date(today);
                        yesterday.setDate(yesterday.getDate() - 1);
                        dateFrom = dateTo = yesterday.toISOString().split('T')[0];
                        break;
                    case 'last7days':
                        const week = new Date(today);
                        week.setDate(week.getDate() - 7);
                        dateFrom = week.toISOString().split('T')[0];
                        dateTo = today.toISOString().split('T')[0];
                        break;
                    case 'last30days':
                        const month = new Date(today);
                        month.setDate(month.getDate() - 30);
                        dateFrom = month.toISOString().split('T')[0];
                        dateTo = today.toISOString().split('T')[0];
                        break;
                    default:
                        return; // Custom range handled separately
                }}
                
                if (dateFrom && dateTo) {{
                    currentFilters.date_from = dateFrom;
                    currentFilters.date_to = dateTo;
                    currentPage = 1;
                    loadData();
                }}
            }}
            
            // Action functions
            async function toggleStatus(entityId, currentStatus) {{
                const action = currentStatus === 'ACTIVE' ? 'pause' : 'activate';
                
                try {{
                    const response = await fetch(`/dashboard/action/${{action}}/${{entityId}}`, {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + getAuthToken(),
                            'Content-Type': 'application/json'
                        }}
                    }});
                    
                    if (response.ok) {{
                        showSuccess(`Successfully ${{action}}d entity`);
                        loadData(); // Refresh data
                    }} else {{
                        throw new Error(`Failed to ${{action}} entity`);
                    }}
                }} catch (error) {{
                    showError(error.message);
                }}
            }}
            
            async function increaseBudget(entityId) {{
                try {{
                    const response = await fetch(`/dashboard/action/increase-budget/${{entityId}}`, {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + getAuthToken(),
                            'Content-Type': 'application/json'
                        }}
                    }});
                    
                    if (response.ok) {{
                        showSuccess('Budget increased successfully');
                        loadData(); // Refresh data
                    }} else {{
                        throw new Error('Failed to increase budget');
                    }}
                }} catch (error) {{
                    showError(error.message);
                }}
            }}
            
            
            // Utility functions
            function formatCurrency(value) {{
                return new Intl.NumberFormat('vi-VN', {{
                    style: 'currency',
                    currency: 'VND',
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                }}).format(value || 0);
            }}
            
            function formatNumber(value) {{
                return new Intl.NumberFormat('vi-VN').format(value || 0);
            }}
            
            function formatPercentage(value) {{
                return (value || 0).toFixed(2);
            }}
            
            function animateCounter(elementId, targetValue, isCurrency = false) {{
                const element = document.getElementById(elementId);
                const duration = 1000;
                const start = 0;
                const increment = targetValue / (duration / 16);
                let current = start;
                
                const timer = setInterval(() => {{
                    current += increment;
                    if (current >= targetValue) {{
                        current = targetValue;
                        clearInterval(timer);
                    }}
                    
                    element.textContent = isCurrency ? formatCurrency(current) : formatNumber(current);
                }}, 16);
            }}
            
            function showSuccess(message) {{
                // Implement toast notification
                console.log('Success:', message);
            }}
            
            function showError(message) {{
                // Implement toast notification  
                console.error('Error:', message);
            }}
            
            // Pagination functions
            function updatePagination(total) {{
                const totalPages = Math.ceil(total / pageSize);
                const paginationElement = document.getElementById('pagination');
                
                if (totalPages <= 1) {{
                    paginationElement.classList.add('hidden');
                    return;
                }}
                
                paginationElement.classList.remove('hidden');
                // Implement pagination UI here
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
async def dashboard_data(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=500),
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    view_type: Optional[str] = Query('adset')
):
    """API endpoint để lấy dữ liệu dashboard"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Lấy account_ids và prefixes của user
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db)
        
        if not user_account_ids:
            return JSONResponse({
                "ads": [],
                "total": 0,
                "stats": {
                    "totalSpend": 0,
                    "totalResults": 0,
                    "avgGiaData": 0,
                    "activeAdsets": 0,
                    "pausedAdsets": 0,
                    "totalAdsets": 0
                }
            })
        
        # Build query
        query = db.query(AdMetrics).filter(AdMetrics.account_id.in_(user_account_ids))
        
        # Apply filters
        if account_id:
            query = query.filter(AdMetrics.account_id == account_id)
        
        if prefix:
            query = query.filter(AdMetrics.prefix == prefix)
        
        if campaign_type and campaign_type != 'all':
            query = query.filter(AdMetrics.campaign_type == campaign_type)
        
        if status:
            query = query.filter(AdMetrics.adset_status == status)
        
        # Date filter
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(func.date(AdMetrics.date) >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(func.date(AdMetrics.date) <= date_to_obj)
            except ValueError:
                pass
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    AdMetrics.campaign_name.ilike(search_term),
                    AdMetrics.adset_name.ilike(search_term),
                    AdMetrics.ad_name.ilike(search_term)
                )
            )
        
        # Get total count
        total_query = query
        total = total_query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        ads = query.offset(offset).limit(page_size).all()
        
        # Calculate stats
        stats_query = db.query(
            func.sum(AdMetrics.spend).label('total_spend'),
            func.sum(AdMetrics.results).label('total_results'),
            func.avg(AdMetrics.gia_data).label('avg_gia_data'),
            func.sum(case((AdMetrics.adset_status == 'ACTIVE', 1), else_=0)).label('active_adsets'),
            func.sum(case((AdMetrics.adset_status == 'PAUSED', 1), else_=0)).label('paused_adsets'),
            func.count(distinct(AdMetrics.adset_id)).label('total_adsets')
        ).filter(AdMetrics.account_id.in_(user_account_ids))
        
        # Apply same filters to stats
        if account_id:
            stats_query = stats_query.filter(AdMetrics.account_id == account_id)
        if prefix:
            stats_query = stats_query.filter(AdMetrics.prefix == prefix)
        if campaign_type and campaign_type != 'all':
            stats_query = stats_query.filter(AdMetrics.campaign_type == campaign_type)
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                stats_query = stats_query.filter(func.date(AdMetrics.date) >= date_from_obj)
            except ValueError:
                pass
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                stats_query = stats_query.filter(func.date(AdMetrics.date) <= date_to_obj)
            except ValueError:
                pass
        
        stats_result = stats_query.first()
        
        stats = {
            "totalSpend": float(stats_result.total_spend or 0),
            "totalResults": int(stats_result.total_results or 0),
            "avgGiaData": float(stats_result.avg_gia_data or 0),
            "activeAdsets": int(stats_result.active_adsets or 0),
            "pausedAdsets": int(stats_result.paused_adsets or 0),
            "totalAdsets": int(stats_result.total_adsets or 0)
        }
        
        # Convert ads to dict
        ads_data = []
        for ad in ads:
            ads_data.append({
                "campaign_id": ad.campaign_id,
                "campaign_name": ad.campaign_name,
                "adset_id": ad.adset_id,
                "adset_name": ad.adset_name,
                "ad_id": ad.ad_id,
                "ad_name": ad.ad_name,
                "account_id": ad.account_id,
                "prefix": ad.prefix,
                "adset_status": ad.adset_status,
                "spend": float(ad.spend or 0),
                "results": int(ad.results or 0),
                "gia_data": float(ad.gia_data or 0),
                "impressions": int(ad.impressions or 0),
                "clicks": int(ad.clicks or 0),
                "ctr": float(ad.ctr or 0),
                "cpc": float(ad.cpc or 0),
                "purchases": int(ad.purchases or 0),
                "purchase_value": float(ad.purchase_value or 0),
                "daily_budget": float(ad.amount_spent or 0)  # Using amount_spent as budget placeholder
            })
        
        return JSONResponse({
            "ads": ads_data,
            "total": total,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error in dashboard_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Action endpoints for dashboard operations
@router.post("/action/pause/{entity_id}")
async def pause_entity(
    entity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Pause an adset/campaign"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Here you would implement the actual pause logic using Facebook API
    # For now, return success
    return JSONResponse({"success": True, "message": "Paused successfully"})


@router.post("/action/activate/{entity_id}")
async def activate_entity(
    entity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Activate an adset/campaign"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Here you would implement the actual activate logic using Facebook API
    # For now, return success
    return JSONResponse({"success": True, "message": "Activated successfully"})


@router.post("/action/increase-budget/{entity_id}")
async def increase_budget(
    entity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Increase budget by 20%"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Here you would implement the actual budget increase logic using Facebook API
    # For now, return success
    return JSONResponse({"success": True, "message": "Budget increased successfully"})


@router.post("/action/decrease-budget/{entity_id}")
async def decrease_budget(
    entity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Decrease budget by 20%"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Here you would implement the actual budget decrease logic using Facebook API
    # For now, return success
    return JSONResponse({"success": True, "message": "Budget decreased successfully"})


@router.get("/data")
async def dashboard_data(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=500),
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    view_type: Optional[str] = Query('adset')
):
    """API endpoint để lấy dữ liệu dashboard"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Lấy account_ids và prefixes của user
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db)
        
        if not user_account_ids:
            return JSONResponse({
                "ads": [],
                "total": 0,
                "stats": {
                    "totalSpend": 0,
                    "totalResults": 0,
                    "avgGiaData": 0,
                    "activeAdsets": 0,
                    "pausedAdsets": 0,
                    "totalAdsets": 0
                }
            })
        
        # Build query
        query = db.query(AdMetrics).filter(AdMetrics.account_id.in_(user_account_ids))
        
        # Apply filters
        if account_id:
            query = query.filter(AdMetrics.account_id == account_id)
        
        if prefix:
            query = query.filter(AdMetrics.prefix == prefix)
        
        if campaign_type and campaign_type != 'all':
            query = query.filter(AdMetrics.campaign_type == campaign_type)
        
        if status:
            query = query.filter(AdMetrics.adset_status == status)
        
        # Date filter
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(func.date(AdMetrics.date) >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(func.date(AdMetrics.date) <= date_to_obj)
            except ValueError:
                pass
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    AdMetrics.campaign_name.ilike(search_term),
                    AdMetrics.adset_name.ilike(search_term),
                    AdMetrics.ad_name.ilike(search_term)
                )
            )
        
        # Get total count
        total_query = query
        total = total_query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        ads = query.offset(offset).limit(page_size).all()
        
        # Calculate stats
        stats_query = db.query(
            func.sum(AdMetrics.spend).label('total_spend'),
            func.sum(AdMetrics.results).label('total_results'),
            func.avg(AdMetrics.gia_data).label('avg_gia_data'),
            func.sum(case((AdMetrics.adset_status == 'ACTIVE', 1), else_=0)).label('active_adsets'),
            func.sum(case((AdMetrics.adset_status == 'PAUSED', 1), else_=0)).label('paused_adsets'),
            func.count(distinct(AdMetrics.adset_id)).label('total_adsets')
        ).filter(AdMetrics.account_id.in_(user_account_ids))
        
        # Apply same filters to stats
        if account_id:
            stats_query = stats_query.filter(AdMetrics.account_id == account_id)
        if prefix:
            stats_query = stats_query.filter(AdMetrics.prefix == prefix)
        if campaign_type and campaign_type != 'all':
            stats_query = stats_query.filter(AdMetrics.campaign_type == campaign_type)
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                stats_query = stats_query.filter(func.date(AdMetrics.date) >= date_from_obj)
            except ValueError:
                pass
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                stats_query = stats_query.filter(func.date(AdMetrics.date) <= date_to_obj)
            except ValueError:
                pass
        
        stats_result = stats_query.first()
        
        stats = {
            "totalSpend": float(stats_result.total_spend or 0),
            "totalResults": int(stats_result.total_results or 0),
            "avgGiaData": float(stats_result.avg_gia_data or 0),
            "activeAdsets": int(stats_result.active_adsets or 0),
            "pausedAdsets": int(stats_result.paused_adsets or 0),
            "totalAdsets": int(stats_result.total_adsets or 0)
        }
        
        # Convert ads to dict
        ads_data = []
        for ad in ads:
            ads_data.append({
                "campaign_id": ad.campaign_id,
                "campaign_name": ad.campaign_name,
                "adset_id": ad.adset_id,
                "adset_name": ad.adset_name,
                "ad_id": ad.ad_id,
                "ad_name": ad.ad_name,
                "account_id": ad.account_id,
                "prefix": ad.prefix,
                "adset_status": ad.adset_status,
                "spend": float(ad.spend or 0),
                "results": int(ad.results or 0),
                "gia_data": float(ad.gia_data or 0),
                "impressions": int(ad.impressions or 0),
                "clicks": int(ad.clicks or 0),
                "ctr": float(ad.ctr or 0),
                "cpc": float(ad.cpc or 0),
                "purchases": int(ad.purchases or 0),
                "purchase_value": float(ad.purchase_value or 0),
                "daily_budget": float(ad.amount_spent or 0)  # Using amount_spent as budget placeholder
            })
        
        return JSONResponse({
            "ads": ads_data,
            "total": total,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error in dashboard_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
    """Get Overview Cards summary based on view mode and date range"""
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
        
        # Build date filter
        end_date = datetime.now(HCM_TZ).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        if date_from:
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
                start_date = HCM_TZ.localize(start_date)
            except ValueError:
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date_to:
            try:
                end_date = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
                end_date = HCM_TZ.localize(end_date)
            except ValueError:
                pass
        
        # Build query
        query = db.query(AdMetrics).filter(
            AdMetrics.account_id.in_(user_account_ids),
            func.date(AdMetrics.date) >= start_date.date(),
            func.date(AdMetrics.date) <= end_date.date()
        )
        
        # Apply filters
        if account_id:
            query = query.filter(AdMetrics.account_id == account_id)
        
        if prefix:
            query = query.filter(AdMetrics.adset_name.like(f"{prefix}%"))
        
        # Filter by view mode (campaign type)
        if view_mode == "ecommerce":
            query = query.filter(AdMetrics.campaign_type == "ECOMMERCE")
        elif view_mode == "lead":
            query = query.filter(AdMetrics.campaign_type == "LEAD_GENERATION")
        
        # Aggregate metrics
        metrics = query.all()
        
        # Calculate totals
        total_spend = sum(float(m.spend or 0) for m in metrics)
        total_purchases = sum(int(m.purchases or 0) for m in metrics)
        total_purchase_value = sum(float(m.purchase_value or 0) for m in metrics)
        
        # Calculate leads (comments + messages)
        # Note: AdMetrics may not have comments/messages fields directly
        # We'll use leads field if available, otherwise calculate from results
        total_leads = sum(int(m.leads or m.results or 0) for m in metrics)
        
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
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=500),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get detailed table data for Campaign/Adset/Ad with different columns based on view mode"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get user's enabled accounts and prefixes
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db, enabled_only=True)
        
        if not user_account_ids:
            return JSONResponse({
                "rows": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            })
        
        # Build date filter
        end_date = datetime.now(HCM_TZ).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        if date_from:
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
                start_date = HCM_TZ.localize(start_date)
            except ValueError:
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date_to:
            try:
                end_date = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
                end_date = HCM_TZ.localize(end_date)
            except ValueError:
                pass
        
        # Build base query
        query = db.query(AdMetrics).filter(
            AdMetrics.account_id.in_(user_account_ids),
            func.date(AdMetrics.date) >= start_date.date(),
            func.date(AdMetrics.date) <= end_date.date()
        )
        
        # Apply filters
        if account_id:
            query = query.filter(AdMetrics.account_id == account_id)
        
        if prefix:
            query = query.filter(AdMetrics.adset_name.like(f"{prefix}%"))
        
        # Filter by view mode (campaign type)
        if view_mode == "ecommerce":
            query = query.filter(AdMetrics.campaign_type == "ECOMMERCE")
        elif view_mode == "lead":
            query = query.filter(AdMetrics.campaign_type == "LEAD_GENERATION")
        
        # Status filter
        if status:
            query = query.filter(AdMetrics.adset_status == status)
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    AdMetrics.campaign_name.ilike(search_term),
                    AdMetrics.adset_name.ilike(search_term),
                    AdMetrics.ad_name.ilike(search_term)
                )
            )
        
        # Group by level
        if level == "campaign":
            # Group by campaign
            group_by_fields = [
                AdMetrics.campaign_id,
                AdMetrics.campaign_name,
                AdMetrics.account_id,
                AdMetrics.prefix
            ]
            
            # Aggregate metrics
            query = query.with_entities(
                AdMetrics.campaign_id,
                AdMetrics.campaign_name,
                AdMetrics.account_id,
                AdMetrics.prefix,
                func.sum(AdMetrics.spend).label('spend'),
                func.sum(AdMetrics.results).label('results'),
                func.sum(AdMetrics.impressions).label('impressions'),
                func.sum(AdMetrics.clicks).label('clicks'),
                func.sum(AdMetrics.purchases).label('purchases'),
                func.sum(AdMetrics.purchase_value).label('purchase_value'),
                func.sum(AdMetrics.leads).label('leads'),
                func.avg(AdMetrics.gia_data).label('gia_data'),
                func.avg(AdMetrics.ctr).label('ctr'),
                func.avg(AdMetrics.cpc).label('cpc'),
                func.max(AdMetrics.adset_status).label('status')  # Use max to get status
            ).group_by(*group_by_fields)
            
        elif level == "adset":
            # Group by adset
            group_by_fields = [
                AdMetrics.adset_id,
                AdMetrics.adset_name,
                AdMetrics.campaign_id,
                AdMetrics.campaign_name,
                AdMetrics.account_id,
                AdMetrics.prefix
            ]
            
            query = query.with_entities(
                AdMetrics.adset_id,
                AdMetrics.adset_name,
                AdMetrics.campaign_id,
                AdMetrics.campaign_name,
                AdMetrics.account_id,
                AdMetrics.prefix,
                func.sum(AdMetrics.spend).label('spend'),
                func.sum(AdMetrics.results).label('results'),
                func.sum(AdMetrics.impressions).label('impressions'),
                func.sum(AdMetrics.clicks).label('clicks'),
                func.sum(AdMetrics.purchases).label('purchases'),
                func.sum(AdMetrics.purchase_value).label('purchase_value'),
                func.sum(AdMetrics.leads).label('leads'),
                func.avg(AdMetrics.gia_data).label('gia_data'),
                func.avg(AdMetrics.ctr).label('ctr'),
                func.avg(AdMetrics.cpc).label('cpc'),
                AdMetrics.adset_status.label('status')
            ).group_by(*group_by_fields)
            
        else:  # level == "ad"
            # Individual ads - no grouping needed
            query = query.with_entities(
                AdMetrics.ad_id,
                AdMetrics.ad_name,
                AdMetrics.adset_id,
                AdMetrics.adset_name,
                AdMetrics.campaign_id,
                AdMetrics.campaign_name,
                AdMetrics.account_id,
                AdMetrics.prefix,
                AdMetrics.spend,
                AdMetrics.results,
                AdMetrics.impressions,
                AdMetrics.clicks,
                AdMetrics.purchases,
                AdMetrics.purchase_value,
                AdMetrics.leads,
                AdMetrics.gia_data,
                AdMetrics.ctr,
                AdMetrics.cpc,
                AdMetrics.adset_status.label('status')
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        results = query.offset(offset).limit(page_size).all()
        
        # Convert to dict format
        rows = []
        for row in results:
            if level == "campaign":
                entity_id = row.campaign_id
                entity_name = row.campaign_name
                status = row.status or "UNKNOWN"
            elif level == "adset":
                entity_id = row.adset_id
                entity_name = row.adset_name
                status = row.status or "UNKNOWN"
            else:  # ad
                entity_id = row.ad_id
                entity_name = row.ad_name
                status = row.status or "UNKNOWN"
            
            # Calculate derived metrics
            spend = float(row.spend or 0)
            results_count = int(row.results or 0)
            impressions = int(row.impressions or 0)
            clicks = int(row.clicks or 0)
            purchases = int(row.purchases or 0)
            purchase_value = float(row.purchase_value or 0)
            leads = int(row.leads or 0)
            
            # Calculate metrics
            gia_data = float(row.gia_data or 0) if row.gia_data else (spend / results_count if results_count > 0 else 0)
            cpm = (spend / impressions * 1000) if impressions > 0 else 0
            ctr = float(row.ctr or 0) if row.ctr else ((clicks / impressions * 100) if impressions > 0 else 0)
            cpc = float(row.cpc or 0) if row.cpc else ((spend / clicks) if clicks > 0 else 0)
            
            # Calculate view-mode specific metrics
            if view_mode == "ecommerce":
                ads_percent = (spend / purchase_value * 100) if purchase_value > 0 else 0
                tlc = (purchases / results_count) if results_count > 0 else 0
                checkout_starts = 0  # Not available in AdMetrics, would need to add
            else:  # lead
                cost_per_checkout_start = 0  # Not available in AdMetrics
                checkout_starts = 0  # Not available in AdMetrics
            
            row_data = {
                "id": entity_id,
                "name": entity_name or "-",
                "account_id": row.account_id,
                "prefix": row.prefix or "-",
                "status": status.upper(),
                "spend": round(spend, 2),
                "results": results_count,
                "gia_data": round(gia_data, 2),
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpm": round(cpm, 2),
                "reach": 0,  # Not available in AdMetrics
                "frequency": 0,  # Not available in AdMetrics
            }
            
            if level == "adset" or level == "ad":
                row_data["campaign_id"] = row.campaign_id
                row_data["campaign_name"] = row.campaign_name if hasattr(row, 'campaign_name') else "-"
            
            if level == "ad":
                row_data["adset_id"] = row.adset_id
                row_data["adset_name"] = row.adset_name if hasattr(row, 'adset_name') else "-"
            
            if view_mode == "ecommerce":
                row_data.update({
                    "ads_percent": round(ads_percent, 2),
                    "tlc": round(tlc, 2),
                    "checkout_starts": checkout_starts,
                    "purchases": purchases,
                    "purchase_value": round(purchase_value, 2)
                })
            else:  # lead
                row_data.update({
                    "leads": leads,
                    "cost_per_checkout_start": cost_per_checkout_start,
                    "checkout_starts": checkout_starts,
                    "purchases": purchases
                })
            
            rows.append(row_data)
        
        return JSONResponse({
            "rows": rows,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading details: {str(e)}")


@router.get("/data")
async def dashboard_data(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=500),
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    view_type: Optional[str] = Query('adset')
):
    """API endpoint để lấy dữ liệu dashboard"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Lấy account_ids và prefixes của user
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db)
        
        if not user_account_ids:
            return JSONResponse({
                "ads": [],
                "total": 0,
                "stats": {
                    "totalSpend": 0,
                    "totalResults": 0,
                    "avgGiaData": 0,
                    "activeAdsets": 0,
                    "pausedAdsets": 0,
                    "totalAdsets": 0
                }
            })
        
        # Build query
        query = db.query(AdMetrics).filter(AdMetrics.account_id.in_(user_account_ids))
        
        # Apply filters
        if account_id:
            query = query.filter(AdMetrics.account_id == account_id)
        
        if prefix:
            query = query.filter(AdMetrics.prefix == prefix)
        
        if campaign_type and campaign_type != 'all':
            query = query.filter(AdMetrics.campaign_type == campaign_type)
        
        if status:
            query = query.filter(AdMetrics.adset_status == status)
        
        # Date filter
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(func.date(AdMetrics.date) >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(func.date(AdMetrics.date) <= date_to_obj)
            except ValueError:
                pass
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    AdMetrics.campaign_name.ilike(search_term),
                    AdMetrics.adset_name.ilike(search_term),
                    AdMetrics.ad_name.ilike(search_term)
                )
            )
        
        # Get total count
        total_query = query
        total = total_query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        ads = query.offset(offset).limit(page_size).all()
        
        # Calculate stats
        stats_query = db.query(
            func.sum(AdMetrics.spend).label('total_spend'),
            func.sum(AdMetrics.results).label('total_results'),
            func.avg(AdMetrics.gia_data).label('avg_gia_data'),
            func.sum(case((AdMetrics.adset_status == 'ACTIVE', 1), else_=0)).label('active_adsets'),
            func.sum(case((AdMetrics.adset_status == 'PAUSED', 1), else_=0)).label('paused_adsets'),
            func.count(distinct(AdMetrics.adset_id)).label('total_adsets')
        ).filter(AdMetrics.account_id.in_(user_account_ids))
        
        # Apply same filters to stats
        if account_id:
            stats_query = stats_query.filter(AdMetrics.account_id == account_id)
        if prefix:
            stats_query = stats_query.filter(AdMetrics.prefix == prefix)
        if campaign_type and campaign_type != 'all':
            stats_query = stats_query.filter(AdMetrics.campaign_type == campaign_type)
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                stats_query = stats_query.filter(func.date(AdMetrics.date) >= date_from_obj)
            except ValueError:
                pass
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                stats_query = stats_query.filter(func.date(AdMetrics.date) <= date_to_obj)
            except ValueError:
                pass
        
        stats_result = stats_query.first()
        
        stats = {
            "totalSpend": float(stats_result.total_spend or 0),
            "totalResults": int(stats_result.total_results or 0),
            "avgGiaData": float(stats_result.avg_gia_data or 0),
            "activeAdsets": int(stats_result.active_adsets or 0),
            "pausedAdsets": int(stats_result.paused_adsets or 0),
            "totalAdsets": int(stats_result.total_adsets or 0)
        }
        
        # Convert ads to dict
        ads_data = []
        for ad in ads:
            ads_data.append({
                "campaign_id": ad.campaign_id,
                "campaign_name": ad.campaign_name,
                "adset_id": ad.adset_id,
                "adset_name": ad.adset_name,
                "ad_id": ad.ad_id,
                "ad_name": ad.ad_name,
                "account_id": ad.account_id,
                "prefix": ad.prefix,
                "adset_status": ad.adset_status,
                "spend": float(ad.spend or 0),
                "results": int(ad.results or 0),
                "gia_data": float(ad.gia_data or 0),
                "impressions": int(ad.impressions or 0),
                "clicks": int(ad.clicks or 0),
                "ctr": float(ad.ctr or 0),
                "cpc": float(ad.cpc or 0),
                "purchases": int(ad.purchases or 0),
                "purchase_value": float(ad.purchase_value or 0),
                "daily_budget": float(ad.amount_spent or 0)  # Using amount_spent as budget placeholder
            })
        
        return JSONResponse({
            "ads": ads_data,
            "total": total,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error in dashboard_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Action endpoints for dashboard operations
@router.post("/action/pause/{entity_id}")
async def pause_entity(
    entity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Pause an adset/campaign"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Here you would implement the actual pause logic using Facebook API
    # For now, return success
    return JSONResponse({"success": True, "message": "Paused successfully"})


@router.post("/action/activate/{entity_id}")
async def activate_entity(
    entity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Activate an adset/campaign"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Here you would implement the actual activate logic using Facebook API
    # For now, return success
    return JSONResponse({"success": True, "message": "Activated successfully"})


@router.post("/action/increase-budget/{entity_id}")
async def increase_budget(
    entity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Increase budget by 20%"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Here you would implement the actual budget increase logic using Facebook API
    # For now, return success
    return JSONResponse({"success": True, "message": "Budget increased successfully"})


@router.post("/action/decrease-budget/{entity_id}")
async def decrease_budget(
    entity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Decrease budget by 20%"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Here you would implement the actual budget decrease logic using Facebook API
    # For now, return success
    return JSONResponse({"success": True, "message": "Budget decreased successfully"})


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
    """Get Overview Cards summary based on view mode and date range"""
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
        
        # Build date filter
        end_date = datetime.now(HCM_TZ).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        if date_from:
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
                start_date = HCM_TZ.localize(start_date)
            except ValueError:
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date_to:
            try:
                end_date = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
                end_date = HCM_TZ.localize(end_date)
            except ValueError:
                pass
        
        # Build query
        query = db.query(AdMetrics).filter(
            AdMetrics.account_id.in_(user_account_ids),
            func.date(AdMetrics.date) >= start_date.date(),
            func.date(AdMetrics.date) <= end_date.date()
        )
        
        # Apply filters
        if account_id:
            query = query.filter(AdMetrics.account_id == account_id)
        
        if prefix:
            query = query.filter(AdMetrics.adset_name.like(f"{prefix}%"))
        
        # Filter by view mode (campaign type)
        if view_mode == "ecommerce":
            query = query.filter(AdMetrics.campaign_type == "ECOMMERCE")
        elif view_mode == "lead":
            query = query.filter(AdMetrics.campaign_type == "LEAD_GENERATION")
        
        # Aggregate metrics
        metrics = query.all()
        
        # Calculate totals
        total_spend = sum(float(m.spend or 0) for m in metrics)
        total_purchases = sum(int(m.purchases or 0) for m in metrics)
        total_purchase_value = sum(float(m.purchase_value or 0) for m in metrics)
        
        # Calculate leads (comments + messages)
        # Note: AdMetrics may not have comments/messages fields directly
        # We'll use leads field if available, otherwise calculate from results
        total_leads = sum(int(m.leads or m.results or 0) for m in metrics)
        
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