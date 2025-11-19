import React from 'react';
import { Search, Filter, RefreshCw, Calendar, Settings } from 'lucide-react';
import FilterPresetDropdown from './FilterPresetDropdown';
import DateRangePickerPopover from './DateRangePickerPopover';

export type ViewType = 'ecommerce' | 'lead';
export type LevelType = 'campaign' | 'adset' | 'ad';

export interface DateRange {
  from: Date;
  to: Date;
}

export interface AdsControlsBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  selectedPreset?: string;
  onPresetChange: (preset: string) => void;
  dateRange: DateRange;
  onDateRangeChange: (range: DateRange) => void;
  view: ViewType;
  onViewChange: (view: ViewType) => void;
  level?: LevelType;
  onLevelChange?: (level: LevelType) => void;
  onOpenFilters: () => void;
  onRefresh: () => void;
  onSettings?: () => void;
  activeFiltersCount?: number;
}

const AdsControlsBar: React.FC<AdsControlsBarProps> = ({
  search,
  onSearchChange,
  selectedPreset,
  onPresetChange,
  dateRange,
  onDateRangeChange,
  view,
  onViewChange,
  level = 'adset',
  onLevelChange,
  onOpenFilters,
  onRefresh,
  onSettings,
  activeFiltersCount = 0
}) => {
  const formatDateRange = (range: DateRange): string => {
    const formatDate = (date: Date) => {
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const year = date.getFullYear();
      return `${month}/${day}/${year}`;
    };

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const fromDate = new Date(range.from);
    fromDate.setHours(0, 0, 0, 0);
    const toDate = new Date(range.to);
    toDate.setHours(0, 0, 0, 0);

    const isToday = fromDate.getTime() === today.getTime() && toDate.getTime() === today.getTime();
    const isYesterday = fromDate.getTime() === today.getTime() - 86400000 && toDate.getTime() === today.getTime() - 86400000;
    const diffDays = Math.ceil((toDate.getTime() - fromDate.getTime()) / (1000 * 60 * 60 * 24));

    let label = '';
    if (isToday) {
      label = 'Hôm nay';
    } else if (isYesterday) {
      label = 'Hôm qua';
    } else if (diffDays === 6) {
      label = '7 ngày qua';
    } else if (diffDays === 13) {
      label = '14 ngày qua';
    } else if (diffDays === 29) {
      label = '30 ngày qua';
    } else {
      label = `${formatDate(range.from)} - ${formatDate(range.to)}`;
    }

    return label;
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 mb-6">
      <div className="flex flex-wrap items-center gap-3">
        {/* Filters Button */}
        <button
          onClick={onOpenFilters}
          className="inline-flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 border border-slate-200 transition-colors"
        >
          <Filter className="w-4 h-4" />
          <span>Bộ lọc</span>
          {activeFiltersCount > 0 && (
            <span className="ml-1 px-1.5 py-0.5 text-xs font-semibold text-white bg-purple-600 rounded-full min-w-[18px] text-center">
              {activeFiltersCount}
            </span>
          )}
        </button>

        {/* Search Input */}
        <div className="relative flex-1 min-w-[260px]">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Tìm kiếm theo tên chiến dịch, adset, quảng cáo..."
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 bg-white text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
          />
        </div>

        {/* Filter Preset Dropdown */}
        <FilterPresetDropdown
          selectedPreset={selectedPreset}
          onPresetChange={onPresetChange}
        />

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-white border border-slate-200 text-slate-600 hover:bg-purple-50 hover:border-purple-200 hover:text-purple-600 transition-colors"
          title="Làm mới dữ liệu"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* Date Range Button */}
        <DateRangePickerPopover
          value={dateRange}
          onChange={onDateRangeChange}
        >
          <button className="inline-flex items-center gap-2 rounded-xl bg-white border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors">
            <Calendar className="w-4 h-4" />
            <div className="flex flex-col items-start">
              <span className="font-medium">{formatDateRange(dateRange)}</span>
              <span className="text-xs text-slate-500">
                {formatDateRange(dateRange).includes('/') 
                  ? `${String(dateRange.from.getDate()).padStart(2, '0')}/${String(dateRange.from.getMonth() + 1).padStart(2, '0')}/${dateRange.from.getFullYear()} - ${String(dateRange.to.getDate()).padStart(2, '0')}/${String(dateRange.to.getMonth() + 1).padStart(2, '0')}/${dateRange.to.getFullYear()}`
                  : `${String(dateRange.from.getDate()).padStart(2, '0')}/${String(dateRange.from.getMonth() + 1).padStart(2, '0')}/${dateRange.from.getFullYear()} - ${String(dateRange.to.getDate()).padStart(2, '0')}/${String(dateRange.to.getMonth() + 1).padStart(2, '0')}/${dateRange.to.getFullYear()}`
                }
              </span>
            </div>
          </button>
        </DateRangePickerPopover>

        {/* View Dropdown */}
        <div className="relative">
          <select
            value={view}
            onChange={(e) => onViewChange(e.target.value as ViewType)}
            className="appearance-none inline-flex items-center gap-2 rounded-xl bg-white border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all cursor-pointer pr-8"
          >
            <option value="ecommerce">🛒 E-Commerce</option>
            <option value="lead">🎯 Lead Generation</option>
          </select>
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        {/* Level Selector */}
        {onLevelChange && (
          <div className="relative">
            <select
              value={level}
              onChange={(e) => onLevelChange(e.target.value as LevelType)}
              className="appearance-none inline-flex items-center gap-2 rounded-xl bg-white border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all cursor-pointer pr-8"
            >
              <option value="campaign">📊 Campaign</option>
              <option value="adset">🎯 Adset</option>
              <option value="ad">📢 Ad</option>
            </select>
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        )}

        {/* Settings Button */}
        {onSettings && (
          <button
            onClick={onSettings}
            className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-white border border-slate-200 text-slate-600 hover:bg-purple-50 hover:border-purple-200 hover:text-purple-600 transition-colors"
            title="Cài đặt"
          >
            <Settings className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default AdsControlsBar;

