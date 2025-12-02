/**
 * FacebookReelsStaticPreview.tsx
 * Static thumbnail preview for Facebook Reels
 * NO video player, NO autoplay - just static vertical thumbnail
 */

import { PreviewProps } from '../../types/preview';

export function FacebookReelsStaticPreview({ data, variant }: PreviewProps) {
  const isMobile = variant === 'mobile';
  
  // Truncate caption for Reels (shorter than Feed)
  const maxCaptionLength = isMobile ? 60 : 100;
  const shouldTruncate = data.caption.length > maxCaptionLength;
  const displayCaption = shouldTruncate 
    ? data.caption.slice(0, maxCaptionLength) 
    : data.caption;

  // Mock engagement data
  const reactions = data.reactionsCount ?? 15600;
  const comments = data.commentsCount ?? 937;
  const shares = data.sharesCount ?? 119;

  // Format numbers (15600 → 15.6K)
  const formatCount = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <div 
      className="relative bg-black rounded-xl overflow-hidden"
      style={{ 
        width: isMobile ? '360px' : '480px',
        height: isMobile ? '640px' : '720px'
      }}
    >
      {/* Static Thumbnail - 9:16 Vertical */}
      <div className="absolute inset-0">
        {data.thumbnailUrl ? (
          <img 
            src={data.thumbnailUrl} 
            alt="Reels thumbnail"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-900">
            <div className="text-gray-400 text-center">
              <svg className="w-20 h-20 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p className="text-sm">Chưa có hình ảnh</p>
            </div>
          </div>
        )}
      </div>

      {/* Right Side Actions - Static Icons */}
      <div className={`absolute ${isMobile ? 'right-2 bottom-32' : 'right-4 bottom-40'} flex flex-col gap-5 z-10`}>
        {/* Like */}
        <div className="flex flex-col items-center">
          <div className="w-11 h-11 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <span className="text-white text-xs font-medium mt-1.5 drop-shadow">
            {formatCount(reactions)}
          </span>
        </div>

        {/* Comment */}
        <div className="flex flex-col items-center">
          <div className="w-11 h-11 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <span className="text-white text-xs font-medium mt-1.5 drop-shadow">
            {formatCount(comments)}
          </span>
        </div>

        {/* Share */}
        <div className="flex flex-col items-center">
          <div className="w-11 h-11 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
          </div>
          <span className="text-white text-xs font-medium mt-1.5 drop-shadow">
            {formatCount(shares)}
          </span>
        </div>

        {/* More */}
        <div className="w-11 h-11 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center">
          <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </div>
      </div>

      {/* Bottom Info Overlay - Gradient Background */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/80 to-transparent pt-24 pb-5 px-3 z-10">
        {/* Page Info */}
        <div className="flex items-center gap-2.5 mb-2">
          {/* Avatar */}
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white font-bold overflow-hidden flex-shrink-0">
            {data.pageAvatarUrl ? (
              <img 
                src={data.pageAvatarUrl} 
                alt={data.pageName} 
                className="w-full h-full object-cover" 
              />
            ) : (
              <span className="text-sm">{data.pageName.charAt(0).toUpperCase()}</span>
            )}
          </div>

          {/* Page Name + Verified */}
          <div className="flex items-center gap-1.5 flex-1 min-w-0">
            <span className="font-semibold text-white text-[15px] truncate">
              {data.pageName}
            </span>
            {/* Verified Badge */}
            {data.isVerified !== false && (
              <svg className="w-[18px] h-[18px] text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        </div>

        {/* Caption */}
        {data.caption && (
          <p className="text-white text-[14px] leading-[1.4] mb-1">
            {displayCaption}
            {shouldTruncate && (
              <span className="text-white/80 ml-1 font-medium">…</span>
            )}
          </p>
        )}

        {/* Sponsored Label (if applicable) */}
        {data.isSponsored !== false && (
          <p className="text-white/70 text-xs">Được tài trợ</p>
        )}
      </div>
    </div>
  );
}
