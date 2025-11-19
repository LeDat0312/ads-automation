import React, { useState, useEffect } from 'react';
import AdsControlsBar, { ViewType, DateRange } from './AdsControlsBar';
import FilterDrawer, { ActiveFilter } from './FilterDrawer';
import SummaryCards from './SummaryCards';
import AdsDataTable from './AdsDataTable';
import BudgetAdjustmentModal from './BudgetAdjustmentModal';

interface DashboardData {
  summary: any;
  details: {
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
  const [view, setView] = useState<ViewType>('all');
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);
  
  // Data state
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Budget modal
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [selectedAdsets, setSelectedAdsets] = useState<any[]>([]);

  const handlePresetChange = (preset: string) => {
    setSelectedPreset(preset);
    console.log('Preset changed:', preset);
  };

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const viewMode = view === 'lead' ? 'lead' : view === 'ecommerce' ? 'ecommerce' : 'all';
      const dateFrom = dateRange.from.toISOString().split('T')[0];
      const dateTo = dateRange.to.toISOString().split('T')[0];
      
      // Build query params
      const params = new URLSearchParams({
        view_mode: viewMode,
        date_from: dateFrom,
        date_to: dateTo,
        level: 'adset',
        page: '1',
        page_size: '50'
      });
      
      if (search) params.append('search', search);
      if (selectedPreset) params.append('prefix', selectedPreset);
      
      const response = await fetch(`/api/dashboard/data?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setDashboardData(data);
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message || 'Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchDashboardData();
  };

  const handleSettings = () => {
    console.log('Opening settings...');
  };

  const handleFiltersChange = (filters: ActiveFilter[]) => {
    setActiveFilters(filters);
    console.log('Filters changed:', filters);
  };
  
  const handleBudgetAdjust = (adsetIds: string[]) => {
    if (!dashboardData) return;
    
    const adsets = dashboardData.details.rows
      .filter(row => adsetIds.includes(row.adset_id))
      .map(row => ({
        adset_id: row.adset_id,
        adset_name: row.adset_name,
        current_budget: row.budget
      }));
    
    setSelectedAdsets(adsets);
    setShowBudgetModal(true);
  };
  
  const handleApplyBudgetChanges = async (changes: { adset_id: string; new_budget: number }[]) => {
    console.log('Applying budget changes:', changes);
    // TODO: Call API to update budgets
    alert(`Sẽ cập nhật ngân sách cho ${changes.length} adset(s)`);
  };
  
  const handleToggleStatus = (adsetIds: string[]) => {
    console.log('Toggle status for:', adsetIds);
    // TODO: Call API to toggle adset status
    alert(`Sẽ bật/tắt ${adsetIds.length} adset(s)`);
  };
  
  // Fetch data on mount and when filters change
  useEffect(() => {
    fetchDashboardData();
  }, [view, dateRange, selectedPreset]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-purple-100 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-800 mb-6">📊 Dashboard – Tổng Quan Hiệu Suất</h1>

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
                onClick={fetchDashboardData}
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
            currency="VND"
            loading={loading}
            onBudgetAdjust={handleBudgetAdjust}
            onToggleStatus={handleToggleStatus}
          />
          
          {/* Pagination Info */}
          {dashboardData?.details?.pagination && (
            <div className="text-center text-sm text-slate-600">
              Trang {dashboardData.details.pagination.page} / {dashboardData.details.pagination.total_pages}
              {' '}({dashboardData.details.pagination.total_rows} kết quả)
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

