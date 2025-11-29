import React, { useState, useEffect } from 'react';

// Types
interface Channel {
  id: string;
  name: string;
  pageId: string;
  avatarUrl?: string;
}

interface BulkComment {
  id: string;
  content: string;
  mediaUrl?: string;
  delayMinutes?: number;
  sendTimeMode: 'IMMEDIATELY' | 'AFTER_POST' | 'AT_SCHEDULED_TIME';
}

interface PostingConfig {
  shareToStory: boolean;
  commentsByChannel: Record<string, BulkComment[]>;
}

// Mock data
const mockChannels: Channel[] = [
  {
    id: '1',
    name: 'Fanpage Mỹ Phẩm ABC',
    pageId: '123456789',
    avatarUrl: 'https://via.placeholder.com/40',
  },
  {
    id: '2',
    name: 'Shop Thời Trang XYZ',
    pageId: '987654321',
    avatarUrl: 'https://via.placeholder.com/40',
  },
];

const PostingSettingsPage: React.FC = () => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [config, setConfig] = useState<PostingConfig>({
    shareToStory: false,
    commentsByChannel: {},
  });
  const [isLoading, setIsLoading] = useState(true);
  const [editingChannelId, setEditingChannelId] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with real API calls
      // const [channelsData, configData] = await Promise.all([
      //   fetchChannels(),
      //   fetchPostingConfig(),
      // ]);
      
      // Mock data
      await new Promise((resolve) => setTimeout(resolve, 500));
      setChannels(mockChannels);
      setConfig({
        shareToStory: false,
        commentsByChannel: {
          '1': [
            {
              id: '1',
              content: 'Cảm ơn bạn đã quan tâm! 💙',
              sendTimeMode: 'IMMEDIATELY',
            },
          ],
        },
      });
    } catch (error) {
      console.error('Error loading data:', error);
      console.error('Không thể tải dữ liệu');
      setChannels(mockChannels);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleShareToStory = () => {
    setConfig((prev) => ({ ...prev, shareToStory: !prev.shareToStory }));
  };

  const handleToggleSignature = () => {
    // TODO: Implement signature toggle
    console.log('Tính năng chữ ký đang được phát triển');
  };

  const handleToggleAutoComment = () => {
    // TODO: Implement auto comment toggle
    console.log('Tính năng bình luận hàng loạt đang được phát triển');
  };

  const handleAddComment = (channelId: string) => {
    const newComment: BulkComment = {
      id: Date.now().toString(),
      content: '',
      sendTimeMode: 'IMMEDIATELY',
    };
    setConfig((prev) => ({
      ...prev,
      commentsByChannel: {
        ...prev.commentsByChannel,
        [channelId]: [...(prev.commentsByChannel[channelId] || []), newComment],
      },
    }));
  };

  const handleUpdateComment = (
    channelId: string,
    commentId: string,
    updates: Partial<BulkComment>
  ) => {
    setConfig((prev) => ({
      ...prev,
      commentsByChannel: {
        ...prev.commentsByChannel,
        [channelId]: (prev.commentsByChannel[channelId] || []).map((c) =>
          c.id === commentId ? { ...c, ...updates } : c
        ),
      },
    }));
  };

  const handleDeleteComment = (channelId: string, commentId: string) => {
    setConfig((prev) => ({
      ...prev,
      commentsByChannel: {
        ...prev.commentsByChannel,
        [channelId]: (prev.commentsByChannel[channelId] || []).filter(
          (c) => c.id !== commentId
        ),
      },
    }));
  };

  const handleSave = async () => {
    try {
      // TODO: Call API to save config
      // await savePostingConfig(config);
      alert('Đã lưu cài đặt');
    } catch (error) {
      console.error('Error saving config:', error);
      alert('Lưu thất bại');
    }
  };

  const renderBulkCommentModal = (channel: Channel) => {
    if (editingChannelId !== channel.id) return null;

    const comments = config.commentsByChannel[channel.id] || [];

    return (
      <div className="modal modal-open">
        <div className="modal-box w-11/12 max-w-5xl">
          <h3 className="font-bold text-lg mb-4">Bình luận hàng loạt - {channel.name}</h3>
          
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
                        handleUpdateComment(channel.id, comment.id, {
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
                      {comment.mediaUrl ? (
                        <img
                          src={comment.mediaUrl}
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
                      value={comment.sendTimeMode}
                      onChange={(e) =>
                        handleUpdateComment(channel.id, comment.id, {
                          sendTimeMode: e.target.value as BulkComment['sendTimeMode'],
                        })
                      }
                    >
                      <option value="IMMEDIATELY">Đăng ngay</option>
                      <option value="AFTER_POST">Sau khi bài đăng được xuất bản</option>
                      <option value="AT_SCHEDULED_TIME">Chọn giờ cụ thể</option>
                    </select>
                    {comment.sendTimeMode === 'AFTER_POST' && (
                      <input
                        type="number"
                        className="input input-bordered input-sm w-full mt-2"
                        placeholder="Phút (ví dụ: 5)"
                        value={comment.delayMinutes || ''}
                        onChange={(e) =>
                          handleUpdateComment(channel.id, comment.id, {
                            delayMinutes: parseInt(e.target.value) || undefined,
                          })
                        }
                      />
                    )}
                  </div>

                  {/* Action Column */}
                  <div className="col-span-1">
                    <button
                      className="btn btn-ghost btn-sm btn-square text-red-600"
                      onClick={() => handleDeleteComment(channel.id, comment.id)}
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
                handleAddComment(channel.id);
              }}
            >
              ➕ Thêm mẫu
            </button>
            <button
              className="btn btn-primary"
              onClick={() => {
                handleSave();
                setEditingChannelId(null);
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
        <button className="btn btn-primary" onClick={handleSave}>
          💾 Lưu
        </button>
      </div>

      {/* General Settings */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Cài đặt chung</h3>
        <div className="form-control">
          <label className="label cursor-pointer justify-start gap-3">
            <input
              type="checkbox"
              className="checkbox checkbox-primary"
              checked={config.shareToStory}
              onChange={handleToggleShareToStory}
            />
            <span className="label-text font-medium">Chia sẻ lên Tin</span>
          </label>
        </div>
      </div>

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
              ) : channels.length === 0 ? (
                <tr>
                  <td colSpan={4} className="text-center py-12 text-gray-500">
                    Chưa có kênh nào
                  </td>
                </tr>
              ) : (
                channels.map((channel) => (
                  <tr key={channel.id} className="hover:bg-gray-50">
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="avatar">
                          <div className="w-10 h-10 rounded-full">
                            <img
                              src={channel.avatarUrl || 'https://via.placeholder.com/40'}
                              alt={channel.name}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{channel.name}</div>
                          <div className="text-xs text-gray-500">{channel.pageId}</div>
                        </div>
                      </div>
                    </td>
                    <td className="text-center">
                      <input
                        type="checkbox"
                        className="checkbox checkbox-primary"
                        onChange={handleToggleSignature}
                      />
                    </td>
                    <td className="text-center">
                      <input
                        type="checkbox"
                        className="checkbox checkbox-primary"
                        onChange={handleToggleAutoComment}
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
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modals */}
      {channels.map((channel) => renderBulkCommentModal(channel))}
    </div>
  );
};

export default PostingSettingsPage;

