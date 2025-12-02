/**
 * FacebookFeedStaticPreview.tsx
 * Static thumbnail preview for Facebook Feed (News Feed)
 * NO video player, NO autoplay - just static card like So9/Publer
 */

import { PreviewProps } from '../../types/preview';

export function FacebookFeedStaticPreview({ data, variant }: PreviewProps) {
  const isMobile = variant === 'mobile';
  
  // Truncate caption based on device
  const maxCaptionLength = isMobile ? 100 : 200;
  const shouldTruncate = data.caption.length > maxCaptionLength;
  const displayCaption = shouldTruncate 
    ? data.caption.slice(0, maxCaptionLength) 
    : data.caption;

  // Mock data with defaults
  const reactions = data.reactionsCount ?? 204;
  const comments = data.commentsCount ?? 25;
  const shares = data.sharesCount ?? 5;

  return (
    <div 
      className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
      style={{ width: isMobile ? '390px' : '600px' }}
    >
      {/* Header - Page Info */}
      <div className={`flex items-center gap-2.5 ${isMobile ? 'p-3' : 'p-4'}`}>
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

        {/* Page Name + Sponsored */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className={`font-semibold text-gray-900 truncate ${isMobile ? 'text-[15px]' : 'text-base'}`}>
              {data.pageName}
            </span>
            {/* Verified Badge */}
            {data.isVerified !== false && (
              <svg className="w-[18px] h-[18px] text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
          </div>
          {/* Sponsored Label */}
          {data.isSponsored !== false && (
            <p className="text-xs text-gray-500">Được tài trợ</p>
          )}
        </div>

        {/* Menu Button */}
        <button className="text-gray-400 hover:text-gray-600 p-1 flex-shrink-0">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>
      </div>

      {/* Caption - Before Thumbnail (Facebook style) */}
      {data.caption && (
        <div className={isMobile ? 'px-3 pb-2' : 'px-4 pb-3'}>
          <p className={`text-gray-800 leading-relaxed whitespace-pre-wrap ${isMobile ? 'text-sm' : 'text-[15px]'}`}>
            {displayCaption}
            {shouldTruncate && (
              <>
                ...{' '}
                <span className="text-gray-600 font-medium cursor-pointer hover:underline">
                  Xem thêm
                </span>
              </>
            )}
          </p>
        </div>
      )}

      {/* Thumbnail - Static Image ONLY (NO VIDEO PLAYER) */}
      <div className="relative bg-gray-900" style={{ aspectRatio: '4/5' }}>
        {data.thumbnailUrl ? (
          <img 
            src={data.thumbnailUrl} 
            alt="Post thumbnail"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-gray-400 text-center">
              <svg className="w-16 h-16 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p className="text-sm">Chưa có hình ảnh</p>
            </div>
          </div>
        )}
      </div>

      {/* CTA Button - Full Width Messenger Style */}
      {data.ctaText && (
        <div className={isMobile ? 'p-3' : 'p-4'}>
          <button className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white rounded-lg font-semibold text-sm flex items-center justify-center gap-2 transition shadow-sm">
            {/* Messenger Icon */}
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
              <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
            </svg>
            {data.ctaText}
          </button>
        </div>
      )}

      {/* Reactions & Stats */}
      <div className={`flex items-center justify-between text-[13px] text-gray-600 border-t border-gray-100 ${isMobile ? 'px-3 py-2.5' : 'px-4 py-3'}`}>
        <div className="flex items-center gap-2">
          {/* Reaction Icons - Facebook SVG Style */}
          <div className="flex -space-x-0.5">
            {/* Like - Blue */}
            <svg className="w-[18px] h-[18px]" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="8" fill="#0866FF"/>
              <path d="M11.5 6.5h-2.25l.5-2.5c.05-.25 0-.5-.25-.65-.15-.1-.35-.15-.5-.1L6.25 5.5c-.1.05-.15.15-.2.25l-1.5 4.5c0 .1-.05.2-.05.3v1c0 .55.45 1 1 1h4.75c.45 0 .85-.3.95-.75l1.25-4c.05-.15.05-.3.05-.45v-.35c0-.55-.45-1-1-1z" fill="white"/>
            </svg>
            
            {/* Love - Red */}
            <svg className="w-[18px] h-[18px]" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="8" fill="#F33E58"/>
              <path d="M10.5 4.5c-.85 0-1.65.5-2 1.25-.35-.75-1.15-1.25-2-1.25-1.25 0-2.25 1-2.25 2.25 0 2.5 4.25 5 4.25 5s4.25-2.5 4.25-5c0-1.25-1-2.25-2.25-2.25z" fill="white"/>
            </svg>
          </div>
          <span className="text-gray-700 hover:underline cursor-pointer">{reactions}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="hover:underline cursor-pointer">{comments} bình luận</span>
          <span className="hover:underline cursor-pointer">{shares} lượt chia sẻ</span>
        </div>
      </div>

      {/* Action Buttons - Static */}
      <div className={`border-t border-gray-200 flex items-center ${isMobile ? 'px-1 py-1' : 'px-2 py-1'}`}>
        {/* Thích */}
        <button className="flex items-center justify-center gap-1.5 py-2 hover:bg-gray-50 rounded transition flex-1">
          <svg className="w-[18px] h-[18px] text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
          </svg>
          <span className="text-[15px] font-medium text-gray-600">Thích</span>
        </button>

        {/* Bình luận */}
        <button className="flex items-center justify-center gap-1.5 py-2 hover:bg-gray-50 rounded transition flex-1">
          <svg className="w-[18px] h-[18px] text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span className="text-[15px] font-medium text-gray-600">Bình luận</span>
        </button>

        {/* Chia sẻ */}
        <button className="flex items-center justify-center gap-1.5 py-2 hover:bg-gray-50 rounded transition flex-1">
          <svg className="w-[18px] h-[18px] text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          <span className="text-[15px] font-medium text-gray-600">Chia sẻ</span>
        </button>
      </div>
    </div>
  );
}
