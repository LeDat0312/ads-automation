import React, { useState, useEffect } from 'react';
import * as SettingsAPI from '../../api/settings';
import type { PostingSettingsRow, AutoCommentTemplate } from '../../api/settings';
import { toast } from 'react-toastify';
import { PageHeader, EmptyState, Badge, StatusSwitch } from '../../components/ui';
import SpinContentModal from '../../components/SpinContentModal';
import MediaUploadCard from '../../components/MediaUploadCard';

// Delay options in minutes
const DELAY_OPTIONS = [
  { label: 'Đăng ngay', value: 0 },
  { label: '10 phút', value: 10 },
  { label: '30 phút', value: 30 },
  { label: '45 phút', value: 45 },
  { label: '1 giờ', value: 60 },
  { label: '2 giờ', value: 120 },
  { label: '6 giờ', value: 360 },
  { label: '12 giờ', value: 720 },
  { label: '24 giờ', value: 1440 },
  { label: '36 giờ', value: 2160 },
  { label: '48 giờ', value: 2880 },
  { label: '72 giờ', value: 4320 },
];

const PostingSettingsPageV2: React.FC = () => {
  const [settingsRows, setSettingsRows] = useState<PostingSettingsRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedChannelId, setSelectedChannelId] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  
  // Spin modal state
  const [spinModalOpen, setSpinModalOpen] = useState(false);
  const [activeCommentId, setActiveCommentId] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await SettingsAPI.fetchPostingSettings();
      setSettingsRows(data);
    } catch (err: any) {
      console.error('Error loading posting settings:', err);
      setError(err.response?.data?.detail || 'Không thể tải cài đặt đăng bài');
    } finally {
      setIsLoading(false);
    }
  };

  const getSettingsRow = (channelId: string): PostingSettingsRow | undefined => {
    return settingsRows.find(row => row.channel.id === channelId);
  };

  const updateSettingsRow = (channelId: string, updates: Partial<PostingSettingsRow>) => {
    setSettingsRows(prev => prev.map(row =>
      row.channel.id === channelId ? { ...row, ...updates } : row
    ));
  };

  const handleToggleAutoComment = async (channelId: string) => {
    const row = getSettingsRow(channelId);
    if (!row) return;

    const currentEnabled = row.settings?.auto_comment_enabled || false;
    const newSettings = row.settings ? {
      ...row.settings,
      auto_comment_enabled: !currentEnabled,
    } : {
      id: '',
      user_id: 0,
      channel_id: channelId,
      default_signature: undefined,
      auto_comment_enabled: true,
      auto_comment_delay_seconds: undefined,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    updateSettingsRow(channelId, { settings: newSettings });
  };

  const handleAddComment = (channelId: string) => {
    const row = getSettingsRow(channelId);
    if (!row) return;

    const newComment: AutoCommentTemplate = {
      id: `temp-${Date.now()}`,
      user_id: 0,
      channel_id: channelId,
      content: '',
      media_url: undefined,
      schedule_type: 'IMMEDIATE',
      delay_minutes: 0,
      is_active: true,
      sort_order: row.auto_comments.length,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    updateSettingsRow(channelId, {
      auto_comments: [...row.auto_comments, newComment]
    });
  };

  const handleUpdateComment = (
    channelId: string,
    commentId: string,
    updates: Partial<AutoCommentTemplate>
  ) => {
    const row = getSettingsRow(channelId);
    if (!row) return;

    const updatedComments = row.auto_comments.map(c =>
      c.id === commentId ? { ...c, ...updates } : c
    );

    updateSettingsRow(channelId, { auto_comments: updatedComments });
  };

  const handleDeleteComment = (channelId: string, commentId: string) => {
    const row = getSettingsRow(channelId);
    if (!row) return;

    const updatedComments = row.auto_comments.filter(c => c.id !== commentId);
    updateSettingsRow(channelId, { auto_comments: updatedComments });
  };

  const handleMediaUpload = async (channelId: string, commentId: string, file: File): Promise<string> => {
    // TODO: Implement actual upload to backend
    // For now, create a local URL
    const url = URL.createObjectURL(file);
    handleUpdateComment(channelId, commentId, { media_url: url });
    return url;
  };

  const handleMediaRemove = (channelId: string, commentId: string) => {
    handleUpdateComment(channelId, commentId, { media_url: undefined });
  };

  const handleOpenSpinModal = (channelId: string, commentId: string) => {
    setActiveCommentId(commentId);
    setSpinModalOpen(true);
  };

  const handleInsertSpin = (text: string) => {
    if (!selectedChannelId || !activeCommentId) return;

    const row = getSettingsRow(selectedChannelId);
    if (!row) return;

    const comment = row.auto_comments.find(c => c.id === activeCommentId);
    if (!comment) return;

    // Insert at end of current content
    const newContent = comment.content ? `${comment.content} ${text}` : text;
    handleUpdateComment(selectedChannelId, activeCommentId, { content: newContent });
  };

  const handleSaveChannel = async (channelId: string) => {
    const row = getSettingsRow(channelId);
    if (!row) return;

    setIsSaving(true);
    setError(null);
    try {
      const payload = {
        default_signature: row.settings?.default_signature || undefined,
        auto_comment_enabled: row.settings?.auto_comment_enabled || false,
        auto_comment_delay_seconds: row.settings?.auto_comment_delay_seconds || undefined,
        auto_comments: row.auto_comments.map(template => ({
          id: template.id.startsWith('temp-') ? undefined : template.id,
          content: template.content,
          media_url: template.media_url || undefined,
          schedule_type: template.schedule_type,
          delay_minutes: template.delay_minutes || 0,
          is_active: template.is_active,
          sort_order: template.sort_order,
        })),
      };

      const updated = await SettingsAPI.savePostingSettings(channelId, payload);
      setSettingsRows(prev => prev.map(r =>
        r.channel.id === channelId ? updated : r
      ));
      toast.success(`Đã lưu cấu hình bình luận cho ${row.channel.page_name}`);
    } catch (err: any) {
      console.error('Error saving posting settings:', err);
      toast.error(err.response?.data?.detail || 'Không thể lưu cài đặt');
    } finally {
      setIsSaving(false);
    }
  };

  const selectedRow = selectedChannelId ? getSettingsRow(selectedChannelId) : null;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Cài đặt đăng bài & Bình luận"
        subtitle="Cấu hình chữ ký và bình luận tự động cho từng kênh"
      />

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
          <span className="text-red-800">{error}</span>
          <button className="text-red-600 hover:text-red-800" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Đang tải cài đặt...</p>
        </div>
      ) : settingsRows.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200">
          <EmptyState
            icon="💬"
            title="Chưa có kênh nào"
            description="Kết nối Fanpage trước để cấu hình bình luận tự động."
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Channels List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <h3 className="font-semibold text-gray-900">Danh sách kênh</h3>
                <p className="text-sm text-gray-500 mt-1">Chọn kênh để cấu hình</p>
              </div>
              <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
                {settingsRows.map(row => {
                  const channel = row.channel;
                  const autoCommentEnabled = row.settings?.auto_comment_enabled || false;
                  const hasTemplates = row.auto_comments.length > 0;
                  const isSelected = selectedChannelId === channel.id;

                  return (
                    <button
                      key={channel.id}
                      onClick={() => setSelectedChannelId(channel.id)}
                      className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                        isSelected ? 'bg-indigo-50 border-l-4 border-indigo-600' : ''
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <img
                          src={channel.avatar_url || 'https://via.placeholder.com/40'}
                          alt={channel.page_name}
                          className="w-10 h-10 rounded-full"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-900 truncate">{channel.page_name}</p>
                          <div className="flex items-center gap-2 mt-1">
                            {autoCommentEnabled && hasTemplates ? (
                              <Badge variant="success" size="sm">Đang hoạt động</Badge>
                            ) : hasTemplates ? (
                              <Badge variant="warning" size="sm">Đã tắt</Badge>
                            ) : (
                              <Badge variant="neutral" size="sm">Chưa cấu hình</Badge>
                            )}
                          </div>
                        </div>
                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Configuration Panel */}
          <div className="lg:col-span-2">
            {!selectedRow ? (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <div className="text-6xl mb-4">👈</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Chọn một kênh</h3>
                <p className="text-gray-500">Chọn kênh từ danh sách bên trái để bắt đầu cấu hình bình luận tự động.</p>
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-gray-200">
                {/* Channel Header */}
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <img
                        src={selectedRow.channel.avatar_url || 'https://via.placeholder.com/48'}
                        alt={selectedRow.channel.page_name}
                        className="w-12 h-12 rounded-full"
                      />
                      <div>
                        <h3 className="font-semibold text-gray-900">{selectedRow.channel.page_name}</h3>
                        <p className="text-sm text-gray-500">ID: {selectedRow.channel.page_id}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">
                        {selectedRow.settings?.auto_comment_enabled ? 'Bật' : 'Tắt'} auto comment
                      </span>
                      <StatusSwitch
                        checked={selectedRow.settings?.auto_comment_enabled || false}
                        onChange={() => handleToggleAutoComment(selectedRow.channel.id)}
                        labelOn=""
                        labelOff=""
                      />
                    </div>
                  </div>
                </div>

                {/* Comment Templates */}
                <div className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-gray-900">Mẫu bình luận</h4>
                    <button
                      onClick={() => handleAddComment(selectedRow.channel.id)}
                      className="flex items-center gap-1 px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Thêm mẫu
                    </button>
                  </div>

                  {selectedRow.auto_comments.length === 0 ? (
                    <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
                      <div className="text-4xl mb-2">💬</div>
                      <p className="text-gray-500 mb-3">Chưa có mẫu bình luận nào</p>
                      <button
                        onClick={() => handleAddComment(selectedRow.channel.id)}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                      >
                        + Thêm mẫu đầu tiên
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {selectedRow.auto_comments.map((comment, index) => (
                        <div
                          key={comment.id}
                          className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                        >
                          {/* Header */}
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-gray-700">Mẫu #{index + 1}</span>
                              <StatusSwitch
                                checked={comment.is_active}
                                onChange={(checked) => handleUpdateComment(selectedRow.channel.id, comment.id, { is_active: checked })}
                                labelOn=""
                                labelOff=""
                              />
                            </div>
                            <button
                              onClick={() => handleDeleteComment(selectedRow.channel.id, comment.id)}
                              className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                              title="Xoá mẫu"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </div>

                          <div className="space-y-4">
                            {/* Content */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">Nội dung</label>
                              <textarea
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                                rows={3}
                                placeholder="Nhập nội dung bình luận..."
                                value={comment.content}
                                onChange={(e) => handleUpdateComment(selectedRow.channel.id, comment.id, { content: e.target.value })}
                              />
                              <div className="flex items-center justify-between mt-1">
                                <p className="text-xs text-gray-500 flex items-center gap-1">
                                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                                  </svg>
                                  Dùng {'{a|b|c}'} để random nội dung (Spin)
                                </p>
                                <button
                                  onClick={() => handleOpenSpinModal(selectedRow.channel.id, comment.id)}
                                  className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                                >
                                  Hướng dẫn Spin →
                                </button>
                              </div>
                            </div>

                            {/* Media Upload */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">Media (tuỳ chọn)</label>
                              <MediaUploadCard
                                mediaUrl={comment.media_url}
                                onUpload={(file) => handleMediaUpload(selectedRow.channel.id, comment.id, file)}
                                onRemove={() => handleMediaRemove(selectedRow.channel.id, comment.id)}
                                accept="image/*,video/mp4"
                                maxSizeMB={50}
                              />
                            </div>

                            {/* Delay */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">Thời gian đăng</label>
                              <select
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                                value={comment.delay_minutes || 0}
                                onChange={(e) => handleUpdateComment(selectedRow.channel.id, comment.id, { delay_minutes: parseInt(e.target.value) })}
                              >
                                {DELAY_OPTIONS.map(option => (
                                  <option key={option.value} value={option.value}>
                                    {option.label}
                                  </option>
                                ))}
                              </select>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Save Button */}
                <div className="p-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-gray-500">
                      {selectedRow.auto_comments.length} mẫu bình luận
                    </p>
                    <button
                      onClick={() => handleSaveChannel(selectedRow.channel.id)}
                      disabled={isSaving}
                      className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                    >
                      {isSaving ? (
                        <>
                          <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          Đang lưu...
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Lưu cấu hình
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Spin Content Modal */}
      <SpinContentModal
        open={spinModalOpen}
        onClose={() => {
          setSpinModalOpen(false);
          setActiveCommentId(null);
        }}
        onInsert={handleInsertSpin}
      />
    </div>
  );
};

export default PostingSettingsPageV2;
