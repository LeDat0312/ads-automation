"""
Dashboard API Routes
API endpoints cho automation overview dashboard
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, distinct

from app.core.database import get_db, AdMetrics, AutomationStatus
from app.models.logic_rule import LogicRule
from app.models.account_prefix import Account
from app.core.config import get_settings
from app.api.routes.auth import get_current_user_optional
from app.models.user import User
from app.core.ui_helpers import get_user_dropdown_menu, get_account_locked_message
from typing import Optional

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/")
async def dashboard_home(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Serve dashboard HTML page"""
    
    # Check if user is locked
    if current_user and not current_user.is_active:
        return HTMLResponse(content=get_account_locked_message())
    
    if not current_user:
        return HTMLResponse(content="""
        <script>
            window.location.href = '/auth/login';
        </script>
        """)
    
    user_menu = get_user_dropdown_menu(current_user)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facebook Ads Automation - Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #f5f5f5;
                color: #333;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header h1 {
                font-size: 24px;
                margin-bottom: 10px;
            }
            .header p {
                opacity: 0.9;
            }
            .container {
                max-width: 1400px;
                margin: 20px auto;
                padding: 0 20px;
            }
            .filters {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .filters h2 {
                margin-bottom: 15px;
                font-size: 18px;
            }
            .filter-row {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin-bottom: 15px;
            }
            .filter-group {
                flex: 1;
                min-width: 200px;
            }
            .filter-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                font-size: 14px;
            }
            .filter-group select,
            .filter-group input {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            .btn {
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
            }
            .btn:hover {
                background: #5568d3;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .stat-card h3 {
                font-size: 14px;
                color: #666;
                margin-bottom: 10px;
            }
            .stat-card .value {
                font-size: 28px;
                font-weight: bold;
                color: #333;
            }
            .stat-card .change {
                font-size: 12px;
                margin-top: 5px;
            }
            .stat-card .change.positive {
                color: #10b981;
            }
            .stat-card .change.negative {
                color: #ef4444;
            }
            .table-container {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .table-header {
                padding: 20px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .table-header h2 {
                font-size: 18px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }
            th {
                background: #f9fafb;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                color: #666;
            }
            td {
                font-size: 14px;
            }
            tr:hover {
                background: #f9fafb;
            }
            .status-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }
            .status-active {
                background: #d1fae5;
                color: #065f46;
            }
            .status-paused {
                background: #fee2e2;
                color: #991b1b;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            .pagination {
                padding: 20px;
                display: flex;
                justify-content: center;
                gap: 10px;
            }
            .pagination button {
                padding: 8px 12px;
                border: 1px solid #ddd;
                background: white;
                border-radius: 4px;
                cursor: pointer;
            }
            .pagination button:hover {
                background: #f9fafb;
            }
            .pagination button.active {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }
        </style>
    </head>
    <body>
        {user_menu}
        <div class="header">
            <h1>🚀 Facebook Ads Automation Dashboard</h1>
            <p>Automation Overview & Performance Metrics</p>
        </div>
        <div class="container">
            <div class="filters">
                <h2>🔍 Filters</h2>
                <div class="filter-row">
                    <div class="filter-group">
                        <label>Account ID</label>
                        <select id="accountFilter">
                            <option value="">All Accounts</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Prefix</label>
                        <select id="prefixFilter">
                            <option value="">All Prefixes</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Status</label>
                        <select id="statusFilter">
                            <option value="">All Status</option>
                            <option value="ACTIVE">Active</option>
                            <option value="PAUSED">Paused</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Date Range</label>
                        <input type="date" id="dateFrom" />
                    </div>
                    <div class="filter-group">
                        <label>&nbsp;</label>
                        <input type="date" id="dateTo" />
                    </div>
                </div>
                <button class="btn" onclick="loadData()">Apply Filters</button>
                <button class="btn" onclick="exportData()" style="background: #10b981; margin-left: 10px;">Export CSV</button>
            </div>
            <div class="stats" id="stats">
                <div class="stat-card">
                    <h3>Total Spend</h3>
                    <div class="value" id="totalSpend">0</div>
                </div>
                <div class="stat-card">
                    <h3>Total Results</h3>
                    <div class="value" id="totalResults">0</div>
                </div>
                <div class="stat-card">
                    <h3>Avg Giá DATA</h3>
                    <div class="value" id="avgGiaData">0</div>
                </div>
                <div class="stat-card">
                    <h3>Active Adsets</h3>
                    <div class="value" id="activeAdsets">0</div>
                </div>
                <div class="stat-card">
                    <h3>Paused Adsets</h3>
                    <div class="value" id="pausedAdsets">0</div>
                </div>
                <div class="stat-card">
                    <h3>Total Ads</h3>
                    <div class="value" id="totalAds">0</div>
                </div>
            </div>
            <div class="table-container">
                <div class="table-header">
                    <h2>📊 Ads Performance</h2>
                    <div id="tableInfo"></div>
                </div>
                <div id="tableContent">
                    <div class="loading">Loading...</div>
                </div>
            </div>
        </div>
        <script>
            let currentPage = 1;
            const pageSize = 50;
            
            async function loadData() {
                const accountId = document.getElementById('accountFilter').value;
                const prefix = document.getElementById('prefixFilter').value;
                const status = document.getElementById('statusFilter').value;
                const dateFrom = document.getElementById('dateFrom').value;
                const dateTo = document.getElementById('dateTo').value;
                
                try {{
                    // Load stats
                    const statsResponse = await fetch('/api/dashboard/stats?account_id=' + accountId + '&prefix=' + prefix + '&status=' + status + '&date_from=' + dateFrom + '&date_to=' + dateTo);
                    const stats = await statsResponse.json();
                    updateStats(stats);
                    
                    // Load ads data
                    const adsResponse = await fetch('/api/dashboard/ads?account_id=' + accountId + '&prefix=' + prefix + '&status=' + status + '&date_from=' + dateFrom + '&date_to=' + dateTo + '&page=' + currentPage + '&page_size=' + pageSize);
                    const adsData = await adsResponse.json();
                    updateTable(adsData);
                }} catch (error) {{
                    console.error('Error loading data:', error);
                    document.getElementById('tableContent').innerHTML = '<div class="loading">Error loading data</div>';
                }}
            }}
            
            function updateStats(stats) {
                document.getElementById('totalSpend').textContent = formatNumber(stats.total_spend || 0);
                document.getElementById('totalResults').textContent = formatNumber(stats.total_results || 0);
                document.getElementById('avgGiaData').textContent = formatNumber(stats.avg_gia_data || 0);
                document.getElementById('activeAdsets').textContent = formatNumber(stats.active_adsets || 0);
                document.getElementById('pausedAdsets').textContent = formatNumber(stats.paused_adsets || 0);
                document.getElementById('totalAds').textContent = formatNumber(stats.total_ads || 0);
            }
            
            function updateTable(data) {
                const ads = data.ads || [];
                const total = data.total || 0;
                
                if (ads.length === 0) {
                    document.getElementById('tableContent').innerHTML = '<div class="loading">No data found</div>';
                    return;
                }
                
                let html = '<table><thead><tr>';
                html += '<th>Adset ID</th>';
                html += '<th>Adset Name</th>';
                html += '<th>Campaign</th>';
                html += '<th>Prefix</th>';
                html += '<th>Status</th>';
                html += '<th>Spend</th>';
                html += '<th>Results</th>';
                html += '<th>Giá DATA</th>';
                html += '<th>Impressions</th>';
                html += '<th>Clicks</th>';
                html += '<th>CTR</th>';
                html += '<th>CPC</th>';
                html += '</tr></thead><tbody>';
                
                ads.forEach(ad => {
                    html += '<tr>';
                    html += `<td>${ad.adset_id || ''}</td>`;
                    html += `<td>${ad.adset_name || ''}</td>`;
                    html += `<td>${ad.campaign_name || ''}</td>`;
                    html += `<td>${ad.prefix || ''}</td>`;
                    html += `<td><span class="status-badge status-${(ad.adset_status || '').toLowerCase()}">${ad.adset_status || ''}</span></td>`;
                    html += `<td>${formatNumber(ad.spend || 0)}</td>`;
                    html += `<td>${formatNumber(ad.results || 0)}</td>`;
                    html += `<td>${formatNumber(ad.gia_data || 0)}</td>`;
                    html += `<td>${formatNumber(ad.impressions || 0)}</td>`;
                    html += `<td>${formatNumber(ad.clicks || 0)}</td>`;
                    html += `<td>${(ad.ctr || 0).toFixed(2)}%</td>`;
                    html += `<td>${formatNumber(ad.cpc || 0)}</td>`;
                    html += '</tr>';
                });
                
                html += '</tbody></table>';
                
                // Add pagination
                const totalPages = Math.ceil(total / pageSize);
                if (totalPages > 1) {
                    html += '<div class="pagination">';
                    for (let i = 1; i <= totalPages; i++) {
                        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
                    }
                    html += '</div>';
                }
                
                document.getElementById('tableContent').innerHTML = html;
                document.getElementById('tableInfo').textContent = `Showing ${ads.length} of ${total} ads`;
            }
            
            function goToPage(page) {
                currentPage = page;
                loadData();
            }
            
            function formatNumber(num) {
                return new Intl.NumberFormat('vi-VN').format(num);
            }
            
            async function exportData() {{
                const accountId = document.getElementById('accountFilter').value;
                const prefix = document.getElementById('prefixFilter').value;
                const status = document.getElementById('statusFilter').value;
                const dateFrom = document.getElementById('dateFrom').value;
                const dateTo = document.getElementById('dateTo').value;
                
                window.open('/api/dashboard/export?account_id=' + accountId + '&prefix=' + prefix + '&status=' + status + '&date_from=' + dateFrom + '&date_to=' + dateTo, '_blank');
            }}
            
            // Load filters options on page load
            async function loadFilters() {
                try {
                    const response = await fetch('/api/dashboard/filters');
                    const filters = await response.json();
                    
                    // Populate account filter
                    const accountFilter = document.getElementById('accountFilter');
                    filters.accounts.forEach(account => {
                        const option = document.createElement('option');
                        option.value = account;
                        option.textContent = account;
                        accountFilter.appendChild(option);
                    });
                    
                    // Populate prefix filter
                    const prefixFilter = document.getElementById('prefixFilter');
                    filters.prefixes.forEach(prefix => {
                        const option = document.createElement('option');
                        option.value = prefix;
                        option.textContent = prefix;
                        prefixFilter.appendChild(option);
                    });
                } catch (error) {
                    console.error('Error loading filters:', error);
                }
            }
            
            // Set default date to yesterday
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            document.getElementById('dateTo').value = yesterday.toISOString().split('T')[0];
            
            // Load data on page load
            loadFilters();
            loadData();
            
            // Helper function to get cookie
            function getCookie(name) {{
                const value = '; ' + document.cookie;
                const parts = value.split('; ' + name + '=');
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }}
            
            function logout() {{
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
                window.location.href = '/auth/login';
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/stats")
async def get_stats(
    request: Request,
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics - filtered by user_id"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        # Get user's account IDs
        user_accounts = db.query(Account.account_id).filter(Account.user_id == current_user.id).all()
        user_account_ids = [acc[0] for acc in user_accounts]
        
        if not user_account_ids:
            # No accounts for this user, return empty stats
            return {
                "total_spend": 0.0,
                "total_results": 0,
                "avg_gia_data": 0.0,
                "active_adsets": 0,
                "paused_adsets": 0,
                "total_ads": 0
            }
        
        # Build base filter conditions
        filters = [AdMetrics.account_id.in_(user_account_ids)]  # Filter by user's accounts
        
        if account_id and account_id in user_account_ids:
            filters.append(AdMetrics.account_id == account_id)
        if prefix:
            filters.append(AdMetrics.prefix == prefix)
        if status:
            filters.append(AdMetrics.adset_status == status)
        if date_from:
            try:
                filters.append(AdMetrics.date >= datetime.fromisoformat(date_from))
            except:
                pass
        if date_to:
            try:
                filters.append(AdMetrics.date <= datetime.fromisoformat(date_to))
            except:
                pass
        
        # Build base query với filters
        base_query = db.query(AdMetrics)
        if filters:
            base_query = base_query.filter(and_(*filters))
        
        # Calculate stats
        total_spend = base_query.with_entities(func.sum(AdMetrics.spend)).scalar() or 0
        total_results = base_query.with_entities(func.sum(AdMetrics.results)).scalar() or 0
        avg_gia_data = base_query.with_entities(func.avg(AdMetrics.gia_data)).scalar() or 0
        total_ads = base_query.count()
        
        # Active adsets (với filters nhưng status = ACTIVE)
        active_filters = filters + [AdMetrics.adset_status == "ACTIVE"]
        active_adsets = db.query(func.count(distinct(AdMetrics.adset_id))).filter(and_(*active_filters)).scalar() or 0
        
        # Paused adsets (với filters nhưng status = PAUSED)
        paused_filters = filters + [AdMetrics.adset_status == "PAUSED"]
        paused_adsets = db.query(func.count(distinct(AdMetrics.adset_id))).filter(and_(*paused_filters)).scalar() or 0
        
        return {
            "total_spend": float(total_spend),
            "total_results": int(total_results),
            "avg_gia_data": float(avg_gia_data),
            "active_adsets": int(active_adsets),
            "paused_adsets": int(paused_adsets),
            "total_ads": int(total_ads)
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/ads")
async def get_ads(
    request: Request,
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get ads data with pagination - filtered by user_id"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        # Get user's account IDs
        user_accounts = db.query(Account.account_id).filter(Account.user_id == current_user.id).all()
        user_account_ids = [acc[0] for acc in user_accounts]
        
        if not user_account_ids:
            return {
                "ads": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        # Build query - filter by user's accounts
        query = db.query(AdMetrics).filter(AdMetrics.account_id.in_(user_account_ids))
        
        # Apply additional filters
        if account_id and account_id in user_account_ids:
            query = query.filter(AdMetrics.account_id == account_id)
        if prefix:
            query = query.filter(AdMetrics.prefix == prefix)
        if status:
            query = query.filter(AdMetrics.adset_status == status)
        if date_from:
            query = query.filter(AdMetrics.date >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(AdMetrics.date <= datetime.fromisoformat(date_to))
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        ads = query.order_by(AdMetrics.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # Convert to dict
        ads_dict = []
        for ad in ads:
            ads_dict.append({
                "adset_id": ad.adset_id,
                "adset_name": ad.adset_name,
                "ad_id": ad.ad_id,
                "ad_name": ad.ad_name,
                "campaign_name": ad.campaign_name,
                "prefix": ad.prefix,
                "account_id": ad.account_id,
                "adset_status": ad.adset_status,
                "spend": float(ad.spend or 0),
                "results": int(ad.results or 0),
                "gia_data": float(ad.gia_data or 0),
                "impressions": int(ad.impressions or 0),
                "clicks": int(ad.clicks or 0),
                "ctr": float(ad.ctr or 0),
                "cpc": float(ad.cpc or 0),
            })
        
        return {
            "ads": ads_dict,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/filters")
async def get_filters(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get filter options (accounts, prefixes) - filtered by user_id"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        # Get user's account IDs
        user_accounts = db.query(Account.account_id).filter(Account.user_id == current_user.id).all()
        user_account_ids = [acc[0] for acc in user_accounts]
        
        if not user_account_ids:
            return {
                "accounts": [],
                "prefixes": []
            }
        
        # Get unique account IDs from user's accounts only
        accounts = db.query(AdMetrics.account_id.distinct()).filter(
            AdMetrics.account_id.in_(user_account_ids),
            AdMetrics.account_id.isnot(None)
        ).all()
        accounts = [acc[0] for acc in accounts if acc[0]]
        
        # Get unique prefixes from user's accounts only
        prefixes = db.query(AdMetrics.prefix.distinct()).filter(
            AdMetrics.account_id.in_(user_account_ids),
            AdMetrics.prefix.isnot(None)
        ).all()
        prefixes = [pref[0] for pref in prefixes if pref[0]]
        
        return {
            "accounts": accounts,
            "prefixes": prefixes
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/export")
async def export_data(
    request: Request,
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Export data to CSV - filtered by user_id"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    
    try:
        import csv
        from io import StringIO
        
        # Get user's account IDs
        user_accounts = db.query(Account.account_id).filter(Account.user_id == current_user.id).all()
        user_account_ids = [acc[0] for acc in user_accounts]
        
        if not user_account_ids:
            # Return empty CSV
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "Adset ID", "Adset Name", "Ad ID", "Ad Name", "Campaign Name",
                "Prefix", "Account ID", "Status", "Spend", "Results", "Giá DATA",
                "Impressions", "Clicks", "CTR", "CPC"
            ])
            from fastapi.responses import Response
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=ads_export.csv"}
            )
        
        # Build query - filter by user's accounts
        query = db.query(AdMetrics).filter(AdMetrics.account_id.in_(user_account_ids))
        
        # Apply additional filters
        if account_id and account_id in user_account_ids:
            query = query.filter(AdMetrics.account_id == account_id)
        if prefix:
            query = query.filter(AdMetrics.prefix == prefix)
        if status:
            query = query.filter(AdMetrics.adset_status == status)
        if date_from:
            query = query.filter(AdMetrics.date >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(AdMetrics.date <= datetime.fromisoformat(date_to))
        
        # Get all data
        ads = query.all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            "Adset ID", "Adset Name", "Ad ID", "Ad Name", "Campaign Name",
            "Prefix", "Account ID", "Status", "Spend", "Results", "Giá DATA",
            "Impressions", "Clicks", "CTR", "CPC"
        ])
        
        # Write data
        for ad in ads:
            writer.writerow([
                ad.adset_id, ad.adset_name, ad.ad_id, ad.ad_name, ad.campaign_name,
                ad.prefix, ad.account_id, ad.adset_status, ad.spend, ad.results, ad.gia_data,
                ad.impressions, ad.clicks, ad.ctr, ad.cpc
            ])
        
        from fastapi.responses import Response
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=ads_export.csv"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

