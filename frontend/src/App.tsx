import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import SummaryCards from './components/SummaryCards';
import AdsetTable from './components/AdsetTable';
import FiltersBar from './components/FiltersBar';
import BudgetModal from './components/BudgetModal';
import LevelTabs, { Level } from './components/LevelTabs';
import PaginationControls from './components/PaginationControls';
import { getDashboardData, getErrorMessage, updateBudget, updateStatus } from './services/api';
import type {
  ViewMode,
  DashboardFilters,
  DashboardDataResponse,
  SortConfig,
  SortableColumn,
  Currency,
} from './types/dashboard';

function App() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // State
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    return (searchParams.get('view') as ViewMode) || 'ecommerce';
  });
  const [currency] = useState<Currency>('VND'); // TODO: Get from backend
  const [data, setData] = useState<DashboardDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [sortConfig, setSortConfig] = useState<SortConfig>({ column: null, direction: 'desc' });
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [currentLevel, setCurrentLevel] = useState<Level>('adset');
  const [drillDownPath, setDrillDownPath] = useState<{
    campaignId?: string;
    campaignName?: string;
    adsetId?: string;
    adsetName?: string;
  }>({});
  
  // Filters - Initialize from URL params
  const today = new Date().toISOString().split('T')[0];
  const [filters, setFilters] = useState<DashboardFilters>(() => {
    return {
      view_mode: (searchParams.get('view') as ViewMode) || 'ecommerce',
      level: (searchParams.get('level') as 'campaign' | 'adset' | 'ad') || 'adset',
      status: 'ALL',
      page: parseInt(searchParams.get('page') || '1'),
      pageSize: parseInt(searchParams.get('pageSize') || '50'),
      force_refresh: 0,
      date_from: searchParams.get('from') || today,
      date_to: searchParams.get('to') || today,
      prefix_filter: searchParams.get('prefix') || undefined,
      status_filter: searchParams.get('status') || undefined,
      search: searchParams.get('search') || undefined,
      campaign_id: searchParams.get('campaign_id') || undefined,
      adset_id: searchParams.get('adset_id') || undefined,
    };
  });
  
  // Sync currentLevel with filters.level
  useEffect(() => {
    setCurrentLevel(filters.level || 'adset');
  }, [filters.level]);

  // ✅ Sync filters to URL when they change
  useEffect(() => {
    const params: Record<string, string> = {
      view: filters.view_mode,
      level: filters.level || 'adset',
      from: filters.date_from,
      to: filters.date_to,
      page: String(filters.page || 1),
      pageSize: String(filters.pageSize || 50),
    };
    
    if (filters.prefix_filter) params.prefix = filters.prefix_filter;
    if (filters.status_filter) params.status = filters.status_filter;
    if (filters.search) params.search = filters.search;
    if (filters.campaign_id) params.campaign_id = filters.campaign_id;
    if (filters.adset_id) params.adset_id = filters.adset_id;
    
    setSearchParams(params, { replace: true });
  }, [filters, setSearchParams]);

  // Fetch data from API
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await getDashboardData(filters);
      setData(response);
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Initial load and on filter change
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle view mode change
  const handleViewModeChange = (mode: ViewMode) => {
    setViewMode(mode);
    setFilters(prev => ({ ...prev, view_mode: mode, page: 1 }));
    setSelectedIds(new Set());
  };

  // Handle sort
  const handleSort = (column: SortableColumn) => {
    setSortConfig(prev => ({
      column,
      direction: prev.column === column && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  // Sort rows client-side
  const sortedRows = React.useMemo(() => {
    if (!data?.details.rows || !sortConfig.column) {
      return data?.details.rows || [];
    }

    const sorted = [...data.details.rows].sort((a, b) => {
      const aVal = a[sortConfig.column!];
      const bVal = b[sortConfig.column!];
      
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;
      
      if (sortConfig.direction === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    return sorted;
  }, [data?.details.rows, sortConfig]);

  // Handle force refresh
  const handleRefresh = () => {
    setFilters(prev => ({ ...prev, force_refresh: 1 }));
    setTimeout(() => {
      setFilters(prev => ({ ...prev, force_refresh: 0 }));
    }, 1000);
  };

  // Handle budget update - bulk
  const handleBudgetUpdate = async (changes: { id: string; new_budget: number }[]) => {
    try {
      setLoading(true);
      await updateBudget({
        operations: changes.map(change => ({
          level: currentLevel === 'campaign' ? 'CAMPAIGN' : 'ADSET',
          id: change.id,
          new_budget: change.new_budget,
        })),
        view_mode: viewMode,
      });
      await fetchData();
      setSelectedIds(new Set());
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle drill-down
  const handleDrillDown = (level: 'campaign' | 'adset', id: string, name: string) => {
    if (level === 'campaign') {
      setFilters(prev => ({
        ...prev,
        campaign_id: id,
        adset_id: undefined,
        page: 1,
      }));
      setDrillDownPath({
        campaignId: id,
        campaignName: name,
      });
      setCurrentLevel('adset');
    } else if (level === 'adset') {
      setFilters(prev => ({
        ...prev,
        adset_id: id,
        page: 1,
      }));
      setDrillDownPath(prev => ({
        ...prev,
        adsetId: id,
        adsetName: name,
      }));
      setCurrentLevel('ad');
    }
  };

  // Handle drill-up
  const handleDrillUp = () => {
    if (drillDownPath.adsetId) {
      // Drill up from ad to adset
      setFilters(prev => ({
        ...prev,
        adset_id: undefined,
        page: 1,
      }));
      setDrillDownPath({
        campaignId: drillDownPath.campaignId,
        campaignName: drillDownPath.campaignName,
      });
      setCurrentLevel('adset');
    } else if (drillDownPath.campaignId) {
      // Drill up from adset to campaign
      setFilters(prev => ({
        ...prev,
        campaign_id: undefined,
        page: 1,
      }));
      setDrillDownPath({});
      setCurrentLevel('campaign');
    }
  };

  // Handle level change
  const handleLevelChange = (level: Level) => {
    setCurrentLevel(level);
    setFilters(prev => ({
      ...prev,
      level,
      campaign_id: undefined,
      adset_id: undefined,
      page: 1,
    }));
    setDrillDownPath({});
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  // Handle page size change
  const handlePageSizeChange = (pageSize: number) => {
    setFilters(prev => ({ ...prev, pageSize, page: 1 }));
  };

  // Handle status update (pause/resume) - single row
  const handleStatusToggle = async (row: any) => {
    try {
      setLoading(true);
      const newStatus = row.delivery === 'ACTIVE' ? 'PAUSED' : 'ACTIVE';
      await updateStatus({
        level: currentLevel.toUpperCase() as 'CAMPAIGN' | 'ADSET' | 'AD',
        items: [{
          id: row.id || row.adset_id || row.campaign_id,
          new_status: newStatus,
        }],
      });
      await fetchData();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle status update (pause/resume) - bulk
  const handleStatusUpdate = async (action: 'pause' | 'resume') => {
    try {
      setLoading(true);
      await updateStatus({
        level: currentLevel.toUpperCase() as 'CAMPAIGN' | 'ADSET' | 'AD',
        items: Array.from(selectedIds).map(id => ({
          id,
          new_status: action === 'pause' ? 'PAUSED' : 'ACTIVE',
        })),
      });
      await fetchData();
      setSelectedIds(new Set());
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle budget update - single row
  const handleBudgetUpdateSingle = async (row: any, newBudget: number) => {
    try {
      setLoading(true);
      await updateBudget({
        operations: [{
          level: row.budget_level || (currentLevel === 'campaign' ? 'CAMPAIGN' : 'ADSET'),
          id: row.id || row.adset_id || row.campaign_id,
          new_budget: newBudget,
        }],
        view_mode: viewMode,
      });
      // Refresh data after budget update
      await fetchData();
    } catch (err) {
      setError(getErrorMessage(err));
      throw err; // Re-throw để BudgetEditor hiển thị error
    } finally {
      setLoading(false);
    }
  };

  const selectedAdsets = sortedRows.filter(row => {
    const rowId = row.id || row.adset_id || row.campaign_id || row.ad_id || '';
    return selectedIds.has(rowId);
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                📊 Dashboard Quảng Cáo Facebook
              </h1>
              <p className="text-sm text-gray-600 mt-1">Quản lý và theo dõi chiến dịch quảng cáo của bạn</p>
            </div>
            
            {/* View Mode Toggle */}
            <div className="inline-flex rounded-xl border-2 border-gray-200 bg-white p-1 shadow-sm">
              <button
                onClick={() => handleViewModeChange('lead')}
                className={`
                  px-6 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200
                  ${viewMode === 'lead'
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200'
                    : 'text-gray-700 hover:bg-gray-50'
                  }
                `}
              >
                📋 Lead Generation
              </button>
              <button
                onClick={() => handleViewModeChange('ecommerce')}
                className={`
                  px-6 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200
                  ${viewMode === 'ecommerce'
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200'
                    : 'text-gray-700 hover:bg-gray-50'
                  }
                `}
              >
                🛒 E-Commerce
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Level Tabs */}
        <LevelTabs
          currentLevel={currentLevel}
          onLevelChange={handleLevelChange}
          drillDownPath={drillDownPath}
          onDrillUp={handleDrillUp}
        />

        {/* FiltersBar */}
        <FiltersBar
          filters={filters}
          onFiltersChange={setFilters}
          onRefresh={handleRefresh}
          isLoading={loading}
          viewMode={viewMode}
        />

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border-2 border-red-200 rounded-xl p-4 shadow-lg animate-shake">
            <div className="flex items-center gap-3">
              <span className="text-red-600 text-2xl">⚠️</span>
              <div>
                <h3 className="text-red-900 font-semibold">Lỗi</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-400 hover:text-red-600"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        <SummaryCards
          summary={data?.summary || {
            totalSpend: 0,
            activeAdsets: 0,
            pausedAdsets: 0,
            totalAdsets: 0,
            totalData: 0,
            avgGiaData: 0,
            totalLead: 0,
            adsPercent: 0,
            purchaseValue: 0,
            currency: currency,
          }}
          viewMode={viewMode}
          isLoading={loading}
        />

        {/* Selected Items Actions */}
        {selectedIds.size > 0 && (
          <div className="mb-6 bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-4 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">✅</span>
                <span className="text-indigo-900 font-semibold text-lg">
                  Đã chọn {selectedIds.size} nhóm quảng cáo
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowBudgetModal(true)}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg font-medium"
                >
                  💰 Điều chỉnh ngân sách
                </button>
                <button
                  onClick={() => handleStatusUpdate('resume')}
                  disabled={loading}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all shadow-md hover:shadow-lg font-medium disabled:opacity-50"
                >
                  ▶️ Kích hoạt
                </button>
                <button
                  onClick={() => handleStatusUpdate('pause')}
                  disabled={loading}
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-all shadow-md hover:shadow-lg font-medium disabled:opacity-50"
                >
                  ⏸️ Tạm dừng
                </button>
                <button 
                  onClick={() => setSelectedIds(new Set())}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                >
                  ✖️ Bỏ chọn
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Adset Table */}
        <AdsetTable
          rows={sortedRows}
          viewMode={viewMode}
          loading={loading}
          onSort={handleSort}
          sortConfig={sortConfig}
          selectedIds={selectedIds}
          onSelectionChange={setSelectedIds}
          onStatusToggle={handleStatusToggle}
          onBudgetUpdate={handleBudgetUpdateSingle}
          onDrillDown={handleDrillDown}
          currency={currency}
        />

        {/* Pagination Controls */}
        {data?.details.pagination && !loading && (
          <PaginationControls
            pagination={data.details.pagination}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
            loading={loading}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-8 py-6 border-t border-gray-200 bg-white">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-600">
          <p>Dashboard Quảng Cáo Facebook • Powered by React + Vite + FastAPI</p>
        </div>
      </footer>

      {/* Budget Modal */}
      <BudgetModal
        isOpen={showBudgetModal}
        onClose={() => setShowBudgetModal(false)}
        selectedAdsets={selectedAdsets}
        onApply={handleBudgetUpdate}
      />
    </div>
  );
}

export default App;
