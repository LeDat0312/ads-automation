import React, { useState } from 'react';
import AdsControlsBar, { ViewType, DateRange } from './AdsControlsBar';
import FilterDrawer, { ActiveFilter } from './FilterDrawer';

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

  const handlePresetChange = (preset: string) => {
    setSelectedPreset(preset);
    // TODO: Apply preset logic
    console.log('Preset changed:', preset);
  };

  const handleRefresh = () => {
    // TODO: Refresh data logic
    console.log('Refreshing data...');
  };

  const handleSettings = () => {
    // TODO: Open settings
    console.log('Opening settings...');
  };

  const handleFiltersChange = (filters: ActiveFilter[]) => {
    setActiveFilters(filters);
    // TODO: Apply filters logic
    console.log('Filters changed:', filters);
  };

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
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <p className="text-slate-600">
            Nội dung dashboard sẽ được hiển thị ở đây...
          </p>
          <div className="mt-4 space-y-2 text-sm text-slate-500">
            <p>• Search: {search || '(trống)'}</p>
            <p>• Preset: {selectedPreset || '(không có)'}</p>
            <p>• Date Range: {dateRange.from.toLocaleDateString('vi-VN')} - {dateRange.to.toLocaleDateString('vi-VN')}</p>
            <p>• View: {view}</p>
            <p>• Active Filters: {activeFilters.length}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;

