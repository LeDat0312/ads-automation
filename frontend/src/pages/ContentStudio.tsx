/**
 * Content Studio - Main Page Component
 * Trang chính của module Content Studio với 4 tabs
 */

import React, { useState } from 'react';
import SearchPanel from '../components/ContentStudio/SearchPanel';
import AdCardList from '../components/ContentStudio/AdCardList';
import AiEditor from '../components/ContentStudio/AiEditor';
import ScheduleForm from '../components/ContentStudio/ScheduleForm';
import PostManagement from '../components/ContentStudio/PostManagement';
import {
  ContentSource,
  ContentVariant,
  ContentSourceType,
  ScheduleType
} from '../types/contentStudio';
import {
  searchContent,
  fetchFromUrls,
  uploadMedia,
  addToCollection,
  createContentVariant,
  schedulePosts
} from '../api/contentStudio';

type TabType = 'search' | 'edit' | 'schedule' | 'manage';

const ContentStudioPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('search');
  const [contents, setContents] = useState<ContentSource[]>([]);
  const [currentVariant, setCurrentVariant] = useState<ContentVariant | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Tab 1: Search & Save
  const handleSearch = async (query: string, sourceType?: ContentSourceType) => {
    setIsLoading(true);
    try {
      const result = await searchContent({ query, sourceType, page: 1, pageSize: 20 });
      setContents(result.items);
    } catch (error) {
      console.error('Search error:', error);
      alert('Lỗi khi tìm kiếm. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFetchUrls = async (urls: string[]) => {
    setIsLoading(true);
    try {
      const items = await fetchFromUrls(urls);
      setContents([...items, ...contents]);
      alert(`Đã lấy ${items.length} nội dung từ ${urls.length} link`);
    } catch (error) {
      console.error('Fetch URLs error:', error);
      alert('Lỗi khi lấy dữ liệu từ link. Vui lòng kiểm tra lại.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadFiles = async (files: File[]) => {
    setIsLoading(true);
    try {
      const result = await uploadMedia(files);
      setContents([...result.sources, ...contents]);
      alert(`Đã upload ${result.sources.length}/${files.length} file`);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Lỗi khi upload file. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToCollection = async (content: ContentSource) => {
    try {
      await addToCollection({ sourceIds: [content.id] });
      alert('Đã thêm vào bộ sưu tập!');
    } catch (error) {
      console.error('Add to collection error:', error);
      alert('Lỗi khi thêm vào bộ sưu tập.');
    }
  };

  const handleViewDetail = (content: ContentSource) => {
    // Open modal or navigate to detail page
    console.log('View detail:', content);
  };

  const handleDownload = (content: ContentSource) => {
    if (content.media[0]) {
      window.open(content.media[0].url, '_blank');
    }
  };

  // Tab 2: AI Edit
  const handleSaveVariant = async (updatedData: Partial<ContentVariant>) => {
    if (!currentVariant) return;

    setIsLoading(true);
    try {
      const saved = await createContentVariant({
        sourceId: currentVariant.sourceId,
        title: updatedData.title || currentVariant.title,
        caption: updatedData.caption || currentVariant.caption,
        captionLao: updatedData.captionLao || currentVariant.captionLao,
        hashtags: updatedData.hashtags || currentVariant.hashtags,
        callToAction: updatedData.callToAction
      });
      setCurrentVariant(saved);
      setActiveTab('schedule');
      alert('Đã lưu! Chuyển sang lên lịch đăng.');
    } catch (error) {
      console.error('Save variant error:', error);
      alert('Lỗi khi lưu nội dung.');
    } finally {
      setIsLoading(false);
    }
  };

  // Tab 3: Schedule
  const handleSchedule = async (
    pageIds: string[],
    scheduleType: ScheduleType,
    fixedTime?: string,
    randomRangeMinutes?: number
  ) => {
    if (!currentVariant) return;

    setIsLoading(true);
    try {
      const result = await schedulePosts({
        contentVariantId: currentVariant.id,
        pageIds,
        scheduleType,
        fixedTime,
        randomRangeMinutes
      });

      if (result.success) {
        alert(`Đã lên lịch ${result.scheduledPosts.length} bài đăng!`);
        setActiveTab('manage');
      } else {
        alert(`Lên lịch một phần thành công. ${result.errors?.length || 0} lỗi.`);
      }
    } catch (error) {
      console.error('Schedule error:', error);
      alert('Lỗi khi lên lịch đăng bài.');
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: 'search' as TabType, label: '🔍 Tìm & lưu quảng cáo', icon: '🔍' },
    { id: 'edit' as TabType, label: '✏️ Biên tập & dịch AI', icon: '✏️' },
    { id: 'schedule' as TabType, label: '📅 Lên lịch đăng', icon: '📅' },
    { id: 'manage' as TabType, label: '📊 Quản lý bài đăng', icon: '📊' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            🎬 Content Studio
          </h1>
          <p className="text-gray-600 mt-2">
            Tìm kiếm, biên tập và lên lịch đăng bài tự động cho fanpage
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-medium transition-colors relative ${
                  activeTab === tab.id
                    ? 'text-blue-600 bg-gray-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {tab.label}
                {activeTab === tab.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'search' && (
          <div className="space-y-6">
            <SearchPanel
              onSearch={handleSearch}
              onFetchUrls={handleFetchUrls}
              onUploadFiles={handleUploadFiles}
              isLoading={isLoading}
            />
            <AdCardList
              contents={contents}
              isLoading={isLoading}
              onViewDetail={handleViewDetail}
              onDownload={handleDownload}
              onAddToCollection={handleAddToCollection}
            />
          </div>
        )}

        {activeTab === 'edit' && (
          <AiEditor
            variant={currentVariant}
            onSave={handleSaveVariant}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'schedule' && (
          <ScheduleForm
            variant={currentVariant}
            onSchedule={handleSchedule}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'manage' && <PostManagement />}
      </div>
    </div>
  );
};

export default ContentStudioPage;
