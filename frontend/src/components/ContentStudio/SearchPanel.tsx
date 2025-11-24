/**
 * Search Panel Component
 * Thanh tìm kiếm và filter cho Content Studio
 */

import React, { useState } from 'react';
import { ContentSourceType } from '../../types/contentStudio';

interface SearchPanelProps {
  onSearch: (query: string, sourceType?: ContentSourceType) => void;
  onFetchUrls: (urls: string[]) => void;
  onUploadFiles: (files: File[]) => void;
  isLoading?: boolean;
}

const SearchPanel: React.FC<SearchPanelProps> = ({
  onSearch,
  onFetchUrls,
  onUploadFiles,
  isLoading = false
}) => {
  const [query, setQuery] = useState('');
  const [sourceType, setSourceType] = useState<ContentSourceType | ''>('');
  const [urlsText, setUrlsText] = useState('');
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleSearch = () => {
    onSearch(query, sourceType || undefined);
  };

  const handleFetchUrls = () => {
    const urls = urlsText
      .split('\n')
      .map(url => url.trim())
      .filter(url => url.length > 0);
    
    if (urls.length > 0) {
      onFetchUrls(urls);
      setUrlsText('');
      setShowUrlInput(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      onUploadFiles(files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onUploadFiles(Array.from(files));
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 space-y-4">
      {/* Search Bar */}
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Nhập từ khóa tìm kiếm..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        
        <select
          value={sourceType}
          onChange={(e) => setSourceType(e.target.value as ContentSourceType | '')}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        >
          <option value="">Tất cả nguồn</option>
          <option value={ContentSourceType.FACEBOOK_ADS_LIBRARY}>Facebook Ads Library</option>
          <option value={ContentSourceType.FACEBOOK_POST}>Bài viết Facebook</option>
          <option value={ContentSourceType.TIKTOK}>TikTok</option>
          <option value={ContentSourceType.COLLECTION}>Bộ sưu tập</option>
        </select>

        <button
          onClick={handleSearch}
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Đang tìm...
            </span>
          ) : (
            'Tìm kiếm'
          )}
        </button>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => setShowUrlInput(!showUrlInput)}
          className="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
        >
          📎 Lấy từ link
        </button>

        <label className="px-4 py-2 border border-green-600 text-green-600 rounded-lg hover:bg-green-50 transition-colors cursor-pointer">
          📁 Upload từ máy
          <input
            type="file"
            multiple
            accept="image/*,video/*"
            onChange={handleFileInput}
            className="hidden"
          />
        </label>
      </div>

      {/* URL Input */}
      {showUrlInput && (
        <div className="border border-gray-200 rounded-lg p-4 space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            Dán link (mỗi dòng 1 link):
          </label>
          <textarea
            value={urlsText}
            onChange={(e) => setUrlsText(e.target.value)}
            placeholder="https://www.tiktok.com/@user/video/123&#10;https://www.facebook.com/page/posts/456"
            rows={5}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          />
          <div className="flex gap-3">
            <button
              onClick={handleFetchUrls}
              disabled={!urlsText.trim() || isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              Lấy dữ liệu
            </button>
            <button
              onClick={() => {
                setUrlsText('');
                setShowUrlInput(false);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Hủy
            </button>
          </div>
        </div>
      )}

      {/* Drag & Drop Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-gray-50'
        }`}
      >
        <div className="text-gray-600">
          <p className="text-lg mb-2">🎬 Kéo thả video/ảnh vào đây</p>
          <p className="text-sm text-gray-500">hoặc click nút "Upload từ máy" ở trên</p>
        </div>
      </div>
    </div>
  );
};

export default SearchPanel;
