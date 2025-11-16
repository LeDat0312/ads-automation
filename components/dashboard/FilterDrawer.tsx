import React, { useState, useEffect } from 'react';
import { X, Search, Filter, ChevronUp, ChevronDown } from 'lucide-react';
import FilterPresetDropdown from './FilterPresetDropdown';

export type FilterType = 
  | 'status' 
  | 'name' 
  | 'gender' 
  | 'country' 
  | 'funnel' 
  | 'device' 
  | 'placement' 
  | 'metric';

export interface ActiveFilter {
  id: string;
  type: FilterType;
  label: string;
  value?: any;
}

export interface FilterDrawerProps {
  open: boolean;
  onClose: () => void;
  activeFilters: ActiveFilter[];
  onChangeFilters: (filters: ActiveFilter[]) => void;
  search: string;
  onSearchChange: (value: string) => void;
  selectedPreset?: string;
  onPresetChange: (preset: string) => void;
}

const FILTER_SUGGESTIONS: Array<{ type: FilterType; label: string; icon: string }> = [
  { type: 'status', label: 'Trạng thái là ...', icon: '⚪' },
  { type: 'name', label: 'Tên chứa ...', icon: '📝' },
  { type: 'gender', label: 'Giới tính là ...', icon: '⚧️' },
  { type: 'country', label: 'Quốc gia ...', icon: '🌍' },
  { type: 'funnel', label: 'Giai đoạn phễu là ...', icon: '🔽' },
  { type: 'device', label: 'Thiết bị là ...', icon: '💻' },
  { type: 'placement', label: 'Vị trí đặt là ...', icon: '📱' },
  { type: 'metric', label: 'Chỉ số lớn hơn ...', icon: '📊' },
];

const FilterDrawer: React.FC<FilterDrawerProps> = ({
  open,
  onClose,
  activeFilters,
  onChangeFilters,
  search,
  onSearchChange,
  selectedPreset,
  onPresetChange,
}) => {
  const [localFilters, setLocalFilters] = useState<ActiveFilter[]>(activeFilters);

  useEffect(() => {
    setLocalFilters(activeFilters);
  }, [activeFilters]);

  const handleAddFilter = (type: FilterType) => {
    const suggestion = FILTER_SUGGESTIONS.find(s => s.type === type);
    if (!suggestion) return;

    const newFilter: ActiveFilter = {
      id: `${type}-${Date.now()}`,
      type,
      label: suggestion.label,
      value: null,
    };

    setLocalFilters([...localFilters, newFilter]);
  };

  const handleRemoveFilter = (id: string) => {
    setLocalFilters(localFilters.filter(f => f.id !== id));
  };

  const handleClearAll = () => {
    setLocalFilters([]);
  };

  const handleApply = () => {
    onChangeFilters(localFilters);
    onClose();
  };

  if (!open) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/10 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Drawer Panel */}
      <div className="fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-2xl z-50 max-h-[400px] flex flex-col animate-slide-up">
        {/* Header with Controls */}
        <div className="p-4 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="inline-flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 border border-slate-200 transition-colors"
            >
              <Filter className="w-4 h-4" />
              <span>Bộ lọc</span>
              {localFilters.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs font-semibold text-white bg-purple-600 rounded-full min-w-[18px] text-center">
                  {localFilters.length}
                </span>
              )}
            </button>

            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => onSearchChange(e.target.value)}
                placeholder="Tìm kiếm..."
                className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 bg-white text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div>

            <FilterPresetDropdown
              selectedPreset={selectedPreset}
              onPresetChange={onPresetChange}
            />
          </div>
        </div>

        {/* Suggestions Section */}
        <div className="flex-1 overflow-y-auto p-6">
          <h4 className="text-sm font-semibold text-slate-700 mb-4">Gợi ý</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {FILTER_SUGGESTIONS.map((suggestion) => (
              <button
                key={suggestion.type}
                onClick={() => handleAddFilter(suggestion.type)}
                className="flex items-center gap-2 px-4 py-2 rounded-full bg-slate-50 hover:bg-purple-50 text-slate-700 hover:text-purple-700 text-sm font-medium transition-colors border border-transparent hover:border-purple-200"
              >
                <span>{suggestion.icon}</span>
                <span>{suggestion.label}</span>
              </button>
            ))}
          </div>

          {/* Active Filters Display */}
          {localFilters.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-200">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-slate-700">Bộ lọc đã chọn</h4>
                <button
                  onClick={handleClearAll}
                  className="text-xs text-slate-500 hover:text-slate-700 transition-colors"
                >
                  Xóa tất cả
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {localFilters.map((filter) => (
                  <div
                    key={filter.id}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-50 text-purple-700 text-sm border border-purple-200"
                  >
                    <span>{filter.label}</span>
                    <button
                      onClick={() => handleRemoveFilter(filter.id)}
                      className="hover:bg-purple-100 rounded p-0.5 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 text-sm font-medium hover:bg-slate-50 transition-colors"
          >
            Đóng
          </button>
          <button
            onClick={handleApply}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm font-medium hover:from-purple-700 hover:to-pink-700 transition-all shadow-sm"
          >
            Áp dụng
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes slide-up {
          from {
            transform: translateY(100%);
          }
          to {
            transform: translateY(0);
          }
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
      `}</style>
    </>
  );
};

export default FilterDrawer;

