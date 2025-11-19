import { useState, useEffect } from 'react';
import type { DashboardFilters } from '@/types/dashboard';
import { getDashboardFilters } from '@/services/api';

interface FiltersBarProps {
  filters: DashboardFilters;
  onFiltersChange: (filters: DashboardFilters) => void;
  onRefresh: () => void;
  isLoading: boolean;
  viewMode?: 'ecommerce' | 'lead';
}

interface DatePreset {
  label: string;
  value: string;
  getDates: () => { from: string; to: string };
}

const datePresets: DatePreset[] = [
  {
    label: 'Hôm nay',
    value: 'today',
    getDates: () => {
      const today = new Date().toISOString().split('T')[0];
      return { from: today, to: today };
    },
  },
  {
    label: 'Hôm qua',
    value: 'yesterday',
    getDates: () => {
      const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
      return { from: yesterday, to: yesterday };
    },
  },
  {
    label: '7 ngày qua',
    value: 'last_7d',
    getDates: () => {
      const to = new Date().toISOString().split('T')[0];
      const from = new Date(Date.now() - 6 * 86400000).toISOString().split('T')[0];
      return { from, to };
    },
  },
  {
    label: '30 ngày qua',
    value: 'last_30d',
    getDates: () => {
      const to = new Date().toISOString().split('T')[0];
      const from = new Date(Date.now() - 29 * 86400000).toISOString().split('T')[0];
      return { from, to };
    },
  },
  {
    label: 'Tháng này',
    value: 'this_month',
    getDates: () => {
      const now = new Date();
      const from = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
      const to = new Date().toISOString().split('T')[0];
      return { from, to };
    },
  },
  {
    label: 'Tháng trước',
    value: 'last_month',
    getDates: () => {
      const now = new Date();
      const from = new Date(now.getFullYear(), now.getMonth() - 1, 1).toISOString().split('T')[0];
      const to = new Date(now.getFullYear(), now.getMonth(), 0).toISOString().split('T')[0];
      return { from, to };
    },
  },
];

export default function FiltersBar({ filters, onFiltersChange, onRefresh, isLoading, viewMode = 'ecommerce' }: FiltersBarProps) {
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [tempFilters, setTempFilters] = useState(filters);
  const [filterOptions, setFilterOptions] = useState<{
    accounts: Array<{ id: string; name: string; type: string }>;
    prefixes: Array<{ id: string; name: string }>;
  }>({ accounts: [], prefixes: [] });

  // Load filter options
  useEffect(() => {
    getDashboardFilters(viewMode).then((data) => {
      setFilterOptions({
        accounts: data.accounts,
        prefixes: data.prefixes,
      });
    }).catch((err) => {
      console.error('Error loading filter options:', err);
    });
  }, [viewMode]);

  const handleDatePresetClick = (preset: DatePreset) => {
    const dates = preset.getDates();
    onFiltersChange({
      ...filters,
      date_from: dates.from,
      date_to: dates.to,
    });
    setShowDatePicker(false);
  };

  const handleCustomDateApply = () => {
    onFiltersChange(tempFilters);
    setShowDatePicker(false);
  };

  const handleFilterApply = () => {
    onFiltersChange(tempFilters);
    setShowFilters(false);
  };

  const handleClearFilters = () => {
    const clearedFilters: DashboardFilters = {
      ...filters,
      account_ids: undefined,
      prefix_filter: undefined,
      prefix: undefined,
      search: undefined,
      status_filter: undefined,
      status: 'ALL',
    };
    setTempFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

  const activeFiltersCount = [
    filters.account_ids,
    filters.prefix_filter,
    filters.search,
    filters.status_filter,
  ].filter(Boolean).length;

  const formatDateRange = () => {
    if (!filters.date_from || !filters.date_to) return 'Chọn khoảng thời gian';
    
    const from = new Date(filters.date_from);
    const to = new Date(filters.date_to);
    
    const formatDate = (date: Date) => {
      return `${date.getDate()}/${date.getMonth() + 1}`;
    };
    
    if (filters.date_from === filters.date_to) {
      return formatDate(from);
    }
    
    return `${formatDate(from)} - ${formatDate(to)}`;
  };

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        {/* Row 1: Search + Date + Filters + Refresh */}
        <div className="flex items-center gap-3 mb-4">
          {/* Search Box - Prominent */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <input
                type="text"
                value={tempFilters.search || ''}
                onChange={(e) => {
                  setTempFilters({ ...tempFilters, search: e.target.value });
                  onFiltersChange({ ...filters, search: e.target.value || undefined });
                }}
                placeholder="🔍 Tìm kiếm tên/ID chiến dịch, nhóm quảng cáo..."
                className="w-full pl-4 pr-10 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
              />
              {tempFilters.search && (
                <button
                  onClick={() => {
                    setTempFilters({ ...tempFilters, search: '' });
                    onFiltersChange({ ...filters, search: undefined });
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              )}
            </div>
          </div>

          {/* Date Picker Button */}
          <button
            onClick={() => setShowDatePicker(!showDatePicker)}
            className="flex items-center gap-2 px-4 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700 whitespace-nowrap"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            📅 {formatDateRange()}
          </button>

          {/* Filters Button */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-4 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700 relative whitespace-nowrap"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            Bộ lọc
            {activeFiltersCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                {activeFiltersCount}
              </span>
            )}
          </button>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            <svg
              className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Làm mới
          </button>
        </div>

        {/* Row 2: Status Chips */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => onFiltersChange({ ...filters, status_filter: undefined })}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              !filters.status_filter
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            📊 Tất cả
          </button>
          <button
            onClick={() => onFiltersChange({ ...filters, status_filter: 'ACTIVE' })}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filters.status_filter === 'ACTIVE'
                ? 'bg-green-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            ✅ Đang hoạt động
          </button>
          <button
            onClick={() => onFiltersChange({ ...filters, status_filter: 'PAUSED' })}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filters.status_filter === 'PAUSED'
                ? 'bg-amber-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            ⏸️ Đã tạm dừng
          </button>

          {/* Active Filters Tags */}
          {filters.account_ids && (
            <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-md text-sm border border-indigo-200">
              Tài khoản: {filterOptions.accounts.find(a => a.id === filters.account_ids)?.name || filters.account_ids}
              <button
                onClick={() => onFiltersChange({ ...filters, account_ids: undefined })}
                className="hover:text-indigo-900 ml-1"
              >
                ×
              </button>
            </span>
          )}
          {filters.prefix_filter && (
            <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-md text-sm border border-indigo-200">
              Prefix: {filters.prefix_filter}
              <button
                onClick={() => onFiltersChange({ ...filters, prefix_filter: undefined })}
                className="hover:text-indigo-900 ml-1"
              >
                ×
              </button>
            </span>
          )}
        </div>
      </div>

      {/* Date Picker Dropdown */}
      {showDatePicker && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowDatePicker(false)}
          />
          <div className="absolute z-50 mt-2 bg-white rounded-xl shadow-2xl border border-gray-200 p-4 w-80">
            <div className="space-y-2">
              <div className="font-semibold text-gray-700 text-sm mb-3">Khoảng thời gian</div>
              {datePresets.map((preset) => (
                <button
                  key={preset.value}
                  onClick={() => handleDatePresetClick(preset)}
                  className="w-full text-left px-3 py-2 rounded-lg hover:bg-indigo-50 hover:text-indigo-700 transition-colors text-sm"
                >
                  {preset.label}
                </button>
              ))}
              
              <div className="border-t border-gray-200 my-3 pt-3">
                <div className="text-xs font-semibold text-gray-500 mb-2">TÙY CHỈNH</div>
                <div className="space-y-2">
                  <div>
                    <label className="text-xs text-gray-600 mb-1 block">Từ ngày</label>
                    <input
                      type="date"
                      value={tempFilters.date_from || ''}
                      onChange={(e) => setTempFilters({ ...tempFilters, date_from: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-600 mb-1 block">Đến ngày</label>
                    <input
                      type="date"
                      value={tempFilters.date_to || ''}
                      onChange={(e) => setTempFilters({ ...tempFilters, date_to: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <button
                    onClick={handleCustomDateApply}
                    className="w-full mt-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                  >
                    Áp dụng
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Filters Sidebar */}
      {showFilters && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setShowFilters(false)}
          />
          <div className="fixed right-0 top-0 bottom-0 w-96 bg-white shadow-2xl z-50 flex flex-col">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Bộ lọc</h3>
                <button
                  onClick={() => setShowFilters(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Trạng thái
                </label>
                <select
                  value={tempFilters.status_filter || ''}
                  onChange={(e) => setTempFilters({ ...tempFilters, status_filter: e.target.value || undefined })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Tất cả</option>
                  <option value="ACTIVE">Đang chạy</option>
                  <option value="PAUSED">Đã tạm dừng</option>
                </select>
              </div>

              {/* Account Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tài khoản
                </label>
                <select
                  value={tempFilters.account_ids || ''}
                  onChange={(e) => setTempFilters({ ...tempFilters, account_ids: e.target.value || undefined })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Tất cả tài khoản</option>
                  {filterOptions.accounts.map((acc) => (
                    <option key={acc.id} value={acc.id}>
                      {acc.name} ({acc.type})
                    </option>
                  ))}
                </select>
              </div>

              {/* Prefix Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prefix
                </label>
                <select
                  value={tempFilters.prefix_filter || ''}
                  onChange={(e) => setTempFilters({ ...tempFilters, prefix_filter: e.target.value || undefined })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Tất cả prefix</option>
                  {filterOptions.prefixes.map((prefix) => (
                    <option key={prefix.id} value={prefix.id}>
                      {prefix.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex items-center justify-between">
              <button
                onClick={handleClearFilters}
                className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium"
              >
                Xóa bộ lọc
              </button>
              <button
                onClick={handleFilterApply}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                Áp dụng
              </button>
            </div>
          </div>
        </>
      )}
    </>
  );
}
