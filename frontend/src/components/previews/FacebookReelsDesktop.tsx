/**
 * FacebookReelsDesktop.tsx
 * Preview giống Facebook Reels trên Desktop/PC
 * - Khung video trung tâm
 * - Sidebar bên phải: Like, Comment, Share
 * - Info bar dưới: Avatar, Page, Caption, CTA
 */

interface FacebookReelsDesktopProps {
  videoUrl?: string;
  thumbnailUrl?: string;
  pageName: string;
  pageAvatar?: string;
  caption: string;
  onVideoRef?: (ref: HTMLVideoElement | null) => void;
}

export function FacebookReelsDesktop({
  videoUrl,
  thumbnailUrl,
  pageName,
  pageAvatar,
  caption,
  onVideoRef
}: FacebookReelsDesktopProps) {

  const truncatedCaption = caption.length > 120 ? caption.slice(0, 120) + '... Xem thêm' : caption;

  return (
    <div className="flex items-start gap-3 bg-black rounded-xl overflow-hidden" style={{ width: '520px', minHeight: '600px' }}>
      {/* Main Video Area */}
      <div className="flex-1">
        <div 
          className="relative bg-black rounded-lg overflow-hidden"
          style={{ aspectRatio: '9/16', height: '580px' }}
        >
          {videoUrl ? (
            <video
              ref={onVideoRef}
              src={videoUrl}
              poster={thumbnailUrl}
              className="w-full h-full object-contain"
              controls
              loop
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

          {/* Caption Overlay (giống Facebook Reels Desktop) */}
          {caption && (
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/70 to-transparent p-4 pt-16">
              <div className="flex items-start gap-3">
                {/* Avatar */}
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white font-bold overflow-hidden flex-shrink-0">
                  {pageAvatar ? (
                    <img src={pageAvatar} alt={pageName} className="w-full h-full object-cover" />
                  ) : (
                    pageName.charAt(0)
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  {/* Page Name + Verified */}
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="font-semibold text-white text-[15px]">{pageName}</span>
                    <svg className="w-[18px] h-[18px] text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <button className="ml-auto px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded-md text-white text-xs font-semibold transition">
                      Theo dõi
                    </button>
                  </div>

                  {/* Sponsored Label */}
                  <p className="text-[13px] text-white/70 mb-2">Được tài trợ</p>

                  {/* Caption */}
                  <p className="text-white text-[14px] leading-[1.4]">
                    {truncatedCaption}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Sidebar - Actions (giống Facebook) */}
      <div className="flex flex-col gap-6 pt-6 pr-3">
        {/* Like */}
        <div className="flex flex-col items-center">
          <button className="w-11 h-11 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center hover:bg-white/25 transition">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
          <span className="text-white/90 text-xs font-medium mt-1.5">15.6K</span>
        </div>

        {/* Comment */}
        <div className="flex flex-col items-center">
          <button className="w-11 h-11 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center hover:bg-white/25 transition">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </button>
          <span className="text-white/90 text-xs font-medium mt-1.5">937</span>
        </div>

        {/* Share */}
        <div className="flex flex-col items-center">
          <button className="w-11 h-11 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center hover:bg-white/25 transition">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
          </button>
          <span className="text-white/90 text-xs font-medium mt-1.5">119</span>
        </div>

        {/* More */}
        <button className="w-11 h-11 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center hover:bg-white/25 transition">
          <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>
      </div>
    </div>
  );
}
