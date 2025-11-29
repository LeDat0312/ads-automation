// NOTE: AdStudio - Updated to use real API calls
import React, { useState, useEffect } from 'react';
import * as API from '../api/adStudio';

// ============================================================================
// TYPES
// ============================================================================

type AssetPlatform = 'tiktok' | 'facebook' | 'other';

type Asset = {
  id: string;
  platform: AssetPlatform;
  sourceUrl: string;
  videoUrl: string;
  thumbnailUrl: string;
  localVideoUrl?: string | null;      // Local video URL if downloaded
  localThumbnailUrl?: string | null;  // Local thumbnail URL if downloaded
  captionOriginal: string;
  duration?: number;
  durationSeconds?: number;           // Alias for duration
  hashtags?: string[];
  note?: string;
  fileSizeBytes?: number;             // Video file size in bytes
  qualityLabel?: string;              // Quality label (e.g., "HD (No Watermark)")
};

type ScheduleMode = 'NOW' | 'RANDOM_2H' | 'EXACT_TIME';

type Language = 'la' | 'vi' | 'th';

type ThumbnailSource = 'FRAME' | 'UPLOAD';

type PostStatus = 'published' | 'scheduled' | 'draft' | 'failed' | 'cancelled';

type Post = {
  id: string;
  caption: string;
  thumbnailUrl: string;
  channels: string[];
  scheduledTime: string;
  status: PostStatus;
  creator: string;
  videoUrl?: string;
};

type DashboardStats = {
  totalPosts: number;
  publishedPosts: number;
  scheduledPosts: number;
  draftPosts: number;
  failedPosts: number;
};

// Error categorization for better UX
type FetchErrorCode =
  | 'NONE'
  | 'APIFY_KEY_MISSING'
  | 'APIFY_KEY_INVALID'
  | 'SCRAPE_FAILED'
  | 'INVALID_URL'
  | 'NETWORK_ERROR'
  | 'UNKNOWN';

type SchedulePayload = {
  assetId: string;
  videoTitle?: string;         // NEW - Video title field
  caption: string;
  language: Language;
  ctaText: string;
  targetUrl: string;
  pageIds: string[];
  scheduleMode: ScheduleMode;
  scheduleTime?: string;
  thumbnailSource: ThumbnailSource;
  thumbnailFile?: File;
  videoUrl?: string;
  customVideoFile?: File;
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Format file size from bytes to human-readable string
 */
function formatFileSize(bytes?: number): string | undefined {
  if (!bytes || bytes <= 0) return undefined;
  const mb = bytes / (1024 * 1024);
  if (mb < 0.1) {
    const kb = bytes / 1024;
    return `${kb.toFixed(0)} KB`;
  }
  return `${mb.toFixed(1)} MB`;
}

/**
 * Phát hiện nền tảng từ URL
 */
function detectPlatform(url: string): AssetPlatform {
  try {
    const urlObj = new URL(url);
    const host = urlObj.hostname.toLowerCase();
    
    if (host.includes('tiktok.com')) return 'tiktok';
    if (host.includes('facebook.com') || host.includes('fb.watch') || host.includes('fb.com')) return 'facebook';
    return 'other';
  } catch {
    return 'other';
  }
}

/**
 * Lấy thông tin nền tảng (icon, label, màu)
 */
function getPlatformInfo(platform: AssetPlatform) {
  switch (platform) {
    case 'tiktok':
      return { label: 'TikTok', icon: '🎵', color: 'bg-black text-white' };
    case 'facebook':
      return { label: 'Facebook', icon: '📘', color: 'bg-blue-600 text-white' };
    default:
      return { label: 'Không xác định', icon: '❓', color: 'bg-gray-400 text-white' };
  }
}

// ============================================================================
// NOTE: AdStudio - Mock data removed, now using real API calls
// All data is loaded via API from backend
// ============================================================================

// CTA Options - Map to backend enum values
const ctaOptions = [
  { label: 'Nhắn tin ngay', value: 'MESSAGE' },
  { label: 'Tìm hiểu thêm', value: 'LEARN_MORE' },
  { label: 'Gọi ngay', value: 'CALL_NOW' },
  { label: 'Đăng ký', value: 'SIGN_UP' },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function AdStudioCard() {
  // Tab management
  const [activeTab, setActiveTab] = useState<'dashboard' | 'collect' | 'collection' | 'posts'>('dashboard');
  
  // Assets
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [isLoadingAssets, setIsLoadingAssets] = useState(false);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);
  
  // Tab 2: Thu thập link - Step 1
  const [inputUrl, setInputUrl] = useState('');
  const [detectedPlatform, setDetectedPlatform] = useState<AssetPlatform>('other');
  const [isLoadingAsset, setIsLoadingAsset] = useState(false);
  const [editedCaption, setEditedCaption] = useState('');
  const [videoSource, setVideoSource] = useState<'original' | 'upload'>('original');
  const [customVideoFile, setCustomVideoFile] = useState<File | null>(null);
  
  // Tab 2: Step 2 - Publish form
  const [publishForm, setPublishForm] = useState({
    videoTitle: '',              // NEW: Video title field
    caption: '',
    language: 'la' as Language,
    ctaText: 'MESSAGE',          // NEW: Use enum value instead of string
    targetUrl: '',
    pageIds: [] as string[],
    scheduleMode: 'NOW' as ScheduleMode,
    scheduleTime: '',
    thumbnailSource: 'FRAME' as ThumbnailSource,
    thumbnailFile: null as File | null,
  });
  
  // Tab 4: Posts management
  const [posts, setPosts] = useState<Post[]>([]);
  const [filterStatus, setFilterStatus] = useState<PostStatus | 'all'>('all');
  
  // Dashboard
  const [dashboardRange, setDashboardRange] = useState('7days');
  const [dashboardStats, setDashboardStats] = useState<DashboardStats>({
    totalPosts: 0,
    publishedPosts: 0,
    scheduledPosts: 0,
    draftPosts: 0,
    failedPosts: 0,
  });
  const [recentPosts, setRecentPosts] = useState<Post[]>([]);
  
  // NOTE: AdStudio - Add loading and error states
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [isLoadingPosts, setIsLoadingPosts] = useState(false);
  
  // NEW - Categorized error handling for fetch operations
  const [fetchErrorCode, setFetchErrorCode] = useState<FetchErrorCode>('NONE');
  const [fetchErrorMessage, setFetchErrorMessage] = useState<string | null>(null);
  
  // Generic error for dashboard/collections (keep for backward compat)
  const [error, setError] = useState<string | null>(null);
  
  const [fanpages, setFanpages] = useState<Array<{id: string, name: string}>>([]);
  const [fanpagesError, setFanpagesError] = useState<string | null>(null);

  // NOTE: AdStudio - Load dashboard stats
  useEffect(() => {
    if (activeTab === 'dashboard') {
      setIsLoadingStats(true);
      setIsLoadingPosts(true);
      setError(null);
      
      API.getSummary(dashboardRange === '30days' ? '30d' : '7d')
        .then(data => {
          setDashboardStats({
            totalPosts: data.totalPosts || 0,
            publishedPosts: data.publishedPosts || 0,
            scheduledPosts: data.scheduledPosts || 0,
            draftPosts: data.draftPosts || 0,
            failedPosts: data.failedPosts || 0,
          });
        })
        .catch(err => {
          console.error('Error loading dashboard stats:', err);
          setError('Không thể tải số liệu tổng quan. Vui lòng thử lại.');
        })
        .finally(() => setIsLoadingStats(false));

      // Load recent posts for dashboard
      API.getPosts({ status: 'ALL' })
        .then(data => {
          const formatted = data.slice(0, 5).map((post: any) => ({
            id: post.id,
            caption: post.caption,
            thumbnailUrl: post.thumbnailUrl || '',
            channels: post.channels || [],
            scheduledTime: post.scheduleTime || '',
            status: post.status,
            creator: post.creatorName || 'User',
          }));
          setRecentPosts(formatted);
        })
        .catch(err => {
          console.error('Error loading recent posts:', err);
        })
        .finally(() => setIsLoadingPosts(false));
    }
  }, [activeTab, dashboardRange]);

  // NOTE: AdStudio - Load assets when switching to collection tab
  useEffect(() => {
    if (activeTab === 'collection') {
      setIsLoadingAssets(true);
      setError(null);
      
      API.getAssets()
        .then(data => {
          setAssets(data);
        })
        .catch(err => {
          console.error('Error loading assets:', err);
          setError('Không thể tải bộ sưu tầm. Vui lòng thử lại.');
        })
        .finally(() => setIsLoadingAssets(false));
    }
  }, [activeTab]);

  // NOTE: AdStudio - Load posts when switching to posts tab
  useEffect(() => {
    if (activeTab === 'posts') {
      setIsLoadingPosts(true);
      const statusFilter = filterStatus === 'all' ? undefined : filterStatus.toUpperCase();
      API.getPosts({ status: statusFilter })
        .then(data => {
          const formatted = data.map((post: any) => ({
            id: post.id,
            caption: post.caption,
            thumbnailUrl: post.thumbnailUrl || '',
            channels: post.channels || [],
            scheduledTime: post.scheduleTime || '',
            status: post.status.toLowerCase() as PostStatus,
            creator: post.creatorName || 'User',
          }));
          setPosts(formatted);
        })
        .catch(err => {
          console.error('Error loading posts:', err);
        })
        .finally(() => setIsLoadingPosts(false));
    }
  }, [activeTab, filterStatus]);

  // NOTE: AdStudio - Load fanpages on mount
  useEffect(() => {
    API.getFanpages()
      .then(data => {
        if (data.length === 0) {
          setFanpagesError('Chưa có fanpage nào được cấu hình. Vui lòng kiểm tra lại mục Cài Đặt.');
        }
        setFanpages(data.map((p: any) => ({ id: p.id, name: p.name })));
      })
      .catch(err => {
        console.error('Error loading fanpages:', err);
        setFanpagesError('Không thể tải danh sách fanpage. Vui lòng kiểm tra kết nối.');
      });
  }, []);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleUrlChange = (url: string) => {
    setInputUrl(url);
    const platform = detectPlatform(url);
    setDetectedPlatform(platform);
  };

  const handleFetchAsset = async () => {
    if (!inputUrl.trim()) {
      setFetchErrorCode('INVALID_URL');
      setFetchErrorMessage('Vui lòng nhập URL video');
      return;
    }

    // Reset errors before new fetch
    setFetchErrorCode('NONE');
    setFetchErrorMessage(null);
    setIsLoadingAsset(true);
    
    try {
      let asset: Asset;
      
      // NOTE: AdStudio - Use real API calls
      if (detectedPlatform === 'tiktok') {
        asset = await API.fetchTiktokAsset(inputUrl);
      } else if (detectedPlatform === 'facebook') {
        asset = await API.fetchFacebookAsset(inputUrl);
      } else {
        setFetchErrorCode('INVALID_URL');
        setFetchErrorMessage('Nền tảng không được hỗ trợ. Chỉ hỗ trợ TikTok và Facebook.');
        setIsLoadingAsset(false);
        return;
      }

      // Success: set asset and clear errors
      setSelectedAsset(asset);
      setEditedCaption(asset.captionOriginal);
      setAssets((prev) => [...prev, asset]);
      setFetchErrorCode('NONE');
      setFetchErrorMessage(null);
    } catch (err: any) {
      console.error('[AdStudio] Error fetching asset:', err);
      
      // Ensure selectedAsset is cleared on error (no fake data)
      setSelectedAsset(null);
      
      // NOTE: AdStudio - Map backend errors to user-friendly messages
      if (API.isApifyKeyMissing(err)) {
        setFetchErrorCode('APIFY_KEY_MISSING');
        setFetchErrorMessage('Apify API key chưa được cấu hình. Vui lòng vào trang Cài đặt để thêm key trước khi tải video TikTok.');
      } else if (err?.detail === 'APIFY_KEY_INVALID' || err?.message?.includes('API Key có định dạng không hợp lệ')) {
        setFetchErrorCode('APIFY_KEY_INVALID');
        setFetchErrorMessage('Apify API key không hợp lệ. Kiểm tra lại key trong trang Cài đặt.');
      } else if (API.isApifyScrapeFailed(err)) {
        setFetchErrorCode('SCRAPE_FAILED');
        setFetchErrorMessage('Không lấy được dữ liệu từ TikTok. Thử lại sau hoặc kiểm tra lại link video.');
      } else if (err?.status === 422 || err?.status === 400) {
        setFetchErrorCode('INVALID_URL');
        setFetchErrorMessage('Đường dẫn TikTok không hợp lệ. Vui lòng kiểm tra lại link.');
      } else if (!err?.status || err?.status === 0 || err?.message?.includes('Network')) {
        setFetchErrorCode('NETWORK_ERROR');
        setFetchErrorMessage('Kết nối mạng không ổn định hoặc server đang bận. Thử lại sau ít phút.');
      } else {
        setFetchErrorCode('UNKNOWN');
        setFetchErrorMessage('Có lỗi không xác định xảy ra khi tải video. Thử lại sau.');
      }
    } finally {
      setIsLoadingAsset(false);
    }
  };

  const handleSchedulePost = async () => {
    if (!selectedAsset) return;
    if (publishForm.pageIds.length === 0) {
      alert('Vui lòng chọn ít nhất 1 fanpage');
      return;
    }

    const payload: SchedulePayload = {
      assetId: selectedAsset.id,
      videoTitle: publishForm.videoTitle?.trim() || undefined,  // NEW: Send video title
      caption: publishForm.caption,
      language: publishForm.language,
      ctaText: publishForm.ctaText || 'MESSAGE',                // NEW: Ensure fallback to MESSAGE
      targetUrl: publishForm.targetUrl,
      pageIds: publishForm.pageIds,
      scheduleMode: publishForm.scheduleMode,
      scheduleTime: publishForm.scheduleTime,
      thumbnailSource: publishForm.thumbnailSource,
      thumbnailFile: publishForm.thumbnailFile || undefined,
      videoUrl: videoSource === 'original' ? selectedAsset.videoUrl : undefined,
      customVideoFile: customVideoFile || undefined,
    };

    // NOTE: AdStudio - Use real API
    try {
      await API.schedulePost(payload);
      alert('Đã lên lịch đăng bài thành công!');
      
      // Reset form (no need to change step in merged UI)
      setSelectedAsset(null);
      setInputUrl('');
      setEditedCaption('');
      setCustomVideoFile(null);
      setPublishForm({
        videoTitle: '',          // NEW: Reset video title
        caption: '',
        language: 'la',
        ctaText: 'MESSAGE',      // NEW: Use enum value
        targetUrl: '',
        pageIds: [],
        scheduleMode: 'NOW',
        scheduleTime: '',
        thumbnailSource: 'FRAME',
        thumbnailFile: null,
      });
      setActiveTab('posts');
    } catch (error) {
      console.error('Error scheduling post:', error);
      alert('Lỗi khi lên lịch đăng bài. Vui lòng thử lại.');
    }
  };

  const handleUseAssetFromCollection = (asset: Asset) => {
    setSelectedAsset(asset);
    setEditedCaption(asset.captionOriginal);
    setActiveTab('collect');
    // Pre-fill caption vào form (no step change needed)
    setPublishForm((prev) => ({ ...prev, caption: asset.captionOriginal }));
  };

  const handleDeleteAsset = async (assetId: string) => {
    if (!window.confirm("Bạn có chắc muốn xóa video này khỏi bộ sưu tập? Hành động này không thể hoàn tác.")) {
      return;
    }

    setIsDeletingId(assetId);

    try {
      await API.deleteAdStudioAsset(assetId);
      setAssets(prev => prev.filter(a => a.id !== assetId));
      alert("Đã xóa video khỏi bộ sưu tập.");
    } catch (error) {
      console.error(error);
      alert("Xóa video thất bại. Thử lại sau.");
    } finally {
      setIsDeletingId(null);
    }
  };

  const handleCustomVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCustomVideoFile(file);
    }
  };

  const handleThumbnailUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPublishForm((prev) => ({ ...prev, thumbnailFile: file }));
    }
  };

  const handleCancelPost = async (postId: string) => {
    if (!confirm('Bạn có chắc muốn hủy bài đăng này?')) {
      return;
    }

    try {
      await API.cancelPost(postId);
      alert('Đã hủy bài đăng thành công!');
      
      // Reload posts
      const statusFilter = filterStatus === 'all' ? undefined : filterStatus.toUpperCase();
      const data = await API.getPosts({ status: statusFilter });
      const formatted = data.map((post: any) => ({
        id: post.id,
        caption: post.caption,
        thumbnailUrl: post.thumbnailUrl || '',
        channels: post.channels || [],
        scheduledTime: post.scheduleTime || '',
        status: post.status.toLowerCase() as PostStatus,
        creator: post.creatorName || 'User',
      }));
      setPosts(formatted);
    } catch (error) {
      console.error('Error canceling post:', error);
      alert('Lỗi khi hủy bài đăng. Vui lòng thử lại.');
    }
  };

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const platformInfo = getPlatformInfo(detectedPlatform);

  const renderTabButton = (
    tab: 'dashboard' | 'collect' | 'collection' | 'posts',
    label: string
  ) => (
    <button
      onClick={() => setActiveTab(tab)}
      className={`px-6 py-3 font-medium transition-colors border-b-2 ${
        activeTab === tab
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-gray-600 hover:text-gray-900'
      }`}
    >
      {label}
    </button>
  );

  const getStatusBadge = (status: PostStatus) => {
    const configs = {
      published: { label: 'Đã đăng', color: 'bg-green-100 text-green-800' },
      scheduled: { label: 'Chờ đăng', color: 'bg-blue-100 text-blue-800' },
      draft: { label: 'Nháp', color: 'bg-gray-100 text-gray-800' },
      failed: { label: 'Thất bại', color: 'bg-red-100 text-red-800' },
      cancelled: { label: 'Đã hủy', color: 'bg-yellow-100 text-yellow-800' },
    };
    const config = configs[status];
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  // ============================================================================
  // TAB RENDERS
  // ============================================================================

  const renderDashboardTab = () => (
    <div className="space-y-6">
      {/* Bộ lọc */}
      <div className="flex gap-4 items-center">
        <select
          value={dashboardRange}
          onChange={(e) => setDashboardRange(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="today">Hôm nay</option>
          <option value="7days">7 ngày</option>
          <option value="30days">30 ngày</option>
          <option value="custom">Tuỳ chọn</option>
        </select>
        <select className="px-4 py-2 border rounded-lg">
          <option value="all">Tất cả kênh</option>
          <option value="facebook">Facebook</option>
          <option value="tiktok">TikTok</option>
        </select>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading indicator */}
      {isLoadingStats && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Đang tải dữ liệu...</p>
        </div>
      )}

      {/* Số liệu tổng quan */}
      {!isLoadingStats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white p-4 rounded-lg border shadow-sm">
            <div className="text-gray-600 text-sm">Tổng bài đăng</div>
            <div className="text-2xl font-bold text-gray-900">{dashboardStats.totalPosts}</div>
          </div>
          <div className="bg-white p-4 rounded-lg border shadow-sm">
            <div className="text-gray-600 text-sm">Đã đăng</div>
            <div className="text-2xl font-bold text-green-600">{dashboardStats.publishedPosts}</div>
          </div>
          <div className="bg-white p-4 rounded-lg border shadow-sm">
            <div className="text-gray-600 text-sm">Chờ đăng</div>
            <div className="text-2xl font-bold text-blue-600">{dashboardStats.scheduledPosts}</div>
          </div>
          <div className="bg-white p-4 rounded-lg border shadow-sm">
            <div className="text-gray-600 text-sm">Nháp</div>
            <div className="text-2xl font-bold text-gray-600">{dashboardStats.draftPosts}</div>
          </div>
          <div className="bg-white p-4 rounded-lg border shadow-sm">
            <div className="text-gray-600 text-sm">Thất bại</div>
            <div className="text-2xl font-bold text-red-600">{dashboardStats.failedPosts}</div>
          </div>
        </div>
      )}

      {/* Lịch đăng 7 ngày tới */}
      {!isLoadingPosts && (
        <div className="bg-white rounded-lg border shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Lịch đăng trong 7 ngày tới</h3>
          {recentPosts.filter((p) => p.status === 'scheduled').length === 0 ? (
            <p className="text-gray-500 text-center py-8">Chưa có bài đăng nào được lên lịch</p>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Thời gian</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Nội dung</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Kênh</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {/* NOTE: AdStudio - Use recentPosts from API */}
                {recentPosts.filter((p) => p.status === 'scheduled').map((post) => (
                  <tr key={post.id} className="border-t">
                    <td className="px-4 py-3 text-sm">{post.scheduledTime}</td>
                    <td className="px-4 py-3 text-sm">{post.caption.substring(0, 50)}...</td>
                    <td className="px-4 py-3 text-sm">{post.channels.join(', ')}</td>
                    <td className="px-4 py-3">{getStatusBadge(post.status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );

  // ============================================================================
  // COLLECT TAB - HELPER FUNCTIONS (NEW: Phase 1 - Merged UI)
  // ============================================================================

  /**
   * Render left panel: URL input + Caption + Publish form
   * All sections visible in single column, no step switching
   */
  const renderLeftPanel = () => {
    return (
      <div className="space-y-6">
        {/* Section 1: URL Input - Always visible */}
        <div className="bg-white border rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">1. Dán link video</h3>
          
          <div className="space-y-4">
            {/* URL Input với platform detection */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">URL video</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputUrl}
                  onChange={(e) => handleUrlChange(e.target.value)}
                  placeholder="Dán link TikTok hoặc Facebook..."
                  className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <span className={`px-3 py-2 rounded-lg text-sm font-medium ${platformInfo.color}`}>
                  {platformInfo.icon} {platformInfo.label}
                </span>
              </div>
            </div>

            {/* Error Display - NEW: Categorized errors with /settings link */}
            {fetchErrorMessage && (
              <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700">
                <div className="flex items-start justify-between gap-2">
                  <span className="flex-1">{fetchErrorMessage}</span>
                  
                  {/* Show settings link only for config errors */}
                  {(fetchErrorCode === 'APIFY_KEY_MISSING' || fetchErrorCode === 'APIFY_KEY_INVALID') && (
                    <a
                      href="/settings"
                      className="shrink-0 rounded border border-red-300 bg-white px-2 py-1 text-[11px] font-semibold text-red-700 hover:bg-red-50 transition-colors"
                    >
                      Mở Cài đặt
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Nút lấy video */}
            <button
              onClick={handleFetchAsset}
              disabled={detectedPlatform === 'other' || isLoadingAsset}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isLoadingAsset ? 'Đang tải...' : `Lấy video ${platformInfo.label}`}
            </button>
          </div>
        </div>

        {/* Section 2: Caption & Video Source - Show after asset fetched */}
        {selectedAsset && (
          <div className="bg-white border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">2. Nội dung & Video</h3>
            
            <div className="space-y-4">
              {/* Caption gốc */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Nội dung gốc (Thai/Viet)
                </label>
                <textarea
                  value={editedCaption}
                  onChange={(e) => setEditedCaption(e.target.value)}
                  rows={6}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Radio: Video source */}
              <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
                <label className="flex items-start gap-3">
                  <input
                    type="radio"
                    name="videoSource"
                    checked={videoSource === 'original'}
                    onChange={() => setVideoSource('original')}
                    className="mt-1"
                  />
                  <div>
                    <div className="font-medium">Dùng video gốc & chỉnh sửa nội dung</div>
                    <div className="text-sm text-gray-600">
                      Video sẽ là video từ link gốc. Bạn có thể chỉnh sửa caption.
                    </div>
                  </div>
                </label>
                
                <label className="flex items-start gap-3">
                  <input
                    type="radio"
                    name="videoSource"
                    checked={videoSource === 'upload'}
                    onChange={() => setVideoSource('upload')}
                    className="mt-1"
                  />
                  <div>
                    <div className="font-medium">Dùng nội dung gốc, tự tải lên video của tôi</div>
                    <div className="text-sm text-gray-600">
                      Giữ caption gốc, nhưng upload video riêng của bạn.
                    </div>
                  </div>
                </label>

                {videoSource === 'upload' && (
                  <input
                    type="file"
                    accept="video/*"
                    onChange={handleCustomVideoUpload}
                    className="w-full px-4 py-2 border rounded-lg bg-white"
                  />
                )}
              </div>
            </div>
          </div>
        )}

        {/* Section 3: Publish Settings - Show after asset fetched */}
        {selectedAsset && (
          <div className="bg-white border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">3. Cấu hình đăng bài</h3>
            
            <div className="space-y-4">
              {/* Video Title - NEW */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Tiêu đề video</label>
                <input
                  type="text"
                  value={publishForm.videoTitle}
                  onChange={(e) => setPublishForm({ ...publishForm, videoTitle: e.target.value })}
                  placeholder="Nhập tiêu đề video (tùy chọn)"
                  maxLength={150}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Caption for publish */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Nội dung đăng</label>
                <textarea
                  value={publishForm.caption}
                  onChange={(e) => setPublishForm({ ...publishForm, caption: e.target.value })}
                  rows={5}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Ngôn ngữ */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Ngôn ngữ</label>
                <select
                  value={publishForm.language}
                  onChange={(e) => setPublishForm({ ...publishForm, language: e.target.value as Language })}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  <option value="la">ພາສາລາວ (Lào)</option>
                  <option value="vi">Tiếng Việt</option>
                  <option value="th">ภาษาไทย (Thái)</option>
                </select>
              </div>

              {/* Fanpage selection */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Chọn fanpage <span className="text-red-500">*</span>
                </label>
                {fanpagesError && (
                  <div className="text-sm text-red-600 mb-2">{fanpagesError}</div>
                )}
                <div className="space-y-2 max-h-40 overflow-y-auto border rounded-lg p-3">
                  {fanpages.map((page) => (
                    <label key={page.id} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={publishForm.pageIds.includes(page.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setPublishForm({
                              ...publishForm,
                              pageIds: [...publishForm.pageIds, page.id],
                            });
                          } else {
                            setPublishForm({
                              ...publishForm,
                              pageIds: publishForm.pageIds.filter((id) => id !== page.id),
                            });
                          }
                        }}
                      />
                      <span className="text-sm">{page.name}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* CTA - NEW: Updated to use enum values */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Nút hành động (CTA)</label>
                <select
                  value={publishForm.ctaText}
                  onChange={(e) => setPublishForm({ ...publishForm, ctaText: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  {ctaOptions.map((cta) => (
                    <option key={cta.value} value={cta.value}>
                      {cta.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Target URL */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Link đích (URL)</label>
                <input
                  type="url"
                  value={publishForm.targetUrl}
                  onChange={(e) => setPublishForm({ ...publishForm, targetUrl: e.target.value })}
                  placeholder="https://..."
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>

              {/* Thumbnail source */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Thumbnail</label>
                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={publishForm.thumbnailSource === 'FRAME'}
                      onChange={() => setPublishForm({ ...publishForm, thumbnailSource: 'FRAME' })}
                    />
                    <span className="text-sm">Dùng frame từ video</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={publishForm.thumbnailSource === 'UPLOAD'}
                      onChange={() => setPublishForm({ ...publishForm, thumbnailSource: 'UPLOAD' })}
                    />
                    <span className="text-sm">Upload ảnh thumbnail riêng</span>
                  </label>
                  {publishForm.thumbnailSource === 'UPLOAD' && (
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleThumbnailUpload}
                      className="w-full px-4 py-2 border rounded-lg bg-white"
                    />
                  )}
                </div>
              </div>

              {/* Schedule mode */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Lịch đăng</label>
                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={publishForm.scheduleMode === 'NOW'}
                      onChange={() => setPublishForm({ ...publishForm, scheduleMode: 'NOW' })}
                    />
                    <span className="text-sm">Đăng ngay</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={publishForm.scheduleMode === 'RANDOM_2H'}
                      onChange={() => setPublishForm({ ...publishForm, scheduleMode: 'RANDOM_2H' })}
                    />
                    <span className="text-sm">Ngẫu nhiên trong 2 giờ tới</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={publishForm.scheduleMode === 'EXACT_TIME'}
                      onChange={() => setPublishForm({ ...publishForm, scheduleMode: 'EXACT_TIME' })}
                    />
                    <span className="text-sm">Hẹn giờ cụ thể</span>
                  </label>
                  {publishForm.scheduleMode === 'EXACT_TIME' && (
                    <input
                      type="datetime-local"
                      value={publishForm.scheduleTime}
                      onChange={(e) => setPublishForm({ ...publishForm, scheduleTime: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg"
                    />
                  )}
                </div>
              </div>

              {/* Submit button */}
              <button
                onClick={handleSchedulePost}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
              >
                Lưu vào lịch đăng
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  /**
   * Render right preview panel: Video player + metadata
   * Always visible, shows placeholder when no asset
   */
  const renderRightPreview = () => {
    return (
      <div className="space-y-4 sticky top-4">
        <h3 className="text-lg font-semibold">Video Preview</h3>
        
        {selectedAsset ? (
          <div className="bg-white border rounded-lg p-4 space-y-3">
            {/* Video preview */}
            <div className="aspect-[9/16] bg-gray-100 rounded-lg overflow-hidden max-w-xs mx-auto">
              {videoSource === 'original' ? (
                <video
                  src={selectedAsset.videoUrl}
                  poster={selectedAsset.thumbnailUrl}
                  controls
                  className="w-full h-full object-cover"
                />
              ) : customVideoFile ? (
                <video
                  src={URL.createObjectURL(customVideoFile)}
                  controls
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  Chọn video để upload
                </div>
              )}
            </div>

            {/* Video metadata */}
            <div className="text-sm text-gray-600 space-y-2">
              {/* Badge + Download Button Row - NEW */}
              <div className="flex items-center justify-between">
                {/* Quality Badge with Size */}
                <span className="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
                  {selectedAsset.qualityLabel || 'HD (No Watermark)'}
                  {formatFileSize(selectedAsset.fileSizeBytes) && (
                    <>
                      <span className="mx-1">·</span>
                      <span>{formatFileSize(selectedAsset.fileSizeBytes)}</span>
                    </>
                  )}
                </span>

                {/* Download Button */}
                {selectedAsset.videoUrl && (
                  <a
                    href={selectedAsset.videoUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    download
                    className="inline-flex items-center rounded-lg border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-colors"
                  >
                    <span className="mr-1">⬇️</span>
                    Tải video
                  </a>
                )}
              </div>

              {/* Duration */}
              {selectedAsset.duration && (
                <div className="flex items-center text-xs text-gray-500">
                  <span>🕒 Thời lượng: {selectedAsset.duration}s</span>
                </div>
              )}

              {/* Hashtags */}
              {selectedAsset.hashtags && selectedAsset.hashtags.length > 0 && (
                <div className="text-xs text-gray-500">
                  #{selectedAsset.hashtags.join(' #')}
                </div>
              )}
            </div>

            {/* Preview of publish content */}
            <div className="mt-4 pt-4 border-t">
              {/* Video Title Preview - NEW */}
              {publishForm.videoTitle && (
                <h4 className="text-base font-semibold text-gray-900 mb-2">
                  {publishForm.videoTitle}
                </h4>
              )}
              <div className="text-sm text-gray-700 whitespace-pre-wrap mb-3">
                {publishForm.caption || editedCaption}
              </div>
              <div className="text-xs text-gray-500 space-y-1">
                <div>📍 Fanpage: {publishForm.pageIds.length} được chọn</div>
                <div>⏰ Lịch: {
                  publishForm.scheduleMode === 'NOW' ? 'Đăng ngay' : 
                  publishForm.scheduleMode === 'RANDOM_2H' ? 'Ngẫu nhiên 2h' : 
                  publishForm.scheduleTime
                }</div>
              </div>
            </div>

            {/* Delete button */}
            <button
              onClick={() => {
                setSelectedAsset(null);
                setEditedCaption('');
                setCustomVideoFile(null);
              }}
              className="w-full px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
            >
              Xoá video
            </button>
          </div>
        ) : (
          <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center text-gray-500">
            Dán link và lấy video để xem preview
          </div>
        )}
      </div>
    );
  };

  const renderCollectTab = () => (
    <div className="space-y-6">
      {/* Error display - Global */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* 2-column layout: Forms left, Preview right */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderLeftPanel()}
        {renderRightPreview()}
      </div>
    </div>
  );
  const renderCollectionTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Bộ sưu tầm ({assets.length} asset)</h3>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Tìm kiếm..."
            className="px-4 py-2 border rounded-lg"
          />
          <select className="px-4 py-2 border rounded-lg">
            <option value="all">Tất cả nền tảng</option>
            <option value="tiktok">TikTok</option>
            <option value="facebook">Facebook</option>
          </select>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading indicator */}
      {isLoadingAssets && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Đang tải bộ sưu tầm...</p>
        </div>
      )}

      {/* Asset grid - Compact layout */}
      {!isLoadingAssets && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
          {assets.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-500">
              Chưa có asset nào. Hãy thu thập video từ tab "Thu thập link".
            </div>
          ) : (
            assets.map((asset) => (
              <div 
                key={asset.id} 
                className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden hover:shadow-md transition-shadow relative"
              >
                {/* Video thumbnail/preview with delete button */}
                <div className="relative aspect-[9/16] bg-black">
                  <video
                    src={asset.localVideoUrl ?? asset.videoUrl}
                    poster={asset.localThumbnailUrl ?? asset.thumbnailUrl}
                    className="h-full w-full object-cover"
                    muted
                    playsInline
                    preload="metadata"
                  />
                  {/* Duration badge - bottom right */}
                  {(asset.durationSeconds || asset.duration) && (
                    <span className="absolute bottom-1 right-1 rounded bg-black/70 px-1.5 py-0.5 text-[10px] text-white">
                      {(asset.durationSeconds || asset.duration)}s
                    </span>
                  )}
                  {/* Delete button - top right */}
                  <button
                    onClick={() => handleDeleteAsset(asset.id)}
                    disabled={isDeletingId === asset.id}
                    className="absolute top-1 right-1 rounded-full bg-black/60 p-1.5 text-white hover:bg-black/80 text-xs disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="Xóa video"
                  >
                    {isDeletingId === asset.id ? '⏳' : '🗑️'}
                  </button>
                </div>
                
                {/* Text info below */}
                <div className="p-2 space-y-1">
                  <p className="line-clamp-2 text-xs text-gray-800 min-h-[2.5rem]">
                    {asset.captionOriginal || "Không có caption"}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] text-gray-500">
                      {asset.qualityLabel || "HD (No Watermark)"}
                      {asset.fileSizeBytes && ` · ${formatFileSize(asset.fileSizeBytes)}`}
                    </span>
                    <button
                      onClick={() => handleUseAssetFromCollection(asset)}
                      className="text-[10px] px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                    >
                      Dùng
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );

  const renderPostsTab = () => {
    const filteredPosts = filterStatus === 'all' ? posts : posts.filter((p) => p.status === filterStatus);

    return (
      <div className="space-y-6">
        <div className="flex gap-4">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as PostStatus | 'all')}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="published">Đã đăng</option>
            <option value="scheduled">Chờ đăng</option>
            <option value="draft">Nháp</option>
            <option value="failed">Thất bại</option>
            <option value="cancelled">Đã hủy</option>
          </select>
        </div>

        <div className="bg-white border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Nội dung</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Media</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Kênh đăng</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Thời gian</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Trạng thái</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Người tạo</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Hành động</th>
              </tr>
            </thead>
            <tbody>
              {filteredPosts.map((post) => (
                <tr key={post.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="text-sm max-w-xs truncate">{post.caption}</div>
                  </td>
                  <td className="px-4 py-3">
                    <img
                      src={post.thumbnailUrl}
                      alt="Thumbnail"
                      className="w-12 h-12 object-cover rounded"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="text-sm">{post.channels.join(', ')}</div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="text-sm">{post.scheduledTime}</div>
                  </td>
                  <td className="px-4 py-3">{getStatusBadge(post.status)}</td>
                  <td className="px-4 py-3">
                    <div className="text-sm">{post.creator}</div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button className="text-blue-600 hover:underline text-sm">Sửa</button>
                      <button 
                        onClick={() => handleCancelPost(post.id)}
                        className="text-red-600 hover:underline text-sm"
                        disabled={post.status === 'published' || post.status === 'cancelled'}
                      >
                        Huỷ
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredPosts.length === 0 && (
            <div className="text-center py-12 text-gray-500">Không có bài đăng nào</div>
          )}
        </div>
      </div>
    );
  };

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">Studio quảng cáo</h2>
        <p className="text-sm text-gray-600 mt-1">
          Quản lý ý tưởng, nội dung và lịch đăng bài cho fanpage
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex">
          {renderTabButton('dashboard', 'Dashboard')}
          {renderTabButton('collect', 'Thu thập link')}
          {renderTabButton('collection', 'Bộ sưu tầm')}
          {renderTabButton('posts', 'Quản lý bài đăng')}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'dashboard' && renderDashboardTab()}
        {activeTab === 'collect' && renderCollectTab()}
        {activeTab === 'collection' && renderCollectionTab()}
        {activeTab === 'posts' && renderPostsTab()}
      </div>
    </div>
  );
}
