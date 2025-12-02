/**
 * FacebookFeedMobile.tsx
 * Preview giống Facebook Feed (News Feed) trên Mobile
 * - Card layout với shadow
 * - Avatar + Page name + "Được tài trợ"
 * - Caption trước video
 * - Video/thumbnail
 * - CTA button dạng Messenger
 * - Like, Comment, Share buttons
 */

interface FacebookFeedMobileProps {
  videoUrl?: string;
  thumbnailUrl?: string;
  pageName: string;
  pageAvatar?: string;
  caption: string;
  videoTitle?: string;
  ctaText?: string;
  onVideoRef?: (ref: HTMLVideoElement | null) => void;
}

export function FacebookFeedMobile({
  videoUrl,
  thumbnailUrl,
  pageName,
  pageAvatar,
  caption,
  ctaText,
  onVideoRef
}: FacebookFeedMobileProps) {

  // Truncate caption - show 2 lines then "...Xem thêm"
  const shouldTruncate = caption.length > 100;
  const displayCaption = shouldTruncate ? caption.slice(0, 100) : caption;

  return (
    <div 
      className="bg-white rounded-lg shadow-md overflow-hidden"
      style={{ width: '390px' }}
    >
      {/* Header - Page Info */}
      <div className="p-3 flex items-center gap-2">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white font-bold overflow-hidden flex-shrink-0">
          {pageAvatar ? (
            <img src={pageAvatar} alt={pageName} className="w-full h-full object-cover" />
          ) : (
            pageName.charAt(0)
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1">
            <span className="font-semibold text-gray-900 text-sm truncate">{pageName}</span>
            <svg className="w-4 h-4 text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-xs text-gray-500">Được tài trợ</p>
        </div>
        <button className="text-gray-400 hover:text-gray-600 p-1">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>
      </div>

      {/* Caption - Before Video (Facebook style) */}
      {caption && (
        <div className="px-3 pb-2">
          <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
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

      {/* Video */}
      <div className="relative bg-black" style={{ aspectRatio: '16/9' }}>
        {videoUrl ? (
          <video
            ref={onVideoRef}
            src={videoUrl}
            poster={thumbnailUrl}
            className="w-full h-full object-contain"
            controls
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-white/50 text-center">
              <svg className="w-16 h-16 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm">Chưa tải video</p>
            </div>
          </div>
        )}
      </div>

      {/* CTA Button - Full Width */}
      {ctaText && (
        <div className="p-3">
          <button className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white rounded-lg font-semibold text-sm flex items-center justify-center gap-2 transition shadow-sm">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
              <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
            </svg>
            {ctaText}
          </button>
        </div>
      )}

      {/* Reactions & Stats */}
      <div className="px-3 py-2 flex items-center justify-between text-xs text-gray-600 border-t border-gray-100">
        <div className="flex items-center gap-1">
          <div className="flex -space-x-1">
            <div className="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center border border-white">
              <span className="text-white text-[10px]">👍</span>
            </div>
            <div className="w-4 h-4 rounded-full bg-red-500 flex items-center justify-center border border-white">
              <span className="text-white text-[10px]">❤️</span>
            </div>
          </div>
          <span>17</span>
        </div>
        <div className="flex items-center gap-3">
          <span>4 bình luận</span>
          <span>1 lượt chia sẻ</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="border-t border-gray-200 px-3 py-2 flex items-center justify-around">
        <button className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 rounded-lg transition flex-1 justify-center">
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
          </svg>
          <span className="text-sm font-medium text-gray-700">Thích</span>
        </button>

        <button className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 rounded-lg transition flex-1 justify-center">
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span className="text-sm font-medium text-gray-700">Bình luận</span>
        </button>

        <button className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 rounded-lg transition flex-1 justify-center">
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          <span className="text-sm font-medium text-gray-700">Chia sẻ</span>
        </button>
      </div>
    </div>
  );
}
