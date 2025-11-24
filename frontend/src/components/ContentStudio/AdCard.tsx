/**
 * Ad Card Component
 * Card hiển thị quảng cáo/nội dung từ các nguồn
 */

import React from 'react';
import { ContentSource, MediaType, ContentSourceType } from '../../types/contentStudio';

interface AdCardProps {
  content: ContentSource;
  onViewDetail: (content: ContentSource) => void;
  onDownload: (content: ContentSource) => void;
  onAddToCollection: (content: ContentSource) => void;
}

const AdCard: React.FC<AdCardProps> = ({
  content,
  onViewDetail,
  onDownload,
  onAddToCollection
}) => {
  const getSourceIcon = (sourceType: ContentSourceType) => {
    switch (sourceType) {
      case ContentSourceType.TIKTOK:
        return '🎵';
      case ContentSourceType.FACEBOOK_POST:
        return '👥';
      case ContentSourceType.FACEBOOK_ADS_LIBRARY:
        return '📢';
      case ContentSourceType.COLLECTION:
        return '📁';
      case ContentSourceType.MANUAL_UPLOAD:
        return '📤';
      default:
        return '📄';
    }
  };

  const getSourceLabel = (sourceType: ContentSourceType) => {
    switch (sourceType) {
      case ContentSourceType.TIKTOK:
        return 'TikTok';
      case ContentSourceType.FACEBOOK_POST:
        return 'Facebook Post';
      case ContentSourceType.FACEBOOK_ADS_LIBRARY:
        return 'Ads Library';
      case ContentSourceType.COLLECTION:
        return 'Bộ sưu tập';
      case ContentSourceType.MANUAL_UPLOAD:
        return 'Upload';
      default:
        return 'Unknown';
    }
  };

  const primaryMedia = content.media[0];
  const truncatedCaption = content.caption.length > 100
    ? content.caption.substring(0, 100) + '...'
    : content.caption;

  return (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden group">
      {/* Media Preview */}
      <div className="relative aspect-video bg-gray-100">
        {primaryMedia ? (
          <>
            {primaryMedia.type === MediaType.VIDEO ? (
              <video
                src={primaryMedia.url}
                poster={primaryMedia.thumbnailUrl}
                className="w-full h-full object-cover"
              />
            ) : (
              <img
                src={primaryMedia.thumbnailUrl || primaryMedia.url}
                alt="Preview"
                className="w-full h-full object-cover"
              />
            )}
            
            {/* Media Type Badge */}
            <div className="absolute top-2 left-2 bg-black bg-opacity-60 text-white px-2 py-1 rounded text-xs">
              {primaryMedia.type === MediaType.VIDEO ? '🎥 Video' : '🖼️ Hình ảnh'}
              {content.media.length > 1 && ` +${content.media.length - 1}`}
            </div>
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            Không có media
          </div>
        )}

        {/* Source Badge */}
        <div className="absolute top-2 right-2 bg-white bg-opacity-90 px-2 py-1 rounded text-xs font-medium">
          {getSourceIcon(content.sourceType)} {getSourceLabel(content.sourceType)}
        </div>

        {/* Hover Overlay */}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
          <button
            onClick={() => onViewDetail(content)}
            className="bg-white text-gray-800 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
          >
            👁️ Xem chi tiết
          </button>
        </div>
      </div>

      {/* Content Info */}
      <div className="p-4 space-y-3">
        {/* Caption */}
        <p className="text-sm text-gray-700 line-clamp-3">
          {truncatedCaption}
        </p>

        {/* Stats */}
        {(content.views || content.likes || content.comments || content.shares) && (
          <div className="flex gap-4 text-xs text-gray-500">
            {content.views && <span>👁️ {content.views.toLocaleString()}</span>}
            {content.likes && <span>❤️ {content.likes.toLocaleString()}</span>}
            {content.comments && <span>💬 {content.comments.toLocaleString()}</span>}
            {content.shares && <span>🔄 {content.shares.toLocaleString()}</span>}
          </div>
        )}

        {/* Author */}
        {content.authorName && (
          <div className="flex items-center gap-2">
            {content.authorAvatar && (
              <img
                src={content.authorAvatar}
                alt={content.authorName}
                className="w-6 h-6 rounded-full"
              />
            )}
            <span className="text-xs text-gray-600">{content.authorName}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2 border-t border-gray-100">
          <button
            onClick={() => onDownload(content)}
            className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            ⬇️ Tải về
          </button>
          <button
            onClick={() => onAddToCollection(content)}
            className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            ➕ Lưu vào bộ sưu tập
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdCard;
