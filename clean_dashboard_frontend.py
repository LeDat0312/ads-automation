"""
Clean Dashboard Frontend - Modern HTML/CSS/JS
Giao diện sạch và tối ưu, tách riêng khỏi Python code
"""

def generate_dashboard_html(current_user):
    """Generate clean dashboard HTML"""
    
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Dashboard - Facebook Ads Automation</title>
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/dashboard.css">
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
                    <div class="loading-spinner"></div>
                    <span>Đang tải...</span>
                </div>
            </div>
            <div class="header-right">
                <a href="/settings" class="link-button">⚙️ Cài Đặt</a>
                <a href="/" class="link-button secondary">← Về Trang Chủ</a>
                <div class="user-menu">{current_user.username}</div>
            </div>
        </header>
        
        <!-- Control Panel -->
        <div class="control-panel">
            <div class="controls-row">
                <!-- View Mode -->
                <div class="filter-group">
                    <label>Chế độ xem:</label>
                    <div class="view-mode">
                        <button class="view-btn active" data-mode="ecommerce">🛒 E-Commerce</button>
                        <button class="view-btn" data-mode="lead">📋 Lead Generation</button>
                    </div>
                </div>
                
                <!-- Filters -->
                <div class="filter-group">
                    <label>Tài khoản:</label>
                    <select class="filter-select" id="accountFilter">
                        <option value="">Tất cả tài khoản</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Prefix:</label>
                    <select class="filter-select" id="prefixFilter">
                        <option value="">Tất cả prefix</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Ngày:</label>
                    <select class="filter-select" id="dateFilter">
                        <option value="today">Hôm nay</option>
                        <option value="yesterday">Hôm qua</option>
                        <option value="last7days" selected>7 ngày qua</option>
                        <option value="last30days">30 ngày qua</option>
                    </select>
                </div>
                
                <button class="refresh-btn" id="refreshBtn">
                    <span class="icon">🔄</span>
                    <span>Làm mới</span>
                </button>
            </div>
        </div>
        
        <!-- Overview Cards -->
        <div class="overview-grid" id="overviewGrid">
            <!-- Cards sẽ được tạo bởi JavaScript -->
        </div>
        
        <!-- Data Table -->
        <div class="table-container">
            <div class="table-header">
                <div class="table-title">
                    <span id="tableIcon">📊</span>
                    <span id="tableTitle">Chi Tiết Quảng Cáo E-Commerce</span>
                </div>
                <div class="table-actions">
                    <div class="bulk-actions" id="bulkActions">
                        <span id="selectedCount">0 đã chọn</span>
                        <button class="bulk-btn play">▶️ Bật</button>
                        <button class="bulk-btn pause">⏸️ Tắt</button>
                    </div>
                    <div class="search-box">
                        <div class="search-icon">🔍</div>
                        <input type="text" class="search-input" id="searchInput" placeholder="Tìm kiếm...">
                    </div>
                </div>
            </div>
            
            <div class="table-scroll">
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
    
    <script src="/static/dashboard.js"></script>
</body>
</html>
"""

# CSS riêng biệt
DASHBOARD_CSS = """
:root {
    --primary-50: #eff6ff;
    --primary-100: #dbeafe;
    --primary-600: #2563eb;
    --primary-700: #1d4ed8;
    --success-500: #22c55e;
    --success-600: #16a34a;
    --red-500: #ef4444;
    --red-600: #dc2626;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-900: #111827;
    --purple-600: #9333ea;
    --warning-600: #d97706;
    --cyan-600: #0891b2;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

/* Header */
.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 30px;
    padding: 0 10px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 15px;
}

.header-title {
    display: flex;
    align-items: center;
    gap: 12px;
    color: white;
    font-size: 32px;
    font-weight: 700;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 15px;
}

.link-button {
    color: rgba(255, 255, 255, 0.9);
    text-decoration: none;
    font-size: 16px;
    padding: 8px 16px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
}

.link-button:hover {
    background: rgba(255, 255, 255, 0.2);
    color: white;
}

/* Settings Status */
.settings-status {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.settings-status.complete {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
    border-color: rgba(34, 197, 94, 0.2);
}

.settings-status.incomplete {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border-color: rgba(239, 68, 68, 0.2);
}

/* Control Panel */
.control-panel {
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.controls-row {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 12px;
}

.filter-group label {
    font-weight: 500;
    color: #374151;
    white-space: nowrap;
}

.view-mode {
    display: flex;
    gap: 8px;
}

.view-btn {
    padding: 10px 20px;
    border: 1px solid #e5e7eb;
    background: white;
    color: #6b7280;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
}

.view-btn.active {
    background: #6366f1;
    color: white;
    border-color: #6366f1;
}

.filter-select {
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    background: white;
    min-width: 150px;
}

.refresh-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
}

.refresh-btn:hover {
    background: #5856eb;
}

.refresh-btn.loading {
    opacity: 0.7;
    pointer-events: none;
}

.refresh-btn.loading .icon {
    animation: spin 1s linear infinite;
}

/* Overview Cards */
.overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.overview-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
}

.overview-card:hover {
    transform: translateY(-2px);
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}

.card-title {
    font-size: 14px;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.card-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    color: white;
}

.card-icon.spend { background: #6366f1; }
.card-icon.leads { background: #22c55e; }
.card-icon.conversion { background: #f59e0b; }
.card-icon.adsets { background: #8b5cf6; }
.card-icon.purchase { background: #06b6d4; }

.card-value {
    font-size: 32px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 8px;
}

.card-subtitle {
    font-size: 14px;
    color: #6b7280;
}

/* Table */
.table-container {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.table-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px;
    border-bottom: 1px solid #e5e7eb;
}

.table-title {
    font-size: 18px;
    font-weight: 700;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 10px;
}

.table-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.bulk-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    opacity: 0;
    transition: all 0.3s ease;
}

.bulk-actions.visible {
    opacity: 1;
}

.search-box {
    position: relative;
    display: flex;
    align-items: center;
}

.search-input {
    padding: 8px 12px 8px 36px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    width: 250px;
}

.search-icon {
    position: absolute;
    left: 12px;
    color: #9ca3af;
}

.table-scroll {
    overflow-x: auto;
    max-height: 600px;
    overflow-y: auto;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #f3f4f6;
}

.data-table th {
    background: #f9fafb;
    font-weight: 600;
    color: #374151;
    font-size: 14px;
    position: sticky;
    top: 0;
    z-index: 10;
}

.data-table tbody tr:hover {
    background: #f9fafb;
}

.data-table td {
    font-size: 14px;
    color: #1f2937;
}

.text-right { text-align: right; }
.text-green { color: #22c55e; }
.text-red { color: #ef4444; }
.text-gray { color: #6b7280; }
.font-semibold { font-weight: 600; }

/* Loading */
.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
    color: #6b7280;
}

.spinner, .loading-spinner {
    width: 24px;
    height: 24px;
    border: 2px solid #f3f4f6;
    border-top: 2px solid #6366f1;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 12px;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
    .overview-grid {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 16px;
    }
    
    .controls-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }
    
    .search-input {
        width: 200px;
    }
}
"""

# JavaScript riêng biệt  
DASHBOARD_JS = """
// Global state
let currentViewMode = 'ecommerce';
let currentFilters = {
    account: '',
    prefix: '',
    dateRange: 'last7days',
    search: ''
};
let selectedItems = new Set();
let isLoading = false;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard loading...');
    loadSavedFilters();
    setupEventListeners();
    initializeDashboard();
});

// Event listeners
function setupEventListeners() {
    // View mode buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.mode;
            switchViewMode(mode);
        });
    });
    
    // Filter changes
    document.getElementById('accountFilter').addEventListener('change', updateFilters);
    document.getElementById('prefixFilter').addEventListener('change', updateFilters);
    document.getElementById('dateFilter').addEventListener('change', updateFilters);
    
    // Search with debouncing
    const searchInput = document.getElementById('searchInput');
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentFilters.search = this.value;
            saveFilters();
            loadData();
        }, 500);
    });
    
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', refreshData);
}

// Filter persistence
function saveFilters() {
    localStorage.setItem('dashboard_filters', JSON.stringify({
        ...currentFilters,
        viewMode: currentViewMode
    }));
}

function loadSavedFilters() {
    const saved = localStorage.getItem('dashboard_filters');
    if (saved) {
        const filters = JSON.parse(saved);
        currentFilters = {
            account: filters.account || '',
            prefix: filters.prefix || '',
            dateRange: filters.dateRange || 'last7days',
            search: filters.search || ''
        };
        
        if (filters.viewMode) {
            currentViewMode = filters.viewMode;
            updateViewModeUI();
        }
        
        // Restore form values
        document.getElementById('accountFilter').value = currentFilters.account;
        document.getElementById('prefixFilter').value = currentFilters.prefix;
        document.getElementById('dateFilter').value = currentFilters.dateRange;
        document.getElementById('searchInput').value = currentFilters.search;
    }
}

// Authentication
function getAuthToken() {
    return localStorage.getItem('access_token') || '';
}

// Initialize dashboard
async function initializeDashboard() {
    try {
        await checkSettingsStatus();
        await loadFilters();
        await loadData();
    } catch (error) {
        console.error('Dashboard initialization failed:', error);
        showError('Lỗi khởi tạo: ' + error.message);
    }
}

// Check settings status
async function checkSettingsStatus() {
    try {
        const response = await fetch('/dashboard/settings-status', {
            headers: { 'Authorization': 'Bearer ' + getAuthToken() }
        });
        
        if (response.ok) {
            const status = await response.json();
            updateSettingsStatus(status);
        }
    } catch (error) {
        console.error('Error checking settings:', error);
    }
}

function updateSettingsStatus(status) {
    const statusElement = document.getElementById('settingsStatus');
    
    if (status.settings_complete) {
        statusElement.className = 'settings-status complete';
        statusElement.innerHTML = `
            <span>✅</span>
            <span>Sẵn sàng (${status.accounts_count} accounts, ${status.prefixes_count} prefixes)</span>
        `;
    } else {
        statusElement.className = 'settings-status incomplete';
        let message = 'Cần cấu hình';
        if (!status.has_token) message = 'Thiếu token';
        else if (status.accounts_count === 0) message = 'Chưa có accounts';
        else if (status.prefixes_count === 0) message = 'Chưa có prefixes';
        
        statusElement.innerHTML = `
            <span>⚠️</span>
            <span>${message}</span>
        `;
    }
}

// Load filters
async function loadFilters() {
    try {
        const response = await fetch('/dashboard/filters', {
            headers: { 'Authorization': 'Bearer ' + getAuthToken() }
        });
        
        if (response.ok) {
            const data = await response.json();
            populateFilterDropdowns(data);
        }
    } catch (error) {
        console.error('Error loading filters:', error);
    }
}

function populateFilterDropdowns(data) {
    // Populate accounts
    const accountSelect = document.getElementById('accountFilter');
    accountSelect.innerHTML = '<option value="">Tất cả tài khoản</option>';
    data.accounts.forEach(acc => {
        const option = document.createElement('option');
        option.value = acc.id;
        option.textContent = `${acc.name} (${acc.type})`;
        accountSelect.appendChild(option);
    });
    accountSelect.value = currentFilters.account;
    
    // Populate prefixes
    const prefixSelect = document.getElementById('prefixFilter');
    prefixSelect.innerHTML = '<option value="">Tất cả prefix</option>';
    data.prefixes.forEach(prefix => {
        const option = document.createElement('option');
        option.value = prefix.id;
        option.textContent = prefix.name;
        prefixSelect.appendChild(option);
    });
    prefixSelect.value = currentFilters.prefix;
}

// View mode
function switchViewMode(mode) {
    if (currentViewMode === mode) return;
    
    currentViewMode = mode;
    updateViewModeUI();
    saveFilters();
    loadData();
}

function updateViewModeUI() {
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === currentViewMode);
    });
    
    const title = currentViewMode === 'ecommerce' 
        ? 'Chi Tiết Quảng Cáo E-Commerce' 
        : 'Chi Tiết Quảng Cáo Lead Generation';
    const icon = currentViewMode === 'ecommerce' ? '🛒' : '📋';
    
    document.getElementById('tableTitle').textContent = title;
    document.getElementById('tableIcon').textContent = icon;
}

// Update filters
function updateFilters() {
    currentFilters.account = document.getElementById('accountFilter').value;
    currentFilters.prefix = document.getElementById('prefixFilter').value;
    currentFilters.dateRange = document.getElementById('dateFilter').value;
    
    saveFilters();
    loadData();
}

// Refresh data
function refreshData() {
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn.classList.add('loading');
    
    loadData().finally(() => {
        refreshBtn.classList.remove('loading');
    });
}

// Load data
async function loadData() {
    if (isLoading) return;
    
    isLoading = true;
    
    try {
        // Load summary and details in parallel
        const [summaryResponse, dataResponse] = await Promise.all([
            fetch(`/dashboard/summary?${buildAPIParams()}`, {
                headers: { 'Authorization': 'Bearer ' + getAuthToken() }
            }),
            fetch(`/dashboard/data?${buildAPIParams()}`, {
                headers: { 'Authorization': 'Bearer ' + getAuthToken() }
            })
        ]);
        
        if (summaryResponse.ok && dataResponse.ok) {
            const summary = await summaryResponse.json();
            const data = await dataResponse.json();
            
            updateOverviewCards(summary);
            updateTable(data.ads || []);
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Lỗi tải dữ liệu: ' + error.message);
    } finally {
        isLoading = false;
    }
}

function buildAPIParams() {
    const params = new URLSearchParams({
        view_mode: currentViewMode
    });
    
    if (currentFilters.account) params.append('account_id', currentFilters.account);
    if (currentFilters.prefix) params.append('prefix', currentFilters.prefix);
    if (currentFilters.dateRange) params.append('date_range', currentFilters.dateRange);
    if (currentFilters.search) params.append('search', currentFilters.search);
    
    return params.toString();
}

// Update overview cards
function updateOverviewCards(overview) {
    const grid = document.getElementById('overviewGrid');
    
    if (currentViewMode === 'ecommerce') {
        grid.innerHTML = `
            <div class="overview-card">
                <div class="card-header">
                    <div class="card-title">Tổng Chi Tiêu</div>
                    <div class="card-icon spend">💰</div>
                </div>
                <div class="card-value">${formatCurrency(overview.totalSpend || 0)}</div>
                <div class="card-subtitle">Tổng chi phí quảng cáo</div>
            </div>
            
            <div class="overview-card">
                <div class="card-header">
                    <div class="card-title">% ADS</div>
                    <div class="card-icon conversion">📈</div>
                </div>
                <div class="card-value">${formatPercentage(overview.adsPercent || 0)}%</div>
                <div class="card-subtitle">Chi tiêu / Giá trị chuyển đổi</div>
            </div>
            
            <div class="overview-card">
                <div class="card-header">
                    <div class="card-title">Giá Trị Chuyển Đổi</div>
                    <div class="card-icon purchase">🛒</div>
                </div>
                <div class="card-value">${formatCurrency(overview.purchaseValue || 0)}</div>
                <div class="card-subtitle">Doanh thu từ quảng cáo</div>
            </div>
            
            <div class="overview-card">
                <div class="card-header">
                    <div class="card-title">Adsets</div>
                    <div class="card-icon adsets">📊</div>
                </div>
                <div class="card-value">
                    <span class="text-green">${overview.activeAdsets || 0}</span> / 
                    <span class="text-red">${overview.pausedAdsets || 0}</span>
                </div>
                <div class="card-subtitle">Hoạt động / Tạm dừng</div>
            </div>
        `;
    } else {
        grid.innerHTML = `
            <div class="overview-card">
                <div class="card-header">
                    <div class="card-title">Tổng Chi Tiêu</div>
                    <div class="card-icon spend">💰</div>
                </div>
                <div class="card-value">${formatCurrency(overview.totalSpend || 0)}</div>
                <div class="card-subtitle">Tổng chi phí quảng cáo</div>
            </div>
            
            <div class="overview-card">
                <div class="card-header">
                    <div class="card-title">Tổng Lead</div>
                    <div class="card-icon leads">📋</div>
                </div>
                <div class="card-value">${formatNumber(overview.totalLeads || 0)}</div>
                <div class="card-subtitle">Comments + Messages</div>
            </div>
            
            <div class="overview-card">
                <div class="card-header">
                    <div class="card-title">Giá Data TB</div>
                    <div class="card-icon conversion">🎯</div>
                </div>
                <div class="card-value">${formatCurrency(overview.avgGiaData || 0)}</div>
                <div class="card-subtitle">Chi phí trung bình mỗi lead</div>
            </div>
            
            <div class="overview-card">
                <div class="card-header">
                    <div class="card-title">Adsets</div>
                    <div class="card-icon adsets">📊</div>
                </div>
                <div class="card-value">
                    <span class="text-green">${overview.activeAdsets || 0}</span> / 
                    <span class="text-red">${overview.pausedAdsets || 0}</span>
                </div>
                <div class="card-subtitle">Hoạt động / Tạm dừng</div>
            </div>
        `;
    }
}

// Update table
function updateTable(ads) {
    const tableHead = document.getElementById('tableHead');
    const tableBody = document.getElementById('tableBody');
    
    // Headers based on view mode
    let headers;
    if (currentViewMode === 'ecommerce') {
        headers = ['Chọn', 'Tên', 'Chi Tiêu', '% ADS', 'Lượt Mua', 'Giá Trị CV', 'CPM', 'CTR'];
    } else {
        headers = ['Chọn', 'Tên', 'Chi Tiêu', 'Lead', 'Giá Data', 'CPM', 'CTR'];
    }
    
    tableHead.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
    
    if (ads.length === 0) {
        tableBody.innerHTML = `
            <tr><td colspan="${headers.length}" class="loading">Không có dữ liệu</td></tr>
        `;
        return;
    }
    
    tableBody.innerHTML = ads.map(ad => {
        if (currentViewMode === 'ecommerce') {
            return `
                <tr>
                    <td><input type="checkbox"></td>
                    <td class="font-semibold">${truncate(ad.name, 30)}</td>
                    <td class="text-right">${formatCurrency(ad.spend || 0)}</td>
                    <td class="text-right">${formatPercentage(ad.adsPercent || 0)}%</td>
                    <td class="text-right">${formatNumber(ad.purchases || 0)}</td>
                    <td class="text-right">${formatCurrency(ad.purchase_value || 0)}</td>
                    <td class="text-right">${formatCurrency(ad.cpm || 0)}</td>
                    <td class="text-right">${formatPercentage(ad.ctr || 0)}%</td>
                </tr>
            `;
        } else {
            return `
                <tr>
                    <td><input type="checkbox"></td>
                    <td class="font-semibold">${truncate(ad.name, 30)}</td>
                    <td class="text-right">${formatCurrency(ad.spend || 0)}</td>
                    <td class="text-right">${formatNumber(ad.results || 0)}</td>
                    <td class="text-right">${formatCurrency(ad.giaData || 0)}</td>
                    <td class="text-right">${formatCurrency(ad.cpm || 0)}</td>
                    <td class="text-right">${formatPercentage(ad.ctr || 0)}%</td>
                </tr>
            `;
        }
    }).join('');
}

// Utility functions
function formatCurrency(value) {
    if (!value) return '0₫';
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND',
        minimumFractionDigits: 0
    }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('vi-VN').format(value || 0);
}

function formatPercentage(value) {
    return (value || 0).toFixed(2);
}

function truncate(text, max) {
    return text && text.length > max ? text.substring(0, max) + '...' : text;
}

function showError(message) {
    console.error('Error:', message);
    alert(message);
}
"""