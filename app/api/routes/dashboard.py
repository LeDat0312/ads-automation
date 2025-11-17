"""
Modern Dashboard Implementation - Complete Rewrite
Tối ưu hóa giao diện và hiệu suất, giữ lại logic nghiệp vụ
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
    """Dashboard page với thiết kế mới tối ưu"""
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
        
        # Modern dashboard HTML với thiết kế mới
        html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📊 Dashboard - Facebook Ads Manager</title>
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary-color: #1877f2;
                --primary-hover: #166fe5;
                --secondary-color: #42b883;
                --danger-color: #e74c3c;
                --warning-color: #f39c12;
                --success-color: #27ae60;
                --gray-50: #f8fafc;
                --gray-100: #f1f5f9;
                --gray-200: #e2e8f0;
                --gray-300: #cbd5e1;
                --gray-400: #94a3b8;
                --gray-500: #64748b;
                --gray-600: #475569;
                --gray-700: #334155;
                --gray-800: #1e293b;
                --gray-900: #0f172a;
                --white: #ffffff;
                --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
                --radius-sm: 0.375rem;
                --radius-md: 0.5rem;
                --radius-lg: 0.75rem;
                --radius-xl: 1rem;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: var(--gray-800);
                line-height: 1.6;
            }}
            
            .container {{
                min-height: 100vh;
                padding: 1.5rem;
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            /* Header */
            .header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 2rem;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                border-radius: var(--radius-xl);
                padding: 1rem 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .header-title {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
                color: var(--white);
                font-size: 1.5rem;
                font-weight: 700;
            }}
            
            .header-actions {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }}
            
            .btn-home {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: rgba(255, 255, 255, 0.2);
                color: var(--white);
                text-decoration: none;
                border-radius: var(--radius-md);
                font-weight: 500;
                transition: all 0.2s ease;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            
            .btn-home:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-1px);
            }}
            
            /* Controls Bar */
            .controls-bar {{
                display: grid;
                grid-template-columns: auto 1fr auto auto auto;
                gap: 1rem;
                align-items: center;
                background: var(--white);
                padding: 1rem 1.5rem;
                border-radius: var(--radius-xl);
                box-shadow: var(--shadow-lg);
                margin-bottom: 2rem;
                border: 1px solid var(--gray-200);
            }}
            
            .filters-btn {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: var(--gray-50);
                border: 1px solid var(--gray-300);
                border-radius: var(--radius-md);
                cursor: pointer;
                transition: all 0.2s ease;
                font-weight: 500;
                position: relative;
            }}
            
            .filters-btn:hover {{
                background: var(--gray-100);
                border-color: var(--primary-color);
            }}
            
            .filters-badge {{
                position: absolute;
                top: -0.5rem;
                right: -0.5rem;
                background: var(--primary-color);
                color: var(--white);
                border-radius: 50%;
                width: 1.25rem;
                height: 1.25rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.75rem;
                font-weight: 600;
            }}
            
            .search-box {{
                position: relative;
                display: flex;
                align-items: center;
            }}
            
            .search-box input {{
                width: 100%;
                padding: 0.5rem 1rem 0.5rem 2.5rem;
                border: 1px solid var(--gray-300);
                border-radius: var(--radius-md);
                font-size: 0.875rem;
                transition: all 0.2s ease;
            }}
            
            .search-box input:focus {{
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(24, 119, 242, 0.1);
            }}
            
            .search-icon {{
                position: absolute;
                left: 0.75rem;
                color: var(--gray-400);
                pointer-events: none;
            }}
            
            .control-btn {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: var(--white);
                border: 1px solid var(--gray-300);
                border-radius: var(--radius-md);
                cursor: pointer;
                transition: all 0.2s ease;
                font-weight: 500;
                white-space: nowrap;
            }}
            
            .control-btn:hover {{
                background: var(--gray-50);
                border-color: var(--primary-color);
            }}
            
            .btn-refresh {{
                background: var(--primary-color);
                color: var(--white);
                border-color: var(--primary-color);
            }}
            
            .btn-refresh:hover {{
                background: var(--primary-hover);
            }}
            
            .btn-refresh.loading {{
                opacity: 0.7;
                pointer-events: none;
            }}
            
            /* Stats Grid */
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            
            .stat-card {{
                background: var(--white);
                padding: 1.5rem;
                border-radius: var(--radius-xl);
                box-shadow: var(--shadow-lg);
                border: 1px solid var(--gray-200);
                transition: all 0.3s ease;
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
                height: 3px;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            }}
            
            .stat-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1rem;
            }}
            
            .stat-label {{
                font-size: 0.875rem;
                font-weight: 600;
                color: var(--gray-600);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            
            .stat-icon {{
                font-size: 1.5rem;
                opacity: 0.8;
            }}
            
            .stat-value {{
                font-size: 2rem;
                font-weight: 800;
                color: var(--gray-900);
                margin-bottom: 0.5rem;
                transition: all 0.3s ease;
            }}
            
            .stat-change {{
                font-size: 0.75rem;
                color: var(--gray-500);
            }}
            
            /* Data Table */
            .table-container {{
                background: var(--white);
                border-radius: var(--radius-xl);
                box-shadow: var(--shadow-lg);
                border: 1px solid var(--gray-200);
                overflow: hidden;
                margin-bottom: 2rem;
            }}
            
            .table-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1.5rem 2rem;
                border-bottom: 1px solid var(--gray-200);
                background: var(--gray-50);
            }}
            
            .table-title {{
                display: flex;
                align-items: center;
                gap: 1rem;
            }}
            
            .table-title h2 {{
                font-size: 1.25rem;
                font-weight: 700;
                color: var(--gray-900);
            }}
            
            .view-tabs {{
                display: flex;
                gap: 0.25rem;
                background: var(--white);
                padding: 0.25rem;
                border-radius: var(--radius-md);
                border: 1px solid var(--gray-200);
            }}
            
            .view-tab {{
                padding: 0.5rem 1rem;
                background: transparent;
                border: none;
                border-radius: var(--radius-sm);
                font-size: 0.875rem;
                font-weight: 500;
                color: var(--gray-600);
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .view-tab:hover {{
                background: var(--gray-100);
                color: var(--gray-900);
            }}
            
            .view-tab.active {{
                background: var(--primary-color);
                color: var(--white);
            }}
            
            .table-actions {{
                display: flex;
                align-items: center;
                gap: 1rem;
            }}
            
            .btn-export {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: var(--success-color);
                color: var(--white);
                border: none;
                border-radius: var(--radius-md);
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .btn-export:hover {{
                background: #219a52;
                transform: translateY(-1px);
            }}
            
            .table-wrapper {{
                overflow-x: auto;
                max-height: 70vh;
                scrollbar-width: thin;
                scrollbar-color: var(--gray-300) transparent;
            }}
            
            .table-wrapper::-webkit-scrollbar {{
                height: 6px;
                width: 6px;
            }}
            
            .table-wrapper::-webkit-scrollbar-track {{
                background: transparent;
            }}
            
            .table-wrapper::-webkit-scrollbar-thumb {{
                background-color: var(--gray-300);
                border-radius: 3px;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th, td {{
                padding: 1rem;
                text-align: left;
                border-bottom: 1px solid var(--gray-200);
                font-size: 0.875rem;
            }}
            
            th {{
                background: var(--gray-50);
                font-weight: 600;
                color: var(--gray-700);
                text-transform: uppercase;
                font-size: 0.75rem;
                letter-spacing: 0.05em;
                cursor: pointer;
                user-select: none;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            
            th:hover {{
                background: var(--gray-100);
            }}
            
            tbody tr {{
                transition: all 0.2s ease;
            }}
            
            tbody tr:hover {{
                background: var(--gray-50);
            }}
            
            .number-cell {{
                text-align: right;
                font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
                font-weight: 500;
            }}
            
            /* Action Buttons */
            .action-buttons {{
                display: flex;
                gap: 0.5rem;
                align-items: center;
                justify-content: center;
            }}
            
            .btn-action {{
                padding: 0.375rem 0.75rem;
                border: none;
                border-radius: var(--radius-sm);
                font-size: 0.75rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                min-width: 2rem;
                height: 2rem;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .btn-action:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            .btn-pause {{
                background: #fee2e2;
                color: #991b1b;
            }}
            
            .btn-pause:hover:not(:disabled) {{
                background: #fecaca;
            }}
            
            .btn-activate {{
                background: #dcfce7;
                color: #166534;
            }}
            
            .btn-activate:hover:not(:disabled) {{
                background: #bbf7d0;
            }}
            
            .btn-budget {{
                background: #dbeafe;
                color: #1e40af;
            }}
            
            .btn-budget:hover:not(:disabled) {{
                background: #bfdbfe;
            }}
            
            /* Toggle Switch */
            .toggle-switch {{
                position: relative;
                display: inline-block;
                width: 3rem;
                height: 1.5rem;
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
                background-color: var(--gray-300);
                transition: 0.3s;
                border-radius: 1.5rem;
            }}
            
            .toggle-slider:before {{
                position: absolute;
                content: "";
                height: 1.125rem;
                width: 1.125rem;
                left: 0.1875rem;
                bottom: 0.1875rem;
                background-color: var(--white);
                transition: 0.3s;
                border-radius: 50%;
            }}
            
            .toggle-switch input:checked + .toggle-slider {{
                background-color: var(--success-color);
            }}
            
            .toggle-switch input:checked + .toggle-slider:before {{
                transform: translateX(1.5rem);
            }}
            
            /* Loading States */
            .loading {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 4rem 2rem;
                color: var(--gray-500);
            }}
            
            .loading-spinner {{
                width: 3rem;
                height: 3rem;
                border: 3px solid var(--gray-200);
                border-top-color: var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 1rem;
            }}
            
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            
            .skeleton {{
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s ease-in-out infinite;
                border-radius: var(--radius-sm);
            }}
            
            @keyframes shimmer {{
                0% {{ background-position: 200% 0; }}
                100% {{ background-position: -200% 0; }}
            }}
            
            /* Responsive Design */
            @media (max-width: 1024px) {{
                .container {{
                    padding: 1rem;
                }}
                
                .controls-bar {{
                    grid-template-columns: 1fr;
                    gap: 0.75rem;
                }}
                
                .stats-grid {{
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                }}
                
                .table-header {{
                    flex-direction: column;
                    gap: 1rem;
                    align-items: stretch;
                }}
                
                .table-title {{
                    justify-content: center;
                }}
                
                .table-actions {{
                    justify-content: center;
                }}
            }}
            
            @media (max-width: 768px) {{
                .header {{
                    flex-direction: column;
                    gap: 1rem;
                }}
                
                .header-title {{
                    font-size: 1.25rem;
                }}
                
                .stats-grid {{
                    grid-template-columns: 1fr 1fr;
                }}
                
                .view-tabs {{
                    width: 100%;
                    justify-content: center;
                }}
                
                th, td {{
                    padding: 0.75rem 0.5rem;
                    font-size: 0.8rem;
                }}
                
                .action-buttons {{
                    flex-direction: column;
                    gap: 0.25rem;
                }}
            }}
            
            /* Empty State */
            .empty-state {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 4rem 2rem;
                text-align: center;
                color: var(--gray-500);
            }}
            
            .empty-icon {{
                font-size: 4rem;
                margin-bottom: 1rem;
                opacity: 0.6;
            }}
            
            .empty-title {{
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--gray-700);
                margin-bottom: 0.5rem;
            }}
            
            .empty-description {{
                color: var(--gray-500);
                margin-bottom: 1.5rem;
            }}
            
            /* Utility Classes */
            .hidden {{
                display: none !important;
            }}
            
            .fade-in {{
                animation: fadeIn 0.3s ease-out;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <header class="header">
                <div class="header-title">
                    <span>📊</span>
                    <span>Facebook Ads Manager</span>
                </div>
                <div class="header-actions">
                    <a href="/" class="btn-home">
                        <span>←</span>
                        <span>Trang chủ</span>
                    </a>
                </div>
            </header>
            
            <!-- Controls Bar -->
            <div class="controls-bar">
                <button class="filters-btn" id="filtersBtn" onclick="toggleFilters()">
                    <span>⚙️</span>
                    <span>Bộ lọc</span>
                    <span class="filters-badge hidden" id="filtersBadge">0</span>
                </button>
                
                <div class="search-box">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="searchInput" placeholder="Tìm kiếm campaigns, adsets, ads..." onkeyup="handleSearch(event)">
                </div>
                
                <button class="control-btn" onclick="showDatePicker()">
                    <span>📅</span>
                    <span id="dateRangeText">Hôm nay</span>
                </button>
                
                <select class="control-btn" id="viewTypeSelect" onchange="handleViewChange()">
                    <option value="all">Tất cả</option>
                    <option value="ECOMMERCE">E-commerce</option>
                    <option value="LEAD">Lead Generation</option>
                </select>
                
                <button class="btn-refresh control-btn" id="refreshBtn" onclick="refreshData()">
                    <span>🔄</span>
                    <span>Làm mới</span>
                </button>
            </div>
            
            <!-- Stats Grid -->
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-label">Tổng Chi Tiêu</div>
                        <div class="stat-icon">💰</div>
                    </div>
                    <div class="stat-value" id="totalSpend">0 ₫</div>
                    <div class="stat-change">Tổng số tiền đã chi</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-label">Tổng Kết Quả</div>
                        <div class="stat-icon">📊</div>
                    </div>
                    <div class="stat-value" id="totalResults">0</div>
                    <div class="stat-change">Leads & Purchases</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-label">Giá DATA TB</div>
                        <div class="stat-icon">💵</div>
                    </div>
                    <div class="stat-value" id="avgGiaData">0 ₫</div>
                    <div class="stat-change">Chi phí trung bình</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-label">Đang Hoạt Động</div>
                        <div class="stat-icon">▶️</div>
                    </div>
                    <div class="stat-value" id="activeAdsets">0</div>
                    <div class="stat-change">Adsets active</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-label">Đã Tạm Dừng</div>
                        <div class="stat-icon">⏸️</div>
                    </div>
                    <div class="stat-value" id="pausedAdsets">0</div>
                    <div class="stat-change">Adsets paused</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-label">Tổng Adsets</div>
                        <div class="stat-icon">📈</div>
                    </div>
                    <div class="stat-value" id="totalAdsets">0</div>
                    <div class="stat-change">Tất cả adsets</div>
                </div>
            </div>
            
            <!-- Data Table -->
            <div class="table-container">
                <div class="table-header">
                    <div class="table-title">
                        <h2>Chi tiết Quảng cáo</h2>
                        <div class="view-tabs">
                            <button class="view-tab active" data-view="campaign" onclick="switchView('campaign', this)">Campaigns</button>
                            <button class="view-tab" data-view="adset" onclick="switchView('adset', this)">Adsets</button>
                            <button class="view-tab" data-view="ad" onclick="switchView('ad', this)">Ads</button>
                        </div>
                    </div>
                    <div class="table-actions">
                        <span id="tableInfo" style="color: var(--gray-600); font-size: 0.875rem;">Đang tải...</span>
                        <button class="btn-export" onclick="exportData()">
                            <span>📥</span>
                            <span>Export</span>
                        </button>
                    </div>
                </div>
                
                <div class="table-wrapper" id="tableWrapper">
                    <div class="loading">
                        <div class="loading-spinner"></div>
                        <div>Đang tải dữ liệu...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Global state
            let currentPage = 1;
            let pageSize = 50;
            let currentFilters = {{
                account: '',
                prefix: '',
                campaignType: '',
                status: '',
                dateFrom: '',
                dateTo: '',
                searchTerm: '',
                viewType: 'adset'
            }};
            let selectedDateRange = {{ start: null, end: null }};
            
            // Initialize page
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('Dashboard initialized');
                initializeDateRange();
                loadData();
            }});
            
            // Date handling
            function initializeDateRange() {{
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                selectedDateRange.start = new Date(today);
                selectedDateRange.end = new Date(today);
                selectedDateRange.end.setHours(23, 59, 59, 999);
                currentFilters.dateFrom = formatDateForAPI(today);
                currentFilters.dateTo = formatDateForAPI(today);
            }}
            
            function formatDateForAPI(date) {{
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                return `${{year}}-${{month}}-${{day}}`;
            }}
            
            function formatNumber(num) {{
                if (num === null || num === undefined || isNaN(num)) return '0';
                return new Intl.NumberFormat('vi-VN').format(num);
            }}
            
            // Data loading
            async function loadData() {{
                try {{
                    showTableLoading();
                    const params = buildAPIParams();
                    const response = await fetch(`/dashboard/data?${{params}}`, {{
                        headers: {{
                            'Authorization': `Bearer ${{getAuthToken()}}`
                        }}
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('Failed to load data');
                    }}
                    
                    const data = await response.json();
                    updateStats(data.stats || {{}});
                    renderTable(data.ads || [], data.total || 0);
                    
                }} catch (error) {{
                    console.error('Error loading data:', error);
                    showTableError('Lỗi khi tải dữ liệu: ' + error.message);
                }}
            }}
            
            function buildAPIParams() {{
                const params = new URLSearchParams({{
                    page: currentPage,
                    page_size: pageSize
                }});
                
                if (currentFilters.account) params.append('account_id', currentFilters.account);
                if (currentFilters.prefix) params.append('prefix', currentFilters.prefix);
                if (currentFilters.campaignType) params.append('campaign_type', currentFilters.campaignType);
                if (currentFilters.status) params.append('status', currentFilters.status);
                if (currentFilters.dateFrom) params.append('date_from', currentFilters.dateFrom);
                if (currentFilters.dateTo) params.append('date_to', currentFilters.dateTo);
                if (currentFilters.searchTerm) params.append('search', currentFilters.searchTerm);
                if (currentFilters.viewType) params.append('view_type', currentFilters.viewType);
                
                return params;
            }}
            
            function getAuthToken() {{
                return localStorage.getItem('access_token') || getCookie('access_token');
            }}
            
            function getCookie(name) {{
                const value = `; ${{document.cookie}}`;
                const parts = value.split(`; ${{name}}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }}
            
            // Stats update
            function updateStats(stats) {{
                function animateValue(element, start, end, duration = 800) {{
                    let startTime = null;
                    const step = (timestamp) => {{
                        if (!startTime) startTime = timestamp;
                        const progress = Math.min((timestamp - startTime) / duration, 1);
                        const value = Math.floor(progress * (end - start) + start);
                        
                        if (element.id === 'totalSpend' || element.id === 'avgGiaData') {{
                            element.textContent = formatNumber(value) + ' ₫';
                        }} else {{
                            element.textContent = formatNumber(value);
                        }}
                        
                        if (progress < 1) {{
                            window.requestAnimationFrame(step);
                        }}
                    }};
                    window.requestAnimationFrame(step);
                }}
                
                const elements = {{
                    totalSpend: document.getElementById('totalSpend'),
                    totalResults: document.getElementById('totalResults'),
                    avgGiaData: document.getElementById('avgGiaData'),
                    activeAdsets: document.getElementById('activeAdsets'),
                    pausedAdsets: document.getElementById('pausedAdsets'),
                    totalAdsets: document.getElementById('totalAdsets')
                }};
                
                Object.entries(elements).forEach(([key, element]) => {{
                    if (element && stats[key] !== undefined) {{
                        const currentValue = parseInt(element.textContent.replace(/[^0-9]/g, '')) || 0;
                        animateValue(element, currentValue, stats[key] || 0);
                    }}
                }});
            }}
            
            // Table rendering
            function showTableLoading() {{
                document.getElementById('tableWrapper').innerHTML = `
                    <div class="loading">
                        <div class="loading-spinner"></div>
                        <div>Đang tải dữ liệu...</div>
                    </div>
                `;
            }}
            
            function showTableError(message) {{
                document.getElementById('tableWrapper').innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">⚠️</div>
                        <div class="empty-title">Lỗi</div>
                        <div class="empty-description">${{message}}</div>
                    </div>
                `;
            }}
            
            function renderTable(ads, total) {{
                const tableInfo = document.getElementById('tableInfo');
                
                if (ads.length === 0) {{
                    document.getElementById('tableWrapper').innerHTML = `
                        <div class="empty-state">
                            <div class="empty-icon">📭</div>
                            <div class="empty-title">Không có dữ liệu</div>
                            <div class="empty-description">
                                Không tìm thấy dữ liệu phù hợp với bộ lọc hiện tại.
                            </div>
                        </div>
                    `;
                    tableInfo.textContent = 'Không có dữ liệu';
                    return;
                }}
                
                const viewType = currentFilters.viewType || 'adset';
                const nameColumn = viewType === 'campaign' ? 'Campaign' : 
                                  viewType === 'ad' ? 'Ad' : 'Adset';
                
                // Define columns based on campaign type
                const isEcommerce = currentFilters.campaignType === 'ECOMMERCE' || !currentFilters.campaignType;
                
                let tableHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 50px;">Trạng thái</th>
                                <th>${{nameColumn}}</th>
                                <th>Account</th>
                                <th>Prefix</th>
                                <th>Chi tiêu</th>
                                <th>Kết quả</th>
                                <th>Giá DATA</th>
                `;
                
                if (isEcommerce) {{
                    tableHTML += `
                                <th>ROAS</th>
                                <th>Purchases</th>
                    `;
                }}
                
                tableHTML += `
                                <th>CPM</th>
                                <th>CTR</th>
                                <th>CPC</th>
                                <th style="width: 200px;">Thao tác</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                ads.forEach(ad => {{
                    const entityId = viewType === 'campaign' ? ad.campaign_id : 
                                    viewType === 'ad' ? ad.ad_id : ad.adset_id;
                    const entityName = viewType === 'campaign' ? ad.campaign_name : 
                                      viewType === 'ad' ? ad.ad_name : ad.adset_name;
                    const isActive = (ad.adset_status || '').toUpperCase() === 'ACTIVE';
                    
                    tableHTML += `
                        <tr>
                            <td>
                                <label class="toggle-switch">
                                    <input type="checkbox" ${{isActive ? 'checked' : ''}} 
                                           onchange="toggleStatus('${{entityId}}', this.checked)">
                                    <span class="toggle-slider"></span>
                                </label>
                            </td>
                            <td>${{entityName || '-'}}</td>
                            <td>${{ad.account_id || '-'}}</td>
                            <td>${{ad.prefix || '-'}}</td>
                            <td class="number-cell">${{formatNumber(ad.spend || 0)}} ₫</td>
                            <td class="number-cell">${{formatNumber(ad.results || 0)}}</td>
                            <td class="number-cell">${{formatNumber(ad.gia_data || 0)}} ₫</td>
                    `;
                    
                    if (isEcommerce) {{
                        const roas = ad.purchase_value > 0 ? (ad.purchase_value / ad.spend) : 0;
                        tableHTML += `
                            <td class="number-cell">${{roas.toFixed(2)}}</td>
                            <td class="number-cell">${{formatNumber(ad.purchases || 0)}}</td>
                        `;
                    }}
                    
                    const cpm = ad.impressions > 0 ? (ad.spend / ad.impressions * 1000) : 0;
                    const ctr = ad.impressions > 0 ? (ad.clicks / ad.impressions * 100) : 0;
                    
                    tableHTML += `
                            <td class="number-cell">${{formatNumber(cpm.toFixed(0))}}</td>
                            <td class="number-cell">${{ctr.toFixed(2)}}%</td>
                            <td class="number-cell">${{formatNumber(ad.cpc || 0)}} ₫</td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn-action btn-${{isActive ? 'pause' : 'activate'}}" 
                                            onclick="toggleStatus('${{entityId}}', ${{!isActive}})"
                                            title="${{isActive ? 'Tắt' : 'Bật'}}">
                                        ${{isActive ? '⏸️' : '▶️'}}
                                    </button>
                                    <button class="btn-action btn-budget" 
                                            onclick="increaseBudget('${{entityId}}')"
                                            title="Tăng ngân sách">
                                        +20%
                                    </button>
                                    <button class="btn-action btn-budget" 
                                            onclick="decreaseBudget('${{entityId}}')"
                                            title="Giảm ngân sách">
                                        -20%
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                }});
                
                tableHTML += '</tbody></table>';
                
                document.getElementById('tableWrapper').innerHTML = tableHTML;
                document.getElementById('tableWrapper').classList.add('fade-in');
                
                tableInfo.textContent = `Hiển thị ${{ads.length}} / ${{total}} kết quả`;
            }}
            
            // Event handlers
            function handleSearch(event) {{
                currentFilters.searchTerm = event.target.value.trim();
                // Debounce search
                clearTimeout(window.searchTimeout);
                window.searchTimeout = setTimeout(() => {{
                    currentPage = 1;
                    loadData();
                }}, 300);
            }}
            
            function handleViewChange() {{
                const select = document.getElementById('viewTypeSelect');
                currentFilters.campaignType = select.value;
                currentPage = 1;
                loadData();
            }}
            
            function switchView(viewType, button) {{
                // Update active tab
                document.querySelectorAll('.view-tab').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                button.classList.add('active');
                
                currentFilters.viewType = viewType;
                currentPage = 1;
                loadData();
            }}
            
            function refreshData() {{
                const refreshBtn = document.getElementById('refreshBtn');
                refreshBtn.classList.add('loading');
                refreshBtn.disabled = true;
                
                loadData().finally(() => {{
                    refreshBtn.classList.remove('loading');
                    refreshBtn.disabled = false;
                }});
            }}
            
            // Action functions
            async function toggleStatus(entityId, isActive) {{
                try {{
                    const action = isActive ? 'activate' : 'pause';
                    const response = await fetch(`/dashboard/action/${{action}}/${{entityId}}`, {{
                        method: 'POST',
                        headers: {{
                            'Authorization': `Bearer ${{getAuthToken()}}`
                        }}
                    }});
                    
                    if (response.ok) {{
                        showNotification(`Đã ${{isActive ? 'bật' : 'tắt'}} thành công`, 'success');
                        loadData();
                    }} else {{
                        throw new Error('Failed to update status');
                    }}
                }} catch (error) {{
                    showNotification('Lỗi khi cập nhật trạng thái', 'error');
                    console.error('Error:', error);
                }}
            }}
            
            async function increaseBudget(entityId) {{
                try {{
                    const response = await fetch(`/dashboard/action/increase-budget/${{entityId}}`, {{
                        method: 'POST',
                        headers: {{
                            'Authorization': `Bearer ${{getAuthToken()}}`
                        }}
                    }});
                    
                    if (response.ok) {{
                        showNotification('Đã tăng ngân sách thành công', 'success');
                        loadData();
                    }} else {{
                        throw new Error('Failed to increase budget');
                    }}
                }} catch (error) {{
                    showNotification('Lỗi khi tăng ngân sách', 'error');
                    console.error('Error:', error);
                }}
            }}
            
            async function decreaseBudget(entityId) {{
                try {{
                    const response = await fetch(`/dashboard/action/decrease-budget/${{entityId}}`, {{
                        method: 'POST',
                        headers: {{
                            'Authorization': `Bearer ${{getAuthToken()}}`
                        }}
                    }});
                    
                    if (response.ok) {{
                        showNotification('Đã giảm ngân sách thành công', 'success');
                        loadData();
                    }} else {{
                        throw new Error('Failed to decrease budget');
                    }}
                }} catch (error) {{
                    showNotification('Lỗi khi giảm ngân sách', 'error');
                    console.error('Error:', error);
                }}
            }}
            
            // Utility functions
            function showNotification(message, type = 'info') {{
                // Create and show notification
                const notification = document.createElement('div');
                notification.style.cssText = `
                    position: fixed;
                    top: 2rem;
                    right: 2rem;
                    z-index: 1000;
                    padding: 1rem 1.5rem;
                    border-radius: var(--radius-md);
                    color: white;
                    font-weight: 500;
                    opacity: 0;
                    transform: translateX(100%);
                    transition: all 0.3s ease;
                `;
                
                notification.textContent = message;
                
                switch(type) {{
                    case 'success':
                        notification.style.background = 'var(--success-color)';
                        break;
                    case 'error':
                        notification.style.background = 'var(--danger-color)';
                        break;
                    default:
                        notification.style.background = 'var(--primary-color)';
                }}
                
                document.body.appendChild(notification);
                
                // Animate in
                setTimeout(() => {{
                    notification.style.opacity = '1';
                    notification.style.transform = 'translateX(0)';
                }}, 10);
                
                // Animate out and remove
                setTimeout(() => {{
                    notification.style.opacity = '0';
                    notification.style.transform = 'translateX(100%)';
                    setTimeout(() => {{
                        if (notification.parentElement) {{
                            notification.parentElement.removeChild(notification);
                        }}
                    }}, 300);
                }}, 3000);
            }}
            
            function exportData() {{
                showNotification('Tính năng export đang được phát triển', 'info');
            }}
            
            function toggleFilters() {{
                showNotification('Bộ lọc nâng cao đang được phát triển', 'info');
            }}
            
            function showDatePicker() {{
                showNotification('Date picker đang được phát triển', 'info');
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