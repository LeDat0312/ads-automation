import React, { useState, useRef } from 'react';
import { Tab } from '@headlessui/react';
import MediaUploadCard from '../MediaUploadCard';
import ThumbnailModal from './ThumbnailModal';

interface PostComposerProps {
  onSubmit: (data: PostData) => void;
  isSaving: boolean;
}

export interface PostData {
  mediaUrl?: string;
  mediaFile?: File;
  videoTitle?: string;
  caption: string;
  language: string;
  postType: 'feed' | 'reel' | 'story';
  ctaType: string;
  ctaUrl?: string;
  scheduleMode: 'now' | 'scheduled' | 'random';
  scheduledTime?: string;
  randomFrom?: string;
  randomTo?: string;
  thumbnailFile?: File;
}

const CTA_OPTIONS = [
  { value: 'none', label: 'Không dùng CTA' },
  { value: 'message', label: 'Nhắn tin ngay' },
  { value: 'call', label: 'Gọi ngay' },
  { value: 'learn_more', label: 'Xem thêm' },
  { value: 'shop_now', label: 'Mua ngay' },
];

const LANGUAGES = [
  { value: 'la', label: 'Lào' },
  { value: 'vi', label: 'Việt' },
  { value: 'th', label: 'Thái' },
];

const PostComposer: React.FC<PostComposerProps> = ({ onSubmit, isSaving }) => {
  // Media state
  const [mediaUrl, setMediaUrl] = useState<string>();
  const [mediaFile, setMediaFile] = useState<File>();
  const [linkInput, setLinkInput] = useState('');
  const [isFetchingLink, setIsFetchingLink] = useState(false);

  // Content state
  const [videoTitle, setVideoTitle] = useState('');
  const [caption, setCaption] = useState('');
  const [language, setLanguage] = useState('la');
  const [useSpin, setUseSpin] = useState(false);

  // Facebook settings
  const [postType, setPostType] = useState<'feed' | 'reel' | 'story'>('feed');
  const [ctaType, setCtaType] = useState('none');
  const [ctaUrl, setCtaUrl] = useState('');

  // Schedule state
  const [scheduleMode, setScheduleMode] = useState<'now' | 'scheduled' | 'random'>('now');
  const [scheduledTime, setScheduledTime] = useState('');
  const [randomFrom, setRandomFrom] = useState('');
  const [randomTo, setRandomTo] = useState('');

  // Thumbnail state
  const [thumbnailFile, setThumbnailFile] = useState<File>();
  const [thumbnailPreview, setThumbnailPreview] = useState<string>();
  const [thumbnailModalOpen, setThumbnailModalOpen] = useState(false);

  const handleMediaUpload = async (file: File): Promise<string> => {
    setMediaFile(file);
    const url = URL.createObjectURL(file);
    setMediaUrl(url);
    return url;
  };

  const handleMediaRemove = () => {
    setMediaFile(undefined);
    setMediaUrl(undefined);
    setThumbnailFile(undefined);
    setThumbnailPreview(undefined);
  };

  const handleFetchLink = async () => {
    if (!linkInput.trim()) return;

    setIsFetchingLink(true);
    try {
      // TODO: Implement actual link fetching
      // For now, just use the link as video URL
      setMediaUrl(linkInput);
      setLinkInput('');
    } catch (error) {
      console.error('Error fetching link:', error);
      alert('Không thể lấy media từ link này');
    } finally {
      setIsFetchingLink(false);
    }
  };

  const handleThumbnailApply = (thumbnail: File | string) => {
    if (thumbnail instanceof File) {
      setThumbnailFile(thumbnail);
      setThumbnailPreview(URL.createObjectURL(thumbnail));
    }
  };

  const handleSubmit = (action: 'draft' | 'publish') => {
    // Validation
    if (!mediaUrl && !mediaFile) {
      alert('Vui lòng tải media lên');
      return;
    }

    if (!caption.trim()) {
      alert('Vui lòng nhập nội dung bài viết');
      return;
    }

    if (scheduleMode === 'scheduled' && !scheduledTime) {
      alert('Vui lòng chọn thời gian đăng bài');
      return;
    }

    if (scheduleMode === 'random' && (!randomFrom || !randomTo)) {
      alert('Vui lòng chọn khoảng thời gian ngẫu nhiên');
      return;
    }

    if (ctaType !== 'none' && !ctaUrl) {
      alert('Vui lòng nhập link đích cho CTA');
      return;
    }

    const data: PostData = {
      mediaUrl,
      mediaFile,
      videoTitle: postType === 'reel' ? videoTitle : undefined,
      caption,
      language,
      postType,
      ctaType,
      ctaUrl: ctaType !== 'none' ? ctaUrl : undefined,
      scheduleMode,
      scheduledTime: scheduleMode === 'scheduled' ? scheduledTime : undefined,
      randomFrom: scheduleMode === 'random' ? randomFrom : undefined,
      randomTo: scheduleMode === 'random' ? randomTo : undefined,
      thumbnailFile,
    };

    onSubmit(data);
  };

  const isVideo = mediaFile?.type.startsWith('video/') || mediaUrl?.match(/\.(mp4|mov|avi|webm)$/i);

  return (
    <div className="bg-white rounded-xl border border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">Đăng bài</h3>
        <p className="text-xs text-gray-500 mt-1">Tạo nội dung và lên lịch đăng</p>
      </div>

      {/* Content - Scrollable */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* 1. Media Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Media</label>
          
          <Tab.Group>
            <Tab.List className="flex space-x-1 rounded-lg bg-gray-100 p-1 mb-3">
              <Tab
                className={({ selected }) =>
                  `w-full rounded-md py-2 text-sm font-medium transition-all
                  ${selected ? 'bg-white text-gray-900 shadow' : 'text-gray-600 hover:text-gray-900'}`
                }
              >
                Tải từ máy
              </Tab>
              <Tab
                className={({ selected }) =>
                  `w-full rounded-md py-2 text-sm font-medium transition-all
                  ${selected ? 'bg-white text-gray-900 shadow' : 'text-gray-600 hover:text-gray-900'}`
                }
              >
                Dán link
              </Tab>
            </Tab.List>

            <Tab.Panels>
              <Tab.Panel>
                <MediaUploadCard
                  mediaUrl={mediaUrl}
                  onUpload={handleMediaUpload}
                  onRemove={handleMediaRemove}
                  accept="image/*,video/mp4,video/webm"
                  maxSizeMB={100}
                />
              </Tab.Panel>

              <Tab.Panel>
                <div className="space-y-2">
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Dán link TikTok, Facebook..."
                    value={linkInput}
                    onChange={(e) => setLinkInput(e.target.value)}
                  />
                  <button
                    onClick={handleFetchLink}
                    disabled={!linkInput.trim() || isFetchingLink}
                    className="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 text-sm font-medium"
                  >
                    {isFetchingLink ? 'Đang lấy media...' : 'Lấy media'}
                  </button>
                </div>
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>

          {/* Thumbnail selector for video */}
          {isVideo && mediaUrl && (
            <div className="mt-3">
              <button
                onClick={() => setThumbnailModalOpen(true)}
                className="text-sm text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {thumbnailPreview ? 'Thay đổi thumbnail' : 'Chỉnh thumbnail'}
              </button>
              {thumbnailPreview && (
                <img src={thumbnailPreview} alt="Thumbnail" className="mt-2 w-32 h-32 object-cover rounded-lg border border-gray-200" />
              )}
            </div>
          )}
        </div>

        {/* 2. Content Section */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Nội dung</h4>

          {/* Video Title (only for Reel) */}
          {postType === 'reel' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tiêu đề video</label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Nhập tiêu đề video..."
                value={videoTitle}
                onChange={(e) => setVideoTitle(e.target.value)}
              />
            </div>
          )}

          {/* Caption */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nội dung bài viết</label>
            <textarea
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
              rows={5}
              placeholder="Nhập nội dung bài viết..."
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
            />
          </div>

          {/* Language */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ngôn ngữ</label>
            <select
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>

          {/* Spin Content (TODO) */}
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={useSpin}
              onChange={(e) => setUseSpin(e.target.checked)}
              className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            Dùng Spin nội dung (TODO)
          </label>
        </div>

        {/* 3. Facebook Settings */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Cài đặt Facebook</h4>

          {/* Post Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Loại bài</label>
            <select
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={postType}
              onChange={(e) => setPostType(e.target.value as any)}
            >
              <option value="feed">Feed</option>
              <option value="reel">Reel</option>
              <option value="story">Story</option>
            </select>
          </div>

          {/* CTA */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">CTA (Call to Action)</label>
            <select
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={ctaType}
              onChange={(e) => setCtaType(e.target.value)}
            >
              {CTA_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* CTA URL */}
          {ctaType !== 'none' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Link đích</label>
              <input
                type="url"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="https://..."
                value={ctaUrl}
                onChange={(e) => setCtaUrl(e.target.value)}
              />
            </div>
          )}
        </div>

        {/* 4. Schedule Settings */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Lịch đăng bài</h4>

          {/* Schedule Mode */}
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="scheduleMode"
                value="now"
                checked={scheduleMode === 'now'}
                onChange={(e) => setScheduleMode(e.target.value as any)}
                className="w-4 h-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-700">Đăng ngay</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="scheduleMode"
                value="scheduled"
                checked={scheduleMode === 'scheduled'}
                onChange={(e) => setScheduleMode(e.target.value as any)}
                className="w-4 h-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-700">Hẹn giờ</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="scheduleMode"
                value="random"
                checked={scheduleMode === 'random'}
                onChange={(e) => setScheduleMode(e.target.value as any)}
                className="w-4 h-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-700">Đăng ngẫu nhiên trong khoảng</span>
            </label>
          </div>

          {/* Scheduled Time */}
          {scheduleMode === 'scheduled' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Thời gian đăng</label>
              <input
                type="datetime-local"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
              />
            </div>
          )}

          {/* Random Range */}
          {scheduleMode === 'random' && (
            <div className="space-y-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Từ</label>
                <input
                  type="datetime-local"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  value={randomFrom}
                  onChange={(e) => setRandomFrom(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Đến</label>
                <input
                  type="datetime-local"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  value={randomTo}
                  onChange={(e) => setRandomTo(e.target.value)}
                />
              </div>
              <p className="text-xs text-gray-500">
                💡 Hệ thống sẽ random một thời điểm bất kỳ trong khoảng này cho mỗi kênh
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Footer - Action Buttons */}
      <div className="p-4 border-t border-gray-200 bg-gray-50 space-y-2">
        <button
          onClick={() => handleSubmit('publish')}
          disabled={isSaving}
          className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 font-medium"
        >
          {isSaving ? 'Đang xử lý...' : 'Lưu & xuất bản'}
        </button>
        <button
          onClick={() => handleSubmit('draft')}
          disabled={isSaving}
          className="w-full py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 text-sm font-medium"
        >
          Lưu nháp
        </button>
      </div>

      {/* Thumbnail Modal */}
      <ThumbnailModal
        open={thumbnailModalOpen}
        onClose={() => setThumbnailModalOpen(false)}
        videoUrl={mediaUrl}
        onApply={handleThumbnailApply}
      />
    </div>
  );
};

export default PostComposer;
