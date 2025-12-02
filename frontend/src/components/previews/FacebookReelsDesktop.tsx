/**
 * FacebookReelsDesktop.tsx
 * Preview giống Facebook Reels trên Desktop/PC
 * - Khung video trung tâm
 * - Sidebar bên phải: Like, Comment, Share
 * - Info bar dưới: Avatar, Page, Caption, CTA
 */

import React from 'react';

interface FacebookReelsDesktopProps {
  videoUrl?: string;
  thumbnailUrl?: string;
  pageName: string;
  pageAvatar?: string;
  caption: string;
  ctaText?: string;
  onVideoRef?: (ref: HTMLVideoElement | null) => void;
}

export function FacebookReelsDesktop({
  videoUrl,
  thumbnailUrl,
  pageName,
  pageAvatar,
  caption,
  ctaText,
  onVideoRef
}: FacebookReelsDesktopProps) {

  const truncatedCaption = caption.length > 120 ? caption.slice(0, 120) + '... Xem thêm' : caption;

  return (
    <div className="flex items-start gap-4 bg-black/95 rounded-xl overflow-hidden p-4" style={{ width: '480px' }}>
      {/* Main Video Area */}
      <div className="flex-1">
        <div 
          className="relative bg-black rounded-lg overflow-hidden"
          style={{ aspectRatio: '9/16', maxHeight: '600px' }}
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
        </div>

        {/* Bottom Info Bar */}
        <div className="mt-3">
          {/* Page Info */}
          <div className="flex items-center gap-2 mb-2">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white font-bold overflow-hidden">
              {pageAvatar ? (
                <img src={pageAvatar} alt={pageName} className="w-full h-full object-cover" />
              ) : (
                pageName.charAt(0)
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-1">
                <span className="font-semibold text-white text-sm">{pageName}</span>
                <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-xs text-gray-400">Được tài trợ</p>
            </div>
            <button className="px-4 py-1.5 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-md text-white text-sm font-medium transition">
              Theo dõi
            </button>
          </div>

          {/* Caption */}
          {caption && (
            <p className="text-white text-sm leading-relaxed mb-3">
              {truncatedCaption}
            </p>
          )}

          {/* CTA Button */}
          {ctaText && (
            <button className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-sm flex items-center justify-center gap-2 transition">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
              </svg>
              {ctaText}
            </button>
          )}
        </div>
      </div>

      {/* Right Sidebar - Actions */}
      <div className="flex flex-col gap-4 pt-4">
        {/* Like */}
        <div className="flex flex-col items-center">
          <button className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center hover:bg-white/20 transition">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
          <span className="text-white text-xs font-medium mt-1">15.6K</span>
        </div>

        {/* Comment */}
        <div className="flex flex-col items-center">
          <button className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center hover:bg-white/20 transition">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </button>
          <span className="text-white text-xs font-medium mt-1">937</span>
        </div>

        {/* Share */}
        <div className="flex flex-col items-center">
          <button className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center hover:bg-white/20 transition">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
          </button>
          <span className="text-white text-xs font-medium mt-1">119</span>
        </div>
      </div>
    </div>
  );
}
