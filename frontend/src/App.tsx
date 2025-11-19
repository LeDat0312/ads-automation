import React, { useState, useEffect, useCallback } from 'react';
import SummaryCards from './components/SummaryCards';
import AdsetTable from './components/AdsetTable';
import FiltersBar from './components/FiltersBar';
import BudgetModal from './components/BudgetModal';
import { getDashboardData, getErrorMessage, updateBudget } from './services/api';
import type {
  ViewMode,
  DashboardFilters,
  DashboardDataResponse,
  SortConfig,
  SortableColumn,
  Currency,
} from './types/dashboard';

function App() {
  // State
  const [viewMode, setViewMode] = useState<ViewMode>('ecommerce');
  const [currency] = useState<Currency>('VND'); // TODO: Get from backend
  const [data, setData] = useState<DashboardDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [sortConfig, setSortConfig] = useState<SortConfig>({ column: null, direction: 'desc' });
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  
  // Filters
  const today = new Date().toISOString().split('T')[0];
  const [filters, setFilters] = useState<DashboardFilters>({
    view_mode: 'ecommerce',
    level: 'adset',
    status: 'ALL',
    page: 1,
    pageSize: 50,
    force_refresh: 0,
    date_from: today,
    date_to: today,
  });

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
    // Reset after fetch
    setTimeout(() => {
      setFilters(prev => ({ ...prev, force_refresh: 0 }));
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">
              📊 Dashboard Quảng Cáo Facebook
            </h1>
            
            {/* View Mode Toggle */}
            <div className="flex items-center gap-4">
              <div className="inline-flex rounded-lg border border-gray-300 bg-white p-1">
                <button
                  onClick={() => handleViewModeChange('lead')}
                  className={`
                    px-4 py-2 rounded-md text-sm font-medium transition-colors
                    ${viewMode === 'lead'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                >
                  📋 Lead Generation
                </button>
                <button
                  onClick={() => handleViewModeChange('ecommerce')}
                  className={`
                    px-4 py-2 rounded-md text-sm font-medium transition-colors
                    ${viewMode === 'ecommerce'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                >
                  🛒 E-Commerce
                </button>
              </div>

              <button
                onClick={handleRefresh}
                disabled={loading}
                className="
                  px-4 py-2 bg-blue-600 text-white rounded-lg
                  hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
                  transition-colors font-medium
                "
              >
                {loading ? '⏳ Đang tải...' : '🔄 Làm mới'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <span className="text-red-600 text-xl">⚠️</span>
              <div>
                <h3 className="text-red-900 font-medium">Lỗi</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        <SummaryCards
          summary={data?.summary || {
            totalSpend: 0,
            totalData: 0,
            costPerData: 0,
            totalCheckouts: 0,
            costPerCheckout: 0,
            totalPurchases: 0,
            costPerPurchase: 0,
            purchaseValue: 0,
            activeAdsets: 0,
            pausedAdsets: 0,
            totalAdsets: 0,
          }}
          viewMode={viewMode}
          currency={currency}
          loading={loading}
        />

        {/* Selected Items Actions */}
        {selectedIds.size > 0 && (
          <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-blue-900 font-medium">
                Đã chọn {selectedIds.size} nhóm quảng cáo
              </span>
              <div className="flex gap-2">
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  💰 Điều chỉnh ngân sách
                </button>
                <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  ▶️ Kích hoạt
                </button>
                <button className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors">
                  ⏸️ Tạm dừng
                </button>
                <button 
                  onClick={() => setSelectedIds(new Set())}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
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
        />

        {/* Pagination Info */}
        {data?.details.pagination && !loading && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Hiển thị{' '}
            <span className="font-medium">{data.details.pagination.total_rows}</span>{' '}
            nhóm quảng cáo
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-8 py-6 border-t border-gray-200 bg-white">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-600">
          <p>Dashboard Quảng Cáo Facebook • Powered by React + Vite + FastAPI</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
