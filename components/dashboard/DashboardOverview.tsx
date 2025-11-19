import React, { useState, useEffect } from 'react';
import AdsControlsBar, { ViewType, DateRange } from './AdsControlsBar';
import FilterDrawer, { ActiveFilter } from './FilterDrawer';
import SummaryCards from './SummaryCards';
import AdsDataTable from './AdsDataTable';
import BudgetAdjustmentModal from './BudgetAdjustmentModal';

type LevelType = 'campaign' | 'adset' | 'ad';

interface DashboardData {
  summary: any;
  details: {
    level: string;
    rows: any[];
    pagination: {
      page: number;
      page_size: number;
      total_rows: number;
      total_pages: number;
    };
  };
}

const DashboardOverview: React.FC = () => {
  const [search, setSearch] = useState('');
  const [selectedPreset, setSelectedPreset] = useState<string | undefined>();
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date(),
    to: new Date(),
  });
  const [view, setView] = useState<ViewType>('ecommerce'); // Default to ecommerce
  const [level, setLevel] = useState<LevelType>('adset'); // Current drill-down level
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);
  
  // Drill-down state
  const [drillDownCampaign, setDrillDownCampaign] = useState<string | null>(null);
  const [drillDownAdset, setDrillDownAdset] = useState<string | null>(null);
  
  // Data state
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Multi-select state
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());
  
  // Budget modal
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [selectedAdsets, setSelectedAdsets] = useState<any[]>([]);

  const handlePresetChange = (preset: string) => {
    setSelectedPreset(preset);
  };

  const fetchDashboardData = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    
    try {
      const viewMode = view === 'lead' ? 'lead' : 'ecommerce';
      const dateFrom = dateRange.from.toISOString().split('T')[0];
      const dateTo = dateRange.to.toISOString().split('T')[0];
      
      // Build query params
      const params = new URLSearchParams({
        view_mode: viewMode,
        level: level,
        date_from: dateFrom,
        date_to: dateTo,
        page: '1',
        page_size: '100',
        force_refresh: forceRefresh ? '1' : '0'
      });
      
      if (search) params.append('search', search);
      if (selectedPreset) params.append('prefix', selectedPreset);
      if (drillDownCampaign) params.append('campaign_id', drillDownCampaign);
      if (drillDownAdset) params.append('adset_id', drillDownAdset);
      
      // Add active filters
      activeFilters.forEach((filter) => {
        if (filter.value) {
          if (filter.type === 'account_id') {
            params.append('account_id', filter.value);
          } else if (filter.type === 'prefix') {
            params.append('prefix', filter.value);
          }
        }
      });
      
      const response = await fetch(`/dashboard/data?${params.toString()}`, {
        credentials: 'include' // Important for cookie-based auth
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setDashboardData(data);
      
      // Save filters to localStorage
      localStorage.setItem('dashboard_filters', JSON.stringify({
        view, level, dateRange, selectedPreset, activeFilters
      }));
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message || 'Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchDashboardData(true); // Force refresh from API
  };

  const handleSettings = () => {
    window.location.href = '/settings';
  };

  const handleFiltersChange = (filters: ActiveFilter[]) => {
    setActiveFilters(filters);
  };
  
  // Drill-down handlers
  const handleRowClick = (row: any) => {
    if (level === 'campaign') {
      // Click on campaign → drill down to adsets
      setDrillDownCampaign(row.id);
      setLevel('adset');
    } else if (level === 'adset') {
      // Click on adset → drill down to ads
      setDrillDownAdset(row.id);
      setLevel('ad');
    }
    // If already at ad level, do nothing (or could open detail modal)
  };
  
  const handleBreadcrumbClick = (newLevel: LevelType) => {
    setLevel(newLevel);
    if (newLevel === 'campaign') {
      setDrillDownCampaign(null);
      setDrillDownAdset(null);
    } else if (newLevel === 'adset') {
      setDrillDownAdset(null);
    }
  };
  
  // Multi-select handlers
  const handleSelectRow = (rowId: string) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(rowId)) {
      newSelected.delete(rowId);
    } else {
      newSelected.add(rowId);
    }
    setSelectedRows(newSelected);
  };
  
  const handleSelectAll = () => {
    if (selectedRows.size === dashboardData?.details.rows.length && dashboardData?.details.rows.length > 0) {
      setSelectedRows(new Set());
    } else if (dashboardData) {
      const allIds = new Set(dashboardData.details.rows.map((row: any) => row.id));
      setSelectedRows(allIds);
    }
  };

  const handleToggleSingleStatus = async (id: string, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'ACTIVE' ? 'PAUSED' : 'ACTIVE';
      const response = await fetch('/dashboard/status/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          level: level.toUpperCase(),
          items: [{ id, new_status: newStatus }]
        })
      });

      if (!response.ok) throw new Error('Failed to toggle status');
      await fetchDashboardData();
    } catch (err) {
      console.error('Error toggling status:', err);
      setError('Lỗi khi chuyển trạng thái');
    }
  };
  
  // Bulk actions
  const handleBulkPause = async () => {
    if (selectedRows.size === 0) return;
    
    try {
      const response = await fetch('/dashboard/status/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          level: level.toUpperCase(),
          items: Array.from(selectedRows).map(id => ({
            id,
            new_status: 'PAUSED'
          }))
        })
      });
      
      if (!response.ok) throw new Error('Failed to pause items');
      
      alert(`Đã tạm dừng ${selectedRows.size} ${level}(s)`);
      setSelectedRows(new Set());
      fetchDashboardData();
    } catch (err: any) {
      alert('Lỗi: ' + err.message);
    }
  };
  
  const handleBulkResume = async () => {
    if (selectedRows.size === 0) return;
    
    try {
      const response = await fetch('/dashboard/status/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          level: level.toUpperCase(),
          items: Array.from(selectedRows).map(id => ({
            id,
            new_status: 'ACTIVE'
          }))
        })
      });
      
      if (!response.ok) throw new Error('Failed to resume items');
      
      alert(`Đã kích hoạt ${selectedRows.size} ${level}(s)`);
      setSelectedRows(new Set());
      fetchDashboardData();
    } catch (err: any) {
      alert('Lỗi: ' + err.message);
    }
  };
  
  const handleBudgetAdjust = () => {
    if (selectedRows.size === 0 || !dashboardData) return;
    
    const items = dashboardData.details.rows
      .filter(row => selectedRows.has(row.id))
      .map(row => ({
        id: row.id,
        name: row.name,
        current_budget: row.budget,
        level: level
      }));
    
    setSelectedAdsets(items);
    setShowBudgetModal(true);
  };
  
  const handleApplyBudgetChanges = async (changes: { adset_id: string; new_budget: number }[]) => {
    const mappedChanges = changes.map(c => ({ id: c.adset_id, new_budget: c.new_budget }));
    try {
      const response = await fetch('/dashboard/budget/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          level: level.toUpperCase(),
          items: mappedChanges
        })
      });
      
      if (!response.ok) throw new Error('Failed to update budgets');
      
      alert(`Đã cập nhật ngân sách cho ${changes.length} ${level}(s)`);
      setSelectedRows(new Set());
      setShowBudgetModal(false);
      fetchDashboardData();
    } catch (err: any) {
      alert('Lỗi: ' + err.message);
    }
  };
  
  // Load saved filters from localStorage on mount
  useEffect(() => {
    const savedFilters = localStorage.getItem('dashboard_filters');
    if (savedFilters) {
      try {
        const parsed = JSON.parse(savedFilters);
        if (parsed.view) setView(parsed.view);
        if (parsed.level) setLevel(parsed.level);
        if (parsed.selectedPreset) setSelectedPreset(parsed.selectedPreset);
        if (parsed.activeFilters) setActiveFilters(parsed.activeFilters);
        if (parsed.dateRange) {
          setDateRange({
            from: new Date(parsed.dateRange.from),
            to: new Date(parsed.dateRange.to)
          });
        }
      } catch (e) {
        console.error('Failed to parse saved filters:', e);
      }
    }
  }, []);
  
  // Fetch data when filters change
  useEffect(() => {
    fetchDashboardData();
    // Clear selected rows when changing filters
    setSelectedRows(new Set());
  }, [view, level, dateRange, selectedPreset, activeFilters, drillDownCampaign, drillDownAdset]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-purple-100 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-800 mb-6">
          📊 Dashboard Quảng Cáo Facebook
        </h1>

        {/* Controls Bar */}
        <AdsControlsBar
          search={search}
          onSearchChange={setSearch}
          selectedPreset={selectedPreset}
          onPresetChange={handlePresetChange}
          dateRange={dateRange}
          onDateRangeChange={setDateRange}
          view={view}
          onViewChange={setView}
          onOpenFilters={() => setShowFilters(true)}
          onRefresh={handleRefresh}
          onSettings={handleSettings}
          activeFiltersCount={activeFilters.length}
        />
        
        {/* Breadcrumb Navigation */}
        {(drillDownCampaign || drillDownAdset) && (
          <div className="mb-4 flex items-center gap-2 text-sm text-slate-600">
            <button
              onClick={() => handleBreadcrumbClick('campaign')}
              className="hover:text-indigo-600 font-medium"
            >
              Chiến dịch
            </button>
            {drillDownCampaign && (
              <>
                <span>→</span>
                <button
                  onClick={() => handleBreadcrumbClick('adset')}
                  className={`hover:text-indigo-600 font-medium ${!drillDownAdset ? 'text-indigo-600' : ''}`}
                >
                  Nhóm quảng cáo
                </button>
              </>
            )}
            {drillDownAdset && (
              <>
                <span>→</span>
                <span className="text-indigo-600 font-medium">Quảng cáo</span>
              </>
            )}
          </div>
        )}

        {/* Bulk Actions Toolbar */}
        {selectedRows.size > 0 && (
          <div className="mb-4 bg-indigo-50 border border-indigo-200 rounded-xl p-4 flex items-center justify-between">
            <div className="text-sm font-medium text-indigo-900">
              Đã chọn {selectedRows.size} {level}(s)
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleBulkPause}
                className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 text-sm font-medium transition-colors"
              >
                ⏸️ Tạm dừng
              </button>
              <button
                onClick={handleBulkResume}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm font-medium transition-colors"
              >
                ▶️ Kích hoạt
              </button>
              <button
                onClick={handleBudgetAdjust}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm font-medium transition-colors"
              >
                💰 Chỉnh ngân sách
              </button>
              <button
                onClick={() => setSelectedRows(new Set())}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm font-medium transition-colors"
              >
                Bỏ chọn
              </button>
            </div>
          </div>
        )}

        {/* Filter Drawer */}
        <FilterDrawer
          open={showFilters}
          onClose={() => setShowFilters(false)}
          activeFilters={activeFilters}
          onChangeFilters={handleFiltersChange}
          search={search}
          onSearchChange={setSearch}
          selectedPreset={selectedPreset}
          onPresetChange={handlePresetChange}
        />

        {/* Main Content Area */}
        <div className="space-y-6">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-red-800 font-medium">❌ Lỗi: {error}</p>
              <button 
                onClick={() => fetchDashboardData()}
                className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
              >
                Thử lại
              </button>
            </div>
          )}
          
          {/* Summary Cards */}
          <SummaryCards 
            data={dashboardData?.summary || null}
            viewMode={view === 'lead' ? 'lead' : 'ecommerce'}
            loading={loading}
            currency="VND"
          />
          
          {/* Data Table */}
          <AdsDataTable
            rows={dashboardData?.details?.rows || []}
            viewMode={view === 'lead' ? 'lead' : 'ecommerce'}
            level={level}
            currency="VND"
            loading={loading}
            selectedRows={selectedRows}
            onSelectRow={handleSelectRow}
            onSelectAll={handleSelectAll}
            onRowClick={handleRowClick}
            onToggleStatus={handleToggleSingleStatus}
          />
          
          {/* Pagination Info */}
          {dashboardData?.details?.pagination && (
            <div className="text-center text-sm text-slate-600">
              Hiển thị {dashboardData.details.rows.length} / {dashboardData.details.pagination.total_rows} kết quả
              {dashboardData.details.pagination.total_pages > 1 && (
                <span> (Trang {dashboardData.details.pagination.page}/{dashboardData.details.pagination.total_pages})</span>
              )}
            </div>
          )}
        </div>
        
        {/* Budget Adjustment Modal */}
        <BudgetAdjustmentModal
          open={showBudgetModal}
          onClose={() => setShowBudgetModal(false)}
          adsets={selectedAdsets}
          currency="VND"
          onApply={handleApplyBudgetChanges}
        />
      </div>
    </div>
  );
};

export default DashboardOverview;

