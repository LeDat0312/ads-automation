import { useState } from 'react';
import type { DashboardFilters } from '@/types/dashboard';

interface FiltersBarProps {
  filters: DashboardFilters;
  onFiltersChange: (filters: DashboardFilters) => void;
  onRefresh: () => void;
  isLoading: boolean;
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

export default function FiltersBar({ filters, onFiltersChange, onRefresh, isLoading }: FiltersBarProps) {
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [tempFilters, setTempFilters] = useState(filters);

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
      date_from: filters.date_from,
      date_to: filters.date_to,
      prefix_filter: undefined,
      search: undefined,
      status_filter: undefined,
    };
    setTempFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

  const activeFiltersCount = [
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
        {/* Status Chips Row */}
        <div className="flex items-center gap-2 mb-4 pb-4 border-b border-gray-200">
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
            onClick={() => onFiltersChange({ ...filters, status_filter: 'ran_today' })}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filters.status_filter === 'ran_today'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            🔥 Đã chạy hôm nay
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
        </div>

        <div className="flex items-center justify-between gap-4">
          {/* Left side - Date and Filters */}
          <div className="flex items-center gap-3 flex-wrap">{/* Date Picker Button */}
            {/* Date Picker Button */}
            <button
              onClick={() => setShowDatePicker(!showDatePicker)}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {formatDateRange()}
            </button>

            {/* Filters Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700 relative"
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

            {/* Active Filters Tags */}
            {filters.prefix_filter && (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-md text-sm">
                Prefix: {filters.prefix_filter}
                <button
                  onClick={() => onFiltersChange({ ...filters, prefix_filter: undefined })}
                  className="hover:text-indigo-900"
                >
                  ×
                </button>
              </span>
            )}
            {filters.status_filter && (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-md text-sm">
                Trạng thái: {filters.status_filter}
                <button
                  onClick={() => onFiltersChange({ ...filters, status_filter: undefined })}
                  className="hover:text-indigo-900"
                >
                  ×
                </button>
              </span>
            )}
            {filters.search && (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-md text-sm">
                Tìm: {filters.search}
                <button
                  onClick={() => onFiltersChange({ ...filters, search: undefined })}
                  className="hover:text-indigo-900"
                >
                  ×
                </button>
              </span>
            )}
          </div>

          {/* Right side - Refresh */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
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
              {/* Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tìm kiếm
                </label>
                <input
                  type="text"
                  value={tempFilters.search || ''}
                  onChange={(e) => setTempFilters({ ...tempFilters, search: e.target.value })}
                  placeholder="Tìm theo tên adset, campaign..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

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

              {/* Prefix Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prefix
                </label>
                <input
                  type="text"
                  value={tempFilters.prefix_filter || ''}
                  onChange={(e) => setTempFilters({ ...tempFilters, prefix_filter: e.target.value || undefined })}
                  placeholder="Nhập prefix..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
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
