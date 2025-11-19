import React from 'react';

interface PaginationInfo {
  page: number;
  page_size: number;
  total_rows: number;
  total_pages: number;
}

interface PaginationControlsProps {
  pagination: PaginationInfo;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  loading?: boolean;
}

export default function PaginationControls({
  pagination,
  onPageChange,
  onPageSizeChange,
  loading = false,
}: PaginationControlsProps) {
  const { page, page_size, total_rows, total_pages } = pagination;

  const handlePrevious = () => {
    if (page > 1 && !loading) {
      onPageChange(page - 1);
    }
  };

  const handleNext = () => {
    if (page < total_pages && !loading) {
      onPageChange(page + 1);
    }
  };

  const handlePageClick = (newPage: number) => {
    if (newPage >= 1 && newPage <= total_pages && newPage !== page && !loading) {
      onPageChange(newPage);
    }
  };

  // Generate page numbers to show
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 7;

    if (total_pages <= maxVisible) {
      // Show all pages
      for (let i = 1; i <= total_pages; i++) {
        pages.push(i);
      }
    } else {
      // Show first page
      pages.push(1);

      if (page > 3) {
        pages.push('...');
      }

      // Show pages around current page
      const start = Math.max(2, page - 1);
      const end = Math.min(total_pages - 1, page + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (page < total_pages - 2) {
        pages.push('...');
      }

      // Show last page
      pages.push(total_pages);
    }

    return pages;
  };

  if (total_rows === 0) {
    return null;
  }

  const startRow = (page - 1) * page_size + 1;
  const endRow = Math.min(page * page_size, total_rows);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between flex-wrap gap-4">
        {/* Info */}
        <div className="text-sm text-gray-600">
          Hiển thị <span className="font-semibold text-gray-900">{startRow}</span> -{' '}
          <span className="font-semibold text-gray-900">{endRow}</span> trong tổng số{' '}
          <span className="font-semibold text-gray-900">{total_rows}</span> kết quả
        </div>

        {/* Page Size Selector */}
        {onPageSizeChange && (
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Hiển thị:</label>
            <select
              value={page_size}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              disabled={loading}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </div>
        )}

        {/* Pagination */}
        <div className="flex items-center gap-2">
          {/* Previous Button */}
          <button
            onClick={handlePrevious}
            disabled={page === 1 || loading}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            ← Trước
          </button>

          {/* Page Numbers */}
          <div className="flex items-center gap-1">
            {getPageNumbers().map((pageNum, index) => {
              if (pageNum === '...') {
                return (
                  <span key={`ellipsis-${index}`} className="px-2 text-gray-400">
                    ...
                  </span>
                );
              }

              const pageNumber = pageNum as number;
              const isActive = pageNumber === page;

              return (
                <button
                  key={pageNumber}
                  onClick={() => handlePageClick(pageNumber)}
                  disabled={loading}
                  className={`
                    min-w-[2.5rem] px-3 py-2 rounded-lg text-sm font-medium transition-colors
                    ${
                      isActive
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }
                    disabled:opacity-50 disabled:cursor-not-allowed
                  `}
                >
                  {pageNumber}
                </button>
              );
            })}
          </div>

          {/* Next Button */}
          <button
            onClick={handleNext}
            disabled={page === total_pages || loading}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Sau →
          </button>
        </div>
      </div>
    </div>
  );
}

