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


def get_user_account_prefixes(user_id: int, db: Session) -> tuple[List[str], List[str]]:
    """Lấy danh sách account_ids và prefixes của user"""
    user_accounts = db.query(Account.account_id).filter(Account.user_id == user_id).all()
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
        
        user_menu = get_user_dropdown_menu(current_user)
        
        # Tạo HTML với date picker giống Facebook và UI đẹp
        # Sử dụng format string để tránh lỗi với user_menu có chứa {{}}
        html_content = """
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
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f5f5;
                color: #1e293b;
                line-height: 1.6;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px 32px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .header h1 {{
                font-size: 24px;
                font-weight: 700;
            }}
            
            .header-actions {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .btn-refresh {{
                padding: 8px 16px;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                color: white;
                cursor: pointer;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.2s;
            }}
            
            .btn-refresh:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
            
            .btn-refresh.loading {{
                opacity: 0.6;
                cursor: not-allowed;
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
            
            .container {{
                max-width: 1800px;
                margin: 0 auto;
                padding: 24px;
            }}
            
            .filters-section {{
                background: white;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 24px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            
            .filters-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}
            
            .filters-header h2 {{
                font-size: 18px;
                font-weight: 600;
            }}
            
            .filters-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                margin-bottom: 16px;
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
                padding: 10px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                transition: all 0.2s;
            }}
            
            .filter-group select:focus,
            .filter-group input:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                overflow: hidden;
            }}
            
            .table-header {{
                padding: 20px 24px;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .table-header h2 {{
                font-size: 18px;
                font-weight: 600;
            }}
            
            .table-wrapper {{
                overflow-x: auto;
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
            }}
            
            th {{
                background: #f8fafc;
                font-weight: 600;
                color: #475569;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            
            tbody tr:hover {{
                background: #f8fafc;
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
                padding: 60px 20px;
                color: #64748b;
            }}
            
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: #64748b;
            }}
            
            .empty-state .icon {{
                font-size: 48px;
                margin-bottom: 16px;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 24px;
            }}
            
            .stat-card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            
            .stat-card .label {{
                font-size: 13px;
                color: #64748b;
                margin-bottom: 8px;
                font-weight: 500;
            }}
            
            .stat-card .value {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
            }}
        </style>
    </head>
    <body>
        """ + user_menu + """
        <div class="header">
            <h1>📊 Dashboard - Tổng Quan Hiệu Suất</h1>
            <div class="header-actions">
                <button class="btn-refresh" onclick="refreshData()" id="refreshBtn">
                    🔄 Làm mới
                </button>
            </div>
        </div>
        
        <div class="container">
            <div class="filters-section">
                <div class="filters-header">
                    <h2>🔍 Bộ Lọc</h2>
                </div>
                <div class="filters-grid">
                    <div class="filter-group">
                        <label>Account</label>
                        <select id="accountFilter">
                            <option value="">Tất cả Accounts</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Prefix</label>
                        <select id="prefixFilter">
                            <option value="">Tất cả Prefixes</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Loại Campaign</label>
                        <select id="campaignTypeFilter">
                            <option value="">Tất cả</option>
                            <option value="ECOMMERCE">E-commerce</option>
                            <option value="LEAD">Lead Generation</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Trạng thái</label>
                        <select id="statusFilter">
                            <option value="">Tất cả</option>
                            <option value="ACTIVE">Active</option>
                            <option value="PAUSED">Paused</option>
                        </select>
                    </div>
                    <div class="filter-group date-picker-wrapper">
                        <label>Khoảng thời gian</label>
                        <div class="date-picker-btn" onclick="openDatePicker()">
                            <span id="dateRangeText">Chọn khoảng thời gian</span>
                            <span>📅</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card">
                    <div class="label">Tổng Chi Tiêu</div>
                    <div class="value" id="totalSpend">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Tổng Kết Quả</div>
                    <div class="value" id="totalResults">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Giá DATA Trung Bình</div>
                    <div class="value" id="avgGiaData">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Adsets Hoạt Động</div>
                    <div class="value" id="activeAdsets">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Adsets Đã Tạm Dừng</div>
                    <div class="value" id="pausedAdsets">0</div>
                </div>
                <div class="stat-card">
                    <div class="label">Tổng Adsets</div>
                    <div class="value" id="totalAdsets">0</div>
                </div>
            </div>
            
            <div class="table-container">
                <div class="table-header">
                    <h2>📈 Dữ Liệu Quảng Cáo</h2>
                    <div id="tableInfo"></div>
                </div>
                <div class="table-wrapper" id="tableWrapper">
                    <div class="loading">Đang tải dữ liệu...</div>
                </div>
                <div class="pagination" id="pagination"></div>
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
            // Wrap toàn bộ code trong try-catch để bắt lỗi
            try {{
                // Đảm bảo các biến và function ở global scope
                window.currentPage = 1;
                window.pageSize = 50;
                window.selectedDateRange = {{ start: null, end: null }};
                window.currentFilters = {{
                    account: '',
                    prefix: '',
                    campaignType: '',
                    status: '',
                    dateFrom: '',
                    dateTo: ''
                }};
                
                // Alias cho backward compatibility
                let currentPage = window.currentPage;
                const pageSize = window.pageSize;
                let selectedDateRange = window.selectedDateRange;
                let currentFilters = window.currentFilters;
                
                console.log('✅ Dashboard script started');
            
            // Date Picker Logic - Đảm bảo ở global scope
            window.openDatePicker = function openDatePicker() {{
                document.getElementById('datePickerModal').classList.add('active');
                renderCalendars();
            }};
            
            window.closeDatePicker = function closeDatePicker() {{
                document.getElementById('datePickerModal').classList.remove('active');
            }};
            
            window.closeDatePickerOnOverlay = function closeDatePickerOnOverlay(event) {{
                if (event.target.id === 'datePickerModal') {{
                    closeDatePicker();
                }}
            }};
            
            window.selectQuickDate = function selectQuickDate(type) {{
                const today = new Date();
                let start, end;
                
                switch(type) {{
                    case 'today':
                        start = new Date(today);
                        end = new Date(today);
                        break;
                    case 'yesterday':
                        start = new Date(today);
                        start.setDate(start.getDate() - 1);
                        end = new Date(start);
                        break;
                    case 'last7days':
                        start = new Date(today);
                        start.setDate(start.getDate() - 6);
                        end = new Date(today);
                        break;
                    case 'last14days':
                        start = new Date(today);
                        start.setDate(start.getDate() - 13);
                        end = new Date(today);
                        break;
                    case 'last30days':
                        start = new Date(today);
                        start.setDate(start.getDate() - 29);
                        end = new Date(today);
                        break;
                    case 'thisMonth':
                        start = new Date(today.getFullYear(), today.getMonth(), 1);
                        end = new Date(today);
                        break;
                    case 'lastMonth':
                        start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                        end = new Date(today.getFullYear(), today.getMonth(), 0);
                        break;
                }}
                
                selectedDateRange.start = start;
                selectedDateRange.end = end;
                renderCalendars();
                applyDateRange();
            }};
            
            window.renderCalendars = function renderCalendars() {{
                const container = document.getElementById('calendarsContainer');
                const startMonth = new Date(currentCalendarYear, currentCalendarMonth, 1);
                const endMonth = new Date(currentCalendarYear, currentCalendarMonth + 1, 1);
                
                container.innerHTML = renderCalendar(startMonth) + renderCalendar(endMonth);
            }};
            
            window.renderCalendar = function renderCalendar(date) {{
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
            }};
            
            window.selectDate = function selectDate(year, month, day) {{
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
            }};
            
            let currentCalendarMonth = new Date().getMonth();
            let currentCalendarYear = new Date().getFullYear();
            
            window.changeMonth = function changeMonth(delta) {{
                currentCalendarMonth += delta;
                if (currentCalendarMonth < 0) {{
                    currentCalendarMonth = 11;
                    currentCalendarYear--;
                }} else if (currentCalendarMonth > 11) {{
                    currentCalendarMonth = 0;
                    currentCalendarYear++;
                }}
                renderCalendars();
            }};
            
            window.changeMonthBySelect = function changeMonthBySelect(monthIndex) {{
                currentCalendarMonth = parseInt(monthIndex);
                renderCalendars();
            }};
            
            window.changeYearBySelect = function changeYearBySelect(yearValue) {{
                currentCalendarYear = parseInt(yearValue);
                renderCalendars();
            }};
            
            window.applyDateRange = function applyDateRange() {{
                if (selectedDateRange.start && selectedDateRange.end) {{
                    const startStr = selectedDateRange.start.toISOString().split('T')[0];
                    const endStr = selectedDateRange.end.toISOString().split('T')[0];
                    currentFilters.dateFrom = startStr;
                    currentFilters.dateTo = endStr;
                    
                    const startFormatted = formatDateVN(selectedDateRange.start);
                    const endFormatted = formatDateVN(selectedDateRange.end);
                    document.getElementById('dateRangeText').textContent = startFormatted + ' - ' + endFormatted;
                    
                    closeDatePicker();
                    loadData();
                }}
            }};
            
            window.formatDateVN = function formatDateVN(date) {{
                const day = date.getDate();
                const month = date.getMonth() + 1;
                const year = date.getFullYear();
                return day + ' Tháng ' + month + ', ' + year;
            }};
            
            // Load data - Đảm bảo ở global scope
            window.loadData = async function loadData() {{
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
                    document.getElementById('tableWrapper').innerHTML = '<div class="loading">Đang tải dữ liệu...</div>';
                    
                    const token = localStorage.getItem('access_token') || getCookie('access_token');
                    const response = await fetch('/dashboard/data?' + params.toString(), {{
                        headers: {{
                            'Authorization': 'Bearer ' + token
                        }}
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        let errorMsg = 'Failed to load data';
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMsg = errorJson.detail || errorJson.message || errorMsg;
                        }} catch {{
                            errorMsg = errorText.substring(0, 200);
                        }}
                        throw new Error(errorMsg);
                    }}
                    
                    const data = await response.json();
                    console.log('Dashboard data received:', data);
                    
                    if (data.stats) {{
                        updateStats(data.stats);
                    }} else {{
                        // Nếu không có stats, set về 0
                        updateStats({{
                            total_spend: 0,
                            total_results: 0,
                            avg_gia_data: 0,
                            active_adsets: 0,
                            paused_adsets: 0,
                            total_adsets: 0
                        }});
                    }}
                    
                    renderTable(data);
                }} catch (error) {{
                    console.error('Error loading data:', error);
                    const errorMsg = error.message || 'Lỗi khi tải dữ liệu';
                    document.getElementById('tableWrapper').innerHTML = 
                        '<div class="empty-state"><div class="icon">⚠️</div><p>Lỗi khi tải dữ liệu</p><p style="font-size: 12px; color: #94a3b8;">' + errorMsg + '</p></div>';
                    // Cũng reset stats về 0 khi có lỗi
                    updateStats({{
                        total_spend: 0,
                        total_results: 0,
                        avg_gia_data: 0,
                        active_adsets: 0,
                        paused_adsets: 0,
                        total_adsets: 0
                    }});
                }}
            }}
            
            window.updateStats = function updateStats(stats) {{
                try {{
                    console.log('updateStats() called with:', stats);
                    document.getElementById('totalSpend').textContent = formatNumber(stats.total_spend || 0);
                    document.getElementById('totalResults').textContent = formatNumber(stats.total_results || 0);
                    document.getElementById('avgGiaData').textContent = formatNumber(stats.avg_gia_data || 0);
                    document.getElementById('activeAdsets').textContent = formatNumber(stats.active_adsets || 0);
                    document.getElementById('pausedAdsets').textContent = formatNumber(stats.paused_adsets || 0);
                    document.getElementById('totalAdsets').textContent = formatNumber(stats.total_adsets || 0);
                    console.log('✅ updateStats() completed');
                }} catch (error) {{
                    console.error('❌ Error in updateStats():', error);
                }}
            }}
            
            window.renderTable = function renderTable(data) {{
                try {{
                    console.log('renderTable() called with:', {{
                        ads_count: data.ads ? data.ads.length : 0,
                        total: data.total,
                        has_stats: !!data.stats
                    }});
                    const ads = data.ads || [];
                    const total = data.total || 0;
                    const campaignType = currentFilters.campaignType || '';
                    
                    if (ads.length === 0) {{
                        console.log('⚠️ No ads to display');
                        document.getElementById('tableWrapper').innerHTML = 
                            '<div class="empty-state"><div class="icon">📭</div><p>Không có dữ liệu</p><p style="font-size: 12px; color: #94a3b8; margin-top: 8px;">Vui lòng kiểm tra lại bộ lọc hoặc cấu hình accounts/prefixes trong Settings</p></div>';
                        document.getElementById('tableInfo').textContent = 'Hiển thị 0 / 0 kết quả';
                        document.getElementById('pagination').innerHTML = '';
                        return;
                    }}
                    
                    console.log(`✅ Rendering ${ads.length} ads...`);
                
                // Define columns based on campaign type
                const columns = campaignType === 'ECOMMERCE' ? [
                    'Tắt/Bật', 'Tên nhóm quảng cáo', 'Phân phối', 'Ngân sách', 'Số tiền chi tiêu',
                    '% ADS', 'Kết quả', 'Giá DATA', 'Chi phí trên mỗi lượt bắt đầu thanh toán',
                    'Tổng số lượt bắt đầu thanh toán', 'Chi phí trên mỗi lượt mua', 'Tổng số lượt mua',
                    'Giá trị chuyển đổi từ lượt mua', 'CPM', 'Lượt hiển thị', 'Số lần nhấp (tất cả)',
                    'CTR (tất cả)', 'CPC (tất cả)'
                ] : [
                    'Tắt/Bật', 'Tên nhóm quảng cáo', 'Phân phối', 'Ngân sách', 'Số tiền chi tiêu',
                    'Kết quả', 'Giá DATA', 'Chi phí trên mỗi lượt bắt đầu thanh toán',
                    'Tổng số lượt bắt đầu thanh toán', 'Chi phí trên mỗi lượt mua', 'Tổng số lượt mua',
                    'CPM', 'Lượt hiển thị', 'Số lần nhấp (tất cả)', 'CTR (tất cả)', 'CPC (tất cả)'
                ];
                
                let html = '<table><thead><tr>';
                columns.forEach(col => {{
                    html += '<th>' + col + '</th>';
                }});
                html += '</tr></thead><tbody>';
                
                ads.forEach(ad => {{
                    html += '<tr>';
                    html += '<td><span class="status-badge status-' + (ad.adset_status || '').toLowerCase() + '">' + (ad.adset_status || '') + '</span></td>';
                    html += '<td>' + (ad.adset_name || '') + '</td>';
                    html += '<td>-</td>'; // Phân phối - cần lấy từ API
                    html += '<td>-</td>'; // Ngân sách - cần lấy từ API
                    html += '<td>' + formatNumber(ad.spend || 0) + '</td>';
                    
                    if (campaignType === 'ECOMMERCE') {{
                        const percentAds = ad.purchase_value > 0 ? ((ad.spend / ad.purchase_value) * 100).toFixed(2) : '0';
                        const alertBadge = parseFloat(percentAds) > 25 ? '<span class="alert-badge">⚠️</span>' : '';
                        html += '<td>' + percentAds + '% ' + alertBadge + '</td>';
                    }}
                    
                    html += '<td>' + formatNumber(ad.results || 0) + '</td>';
                    
                    const giaData = ad.gia_data || 0;
                    // Chỉ hiển thị cảnh báo cho E-commerce
                    const showGiaDataAlert = campaignType === 'ECOMMERCE' && giaData > 10000;
                    const giaDataAlert = showGiaDataAlert ? '<span class="alert-badge">⚠️</span>' : '';
                    html += '<td>' + formatNumber(giaData) + ' ' + giaDataAlert + '</td>';
                    
                    const costPerCheckout = ad.cost_per_checkout_initiated || 0;
                    html += '<td>' + formatNumber(costPerCheckout) + '</td>';
                    html += '<td>' + formatNumber(ad.checkouts_initiated || 0) + '</td>';
                    
                    const costPerPurchase = ad.cost_per_purchase || 0;
                    html += '<td>' + formatNumber(costPerPurchase) + '</td>';
                    html += '<td>' + formatNumber(ad.purchases || 0) + '</td>';
                    
                    if (campaignType === 'ECOMMERCE') {{
                        html += '<td>' + formatNumber(ad.purchase_value || 0) + '</td>';
                    }}
                    
                    const cpm = ad.impressions > 0 ? ((ad.spend / ad.impressions) * 1000).toFixed(2) : '0';
                    html += '<td>' + formatNumber(cpm) + '</td>';
                    html += '<td>' + formatNumber(ad.impressions || 0) + '</td>';
                    html += '<td>' + formatNumber(ad.clicks || 0) + '</td>';
                    html += '<td>' + ((ad.ctr || 0)).toFixed(2) + '%</td>';
                    html += '<td>' + formatNumber(ad.cpc || 0) + '</td>';
                    html += '</tr>';
                }});
                
                    html += '</tbody></table>';
                    document.getElementById('tableWrapper').innerHTML = html;
                    
                    // Pagination
                    const totalPages = Math.ceil(total / pageSize);
                    renderPagination(totalPages);
                    
                    document.getElementById('tableInfo').textContent = 
                        'Hiển thị ' + ads.length + ' / ' + total + ' kết quả';
                    
                    console.log('✅ renderTable() completed successfully');
                }} catch (error) {{
                    console.error('❌ Error in renderTable():', error);
                    document.getElementById('tableWrapper').innerHTML = 
                        '<div class="empty-state"><div class="icon">⚠️</div><p>Lỗi khi render bảng</p><p style="font-size: 12px; color: #94a3b8;">' + error.message + '</p></div>';
                }}
            }}
            
            window.renderPagination = function renderPagination(totalPages) {{
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
            }};
            
            window.goToPage = function goToPage(page) {{
                currentPage = page;
                loadData();
            }};
            
            window.formatNumber = function formatNumber(num) {{
                return new Intl.NumberFormat('vi-VN').format(num);
            }};
            
            // Pull dữ liệu từ Facebook (tự động, không hiển thị thông báo)
            window.pullFacebookDataSilent = async function pullFacebookDataSilent() {{
                try {{
                    const response = await fetch('/dashboard/pull-data', {{
                        method: 'POST',
                        headers: {{
                            'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || getCookie('access_token'))
                        }}
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok && data.success) {{
                        console.log('✅ Đã pull dữ liệu:', data.count + ' adsets');
                        return true;
                    }} else {{
                        console.warn('⚠️ Pull dữ liệu:', data.message || data.detail || 'Không có dữ liệu mới');
                        return false;
                    }}
                }} catch (error) {{
                    console.error('❌ Lỗi khi pull dữ liệu:', error.message);
                    return false;
                }}
            }}
            
            window.refreshData = async function refreshData() {{
                const btn = document.getElementById('refreshBtn');
                btn.classList.add('loading');
                btn.disabled = true;
                
                // Pull dữ liệu mới từ Facebook trước khi load
                await pullFacebookDataSilent();
                
                // Sau đó load dữ liệu từ database
                await loadData();
                
                setTimeout(() => {{
                    btn.classList.remove('loading');
                    btn.disabled = false;
                }}, 500);
            }}
            
            window.loadFilters = async function loadFilters() {{
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
            
            // Set default date to today
            window.addEventListener('DOMContentLoaded', async () => {{
                console.log('✅ DOMContentLoaded fired');
                try {{
                    const today = new Date();
                    selectedDateRange.start = today;
                    selectedDateRange.end = today;
                    currentFilters.dateFrom = today.toISOString().split('T')[0];
                    currentFilters.dateTo = today.toISOString().split('T')[0];
                    document.getElementById('dateRangeText').textContent = formatDateVN(today) + ' - ' + formatDateVN(today);
                    
                    console.log('✅ Date range initialized');
                    
                    // Load filters trước
                    console.log('🔄 Loading filters...');
                    await loadFilters();
                    console.log('✅ Filters loaded');
                    
                    // Pull dữ liệu mới từ Facebook khi trang load (giống Facebook Ads Manager)
                    console.log('🔄 Pulling Facebook data...');
                    await pullFacebookDataSilent();
                    console.log('✅ Facebook data pulled');
                    
                    // Sau đó load dữ liệu từ database
                    console.log('🔄 Loading dashboard data...');
                    loadData();
                }} catch (error) {{
                    console.error('❌ Error in DOMContentLoaded:', error);
                }}
                
                // Add event listeners for filters
                try {{
                    document.getElementById('accountFilter').addEventListener('change', loadData);
                    document.getElementById('prefixFilter').addEventListener('change', loadData);
                    document.getElementById('campaignTypeFilter').addEventListener('change', loadData);
                    document.getElementById('statusFilter').addEventListener('change', loadData);
                    console.log('✅ Event listeners added');
                }} catch (error) {{
                    console.error('❌ Error adding event listeners:', error);
                }}
            }});
            
            window.getCookie = function getCookie(name) {{
                const value = '; ' + document.cookie;
                const parts = value.split('; ' + name + '=');
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }};
            
            window.logout = function logout() {{
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                // Clear cookie
                document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
                window.location.href = '/auth/login';
            }};
            
            console.log('✅ All functions defined');
            }} catch (error) {{
                console.error('❌ CRITICAL ERROR in Dashboard script:', error);
                console.error('Error stack:', error.stack);
                // Hiển thị lỗi trên trang
                document.body.innerHTML = '<div style="padding: 20px; color: red;"><h1>❌ Lỗi JavaScript</h1><p>' + error.message + '</p><pre>' + error.stack + '</pre></div>';
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
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy dữ liệu dashboard với filters và pagination"""
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


@router.post("/pull-data")
async def pull_facebook_data_endpoint(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Pull dữ liệu từ Facebook cho các accounts được bật
    Chỉ lấy adsets ACTIVE của hôm nay
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        # Lấy token từ UserSettings
        from app.models.user_settings import UserSettings
        from app.core.security import decrypt_token
        
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not user_settings or not user_settings.facebook_token_encrypted:
            raise HTTPException(status_code=400, detail="Chưa cấu hình Facebook token. Vui lòng vào Settings để thêm token.")
        
        token = decrypt_token(user_settings.facebook_token_encrypted)
        
        # Lấy danh sách accounts được bật
        enabled_accounts = db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.enabled == True
        ).all()
        
        if not enabled_accounts:
            return {
                "success": False,
                "message": "Không có accounts nào được bật. Vui lòng bật ít nhất một account trong Settings.",
                "count": 0
            }
        
        account_ids = [acc.account_id for acc in enabled_accounts]
        logger.info(f"Đang pull dữ liệu cho {len(account_ids)} accounts được bật: {account_ids}")
        
        # Pull dữ liệu từ Facebook
        from app.services.facebook_api import pull_facebook_adset_data
        from pytz import timezone as tz
        
        tz_vn = tz('Asia/Ho_Chi_Minh')
        today = datetime.now(tz_vn).replace(hour=0, minute=0, second=0, microsecond=0)
        
        ad_metrics_list = pull_facebook_adset_data(
            access_token=token,
            ad_account_ids=account_ids,
            date_preset="today",
            only_active=True  # Chỉ lấy adsets ACTIVE
        )
        
        if not ad_metrics_list:
            return {
                "success": True,
                "message": "Không có dữ liệu mới từ Facebook (có thể chưa có dữ liệu hôm nay hoặc không có adsets ACTIVE)",
                "count": 0
            }
        
        # Lưu vào database
        saved_count = 0
        updated_count = 0
        
        for ad_metric in ad_metrics_list:
            # Đảm bảo date là hôm nay
            ad_metric['date'] = datetime.now(tz_vn)
            
            # Kiểm tra xem đã có chưa (chỉ check trong ngày hôm nay, theo adset_id)
            existing = db.query(AdMetrics).filter(
                AdMetrics.adset_id == ad_metric.get('adset_id'),
                AdMetrics.account_id == ad_metric.get('account_id'),
                AdMetrics.date >= today
            ).first()
            
            if existing:
                # Update
                for key, value in ad_metric.items():
                    if hasattr(existing, key) and not key.startswith('_'):
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                updated_count += 1
            else:
                # Create new
                valid_fields = {
                    'adset_id', 'ad_id', 'ad_name', 'adset_name', 'campaign_name', 'campaign_id',
                    'account_id', 'account_name', 'prefix', 'spend', 'impressions', 'clicks', 'results',
                    'ctr', 'cpc', 'cpa', 'roas', 'gia_data', 'sdt', 'gia_sdt', 'ty_le_sdt',
                    'adset_status', 'effective_status', 'date', 'date_preset',
                    'campaign_type', 'campaign_objective', 'amount_spent', 'ket_qua',
                    'purchases', 'purchase_value', 'revenue', 'leads', 'phone_calls',
                    'cost_per_lead'
                }
                
                ad_metric_dict = {k: v for k, v in ad_metric.items() if k in valid_fields}
                new_metric = AdMetrics(**ad_metric_dict)
                db.add(new_metric)
                saved_count += 1
        
        db.commit()
        
        logger.info(f"✅ Đã pull và lưu {saved_count} records mới, cập nhật {updated_count} records")
        
        return {
            "success": True,
            "message": f"Đã pull thành công {len(ad_metrics_list)} adsets từ {len(account_ids)} accounts. Lưu {saved_count} mới, cập nhật {updated_count}.",
            "count": len(ad_metrics_list),
            "saved": saved_count,
            "updated": updated_count,
            "accounts": account_ids
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pulling Facebook data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi pull dữ liệu: {str(e)}")


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
