import React from 'react';
import type { PostData } from './PostComposer';

interface PostPreviewProps {
  postData: PostData;
  selectedChannels: Array<{ id: string; page_name: string; avatar_url?: string }>;
}

const PostPreview: React.FC<PostPreviewProps> = ({ postData, selectedChannels }) => {
  const firstChannel = selectedChannels[0];
  const isVideo = postData.mediaFile?.type.startsWith('video/') || postData.mediaUrl?.match(/\.(mp4|mov|avi|webm)$/i);

  return (
    <div className="bg-white rounded-xl border border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">Xem trước</h3>
        <p className="text-xs text-gray-500 mt-1">Bài viết sẽ hiển thị như thế này</p>
      </div>

      {/* Preview Content - Scrollable */}
      <div className="flex-1 overflow-y-auto p-4">
        {!postData.mediaUrl && !postData.mediaFile ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">👁️</div>
            <p className="text-gray-500">Thêm media và nội dung để xem trước</p>
          </div>
        ) : (
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
            {/* Facebook Post Header */}
            <div className="p-3 flex items-center gap-3">
              <img
                src={firstChannel?.avatar_url || 'https://via.placeholder.com/40'}
                alt={firstChannel?.page_name || 'Page'}
                className="w-10 h-10 rounded-full"
              />
              <div className="flex-1">
                <p className="font-semibold text-sm text-gray-900">
                  {firstChannel?.page_name || 'Tên Fanpage'}
                </p>
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <span>Vừa xong</span>
                  <span>·</span>
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM4.332 8.027a6.012 6.012 0 011.912-2.706C6.512 5.73 6.974 6 7.5 6A1.5 1.5 0 019 7.5V8a2 2 0 004 0 2 2 0 011.523-1.943A5.977 5.977 0 0116 10c0 .34-.028.675-.083 1H15a2 2 0 00-2 2v2.197A5.973 5.973 0 0110 16v-2a2 2 0 00-2-2 2 2 0 01-2-2 2 2 0 00-1.668-1.973z" />
                  </svg>
                </div>
              </div>
              <button className="p-1 text-gray-400 hover:bg-gray-100 rounded">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                </svg>
              </button>
            </div>

            {/* Caption */}
            {postData.caption && (
              <div className="px-3 pb-3">
                <p className="text-sm text-gray-900 whitespace-pre-wrap">{postData.caption}</p>
              </div>
            )}

            {/* Media */}
            {(postData.mediaUrl || postData.mediaFile) && (
              <div className="relative bg-black">
                {isVideo ? (
                  <video
                    src={postData.mediaUrl}
                    controls
                    className="w-full"
                    style={{ maxHeight: '400px' }}
                  />
                ) : (
                  <img
                    src={postData.mediaUrl}
                    alt="Post media"
                    className="w-full"
                    style={{ maxHeight: '400px', objectFit: 'contain' }}
                  />
                )}
                
                {/* Post Type Badge */}
                {postData.postType !== 'feed' && (
                  <div className="absolute top-2 left-2 px-2 py-1 bg-black/70 text-white text-xs font-medium rounded">
                    {postData.postType === 'reel' ? '🎬 Reel' : '📖 Story'}
                  </div>
                )}
              </div>
            )}

            {/* CTA Button */}
            {postData.ctaType !== 'none' && (
              <div className="p-3 border-t border-gray-200">
                <button className="w-full py-2 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 transition-colors">
                  {postData.ctaType === 'message' && '💬 Nhắn tin ngay'}
                  {postData.ctaType === 'call' && '📞 Gọi ngay'}
                  {postData.ctaType === 'learn_more' && '👉 Xem thêm'}
                  {postData.ctaType === 'shop_now' && '🛒 Mua ngay'}
                </button>
              </div>
            )}

            {/* Engagement Bar */}
            <div className="p-3 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                <div className="flex items-center gap-1">
                  <span className="flex items-center">
                    <span className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center text-white text-[10px]">👍</span>
                  </span>
                  <span>0</span>
                </div>
                <div className="flex items-center gap-3">
                  <span>0 bình luận</span>
                  <span>0 chia sẻ</span>
                </div>
              </div>
              <div className="flex items-center justify-around border-t border-gray-200 pt-2">
                <button className="flex items-center gap-1 text-gray-600 hover:bg-gray-100 px-3 py-1 rounded">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                  </svg>
                  <span className="text-sm">Thích</span>
                </button>
                <button className="flex items-center gap-1 text-gray-600 hover:bg-gray-100 px-3 py-1 rounded">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span className="text-sm">Bình luận</span>
                </button>
                <button className="flex items-center gap-1 text-gray-600 hover:bg-gray-100 px-3 py-1 rounded">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                  </svg>
                  <span className="text-sm">Chia sẻ</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Schedule Info */}
        {postData.scheduleMode !== 'now' && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-900">Lịch đăng bài</p>
                {postData.scheduleMode === 'scheduled' && postData.scheduledTime && (
                  <p className="text-xs text-blue-700 mt-1">
                    Đăng vào: {new Date(postData.scheduledTime).toLocaleString('vi-VN')}
                  </p>
                )}
                {postData.scheduleMode === 'random' && postData.randomFrom && postData.randomTo && (
                  <p className="text-xs text-blue-700 mt-1">
                    Random từ {new Date(postData.randomFrom).toLocaleString('vi-VN')} đến{' '}
                    {new Date(postData.randomTo).toLocaleString('vi-VN')}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Selected Channels Info */}
        {selectedChannels.length > 0 && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-green-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <p className="text-sm font-medium text-green-900">
                  Đăng lên {selectedChannels.length} kênh
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {selectedChannels.slice(0, 3).map((channel) => (
                    <div key={channel.id} className="flex items-center gap-1 bg-white px-2 py-1 rounded border border-green-200">
                      <img
                        src={channel.avatar_url || 'https://via.placeholder.com/20'}
                        alt={channel.page_name}
                        className="w-4 h-4 rounded-full"
                      />
                      <span className="text-xs text-gray-700">{channel.page_name}</span>
                    </div>
                  ))}
                  {selectedChannels.length > 3 && (
                    <div className="flex items-center px-2 py-1 bg-white rounded border border-green-200">
                      <span className="text-xs text-gray-600">+{selectedChannels.length - 3} kênh khác</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PostPreview;
