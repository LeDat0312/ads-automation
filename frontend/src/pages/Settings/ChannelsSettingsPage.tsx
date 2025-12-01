import React, { useState, useEffect } from 'react';
import * as SettingsAPI from '../../api/settings';
import type { Channel } from '../../api/settings';
import ConnectFacebookPageModal from '../../components/ConnectFacebookPageModal';

const ChannelsSettingsPage: React.FC = () => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChannels, setSelectedChannels] = useState<Set<string>>(new Set());
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  // NEW: Connect Facebook Page Modal
  const [showConnectModal, setShowConnectModal] = useState(false);

  // Check for OAuth callback parameters
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const connectStatus = params.get('connect');
    const created = params.get('created');
    const updated = params.get('updated');
    const reason = params.get('reason');

    if (connectStatus === 'success') {
      const createdCount = parseInt(created || '0');
      const updatedCount = parseInt(updated || '0');
      setToast({
        message: `✅ Kết nối Fanpage thành công! (${createdCount} mới, ${updatedCount} cập nhật)`,
        type: 'success',
      });
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
      // Reload channels
      loadChannels();
    } else if (connectStatus === 'error') {
      let errorMessage = '❌ Kết nối Fanpage thất bại';
      if (reason === 'no_pages') {
        errorMessage = '❌ Không tìm thấy Fanpage nào. Vui lòng đảm bảo bạn có quyền quản lý Fanpage.';
      } else if (reason === 'no_code') {
        errorMessage = '❌ Không nhận được mã xác thực từ Facebook.';
      } else if (reason === 'server_error') {
        errorMessage = '❌ Lỗi server. Vui lòng thử lại sau.';
      } else if (reason) {
        errorMessage = `❌ Lỗi: ${decodeURIComponent(reason)}`;
      }
      setToast({
        message: errorMessage,
        type: 'error',
      });
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  // Auto-hide toast after 5 seconds
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await SettingsAPI.fetchChannels('facebook'); // Filter by Facebook for now
      setChannels(data);
    } catch (err: any) {
      console.error('Error loading channels:', err);
      setError(err.response?.data?.detail || 'Không thể tải danh sách kênh');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnectFacebook = async () => {
    try {
      // Call API to get OAuth URL
      const response = await fetch('/api/facebook/oauth-url', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Không thể lấy URL OAuth');
      }

      const data = await response.json();
      
      // Redirect to Facebook OAuth
      window.location.href = data.url;
    } catch (err: any) {
      console.error('Error connecting Facebook:', err);
      setToast({
        message: '❌ Không thể kết nối với Facebook. Vui lòng thử lại.',
        type: 'error',
      });
    }
  };

  // Map backend Channel to frontend-friendly format for display
  const getChannelDisplayName = (channel: Channel) => channel.page_name;
  const getChannelAvatar = (channel: Channel) => channel.avatar_url;
  const getChannelPageId = (channel: Channel) => channel.page_id;

  const filteredChannels = channels.filter((channel) =>
    channel.page_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    channel.page_id.includes(searchQuery)
  );

  const handleDeleteChannel = async (channelId: string) => {
    if (!window.confirm('Bạn có chắc muốn xóa kênh này?')) {
      return;
    }

    try {
      await SettingsAPI.deleteChannel(channelId);
      // Reload channels after deletion
      await loadChannels();
    } catch (err: any) {
      console.error('Error deleting channel:', err);
      alert(err.response?.data?.detail || 'Không thể xóa kênh');
    }
  };

  const handleToggleSelect = (channelId: string) => {
    setSelectedChannels((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(channelId)) {
        newSet.delete(channelId);
      } else {
        newSet.add(channelId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedChannels.size === filteredChannels.length) {
      setSelectedChannels(new Set());
    } else {
      setSelectedChannels(new Set(filteredChannels.map((c) => c.id)));
    }
  };

  const handleConnectSuccess = () => {
    setToast({
      message: '✅ Kết nối Fanpage thành công!',
      type: 'success',
    });
    loadChannels();
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {toast && (
        <div className={`alert ${toast.type === 'success' ? 'alert-success' : 'alert-error'} shadow-lg`}>
          <div className="flex items-center justify-between w-full">
            <span>{toast.message}</span>
            <button className="btn btn-sm btn-ghost" onClick={() => setToast(null)}>✕</button>
          </div>
        </div>
      )}

      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Kênh đã kết nối</h2>
        <p className="text-sm text-gray-600 mt-1">
          Quản lý các kênh Facebook Page đã kết nối
        </p>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex-1 flex gap-3 items-center">
          <input
            type="text"
            placeholder="Tìm kiếm kênh..."
            className="input input-bordered flex-1 max-w-xs"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button className="btn btn-outline btn-sm">
            🔄 Sắp xếp
          </button>
          <button className="btn btn-outline btn-sm">
            🔍 Filter
          </button>
          <button className="btn btn-outline btn-sm">
            📊 Xuất báo cáo
          </button>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-primary" onClick={() => setShowConnectModal(true)}>
            ➕ Thêm kênh
          </button>
          <button className="btn btn-outline" onClick={handleConnectFacebook}>
            🔗 Kết nối OAuth (Legacy)
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <button className="btn btn-sm btn-ghost" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="loading loading-spinner loading-lg text-indigo-600"></div>
          <p className="text-gray-600 mt-4">Đang tải danh sách kênh...</p>
        </div>
      ) : (
        /* Channels Table */
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="table w-full">
            <thead className="bg-gray-50">
              <tr>
                <th>
                  <input
                    type="checkbox"
                    className="checkbox checkbox-sm"
                    checked={selectedChannels.size === filteredChannels.length && filteredChannels.length > 0}
                    onChange={handleSelectAll}
                  />
                </th>
                <th className="font-semibold text-gray-900">Kênh</th>
                <th className="font-semibold text-gray-900">ID</th>
                <th className="font-semibold text-gray-900">Người phụ trách</th>
                <th className="font-semibold text-gray-900">Hành động</th>
              </tr>
            </thead>
            <tbody>
              {filteredChannels.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-12 text-gray-500">
                    {searchQuery ? 'Không tìm thấy kênh nào' : 'Chưa có kênh nào được kết nối'}
                  </td>
                </tr>
              ) : (
                filteredChannels.map((channel) => (
                  <tr key={channel.id} className="hover:bg-gray-50">
                    <td>
                      <input
                        type="checkbox"
                        className="checkbox checkbox-sm"
                        checked={selectedChannels.has(channel.id)}
                        onChange={() => handleToggleSelect(channel.id)}
                      />
                    </td>
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="avatar">
                          <div className="w-10 h-10 rounded-full">
                            <img
                              src={getChannelAvatar(channel) || 'https://via.placeholder.com/40'}
                              alt={getChannelDisplayName(channel)}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{getChannelDisplayName(channel)}</div>
                          <div className="text-xs text-gray-500 flex items-center gap-1">
                            <span>📘</span>
                            <span>{getChannelPageId(channel)}</span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="text-sm text-gray-600 font-mono">{getChannelPageId(channel)}</span>
                    </td>
                    <td>
                      <span className="text-sm text-gray-600">
                        {channel.page_username || 'Chưa có'}
                      </span>
                    </td>
                    <td>
                      <div className="dropdown dropdown-end">
                        <label tabIndex={0} className="btn btn-ghost btn-sm">
                          ⋮
                        </label>
                        <ul
                          tabIndex={0}
                          className="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52"
                        >
                          <li>
                            <a>Xem chi tiết</a>
                          </li>
                          <li>
                            <a onClick={() => SettingsAPI.updateChannel(channel.id, { is_active: !channel.is_active })}>
                              {channel.is_active ? 'Tắt' : 'Bật'}
                            </a>
                          </li>
                          <li>
                            <a className="text-red-600" onClick={() => handleDeleteChannel(channel.id)}>Xóa</a>
                          </li>
                        </ul>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Bulk Actions */}
      {selectedChannels.size > 0 && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 flex items-center justify-between">
          <span className="text-indigo-900 font-medium">
            Đã chọn {selectedChannels.size} kênh
          </span>
          <div className="flex gap-2">
            <button className="btn btn-sm btn-outline">Thao tác hàng loạt</button>
            <button
              className="btn btn-sm btn-ghost"
              onClick={() => setSelectedChannels(new Set())}
            >
              Bỏ chọn
            </button>
          </div>
        </div>
      )}

      {/* Connect Facebook Page Modal - NEW */}
      <ConnectFacebookPageModal
        open={showConnectModal}
        onClose={() => setShowConnectModal(false)}
        onSuccess={handleConnectSuccess}
      />
    </div>
  );
};

export default ChannelsSettingsPage;

