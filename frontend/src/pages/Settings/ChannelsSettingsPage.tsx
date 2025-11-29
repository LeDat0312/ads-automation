import React, { useState, useEffect } from 'react';

// Types
interface Channel {
  id: string;
  name: string;
  pageId: string;
  avatarUrl?: string;
  ownerName?: string;
  platform: 'facebook';
}

// Mock data - will be replaced with real API later
const mockChannels: Channel[] = [
  {
    id: '1',
    name: 'Fanpage Mỹ Phẩm ABC',
    pageId: '123456789',
    avatarUrl: 'https://via.placeholder.com/40',
    ownerName: 'Nguyễn Văn A',
    platform: 'facebook',
  },
  {
    id: '2',
    name: 'Shop Thời Trang XYZ',
    pageId: '987654321',
    avatarUrl: 'https://via.placeholder.com/40',
    ownerName: 'Trần Thị B',
    platform: 'facebook',
  },
];

const ChannelsSettingsPage: React.FC = () => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChannels, setSelectedChannels] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with real API call
      // const data = await fetchChannels();
      // setChannels(data);
      
      // Mock data for now
      await new Promise((resolve) => setTimeout(resolve, 500));
      setChannels(mockChannels);
    } catch (error) {
      console.error('Error loading channels:', error);
      console.error('Không thể tải danh sách kênh');
      // Fallback to mock data
      setChannels(mockChannels);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredChannels = channels.filter((channel) =>
    channel.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    channel.pageId.includes(searchQuery)
  );

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
                              src={channel.avatarUrl || 'https://via.placeholder.com/40'}
                              alt={channel.name}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{channel.name}</div>
                          <div className="text-xs text-gray-500 flex items-center gap-1">
                            <span>📘</span>
                            <span>{channel.pageId}</span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="text-sm text-gray-600 font-mono">{channel.pageId}</span>
                    </td>
                    <td>
                      <span className="text-sm text-gray-600">
                        {channel.ownerName || 'Chưa có'}
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
                            <a>Ngắt kết nối</a>
                          </li>
                          <li>
                            <a className="text-red-600">Xóa</a>
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

