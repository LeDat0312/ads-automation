import React, { useState, useEffect } from 'react';
import * as SettingsAPI from '../../api/settings';
import type { Channel } from '../../api/settings';

const ChannelsSettingsPage: React.FC = () => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChannels, setSelectedChannels] = useState<Set<string>>(new Set());

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

  return (
    <div className="space-y-6">
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
        <button className="btn btn-primary">
          ➕ Thêm kênh
        </button>
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
    </div>
  );
};

export default ChannelsSettingsPage;

