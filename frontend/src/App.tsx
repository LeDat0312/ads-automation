import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import SummaryCards from './components/SummaryCards';
import AdsetTable from './components/AdsetTable';
import FiltersBar from './components/FiltersBar';
import BudgetModal from './components/BudgetModal';
import { Level } from './components/LevelTabs';
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
  // Use Vietnam timezone (UTC+7) for correct date
  const getVietnamDate = () => {
    const now = new Date();
    const vietnamTime = new Date(now.getTime() + (7 * 60 * 60 * 1000)); // UTC+7
    return vietnamTime.toISOString().split('T')[0];
  };
  const today = getVietnamDate();
  
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

  // Handle sort - gửi sort request lên backend
  const handleSort = (column: SortableColumn) => {
    // Toggle direction: nếu đang sort column này thì đổi hướng, nếu không thì mặc định desc
    let newDirection: 'asc' | 'desc' = 'desc';
    if (sortConfig.column === column) {
      newDirection = sortConfig.direction === 'desc' ? 'asc' : 'desc';
    }
    setSortConfig({
      column,
      direction: newDirection,
    });
    // Update filters để trigger fetchData với sort mới
    setFilters(prev => ({
      ...prev,
      sort_by: column,
      sort_order: newDirection,
      page: 1,  // Reset về trang 1 khi sort
    }));
  };

  // Rows đã được sort ở backend, không cần sort client-side nữa
  const sortedRows = React.useMemo(() => {
    return data?.details.rows || [];
  }, [data?.details.rows]);

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
      // Chỉ update các rows đã thay đổi, không reload toàn bộ
      setData(prev => {
        if (!prev) return prev;
        const updatedRows = prev.details.rows.map(r => {
          const rowId = r.id || r.adset_id || r.campaign_id || r.ad_id || '';
          const change = changes.find(c => c.id === rowId);
          if (change) {
            return { ...r, budget: change.new_budget };
          }
          return r;
        });
        return {
          ...prev,
          details: {
            ...prev.details,
            rows: updatedRows
          }
        };
      });
      setSelectedIds(new Set());
      // KHÔNG gọi fetchData - chỉ update số tiền ngân sách
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

  // Handle budget update - single row (chỉ update row đó, không reload toàn bộ)
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
      // Chỉ update row đó trong state, không reload toàn bộ
      setData(prev => {
        if (!prev) return prev;
        const updatedRows = prev.details.rows.map(r => {
          const rowId = r.id || r.adset_id || r.campaign_id || r.ad_id || '';
          const targetId = row.id || row.adset_id || row.campaign_id || row.ad_id || '';
          if (rowId === targetId) {
            return { ...r, budget: newBudget };
          }
          return r;
        });
        return {
          ...prev,
          details: {
            ...prev.details,
            rows: updatedRows
          }
        };
      });
      // KHÔNG gọi fetchData - chỉ update số tiền ngân sách
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
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Top Bar - Purple Header */}
      <header className="bg-transparent shadow-lg sticky top-0 z-30">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between">
            {/* Left: Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="text-3xl">🚀</div>
              <div>
                <h1 className="text-xl font-bold text-white">
                  Facebook Ads Automation - Dashboard
                </h1>
                <p className="text-xs text-white/80">Quản lý chiến dịch quảng cáo thông minh</p>
              </div>
            </div>
            
            {/* Right: Status + Buttons */}
            <div className="flex items-center gap-3">
              {/* Status Badge */}
              <div className="px-4 py-2 bg-green-500/20 backdrop-blur-sm border border-green-400/30 text-white rounded-full text-sm font-medium">
                ✓ Sẵn sàng ({data?.summary?.totalAdsets || 0} adsets)
              </div>
              
              {/* Settings Button */}
              <button 
                className="px-4 py-2 border-2 border-white/30 text-white rounded-lg hover:bg-white/20 transition-colors text-sm font-medium backdrop-blur-sm"
                onClick={() => window.location.href = '/settings'}
              >
                ⚙️ Cài đặt
              </button>
              
              {/* Home Button */}
              <button 
                className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-lg hover:bg-white/30 transition-colors text-sm font-semibold border border-white/30"
                onClick={() => window.location.href = '/'}
              >
                🏠 Về Trang Chủ
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* View Mode Strip */}
      <div className="bg-transparent sticky top-[60px] z-20">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-4">
            {/* View Mode Tabs */}
            <div className="inline-flex rounded-lg border border-white/30 p-1 bg-white/10 backdrop-blur-sm">
              <button
                onClick={() => handleViewModeChange('ecommerce')}
                className={`
                  px-6 py-2 rounded-md text-sm font-semibold transition-all duration-200
                  ${viewMode === 'ecommerce'
                    ? 'bg-white text-[#667eea] shadow-md'
                    : 'text-white hover:bg-white/20'
                  }
                `}
              >
                🛒 E-Commerce
              </button>
              <button
                onClick={() => handleViewModeChange('lead')}
                className={`
                  px-6 py-2 rounded-md text-sm font-semibold transition-all duration-200
                  ${viewMode === 'lead'
                    ? 'bg-white text-[#667eea] shadow-md'
                    : 'text-white hover:bg-white/20'
                  }
                `}
              >
                📋 Lead Generation
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
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

        {/* Summary Cards - Lên đầu tiên sau view mode tabs */}
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
            totalCheckouts: 0,
            currency: currency,
          }}
          viewMode={viewMode}
          isLoading={loading}
        />

        {/* FiltersBar - Chuyển xuống dưới cạnh Table Header */}
        <div className="mb-6">
          <FiltersBar
            filters={filters}
            onFiltersChange={setFilters}
            onRefresh={handleRefresh}
            isLoading={loading}
            viewMode={viewMode}
          />
        </div>

        {/* Table Header with Level Selector - Improved Layout */}
        <div className="bg-white rounded-t-xl shadow-sm border border-gray-200 border-b-0 px-6 py-4 mb-0">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              {viewMode === 'ecommerce' ? (
                <>
                  <span>🛒</span>
                  <span>Chi Tiết Quảng Cáo E-Commerce</span>
                </>
              ) : (
                <>
                  <span>📋</span>
                  <span>Chi Tiết Quảng Cáo Lead Generation</span>
                </>
              )}
            </h2>
            
            {/* Level Tabs */}
            <div className="flex items-center gap-2">
              {/* Drill-down Path */}
              {drillDownPath && (drillDownPath.campaignId || drillDownPath.adsetId) && (
                <div className="flex items-center gap-2 px-4 py-2 bg-indigo-50 rounded-lg border border-indigo-200">
                  {drillDownPath.campaignId && (
                    <>
                      <span className="text-sm font-medium text-indigo-700">
                        🎯 {drillDownPath.campaignName || drillDownPath.campaignId}
                      </span>
                      {drillDownPath.adsetId && (
                        <>
                          <span className="text-indigo-400">→</span>
                          <span className="text-sm font-medium text-indigo-700">
                            📊 {drillDownPath.adsetName || drillDownPath.adsetId}
                          </span>
                        </>
                      )}
                    </>
                  )}
                  {handleDrillUp && (
                    <button
                      onClick={handleDrillUp}
                      className="ml-2 px-2 py-1 text-xs bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
                      title="Quay lại"
                    >
                      ← Quay lại
                    </button>
                  )}
                </div>
              )}

              {/* Level Selector Buttons */}
              <div className="inline-flex rounded-xl border-2 border-gray-200 bg-white p-1">
                <button
                  onClick={() => handleLevelChange('campaign')}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200
                    ${currentLevel === 'campaign'
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                >
                  🎯 Chiến dịch
                </button>
                <button
                  onClick={() => handleLevelChange('adset')}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200
                    ${currentLevel === 'adset'
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                >
                  📊 Nhóm QC
                </button>
                <button
                  onClick={() => handleLevelChange('ad')}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200
                    ${currentLevel === 'ad'
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                >
                  📱 Quảng cáo
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Bulk Actions Bar - Beautiful Design */}
        {selectedIds.size > 0 && (
          <div className="mb-6 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-5 shadow-xl animate-fadeIn">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="bg-white/20 rounded-lg p-2">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <div className="text-white font-bold text-lg">
                    {selectedIds.size} đã chọn
                  </div>
                  <div className="text-indigo-100 text-xs">
                    Thao tác hàng loạt
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowBudgetModal(true)}
                  className="px-5 py-2.5 bg-white text-indigo-600 rounded-lg hover:bg-indigo-50 transition-all shadow-lg hover:shadow-xl font-semibold transform hover:scale-105 active:scale-95"
                >
                  💰 Điều chỉnh NS
                </button>
                <button
                  onClick={() => handleStatusUpdate('resume')}
                  disabled={loading}
                  className="px-5 py-2.5 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-all shadow-lg hover:shadow-xl font-semibold disabled:opacity-50 transform hover:scale-105 active:scale-95"
                >
                  ▶️ Bật
                </button>
                <button
                  onClick={() => handleStatusUpdate('pause')}
                  disabled={loading}
                  className="px-5 py-2.5 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-all shadow-lg hover:shadow-xl font-semibold disabled:opacity-50 transform hover:scale-105 active:scale-95"
                >
                  ⏸️ Tắt
                </button>
                <button 
                  onClick={() => setSelectedIds(new Set())}
                  className="px-4 py-2.5 bg-white/10 text-white border border-white/30 rounded-lg hover:bg-white/20 transition-all font-medium backdrop-blur-sm"
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
          currentLevel={currentLevel}
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
