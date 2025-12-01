import React, { useState } from 'react';
import { toast } from 'react-toastify';
import ChannelSelector from '../components/AdStudio/ChannelSelector';
import PostComposer, { PostData } from '../components/AdStudio/PostComposer';
import PostPreview from '../components/AdStudio/PostPreview';

const AdStudioPageV2: React.FC = () => {
  const [selectedChannelIds, setSelectedChannelIds] = useState<string[]>([]);
  const [postData, setPostData] = useState<PostData>({
    caption: '',
    language: 'la',
    postType: 'feed',
    ctaType: 'none',
    scheduleMode: 'now',
  });
  const [isSaving, setIsSaving] = useState(false);

  // Mock channels for preview (in real app, fetch from API)
  const [channels] = useState([
    { id: '1', page_name: 'Cheap Store', avatar_url: 'https://via.placeholder.com/40' },
    { id: '2', page_name: 'Beauty Shop', avatar_url: 'https://via.placeholder.com/40' },
  ]);

  const selectedChannels = channels.filter((c) => selectedChannelIds.includes(c.id));

  const handlePostSubmit = async (data: PostData) => {
    if (selectedChannelIds.length === 0) {
      toast.error('Vui lòng chọn ít nhất một kênh');
      return;
    }

    setIsSaving(true);
    try {
      // TODO: Implement actual API call
      console.log('Submitting post:', {
        ...data,
        channelIds: selectedChannelIds,
      });

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));

      toast.success(`Đã tạo bài viết cho ${selectedChannelIds.length} kênh!`);
      
      // Reset form
      setPostData({
        caption: '',
        language: 'la',
        postType: 'feed',
        ctaType: 'none',
        scheduleMode: 'now',
      });
    } catch (error: any) {
      console.error('Error creating post:', error);
      toast.error(error.message || 'Không thể tạo bài viết');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Header */}
      <header className="bg-transparent shadow-lg sticky top-0 z-30 backdrop-blur-sm">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between">
            {/* Left: Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="text-3xl">🎬</div>
              <div>
                <h1 className="text-xl font-bold text-white">Ad Studio</h1>
                <p className="text-xs text-white/80">Thu thập, quản lý video và lên lịch đăng bài</p>
              </div>
            </div>

            {/* Right: Navigation */}
            <div className="flex items-center gap-3">
              <button
                className="px-4 py-2 border-2 border-white/30 text-white rounded-lg hover:bg-white/20 transition-colors text-sm font-medium backdrop-blur-sm"
                onClick={() => (window.location.href = '/dashboard')}
              >
                🚀 Dashboard
              </button>

              <button
                className="px-4 py-2 border-2 border-white/30 text-white rounded-lg hover:bg-white/20 transition-colors text-sm font-medium backdrop-blur-sm"
                onClick={() => (window.location.href = '/settings/channels')}
              >
                📡 Quản lý kênh
              </button>

              <button
                className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-lg hover:bg-white/30 transition-colors text-sm font-semibold border border-white/30"
                onClick={() => (window.location.href = '/')}
              >
                🏠 Về Trang Chủ
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - 3 Column Layout */}
      <main className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6" style={{ minHeight: 'calc(100vh - 200px)' }}>
          {/* Left Column - Channel Selector */}
          <div className="lg:col-span-3">
            <ChannelSelector
              selectedChannelIds={selectedChannelIds}
              onSelectionChange={setSelectedChannelIds}
            />
          </div>

          {/* Middle Column - Post Composer */}
          <div className="lg:col-span-5">
            <PostComposer
              onSubmit={(data) => {
                setPostData(data);
                handlePostSubmit(data);
              }}
              isSaving={isSaving}
            />
          </div>

          {/* Right Column - Preview */}
          <div className="lg:col-span-4">
            <PostPreview postData={postData} selectedChannels={selectedChannels} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 py-6 border-t border-white/20">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-white/80">
          <p>Ad Studio V2 • Powered by React + TypeScript + Tailwind CSS</p>
        </div>
      </footer>
    </div>
  );
};

export default AdStudioPageV2;
