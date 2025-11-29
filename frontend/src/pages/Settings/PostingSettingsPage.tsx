import React, { useState, useEffect } from 'react';
import * as SettingsAPI from '../../api/settings';
import type { PostingSettingsRow, AutoCommentTemplate } from '../../api/settings';

const PostingSettingsPage: React.FC = () => {
  const [settingsRows, setSettingsRows] = useState<PostingSettingsRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingChannelId, setEditingChannelId] = useState<string | null>(null);

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

  // Get settings row for a channel
  const getSettingsRow = (channelId: string): PostingSettingsRow | undefined => {
    return settingsRows.find(row => row.channel.id === channelId);
  };

  // Update local state for a channel's settings
  const updateSettingsRow = (channelId: string, updates: Partial<PostingSettingsRow>) => {
    setSettingsRows(prev => prev.map(row => 
      row.channel.id === channelId ? { ...row, ...updates } : row
    ));
  };

  const handleToggleSignature = async (channelId: string) => {
    const row = getSettingsRow(channelId);
    if (!row) return;

    // Create settings if doesn't exist, or update existing
    const newSettings: PostingSettingsRow['settings'] = row.settings ? {
      ...row.settings,
      default_signature: row.settings.default_signature ? undefined : 'Chữ ký mặc định',
    } : null;

    updateSettingsRow(channelId, { settings: newSettings });
    // Auto-save toggle changes
    await handleSaveChannel(channelId);
  };

  const handleToggleAutoComment = async (channelId: string) => {
    const row = getSettingsRow(channelId);
    if (!row) return;

    const currentEnabled = row.settings?.auto_comment_enabled || false;
    // Create settings if doesn't exist, or update existing
    const newSettings: PostingSettingsRow['settings'] = row.settings ? {
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
    // Auto-save toggle changes
    await handleSaveChannel(channelId);
  };

  const handleAddComment = (channelId: string) => {
    const row = getSettingsRow(channelId);
    if (!row) return;

    const newComment: AutoCommentTemplate = {
      id: `temp-${Date.now()}`, // Temporary ID
      user_id: 0,
      channel_id: channelId,
      content: '',
      schedule_type: 'IMMEDIATE',
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

  // Save settings for a specific channel
  const handleSaveChannel = async (channelId: string) => {
    const row = getSettingsRow(channelId);
    if (!row) return;

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
          delay_minutes: template.delay_minutes || undefined,
          is_active: template.is_active,
          sort_order: template.sort_order,
        })),
      };

      const updated = await SettingsAPI.savePostingSettings(channelId, payload);
      
      // Update local state with response from server
      setSettingsRows(prev => prev.map(r => 
        r.channel.id === channelId ? updated : r
      ));
    } catch (err: any) {
      console.error('Error saving posting settings:', err);
      setError(err.response?.data?.detail || 'Không thể lưu cài đặt');
      throw err;
    }
  };

  const renderBulkCommentModal = (channelId: string) => {
    if (editingChannelId !== channelId) return null;

    const row = getSettingsRow(channelId);
    if (!row) return null;

    const channel = row.channel;
    const comments = row.auto_comments || [];

    return (
      <div className="modal modal-open">
        <div className="modal-box w-11/12 max-w-5xl">
          <h3 className="font-bold text-lg mb-4">Bình luận hàng loạt - {channel.page_name}</h3>
          
          <div className="space-y-4 max-h-[60vh] overflow-y-auto">
            {comments.map((comment) => (
              <div
                key={comment.id}
                className="border border-gray-200 rounded-lg p-4 bg-gray-50"
              >
                <div className="grid grid-cols-12 gap-4 items-start">
                  {/* Content Column */}
                  <div className="col-span-5">
                    <label className="label">
                      <span className="label-text font-semibold">Nội dung</span>
                    </label>
                    <textarea
                      className="textarea textarea-bordered w-full h-24"
                      placeholder="Nhập nội dung bình luận..."
                      value={comment.content}
                      onChange={(e) =>
                        handleUpdateComment(channelId, comment.id, {
                          content: e.target.value,
                        })
                      }
                    />
                  </div>

                  {/* Media Column */}
                  <div className="col-span-3">
                    <label className="label">
                      <span className="label-text font-semibold">Media</span>
                    </label>
                    <div className="border border-gray-300 rounded-lg p-4 text-center text-gray-500 text-sm">
                      {comment.media_url ? (
                        <img
                          src={comment.media_url}
                          alt="Media"
                          className="w-full h-20 object-cover rounded"
                        />
                      ) : (
                        <div>
                          <div className="text-2xl mb-2">🖼️</div>
                          <div>Không có media</div>
                          <button className="btn btn-sm btn-ghost mt-2">
                            Tải lên
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Time Column */}
                  <div className="col-span-3">
                    <label className="label">
                      <span className="label-text font-semibold">Thời gian</span>
                    </label>
                    <select
                      className="select select-bordered w-full"
                      value={comment.schedule_type}
                      onChange={(e) =>
                        handleUpdateComment(channelId, comment.id, {
                          schedule_type: e.target.value,
                        })
                      }
                    >
                      <option value="IMMEDIATE">Đăng ngay</option>
                      <option value="AFTER_X_MINUTES">Sau X phút</option>
                      <option value="DELAYED">Đăng sau</option>
                      <option value="CUSTOM">Chọn giờ cụ thể</option>
                    </select>
                    {(comment.schedule_type === 'AFTER_X_MINUTES' || comment.schedule_type === 'DELAYED') && (
                      <input
                        type="number"
                        className="input input-bordered input-sm w-full mt-2"
                        placeholder="Phút (ví dụ: 5)"
                        value={comment.delay_minutes || ''}
                        onChange={(e) =>
                          handleUpdateComment(channelId, comment.id, {
                            delay_minutes: parseInt(e.target.value) || undefined,
                          })
                        }
                      />
                    )}
                  </div>

                  {/* Action Column */}
                  <div className="col-span-1">
                    <button
                      className="btn btn-ghost btn-sm btn-square text-red-600"
                      onClick={() => handleDeleteComment(channelId, comment.id)}
                      title="Xóa"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="modal-action">
            <button
              className="btn btn-ghost"
              onClick={() => setEditingChannelId(null)}
            >
              Đóng
            </button>
            <button
              className="btn btn-primary"
              onClick={() => {
                handleAddComment(channelId);
              }}
            >
              ➕ Thêm mẫu
            </button>
            <button
              className="btn btn-primary"
              onClick={async () => {
                try {
                  await handleSaveChannel(channelId);
                  setEditingChannelId(null);
                } catch (err) {
                  // Error already shown
                }
              }}
            >
              💾 Lưu
            </button>
          </div>

          {/* Tip */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
            💡 <strong>Mẹo:</strong> Đa dạng hóa nội dung của bạn với Chức năng Spin.
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Cài đặt đăng bài & Bình luận hàng loạt
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Cấu hình chữ ký và bình luận tự động cho từng kênh
          </p>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <button className="btn btn-sm btn-ghost" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Channels Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="font-semibold text-gray-900">Kênh</th>
                <th className="font-semibold text-gray-900 text-center">Chữ ký</th>
                <th className="font-semibold text-gray-900 text-center">
                  Bình luận hàng loạt
                </th>
                <th className="font-semibold text-gray-900">Hành động</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={4} className="text-center py-12">
                    <div className="loading loading-spinner loading-lg text-indigo-600"></div>
                  </td>
                </tr>
              ) : settingsRows.length === 0 ? (
                <tr>
                  <td colSpan={4} className="text-center py-12 text-gray-500">
                    Chưa có kênh nào
                  </td>
                </tr>
              ) : (
                settingsRows.map((row) => {
                  const channel = row.channel;
                  const hasSignature = !!row.settings?.default_signature;
                  const autoCommentEnabled = row.settings?.auto_comment_enabled || false;
                  
                  return (
                    <tr key={channel.id} className="hover:bg-gray-50">
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="avatar">
                            <div className="w-10 h-10 rounded-full">
                              <img
                                src={channel.avatar_url || 'https://via.placeholder.com/40'}
                                alt={channel.page_name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{channel.page_name}</div>
                            <div className="text-xs text-gray-500">{channel.page_id}</div>
                          </div>
                        </div>
                      </td>
                      <td className="text-center">
                        <input
                          type="checkbox"
                          className="checkbox checkbox-primary"
                          checked={hasSignature}
                          onChange={() => handleToggleSignature(channel.id)}
                        />
                      </td>
                      <td className="text-center">
                        <input
                          type="checkbox"
                          className="checkbox checkbox-primary"
                          checked={autoCommentEnabled}
                          onChange={() => handleToggleAutoComment(channel.id)}
                        />
                      </td>
                      <td>
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => setEditingChannelId(channel.id)}
                        >
                          Sửa
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modals */}
      {settingsRows.map((row) => renderBulkCommentModal(row.channel.id))}
    </div>
  );
};

export default PostingSettingsPage;

