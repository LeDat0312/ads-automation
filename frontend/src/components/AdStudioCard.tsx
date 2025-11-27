import React, { useState } from 'react';

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
  captionOriginal: string;
  duration?: number;
  hashtags?: string[];
  note?: string;
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

type SchedulePayload = {
  assetId: string;
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
// API STUBS
// ============================================================================

/**
 * QUAN TRỌNG: Hàm này gọi backend để lấy video + caption từ TikTok.
 * Backend sẽ dùng Apify API key đã được admin cấu hình tại /settings.
 * Frontend KHÔNG BAO GIỜ biết hoặc lưu trữ Apify API key.
 */
async function fetchTiktokAsset(url: string, note?: string): Promise<Asset> {
  // TODO: Implement call to POST /api/tiktok/scrape
  // Backend sẽ:
  // 1. Lấy Apify API key từ DB (admin đã cấu hình tại /settings)
  // 2. Gọi TikTok Data Extractor actor trên Apify
  // 3. Parse kết quả thành Asset object
  // 4. Trả về JSON Asset
  
  console.log('[fetchTiktokAsset] Calling backend with:', { url, note });
  
  // Mock data cho development
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: `tiktok-${Date.now()}`,
        platform: 'tiktok',
        sourceUrl: url,
        videoUrl: 'https://example.com/mock-video.mp4',
        thumbnailUrl: 'https://via.placeholder.com/300x400',
        captionOriginal: 'สวัสดีค่ะ! วันนี้เรามาแชร์เคล็ดลับดูแลผิวกันนะคะ 🌸✨\n\n#skincare #beauty #thailand',
        duration: 45,
        hashtags: ['skincare', 'beauty', 'thailand'],
        note,
      });
    }, 1500);
  });
}

/**
 * QUAN TRỌNG: Hàm này gọi backend để lấy video + caption từ Facebook.
 * Backend sẽ dùng Apify API key đã được admin cấu hình tại /settings.
 * Frontend KHÔNG BAO GIỜ biết hoặc lưu trữ Apify API key.
 */
async function fetchFacebookAsset(url: string, note?: string): Promise<Asset> {
  // TODO: Implement call to POST /api/facebook/scrape
  // Tương tự TikTok, backend sẽ dùng Apify actor cho Facebook
  
  console.log('[fetchFacebookAsset] Calling backend with:', { url, note });
  
  // Mock placeholder
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: `facebook-${Date.now()}`,
        platform: 'facebook',
        sourceUrl: url,
        videoUrl: 'https://example.com/mock-fb-video.mp4',
        thumbnailUrl: 'https://via.placeholder.com/300x400',
        captionOriginal: 'Check out this amazing product! 🎉',
        note,
      });
    }, 1500);
  });
}

/**
 * Gọi backend để lên lịch đăng bài
 */
async function schedulePost(payload: SchedulePayload): Promise<void> {
  // TODO: Implement call to POST /api/posts/schedule
  console.log('[schedulePost] Calling backend with:', payload);
  
  return new Promise((resolve) => {
    setTimeout(() => {
      alert('Đã lưu vào lịch đăng thành công!');
      resolve();
    }, 1000);
  });
}

// ============================================================================
// MOCK DATA
// ============================================================================

function getMockDashboardData(range: string): DashboardStats {
  return {
    totalPosts: 127,
    publishedPosts: 89,
    scheduledPosts: 15,
    draftPosts: 18,
    failedPosts: 5,
  };
}

const mockPosts: Post[] = [
  {
    id: '1',
    caption: 'Khuyến mãi lớn cuối năm! Giảm giá 50%...',
    thumbnailUrl: 'https://via.placeholder.com/150',
    channels: ['Facebook', 'TikTok'],
    scheduledTime: '2025-11-28 14:30',
    status: 'scheduled',
    creator: 'Admin',
  },
  {
    id: '2',
    caption: 'Sản phẩm mới vừa về! Đặt hàng ngay...',
    thumbnailUrl: 'https://via.placeholder.com/150',
    channels: ['Facebook'],
    scheduledTime: '2025-11-27 10:00',
    status: 'published',
    creator: 'Marketing Team',
  },
];

const mockFanpages = [
  { id: 'page1', name: 'Fanpage A - Skincare' },
  { id: 'page2', name: 'Fanpage B - Fashion' },
  { id: 'page3', name: 'Fanpage C - Food' },
];

const ctaOptions = [
  'Nhắn tin ngay',
  'Gọi tư vấn',
  'Đặt hàng ngay',
  'Tìm hiểu thêm',
  'Đăng ký ngay',
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
  
  // Tab 2: Thu thập link - Step 1
  const [inputUrl, setInputUrl] = useState('');
  const [detectedPlatform, setDetectedPlatform] = useState<AssetPlatform>('other');
  const [isLoadingAsset, setIsLoadingAsset] = useState(false);
  const [currentStep, setCurrentStep] = useState<1 | 2>(1); // Step trong Tab 2
  const [editedCaption, setEditedCaption] = useState('');
  const [videoSource, setVideoSource] = useState<'original' | 'upload'>('original');
  const [customVideoFile, setCustomVideoFile] = useState<File | null>(null);
  
  // Tab 2: Step 2 - Publish form
  const [publishForm, setPublishForm] = useState({
    caption: '',
    language: 'la' as Language,
    ctaText: 'Nhắn tin ngay',
    targetUrl: '',
    pageIds: [] as string[],
    scheduleMode: 'NOW' as ScheduleMode,
    scheduleTime: '',
    thumbnailSource: 'FRAME' as ThumbnailSource,
    thumbnailFile: null as File | null,
  });
  
  // Tab 4: Posts management
  const [posts, setPosts] = useState<Post[]>(mockPosts);
  const [filterStatus, setFilterStatus] = useState<PostStatus | 'all'>('all');
  
  // Dashboard
  const [dashboardRange, setDashboardRange] = useState('7days');
  const dashboardStats = getMockDashboardData(dashboardRange);

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
      alert('Vui lòng nhập URL');
      return;
    }

    setIsLoadingAsset(true);
    try {
      let asset: Asset;
      
      if (detectedPlatform === 'tiktok') {
        asset = await fetchTiktokAsset(inputUrl);
      } else if (detectedPlatform === 'facebook') {
        asset = await fetchFacebookAsset(inputUrl);
      } else {
        alert('Nền tảng không được hỗ trợ');
        return;
      }

      setSelectedAsset(asset);
      setEditedCaption(asset.captionOriginal);
      setAssets((prev) => [...prev, asset]);
    } catch (error) {
      console.error('Error fetching asset:', error);
      alert('Lỗi khi lấy video. Vui lòng thử lại.');
    } finally {
      setIsLoadingAsset(false);
    }
  };

  const handleContinueToStep2 = () => {
    if (!selectedAsset) {
      alert('Vui lòng lấy video trước');
      return;
    }
    setCurrentStep(2);
    // Pre-fill caption vào form
    setPublishForm((prev) => ({ ...prev, caption: editedCaption }));
  };

  const handleSchedulePost = async () => {
    if (!selectedAsset) return;
    if (publishForm.pageIds.length === 0) {
      alert('Vui lòng chọn ít nhất 1 fanpage');
      return;
    }

    const payload: SchedulePayload = {
      assetId: selectedAsset.id,
      caption: publishForm.caption,
      language: publishForm.language,
      ctaText: publishForm.ctaText,
      targetUrl: publishForm.targetUrl,
      pageIds: publishForm.pageIds,
      scheduleMode: publishForm.scheduleMode,
      scheduleTime: publishForm.scheduleTime,
      thumbnailSource: publishForm.thumbnailSource,
      thumbnailFile: publishForm.thumbnailFile || undefined,
      videoUrl: videoSource === 'original' ? selectedAsset.videoUrl : undefined,
      customVideoFile: customVideoFile || undefined,
    };

    await schedulePost(payload);
    
    // Reset form và chuyển tab
    setCurrentStep(1);
    setSelectedAsset(null);
    setInputUrl('');
    setEditedCaption('');
    setCustomVideoFile(null);
    setPublishForm({
      caption: '',
      language: 'la',
      ctaText: 'Nhắn tin ngay',
      targetUrl: '',
      pageIds: [],
      scheduleMode: 'NOW',
      scheduleTime: '',
      thumbnailSource: 'FRAME',
      thumbnailFile: null,
    });
    setActiveTab('posts');
  };

  const handleUseAssetFromCollection = (asset: Asset) => {
    setSelectedAsset(asset);
    setEditedCaption(asset.captionOriginal);
    setActiveTab('collect');
    setCurrentStep(2);
    setPublishForm((prev) => ({ ...prev, caption: asset.captionOriginal }));
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

      {/* Số liệu tổng quan */}
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

      {/* Lịch đăng 7 ngày tới */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Lịch đăng trong 7 ngày tới</h3>
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
            {mockPosts.filter((p) => p.status === 'scheduled').map((post) => (
              <tr key={post.id} className="border-t">
                <td className="px-4 py-3 text-sm">{post.scheduledTime}</td>
                <td className="px-4 py-3 text-sm">{post.caption.substring(0, 50)}...</td>
                <td className="px-4 py-3 text-sm">{post.channels.join(', ')}</td>
                <td className="px-4 py-3">{getStatusBadge(post.status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderCollectTab = () => (
    <div className="space-y-6">
      {/* Stepper indicator */}
      <div className="flex items-center gap-4 mb-6">
        <div className={`flex items-center gap-2 ${currentStep === 1 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            currentStep === 1 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
          }`}>
            1
          </div>
          <span className="font-medium">Dán link & lấy video</span>
        </div>
        <div className="flex-1 h-1 bg-gray-300"></div>
        <div className={`flex items-center gap-2 ${currentStep === 2 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            currentStep === 2 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
          }`}>
            2
          </div>
          <span className="font-medium">Chọn fanpage & lịch đăng</span>
        </div>
      </div>

      {currentStep === 1 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Cột trái: Input & Caption */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Bước 1: Dán link quảng cáo</h3>
            
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

            {/* Nút lấy video */}
            <button
              onClick={handleFetchAsset}
              disabled={detectedPlatform === 'other' || isLoadingAsset}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isLoadingAsset ? 'Đang tải...' : `Lấy video ${platformInfo.label}`}
            </button>

            {selectedAsset && (
              <>
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
              </>
            )}
          </div>

          {/* Cột phải: Video Preview */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Video Asset</h3>
            
            {selectedAsset ? (
              <div className="bg-white border rounded-lg p-4 space-y-3">
                {/* Video preview */}
                <div className="aspect-[9/16] bg-gray-100 rounded-lg overflow-hidden max-w-xs mx-auto">
                  {videoSource === 'original' ? (
                    <img
                      src={selectedAsset.thumbnailUrl}
                      alt="Video thumbnail"
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

                <div className="text-sm text-gray-600 text-center">
                  Chất lượng: HD (No logo)
                </div>

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

                <button
                  onClick={handleContinueToStep2}
                  className="w-full px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700"
                >
                  Tiếp tục: Chọn fanpage & lịch đăng →
                </button>
              </div>
            ) : (
              <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center text-gray-500">
                Dán link và lấy video để xem preview
              </div>
            )}
          </div>
        </div>
      )}

      {currentStep === 2 && selectedAsset && (
        <div className="space-y-6">
          <button
            onClick={() => setCurrentStep(1)}
            className="text-blue-600 hover:underline flex items-center gap-2"
          >
            ← Quay lại Bước 1
          </button>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Form bên trái */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Bước 2: Cấu hình đăng bài</h3>

              {/* Caption */}
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
                <div className="space-y-2 max-h-40 overflow-y-auto border rounded-lg p-3">
                  {mockFanpages.map((page) => (
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

              {/* CTA */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Call-to-Action</label>
                <select
                  value={publishForm.ctaText}
                  onChange={(e) => setPublishForm({ ...publishForm, ctaText: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  {ctaOptions.map((cta) => (
                    <option key={cta} value={cta}>
                      {cta}
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

            {/* Preview bên phải */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Xem trước</h3>
              <div className="bg-white border rounded-lg p-4">
                <div className="aspect-[9/16] bg-gray-100 rounded-lg overflow-hidden max-w-xs mx-auto mb-4">
                  <img
                    src={selectedAsset.thumbnailUrl}
                    alt="Preview"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="text-sm text-gray-700 whitespace-pre-wrap">
                  {publishForm.caption || editedCaption}
                </div>
                <div className="mt-4 pt-4 border-t">
                  <div className="text-xs text-gray-500">
                    <div>📍 Fanpage: {publishForm.pageIds.length} được chọn</div>
                    <div>⏰ Lịch: {publishForm.scheduleMode === 'NOW' ? 'Đăng ngay' : publishForm.scheduleMode === 'RANDOM_2H' ? 'Ngẫu nhiên 2h' : publishForm.scheduleTime}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {assets.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            Chưa có asset nào. Hãy thu thập video từ tab "Thu thập link".
          </div>
        ) : (
          assets.map((asset) => (
            <div key={asset.id} className="bg-white border rounded-lg p-4 space-y-3">
              <div className="aspect-[9/16] bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={asset.thumbnailUrl}
                  alt="Asset thumbnail"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  {getPlatformInfo(asset.platform).icon}
                  <span className="text-xs font-medium">{getPlatformInfo(asset.platform).label}</span>
                </div>
                <div className="text-sm text-gray-700 line-clamp-3">
                  {asset.captionOriginal}
                </div>
                {asset.note && (
                  <div className="text-xs text-gray-500 italic">Note: {asset.note}</div>
                )}
                <button
                  onClick={() => handleUseAssetFromCollection(asset)}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
                >
                  Dùng để tạo bài đăng
                </button>
              </div>
            </div>
          ))
        )}
      </div>
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
                      <button className="text-red-600 hover:underline text-sm">Huỷ</button>
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
