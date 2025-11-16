"""
Dashboard API Routes - Tổng quan hiệu suất và thống kê quảng cáo
Hiển thị dữ liệu theo E-commerce và Lead Generation
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


@router.get("/", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Trang Dashboard - Tổng quan hiệu suất quảng cáo"""
    logger.info("Dashboard page accessed")
    
    try:
        logger.info(f"Current user: {current_user.username if current_user else 'None'}")
        if not current_user:
            return HTMLResponse(content="""
            <script>
                window.location.href = '/auth/login';
            </script>
            """)
        
        if not current_user.is_active:
            return HTMLResponse(content=get_account_locked_message())
        
        # Tạo HTML với date picker giống Facebook và UI đẹp
        html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - Facebook Ads Automation</title>
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            html {{
                width: 100%;
                height: 100%;
                scroll-behavior: smooth;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                color: #1e293b;
                line-height: 1.6;
                width: 100%;
                min-height: 100vh;
                margin: 0;
                padding: 0;
                position: relative;
                overflow-x: hidden;
            }}
            
            @keyframes gradientShift {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            body::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 40% 20%, rgba(120, 200, 255, 0.3) 0%, transparent 50%);
                pointer-events: none;
                z-index: 0;
            }}
            
            .header {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.3);
                padding: 16px 32px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                z-index: 100;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            }}
            
            .header-left {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}
            
            .btn-home {{
                padding: 8px 16px;
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                color: #64748b;
                cursor: pointer;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 6px;
                transition: all 0.3s ease;
                text-decoration: none;
                font-size: 14px;
            }}
            
            .btn-home:hover {{
                background: #f3f4f6;
                border-color: #667eea;
                color: #667eea;
            }}
            
            .header h1 {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
                margin: 0;
            }}
            
            .header-actions {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .search-box {{
                position: relative;
                margin-bottom: 16px;
            }}
            
            .search-box input {{
                width: 100%;
                padding: 12px 16px 12px 44px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
                transition: all 0.3s ease;
                background: white;
            }}
            
            .search-box input:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            }}
            
            .search-box .search-icon {{
                position: absolute;
                left: 16px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 18px;
                pointer-events: none;
                z-index: 1;
            }}
            
            .quick-filters {{
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                margin-bottom: 16px;
            }}
            
            .quick-filter-btn {{
                padding: 8px 16px;
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .quick-filter-btn:hover {{
                border-color: #667eea;
                color: #667eea;
                transform: translateY(-2px);
            }}
            
            .quick-filter-btn.active {{
                background: #667eea;
                border-color: #667eea;
                color: white;
            }}
            
            .btn-refresh {{
                padding: 10px 20px;
                background: #667eea;
                border: none;
                border-radius: 8px;
                color: white;
                cursor: pointer;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
            }}
            
            .btn-refresh:hover {{
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }}
            
            .btn-refresh.loading {{
                opacity: 0.7;
                cursor: not-allowed;
                transform: none;
            }}
            
            .btn-refresh.loading::after {{
                content: '';
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }}
            
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateX(-20px); }}
                to {{ opacity: 1; transform: translateX(0); }}
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            
            @keyframes slideInRight {{
                from {{ transform: translateX(100%); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
            
            @keyframes slideOutRight {{
                from {{ transform: translateX(0); opacity: 1; }}
                to {{ transform: translateX(100%); opacity: 0; }}
            }}
            
            .container {{
                max-width: 1800px;
                width: 100%;
                margin: 0 auto;
                padding: 24px;
                box-sizing: border-box;
                position: relative;
                z-index: 1;
                animation: fadeIn 0.5s ease-out;
            }}
            
            /* Sticky Filter Bar - GỌN, NHẸ, GIỐNG FACEBOOK ADS MANAGER */
            .sticky-filter-bar {{
                position: sticky;
                top: 70px;
                z-index: 20;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-bottom: 1px solid #e2e8f0;
                padding: 12px 20px;
                margin-bottom: 16px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
                display: block !important;
            }}
            
            .filter-bar-row {{
                display: flex;
                gap: 12px;
                align-items: center;
                margin-bottom: 8px;
                flex-wrap: wrap;
            }}
            
            .filter-bar-row:last-child {{
                margin-bottom: 0;
            }}
            
            .search-box-filter {{
                position: relative;
                flex: 1;
                min-width: 250px;
                max-width: 400px;
            }}
            
            .search-box-filter .search-icon {{
                position: absolute;
                left: 10px;
                top: 50%;
                transform: translateY(-50%);
                color: #9ca3af;
                font-size: 14px;
            }}
            
            .search-box-filter input {{
                width: 100%;
                padding: 8px 12px 8px 36px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 13px;
                transition: all 0.2s ease;
                background: #f9fafb;
                height: 36px;
            }}
            
            .search-box-filter input:focus {{
                background: white;
                border-color: #667eea;
                box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
                outline: none;
            }}
            
            .filter-group-inline {{
                display: flex;
                flex-direction: column;
                min-width: 140px;
            }}
            
            .filter-group-inline label {{
                font-size: 11px;
                font-weight: 500;
                color: #6b7280;
                margin-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .filter-group-inline select {{
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 13px;
                background: white;
                transition: all 0.2s ease;
                height: 32px;
                cursor: pointer;
            }}
            
            .filter-group-inline select:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
            }}
            
            .date-picker-btn-inline {{
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 13px;
                background: white;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.2s ease;
                height: 32px;
                min-width: 180px;
            }}
            
            .date-picker-btn-inline:hover {{
                border-color: #667eea;
            }}
            
            .quick-filters-inline {{
                display: flex;
                gap: 6px;
                flex-wrap: wrap;
                width: 100%;
            }}
            
            .quick-filter-btn {{
                padding: 6px 12px;
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                color: #374151;
                cursor: pointer;
                transition: all 0.2s ease;
                height: 28px;
            }}
            
            .quick-filter-btn:hover {{
                border-color: #667eea;
                color: #667eea;
                background: #f3f4f6;
            }}
            
            .quick-filter-btn.active {{
                background: #667eea;
                border-color: #667eea;
                color: white;
            }}
            
            @media (max-width: 1024px) {{
                .sticky-filter-bar {{
                    position: relative;
                    top: 0;
                }}
                
                .filter-bar-row {{
                    flex-direction: column;
                    align-items: stretch;
                }}
                
                .search-box-filter {{
                    max-width: 100%;
                }}
                
                .filter-group-inline {{
                    width: 100%;
                }}
            }}
            
            .filters-section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
                padding: 32px;
                margin-bottom: 32px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                width: 100%;
                box-sizing: border-box;
                animation: slideIn 0.4s ease-out;
            }}
            
            .filters-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 16px;
                border-bottom: 2px solid #e2e8f0;
            }}
            
            .filters-header h2 {{
                font-size: 18px;
                font-weight: 700;
                color: #1e293b;
            }}
            
            .filter-actions {{
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin-top: 20px;
            }}
            
            .btn-apply {{
                width: 100%;
                padding: 12px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .btn-apply:hover {{
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }}
            
            .btn-reset {{
                width: 100%;
                padding: 12px;
                background: transparent;
                color: #64748b;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .btn-reset:hover {{
                border-color: #cbd5e1;
                background: #f8fafc;
            }}
            
            .filters-grid {{
                display: flex;
                flex-direction: column;
                gap: 16px;
                margin-bottom: 20px;
                width: 100%;
            }}
            
            .filter-group {{
                display: flex;
                flex-direction: column;
            }}
            
            .filter-group label {{
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
                margin-bottom: 6px;
            }}
            
            .filter-group select,
            .filter-group input {{
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                background: white;
            }}
            
            .filter-group select:hover,
            .filter-group input:hover {{
                border-color: #cbd5e1;
            }}
            
            .filter-group select:focus,
            .filter-group input:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
                transform: translateY(-1px);
            }}
            
            .date-picker-wrapper {{
                position: relative;
            }}
            
            .date-picker-btn {{
                width: 100%;
                padding: 10px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background: white;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .date-picker-btn:hover {{
                border-color: #667eea;
            }}
            
            .date-picker-modal {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }}
            
            .date-picker-modal.active {{
                display: flex;
            }}
            
            .date-picker-content {{
                background: white;
                border-radius: 12px;
                padding: 0;
                width: 90%;
                max-width: 800px;
                max-height: 90vh;
                overflow: hidden;
                display: flex;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            
            .date-picker-sidebar {{
                width: 240px;
                padding: 20px;
                border-right: 1px solid #e2e8f0;
                overflow-y: auto;
            }}
            
            .date-picker-sidebar h3 {{
                font-size: 14px;
                font-weight: 600;
                color: #64748b;
                margin-bottom: 12px;
            }}
            
            .date-option {{
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
                margin-bottom: 4px;
                font-size: 14px;
                transition: background 0.2s;
            }}
            
            .date-option:hover {{
                background: #f1f5f9;
            }}
            
            .date-option.selected {{
                background: #667eea;
                color: white;
            }}
            
            .date-picker-main {{
                flex: 1;
                padding: 24px;
                overflow-y: auto;
            }}
            
            .date-picker-calendars {{
                display: flex;
                gap: 24px;
                margin-bottom: 20px;
            }}
            
            .calendar {{
                flex: 1;
            }}
            
            .calendar-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }}
            
            .calendar-header select {{
                padding: 4px 8px;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                font-size: 14px;
            }}
            
            .calendar-nav {{
                display: flex;
                gap: 12px;
                align-items: center;
            }}
            
            .calendar-nav button {{
                padding: 4px 8px;
                border: none;
                background: #f1f5f9;
                border-radius: 4px;
                cursor: pointer;
                font-size: 18px;
            }}
            
            .calendar-nav button:hover {{
                background: #e2e8f0;
            }}
            
            .calendar-grid {{
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 4px;
            }}
            
            .calendar-day-header {{
                text-align: center;
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
                padding: 8px;
            }}
            
            .calendar-day {{
                text-align: center;
                padding: 8px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }}
            
            .calendar-day:hover {{
                background: #f1f5f9;
            }}
            
            .calendar-day.selected {{
                background: #667eea;
                color: white;
            }}
            
            .calendar-day.other-month {{
                color: #cbd5e1;
            }}
            
            .date-picker-footer {{
                padding: 16px 24px;
                border-top: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .date-picker-footer .timezone-note {{
                font-size: 12px;
                color: #64748b;
            }}
            
            .date-picker-footer .actions {{
                display: flex;
                gap: 12px;
            }}
            
            .btn {{
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                border: none;
                transition: all 0.2s;
            }}
            
            .btn-secondary {{
                background: #e2e8f0;
                color: #475569;
            }}
            
            .btn-secondary:hover {{
                background: #cbd5e1;
            }}
            
            .btn-primary {{
                background: #667eea;
                color: white;
            }}
            
            .btn-primary:hover {{
                background: #5568d3;
            }}
            
            .table-container {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                overflow: hidden;
                width: 100%;
                animation: fadeIn 0.7s ease-out;
            }}
            
            .table-header {{
                padding: 24px 32px;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: transparent;
            }}
            
            .table-header h2 {{
                font-size: 20px;
                font-weight: 700;
                color: #1e293b;
                margin: 0;
            }}
            
            .view-type-tabs {{
                display: flex;
                gap: 4px;
                background: #f3f4f6;
                padding: 4px;
                border-radius: 8px;
            }}
            
            .view-type-tab {{
                padding: 6px 12px;
                background: transparent;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .view-type-tab:hover {{
                background: rgba(102, 126, 234, 0.1);
                color: #667eea;
            }}
            
            .view-type-tab.active {{
                background: #667eea;
                color: white;
            }}
            
            .table-header-actions {{
                display: flex;
                gap: 12px;
                align-items: center;
            }}
            
            .btn-export {{
                padding: 8px 16px;
                background: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            
            .btn-export:hover {{
                background: #059669;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            }}
            
            .table-wrapper {{
                overflow-x: auto;
                width: 100%;
                -webkit-overflow-scrolling: touch;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th, td {{
                padding: 12px 16px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
                font-size: 13px;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}
            
            th {{
                background: #f8fafc;
                font-weight: 600;
                color: #475569;
                position: sticky;
                top: 0;
                z-index: 10;
                font-size: 12px;
                text-transform: uppercase;
                cursor: pointer;
                user-select: none;
                white-space: nowrap;
            }}
            
            th:hover {{
                background: #f1f5f9;
            }}
            
            th.sortable::after {{
                content: ' ↕️';
                font-size: 10px;
                opacity: 0.5;
                margin-left: 4px;
            }}
            
            th.sort-asc::after {{
                content: ' ↑';
                opacity: 1;
            }}
            
            th.sort-desc::after {{
                content: ' ↓';
                opacity: 1;
            }}
            
            .number-cell {{
                text-align: right;
            }}
            
            .action-buttons {{
                display: flex;
                gap: 6px;
                align-items: center;
                justify-content: center;
                white-space: nowrap;
            }}
            
            .btn-action {{
                padding: 6px 10px;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-width: 36px;
            }}
            
            .btn-pause {{
                background: #fee2e2;
                color: #991b1b;
            }}
            
            .btn-pause:hover {{
                background: #fecaca;
                transform: translateY(-1px);
            }}
            
            .btn-activate {{
                background: #d1fae5;
                color: #065f46;
            }}
            
            .btn-activate:hover {{
                background: #a7f3d0;
                transform: translateY(-1px);
            }}
            
            .btn-increase {{
                background: #dbeafe;
                color: #1e40af;
            }}
            
            .btn-increase:hover {{
                background: #bfdbfe;
                transform: translateY(-1px);
            }}
            
            .btn-decrease {{
                background: #fef3c7;
                color: #92400e;
            }}
            
            .btn-decrease:hover {{
                background: #fde68a;
                transform: translateY(-1px);
            }}
            
            .btn-action:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }}
            
            .btn-action.loading {{
                position: relative;
                color: transparent;
            }}
            
            .btn-action.loading::after {{
                content: '';
                position: absolute;
                width: 14px;
                height: 14px;
                border: 2px solid currentColor;
                border-top-color: transparent;
                border-radius: 50%;
                animation: spin 0.6s linear infinite;
            }}
            
            tbody tr {{
                transition: all 0.2s ease;
            }}
            
            tbody tr:hover {{
                background: #f8fafc;
                transform: scale(1.01);
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            
            .status-badge {{
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }}
            
            .status-active {{
                background: #d1fae5;
                color: #065f46;
            }}
            
            .status-paused {{
                background: #fee2e2;
                color: #991b1b;
            }}
            
            /* Toggle Switch cho Adset Status */
            .toggle-switch {{
                position: relative;
                display: inline-block;
                width: 44px;
                height: 24px;
            }}
            
            .toggle-switch input {{
                opacity: 0;
                width: 0;
                height: 0;
            }}
            
            .toggle-slider {{
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #cbd5e1;
                transition: 0.3s;
                border-radius: 24px;
            }}
            
            .toggle-slider:before {{
                position: absolute;
                content: "";
                height: 18px;
                width: 18px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: 0.3s;
                border-radius: 50%;
            }}
            
            .toggle-switch input:checked + .toggle-slider {{
                background-color: #10b981;
            }}
            
            .toggle-switch input:checked + .toggle-slider:before {{
                transform: translateX(20px);
            }}
            
            .toggle-switch input:disabled + .toggle-slider {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            /* Budget Editor */
            .budget-cell {{
                position: relative;
            }}
            
            .budget-display {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .budget-display:hover {{
                background: #f3f4f6;
            }}
            
            .budget-value {{
                font-size: 13px;
                color: #374151;
            }}
            
            .budget-edit-icon {{
                font-size: 12px;
                opacity: 0;
                transition: opacity 0.2s ease;
                margin-left: 6px;
            }}
            
            .budget-display:hover .budget-edit-icon {{
                opacity: 1;
            }}
            
            .budget-editor-popover {{
                position: absolute;
                top: 100%;
                left: 0;
                z-index: 100;
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                min-width: 280px;
                margin-top: 4px;
            }}
            
            .budget-editor-popover h4 {{
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 12px;
                color: #1e293b;
            }}
            
            .budget-input-group {{
                margin-bottom: 12px;
            }}
            
            .budget-input-group label {{
                display: block;
                font-size: 12px;
                color: #64748b;
                margin-bottom: 6px;
            }}
            
            .budget-input-group input {{
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
            }}
            
            .budget-shortcuts {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
                margin-bottom: 12px;
            }}
            
            .budget-shortcut-btn {{
                padding: 8px 12px;
                background: #f3f4f6;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .budget-shortcut-btn:hover {{
                background: #e5e7eb;
                border-color: #667eea;
            }}
            
            .budget-actions {{
                display: flex;
                gap: 8px;
            }}
            
            .budget-btn {{
                flex: 1;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .budget-btn-primary {{
                background: #667eea;
                color: white;
            }}
            
            .budget-btn-primary:hover {{
                background: #5568d3;
            }}
            
            .budget-btn-secondary {{
                background: #f3f4f6;
                color: #374151;
            }}
            
            .budget-btn-secondary:hover {{
                background: #e5e7eb;
            }}
            
            .alert-badge {{
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                background: #fef3c7;
                color: #92400e;
            }}
            
            .pagination {{
                padding: 20px 24px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 8px;
                border-top: 1px solid #e2e8f0;
            }}
            
            .pagination button {{
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                background: white;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }}
            
            .pagination button:hover:not(:disabled) {{
                background: #f1f5f9;
            }}
            
            .pagination button.active {{
                background: #667eea;
                color: white;
                border-color: #667eea;
            }}
            
            .pagination button:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            .loading {{
                text-align: center;
                padding: 80px 20px;
                color: #64748b;
            }}
            
            /* Improved Skeleton Loading */
            .loading-skeleton {{
                padding: 20px;
            }}
            
            .skeleton-header {{
                display: flex;
                gap: 16px;
                margin-bottom: 16px;
                padding-bottom: 16px;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            .skeleton-line {{
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: skeleton-loading 1.5s ease-in-out infinite;
                border-radius: 4px;
            }}
            
            .skeleton-row {{
                display: flex;
                gap: 12px;
                padding: 12px 0;
                border-bottom: 1px solid #f3f4f6;
            }}
            
            .skeleton-item {{
                height: 16px;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: skeleton-loading 1.5s ease-in-out infinite;
                border-radius: 4px;
                flex-shrink: 0;
            }}
            
            @keyframes skeleton-loading {{
                0% {{
                    background-position: 200% 0;
                }}
                100% {{
                    background-position: -200% 0;
                }}
            }}
            
            /* Improved Empty State */
            .empty-state {{
                text-align: center;
                padding: 80px 20px;
                color: #64748b;
                width: 100%;
                animation: fadeIn 0.5s ease-out;
            }}
            
            .empty-icon {{
                font-size: 72px;
                margin-bottom: 24px;
                opacity: 0.6;
                animation: pulse 2s ease-in-out infinite;
            }}
            
            .empty-state h3 {{
                font-size: 24px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 12px;
            }}
            
            .empty-message {{
                font-size: 16px;
                color: #64748b;
                margin-bottom: 32px;
            }}
            
            .empty-suggestions {{
                text-align: left;
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
                padding: 24px;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            }}
            
            .suggestion-item {{
                padding: 8px 0;
                font-size: 14px;
                color: #475569;
                line-height: 1.6;
            }}
            
            .suggestion-item:first-child {{
                font-size: 15px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 8px;
                padding-bottom: 12px;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 24px;
                margin-bottom: 32px;
                width: 100%;
            }}
            
            .stat-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                animation: fadeIn 0.6s ease-out;
                display: flex;
                flex-direction: column;
            }}
            
            .stat-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #667eea, #764ba2);
                transform: scaleX(0);
                transition: transform 0.3s ease;
            }}
            
            .stat-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
            }}
            
            .stat-card:hover::before {{
                transform: scaleX(1);
            }}
            
            .stat-card-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 16px;
            }}
            
            .stat-card-icon {{
                font-size: 32px;
                opacity: 0.8;
            }}
            
            .stat-card .label {{
                font-size: 13px;
                color: #64748b;
                margin-bottom: 8px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stat-card .value {{
                font-size: 32px;
                font-weight: 700;
                color: #1e293b;
                transition: all 0.3s ease;
                line-height: 1.2;
            }}
            
            .stat-card .subtext {{
                font-size: 12px;
                color: #94a3b8;
                margin-top: 8px;
            }}
            
            .stat-card:hover .value {{
                color: #667eea;
            }}
            
            .charts-section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
                padding: 32px;
                margin-bottom: 32px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                animation: fadeIn 0.7s ease-out;
            }}
            
            .charts-header {{
                margin-bottom: 24px;
            }}
            
            .charts-header h2 {{
                font-size: 20px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 8px;
            }}
            
            .charts-header p {{
                font-size: 14px;
                color: #64748b;
            }}
            
            .charts-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 24px;
            }}
            
            .chart-container {{
                background: #f8fafc;
                border-radius: 12px;
                padding: 24px;
                min-height: 300px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #94a3b8;
                font-size: 14px;
            }}
            
            .prefix-summary-section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
                padding: 32px;
                margin-bottom: 32px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                animation: fadeIn 0.7s ease-out;
            }}
            
            .prefix-tabs {{
                display: flex;
                gap: 12px;
                margin-bottom: 24px;
                border-bottom: 2px solid #e2e8f0;
            }}
            
            .prefix-tab {{
                padding: 12px 24px;
                background: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                font-size: 14px;
                font-weight: 600;
                color: #64748b;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: -2px;
            }}
            
            .prefix-tab:hover {{
                color: #667eea;
            }}
            
            .prefix-tab.active {{
                color: #667eea;
                border-bottom-color: #667eea;
            }}
            
            .prefix-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 20px;
            }}
            
            .prefix-card {{
                background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                padding: 20px;
                transition: all 0.3s ease;
            }}
            
            .prefix-card:hover {{
                border-color: #667eea;
                transform: translateY(-4px);
                box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
            }}
            
            .prefix-card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 2px solid #e2e8f0;
            }}
            
            .prefix-card-title {{
                font-size: 20px;
                font-weight: 700;
                color: #1e293b;
            }}
            
            .prefix-card-badge {{
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            
            .badge-ecommerce {{
                background: #dbeafe;
                color: #1e40af;
            }}
            
            .badge-lead {{
                background: #fef3c7;
                color: #92400e;
            }}
            
            .prefix-stats {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }}
            
            .prefix-stat-item {{
                display: flex;
                flex-direction: column;
            }}
            
            .prefix-stat-label {{
                font-size: 11px;
                color: #64748b;
                text-transform: uppercase;
                margin-bottom: 4px;
                font-weight: 600;
            }}
            
            .prefix-stat-value {{
                font-size: 18px;
                font-weight: 700;
                color: #1e293b;
            }}
            
            .mobile-filter-toggle {{
                display: none;
                padding: 12px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                margin-bottom: 16px;
                width: 100%;
            }}
            
            .sidebar-filters.mobile-hidden {{
                display: none;
            }}
            
            /* Responsive Design */
            @media (max-width: 1024px) {{
                .dashboard-layout {{
                    flex-direction: column;
                    padding: 100px 24px 40px;
                }}
                
                .sidebar-filters {{
                    width: 100%;
                    position: static;
                    max-height: none;
                }}
                
                .mobile-filter-toggle {{
                    display: block;
                }}
                
                .sidebar-filters.mobile-hidden {{
                    display: none;
                }}
            }}
            
            @media (max-width: 768px) {{
                .header {{
                    padding: 12px 16px;
                    flex-direction: column;
                    gap: 12px;
                    align-items: flex-start;
                }}
                
                .header h1 {{
                    font-size: 20px;
                }}
                
                .header-actions {{
                    width: 100%;
                    justify-content: flex-end;
                }}
                
                .dashboard-layout {{
                    padding: 100px 16px 40px;
                }}
                
                .filters-section {{
                    padding: 20px;
                }}
                
                .stats-grid {{
                    grid-template-columns: repeat(2, 1fr);
                    gap: 16px;
                }}
                
                .stat-card {{
                    padding: 20px;
                }}
                
                .stat-card .value {{
                    font-size: 24px;
                }}
                
                .charts-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .chart-container {{
                    min-height: 250px;
                }}
                
                .table-header {{
                    flex-direction: column;
                    gap: 12px;
                    align-items: flex-start;
                }}
                
                .table-header-actions {{
                    width: 100%;
                    flex-direction: column;
                    gap: 8px;
                }}
                
                .table-wrapper {{
                    overflow-x: scroll;
                }}
                
                table {{
                    min-width: 1200px;
                }}
                
                .date-picker-content {{
                    flex-direction: column;
                    width: 95%;
                    max-height: 95vh;
                }}
                
                .date-picker-sidebar {{
                    width: 100%;
                    border-right: none;
                    border-bottom: 1px solid #e2e8f0;
                    max-height: 200px;
                }}
                
                .date-picker-calendars {{
                    flex-direction: column;
                }}
                
                .quick-filters {{
                    overflow-x: auto;
                    flex-wrap: nowrap;
                    padding-bottom: 8px;
                }}
                
                .quick-filter-btn {{
                    white-space: nowrap;
                    flex-shrink: 0;
                }}
            }}
            
            @media (max-width: 480px) {{
                .header h1 {{
                    font-size: 18px;
                }}
                
                .btn-refresh {{
                    padding: 8px 12px;
                    font-size: 13px;
                }}
                
                .stat-card .value {{
                    font-size: 24px;
                }}
                
                th, td {{
                    padding: 8px 12px;
                    font-size: 12px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left">
                <a href="/" class="btn-home">← Trang chủ</a>
                <h1>📊 Dashboard – Tổng Quan Hiệu Suất</h1>
            </div>
            <div class="header-actions">
                <button class="btn-refresh" onclick="refreshData()" id="refreshBtn" title="Làm mới dữ liệu">
                    🔄 Làm mới
                </button>
            </div>
        </div>
        
        <div class="dashboard-layout">
            <!-- Sticky Filter Bar - GỌN, NHẸ, GIỐNG FACEBOOK ADS MANAGER -->
            <div class="sticky-filter-bar" id="stickyFilterBar">
                <div class="filter-bar-row">
                    <div class="search-box-filter">
                        <span class="search-icon">🔍</span>
                        <input type="text" id="searchInput" placeholder="Tìm kiếm theo tên adset, campaign, ID..." onkeyup="handleSearch(event)" oninput="handleSearch(event)">
                    </div>
                    <div class="filter-group-inline">
                        <label>Account</label>
                        <select id="accountFilter" onchange="handleFilterChange()">
                            <option value="">Tất cả</option>
                        </select>
                    </div>
                    <div class="filter-group-inline">
                        <label>Prefix</label>
                        <select id="prefixFilter" onchange="handleFilterChange()">
                            <option value="">Tất cả</option>
                        </select>
                    </div>
                    <div class="filter-group-inline">
                        <label>Loại Campaign</label>
                        <select id="campaignTypeFilter" onchange="handleFilterChange()">
                            <option value="">Tất cả</option>
                            <option value="ECOMMERCE">E-commerce</option>
                            <option value="LEAD">Lead Generation</option>
                        </select>
                    </div>
                    <div class="filter-group-inline">
                        <label>Trạng thái</label>
                        <select id="statusFilter" onchange="handleFilterChange()">
                            <option value="">Tất cả</option>
                            <option value="ACTIVE">Đang hoạt động</option>
                            <option value="PAUSED">Đã tắt</option>
                        </select>
                    </div>
                    <div class="filter-group-inline date-picker-wrapper">
                        <label>Khoảng thời gian</label>
                        <div class="date-picker-btn-inline" onclick="openDatePicker()">
                            <span id="dateRangeText">Chọn khoảng thời gian</span>
                            <span>📅</span>
                        </div>
                    </div>
                </div>
                <div class="filter-bar-row">
                    <div class="quick-filters-inline">
                        <button class="quick-filter-btn" onclick="applyQuickFilter('today', this)">Hôm nay</button>
                        <button class="quick-filter-btn" onclick="applyQuickFilter('yesterday', this)">Hôm qua</button>
                        <button class="quick-filter-btn" onclick="applyQuickFilter('last7days', this)">7 ngày qua</button>
                        <button class="quick-filter-btn" onclick="applyQuickFilter('last14days', this)">14 ngày qua</button>
                        <button class="quick-filter-btn" onclick="applyQuickFilter('last30days', this)">30 ngày qua</button>
                        <button class="quick-filter-btn" onclick="applyQuickFilter('thisMonth', this)">Tháng này</button>
                        <button class="quick-filter-btn" onclick="applyQuickFilter('lastMonth', this)">Tháng trước</button>
                    </div>
                </div>
            </div>
            
            <div class="main-content">
                
                <div class="stats-grid" id="statsGrid">
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div>
                                <div class="label">💰 Tổng Chi Tiêu</div>
                                <div class="value" id="totalSpend">0</div>
                                <div class="subtext">Tổng số tiền đã chi</div>
                            </div>
                            <div class="stat-card-icon">💰</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div>
                                <div class="label">📊 Tổng Kết Quả</div>
                                <div class="value" id="totalResults">0</div>
                                <div class="subtext">Tổng số leads/purchases</div>
                            </div>
                            <div class="stat-card-icon">📊</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div>
                                <div class="label">💵 Giá DATA Trung Bình</div>
                                <div class="value" id="avgGiaData">0</div>
                                <div class="subtext">Giá trung bình mỗi data</div>
                            </div>
                            <div class="stat-card-icon">💵</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div>
                                <div class="label">▶️ Adsets Hoạt Động</div>
                                <div class="value" id="activeAdsets">0</div>
                                <div class="subtext">Đang chạy quảng cáo</div>
                            </div>
                            <div class="stat-card-icon">▶️</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div>
                                <div class="label">⏸️ Adsets Đã Tạm Dừng</div>
                                <div class="value" id="pausedAdsets">0</div>
                                <div class="subtext">Đã dừng quảng cáo</div>
                            </div>
                            <div class="stat-card-icon">⏸️</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div>
                                <div class="label">📈 Tổng Adsets</div>
                                <div class="value" id="totalAdsets">0</div>
                                <div class="subtext">Tổng số adsets</div>
                            </div>
                            <div class="stat-card-icon">📈</div>
                        </div>
                    </div>
                </div>
                
                <!-- Chi Tiết Quảng Cáo - Move lên trước Tổng Quan Theo Prefix -->
                <div class="table-container">
                    <div class="table-header">
                        <div style="display: flex; align-items: center; gap: 16px;">
                            <h2>📋 Chi Tiết Quảng Cáo</h2>
                            <!-- View Type Tabs: Campaign / Adset / Ad -->
                            <div class="view-type-tabs" style="display: flex; gap: 4px; background: #f3f4f6; padding: 4px; border-radius: 8px;">
                                <button class="view-type-tab active" onclick="switchViewType('campaign', this)" data-view="campaign">Chiến dịch</button>
                                <button class="view-type-tab" onclick="switchViewType('adset', this)" data-view="adset">Nhóm quảng cáo</button>
                                <button class="view-type-tab" onclick="switchViewType('ad', this)" data-view="ad">Quảng cáo</button>
                            </div>
                        </div>
                        <div class="table-header-actions">
                            <div id="tableInfo" style="font-size: 14px; color: #64748b;">Hiển thị 0 / 0 kết quả</div>
                            <button class="btn-export" onclick="exportData()" id="exportBtn">📥 Xuất Excel</button>
                        </div>
                    </div>
                    <!-- Batch Actions Bar (hidden by default) -->
                    <div id="batchActionsBar" style="display: none; padding: 12px 16px; background: #f3f4f6; border-bottom: 1px solid #e2e8f0; margin-bottom: 0;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span id="selectedCount" style="font-weight: 500; color: #1e293b;">0 mục đã chọn</span>
                            <div style="display: flex; gap: 8px;">
                                <button class="btn-batch-action" onclick="batchAction('pause')" style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">⏸️ Tắt</button>
                                <button class="btn-batch-action" onclick="batchAction('activate')" style="padding: 6px 12px; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">▶️ Bật</button>
                                <button class="btn-batch-action" onclick="batchAction('increase')" style="padding: 6px 12px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">+20% Ngân sách</button>
                                <button class="btn-batch-action" onclick="batchAction('decrease')" style="padding: 6px 12px; background: #f59e0b; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">-20% Ngân sách</button>
                            </div>
                        </div>
                    </div>
                    <div class="table-wrapper" id="tableWrapper">
                        <div class="loading">
                            <div style="font-size: 48px; margin-bottom: 16px;">⏳</div>
                            <div style="font-size: 16px; font-weight: 500;">Đang tải dữ liệu...</div>
                        </div>
                    </div>
                    <div class="pagination" id="pagination"></div>
                </div>
                
                <!-- Tổng Quan Theo Prefix - Move xuống sau Chi Tiết Quảng Cáo -->
                <div class="prefix-summary-section" id="prefixSummarySection">
                    <div class="charts-header">
                        <h2>📊 Tổng Quan Theo Prefix</h2>
                        <p>Thống kê chi tiết cho từng prefix (FL, NM, PX, TL...) - Hỗ trợ cả E-commerce và Lead Generation</p>
                    </div>
                    <div class="prefix-tabs">
                        <button class="prefix-tab active" onclick="switchPrefixTab('all', this)">Tất cả</button>
                        <button class="prefix-tab" onclick="switchPrefixTab('ecommerce', this)">E-commerce</button>
                        <button class="prefix-tab" onclick="switchPrefixTab('lead', this)">Lead Generation</button>
                    </div>
                    <div class="prefix-grid" id="prefixGrid">
                        <div class="loading">Đang tải dữ liệu prefix...</div>
                    </div>
                </div>
                
                <!-- Biểu Đồ Phân Tích - Chỉ 1 section -->
                <div class="charts-section" id="chartsSection">
                    <div class="charts-header">
                        <h2>📈 Biểu Đồ Phân Tích</h2>
                        <p>Tổng quan theo ngày trong khoảng thời gian chọn</p>
                    </div>
                    <div class="charts-grid">
                        <div class="chart-container">
                            <div style="text-align: center;">
                                <div style="font-size: 48px; margin-bottom: 12px;">📈</div>
                                <div>Line Chart: Chi tiêu & Kết quả theo ngày</div>
                                <div style="font-size: 12px; margin-top: 8px; color: #cbd5e1;">(Sẽ tích hợp Chart.js sau)</div>
                            </div>
                        </div>
                        <div class="chart-container">
                            <div style="text-align: center;">
                                <div style="font-size: 48px; margin-bottom: 12px;">📊</div>
                                <div>Bar Chart: Chi tiêu theo Prefix</div>
                                <div style="font-size: 12px; margin-top: 8px; color: #cbd5e1;">(Sẽ tích hợp Chart.js sau)</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Date Picker Modal -->
        <div class="date-picker-modal" id="datePickerModal" onclick="closeDatePickerOnOverlay(event)">
            <div class="date-picker-content" onclick="event.stopPropagation()">
                <div class="date-picker-sidebar">
                    <h3>Đã dùng mới đây</h3>
                    <div class="date-option" onclick="selectQuickDate('today')">Hôm nay</div>
                    <div class="date-option" onclick="selectQuickDate('yesterday')">Hôm qua</div>
                    <div class="date-option" onclick="selectQuickDate('last7days')">7 ngày qua</div>
                    <div class="date-option" onclick="selectQuickDate('last14days')">14 ngày qua</div>
                    <div class="date-option" onclick="selectQuickDate('last30days')">30 ngày qua</div>
                    <div class="date-option" onclick="selectQuickDate('thisMonth')">Tháng này</div>
                    <div class="date-option" onclick="selectQuickDate('lastMonth')">Tháng trước</div>
                </div>
                <div class="date-picker-main">
                    <div class="date-picker-calendars" id="calendarsContainer"></div>
                    <div class="date-picker-footer">
                        <div class="timezone-note">Ngày hiển thị theo Giờ TP Hồ Chí Minh</div>
                        <div class="actions">
                            <button class="btn btn-secondary" onclick="closeDatePicker()">Hủy</button>
                            <button class="btn btn-primary" onclick="applyDateRange()">Cập nhật</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let currentPage = 1;
            const pageSize = 50;
            let selectedDateRange = {{ start: null, end: null }};
            let currentFilters = {{
                account: '',
                prefix: '',
                campaignType: '',
                status: '',
                dateFrom: '',
                dateTo: ''
            }};
            
            // Date Picker Logic
            function openDatePicker() {{
                document.getElementById('datePickerModal').classList.add('active');
                renderCalendars();
            }}
            
            function closeDatePicker() {{
                document.getElementById('datePickerModal').classList.remove('active');
            }}
            
            function closeDatePickerOnOverlay(event) {{
                if (event.target.id === 'datePickerModal') {{
                    closeDatePicker();
                }}
            }}
            
            // Get today in Asia/Ho_Chi_Minh timezone
            function getTodayVN() {{
                const now = new Date();
                // Convert to VN timezone (UTC+7)
                const vnTime = new Date(now.toLocaleString('en-US', {{ timeZone: 'Asia/Ho_Chi_Minh' }}));
                return new Date(vnTime.getFullYear(), vnTime.getMonth(), vnTime.getDate());
            }}
            
            function selectQuickDate(type) {{
                const today = getTodayVN();
                let start, end;
                
                switch(type) {{
                    case 'today':
                        // Hôm nay: since = today 00:00, until = today 23:59:59
                        start = new Date(today);
                        end = new Date(today);
                        end.setHours(23, 59, 59, 999);
                        break;
                    case 'yesterday':
                        // Hôm qua: today - 1 day
                        start = new Date(today);
                        start.setDate(start.getDate() - 1);
                        end = new Date(start);
                        end.setHours(23, 59, 59, 999);
                        break;
                    case 'last7days':
                        // 7 ngày qua: today - 6 → today (bao gồm hôm nay)
                        start = new Date(today);
                        start.setDate(start.getDate() - 6);
                        end = new Date(today);
                        end.setHours(23, 59, 59, 999);
                        break;
                    case 'last14days':
                        // 14 ngày qua: today - 13 → today
                        start = new Date(today);
                        start.setDate(start.getDate() - 13);
                        end = new Date(today);
                        end.setHours(23, 59, 59, 999);
                        break;
                    case 'last30days':
                        // 30 ngày qua: today - 29 → today
                        start = new Date(today);
                        start.setDate(start.getDate() - 29);
                        end = new Date(today);
                        end.setHours(23, 59, 59, 999);
                        break;
                    case 'thisMonth':
                        // Tháng này: từ ngày 1 đến hôm nay
                        start = new Date(today.getFullYear(), today.getMonth(), 1);
                        end = new Date(today);
                        end.setHours(23, 59, 59, 999);
                        break;
                    case 'lastMonth':
                        // Tháng trước: full tháng trước
                        start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                        end = new Date(today.getFullYear(), today.getMonth(), 0);
                        end.setHours(23, 59, 59, 999);
                        break;
                }}
                
                selectedDateRange.start = start;
                selectedDateRange.end = end;
                currentFilters.datePreset = type;
                renderCalendars();
                applyDateRange();
            }}
            
            function renderCalendars() {{
                const container = document.getElementById('calendarsContainer');
                const startMonth = new Date(currentCalendarYear, currentCalendarMonth, 1);
                const endMonth = new Date(currentCalendarYear, currentCalendarMonth + 1, 1);
                
                container.innerHTML = renderCalendar(startMonth) + renderCalendar(endMonth);
            }}
            
            function renderCalendar(date) {{
                const year = date.getFullYear();
                const month = date.getMonth();
                const firstDay = new Date(year, month, 1);
                const lastDay = new Date(year, month + 1, 0);
                const daysInMonth = lastDay.getDate();
                const startingDayOfWeek = firstDay.getDay();
                
                let html = `
                    <div class="calendar">
                        <div class="calendar-header">
                            <div class="calendar-nav">
                                <button onclick="changeMonth(-1)">‹</button>
                                <select onchange="changeMonthBySelect(this.value)">
                                    ` + Array.from({length: 12}, (_, i) => `
                                        <option value="` + i + `" ` + (i === month ? 'selected' : '') + `>
                                            Tháng ` + (i + 1) + `
                                        </option>
                                    `).join('') + `
                                </select>
                                <select onchange="changeYearBySelect(this.value)">
                                    ` + Array.from({length: 10}, (_, i) => year - 5 + i).map(y => `
                                        <option value="` + y + `" ` + (y === year ? 'selected' : '') + `>` + y + `</option>
                                    `).join('') + `
                                </select>
                            </div>
                            <div class="calendar-nav">
                                <button onclick="changeMonth(1)">›</button>
                            </div>
                        </div>
                        <div class="calendar-grid">
                            <div class="calendar-day-header">CN</div>
                            <div class="calendar-day-header">T2</div>
                            <div class="calendar-day-header">T3</div>
                            <div class="calendar-day-header">T4</div>
                            <div class="calendar-day-header">T5</div>
                            <div class="calendar-day-header">T6</div>
                            <div class="calendar-day-header">T7</div>
                `;
                
                // Empty cells for days before month starts
                for (let i = 0; i < startingDayOfWeek; i++) {{
                    html += '<div class="calendar-day other-month"></div>';
                }}
                
                // Days of the month
                for (let day = 1; day <= daysInMonth; day++) {{
                    const dayDate = new Date(year, month, day);
                    const isSelected = selectedDateRange.start && selectedDateRange.end &&
                        dayDate >= selectedDateRange.start && dayDate <= selectedDateRange.end;
                    const isStart = selectedDateRange.start && 
                        dayDate.toDateString() === selectedDateRange.start.toDateString();
                    const isEnd = selectedDateRange.end && 
                        dayDate.toDateString() === selectedDateRange.end.toDateString();
                    
                    html += '<div class="calendar-day ' + (isSelected ? 'selected' : '') + '" onclick="selectDate(' + year + ', ' + month + ', ' + day + ')">' + day + '</div>';
                }}
                
                html += '</div></div>';
                return html;
            }}
            
            function selectDate(year, month, day) {{
                const date = new Date(year, month, day);
                if (!selectedDateRange.start || (selectedDateRange.start && selectedDateRange.end)) {{
                    selectedDateRange.start = date;
                    selectedDateRange.end = null;
                }} else if (date < selectedDateRange.start) {{
                    selectedDateRange.end = selectedDateRange.start;
                    selectedDateRange.start = date;
                }} else {{
                    selectedDateRange.end = date;
                }}
                renderCalendars();
            }}
            
            let currentCalendarMonth = new Date().getMonth();
            let currentCalendarYear = new Date().getFullYear();
            
            function changeMonth(delta) {{
                currentCalendarMonth += delta;
                if (currentCalendarMonth < 0) {{
                    currentCalendarMonth = 11;
                    currentCalendarYear--;
                }} else if (currentCalendarMonth > 11) {{
                    currentCalendarMonth = 0;
                    currentCalendarYear++;
                }}
                renderCalendars();
            }}
            
            function changeMonthBySelect(monthIndex) {{
                currentCalendarMonth = parseInt(monthIndex);
                renderCalendars();
            }}
            
            function changeYearBySelect(yearValue) {{
                currentCalendarYear = parseInt(yearValue);
                renderCalendars();
            }}
            
            // LocalStorage key for filter state
            const FILTER_STORAGE_KEY = 'meta_dashboard_filters';
            
            // Load filter state from localStorage
            function loadFilterState() {{
                try {{
                    const saved = localStorage.getItem(FILTER_STORAGE_KEY);
                    if (saved) {{
                        const savedFilters = JSON.parse(saved);
                        
                        // Restore account and prefix
                        if (savedFilters.account) {{
                            currentFilters.account = savedFilters.account;
                            setTimeout(() => {{
                                const accountFilter = document.getElementById('accountFilter');
                                if (accountFilter) accountFilter.value = savedFilters.account;
                            }}, 500);
                        }}
                        
                        if (savedFilters.prefix) {{
                            currentFilters.prefix = savedFilters.prefix;
                            setTimeout(() => {{
                                const prefixFilter = document.getElementById('prefixFilter');
                                if (prefixFilter) prefixFilter.value = savedFilters.prefix;
                            }}, 500);
                        }}
                        
                        // Restore campaign type and status
                        if (savedFilters.campaignType) {{
                            currentFilters.campaignType = savedFilters.campaignType;
                            const campaignTypeFilter = document.getElementById('campaignTypeFilter');
                            if (campaignTypeFilter) campaignTypeFilter.value = savedFilters.campaignType;
                        }}
                        
                        if (savedFilters.status) {{
                            currentFilters.status = savedFilters.status;
                            const statusFilter = document.getElementById('statusFilter');
                            if (statusFilter) statusFilter.value = savedFilters.status;
                        }}
                        
                        // Restore date range
                        if (savedFilters.dateRange && savedFilters.dateRange.from && savedFilters.dateRange.to) {{
                            selectedDateRange.start = new Date(savedFilters.dateRange.from);
                            selectedDateRange.end = new Date(savedFilters.dateRange.to);
                            currentFilters.dateFrom = savedFilters.dateRange.from;
                            currentFilters.dateTo = savedFilters.dateRange.to;
                            const dateRangeText = document.getElementById('dateRangeText');
                            if (dateRangeText) {{
                                dateRangeText.textContent = formatDateVN(selectedDateRange.start) + ' - ' + formatDateVN(selectedDateRange.end);
                            }}
                        }} else if (savedFilters.datePreset) {{
                            // Restore quick date preset
                            selectQuickDate(savedFilters.datePreset);
                        }}
                        
                        // Restore search
                        if (savedFilters.search) {{
                            currentFilters.searchTerm = savedFilters.search;
                            const searchInput = document.getElementById('searchInput');
                            if (searchInput) searchInput.value = savedFilters.search;
                        }}
                        
                        // Restore view type
                        if (savedFilters.viewType) {{
                            currentFilters.viewType = savedFilters.viewType;
                        }}
                    }}
                }} catch (e) {{
                    console.error('Error loading filter state:', e);
                }}
            }}
            
            // Save filter state to localStorage
            function saveFilterState() {{
                try {{
                    const stateToSave = {{
                        account: currentFilters.account || '',
                        prefix: currentFilters.prefix || '',
                        campaignType: currentFilters.campaignType || '',
                        status: currentFilters.status || '',
                        dateRange: {{
                            from: currentFilters.dateFrom || '',
                            to: currentFilters.dateTo || ''
                        }},
                        datePreset: currentFilters.datePreset || '',
                        search: currentFilters.searchTerm || '',
                        viewType: currentFilters.viewType || 'adset'
                    }};
                    localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(stateToSave));
                }} catch (e) {{
                    console.error('Error saving filter state:', e);
                }}
            }}
            
            function applyDateRange() {{
                if (selectedDateRange.start && selectedDateRange.end) {{
                    // Format dates as YYYY-MM-DD for API (timezone VN)
                    const startStr = formatDateForAPI(selectedDateRange.start);
                    const endStr = formatDateForAPI(selectedDateRange.end);
                    currentFilters.dateFrom = startStr;
                    currentFilters.dateTo = endStr;
                    
                    const startFormatted = formatDateVN(selectedDateRange.start);
                    const endFormatted = formatDateVN(selectedDateRange.end);
                    document.getElementById('dateRangeText').textContent = startFormatted + ' - ' + endFormatted;
                    
                    saveFilterState();
                    closeDatePicker();
                    loadData();
                }}
            }}
            
            // Format date as YYYY-MM-DD in VN timezone
            function formatDateForAPI(date) {{
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                return year + '-' + month + '-' + day;
            }}
            
            function formatDateVN(date) {{
                const day = date.getDate();
                const month = date.getMonth() + 1;
                const year = date.getFullYear();
                return day + ' Tháng ' + month + ', ' + year;
            }}
            
            // Load data
            async function loadData() {{
                const account = document.getElementById('accountFilter').value;
                const prefix = document.getElementById('prefixFilter').value;
                const campaignType = document.getElementById('campaignTypeFilter').value;
                const status = document.getElementById('statusFilter').value;
                
                currentFilters.account = account;
                currentFilters.prefix = prefix;
                currentFilters.campaignType = campaignType;
                currentFilters.status = status;
                
                const params = new URLSearchParams({{
                    page: currentPage,
                    page_size: pageSize
                }});
                
                if (account) params.append('account_id', account);
                if (prefix) params.append('prefix', prefix);
                if (campaignType) params.append('campaign_type', campaignType);
                if (status) params.append('status', status);
                if (currentFilters.dateFrom) params.append('date_from', currentFilters.dateFrom);
                if (currentFilters.dateTo) params.append('date_to', currentFilters.dateTo);
                
                try {{
                    // Show improved loading skeleton
                    const skeleton = '<div class="loading-skeleton">' +
                        '<div class="skeleton-header">' +
                        '<div class="skeleton-line" style="width: 200px; height: 20px;"></div>' +
                        '<div class="skeleton-line" style="width: 150px; height: 20px;"></div>' +
                        '</div>' +
                        Array(8).fill(0).map(() => 
                            '<div class="skeleton-row">' +
                            '<div class="skeleton-item" style="width: 50px;"></div>' +
                            '<div class="skeleton-item" style="width: 200px;"></div>' +
                            '<div class="skeleton-item" style="width: 120px;"></div>' +
                            '<div class="skeleton-item" style="width: 80px;"></div>' +
                            '<div class="skeleton-item" style="width: 100px;"></div>' +
                            '<div class="skeleton-item" style="width: 100px;"></div>' +
                            '<div class="skeleton-item" style="width: 100px;"></div>' +
                            '<div class="skeleton-item" style="width: 80px;"></div>' +
                            '</div>'
                        ).join('') +
                        '</div>';
                    document.getElementById('tableWrapper').innerHTML = skeleton;
                    
                    const response = await fetch('/dashboard/data?' + params.toString(), {{
                        headers: {{
                            'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || getCookie('access_token'))
                        }}
                    }});
                    
                    if (!response.ok) throw new Error('Failed to load data');
                    
                    const data = await response.json();
                    if (data.stats) {{
                        updateStats(data.stats);
                    }}
                    renderTable(data);
                }} catch (error) {{
                    console.error('Error loading data:', error);
                    document.getElementById('tableWrapper').innerHTML = 
                        '<div class="empty-state"><div class="icon">⚠️</div>Lỗi khi tải dữ liệu</div>';
                }}
            }}
            
            function updateStats(stats) {{
                // Animate số đếm
                function animateValue(element, start, end, duration) {{
                    let startTimestamp = null;
                    const step = (timestamp) => {{
                        if (!startTimestamp) startTimestamp = timestamp;
                        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                        const value = Math.floor(progress * (end - start) + start);
                        element.textContent = formatNumber(value);
                        if (progress < 1) {{
                            window.requestAnimationFrame(step);
                        }} else {{
                            element.textContent = formatNumber(end);
                        }}
                    }};
                    window.requestAnimationFrame(step);
                }}
                
                const totalSpendEl = document.getElementById('totalSpend');
                const totalResultsEl = document.getElementById('totalResults');
                const avgGiaDataEl = document.getElementById('avgGiaData');
                const activeAdsetsEl = document.getElementById('activeAdsets');
                const pausedAdsetsEl = document.getElementById('pausedAdsets');
                const totalAdsetsEl = document.getElementById('totalAdsets');
                
                const currentSpend = parseFloat(totalSpendEl.textContent.replace(/[^0-9.-]+/g, '')) || 0;
                const currentResults = parseFloat(totalResultsEl.textContent.replace(/[^0-9.-]+/g, '')) || 0;
                const currentGiaData = parseFloat(avgGiaDataEl.textContent.replace(/[^0-9.-]+/g, '')) || 0;
                const currentActive = parseFloat(activeAdsetsEl.textContent.replace(/[^0-9.-]+/g, '')) || 0;
                const currentPaused = parseFloat(pausedAdsetsEl.textContent.replace(/[^0-9.-]+/g, '')) || 0;
                const currentTotal = parseFloat(totalAdsetsEl.textContent.replace(/[^0-9.-]+/g, '')) || 0;
                
                animateValue(totalSpendEl, currentSpend, stats.total_spend || 0, 800);
                animateValue(totalResultsEl, currentResults, stats.total_results || 0, 800);
                animateValue(avgGiaDataEl, currentGiaData, stats.avg_gia_data || 0, 800);
                animateValue(activeAdsetsEl, currentActive, stats.active_adsets || 0, 800);
                animateValue(pausedAdsetsEl, currentPaused, stats.paused_adsets || 0, 800);
                animateValue(totalAdsetsEl, currentTotal, stats.total_adsets || 0, 800);
            }}
            
            function renderTable(data) {{
                const ads = data.ads || [];
                const total = data.total || 0;
                const campaignType = currentFilters.campaignType || 'ECOMMERCE';
                
                if (ads.length === 0) {{
                    document.getElementById('tableWrapper').innerHTML = 
                        '<div class="empty-state">' +
                        '<div class="empty-icon">📭</div>' +
                        '<h3>Không có dữ liệu</h3>' +
                        '<p class="empty-message">Không tìm thấy dữ liệu phù hợp với bộ lọc hiện tại.</p>' +
                        '<div class="empty-suggestions">' +
                        '<div class="suggestion-item">💡 <strong>Gợi ý:</strong></div>' +
                        '<div class="suggestion-item">• Kiểm tra lại khoảng thời gian đã chọn</div>' +
                        '<div class="suggestion-item">• Thử chọn "Tất cả" cho các bộ lọc</div>' +
                        '<div class="suggestion-item">• Đảm bảo accounts đã được bật trong Settings</div>' +
                        '<div class="suggestion-item">• Nhấn nút "Làm mới" để pull dữ liệu từ Facebook</div>' +
                        '</div>' +
                        '</div>';
                    document.getElementById('tableInfo').textContent = 'Hiển thị 0 / 0 kết quả';
                    return;
                }}
                
                // Define columns based on view type and campaign type
                const viewType = currentFilters.viewType || 'adset';
                const nameColumn = viewType === 'campaign' ? 'Tên chiến dịch' : 
                                  viewType === 'ad' ? 'Tên quảng cáo' : 'Tên nhóm quảng cáo';
                
                const columns = campaignType === 'ECOMMERCE' ? [
                    'Chọn', 'Tắt/Bật', nameColumn, 'Account', 'Prefix', 'Số tiền chi tiêu',
                    '% ADS', 'Kết quả', 'Giá DATA', 'Chi phí trên mỗi lượt bắt đầu thanh toán',
                    'Tổng số lượt bắt đầu thanh toán', 'Chi phí trên mỗi lượt mua', 'Tổng số lượt mua',
                    'Giá trị chuyển đổi từ lượt mua', 'CPM', 'Lượt hiển thị', 'Số lần nhấp (tất cả)',
                    'CTR (tất cả)', 'CPC (tất cả)', 'Ngân sách', 'Thao tác'
                ] : [
                    'Chọn', 'Tắt/Bật', nameColumn, 'Account', 'Prefix', 'Số tiền chi tiêu',
                    'Kết quả', 'Giá DATA', 'Chi phí trên mỗi lượt bắt đầu thanh toán',
                    'Tổng số lượt bắt đầu thanh toán', 'Chi phí trên mỗi lượt mua', 'Tổng số lượt mua',
                    'CPM', 'Lượt hiển thị', 'Số lần nhấp (tất cả)', 'CTR (tất cả)', 'CPC (tất cả)', 'Ngân sách', 'Thao tác'
                ];
                
                // Define sortable columns
                const sortableColumns = {
                    'Số tiền chi tiêu': 'spend',
                    'Kết quả': 'results',
                    'Giá DATA': 'gia_data',
                    'CPM': 'cpm',
                    'Lượt hiển thị': 'impressions',
                    'Số lần nhấp (tất cả)': 'clicks',
                    'CTR (tất cả)': 'ctr',
                    'CPC (tất cả)': 'cpc',
                    'Ngân sách': 'budget'
                };
                
                let html = '<table><thead><tr>';
                columns.forEach((col, idx) => {{
                    if (col === 'Chọn') {{
                        // Checkbox header for select all
                        html += '<th style="width: 40px;"><input type="checkbox" id="selectAllCheckbox" onchange="toggleSelectAll(this)"></th>';
                    }} else {{
                        const sortKey = sortableColumns[col];
                        if (sortKey) {{
                            html += '<th class="sortable" onclick="sortTable(' + idx + ', \\'' + sortKey + '\\')">' + col + '</th>';
                        }} else {{
                            html += '<th>' + col + '</th>';
                        }}
                    }}
                }});
                html += '</tr></thead><tbody>';
                
                ads.forEach(ad => {{
                    const rowId = (ad.adset_id || ad.campaign_id || ad.ad_id || '') + '_' + Math.random().toString(36).substr(2, 9);
                    const entityId = viewType === 'campaign' ? (ad.campaign_id || '') : 
                                    viewType === 'ad' ? (ad.ad_id || '') : (ad.adset_id || '');
                    const entityName = viewType === 'campaign' ? (ad.campaign_name || '') : 
                                      viewType === 'ad' ? (ad.ad_name || '') : (ad.adset_name || '');
                    
                    html += '<tr data-row-id="' + rowId + '" data-entity-id="' + entityId + '" data-account-id="' + (ad.account_id || '') + '">';
                    
                    // Checkbox for multi-select
                    html += '<td><input type="checkbox" class="row-checkbox" onchange="updateBatchActionsBar()" data-entity-id="' + entityId + '"></td>';
                    
                    // Toggle switch cho status
                    const isActive = (ad.adset_status || ad.campaign_status || ad.ad_status || '').toUpperCase() === 'ACTIVE';
                    html += '<td><label class="toggle-switch" title="' + (isActive ? 'Tắt' : 'Bật') + '">' +
                        '<input type="checkbox" ' + (isActive ? 'checked' : '') + 
                        ' onchange="toggleAdsetStatus(\\'' + entityId + '\\', this)">' +
                        '<span class="toggle-slider"></span>' +
                        '</label></td>';
                    html += '<td>' + entityName + '</td>';
                    html += '<td>' + (ad.account_id || '-') + '</td>';
                    html += '<td>' + (ad.prefix || '-') + '</td>';
                    const cpm = ad.impressions > 0 ? ((ad.spend / ad.impressions) * 1000) : 0;
                    // Store calculated values for sorting
                    ad._cpm = cpm;
                    
                    html += '<td class="number-cell">' + formatNumber(ad.spend || 0) + '</td>';
                    
                    if (campaignType === 'ECOMMERCE') {{
                        const percentAds = ad.purchase_value > 0 ? ((ad.spend / ad.purchase_value) * 100).toFixed(2) : '0';
                        const alertBadge = parseFloat(percentAds) > 25 ? '<span class="alert-badge">⚠️</span>' : '';
                        html += '<td class="number-cell">' + percentAds + '% ' + alertBadge + '</td>';
                    }}
                    
                    html += '<td class="number-cell">' + formatNumber(ad.results || 0) + '</td>';
                    
                    const giaData = ad.gia_data || 0;
                    // Chỉ hiển thị cảnh báo cho E-commerce
                    const showGiaDataAlert = campaignType === 'ECOMMERCE' && giaData > 10000;
                    const giaDataAlert = showGiaDataAlert ? '<span class="alert-badge">⚠️</span>' : '';
                    html += '<td class="number-cell">' + formatNumber(giaData) + ' ' + giaDataAlert + '</td>';
                    
                    const costPerCheckout = ad.cost_per_checkout_initiated || 0;
                    html += '<td class="number-cell">' + formatNumber(costPerCheckout) + '</td>';
                    html += '<td class="number-cell">' + formatNumber(ad.checkouts_initiated || 0) + '</td>';
                    
                    const costPerPurchase = ad.cost_per_purchase || 0;
                    html += '<td class="number-cell">' + formatNumber(costPerPurchase) + '</td>';
                    html += '<td class="number-cell">' + formatNumber(ad.purchases || 0) + '</td>';
                    
                    if (campaignType === 'ECOMMERCE') {{
                        html += '<td class="number-cell">' + formatNumber(ad.purchase_value || 0) + '</td>';
                    }}
                    
                    html += '<td class="number-cell">' + formatNumber(cpm.toFixed(2)) + '</td>';
                    html += '<td class="number-cell">' + formatNumber(ad.impressions || 0) + '</td>';
                    html += '<td class="number-cell">' + formatNumber(ad.clicks || 0) + '</td>';
                    html += '<td class="number-cell">' + ((ad.ctr || 0)).toFixed(2) + '%</td>';
                    html += '<td class="number-cell">' + formatNumber(ad.cpc || 0) + '</td>';
                    
                    // Budget column với inline editor
                    const currentBudget = ad.daily_budget || 0;
                    html += '<td class="budget-cell">' +
                        '<div class="budget-display" onclick="openBudgetEditor(\\'' + (ad.adset_id || '') + '\\', ' + currentBudget + ', this)">' +
                        '<span class="budget-value">' + (currentBudget > 0 ? formatNumber(currentBudget) + ' đ/ngày' : 'Chưa có') + '</span>' +
                        '<span class="budget-edit-icon">✏️</span>' +
                        '</div>' +
                        '</td>';
                    
                    // Action buttons
                    const isActive = (ad.adset_status || '').toUpperCase() === 'ACTIVE';
                    html += '<td class="action-buttons">';
                    if (isActive) {{
                        html += '<button class="btn-action btn-pause" onclick="pauseAdset(\\'' + (ad.adset_id || '') + '\\', this)" title="Tắt adset">⏸️</button>';
                    }} else {{
                        html += '<button class="btn-action btn-activate" onclick="activateAdset(\\'' + (ad.adset_id || '') + '\\', this)" title="Bật adset">▶️</button>';
                    }}
                    html += '<button class="btn-action btn-increase" onclick="increaseBudget(\\'' + (ad.adset_id || '') + '\\', this)" title="Tăng ngân sách 10%">+10%</button>';
                    html += '<button class="btn-action btn-decrease" onclick="decreaseBudget(\\'' + (ad.adset_id || '') + '\\', this)" title="Giảm ngân sách 10%">-10%</button>';
                    html += '</td>';
                    html += '</tr>';
                }});
                
                html += '</tbody></table>';
                document.getElementById('tableWrapper').innerHTML = html;
                
                // Store ads data for sorting
                window.currentAdsData = ads;
                
                // Apply search filter nếu có
                if (currentSearchTerm) {{
                    const searchTerm = currentSearchTerm.toLowerCase();
                    const rows = document.querySelectorAll('#tableWrapper tbody tr');
                    let visibleCount = 0;
                    
                    rows.forEach(row => {{
                        const text = row.textContent.toLowerCase();
                        if (text.includes(searchTerm)) {{
                            row.style.display = '';
                            visibleCount++;
                        }} else {{
                            row.style.display = 'none';
                        }}
                    }});
                    
                    if (visibleCount === 0) {{
                        document.getElementById('tableInfo').textContent = 'Không tìm thấy kết quả cho "' + currentSearchTerm + '"';
                    }} else {{
                        document.getElementById('tableInfo').textContent = 'Tìm thấy ' + visibleCount + ' / ' + total + ' kết quả';
                    }}
                }} else {{
                    document.getElementById('tableInfo').textContent = 
                        'Hiển thị ' + ads.length + ' / ' + total + ' kết quả';
                }}
                
                // Pagination
                const totalPages = Math.ceil(total / pageSize);
                renderPagination(totalPages);
            }}
            
            function renderPagination(totalPages) {{
                const pagination = document.getElementById('pagination');
                if (totalPages <= 1) {{
                    pagination.innerHTML = '';
                    return;
                }}
                
                let html = '';
                html += '<button onclick="goToPage(1)"' + (currentPage === 1 ? ' disabled' : '') + '>«</button>';
                html += '<button onclick="goToPage(' + (currentPage - 1) + ')"' + (currentPage === 1 ? ' disabled' : '') + '>‹</button>';
                
                const startPage = Math.max(1, currentPage - 2);
                const endPage = Math.min(totalPages, currentPage + 2);
                
                for (let i = startPage; i <= endPage; i++) {{
                    const activeClass = i === currentPage ? 'active' : '';
                    html += '<button class="' + activeClass + '" onclick="goToPage(' + i + ')">' + i + '</button>';
                }}
                
                html += '<button onclick="goToPage(' + (currentPage + 1) + ')"' + (currentPage === totalPages ? ' disabled' : '') + '>›</button>';
                html += '<button onclick="goToPage(' + totalPages + ')"' + (currentPage === totalPages ? ' disabled' : '') + '>»</button>';
                
                pagination.innerHTML = html;
            }}
            
            function goToPage(page) {{
                currentPage = page;
                loadData();
            }}
            
            function formatNumber(num) {{
                return new Intl.NumberFormat('vi-VN').format(num);
            }}
            
            // Action functions for adset control
            // Toggle adset status (thay thế pauseAdset và activateAdset)
            async function toggleAdsetStatus(adsetId, checkboxElement) {{
                const isActive = checkboxElement.checked;
                const originalState = !isActive; // Lưu trạng thái ban đầu để rollback nếu lỗi
                
                // Disable checkbox trong khi xử lý
                checkboxElement.disabled = true;
                
                try {{
                    const token = localStorage.getItem('access_token') || getCookie('access_token');
                    const endpoint = isActive ? '/dashboard/adsets/activate' : '/dashboard/adsets/pause';
                    
                    const response = await fetch(endpoint, {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + token,
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{ adset_id: adsetId }})
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {{
                        showToast('✅ Đã ' + (isActive ? 'bật' : 'tắt') + ' adset thành công', 'success');
                        // Reload data để cập nhật UI
                        loadData();
                    }} else {{
                        // Rollback UI
                        checkboxElement.checked = originalState;
                        showToast('❌ Lỗi: ' + (result.detail || result.message || 'Unknown error'), 'error');
                    }}
                }} catch (error) {{
                    // Rollback UI
                    checkboxElement.checked = originalState;
                    showToast('❌ Lỗi: ' + error.message, 'error');
                }} finally {{
                    checkboxElement.disabled = false;
                }}
            }}
            
            async function pauseAdset(adsetId, buttonElement) {{
                if (!confirm('Bạn có chắc muốn tắt adset này?')) return;
                
                const btn = buttonElement;
                btn.disabled = true;
                btn.classList.add('loading');
                
                try {{
                    const token = localStorage.getItem('access_token') || getCookie('access_token');
                    const response = await fetch('/dashboard/adset/pause?adset_id=' + adsetId, {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + token
                        }}
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        // Update status badge
                        const row = btn.closest('tr');
                        const statusBadge = row.querySelector('.status-badge');
                        statusBadge.textContent = 'PAUSED';
                        statusBadge.className = 'status-badge status-paused';
                        
                        // Update button to activate
                        btn.outerHTML = '<button class="btn-action btn-activate" onclick="activateAdset(\\'' + adsetId + '\\', this)" title="Bật adset">▶️</button>';
                        
                        showToast('✅ Đã tắt adset thành công', 'success');
                    }} else {{
                        showToast('❌ Lỗi: ' + (result.detail || result.message || 'Unknown error'), 'error');
                    }}
                }} catch (error) {{
                    showToast('❌ Lỗi: ' + error.message, 'error');
                }} finally {{
                    btn.disabled = false;
                    btn.classList.remove('loading');
                }}
            }}
            
            async function activateAdset(adsetId, buttonElement) {{
                if (!confirm('Bạn có chắc muốn bật adset này?')) return;
                
                const btn = buttonElement;
                btn.disabled = true;
                btn.classList.add('loading');
                
                try {{
                    const token = localStorage.getItem('access_token') || getCookie('access_token');
                    const response = await fetch('/dashboard/adset/activate?adset_id=' + adsetId, {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + token
                        }}
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        // Update status badge
                        const row = btn.closest('tr');
                        const statusBadge = row.querySelector('.status-badge');
                        statusBadge.textContent = 'ACTIVE';
                        statusBadge.className = 'status-badge status-active';
                        
                        // Update button to pause
                        btn.outerHTML = '<button class="btn-action btn-pause" onclick="pauseAdset(\\'' + adsetId + '\\', this)" title="Tắt adset">⏸️</button>';
                        
                        showToast('✅ Đã bật adset thành công', 'success');
                    }} else {{
                        showToast('❌ Lỗi: ' + (result.detail || result.message || 'Unknown error'), 'error');
                    }}
                }} catch (error) {{
                    showToast('❌ Lỗi: ' + error.message, 'error');
                }} finally {{
                    btn.disabled = false;
                    btn.classList.remove('loading');
                }}
            }}
            
            async function increaseBudget(adsetId, buttonElement) {{
                if (!confirm('Bạn có chắc muốn tăng ngân sách adset này thêm 10%?')) return;
                
                const btn = buttonElement;
                btn.disabled = true;
                btn.classList.add('loading');
                
                try {{
                    const token = localStorage.getItem('access_token') || getCookie('access_token');
                    const response = await fetch('/dashboard/adset/budget/increase?adset_id=' + adsetId + '&percent=10', {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + token
                        }}
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        showToast('✅ Đã tăng ngân sách: ' + formatNumber(result.old_budget) + ' → ' + formatNumber(result.new_budget), 'success');
                        // Reload data to update budget display
                        setTimeout(() => loadData(), 1000);
                    }} else {{
                        showToast('❌ Lỗi: ' + (result.detail || result.message || 'Unknown error'), 'error');
                    }}
                }} catch (error) {{
                    showToast('❌ Lỗi: ' + error.message, 'error');
                }} finally {{
                    btn.disabled = false;
                    btn.classList.remove('loading');
                }}
            }}
            
            async function decreaseBudget(adsetId, buttonElement) {{
                if (!confirm('Bạn có chắc muốn giảm ngân sách adset này đi 10%?')) return;
                
                const btn = buttonElement;
                btn.disabled = true;
                btn.classList.add('loading');
                
                try {{
                    const token = localStorage.getItem('access_token') || getCookie('access_token');
                    const response = await fetch('/dashboard/adset/budget/decrease?adset_id=' + adsetId + '&percent=10', {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + token
                        }}
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        showToast('✅ Đã giảm ngân sách: ' + formatNumber(result.old_budget) + ' → ' + formatNumber(result.new_budget), 'success');
                        // Reload data to update budget display
                        setTimeout(() => loadData(), 1000);
                    }} else {{
                        showToast('❌ Lỗi: ' + (result.detail || result.message || 'Unknown error'), 'error');
                    }}
                }} catch (error) {{
                    showToast('❌ Lỗi: ' + error.message, 'error');
                }} finally {{
                    btn.disabled = false;
                    btn.classList.remove('loading');
                }}
            }}
            
            // Budget Editor Functions
            function openBudgetEditor(adsetId, currentBudget, element) {{
                // Close any existing editor
                document.querySelectorAll('.budget-editor-popover').forEach(el => el.remove());
                
                const popover = document.createElement('div');
                popover.className = 'budget-editor-popover';
                popover.innerHTML = 
                    '<h4>Chỉnh sửa ngân sách</h4>' +
                    '<div class="budget-input-group">' +
                    '<label>Ngân sách hiện tại</label>' +
                    '<input type="text" id="budgetCurrent" value="' + formatNumber(currentBudget) + ' đ/ngày" readonly style="background: #f3f4f6;">' +
                    '</div>' +
                    '<div class="budget-input-group">' +
                    '<label>Ngân sách mới (VND)</label>' +
                    '<input type="number" id="budgetNew" value="' + currentBudget + '" min="0" step="1000" placeholder="Nhập số tiền">' +
                    '</div>' +
                    '<div class="budget-shortcuts">' +
                    '<button class="budget-shortcut-btn" onclick="applyBudgetShortcut(\\'' + adsetId + '\\', -20)">-20%</button>' +
                    '<button class="budget-shortcut-btn" onclick="applyBudgetShortcut(\\'' + adsetId + '\\', -10)">-10%</button>' +
                    '<button class="budget-shortcut-btn" onclick="applyBudgetShortcut(\\'' + adsetId + '\\', 10)">+10%</button>' +
                    '<button class="budget-shortcut-btn" onclick="applyBudgetShortcut(\\'' + adsetId + '\\', 20)">+20%</button>' +
                    '</div>' +
                    '<div class="budget-actions">' +
                    '<button class="budget-btn budget-btn-secondary" onclick="closeBudgetEditor()">Hủy</button>' +
                    '<button class="budget-btn budget-btn-primary" onclick="saveBudget(\\'' + adsetId + '\\')">Lưu</button>' +
                    '</div>';
                
                const rect = element.getBoundingClientRect();
                popover.style.position = 'fixed';
                popover.style.top = (rect.bottom + window.scrollY + 4) + 'px';
                popover.style.left = rect.left + 'px';
                
                element.parentElement.appendChild(popover);
                
                // Focus input
                setTimeout(() => {{
                    const input = document.getElementById('budgetNew');
                    if (input) {{
                        input.focus();
                        input.select();
                    }}
                }}, 100);
                
                // Close on outside click
                setTimeout(() => {{
                    const closeHandler = function(e) {{
                        if (!popover.contains(e.target) && !element.contains(e.target)) {{
                            popover.remove();
                            document.removeEventListener('click', closeHandler);
                        }}
                    }};
                    document.addEventListener('click', closeHandler);
                }}, 0);
            }}
            
            function closeBudgetEditor() {{
                document.querySelectorAll('.budget-editor-popover').forEach(el => el.remove());
            }}
            
            function applyBudgetShortcut(adsetId, percent) {{
                const currentInput = document.getElementById('budgetCurrent');
                const newInput = document.getElementById('budgetNew');
                
                if (currentInput && newInput) {{
                    const currentValue = parseFloat(currentInput.value.replace(/[^0-9]/g, '')) || 0;
                    const newValue = Math.max(0, currentValue * (1 + percent / 100));
                    newInput.value = Math.round(newValue);
                }}
            }}
            
            async function saveBudget(adsetId) {{
                const newInput = document.getElementById('budgetNew');
                if (!newInput) return;
                
                const newBudget = parseFloat(newInput.value);
                if (isNaN(newBudget) || newBudget < 0) {{
                    showToast('❌ Vui lòng nhập số tiền hợp lệ', 'error');
                    return;
                }}
                
                try {{
                    const token = localStorage.getItem('access_token') || getCookie('access_token');
                    const response = await fetch('/dashboard/adset/budget', {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + token,
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            adset_id: adsetId,
                            daily_budget: newBudget
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {{
                        showToast('✅ Đã cập nhật ngân sách thành công', 'success');
                        closeBudgetEditor();
                        loadData(); // Reload để cập nhật UI
                    }} else {{
                        showToast('❌ Lỗi: ' + (result.detail || result.message || 'Unknown error'), 'error');
                    }}
                }} catch (error) {{
                    showToast('❌ Lỗi: ' + error.message, 'error');
                }}
            }}
            
            // Toast notification
            function showToast(message, type = 'info') {{
                const toast = document.createElement('div');
                toast.className = 'toast toast-' + type;
                toast.textContent = message;
                toast.style.cssText = 'position:fixed;top:20px;right:20px;padding:12px 20px;background:' + 
                    (type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6') + 
                    ';color:white;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:10000;animation:slideInRight 0.3s ease;';
                document.body.appendChild(toast);
                
                setTimeout(() => {{
                    toast.style.animation = 'slideOutRight 0.3s ease';
                    setTimeout(() => toast.remove(), 300);
                }}, 3000);
            }}
            
            // Table sorting
            let currentSortColumn = null;
            let currentSortDirection = 'desc'; // Default sort by Giá DATA descending
            
            function sortTable(columnIndex, sortKey) {{
                const table = document.querySelector('#tableWrapper table');
                if (!table || !window.currentAdsData) return;
                
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const headers = table.querySelectorAll('th');
                
                // Remove previous sort classes
                headers.forEach(h => {{
                    h.classList.remove('sort-asc', 'sort-desc');
                }});
                
                // Toggle sort direction
                if (currentSortColumn === columnIndex) {{
                    currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
                }} else {{
                    currentSortColumn = columnIndex;
                    currentSortDirection = 'desc';
                }}
                
                // Add sort class to header
                headers[columnIndex].classList.add('sort-' + currentSortDirection);
                
                // Sort rows - map rows to data first
                const rowDataMap = new Map();
                rows.forEach((row, idx) => {{
                    rowDataMap.set(row, window.currentAdsData[idx]);
                }});
                
                // Sort rows
                rows.sort((a, b) => {{
                    const aData = rowDataMap.get(a);
                    const bData = rowDataMap.get(b);
                    
                    let aVal, bVal;
                    
                    switch(sortKey) {{
                        case 'spend':
                            aVal = aData.spend || 0;
                            bVal = bData.spend || 0;
                            break;
                        case 'results':
                            aVal = aData.results || 0;
                            bVal = bData.results || 0;
                            break;
                        case 'gia_data':
                            aVal = aData.gia_data || 0;
                            bVal = bData.gia_data || 0;
                            break;
                        case 'cpm':
                            aVal = aData._cpm || 0;
                            bVal = bData._cpm || 0;
                            break;
                        case 'impressions':
                            aVal = aData.impressions || 0;
                            bVal = bData.impressions || 0;
                            break;
                        case 'clicks':
                            aVal = aData.clicks || 0;
                            bVal = bData.clicks || 0;
                            break;
                        case 'ctr':
                            aVal = aData.ctr || 0;
                            bVal = bData.ctr || 0;
                            break;
                        case 'cpc':
                            aVal = aData.cpc || 0;
                            bVal = bData.cpc || 0;
                            break;
                        default:
                            return 0;
                    }}
                    
                    if (currentSortDirection === 'asc') {{
                        return aVal - bVal;
                    }} else {{
                        return bVal - aVal;
                    }}
                }});
                
                // Reorder rows
                rows.forEach(row => tbody.appendChild(row));
            }}
            
            // Export data to Excel
            function exportData() {{
                const btn = document.getElementById('exportBtn');
                btn.disabled = true;
                btn.textContent = '⏳ Đang xuất...';
                
                const account = document.getElementById('accountFilter').value;
                const prefix = document.getElementById('prefixFilter').value;
                const campaignType = document.getElementById('campaignTypeFilter').value;
                const status = document.getElementById('statusFilter').value;
                
                const params = new URLSearchParams({{
                    page: 1,
                    page_size: 10000
                }});
                
                if (account) params.append('account_id', account);
                if (prefix) params.append('prefix', prefix);
                if (campaignType) params.append('campaign_type', campaignType);
                if (status) params.append('status', status);
                if (currentFilters.dateFrom) params.append('date_from', currentFilters.dateFrom);
                if (currentFilters.dateTo) params.append('date_to', currentFilters.dateTo);
                
                fetch('/dashboard/data?' + params.toString(), {{
                    headers: {{
                        'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || getCookie('access_token'))
                    }}
                }})
                .then(res => res.json())
                .then(data => {{
                    const ads = data.ads || [];
                    if (ads.length === 0) {{
                        alert('Không có dữ liệu để xuất!');
                        btn.disabled = false;
                        btn.textContent = '📥 Xuất Excel';
                        return;
                    }}
                    
                    // Create CSV
                    const campaignType = currentFilters.campaignType || 'ECOMMERCE';
                    const headers = campaignType === 'ECOMMERCE' ? [
                        'Tắt/Bật', 'Tên nhóm quảng cáo', 'Số tiền chi tiêu', '% ADS', 'Kết quả', 
                        'Giá DATA', 'Chi phí trên mỗi lượt bắt đầu thanh toán', 'Tổng số lượt bắt đầu thanh toán',
                        'Chi phí trên mỗi lượt mua', 'Tổng số lượt mua', 'Giá trị chuyển đổi từ lượt mua',
                        'CPM', 'Lượt hiển thị', 'Số lần nhấp (tất cả)', 'CTR (tất cả)', 'CPC (tất cả)'
                    ] : [
                        'Tắt/Bật', 'Tên nhóm quảng cáo', 'Số tiền chi tiêu', 'Kết quả', 'Giá DATA',
                        'Chi phí trên mỗi lượt bắt đầu thanh toán', 'Tổng số lượt bắt đầu thanh toán',
                        'Chi phí trên mỗi lượt mua', 'Tổng số lượt mua', 'CPM', 'Lượt hiển thị',
                        'Số lần nhấp (tất cả)', 'CTR (tất cả)', 'CPC (tất cả)'
                    ];
                    
                    let csv = headers.join(',') + '\\n';
                    
                    ads.forEach(ad => {{
                        const row = [
                            ad.adset_status || '',
                            '"' + (ad.adset_name || '').replace(/"/g, '""') + '"',
                            ad.spend || 0,
                            campaignType === 'ECOMMERCE' ? (ad.purchase_value > 0 ? ((ad.spend / ad.purchase_value) * 100).toFixed(2) : '0') : '',
                            ad.results || 0,
                            ad.gia_data || 0,
                            ad.cost_per_checkout_initiated || 0,
                            ad.checkouts_initiated || 0,
                            ad.cost_per_purchase || 0,
                            ad.purchases || 0,
                            campaignType === 'ECOMMERCE' ? (ad.purchase_value || 0) : '',
                            ad.impressions > 0 ? ((ad.spend / ad.impressions) * 1000).toFixed(2) : '0',
                            ad.impressions || 0,
                            ad.clicks || 0,
                            (ad.ctr || 0).toFixed(2),
                            ad.cpc || 0
                        ];
                        csv += row.join(',') + '\\n';
                    }});
                    
                    // Download
                    const blob = new Blob(['\\ufeff' + csv], {{ type: 'text/csv;charset=utf-8;' }});
                    const link = document.createElement('a');
                    const url = URL.createObjectURL(blob);
                    link.setAttribute('href', url);
                    link.setAttribute('download', 'dashboard_data_' + new Date().toISOString().split('T')[0] + '.csv');
                    link.style.visibility = 'hidden';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    btn.disabled = false;
                    btn.textContent = '📥 Xuất Excel';
                }})
                .catch(error => {{
                    console.error('Export error:', error);
                    alert('Lỗi khi xuất dữ liệu!');
                    btn.disabled = false;
                    btn.textContent = '📥 Xuất Excel';
                }});
            }}
            
            // Filter change handler
            function handleFilterChange() {{
                currentFilters.campaignType = document.getElementById('campaignTypeFilter').value;
                currentFilters.status = document.getElementById('statusFilter').value;
                currentFilters.account = document.getElementById('accountFilter').value;
                currentFilters.prefix = document.getElementById('prefixFilter').value;
                saveFilterState(); // Save to localStorage
                debouncedLoadData();
            }}
            
            // Search functionality với debounce
            let searchTimeout;
            let currentSearchTerm = '';
            function handleSearch(event) {{
                clearTimeout(searchTimeout);
                const searchInput = event.target;
                currentSearchTerm = searchInput.value.trim();
                currentFilters.searchTerm = currentSearchTerm;
                saveFilterState(); // Save to localStorage
                
                searchTimeout = setTimeout(() => {{
                    if (!currentSearchTerm) {{
                        // Nếu search rỗng, hiển thị lại tất cả
                        const rows = document.querySelectorAll('#tableWrapper tbody tr');
                        rows.forEach(row => {{
                            row.style.display = '';
                        }});
                        const total = document.querySelectorAll('#tableWrapper tbody tr').length;
                        document.getElementById('tableInfo').textContent = 'Hiển thị ' + total + ' kết quả';
                        return;
                    }}
                    
                    const searchTerm = currentSearchTerm.toLowerCase();
                    const rows = document.querySelectorAll('#tableWrapper tbody tr');
                    let visibleCount = 0;
                    
                    if (rows.length === 0) {{
                        // Table chưa được render, không làm gì
                        return;
                    }}
                    
                    rows.forEach(row => {{
                        const text = row.textContent.toLowerCase();
                        if (text.includes(searchTerm)) {{
                            row.style.display = '';
                            visibleCount++;
                        }} else {{
                            row.style.display = 'none';
                        }}
                    }});
                    
                    if (visibleCount === 0) {{
                        document.getElementById('tableInfo').textContent = 'Không tìm thấy kết quả cho "' + currentSearchTerm + '"';
                    }} else {{
                        document.getElementById('tableInfo').textContent = 'Tìm thấy ' + visibleCount + ' kết quả';
                    }}
                }}, 300);
            }}
            
            // Mobile filter toggle
            function toggleMobileFilters() {{
                const sidebar = document.getElementById('sidebarFilters');
                sidebar.classList.toggle('mobile-hidden');
            }}
            
            // Apply filters
            function applyFilters() {{
                loadData();
                loadPrefixSummary();
                updateLastUpdateTime();
                // Close mobile sidebar if open
                if (window.innerWidth <= 1024) {{
                    document.getElementById('sidebarFilters').classList.add('mobile-hidden');
                }}
            }}
            
            // Reset filters
            function resetFilters() {{
                document.getElementById('accountFilter').value = '';
                document.getElementById('prefixFilter').value = '';
                document.getElementById('campaignTypeFilter').value = '';
                document.getElementById('statusFilter').value = '';
                document.getElementById('searchInput').value = '';
                currentSearchTerm = '';
                const today = new Date();
                selectedDateRange.start = today;
                selectedDateRange.end = today;
                currentFilters.dateFrom = today.toISOString().split('T')[0];
                currentFilters.dateTo = today.toISOString().split('T')[0];
                document.getElementById('dateRangeText').textContent = formatDateVN(today) + ' - ' + formatDateVN(today);
                document.querySelectorAll('.quick-filter-btn').forEach(btn => btn.classList.remove('active'));
                loadData();
                loadPrefixSummary();
                updateLastUpdateTime();
            }}
            
            // Quick filters
            function applyQuickFilter(type, buttonElement) {{
                document.querySelectorAll('.quick-filter-btn').forEach(btn => btn.classList.remove('active'));
                if (buttonElement) {{
                    buttonElement.classList.add('active');
                }}
                currentFilters.datePreset = type; // Save preset type
                selectQuickDate(type);
            }}
            
            async function refreshData() {{
                const btn = document.getElementById('refreshBtn');
                btn.classList.add('loading');
                btn.disabled = true;
                
                await Promise.all([
                    loadData(),
                    loadPrefixSummary()
                ]);
                
                updateLastUpdateTime();
                
                setTimeout(() => {{
                    btn.classList.remove('loading');
                    btn.disabled = false;
                }}, 500);
            }}
            
            async function loadFilters() {{
                try {{
                    const response = await fetch('/dashboard/filters', {{
                        headers: {{
                            'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || getCookie('access_token'))
                        }}
                    }});
                    
                    if (!response.ok) return;
                    
                    const filters = await response.json();
                    
                    // Populate account filter
                    const accountFilter = document.getElementById('accountFilter');
                    filters.accounts.forEach(account => {{
                        const option = document.createElement('option');
                        option.value = account;
                        option.textContent = account;
                        accountFilter.appendChild(option);
                    }});
                    
                    // Populate prefix filter
                    const prefixFilter = document.getElementById('prefixFilter');
                    filters.prefixes.forEach(prefix => {{
                        const option = document.createElement('option');
                        option.value = prefix;
                        option.textContent = prefix;
                        prefixFilter.appendChild(option);
                    }});
                }} catch (error) {{
                    console.error('Error loading filters:', error);
                }}
            }}
            
            // Debounce function cho performance
            function debounce(func, wait) {{
                let timeout;
                return function executedFunction(...args) {{
                    const later = () => {{
                        clearTimeout(timeout);
                        func(...args);
                    }};
                    clearTimeout(timeout);
                    timeout = setTimeout(later, wait);
                }};
            }}
            
            // Prefix summary
            let currentPrefixTab = 'all';
            
            async function loadPrefixSummary() {{
                try {{
                    const token = localStorage.getItem('access_token') || getCookie('access_token');
                    const params = new URLSearchParams();
                    if (currentFilters.dateFrom) params.append('date_from', currentFilters.dateFrom);
                    if (currentFilters.dateTo) params.append('date_to', currentFilters.dateTo);
                    if (currentFilters.campaignType) params.append('campaign_type', currentFilters.campaignType);
                    
                    const response = await fetch('/dashboard/prefix-summary?' + params.toString(), {{
                        headers: {{
                            'Authorization': 'Bearer ' + token
                        }}
                    }});
                    
                    if (!response.ok) return;
                    
                    const data = await response.json();
                    renderPrefixSummary(data);
                }} catch (error) {{
                    console.error('Error loading prefix summary:', error);
                }}
            }}
            
            function renderPrefixSummary(data) {{
                const container = document.getElementById('prefixGrid');
                const prefixes = data.prefixes || {{}};
                const ecommerce = data.ecommerce || {{}};
                const lead = data.lead || {{}};
                
                if (Object.keys(prefixes).length === 0) {{
                    container.innerHTML = '<div class="empty-state"><div class="icon">📊</div><p>Chưa có dữ liệu prefix</p></div>';
                    return;
                }}
                
                let html = '';
                
                Object.keys(prefixes).forEach(prefix => {{
                    const prefixData = prefixes[prefix];
                    const ecomData = ecommerce[prefix] || null;
                    const leadData = lead[prefix] || null;
                    
                    // Determine which data to show based on current tab
                    let displayData = prefixData;
                    let badge = '';
                    
                    if (currentPrefixTab === 'ecommerce' && ecomData) {{
                        displayData = ecomData;
                        badge = '<span class="prefix-card-badge badge-ecommerce">E-commerce</span>';
                    }} else if (currentPrefixTab === 'lead' && leadData) {{
                        displayData = leadData;
                        badge = '<span class="prefix-card-badge badge-lead">Lead</span>';
                    }} else if (currentPrefixTab === 'all') {{
                        // Show combined data
                        if (ecomData && leadData) {{
                            badge = '<span class="prefix-card-badge badge-ecommerce">E-com</span> <span class="prefix-card-badge badge-lead">Lead</span>';
                        }} else if (ecomData) {{
                            badge = '<span class="prefix-card-badge badge-ecommerce">E-commerce</span>';
                        }} else if (leadData) {{
                            badge = '<span class="prefix-card-badge badge-lead">Lead</span>';
                        }}
                    }}
                    
                    // Skip if current tab doesn't have data
                    if (currentPrefixTab === 'ecommerce' && !ecomData) return;
                    if (currentPrefixTab === 'lead' && !leadData) return;
                    
                    html += '<div class="prefix-card">';
                    html += '<div class="prefix-card-header">';
                    html += '<div class="prefix-card-title">' + prefix + '</div>';
                    html += badge;
                    html += '</div>';
                    html += '<div class="prefix-stats">';
                    html += '<div class="prefix-stat-item">';
                    html += '<div class="prefix-stat-label">Chi tiêu</div>';
                    html += '<div class="prefix-stat-value">' + formatNumber(displayData.spend || 0) + '</div>';
                    html += '</div>';
                    html += '<div class="prefix-stat-item">';
                    html += '<div class="prefix-stat-label">Kết quả</div>';
                    html += '<div class="prefix-stat-value">' + formatNumber(displayData.results || 0) + '</div>';
                    html += '</div>';
                    html += '<div class="prefix-stat-item">';
                    html += '<div class="prefix-stat-label">CPL</div>';
                    html += '<div class="prefix-stat-value">' + formatNumber(displayData.cpl || 0) + '</div>';
                    html += '</div>';
                    html += '<div class="prefix-stat-item">';
                    html += '<div class="prefix-stat-label">Giá DATA</div>';
                    html += '<div class="prefix-stat-value">' + formatNumber(displayData.avg_gia_data || 0) + '</div>';
                    html += '</div>';
                    if (displayData.roas) {{
                        html += '<div class="prefix-stat-item">';
                        html += '<div class="prefix-stat-label">ROAS</div>';
                        html += '<div class="prefix-stat-value">' + displayData.roas.toFixed(2) + 'x</div>';
                        html += '</div>';
                    }}
                    if (displayData.active_adsets !== undefined) {{
                        html += '<div class="prefix-stat-item">';
                        html += '<div class="prefix-stat-label">Adsets</div>';
                        html += '<div class="prefix-stat-value">' + displayData.active_adsets + '/' + displayData.total_adsets + '</div>';
                        html += '</div>';
                    }}
                    html += '</div>';
                    html += '</div>';
                }});
                
                container.innerHTML = html;
            }}
            
            function switchPrefixTab(tab, buttonElement) {{
                currentPrefixTab = tab;
                document.querySelectorAll('.prefix-tab').forEach(btn => btn.classList.remove('active'));
                buttonElement.classList.add('active');
                loadPrefixSummary();
            }}
            
            // Last update time
            let lastUpdateTime = null;
            
            function updateLastUpdateTime() {{
                lastUpdateTime = new Date();
                const timeStr = lastUpdateTime.toLocaleTimeString('vi-VN');
                const updateTimeEl = document.getElementById('lastUpdateTime');
                if (updateTimeEl) {{
                    updateTimeEl.textContent = 'Cập nhật lần cuối: ' + timeStr;
                }}
            }}
            
            // View Type Switch
            function switchViewType(type, buttonElement) {{
                document.querySelectorAll('.view-type-tab').forEach(btn => btn.classList.remove('active'));
                buttonElement.classList.add('active');
                currentFilters.viewType = type;
                saveFilterState();
                loadData();
            }}
            
            // Multi-select functions
            function toggleSelectAll(checkbox) {{
                const checkboxes = document.querySelectorAll('.row-checkbox');
                checkboxes.forEach(cb => cb.checked = checkbox.checked);
                updateBatchActionsBar();
            }}
            
            function updateBatchActionsBar() {{
                const checkboxes = document.querySelectorAll('.row-checkbox:checked');
                const count = checkboxes.length;
                const batchBar = document.getElementById('batchActionsBar');
                const selectedCount = document.getElementById('selectedCount');
                
                if (count > 0) {{
                    batchBar.style.display = 'block';
                    selectedCount.textContent = count + ' mục đã chọn';
                }} else {{
                    batchBar.style.display = 'none';
                }}
                
                const selectAll = document.getElementById('selectAllCheckbox');
                if (selectAll) {{
                    const allCheckboxes = document.querySelectorAll('.row-checkbox');
                    selectAll.checked = allCheckboxes.length > 0 && checkboxes.length === allCheckboxes.length;
                }}
            }}
            
            // Batch Actions
            async function batchAction(action) {{
                const checkboxes = document.querySelectorAll('.row-checkbox:checked');
                if (checkboxes.length === 0) {{
                    showToast('❌ Vui lòng chọn ít nhất 1 mục', 'error');
                    return;
                }}
                
                const entityIds = Array.from(checkboxes).map(cb => cb.getAttribute('data-entity-id')).filter(id => id);
                if (entityIds.length === 0) return;
                
                const viewType = currentFilters.viewType || 'adset';
                const actionText = action === 'pause' ? 'tắt' : action === 'activate' ? 'bật' : 
                                 action === 'increase' ? 'tăng ngân sách' : 'giảm ngân sách';
                
                if (!confirm('Bạn có chắc muốn ' + actionText + ' ' + entityIds.length + ' mục đã chọn?')) return;
                
                try {{
                    const token = localStorage.getItem('access_token') || getCookie('access_token');
                    const response = await fetch('/dashboard/adsets/batch-action', {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + token,
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            entity_ids: entityIds,
                            action: action,
                            view_type: viewType
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {{
                        showToast('✅ Đã ' + actionText + ' thành công ' + entityIds.length + ' mục', 'success');
                        checkboxes.forEach(cb => cb.checked = false);
                        updateBatchActionsBar();
                        loadData();
                    }} else {{
                        showToast('❌ Lỗi: ' + (result.detail || result.message || 'Unknown error'), 'error');
                    }}
                }} catch (error) {{
                    showToast('❌ Lỗi: ' + error.message, 'error');
                }}
            }}
            
            // Initialize on page load
            window.addEventListener('DOMContentLoaded', () => {{
                // Load filter state from localStorage first
                loadFilterState();
                
                // Set default date to today if no saved state
                if (!selectedDateRange.start || !selectedDateRange.end) {{
                    const today = getTodayVN();
                    selectedDateRange.start = new Date(today);
                    selectedDateRange.end = new Date(today);
                    selectedDateRange.end.setHours(23, 59, 59, 999);
                    currentFilters.dateFrom = formatDateForAPI(selectedDateRange.start);
                    currentFilters.dateTo = formatDateForAPI(selectedDateRange.end);
                    currentFilters.datePreset = 'today';
                    const dateRangeText = document.getElementById('dateRangeText');
                    if (dateRangeText) {{
                        dateRangeText.textContent = formatDateVN(selectedDateRange.start) + ' - ' + formatDateVN(selectedDateRange.end);
                    }}
                }}
                
                // Load filters (accounts, prefixes) from API
                loadFilters();
                
                // Load data after filters are loaded
                setTimeout(() => {{
                    loadData();
                    loadPrefixSummary();
                    updateLastUpdateTime();
                }}, 500);
                
                // Add event listeners với debounce
                const debouncedLoadData = debounce(loadData, 300);
                const accountFilter = document.getElementById('accountFilter');
                const prefixFilter = document.getElementById('prefixFilter');
                const campaignTypeFilter = document.getElementById('campaignTypeFilter');
                const statusFilter = document.getElementById('statusFilter');
                
                if (accountFilter) accountFilter.addEventListener('change', () => {{ handleFilterChange(); }});
                if (prefixFilter) prefixFilter.addEventListener('change', () => {{ handleFilterChange(); }});
                if (campaignTypeFilter) campaignTypeFilter.addEventListener('change', () => {{ handleFilterChange(); }});
                if (statusFilter) statusFilter.addEventListener('change', () => {{ handleFilterChange(); }});
            }});
            
            function getCookie(name) {{
                const value = '; ' + document.cookie;
                const parts = value.split('; ' + name + '=');
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }}
        </script>
    </body>
    </html>
    """
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error in dashboard_page: {e}", exc_info=True)
        return HTMLResponse(
            status_code=500,
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body>
                <h1>Internal Server Error</h1>
                <p>Error: {str(e)}</p>
                <p>Please check the server logs for more details.</p>
            </body>
            </html>
            """
        )


@router.get("/data")
async def get_dashboard_data(
    request: Request,
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    level: Optional[str] = Query('adset', description="Level: campaign, adset, or ad"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy dữ liệu dashboard với filters và pagination. Level: campaign/adset/ad"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        # Get user's accounts and prefixes
        account_ids, _ = get_user_account_prefixes(current_user.id, db)
        
        # Build base query
        base_query = db.query(AdMetrics).filter(AdMetrics.account_id.in_(account_ids))
        
        # Apply filters for stats
        stats_query = base_query
        if account_id and account_id in account_ids:
            stats_query = stats_query.filter(AdMetrics.account_id == account_id)
        if prefix:
            stats_query = stats_query.filter(AdMetrics.prefix == prefix)
        if campaign_type:
            stats_query = stats_query.filter(AdMetrics.campaign_type == campaign_type)
        if status:
            stats_query = stats_query.filter(AdMetrics.adset_status == status)
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from)
                stats_query = stats_query.filter(AdMetrics.date >= date_from_dt)
            except:
                pass
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to)
                date_to_dt = date_to_dt.replace(hour=23, minute=59, second=59)
                stats_query = stats_query.filter(AdMetrics.date <= date_to_dt)
            except:
                pass
        
        # Calculate stats
        total_spend = stats_query.with_entities(func.sum(AdMetrics.spend)).scalar() or 0
        total_results = stats_query.with_entities(func.sum(AdMetrics.results)).scalar() or 0
        avg_gia_data = stats_query.with_entities(func.avg(AdMetrics.gia_data)).scalar() or 0
        total_adsets_count = stats_query.with_entities(func.count(distinct(AdMetrics.adset_id))).scalar() or 0
        
        active_adsets_count = stats_query.filter(AdMetrics.adset_status == "ACTIVE").with_entities(
            func.count(distinct(AdMetrics.adset_id))
        ).scalar() or 0
        paused_adsets_count = stats_query.filter(AdMetrics.adset_status == "PAUSED").with_entities(
            func.count(distinct(AdMetrics.adset_id))
        ).scalar() or 0
        
        stats_result = {
            "total_spend": float(total_spend),
            "total_results": int(total_results),
            "avg_gia_data": float(avg_gia_data),
            "active_adsets": int(active_adsets_count),
            "paused_adsets": int(paused_adsets_count),
            "total_adsets": int(total_adsets_count)
        }
        
        if not account_ids:
            return {
                "stats": stats_result,
                "ads": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        # Build query for ads
        query = base_query
        
        # Apply filters for ads
        if account_id and account_id in account_ids:
            query = query.filter(AdMetrics.account_id == account_id)
        if prefix:
            query = query.filter(AdMetrics.prefix == prefix)
        if campaign_type:
            query = query.filter(AdMetrics.campaign_type == campaign_type)
        if status:
            query = query.filter(AdMetrics.adset_status == status)
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from)
                query = query.filter(AdMetrics.date >= date_from_dt)
            except:
                pass
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to)
                date_to_dt = date_to_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(AdMetrics.date <= date_to_dt)
            except:
                pass
        
        # Group by adset_id to aggregate metrics
        # Get distinct adsets
        adsets_query = query.with_entities(
            AdMetrics.adset_id,
            AdMetrics.adset_name,
            AdMetrics.campaign_name,
            AdMetrics.prefix,
            AdMetrics.account_id,
            AdMetrics.campaign_type,
            func.max(AdMetrics.adset_status).label('adset_status')
        ).group_by(
            AdMetrics.adset_id,
            AdMetrics.adset_name,
            AdMetrics.campaign_name,
            AdMetrics.prefix,
            AdMetrics.account_id,
            AdMetrics.campaign_type
        )
        
        # Get total count
        total = adsets_query.count()
        
        # Get paginated results
        adsets = adsets_query.offset((page - 1) * page_size).limit(page_size).all()
        
        # Get aggregated metrics for each adset
        ads_dict = []
        for adset in adsets:
            adset_metrics = query.filter(AdMetrics.adset_id == adset.adset_id).all()
            
            # Aggregate metrics
            total_spend = sum(m.spend or 0 for m in adset_metrics)
            total_results = sum(m.results or 0 for m in adset_metrics)
            total_impressions = sum(m.impressions or 0 for m in adset_metrics)
            total_clicks = sum(m.clicks or 0 for m in adset_metrics)
            total_purchases = sum(m.purchases or 0 for m in adset_metrics)
            total_purchase_value = sum(m.purchase_value or 0 for m in adset_metrics)
            
            # Calculate averages
            avg_gia_data = sum(m.gia_data or 0 for m in adset_metrics) / len(adset_metrics) if adset_metrics else 0
            avg_ctr = sum(m.ctr or 0 for m in adset_metrics) / len(adset_metrics) if adset_metrics else 0
            avg_cpc = sum(m.cpc or 0 for m in adset_metrics) / len(adset_metrics) if adset_metrics else 0
            
            # Calculate derived metrics
            cost_per_checkout_initiated = 0  # Cần lấy từ Facebook API hoặc tính từ checkouts
            checkouts_initiated = sum(m.sdt or 0 for m in adset_metrics)  # Sử dụng sdt như checkouts
            cost_per_purchase = (total_spend / total_purchases) if total_purchases > 0 else 0
            
            ads_dict.append({
                "adset_id": adset.adset_id,
                "adset_name": adset.adset_name,
                "campaign_name": adset.campaign_name,
                "prefix": adset.prefix,
                "account_id": adset.account_id,
                "campaign_type": adset.campaign_type,
                "adset_status": adset.adset_status,
                "spend": total_spend,
                "results": total_results,
                "gia_data": avg_gia_data,
                "impressions": total_impressions,
                "clicks": total_clicks,
                "ctr": avg_ctr,
                "cpc": avg_cpc,
                "purchases": total_purchases,
                "purchase_value": total_purchase_value,
                "cost_per_checkout_initiated": cost_per_checkout_initiated,
                "checkouts_initiated": checkouts_initiated,
                "cost_per_purchase": cost_per_purchase
            })
        
        # Sắp xếp theo Giá DATA từ cao xuống thấp
        ads_dict.sort(key=lambda x: x.get('gia_data', 0), reverse=True)
        
        return {
            "stats": stats_result,
            "ads": ads_dict,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu: {str(e)}")


@router.get("/filters")
async def get_filters(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách filters (accounts, prefixes)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        account_ids, prefixes = get_user_account_prefixes(current_user.id, db)
        
        # Get unique accounts from metrics
        accounts = db.query(AdMetrics.account_id.distinct()).filter(
            AdMetrics.account_id.in_(account_ids),
            AdMetrics.account_id.isnot(None)
        ).all()
        accounts = [acc[0] for acc in accounts if acc[0]]
        
        # Get unique prefixes from metrics
        prefixes_from_metrics = db.query(AdMetrics.prefix.distinct()).filter(
            AdMetrics.account_id.in_(account_ids),
            AdMetrics.prefix.isnot(None),
            AdMetrics.prefix.in_(prefixes) if prefixes else True
        ).all()
        prefixes_list = [pref[0] for pref in prefixes_from_metrics if pref[0]]
        
        return {
            "accounts": accounts,
            "prefixes": prefixes_list
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting filters: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy filters: {str(e)}")


@router.get("/prefix-summary")
async def get_prefix_summary(
    request: Request,
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy summary theo prefix (FL, NM, PX, etc.) cho cả E-commerce và Lead Generation"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        account_ids, prefixes = get_user_account_prefixes(current_user.id, db, enabled_only=True)
        
        if not account_ids:
            return {
                "prefixes": {},
                "ecommerce": {},
                "lead": {}
            }
        
        # Build base query
        base_query = db.query(AdMetrics).filter(AdMetrics.account_id.in_(account_ids))
        
        # Apply date filters
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from)
                base_query = base_query.filter(AdMetrics.date >= date_from_dt)
            except:
                pass
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to)
                date_to_dt = date_to_dt.replace(hour=23, minute=59, second=59)
                base_query = base_query.filter(AdMetrics.date <= date_to_dt)
            except:
                pass
        
        # Get all prefixes from metrics
        all_prefixes = db.query(AdMetrics.prefix.distinct()).filter(
            AdMetrics.account_id.in_(account_ids),
            AdMetrics.prefix.isnot(None)
        ).all()
        prefix_list = [pref[0] for pref in all_prefixes if pref[0]]
        
        prefix_summary = {}
        ecommerce_summary = {}
        lead_summary = {}
        
        for prefix in prefix_list:
            prefix_query = base_query.filter(AdMetrics.prefix == prefix)
            
            # Overall stats
            total_spend = prefix_query.with_entities(func.sum(AdMetrics.spend)).scalar() or 0
            total_results = prefix_query.with_entities(func.sum(AdMetrics.results)).scalar() or 0
            avg_gia_data = prefix_query.with_entities(func.avg(AdMetrics.gia_data)).scalar() or 0
            active_adsets = prefix_query.filter(AdMetrics.adset_status == "ACTIVE").with_entities(
                func.count(distinct(AdMetrics.adset_id))
            ).scalar() or 0
            total_adsets = prefix_query.with_entities(func.count(distinct(AdMetrics.adset_id))).scalar() or 0
            
            prefix_summary[prefix] = {
                "spend": float(total_spend),
                "results": int(total_results),
                "avg_gia_data": float(avg_gia_data),
                "active_adsets": int(active_adsets),
                "total_adsets": int(total_adsets),
                "cpl": float(total_spend / total_results) if total_results > 0 else 0
            }
            
            # E-commerce stats
            ecom_query = prefix_query.filter(AdMetrics.campaign_type == "ECOMMERCE")
            ecom_spend = ecom_query.with_entities(func.sum(AdMetrics.spend)).scalar() or 0
            ecom_results = ecom_query.with_entities(func.sum(AdMetrics.results)).scalar() or 0
            ecom_purchases = ecom_query.with_entities(func.sum(AdMetrics.purchases)).scalar() or 0
            ecom_purchase_value = ecom_query.with_entities(func.sum(AdMetrics.purchase_value)).scalar() or 0
            ecom_avg_gia_data = ecom_query.with_entities(func.avg(AdMetrics.gia_data)).scalar() or 0
            
            if ecom_spend > 0 or ecom_results > 0:
                ecommerce_summary[prefix] = {
                    "spend": float(ecom_spend),
                    "results": int(ecom_results),
                    "purchases": int(ecom_purchases),
                    "purchase_value": float(ecom_purchase_value),
                    "avg_gia_data": float(ecom_avg_gia_data),
                    "cpl": float(ecom_spend / ecom_results) if ecom_results > 0 else 0,
                    "roas": float(ecom_purchase_value / ecom_spend) if ecom_spend > 0 else 0
                }
            
            # Lead Generation stats
            lead_query = prefix_query.filter(AdMetrics.campaign_type == "LEAD")
            lead_spend = lead_query.with_entities(func.sum(AdMetrics.spend)).scalar() or 0
            lead_results = lead_query.with_entities(func.sum(AdMetrics.results)).scalar() or 0
            lead_avg_gia_data = lead_query.with_entities(func.avg(AdMetrics.gia_data)).scalar() or 0
            
            if lead_spend > 0 or lead_results > 0:
                lead_summary[prefix] = {
                    "spend": float(lead_spend),
                    "results": int(lead_results),
                    "avg_gia_data": float(lead_avg_gia_data),
                    "cpl": float(lead_spend / lead_results) if lead_results > 0 else 0
                }
        
        return {
            "prefixes": prefix_summary,
            "ecommerce": ecommerce_summary,
            "lead": lead_summary
        }
        
    except Exception as e:
        logger.error(f"Error getting prefix summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy prefix summary: {str(e)}")


@router.post("/adset/pause")
async def pause_adset(
    request: Request,
    adset_id: str = Query(...),
    account_id: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Tắt một adset"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        from app.models.user_settings import UserSettings
        from app.core.security import decrypt_token
        
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not user_settings or not user_settings.facebook_token_encrypted:
            raise HTTPException(status_code=400, detail="Chưa cấu hình Facebook token")
        
        token = decrypt_token(user_settings.facebook_token_encrypted)
        
        from app.services.facebook_api import pause_adsets
        
        result = pause_adsets([adset_id], token)
        
        if result.get("success", 0) > 0:
            return {
                "success": True,
                "message": f"Đã tắt adset {adset_id}",
                "adset_id": adset_id
            }
        else:
            error_msg = result.get("errorDetails", [{}])[0].get("error", "Unknown error") if result.get("errorDetails") else "Unknown error"
            raise HTTPException(status_code=400, detail=f"Lỗi khi tắt adset: {error_msg}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing adset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi tắt adset: {str(e)}")


@router.post("/adset/activate")
async def activate_adset(
    request: Request,
    adset_id: str = Query(...),
    account_id: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Bật một adset"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        from app.models.user_settings import UserSettings
        from app.core.security import decrypt_token
        
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not user_settings or not user_settings.facebook_token_encrypted:
            raise HTTPException(status_code=400, detail="Chưa cấu hình Facebook token")
        
        token = decrypt_token(user_settings.facebook_token_encrypted)
        
        from app.services.facebook_api import resume_adsets
        
        result = resume_adsets([adset_id], token)
        
        if result.get("success", 0) > 0:
            return {
                "success": True,
                "message": f"Đã bật adset {adset_id}",
                "adset_id": adset_id
            }
        else:
            error_msg = result.get("errorDetails", [{}])[0].get("error", "Unknown error") if result.get("errorDetails") else "Unknown error"
            raise HTTPException(status_code=400, detail=f"Lỗi khi bật adset: {error_msg}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating adset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi bật adset: {str(e)}")


@router.post("/adset/budget/increase")
async def increase_adset_budget(
    request: Request,
    adset_id: str = Query(...),
    percent: float = Query(10.0, ge=0.1, le=100.0),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Tăng ngân sách adset theo phần trăm"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        from app.models.user_settings import UserSettings
        from app.core.security import decrypt_token
        
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not user_settings or not user_settings.facebook_token_encrypted:
            raise HTTPException(status_code=400, detail="Chưa cấu hình Facebook token")
        
        token = decrypt_token(user_settings.facebook_token_encrypted)
        
        from app.services.facebook_api import update_adset_budget
        
        result = update_adset_budget(adset_id, token, action_type="increase", percent=percent)
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Đã tăng ngân sách adset {adset_id} thêm {percent}%",
                "adset_id": adset_id,
                "old_budget": result.get("old_budget"),
                "new_budget": result.get("new_budget")
            }
        else:
            raise HTTPException(status_code=400, detail=f"Lỗi khi tăng ngân sách: {result.get('error', 'Unknown error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error increasing adset budget: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi tăng ngân sách: {str(e)}")


@router.post("/adset/budget/decrease")
async def decrease_adset_budget(
    request: Request,
    adset_id: str = Query(...),
    percent: float = Query(10.0, ge=0.1, le=100.0),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Giảm ngân sách adset theo phần trăm"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        from app.models.user_settings import UserSettings
        from app.core.security import decrypt_token
        
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not user_settings or not user_settings.facebook_token_encrypted:
            raise HTTPException(status_code=400, detail="Chưa cấu hình Facebook token")
        
        token = decrypt_token(user_settings.facebook_token_encrypted)
        
        from app.services.facebook_api import update_adset_budget
        
        result = update_adset_budget(adset_id, token, action_type="decrease", percent=percent)
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Đã giảm ngân sách adset {adset_id} đi {percent}%",
                "adset_id": adset_id,
                "old_budget": result.get("old_budget"),
                "new_budget": result.get("new_budget")
            }
        else:
            raise HTTPException(status_code=400, detail=f"Lỗi khi giảm ngân sách: {result.get('error', 'Unknown error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error decreasing adset budget: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi giảm ngân sách: {str(e)}")


@router.post("/adset/budget")
async def set_adset_budget(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Set ngân sách adset với giá trị tuyệt đối"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        from app.models.user_settings import UserSettings
        from app.core.security import decrypt_token
        
        body = await request.json()
        adset_id = body.get("adset_id")
        daily_budget = body.get("daily_budget")
        
        if not adset_id or daily_budget is None:
            raise HTTPException(status_code=400, detail="Thiếu adset_id hoặc daily_budget")
        
        if daily_budget < 0:
            raise HTTPException(status_code=400, detail="Ngân sách phải >= 0")
        
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not user_settings or not user_settings.facebook_token_encrypted:
            raise HTTPException(status_code=400, detail="Chưa cấu hình Facebook token")
        
        token = decrypt_token(user_settings.facebook_token_encrypted)
        
        from app.services.facebook_api import update_adset_budget
        
        result = update_adset_budget(adset_id, token, action_type="set", amount=daily_budget)
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Đã cập nhật ngân sách adset {adset_id}",
                "adset_id": adset_id,
                "old_budget": result.get("old_budget"),
                "new_budget": result.get("new_budget")
            }
        else:
            raise HTTPException(status_code=400, detail=f"Lỗi khi cập nhật ngân sách: {result.get('error', 'Unknown error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting adset budget: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật ngân sách: {str(e)}")
