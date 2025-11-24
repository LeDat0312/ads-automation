/**
 * Schedule Form Component
 * Form lên lịch đăng bài
 */

import React, { useState, useEffect } from 'react';
import { FacebookPage, ContentVariant, ScheduleType } from '../../types/contentStudio';
import { getFacebookPages } from '../../api/contentStudio';

interface ScheduleFormProps {
  variant: ContentVariant | null;
  onSchedule: (pageIds: string[], scheduleType: ScheduleType, fixedTime?: string, randomRangeMinutes?: number) => void;
  isLoading?: boolean;
}

const ScheduleForm: React.FC<ScheduleFormProps> = ({
  variant,
  onSchedule,
  isLoading = false
}) => {
  const [pages, setPages] = useState<FacebookPage[]>([]);
  const [selectedPages, setSelectedPages] = useState<Set<string>>(new Set());
  const [scheduleType, setScheduleType] = useState<ScheduleType>(ScheduleType.NOW);
  const [fixedTime, setFixedTime] = useState('');
  const [randomRange, setRandomRange] = useState(120);
  const [groupFilter, setGroupFilter] = useState('');
  const [isLoadingPages, setIsLoadingPages] = useState(false);

  useEffect(() => {
    loadPages();
  }, []);

  const loadPages = async () => {
    setIsLoadingPages(true);
    try {
      const data = await getFacebookPages();
      setPages(data.filter(p => p.isActive));
    } catch (error) {
      console.error('Error loading pages:', error);
    } finally {
      setIsLoadingPages(false);
    }
  };

  const togglePage = (pageId: string) => {
    const newSelected = new Set(selectedPages);
    if (newSelected.has(pageId)) {
      newSelected.delete(pageId);
    } else {
      newSelected.add(pageId);
    }
    setSelectedPages(newSelected);
  };

  const selectAllInGroup = (groupTag: string) => {
    const pagesInGroup = pages.filter(p => p.groupTag === groupTag);
    const newSelected = new Set(selectedPages);
    pagesInGroup.forEach(p => newSelected.add(p.id));
    setSelectedPages(newSelected);
  };

  const handleSubmit = () => {
    if (selectedPages.size === 0) {
      alert('Vui lòng chọn ít nhất một fanpage');
      return;
    }

    if (scheduleType === ScheduleType.FIXED && !fixedTime) {
      alert('Vui lòng chọn thời gian đăng bài');
      return;
    }

    onSchedule(
      Array.from(selectedPages),
      scheduleType,
      scheduleType === ScheduleType.FIXED ? fixedTime : undefined,
      scheduleType === ScheduleType.RANDOM ? randomRange : undefined
    );
  };

  const groupedPages = pages.reduce((acc, page) => {
    const group = page.groupTag || 'Khác';
    if (!acc[group]) acc[group] = [];
    acc[group].push(page);
    return acc;
  }, {} as Record<string, FacebookPage[]>);

  const filteredGroups = groupFilter
    ? Object.keys(groupedPages).filter(g => g.toLowerCase().includes(groupFilter.toLowerCase()))
    : Object.keys(groupedPages);

  if (!variant) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-12 text-center">
        <div className="text-gray-400 text-6xl mb-4">📅</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Chưa có nội dung để lên lịch
        </h3>
        <p className="text-gray-500">
          Vui lòng hoàn thành biên tập nội dung trước khi lên lịch đăng
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Step 1: Select Pages */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Bước 1: Chọn fanpage đăng bài ({selectedPages.size} đã chọn)
        </h3>

        {/* Group Filter */}
        <input
          type="text"
          placeholder="🔍 Lọc theo nhóm fanpage..."
          value={groupFilter}
          onChange={(e) => setGroupFilter(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
        />

        {isLoadingPages ? (
          <div className="text-center py-8 text-gray-500">Đang tải danh sách fanpage...</div>
        ) : (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {filteredGroups.map((groupName) => (
              <div key={groupName} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">📁 {groupName}</h4>
                  <button
                    onClick={() => selectAllInGroup(groupName)}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    Chọn tất cả
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {groupedPages[groupName].map((page) => (
                    <label
                      key={page.id}
                      className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedPages.has(page.id)}
                        onChange={() => togglePage(page.id)}
                        className="w-4 h-4 text-blue-600"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {page.name}
                        </p>
                        {page.followers && (
                          <p className="text-xs text-gray-500">
                            👥 {page.followers.toLocaleString()} followers
                          </p>
                        )}
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Step 2: Schedule Type */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Bước 2: Chọn thời gian đăng
        </h3>

        <div className="space-y-3">
          {/* Now */}
          <label className="flex items-start gap-3 p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
            <input
              type="radio"
              name="scheduleType"
              value={ScheduleType.NOW}
              checked={scheduleType === ScheduleType.NOW}
              onChange={(e) => setScheduleType(e.target.value as ScheduleType)}
              className="mt-1"
            />
            <div>
              <p className="font-medium text-gray-900">⚡ Đăng ngay</p>
              <p className="text-sm text-gray-500">Bài viết sẽ được đăng lên ngay lập tức</p>
            </div>
          </label>

          {/* Fixed Time */}
          <label className="flex items-start gap-3 p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
            <input
              type="radio"
              name="scheduleType"
              value={ScheduleType.FIXED}
              checked={scheduleType === ScheduleType.FIXED}
              onChange={(e) => setScheduleType(e.target.value as ScheduleType)}
              className="mt-1"
            />
            <div className="flex-1">
              <p className="font-medium text-gray-900 mb-2">🕐 Hẹn giờ cụ thể</p>
              {scheduleType === ScheduleType.FIXED && (
                <input
                  type="datetime-local"
                  value={fixedTime}
                  onChange={(e) => setFixedTime(e.target.value)}
                  min={new Date().toISOString().slice(0, 16)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              )}
            </div>
          </label>

          {/* Random */}
          <label className="flex items-start gap-3 p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
            <input
              type="radio"
              name="scheduleType"
              value={ScheduleType.RANDOM}
              checked={scheduleType === ScheduleType.RANDOM}
              onChange={(e) => setScheduleType(e.target.value as ScheduleType)}
              className="mt-1"
            />
            <div className="flex-1">
              <p className="font-medium text-gray-900 mb-2">🎲 Ngẫu nhiên trong khoảng thời gian</p>
              {scheduleType === ScheduleType.RANDOM && (
                <div className="space-y-2">
                  <input
                    type="range"
                    min="15"
                    max="480"
                    step="15"
                    value={randomRange}
                    onChange={(e) => setRandomRange(Number(e.target.value))}
                    className="w-full"
                  />
                  <p className="text-sm text-gray-600">
                    Đăng ngẫu nhiên từ bây giờ đến <strong>{randomRange} phút</strong> nữa ({Math.floor(randomRange / 60)}h {randomRange % 60}p)
                  </p>
                </div>
              )}
            </div>
          </label>
        </div>
      </div>

      {/* Submit Button */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <button
          onClick={handleSubmit}
          disabled={isLoading || selectedPages.size === 0}
          className="w-full px-6 py-4 bg-green-600 text-white font-semibold text-lg rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Đang lên lịch...
            </span>
          ) : (
            `📅 Lên lịch đăng cho ${selectedPages.size} fanpage`
          )}
        </button>
      </div>
    </div>
  );
};

export default ScheduleForm;
