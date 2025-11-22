import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import SummaryCards from './components/SummaryCards';
import AdsetTable from './components/AdsetTable';
import FiltersBar from './components/FiltersBar';
import BudgetModal from './components/BudgetModal';
import ConfirmModal from './components/ConfirmModal';
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
  AdsetStatus,
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
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmAction, setConfirmAction] = useState<'pause' | 'resume' | null>(null);
  const [bulkProgress, setBulkProgress] = useState<{ current: number; total: number } | null>(null);
  const [batchProgress, setBatchProgress] = useState<{ total: number; done: number; status: string } | null>(null);
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

  // 🔹 NHIỆM VỤ 3: Tính totals từ rows hiện tại (sau filter) cho footer
  const calculatedTotals = React.useMemo(() => {
    if (!sortedRows || sortedRows.length === 0) {
      return undefined;
    }

    const totals = sortedRows.reduce(
      (acc, row) => {
        acc.spend += Number(row.spend || 0);
        acc.results += Number(row.results || 0);
        acc.checkouts_initiated += Number(row.checkouts_initiated || row.initiated_checkout || 0);
        acc.purchases += Number(row.purchases || 0);
        acc.purchase_value += Number(row.purchase_value || 0);
        acc.impressions += Number(row.impressions || 0);
        acc.reach += Number(row.reach || 0);
        acc.clicks += Number(row.clicks || 0);
        acc.data_cost += Number(row.data_cost || 0);
        acc.cost_per_checkout_initiated += Number(row.cost_per_checkout_initiated || 0);
        acc.cost_per_purchase += Number(row.cost_per_purchase || 0);
        acc.cpm += Number(row.cpm || 0);
        acc.ctr += Number(row.ctr || 0);
        acc.cpc += Number(row.cpc || 0);
        acc.frequency += Number(row.frequency || 0);
        
        // E-Commerce specific
        if (viewMode === 'ecommerce') {
          acc.ads_percent += Number(row.ads_percent || 0);
          acc.tlc += Number(row.tlc || 0);
        }
        
        return acc;
      },
      {
        spend: 0,
        results: 0,
        checkouts_initiated: 0,
        purchases: 0,
        purchase_value: 0,
        impressions: 0,
        reach: 0,
        clicks: 0,
        data_cost: 0,
        cost_per_checkout_initiated: 0,
        cost_per_purchase: 0,
        cpm: 0,
        ctr: 0,
        cpc: 0,
        frequency: 0,
        ads_percent: 0,
        tlc: 0,
      }
    );

    // Tính các metrics trung bình / tổng hợp
    return {
      ...totals,
      // Trung bình cho các metrics cần chia
      data_cost: totals.results > 0 ? totals.spend / totals.results : 0,
      cost_per_checkout_initiated: totals.checkouts_initiated > 0 ? totals.spend / totals.checkouts_initiated : 0,
      cost_per_purchase: totals.purchases > 0 ? totals.spend / totals.purchases : 0,
      cpm: totals.impressions > 0 ? (totals.spend / totals.impressions) * 1000 : 0,
      ctr: totals.impressions > 0 ? (totals.clicks / totals.impressions) * 100 : 0,
      cpc: totals.clicks > 0 ? totals.spend / totals.clicks : 0,
      frequency: totals.reach > 0 ? totals.impressions / totals.reach : 0,
      // % ADS cho E-Commerce (tổng spend / tổng purchase_value * 100)
      ads_percent: totals.purchase_value > 0 ? (totals.spend / totals.purchase_value) * 100 : 0,
      // TLC (tỷ lệ chuyển đổi) = purchases / checkouts_initiated * 100
      tlc: totals.checkouts_initiated > 0 ? (totals.purchases / totals.checkouts_initiated) * 100 : 0,
      // Alias cho initiated_checkout
      initiated_checkout: totals.checkouts_initiated,
    };
  }, [sortedRows, viewMode]);

  // Handle force refresh
  const handleRefresh = () => {
    setFilters(prev => ({ ...prev, force_refresh: 1 }));
    setTimeout(() => {
      setFilters(prev => ({ ...prev, force_refresh: 0 }));
    }, 1000);
  };

  // Handle budget update - bulk
  // 🔹 FIX LỖI 2 & 3: Xác định đúng level, KHÔNG reload toàn bộ, hiển thị progress
  const handleBudgetUpdate = async (changes: { id: string; new_budget: number }[]) => {
    try {
      setLoading(true);
      
      // ✅ MỚI: GỬI TẤT CẢ items được chọn (không lọc CBO/trọn đời)
      setBatchProgress({ 
        total: changes.length, 
        done: 0, 
        status: 'Đang cập nhật...'
      });
      
      const operations = changes.map(change => {
        // Tìm row tương ứng để xác định budget_level
        const row = data?.details.rows.find(r => 
          r.id === change.id || 
          r.adset_id === change.id || 
          r.campaign_id === change.id
        );
        
        // Xác định level: nếu row có budget_level = CAMPAIGN hoặc using_campaign_budget → CAMPAIGN
        let opLevel: 'CAMPAIGN' | 'ADSET' = 'ADSET';
        let campaignId: string | undefined;
        
        if (row) {
          if (row.budget_level === 'CAMPAIGN' || row.using_campaign_budget) {
            opLevel = 'CAMPAIGN';
          }
          // Luôn gửi campaign_id để backend có thể gom CBO
          campaignId = row.campaign_id;
        } else if (currentLevel === 'campaign') {
          // Fallback: nếu ở tab campaign và không tìm thấy row → assume CAMPAIGN
          opLevel = 'CAMPAIGN';
        }
        
        return {
          level: opLevel,
          id: change.id,
          new_budget: change.new_budget,
          campaign_id: campaignId,
          budget_edit_level: row?.budget_edit_level,
          budget_edit_reason: row?.budget_edit_reason,
        };
      });
      
      // FIX LỖI 1: Gọi API update với batch processing (backend xử lý song song)
      const response = await updateBudget({
        operations,
        view_mode: viewMode,
      });
      
      // FIX LỖI 3: Cập nhật progress từ response (total, success_count, failed_count)
      const successCount = response.success_count || 0;
      const failedCount = response.failed_count || 0;
      setBatchProgress({ 
        total: response.total || changes.length, 
        done: successCount, 
        status: `Hoàn thành ${successCount}/${response.total}` + (failedCount > 0 ? ` (${failedCount} lỗi)` : '')
      });
      
      // FIX LỖI 2: KHÔNG gọi fetchData() - cập nhật state trực tiếp từ response
      if (data && response.results && response.results.length > 0) {
        setData(prevData => {
          if (!prevData) return prevData;
          
          // Map results để update budget trong rows
          const updatedRows = prevData.details.rows.map(row => {
            const result = response.results.find(r => 
              r.id === row.id || r.id === row.adset_id || r.id === row.campaign_id
            );
            
            if (result && result.status === 'ok') {
              // Cập nhật budget mới từ response
              return {
                ...row,
                budget: result.new_budget,
                daily_budget: result.budget_type === 'DAILY' ? result.new_budget : row.daily_budget,
                lifetime_budget: result.budget_type === 'LIFETIME' ? result.new_budget : row.lifetime_budget,
              };
            }
            return row;
          });
          
          return {
            ...prevData,
            details: {
              ...prevData.details,
              rows: updatedRows,
            },
          };
        });
      }
      
      // Clear selection và ẩn progress sau 1.5s
      setSelectedIds(new Set());
      setTimeout(() => setBatchProgress(null), 1500);
      
    } catch (err) {
      setError(getErrorMessage(err));
      setBatchProgress(null);
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
  // 🔹 FIX: Dùng configured_status hoặc effective_status để xác định status hiện tại
  const handleStatusToggle = async (row: any) => {
    try {
      setLoading(true);
      // Ưu tiên configured_status, sau đó effective_status, cuối cùng delivery
      const currentStatus = (row.configured_status || row.effective_status || row.delivery || 'UNKNOWN').toUpperCase();
      const newStatus = currentStatus === 'ACTIVE' ? 'PAUSED' : 'ACTIVE';
      const rowId = row.id || row.adset_id || row.campaign_id;
      
      const response = await updateStatus({
        level: currentLevel.toUpperCase() as 'CAMPAIGN' | 'ADSET' | 'AD',
        items: [{
          id: rowId,
          new_status: newStatus,
        }],
      });
      
      // ✅ KHÔNG RELOAD - Cập nhật state trực tiếp
      if (data && response.success_ids && response.success_ids.includes(rowId)) {
        setData(prevData => {
          if (!prevData) return prevData;
          
          const updatedRows = prevData.details.rows.map(r => {
            const rId = r.id || r.adset_id || r.campaign_id;
            if (rId === rowId) {
              return {
                ...r,
                delivery: newStatus as AdsetStatus,
                configured_status: newStatus,
                effective_status: newStatus,
                is_active_now: newStatus === 'ACTIVE',
              };
            }
            return r;
          });
          
          return {
            ...prevData,
            details: {
              ...prevData.details,
              rows: updatedRows,
            },
          };
        });
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // 🔹 FIX: Thêm confirm modal và progress bar cho bulk actions
  const handleStatusUpdateClick = (action: 'pause' | 'resume') => {
    setConfirmAction(action);
    setShowConfirmModal(true);
  };

  const handleConfirmStatusUpdate = async () => {
    if (!confirmAction) return;
    
    try {
      setLoading(true);
      setShowConfirmModal(false);
      
      const selectedIdsArray = Array.from(selectedIds);
      const total = selectedIdsArray.length;
      const newStatus = (confirmAction === 'pause' ? 'PAUSED' : 'ACTIVE') as 'ACTIVE' | 'PAUSED';
      
      // ✅ Hiển thị progress ban đầu
      setBulkProgress({ current: 0, total });
      
      // ✅ GỬI 1 REQUEST DUY NHẤT với tất cả IDs
      const response = await updateStatus({
        level: currentLevel.toUpperCase() as 'CAMPAIGN' | 'ADSET' | 'AD',
        items: selectedIdsArray.map(id => ({
          id,
          new_status: newStatus,
        })),
      });
      
      const successCount = response.success_count || 0;
      const failedCount = response.failed_count || 0;
      const successIds = response.success_ids || [];
      
      // ✅ Cập nhật progress
      setBulkProgress({ current: successCount, total });
      
      // ✅ KHÔNG RELOAD - Cập nhật state trực tiếp
      if (data && successIds.length > 0) {
        setData(prevData => {
          if (!prevData) return prevData;
          
          const successIdSet = new Set(successIds);
          const updatedRows = prevData.details.rows.map(row => {
            const rowId = row.id || row.adset_id || row.campaign_id;
            if (successIdSet.has(rowId)) {
              // Cập nhật status mới
              return {
                ...row,
                delivery: newStatus as AdsetStatus,
                configured_status: newStatus,
                effective_status: newStatus,
                is_active_now: newStatus === 'ACTIVE',
              };
            }
            return row;
          });
          
          return {
            ...prevData,
            details: {
              ...prevData.details,
              rows: updatedRows,
            },
          };
        });
      }
      
      // Đợi 1 chút để user thấy progress 100%
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Clear selection và ẩn progress
      setSelectedIds(new Set());
      setBulkProgress(null);
      setConfirmAction(null);
      
      // Hiển thị thông báo
      if (failedCount === 0) {
        // Tất cả thành công - có thể show toast
        console.log(`✅ Đã ${confirmAction === 'pause' ? 'tắt' : 'bật'} thành công ${successCount}/${total} ${currentLevel}`);
      } else {
        setError(`Đã xử lý ${successCount}/${total} item thành công. ${failedCount} item thất bại.`);
      }
    } catch (err) {
      setError(getErrorMessage(err));
      setBulkProgress(null);
      setConfirmAction(null);
    } finally {
      setLoading(false);
    }
  };

  // Handle budget update - single row
  // 🔹 FIX: Xác định đúng level dựa trên budget_level và using_campaign_budget
  const handleBudgetUpdateSingle = async (row: any, newBudget: number) => {
    try {
      setLoading(true);
      const targetId = row.id || row.adset_id || row.campaign_id || row.ad_id || '';
      
      // 🔹 FIX: Xác định level đúng
      let opLevel: 'CAMPAIGN' | 'ADSET' = 'ADSET';
      let actualId = targetId;
      
      if (row.budget_level === 'CAMPAIGN' || row.using_campaign_budget) {
        // Nếu là campaign budget, dùng campaign_id
        opLevel = 'CAMPAIGN';
        actualId = row.campaign_id || targetId;
      }
      
      const response = await updateBudget({
        operations: [{
          level: opLevel,
          id: actualId,
          new_budget: newBudget,
        }],
        view_mode: viewMode,
      });
      
      // FIX LỖI 2: KHÔNG reload - cập nhật local state
      if (data && response.results && response.results.length > 0) {
        const result = response.results[0];
        if (result && result.status === 'ok') {
          setData(prevData => {
            if (!prevData) return prevData;
            
            const updatedRows = prevData.details.rows.map(r => {
              if (r.id === actualId || r.adset_id === actualId || r.campaign_id === actualId) {
                return {
                  ...r,
                  budget: result.new_budget,
                  daily_budget: result.budget_type === 'daily_budget' ? result.new_budget : r.daily_budget,
                  lifetime_budget: result.budget_type === 'lifetime_budget' ? result.new_budget : r.lifetime_budget,
                };
              }
              return r;
            });
            
            return {
              ...prevData,
              details: {
                ...prevData.details,
                rows: updatedRows,
              },
            };
          });
        }
      }
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

        {/* Bulk Actions Bar - Di chuyển xuống dưới header "Chi Tiết Quảng Cáo" */}
        {selectedIds.size > 0 && (() => {
          return (
          <div className="sticky top-0 z-20 mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-4 shadow-xl animate-fadeIn">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="bg-white/20 rounded-lg p-2">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <div className="text-white font-bold text-base">
                    {selectedIds.size} đã chọn
                  </div>
                  <div className="text-indigo-100 text-xs">
                    Thao tác hàng loạt
                  </div>
                  {/* Progress Bar - Status Update */}
                  {bulkProgress && (
                    <div className="mt-2">
                      <div className="flex items-center gap-2 text-xs text-white/90">
                        <span>Đang xử lý {bulkProgress.current} / {bulkProgress.total}</span>
                        <span className="text-white/70">
                          ({Math.round((bulkProgress.current / bulkProgress.total) * 100)}%)
                        </span>
                      </div>
                      <div className="mt-1 w-full bg-white/20 rounded-full h-1.5">
                        <div 
                          className="bg-white rounded-full h-1.5 transition-all duration-300"
                          style={{ width: `${(bulkProgress.current / bulkProgress.total) * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                  {/* Progress Bar - Budget Update */}
                  {batchProgress && (
                    <div className="mt-2">
                      <div className="flex items-center gap-2 text-xs text-white/90">
                        <span>{batchProgress.status}</span>
                        {batchProgress.done > 0 && (
                          <span className="text-white/70">
                            ({Math.round((batchProgress.done / batchProgress.total) * 100)}%)
                          </span>
                        )}
                      </div>
                      <div className="mt-1 w-full bg-white/20 rounded-full h-1.5">
                        <div 
                          className="bg-white rounded-full h-1.5 transition-all duration-300"
                          style={{ width: `${(batchProgress.done / batchProgress.total) * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowBudgetModal(true)}
                  disabled={loading || !!bulkProgress || !!batchProgress}
                  className="px-4 py-2 bg-white text-indigo-600 rounded-lg hover:bg-indigo-50 transition-all shadow-lg hover:shadow-xl font-semibold disabled:opacity-50 transform hover:scale-105 active:scale-95 text-sm"
                >
                  💰 Điều chỉnh NS
                </button>
                <button
                  onClick={() => handleStatusUpdateClick('resume')}
                  disabled={loading || !!bulkProgress || !!batchProgress}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-all shadow-lg hover:shadow-xl font-semibold disabled:opacity-50 transform hover:scale-105 active:scale-95 text-sm"
                >
                  ▶️ Bật
                </button>
                <button
                  onClick={() => handleStatusUpdateClick('pause')}
                  disabled={loading || !!bulkProgress || !!batchProgress}
                  className="px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-all shadow-lg hover:shadow-xl font-semibold disabled:opacity-50 transform hover:scale-105 active:scale-95 text-sm"
                >
                  ⏸️ Tắt
                </button>
                <button 
                  onClick={() => {
                    setSelectedIds(new Set());
                    setBulkProgress(null);
                    setBatchProgress(null);
                  }}
                  disabled={loading || !!bulkProgress || !!batchProgress}
                  className="px-3 py-2 bg-white/10 text-white border border-white/30 rounded-lg hover:bg-white/20 transition-all font-medium backdrop-blur-sm disabled:opacity-50 text-sm"
                >
                  ✖️ Bỏ chọn
                </button>
              </div>
            </div>
          </div>
          );
        })()}

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
          totals={calculatedTotals}
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
        currentLevel={currentLevel}
        batchProgress={batchProgress}
      />

      {/* Confirm Modal for Bulk Actions */}
      <ConfirmModal
        isOpen={showConfirmModal}
        onClose={() => {
          setShowConfirmModal(false);
          setConfirmAction(null);
        }}
        onConfirm={handleConfirmStatusUpdate}
        title={
          confirmAction === 'pause'
            ? `Tắt ${selectedIds.size} ${currentLevel === 'campaign' ? 'chiến dịch' : currentLevel === 'adset' ? 'nhóm quảng cáo' : 'quảng cáo'}?`
            : `Bật ${selectedIds.size} ${currentLevel === 'campaign' ? 'chiến dịch' : currentLevel === 'adset' ? 'nhóm quảng cáo' : 'quảng cáo'}?`
        }
        message={
          confirmAction === 'pause'
            ? `Bạn chắc chắn muốn tắt ${selectedIds.size} ${currentLevel === 'campaign' ? 'chiến dịch' : currentLevel === 'adset' ? 'nhóm quảng cáo' : 'quảng cáo'} không?`
            : `Bạn chắc chắn muốn bật ${selectedIds.size} ${currentLevel === 'campaign' ? 'chiến dịch' : currentLevel === 'adset' ? 'nhóm quảng cáo' : 'quảng cáo'} không?`
        }
        confirmText={confirmAction === 'pause' ? 'Tắt' : 'Bật'}
        cancelText="Hủy"
        loading={loading && !!bulkProgress}
      />
    </div>
  );
}

export default App;
