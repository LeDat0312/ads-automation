import React, { useState, useEffect } from 'react';

// Types
interface Channel {
  id: string;
  name: string;
  pageId: string;
  avatarUrl?: string;
}

interface ChannelGroup {
  id: string;
  name: string;
  color: string;
  channelIds: string[];
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

const mockGroups: ChannelGroup[] = [
  {
    id: '1',
    name: 'Tiền',
    color: '#3B82F6',
    channelIds: ['1'],
  },
  {
    id: '2',
    name: 'Hút Mỡ',
    color: '#EF4444',
    channelIds: ['2'],
  },
];

const ChannelGroupsSettingsPage: React.FC = () => {
  const [groups, setGroups] = useState<ChannelGroup[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showChannelSelector, setShowChannelSelector] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with real API calls
      // const [groupsData, channelsData] = await Promise.all([
      //   fetchChannelGroups(),
      //   fetchChannels(),
      // ]);
      
      // Mock data
      await new Promise((resolve) => setTimeout(resolve, 500));
      setGroups(mockGroups);
      setChannels(mockChannels);
    } catch (error) {
      console.error('Error loading data:', error);
      console.error('Không thể tải dữ liệu');
      setGroups(mockGroups);
      setChannels(mockChannels);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateGroup = () => {
    const newGroup: ChannelGroup = {
      id: Date.now().toString(),
      name: 'Nhóm mới',
      color: '#3B82F6',
      channelIds: [],
    };
    setGroups([...groups, newGroup]);
  };

  const handleUpdateGroupName = (groupId: string, newName: string) => {
    setGroups((prev) =>
      prev.map((g) => (g.id === groupId ? { ...g, name: newName } : g))
    );
  };

  const handleUpdateGroupColor = (groupId: string, newColor: string) => {
    setGroups((prev) =>
      prev.map((g) => (g.id === groupId ? { ...g, color: newColor } : g))
    );
  };

  const handleDeleteGroup = (groupId: string) => {
    if (window.confirm('Bạn có chắc muốn xóa nhóm này?')) {
      setGroups((prev) => prev.filter((g) => g.id !== groupId));
      console.log('Đã xóa nhóm');
    }
  };

  const handleAddChannelToGroup = (groupId: string, channelId: string) => {
    setGroups((prev) =>
      prev.map((g) => {
        if (g.id === groupId) {
          if (!g.channelIds.includes(channelId)) {
            return { ...g, channelIds: [...g.channelIds, channelId] };
          }
        }
        return g;
      })
    );
    setShowChannelSelector(null);
    console.log('Đã thêm kênh vào nhóm');
  };

  const handleRemoveChannelFromGroup = (groupId: string, channelId: string) => {
    setGroups((prev) =>
      prev.map((g) =>
        g.id === groupId
          ? { ...g, channelIds: g.channelIds.filter((id) => id !== channelId) }
          : g
      )
    );
    console.log('Đã xóa kênh khỏi nhóm');
  };

  const getChannelsInGroup = (group: ChannelGroup) => {
    return channels.filter((c) => group.channelIds.includes(c.id));
  };

  const getAvailableChannels = (group: ChannelGroup) => {
    return channels.filter((c) => !group.channelIds.includes(c.id));
  };

  const handleSave = async () => {
    try {
      // TODO: Call API to save groups
      // await saveChannelGroups(groups);
      alert('Đã lưu nhóm kênh');
    } catch (error) {
      console.error('Error saving groups:', error);
      alert('Lưu thất bại');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Thiết lập Nhóm kênh</h2>
          <p className="text-sm text-gray-600 mt-1">
            Tạo và quản lý các nhóm kênh để phân loại fanpage
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-primary" onClick={handleSave}>
            💾 Lưu
          </button>
        </div>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="loading loading-spinner loading-lg text-indigo-600"></div>
          <p className="text-gray-600 mt-4">Đang tải dữ liệu...</p>
        </div>
      ) : (
        <>
          {/* Groups Table */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="table w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="font-semibold text-gray-900">Tên nhóm</th>
                    <th className="font-semibold text-gray-900">Màu sắc</th>
                    <th className="font-semibold text-gray-900">Kênh</th>
                  </tr>
                </thead>
                <tbody>
                  {groups.map((group) => {
                    const channelsInGroup = getChannelsInGroup(group);
                    const availableChannels = getAvailableChannels(group);
                    
                    return (
                      <tr key={group.id} className="hover:bg-gray-50">
                        <td>
                          <div className="flex items-center gap-2">
                            <input
                              type="text"
                              className="input input-bordered input-sm flex-1"
                              value={group.name}
                              onChange={(e) =>
                                handleUpdateGroupName(group.id, e.target.value)
                              }
                            />
                            <button
                              className="btn btn-ghost btn-sm btn-square"
                              onClick={() => handleDeleteGroup(group.id)}
                              title="Xóa nhóm"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                        <td>
                          <div className="flex items-center gap-2">
                            <input
                              type="color"
                              className="w-10 h-10 rounded border border-gray-300 cursor-pointer"
                              value={group.color}
                              onChange={(e) =>
                                handleUpdateGroupColor(group.id, e.target.value)
                              }
                              title="Chọn màu"
                            />
                            <input
                              type="text"
                              className="input input-bordered input-sm w-24"
                              value={group.color}
                              onChange={(e) =>
                                handleUpdateGroupColor(group.id, e.target.value)
                              }
                              placeholder="#3B82F6"
                            />
                          </div>
                        </td>
                        <td>
                          <div className="flex flex-wrap gap-2 items-center">
                            {channelsInGroup.map((channel) => (
                              <div
                                key={channel.id}
                                className="badge badge-outline flex items-center gap-1"
                                style={{
                                  borderColor: group.color,
                                  color: group.color,
                                }}
                              >
                                <img
                                  src={channel.avatarUrl || 'https://via.placeholder.com/20'}
                                  alt={channel.name}
                                  className="w-4 h-4 rounded-full"
                                />
                                <span className="text-xs">{channel.name}</span>
                                <button
                                  className="ml-1 text-red-500 hover:text-red-700"
                                  onClick={() =>
                                    handleRemoveChannelFromGroup(group.id, channel.id)
                                  }
                                >
                                  ×
                                </button>
                              </div>
                            ))}
                            <div className="relative">
                              <button
                                className="btn btn-sm btn-ghost btn-square"
                                onClick={() =>
                                  setShowChannelSelector(
                                    showChannelSelector === group.id ? null : group.id
                                  )
                                }
                                title="Thêm kênh"
                              >
                                ➕
                              </button>
                              {showChannelSelector === group.id && (
                                <div className="absolute top-full right-0 mt-2 z-10 bg-white p-2 rounded-lg shadow-lg border border-gray-200 min-w-[200px]">
                                  {availableChannels.length === 0 ? (
                                    <p className="text-sm text-gray-500 p-2">
                                      Không còn kênh nào
                                    </p>
                                  ) : (
                                    <ul className="menu">
                                      {availableChannels.map((channel) => (
                                        <li key={channel.id}>
                                          <a
                                            onClick={() =>
                                              handleAddChannelToGroup(group.id, channel.id)
                                            }
                                          >
                                            <img
                                              src={channel.avatarUrl || 'https://via.placeholder.com/20'}
                                              alt={channel.name}
                                              className="w-5 h-5 rounded-full"
                                            />
                                            <span className="text-sm">{channel.name}</span>
                                          </a>
                                        </li>
                                      ))}
                                    </ul>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Add Group Button */}
          <button
            className="btn btn-outline btn-primary w-full"
            onClick={handleCreateGroup}
          >
            ➕ Thêm Nhóm kênh
          </button>
        </>
      )}
    </div>
  );
};

export default ChannelGroupsSettingsPage;

