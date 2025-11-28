import React, { useState, useEffect } from 'react';
import { getGroups } from '../api/channel';
import { scheduleAutoComment } from '../api/channel';
import type { ChannelGroup } from '../types/channel';

interface AutoCommentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const AutoCommentModal: React.FC<AutoCommentModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [groups, setGroups] = useState<ChannelGroup[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedGroupId, setSelectedGroupId] = useState('');
  const [postId, setPostId] = useState('');
  const [commentText, setCommentText] = useState('');
  const [mediaUrl, setMediaUrl] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [scheduling, setScheduling] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadGroups();
      // Set default scheduled time to now
      const now = new Date();
      now.setMinutes(now.getMinutes() + 1); // 1 minute from now
      setScheduledAt(now.toISOString().slice(0, 16));
    }
  }, [isOpen]);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const data = await getGroups();
      setGroups(data);
      if (data.length > 0) {
        setSelectedGroupId(data[0].id);
      }
    } catch (error) {
      console.error('Error loading groups:', error);
      alert('Lỗi khi tải danh sách nhóm');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!selectedGroupId) {
      alert('Vui lòng chọn nhóm');
      return;
    }
    if (!postId.trim()) {
      alert('Vui lòng nhập Post ID');
      return;
    }
    if (!commentText.trim()) {
      alert('Vui lòng nhập nội dung comment');
      return;
    }
    if (!scheduledAt) {
      alert('Vui lòng chọn thời gian đăng');
      return;
    }

    try {
      setScheduling(true);
      await scheduleAutoComment({
        group_id: selectedGroupId,
        post_id: postId.trim(),
        comment_text: commentText,
        media_url: mediaUrl.trim() || null,
        scheduled_at: new Date(scheduledAt).toISOString()
      });
      alert('Đã lên lịch auto comment thành công!');
      onSuccess?.();
      handleClose();
    } catch (error: any) {
      console.error('Error scheduling auto comment:', error);
      alert(error.response?.data?.detail || 'Lỗi khi lên lịch auto comment');
    } finally {
      setScheduling(false);
    }
  };

  const handleClose = () => {
    setSelectedGroupId('');
    setPostId('');
    setCommentText('');
    setMediaUrl('');
    setScheduledAt('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">💬 Lên Lịch Auto Comment</h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Group Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chọn nhóm kênh <span className="text-red-500">*</span>
            </label>
            {loading ? (
              <div className="text-center py-4 text-gray-500">Đang tải...</div>
            ) : groups.length === 0 ? (
              <div className="text-center py-4 text-gray-500">
                Chưa có nhóm nào. Vui lòng tạo nhóm trước.
              </div>
            ) : (
              <select
                value={selectedGroupId}
                onChange={(e) => setSelectedGroupId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                {groups.map((group) => (
                  <option key={group.id} value={group.id}>
                    {group.name} ({group.pages.length} pages)
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Post ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Facebook Post ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={postId}
              onChange={(e) => setPostId(e.target.value)}
              placeholder="Nhập Post ID (ví dụ: 123456789_987654321)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
            <p className="mt-1 text-xs text-gray-500">
              Post ID là ID của bài viết Facebook bạn muốn comment
            </p>
          </div>

          {/* Comment Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nội dung comment <span className="text-red-500">*</span>
            </label>
            <textarea
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Nhập nội dung comment...&#10;&#10;Bạn có thể dùng placeholders:&#10;{iconR1} {iconR2} ..."
              rows={6}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
            />
            <p className="mt-1 text-xs text-gray-500">
              Hỗ trợ multi-line. Placeholders: {'{iconR1}'}, {'{iconR2}'}, ...
            </p>
          </div>

          {/* Media URL (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Media URL (Tùy chọn)
            </label>
            <input
              type="url"
              value={mediaUrl}
              onChange={(e) => setMediaUrl(e.target.value)}
              placeholder="https://example.com/image.jpg"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
            <p className="mt-1 text-xs text-gray-500">
              URL của hình ảnh hoặc video (nếu có)
            </p>
          </div>

          {/* Schedule Time */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Thời gian đăng <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-4">
              <div className="flex-1">
                <input
                  type="datetime-local"
                  value={scheduledAt}
                  onChange={(e) => setScheduledAt(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
              <button
                type="button"
                onClick={() => {
                  const now = new Date();
                  now.setMinutes(now.getMinutes() + 1);
                  setScheduledAt(now.toISOString().slice(0, 16));
                }}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
              >
                Ngay bây giờ
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-6 flex gap-3">
          <button
            onClick={handleClose}
            disabled={scheduling}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 disabled:opacity-50"
          >
            Hủy
          </button>
          <button
            onClick={handleSubmit}
            disabled={scheduling || !selectedGroupId || !postId.trim() || !commentText.trim() || !scheduledAt}
            className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
          >
            {scheduling ? '⏳ Đang lên lịch...' : '✅ Lên Lịch'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AutoCommentModal;


