/**
 * Post Management Component
 * Quản lý bài đăng với dashboard stats, filters và actions
 */

import React, { useState, useEffect } from 'react';
import { ScheduledPost, PostStatus, DashboardStats, PostsFilterParams } from '../../types/contentStudio';
import { getScheduledPosts, getDashboardStats, updateScheduledPost, deleteScheduledPost, publishPostNow } from '../../api/contentStudio';
import { format } from 'date-fns';
import { vi } from 'date-fns/locale';

const PostManagement: React.FC = () => {
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [filters, setFilters] = useState<PostsFilterParams>({
    page: 1,
    pageSize: 20
  });
  const [isLoading, setIsLoading] = useState(false);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    loadStats();
    loadPosts();
  }, [filters]);

  const loadStats = async () => {
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadPosts = async () => {
    setIsLoading(true);
    try {
      const result = await getScheduledPosts(filters);
      setPosts(result.items);
      setTotal(result.total);
    } catch (error) {
      console.error('Error loading posts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePublishNow = async (postId: string) => {
    if (!confirm('Đăng bài ngay lập tức?')) return;

    try {
      await publishPostNow(postId);
      alert('Bài đăng đang được xử lý!');
      loadPosts();
      loadStats();
    } catch (error) {
      console.error('Error publishing:', error);
      alert('Lỗi khi đăng bài.');
    }
  };

  const handleDelete = async (postId: string) => {
    if (!confirm('Xóa bài đăng này?')) return;

    try {
      await deleteScheduledPost(postId);
      alert('Đã xóa!');
      loadPosts();
      loadStats();
    } catch (error) {
      console.error('Error deleting:', error);
      alert('Lỗi khi xóa bài đăng.');
    }
  };

  const getStatusBadge = (status: PostStatus) => {
    const statusConfig = {
      [PostStatus.DRAFT]: { color: 'bg-gray-100 text-gray-700', label: '📝 Nháp' },
      [PostStatus.SCHEDULED]: { color: 'bg-blue-100 text-blue-700', label: '⏰ Đã lên lịch' },
      [PostStatus.PUBLISHING]: { color: 'bg-yellow-100 text-yellow-700', label: '⏳ Đang đăng' },
      [PostStatus.PUBLISHED]: { color: 'bg-green-100 text-green-700', label: '✅ Đã đăng' },
      [PostStatus.FAILED]: { color: 'bg-red-100 text-red-700', label: '❌ Lỗi' },
      [PostStatus.CANCELLED]: { color: 'bg-gray-100 text-gray-500', label: '🚫 Đã hủy' }
    };

    const config = statusConfig[status] || statusConfig[PostStatus.DRAFT];
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Dashboard Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Bài đăng hôm nay</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.postsToday}</p>
              </div>
              <div className="text-4xl">📝</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Đang chờ đăng</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">{stats.postsScheduled}</p>
              </div>
              <div className="text-4xl">⏰</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Đăng thành công</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.postsPublishedToday}</p>
              </div>
              <div className="text-4xl">✅</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Lỗi hôm nay</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{stats.postsFailedToday}</p>
              </div>
              <div className="text-4xl">❌</div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filters.status || ''}
            onChange={(e) => setFilters({ ...filters, status: e.target.value as PostStatus || undefined, page: 1 })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tất cả trạng thái</option>
            <option value={PostStatus.SCHEDULED}>Đã lên lịch</option>
            <option value={PostStatus.PUBLISHED}>Đã đăng</option>
            <option value={PostStatus.FAILED}>Lỗi</option>
            <option value={PostStatus.DRAFT}>Nháp</option>
          </select>

          <input
            type="date"
            value={filters.startDate || ''}
            onChange={(e) => setFilters({ ...filters, startDate: e.target.value, page: 1 })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Từ ngày"
          />

          <input
            type="date"
            value={filters.endDate || ''}
            onChange={(e) => setFilters({ ...filters, endDate: e.target.value, page: 1 })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Đến ngày"
          />
        </div>
      </div>

      {/* Posts Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nội dung
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fanpage
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Giờ đăng
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Trạng thái
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Hành động
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                  Đang tải...
                </td>
              </tr>
            ) : posts.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                  Chưa có bài đăng nào
                </td>
              </tr>
            ) : (
              posts.map((post) => (
                <tr key={post.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      {post.contentVariant?.media[0] && (
                        <img
                          src={post.contentVariant.media[0].thumbnailUrl || post.contentVariant.media[0].url}
                          alt="Thumbnail"
                          className="w-16 h-16 object-cover rounded"
                        />
                      )}
                      <div className="max-w-md">
                        <p className="font-medium text-gray-900 line-clamp-1">
                          {post.contentVariant?.title || 'Không có tiêu đề'}
                        </p>
                        <p className="text-sm text-gray-500 line-clamp-2">
                          {post.contentVariant?.captionLao || post.contentVariant?.caption || ''}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-sm text-gray-900">{post.page?.name || 'N/A'}</p>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <p className="text-sm text-gray-900">
                      {format(new Date(post.scheduledAt), 'dd/MM/yyyy HH:mm', { locale: vi })}
                    </p>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(post.status)}
                    {post.error && (
                      <p className="text-xs text-red-600 mt-1">{post.error}</p>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex gap-2 justify-end">
                      {(post.status === PostStatus.SCHEDULED || post.status === PostStatus.FAILED) && (
                        <button
                          onClick={() => handlePublishNow(post.id)}
                          className="text-green-600 hover:text-green-900"
                          title="Đăng ngay"
                        >
                          ▶️
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(post.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Xóa"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {total > (filters.pageSize || 20) && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <p className="text-sm text-gray-700">
              Hiển thị <span className="font-medium">{((filters.page || 1) - 1) * (filters.pageSize || 20) + 1}</span> đến{' '}
              <span className="font-medium">{Math.min((filters.page || 1) * (filters.pageSize || 20), total)}</span> trong{' '}
              <span className="font-medium">{total}</span> kết quả
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setFilters({ ...filters, page: (filters.page || 1) - 1 })}
                disabled={(filters.page || 1) === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Trước
              </button>
              <button
                onClick={() => setFilters({ ...filters, page: (filters.page || 1) + 1 })}
                disabled={(filters.page || 1) * (filters.pageSize || 20) >= total}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Sau
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PostManagement;
