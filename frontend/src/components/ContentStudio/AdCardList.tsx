/**
 * Ad Card List Component
 * Grid layout hiển thị danh sách quảng cáo với pagination và skeleton loading
 */

import React from 'react';
import AdCard from './AdCard';
import { ContentSource } from '../../types/contentStudio';

interface AdCardListProps {
  contents: ContentSource[];
  isLoading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  onViewDetail: (content: ContentSource) => void;
  onDownload: (content: ContentSource) => void;
  onAddToCollection: (content: ContentSource) => void;
}

const SkeletonCard: React.FC = () => (
  <div className="bg-white rounded-lg shadow-sm overflow-hidden animate-pulse">
    <div className="aspect-video bg-gray-200" />
    <div className="p-4 space-y-3">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-4 bg-gray-200 rounded w-1/2" />
      <div className="flex gap-2 pt-2">
        <div className="flex-1 h-9 bg-gray-200 rounded" />
        <div className="flex-1 h-9 bg-gray-200 rounded" />
      </div>
    </div>
  </div>
);

const AdCardList: React.FC<AdCardListProps> = ({
  contents,
  isLoading = false,
  hasMore = false,
  onLoadMore,
  onViewDetail,
  onDownload,
  onAddToCollection
}) => {
  if (isLoading && contents.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, index) => (
          <SkeletonCard key={index} />
        ))}
      </div>
    );
  }

  if (!isLoading && contents.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-12 text-center">
        <div className="text-gray-400 text-6xl mb-4">🔍</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Chưa có kết quả
        </h3>
        <p className="text-gray-500">
          Thử tìm kiếm bằng từ khóa khác hoặc thêm link để lấy nội dung
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {contents.map((content) => (
          <AdCard
            key={content.id}
            content={content}
            onViewDetail={onViewDetail}
            onDownload={onDownload}
            onAddToCollection={onAddToCollection}
          />
        ))}
      </div>

      {/* Load More */}
      {hasMore && (
        <div className="flex justify-center">
          <button
            onClick={onLoadMore}
            disabled={isLoading}
            className="px-6 py-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Đang tải...
              </span>
            ) : (
              'Xem thêm'
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default AdCardList;
