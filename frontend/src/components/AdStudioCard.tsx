/**
 * AdStudioCard.tsx - Thu thập link & Lên lịch đăng bài
 * Layout 2 cột theo phong cách Publer:
 * - Cột trái (70%): Form nhập liệu
 * - Cột phải (30%): Video Preview sticky
 * 
 * @author AI Assistant
 * @version 3.0 - Facebook-like Preview System
 */
import React, { useState, useRef, useCallback, useEffect } from 'react';
import { toast } from 'react-toastify';
import { fetchTiktokAsset, fetchFacebookAsset } from '../api/adStudio';
import { fetchChannels, fetchChannelGroups } from '../api/settings';
import type { Channel, ChannelGroup } from '../api/settings';
import { PreviewPanel } from './preview/PreviewPanel';
import type { PreviewData } from '../types/preview';

// ==================== TYPES ====================
interface VideoData {
  id: string;
  platform: 'tiktok' | 'facebook';
  videoUrl: string;
  thumbnailUrl: string;
  caption: string;
  duration?: number;
  hashtags?: string[];
}

interface AutoComment {
  id: string;
  text: string;
  mediaUrl?: string;
}

interface FormPayload {
  sourceUrl: string;
  platform: 'tiktok' | 'facebook' | 'auto';
  video: { id?: string; thumbnailUrl?: string; localUpload?: File | null };
  caption: string;
  title?: string;
  cta: string;
  postType: 'feed' | 'reel' | 'story';
  channels: string[];
  schedule: { mode: 'now' | 'at' | 'auto'; time?: string };
  autoCommentsEnabled: boolean;
  autoComments: { text: string; mediaUrl?: string }[];
}

type FetchStatus = 'idle' | 'loading' | 'success' | 'error';
type VideoSource = 'original' | 'upload';

// ==================== CONSTANTS ====================
const CTA_OPTIONS = [
  { value: '', label: 'Không dùng CTA' },
  { value: 'MESSAGE', label: 'Nhắn tin ngay' },
  { value: 'LEARN_MORE', label: 'Tìm hiểu thêm' },
  { value: 'CALL_NOW', label: 'Gọi ngay' },
  { value: 'BOOK_NOW', label: 'Đặt lịch hẹn' },
  { value: 'SHOP_NOW', label: 'Mua ngay' },
  { value: 'SIGN_UP', label: 'Đăng ký ngay' },
];

const POST_TYPES = [
  { value: 'feed', label: 'Feed' },
  { value: 'reel', label: 'Reel' },
  { value: 'story', label: 'Story' },
];

// ==================== HELPER HOOKS ====================

/**
 * Hook để fetch video từ link TikTok/Facebook
 */
function useFetchVideo() {
  const [status, setStatus] = useState<FetchStatus>('idle');
  const [error, setError] = useState<string>('');
  const [video, setVideo] = useState<VideoData | null>(null);

  const fetchVideo = useCallback(async (url: string, platform: 'tiktok' | 'facebook' | 'auto') => {
    if (!url.trim()) {
      setError('Vui lòng nhập link video');
      return null;
    }

    setStatus('loading');
    setError('');

    try {
      // Auto detect platform
      let detectedPlatform = platform;
      if (platform === 'auto') {
        if (url.includes('tiktok.com')) detectedPlatform = 'tiktok';
        else if (url.includes('facebook.com') || url.includes('fb.watch')) detectedPlatform = 'facebook';
        else {
          setError('Không nhận diện được nền tảng. Vui lòng chọn thủ công.');
          setStatus('error');
          return null;
        }
      }

      const result = detectedPlatform === 'tiktok'
        ? await fetchTiktokAsset(url)
        : await fetchFacebookAsset(url);

      const videoData: VideoData = {
        id: result.id,
        platform: result.platform as 'tiktok' | 'facebook',
        videoUrl: result.videoUrl,
        thumbnailUrl: result.thumbnailUrl,
        caption: result.captionOriginal || '',
        duration: result.duration,
        hashtags: result.hashtags,
      };

      setVideo(videoData);
      setStatus('success');
      return videoData;
    } catch (err: any) {
      const message = err.detail || err.message || 'Không lấy được video, vui lòng kiểm tra link hoặc thử lại sau';
      setError(message);
      setStatus('error');
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setStatus('idle');
    setError('');
    setVideo(null);
  }, []);

  return { status, error, video, fetchVideo, reset };
}

/**
 * Hook để quản lý danh sách kênh
 */
function useChannels() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [groups, setGroups] = useState<ChannelGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [channelsData, groupsData] = await Promise.all([
        fetchChannels('facebook', undefined, true),
        fetchChannelGroups(),
      ]);
      setChannels(channelsData);
      setGroups(groupsData);
    } catch (err: any) {
      setError('Không thể tải danh sách kênh');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return { channels, groups, loading, error, reload: load };
}

// ==================== SUB COMPONENTS ====================

/** Section 1: Dán link video */
function LinkSection({
  url, setUrl, platform, setPlatform, status, error, onFetch, onReset
}: {
  url: string;
  setUrl: (v: string) => void;
  platform: 'tiktok' | 'facebook' | 'auto';
  setPlatform: (v: 'tiktok' | 'facebook' | 'auto') => void;
  status: FetchStatus;
  error: string;
  onFetch: () => void;
  onReset: () => void;
}) {
  const isLoading = status === 'loading';
  const hasVideo = status === 'success';

  return (
    <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 bg-violet-100 text-violet-600 rounded-full flex items-center justify-center text-sm font-bold">1</div>
        <h3 className="font-semibold text-gray-900">Dán link video</h3>
        {hasVideo && <span className="ml-auto px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium">✓ Đã tải</span>}
      </div>

      <div className="flex gap-2">
        {/* URL Input */}
        <div className="flex-1 relative">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <input
            type="text"
            className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition disabled:bg-gray-50"
            placeholder="Dán link TikTok / Facebook / Reels vào đây..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading || hasVideo}
            onKeyDown={(e) => e.key === 'Enter' && !hasVideo && onFetch()}
          />
        </div>

        {/* Platform Select */}
        <select
          className="px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-violet-500 text-sm bg-white disabled:bg-gray-50"
          value={platform}
          onChange={(e) => setPlatform(e.target.value as any)}
          disabled={isLoading || hasVideo}
        >
          <option value="auto">Tự động</option>
          <option value="tiktok">TikTok</option>
          <option value="facebook">Facebook</option>
        </select>

        {/* Action Button */}
        {!hasVideo ? (
          <button
            onClick={onFetch}
            disabled={isLoading || !url.trim()}
            className="px-5 py-3 bg-violet-600 text-white rounded-xl hover:bg-violet-700 transition disabled:opacity-50 font-medium whitespace-nowrap flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Đang tải...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Lấy video
              </>
            )}
          </button>
        ) : (
          <button
            onClick={onReset}
            className="px-5 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition font-medium"
          >
            Đổi link
          </button>
        )}
      </div>

      {/* Status Messages */}
      {status === 'idle' && (
        <p className="mt-2 text-sm text-gray-500">Ví dụ: https://www.tiktok.com/@user/video/123...</p>
      )}
      {status === 'error' && error && (
        <div className="mt-2 flex items-center gap-2 text-red-600 text-sm">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </div>
      )}
    </div>
  );
}

/** Section 2: Nội dung & Video */
function ContentSection({
  caption, setCaption, videoSource, setVideoSource, uploadedFile, setUploadedFile, onAIRewrite
}: {
  caption: string;
  setCaption: (v: string) => void;
  videoSource: VideoSource;
  setVideoSource: (v: VideoSource) => void;
  uploadedFile: File | null;
  setUploadedFile: (f: File | null) => void;
  onAIRewrite?: () => void;
}) {
  const [showSpinModal, setShowSpinModal] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const captionRef = useRef<HTMLTextAreaElement>(null);

  // Auto-expand textarea
  useEffect(() => {
    const textarea = captionRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.max(300, textarea.scrollHeight);
      textarea.style.height = `${newHeight}px`;
    }
  }, [caption]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('video/')) {
      toast.error('Chỉ chấp nhận file video (MP4, MOV, WebM)');
      return;
    }
    
    if (file.size > 100 * 1024 * 1024) {
      toast.error('File quá lớn (tối đa 100MB)');
      return;
    }
    
    setUploadedFile(file);
    toast.success(`Đã tải lên: ${file.name}`);
  };

  const insertSpinAtCursor = (snippet: string) => {
    const textarea = captionRef.current;
    if (!textarea) {
      setCaption(caption + ' ' + snippet);
      return;
    }

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newCaption = caption.substring(0, start) + snippet + caption.substring(end);
    setCaption(newCaption);
    
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + snippet.length, start + snippet.length);
    }, 0);
  };

  return (
    <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 bg-violet-100 text-violet-600 rounded-full flex items-center justify-center text-sm font-bold">2</div>
        <h3 className="font-semibold text-gray-900">Nội dung & Video</h3>
      </div>

      {/* Caption Textarea */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Nội dung sẽ đăng</label>
        <textarea
          ref={captionRef}
          className="w-full border border-gray-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 resize-none overflow-hidden transition"
          style={{ minHeight: '300px' }}
          placeholder="Nhập nội dung bài đăng..."
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
        />
        <div className="flex items-center justify-between mt-2">
          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Spin Content Modal */}
            <button
              onClick={() => setShowSpinModal(true)}
              className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Spin nội dung
            </button>

            {/* AI Rewrite */}
            <button
              onClick={onAIRewrite}
              className="px-3 py-1.5 text-sm bg-gradient-to-r from-violet-500 to-purple-500 text-white rounded-lg hover:from-violet-600 hover:to-purple-600 transition flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              AI gợi ý
            </button>
          </div>

          {/* Character Count */}
          <span className="text-xs text-gray-500">
            <span className={caption.length > 2200 ? 'text-red-500 font-semibold' : ''}>{caption.length}</span> / 2200 ký tự
          </span>
        </div>
      </div>

      {/* Video Source Options */}
      <div className="border-t border-gray-100 pt-4">
        <label className="block text-sm font-medium text-gray-700 mb-3">Nguồn video</label>
        <div className="space-y-2">
          <label className={`flex items-start gap-3 p-3 border rounded-xl cursor-pointer transition ${videoSource === 'original' ? 'border-violet-500 bg-violet-50' : 'border-gray-200 hover:border-gray-300'}`}>
            <input
              type="radio"
              name="videoSource"
              checked={videoSource === 'original'}
              onChange={() => setVideoSource('original')}
              className="mt-0.5 w-4 h-4 text-violet-600"
            />
            <div>
              <p className="font-medium text-gray-900">Dùng video gốc & chỉnh sửa nội dung</p>
              <p className="text-sm text-gray-500">Video sẽ là video từ link gốc. Bạn có thể chỉnh sửa caption.</p>
            </div>
          </label>

          <label className={`flex items-start gap-3 p-3 border rounded-xl cursor-pointer transition ${videoSource === 'upload' ? 'border-violet-500 bg-violet-50' : 'border-gray-200 hover:border-gray-300'}`}>
            <input
              type="radio"
              name="videoSource"
              checked={videoSource === 'upload'}
              onChange={() => setVideoSource('upload')}
              className="mt-0.5 w-4 h-4 text-violet-600"
            />
            <div className="flex-1">
              <p className="font-medium text-gray-900">Dùng nội dung gốc, tự tải lên video của tôi</p>
              <p className="text-sm text-gray-500">Giữ caption gốc nhưng thay video bằng file của bạn.</p>
            </div>
          </label>
        </div>

        {/* Upload Zone with Drag & Drop */}
        {videoSource === 'upload' && (
          <div className="mt-3">
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              className="hidden"
              onChange={(e) => setUploadedFile(e.target.files?.[0] || null)}
            />
            {!uploadedFile ? (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`w-full p-6 border-2 border-dashed rounded-xl transition text-center cursor-pointer ${
                  isDragging
                    ? 'border-violet-500 bg-violet-50'
                    : 'border-gray-300 hover:border-violet-400'
                }`}
              >
                <svg className="w-8 h-8 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-sm text-gray-600">Nhấn để chọn video hoặc kéo thả vào đây</p>
                <p className="text-xs text-gray-400 mt-1">MP4, MOV, WebM (tối đa 100MB)</p>
              </div>
            ) : (
              <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-xl">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-green-800 truncate">{uploadedFile.name}</p>
                  <p className="text-xs text-green-600">{(uploadedFile.size / 1024 / 1024).toFixed(1)} MB</p>
                </div>
                <button onClick={() => setUploadedFile(null)} className="text-green-600 hover:text-green-800">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Spin Content Modal */}
      {showSpinModal && (
        <SpinContentModal
          onClose={() => setShowSpinModal(false)}
          onInsert={insertSpinAtCursor}
        />
      )}
    </div>
  );
}

/** Section 3: Cấu hình đăng bài */
function SettingsSection({
  channels, groups, channelsLoading, selectedChannelIds, setSelectedChannelIds,
  postType, setPostType, cta, setCta, videoTitle, setVideoTitle,
  scheduleMode, setScheduleMode, scheduleTime, setScheduleTime
}: {
  channels: Channel[];
  groups: ChannelGroup[];
  channelsLoading: boolean;
  selectedChannelIds: string[];
  setSelectedChannelIds: (ids: string[]) => void;
  postType: 'feed' | 'reel' | 'story';
  setPostType: (v: 'feed' | 'reel' | 'story') => void;
  cta: string;
  setCta: (v: string) => void;
  videoTitle: string;
  setVideoTitle: (v: string) => void;
  scheduleMode: 'now' | 'at' | 'auto';
  setScheduleMode: (v: 'now' | 'at' | 'auto') => void;
  scheduleTime: string;
  setScheduleTime: (v: string) => void;
}) {
  const [showChannelDrawer, setShowChannelDrawer] = useState(false);
  const [channelSearch, setChannelSearch] = useState('');
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);

  const filteredChannels = channels.filter(c => {
    const matchesSearch = c.page_name.toLowerCase().includes(channelSearch.toLowerCase());
    const matchesGroup = !selectedGroupId || (c as any).channel_group_id === selectedGroupId;
    return matchesSearch && matchesGroup;
  });

  const toggleChannel = (id: string) => {
    setSelectedChannelIds(
      selectedChannelIds.includes(id)
        ? selectedChannelIds.filter(x => x !== id)
        : [...selectedChannelIds, id]
    );
  };

  const selectAll = () => setSelectedChannelIds(filteredChannels.map(c => c.id));
  const deselectAll = () => setSelectedChannelIds([]);

  return (
    <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 bg-violet-100 text-violet-600 rounded-full flex items-center justify-center text-sm font-bold">3</div>
        <h3 className="font-semibold text-gray-900">Cấu hình đăng bài</h3>
      </div>

      {/* 3.1 Chọn kênh đăng */}
      <div className="mb-5">
        <label className="block text-sm font-medium text-gray-700 mb-2">Chọn kênh đăng</label>
        <button
          onClick={() => setShowChannelDrawer(true)}
          className="w-full flex items-center justify-between px-4 py-3 border border-gray-200 rounded-xl hover:border-violet-300 transition"
        >
          <span className="text-gray-700">
            {selectedChannelIds.length > 0 ? `Đã chọn ${selectedChannelIds.length} kênh` : 'Chọn kênh...'}
          </span>
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Selected Channels Tags */}
        {selectedChannelIds.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {selectedChannelIds.slice(0, 5).map(id => {
              const ch = channels.find(c => c.id === id);
              return ch ? (
                <span key={id} className="inline-flex items-center gap-1 px-2 py-1 bg-violet-50 text-violet-700 rounded-lg text-sm">
                  <img src={ch.avatar_url || 'https://via.placeholder.com/20'} alt="" className="w-4 h-4 rounded-full" />
                  {ch.page_name}
                </span>
              ) : null;
            })}
            {selectedChannelIds.length > 5 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-lg text-sm">+{selectedChannelIds.length - 5} khác</span>
            )}
          </div>
        )}
      </div>

      {/* 3.2 Loại bài & CTA */}
      <div className="grid grid-cols-2 gap-4 mb-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Loại bài</label>
          <select
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-violet-500 bg-white"
            value={postType}
            onChange={(e) => setPostType(e.target.value as any)}
          >
            {POST_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Nút kêu gọi (CTA)</label>
          <select
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-violet-500 bg-white"
            value={cta}
            onChange={(e) => setCta(e.target.value)}
          >
            {CTA_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
      </div>

      {/* Video Title - ONLY for Feed (not Reels) */}
      {postType === 'feed' && (
        <div className="mb-5">
          <label className="block text-sm font-medium text-gray-700 mb-2">Tiêu đề video (tuỳ chọn)</label>
          <input
            type="text"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-violet-500"
            placeholder="Nhập tiêu đề cho video Feed..."
            value={videoTitle}
            onChange={(e) => setVideoTitle(e.target.value)}
          />
        </div>
      )}

      {/* 3.3 Lịch đăng bài */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">Lịch đăng bài</label>
        <div className="space-y-2">
          <label className={`flex items-center gap-3 p-3 border rounded-xl cursor-pointer transition ${scheduleMode === 'now' ? 'border-violet-500 bg-violet-50' : 'border-gray-200 hover:border-gray-300'}`}>
            <input type="radio" name="schedule" checked={scheduleMode === 'now'} onChange={() => setScheduleMode('now')} className="w-4 h-4 text-violet-600" />
            <div>
              <p className="font-medium text-gray-900">⚡ Đăng ngay</p>
              <p className="text-xs text-gray-500">Bài viết sẽ được đăng ngay lập tức</p>
            </div>
          </label>

          <label className={`flex items-center gap-3 p-3 border rounded-xl cursor-pointer transition ${scheduleMode === 'at' ? 'border-violet-500 bg-violet-50' : 'border-gray-200 hover:border-gray-300'}`}>
            <input type="radio" name="schedule" checked={scheduleMode === 'at'} onChange={() => setScheduleMode('at')} className="w-4 h-4 text-violet-600" />
            <div className="flex-1">
              <p className="font-medium text-gray-900">🕐 Hẹn giờ</p>
              <p className="text-xs text-gray-500">Chọn thời gian cụ thể để đăng bài</p>
            </div>
          </label>

          {scheduleMode === 'at' && (
            <div className="ml-7 mt-2">
              <input
                type="datetime-local"
                className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-violet-500 ${!scheduleTime ? 'border-red-300' : 'border-gray-200'}`}
                value={scheduleTime}
                onChange={(e) => setScheduleTime(e.target.value)}
                min={new Date().toISOString().slice(0, 16)}
              />
              {!scheduleTime && <p className="text-xs text-red-500 mt-1">Vui lòng chọn thời gian đăng</p>}
            </div>
          )}

          <label className={`flex items-center gap-3 p-3 border rounded-xl cursor-pointer transition ${scheduleMode === 'auto' ? 'border-violet-500 bg-violet-50' : 'border-gray-200 hover:border-gray-300'}`}>
            <input type="radio" name="schedule" checked={scheduleMode === 'auto'} onChange={() => setScheduleMode('auto')} className="w-4 h-4 text-violet-600" />
            <div>
              <p className="font-medium text-gray-900">🎲 Lịch tự động</p>
              <p className="text-xs text-gray-500">Tính năng đang phát triển...</p>
            </div>
          </label>
        </div>
      </div>

      {/* Channel Drawer */}
      {showChannelDrawer && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-black/30" onClick={() => setShowChannelDrawer(false)} />
          <div className="relative w-full max-w-md bg-white shadow-xl flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">Chọn kênh đăng</h3>
              <button onClick={() => setShowChannelDrawer(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Group Filter + Search */}
            <div className="p-4 border-b border-gray-100">
              {/* Group Filter */}
              {groups.length > 0 && (
                <div className="mb-3">
                  <label className="block text-xs font-medium text-gray-600 mb-2">Lọc theo nhóm</label>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => setSelectedGroupId(null)}
                      className={`px-3 py-1.5 text-sm rounded-full transition ${
                        !selectedGroupId
                          ? 'bg-violet-600 text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      Tất cả
                    </button>
                    {groups.map(g => (
                      <button
                        key={g.id}
                        onClick={() => setSelectedGroupId(g.id)}
                        className={`px-3 py-1.5 text-sm rounded-full transition flex items-center gap-1 ${
                          selectedGroupId === g.id
                            ? 'text-white'
                            : 'text-gray-700 hover:opacity-80'
                        }`}
                        style={{
                          backgroundColor: selectedGroupId === g.id
                            ? g.color_hex || '#8B5CF6'
                            : `${g.color_hex || '#E5E7EB'}33`,
                        }}
                      >
                        <span
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: g.color_hex || '#8B5CF6' }}
                        />
                        {g.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Search */}
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500"
                placeholder="Tìm kiếm fanpage..."
                value={channelSearch}
                onChange={(e) => setChannelSearch(e.target.value)}
              />
              <div className="flex gap-2 mt-2">
                <button onClick={selectAll} className="text-xs text-violet-600 hover:underline">Chọn tất cả</button>
                <button onClick={deselectAll} className="text-xs text-gray-500 hover:underline">Bỏ chọn</button>
              </div>
            </div>

            {/* Channel List */}
            <div className="flex-1 overflow-y-auto p-2">
              {channelsLoading ? (
                <div className="p-8 text-center text-gray-500">Đang tải...</div>
              ) : filteredChannels.length === 0 ? (
                <div className="p-8 text-center text-gray-500">Không tìm thấy kênh nào</div>
              ) : (
                filteredChannels.map(ch => (
                  <label
                    key={ch.id}
                    className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition ${selectedChannelIds.includes(ch.id) ? 'bg-violet-50' : 'hover:bg-gray-50'}`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedChannelIds.includes(ch.id)}
                      onChange={() => toggleChannel(ch.id)}
                      className="w-5 h-5 text-violet-600 rounded"
                    />
                    <img src={ch.avatar_url || 'https://via.placeholder.com/40'} alt="" className="w-10 h-10 rounded-full" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{ch.page_name}</p>
                      <p className="text-xs text-gray-500">Fanpage</p>
                    </div>
                  </label>
                ))
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200">
              <button
                onClick={() => setShowChannelDrawer(false)}
                className="w-full py-3 bg-violet-600 text-white rounded-xl font-medium hover:bg-violet-700 transition"
              >
                Xác nhận ({selectedChannelIds.length} kênh)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/** Section 4: Bình luận tự động (Accordion) */
function AutoCommentSection({
  enabled, setEnabled, comments, setComments
}: {
  enabled: boolean;
  setEnabled: (v: boolean) => void;
  comments: AutoComment[];
  setComments: (c: AutoComment[]) => void;
}) {
  const [expanded, setExpanded] = useState(false);

  const addComment = () => {
    setComments([...comments, { id: Date.now().toString(), text: '', mediaUrl: '' }]);
  };

  const updateComment = (id: string, text: string) => {
    setComments(comments.map(c => c.id === id ? { ...c, text } : c));
  };

  const removeComment = (id: string) => {
    setComments(comments.filter(c => c.id !== id));
  };

  return (
    <div className="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
      {/* Header - Clickable */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-5 flex items-center justify-between hover:bg-gray-50 transition"
      >
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-violet-100 text-violet-600 rounded-full flex items-center justify-center text-sm font-bold">4</div>
          <h3 className="font-semibold text-gray-900">Bình luận tự động</h3>
          <span className="text-xs text-gray-400">(tuỳ chọn)</span>
        </div>
        <div className="flex items-center gap-3">
          {/* Toggle Switch */}
          <div
            onClick={(e) => { e.stopPropagation(); setEnabled(!enabled); }}
            className={`relative w-11 h-6 rounded-full transition cursor-pointer ${enabled ? 'bg-violet-600' : 'bg-gray-300'}`}
          >
            <div className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${enabled ? 'translate-x-5' : 'translate-x-0.5'}`} />
          </div>
          {/* Expand Icon */}
          <svg className={`w-5 h-5 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Content */}
      {expanded && (
        <div className="px-5 pb-5 border-t border-gray-100">
          {!enabled ? (
            <p className="text-sm text-gray-500 py-4">Bật công tắc để sử dụng tính năng bình luận tự động.</p>
          ) : (
            <>
              <p className="text-xs text-gray-500 py-3">
                💡 Trong tương lai sẽ thêm điều kiện hiển thị bình luận (ví dụ sau 5 phút, sau 10 comment...)
              </p>

              {/* Comment List */}
              <div className="space-y-3">
                {comments.map((c, idx) => (
                  <div key={c.id} className="flex gap-2">
                    <span className="text-xs text-gray-400 mt-3 w-5">{idx + 1}.</span>
                    <textarea
                      className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-violet-500 resize-none"
                      rows={2}
                      placeholder="Nhập nội dung bình luận..."
                      value={c.text}
                      onChange={(e) => updateComment(c.id, e.target.value)}
                    />
                    <button
                      onClick={() => removeComment(c.id)}
                      className="text-gray-400 hover:text-red-500 transition"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>

              {/* Add Button */}
              <button
                onClick={addComment}
                className="mt-3 w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-600 hover:border-violet-400 hover:text-violet-600 transition"
              >
                + Thêm bình luận
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

/** Video Preview - Static Thumbnail Preview (NO VIDEO PLAYER) */
function VideoPreview({
  video, caption, selectedChannels, cta, thumbnailUrl, onChangeThumbnail, onDownload, postType
}: {
  video: VideoData | null;
  caption: string;
  selectedChannels: Channel[];
  cta: string;
  thumbnailUrl?: string;
  onChangeThumbnail: () => void;
  onDownload: () => void;
  postType: 'feed' | 'reel' | 'story';
}) {
  const [previewMode, setPreviewMode] = useState<'mobile' | 'desktop'>('mobile');
  const firstChannel = selectedChannels[0];

  // Prepare thumbnail URL (from uploaded file or fetched video)
  const getThumbnailUrl = (): string | undefined => {
    if (thumbnailUrl) return thumbnailUrl;
    if (video?.thumbnailUrl) return video.thumbnailUrl;
    return undefined;
  };

  // Prepare preview data
  const previewData: PreviewData = {
    pageName: firstChannel?.page_name || 'Tên Fanpage',
    pageAvatarUrl: firstChannel?.avatar_url,
    isVerified: true,
    isSponsored: true,
    caption: caption || 'Nội dung bài viết sẽ hiển thị ở đây...',
    thumbnailUrl: getThumbnailUrl(),
    ctaText: cta ? CTA_OPTIONS.find(o => o.value === cta)?.label : undefined,
    reactionsCount: postType === 'reel' || postType === 'story' ? 15600 : 204,
    commentsCount: postType === 'reel' || postType === 'story' ? 937 : 25,
    sharesCount: postType === 'reel' || postType === 'story' ? 119 : 5,
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900">Xem trước</h3>
        </div>
        
        {/* Preview Mode Toggle */}
        <div className="flex gap-2">
          <button
            onClick={() => setPreviewMode('mobile')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-sm font-medium transition ${
              previewMode === 'mobile'
                ? 'bg-violet-600 text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <span>📱</span>
            <span>Mobile</span>
          </button>
          <button
            onClick={() => setPreviewMode('desktop')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-sm font-medium transition ${
              previewMode === 'desktop'
                ? 'bg-violet-600 text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <span>🖥️</span>
            <span>PC</span>
          </button>
        </div>

        {/* Post Type Info */}
        <div className="mt-3 text-xs text-gray-500 text-center">
          {postType === 'reel' || postType === 'story' ? 'Facebook Reels' : 'Facebook Feed'}
        </div>
      </div>

      {/* Static Preview Panel - NO VIDEO PLAYER */}
      <PreviewPanel 
        mode={postType}
        device={previewMode}
        data={previewData}
      />

      {/* Actions */}
      {video && (
        <div className="p-4 border-t border-gray-100 flex gap-2">
          <button
            onClick={onChangeThumbnail}
            className="flex-1 py-2 border border-gray-200 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition"
          >
            🖼️ Chọn thumbnail
          </button>
          <button
            onClick={onDownload}
            className="flex-1 py-2 border border-gray-200 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition"
          >
            ⬇️ Tải video
          </button>
        </div>
      )}
    </div>
  );
}

/** Thumbnail Modal */
function ThumbnailModal({
  open, onClose, videoUrl, currentThumbnail, onApply
}: {
  open: boolean;
  onClose: () => void;
  videoUrl?: string;
  currentThumbnail?: string;
  onApply: (url: string) => void;
}) {
  const [tab, setTab] = useState<'frame' | 'upload'>('frame');
  const [selectedFrame, setSelectedFrame] = useState(currentThumbnail || '');
  const [uploadedUrl, setUploadedUrl] = useState('');
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx?.drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
    setSelectedFrame(dataUrl);
  };

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setUploadedUrl(url);
    }
  };

  const handleApply = () => {
    const url = tab === 'frame' ? selectedFrame : uploadedUrl;
    if (url) {
      onApply(url);
      onClose();
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Chọn thumbnail</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setTab('frame')}
            className={`flex-1 py-3 text-sm font-medium transition ${tab === 'frame' ? 'text-violet-600 border-b-2 border-violet-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Lấy từ video
          </button>
          <button
            onClick={() => setTab('upload')}
            className={`flex-1 py-3 text-sm font-medium transition ${tab === 'upload' ? 'text-violet-600 border-b-2 border-violet-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Tải ảnh lên
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {tab === 'frame' ? (
            <div className="space-y-4">
              <div className="bg-black rounded-xl overflow-hidden">
                <video
                  ref={videoRef}
                  src={videoUrl}
                  controls
                  className="w-full max-h-64 object-contain"
                />
              </div>
              <canvas ref={canvasRef} className="hidden" />
              <button
                onClick={captureFrame}
                className="w-full py-2 bg-violet-100 text-violet-700 rounded-lg font-medium hover:bg-violet-200 transition"
              >
                📸 Chụp frame hiện tại
              </button>
              {selectedFrame && (
                <div className="border border-gray-200 rounded-xl p-2">
                  <p className="text-xs text-gray-500 mb-2">Frame đã chọn:</p>
                  <img src={selectedFrame} alt="Selected frame" className="w-full rounded-lg" />
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <input
                type="file"
                accept="image/*"
                onChange={handleUpload}
                className="w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-violet-100 file:text-violet-700 hover:file:bg-violet-200"
              />
              {uploadedUrl && (
                <div className="border border-gray-200 rounded-xl p-2">
                  <p className="text-xs text-gray-500 mb-2">Ảnh đã chọn:</p>
                  <img src={uploadedUrl} alt="Uploaded" className="w-full rounded-lg" />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 flex gap-2">
          <button onClick={onClose} className="flex-1 py-2 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 transition">
            Huỷ
          </button>
          <button
            onClick={handleApply}
            disabled={tab === 'frame' ? !selectedFrame : !uploadedUrl}
            className="flex-1 py-2 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 transition disabled:opacity-50"
          >
            Áp dụng
          </button>
        </div>
      </div>
    </div>
  );
}

// ==================== MAIN COMPONENT ====================
export default function AdStudioCard() {
  // ===== Hooks =====
  const { status: fetchStatus, error: fetchError, video, fetchVideo, reset: resetVideo } = useFetchVideo();
  const { channels, groups, loading: channelsLoading } = useChannels();

  // ===== Form State =====
  const [url, setUrl] = useState('');
  const [platform, setPlatform] = useState<'tiktok' | 'facebook' | 'auto'>('auto');
  const [caption, setCaption] = useState('');
  const [videoSource, setVideoSource] = useState<VideoSource>('original');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [selectedChannelIds, setSelectedChannelIds] = useState<string[]>([]);
  const [postType, setPostType] = useState<'feed' | 'reel' | 'story'>('reel');
  const [cta, setCta] = useState('');
  const [videoTitle, setVideoTitle] = useState('');
  const [scheduleMode, setScheduleMode] = useState<'now' | 'at' | 'auto'>('now');
  const [scheduleTime, setScheduleTime] = useState('');
  const [autoCommentsEnabled, setAutoCommentsEnabled] = useState(false);
  const [autoComments, setAutoComments] = useState<AutoComment[]>([]);
  const [customThumbnail, setCustomThumbnail] = useState<string>('');
  const [showThumbnailModal, setShowThumbnailModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ===== Derived State =====
  const selectedChannels = channels.filter(c => selectedChannelIds.includes(c.id));
  const hasVideo = fetchStatus === 'success' && video;
  const canSubmit = hasVideo && selectedChannelIds.length > 0 && (scheduleMode !== 'at' || scheduleTime);

  // ===== Handlers =====
  const handleFetch = async () => {
    const result = await fetchVideo(url, platform);
    if (result) {
      setCaption(result.caption);
      toast.success('🎉 Đã tải video thành công!');
    }
  };

  const handleReset = () => {
    resetVideo();
    setUrl('');
    setCaption('');
    setCustomThumbnail('');
    setUploadedFile(null);
    setVideoSource('original');
  };

  const handleAIRewrite = () => {
    // TODO: Integrate AI rewrite API
    toast.info('Tính năng AI gợi ý đang phát triển...');
  };

  const handleDownload = () => {
    if (video?.videoUrl) {
      const a = document.createElement('a');
      a.href = video.videoUrl;
      a.download = `video_${video.id}.mp4`;
      a.click();
    }
  };

  const handleSubmit = async (isDraft: boolean = false) => {
    if (!canSubmit && !isDraft) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }

    const payload: FormPayload = {
      sourceUrl: url,
      platform,
      video: {
        id: video?.id,
        thumbnailUrl: customThumbnail || video?.thumbnailUrl,
        localUpload: videoSource === 'upload' ? uploadedFile : null,
      },
      caption,
      title: videoTitle || undefined,
      cta,
      postType,
      channels: selectedChannelIds,
      schedule: {
        mode: scheduleMode,
        time: scheduleMode === 'at' ? scheduleTime : undefined,
      },
      autoCommentsEnabled,
      autoComments: autoComments.map(c => ({ text: c.text, mediaUrl: c.mediaUrl })),
    };

    setIsSubmitting(true);
    try {
      // TODO: Replace with actual API call
      // await schedulePost(payload);
      console.log('Submit payload:', payload);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast.success(isDraft ? '📝 Đã lưu nháp!' : `🚀 Đã lên lịch đăng cho ${selectedChannelIds.length} kênh!`);
      
      if (!isDraft) {
        // Reset form after successful submit
        handleReset();
        setSelectedChannelIds([]);
        setScheduleMode('now');
        setScheduleTime('');
        setAutoCommentsEnabled(false);
        setAutoComments([]);
      }
    } catch (err: any) {
      toast.error(err.message || 'Có lỗi xảy ra, vui lòng thử lại');
    } finally {
      setIsSubmitting(false);
    }
  };

  // ===== Render =====
  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-600 via-purple-600 to-fuchsia-600">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/10 backdrop-blur-lg border-b border-white/20">
        <div className="max-w-[1800px] mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
              <span className="text-xl">🎬</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">Ad Studio</h1>
              <p className="text-xs text-white/70">Thu thập link & Lên lịch đăng</p>
            </div>
            {/* Status Badge */}
            <span className={`ml-4 px-3 py-1 rounded-full text-xs font-medium ${
              hasVideo ? 'bg-green-500/20 text-green-100' : 
              fetchStatus === 'error' ? 'bg-red-500/20 text-red-100' : 
              'bg-white/20 text-white/80'
            }`}>
              {hasVideo ? '✓ Đã tải video' : fetchStatus === 'error' ? '✗ Lỗi tải video' : 'Chưa tải video'}
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleSubmit(true)}
              disabled={isSubmitting}
              className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition text-sm font-medium disabled:opacity-50"
            >
              Lưu nháp
            </button>
            <button
              onClick={() => handleSubmit(false)}
              disabled={!canSubmit || isSubmitting}
              className="px-4 py-2 bg-white text-violet-700 rounded-lg hover:bg-white/90 transition text-sm font-semibold disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Đang xử lý...
                </>
              ) : (
                <>🚀 Lên lịch đăng</>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content - 2 Columns */}
      <main className="max-w-[1800px] mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-10 gap-6">
          {/* Left Column - Form (70%) */}
          <div className="lg:col-span-7 space-y-8">
            {/* Section 1: Dán link */}
            <LinkSection
              url={url}
              setUrl={setUrl}
              platform={platform}
              setPlatform={setPlatform}
              status={fetchStatus}
              error={fetchError}
              onFetch={handleFetch}
              onReset={handleReset}
            />

            {/* Section 2: Nội dung & Video */}
            <ContentSection
              caption={caption}
              setCaption={setCaption}
              videoSource={videoSource}
              setVideoSource={setVideoSource}
              uploadedFile={uploadedFile}
              setUploadedFile={setUploadedFile}
              onAIRewrite={handleAIRewrite}
            />

            {/* Section 3: Cấu hình đăng bài */}
            <SettingsSection
              channels={channels}
              groups={groups}
              channelsLoading={channelsLoading}
              selectedChannelIds={selectedChannelIds}
              setSelectedChannelIds={setSelectedChannelIds}
              postType={postType}
              setPostType={setPostType}
              cta={cta}
              setCta={setCta}
              videoTitle={videoTitle}
              setVideoTitle={setVideoTitle}
              scheduleMode={scheduleMode}
              setScheduleMode={setScheduleMode}
              scheduleTime={scheduleTime}
              setScheduleTime={setScheduleTime}
            />

            {/* Section 4: Bình luận tự động */}
            <AutoCommentSection
              enabled={autoCommentsEnabled}
              setEnabled={setAutoCommentsEnabled}
              comments={autoComments}
              setComments={setAutoComments}
            />
          </div>

          {/* Right Column - Preview (30%) */}
          <div className="lg:col-span-3">
            <div className="sticky top-20">
              <VideoPreview
                video={video}
                caption={caption}
                selectedChannels={selectedChannels}
                cta={cta}
                thumbnailUrl={customThumbnail || video?.thumbnailUrl}
                onChangeThumbnail={() => setShowThumbnailModal(true)}
                onDownload={handleDownload}
                postType={postType}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Thumbnail Modal */}
      <ThumbnailModal
        open={showThumbnailModal}
        onClose={() => setShowThumbnailModal(false)}
        videoUrl={video?.videoUrl}
        currentThumbnail={customThumbnail || video?.thumbnailUrl}
        onApply={setCustomThumbnail}
      />
    </div>
  );
}

// ==================== SPIN CONTENT MODAL ====================

/**
 * Modal chi tiết cho Spin Content với 3 tabs
 */
function SpinContentModal({ onClose, onInsert }: { onClose: () => void; onInsert: (snippet: string) => void }) {
  const [activeTab, setActiveTab] = useState<'text' | 'icon' | 'emoji'>('text');

  const textExamples = [
    { label: 'Chào buổi sáng/tối', snippet: 'Chào {buổi sáng|buổi tối}!' },
    { label: 'Sản phẩm đa dạng', snippet: '{Sản phẩm|Dịch vụ|Giải pháp} của chúng tôi' },
    { label: 'Khuyến mãi', snippet: 'Giảm giá {10%|15%|20%} hôm nay!' },
    { label: 'Kêu gọi hành động', snippet: '{Inbox ngay|Gọi hotline|Đặt hàng} để nhận ưu đãi' },
  ];

  const iconPresets = [
    { code: '@icon{R1}', desc: 'Random icon bộ 1', preview: '🎯🔥💎✨🌟' },
    { code: '@icon{R2}', desc: 'Random icon bộ 2', preview: '💡🚀🎁🏆⭐' },
    { code: '@icon{R3}', desc: 'Random icon bộ 3', preview: '❤️👍🎉🌈🌺' },
    { code: '@icon{shopping}', desc: 'Shopping icons', preview: '🛍️🛒💳🎁📦' },
    { code: '@icon{food}', desc: 'Food icons', preview: '🍔🍕🍜🍰🍹' },
  ];

  const emojiGroups = [
    { code: '@emoji{happy}', desc: 'Happy faces', preview: '😊😃😄😁🤩' },
    { code: '@emoji{love}', desc: 'Love & hearts', preview: '❤️💕💖💗💘' },
    { code: '@emoji{celebration}', desc: 'Celebration', preview: '🎉🎊🥳🎈🎁' },
    { code: '@emoji{nature}', desc: 'Nature', preview: '🌸🌺🌻🌷🌹' },
    { code: '@emoji{fire}', desc: 'Fire & energy', preview: '🔥💥⚡✨💫' },
  ];

  const handleInsert = (snippet: string) => {
    onInsert(snippet);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="p-5 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900">🔄 Spin Content</h3>
            <p className="text-sm text-gray-500 mt-1">Tạo nội dung đa dạng với cú pháp spin</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('text')}
            className={`flex-1 py-3 px-4 text-sm font-medium transition ${
              activeTab === 'text'
                ? 'text-violet-600 border-b-2 border-violet-600 bg-violet-50/50'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📝 Text Spin
          </button>
          <button
            onClick={() => setActiveTab('icon')}
            className={`flex-1 py-3 px-4 text-sm font-medium transition ${
              activeTab === 'icon'
                ? 'text-violet-600 border-b-2 border-violet-600 bg-violet-50/50'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            🎨 Icon Spin
          </button>
          <button
            onClick={() => setActiveTab('emoji')}
            className={`flex-1 py-3 px-4 text-sm font-medium transition ${
              activeTab === 'emoji'
                ? 'text-violet-600 border-b-2 border-violet-600 bg-violet-50/50'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            😊 Emoji Spin
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">
          {activeTab === 'text' && (
            <div>
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4">
                <h4 className="font-semibold text-blue-900 mb-2">📖 Cách dùng</h4>
                <p className="text-sm text-blue-800 mb-2">Dùng dấu <code className="bg-blue-100 px-1 rounded">|</code> để ngăn cách các lựa chọn trong dấu ngoặc nhọn:</p>
                <code className="block bg-white border border-blue-300 rounded px-3 py-2 text-sm text-gray-800">
                  {'Chào {buổi sáng|buổi chiều|buổi tối}!'}
                </code>
                <p className="text-xs text-blue-700 mt-2">→ Hệ thống sẽ random chọn 1 trong 3 cụm từ khi đăng</p>
              </div>

              <h4 className="font-semibold text-gray-900 mb-3">✨ Mẫu có sẵn</h4>
              <div className="space-y-2">
                {textExamples.map((item, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-xl p-3 hover:border-violet-400 transition">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-700">{item.label}</p>
                        <code className="text-xs text-violet-600 bg-violet-50 px-2 py-1 rounded mt-1 inline-block">
                          {item.snippet}
                        </code>
                      </div>
                      <button
                        onClick={() => handleInsert(item.snippet)}
                        className="px-3 py-1 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700"
                      >
                        Chèn
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'icon' && (
            <div>
              <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 mb-4">
                <h4 className="font-semibold text-purple-900 mb-2">🎨 Icon Random</h4>
                <p className="text-sm text-purple-800 mb-2">Hệ thống sẽ tự động chọn 1 icon ngẫu nhiên từ bộ preset:</p>
                <code className="block bg-white border border-purple-300 rounded px-3 py-2 text-sm text-gray-800">
                  Sản phẩm hot @icon{'{'}R1{'}'} nhất tuần!
                </code>
                <p className="text-xs text-purple-700 mt-2">→ Mỗi lần đăng sẽ hiện icon khác nhau từ bộ R1</p>
              </div>

              <h4 className="font-semibold text-gray-900 mb-3">🎯 Bộ icon có sẵn</h4>
              <div className="space-y-2">
                {iconPresets.map((item, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-xl p-3 hover:border-violet-400 transition">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-700">{item.desc}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <code className="text-xs text-violet-600 bg-violet-50 px-2 py-1 rounded">
                            {item.code}
                          </code>
                          <span className="text-lg">{item.preview}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleInsert(item.code)}
                        className="px-3 py-1 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700"
                      >
                        Chèn
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'emoji' && (
            <div>
              <div className="bg-pink-50 border border-pink-200 rounded-xl p-4 mb-4">
                <h4 className="font-semibold text-pink-900 mb-2">😊 Emoji Random</h4>
                <p className="text-sm text-pink-800 mb-2">Chọn 1 emoji ngẫu nhiên từ nhóm cảm xúc:</p>
                <code className="block bg-white border border-pink-300 rounded px-3 py-2 text-sm text-gray-800">
                  Chúc bạn một ngày tuyệt vời @emoji{'{'}happy{'}'}
                </code>
                <p className="text-xs text-pink-700 mt-2">→ Random từ các emoji vui vẻ: 😊😃😄😁🤩</p>
              </div>

              <h4 className="font-semibold text-gray-900 mb-3">💬 Nhóm emoji có sẵn</h4>
              <div className="space-y-2">
                {emojiGroups.map((item, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-xl p-3 hover:border-violet-400 transition">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-700">{item.desc}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <code className="text-xs text-violet-600 bg-violet-50 px-2 py-1 rounded">
                            {item.code}
                          </code>
                          <span className="text-lg">{item.preview}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleInsert(item.code)}
                        className="px-3 py-1 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700"
                      >
                        Chèn
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 rounded-b-2xl">
          <p className="text-xs text-gray-500 text-center">
            💡 Tip: Kết hợp nhiều cú pháp spin để tạo nội dung đa dạng hơn!
          </p>
        </div>
      </div>
    </div>
  );
}
