import React, { useState, useEffect } from 'react';
import { getPages, syncPages, enablePage, deletePage } from '../../api/channel';
import type { FacebookPage } from '../../types/channel';

const PagesList: React.FC = () => {
  const [pages, setPages] = useState<FacebookPage[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState('');
  const [filterEnabled, setFilterEnabled] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    loadPages();
  }, [search, filterEnabled]);

  const loadPages = async () => {
    try {
      setLoading(true);
      const data = await getPages(search || undefined, filterEnabled);
      setPages(data);
    } catch (error) {
      console.error('Error loading pages:', error);
      alert('Lỗi khi tải danh sách pages');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      const result = await syncPages();
      alert(`Đồng bộ thành công: ${result.synced} mới, ${result.updated} cập nhật`);
      loadPages();
    } catch (error: any) {
      console.error('Error syncing pages:', error);
      alert(error.response?.data?.detail || 'Lỗi khi đồng bộ pages');
    } finally {
      setSyncing(false);
    }
  };

  const handleToggle = async (page: FacebookPage) => {
    try {
      await enablePage(page.id, !page.enabled);
      loadPages();
    } catch (error: any) {
      console.error('Error toggling page:', error);
      alert(error.response?.data?.detail || 'Lỗi khi cập nhật page');
    }
  };

  const handleDelete = async (page: FacebookPage) => {
    if (!confirm(`Bạn có chắc muốn ngắt kết nối "${page.page_name}"?`)) {
      return;
    }
    
    try {
      await deletePage(page.id);
      loadPages();
    } catch (error: any) {
      console.error('Error deleting page:', error);
      alert(error.response?.data?.detail || 'Lỗi khi xóa page');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">📄 Danh Sách Fanpage</h1>
              <p className="text-gray-600">Quản lý các Facebook Pages đã kết nối</p>
            </div>
            <button
              onClick={handleSync}
              disabled={syncing}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-md transition-colors"
            >
              {syncing ? '⏳ Đang đồng bộ...' : '🔄 Đồng Bộ Pages'}
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="🔍 Tìm kiếm theo tên hoặc ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              value={filterEnabled === undefined ? 'all' : filterEnabled ? 'enabled' : 'disabled'}
              onChange={(e) => {
                const value = e.target.value;
                setFilterEnabled(value === 'all' ? undefined : value === 'enabled');
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Tất cả</option>
              <option value="enabled">Đã bật</option>
              <option value="disabled">Đã tắt</option>
            </select>
          </div>
        </div>

        {/* Pages List */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Đang tải...</p>
            </div>
          ) : pages.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-gray-500 text-lg">Chưa có page nào. Hãy đồng bộ để lấy danh sách pages từ Facebook.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Page</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Category</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Trạng thái</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Thao tác</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pages.map((page) => (
                    <tr key={page.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {page.page_avatar ? (
                            <img
                              src={page.page_avatar}
                              alt={page.page_name}
                              className="h-10 w-10 rounded-full mr-3"
                            />
                          ) : (
                            <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center mr-3">
                              <span className="text-gray-600 text-lg">📄</span>
                            </div>
                          )}
                          <div>
                            <div className="text-sm font-medium text-gray-900">{page.page_name}</div>
                            <div className="text-xs text-gray-500">
                              Kết nối: {new Date(page.connected_at).toLocaleDateString('vi-VN')}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-700">{page.page_id}</code>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {page.category || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={page.enabled}
                            onChange={() => handleToggle(page)}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          <span className="ml-3 text-sm text-gray-700">
                            {page.enabled ? '✅ Đã bật' : '❌ Đã tắt'}
                          </span>
                        </label>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => handleDelete(page)}
                          className="text-red-600 hover:text-red-800 font-semibold px-3 py-1 rounded hover:bg-red-50 transition-colors"
                        >
                          🗑️ Xóa
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PagesList;

