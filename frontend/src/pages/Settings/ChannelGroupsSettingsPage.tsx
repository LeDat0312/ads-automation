import React, { useState, useEffect } from 'react';
import * as SettingsAPI from '../../api/settings';
import type { Channel, ChannelGroup } from '../../api/settings';

const ChannelGroupsSettingsPage: React.FC = () => {
  const [groups, setGroups] = useState<ChannelGroup[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showChannelSelector, setShowChannelSelector] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [groupsData, channelsData] = await Promise.all([
        SettingsAPI.fetchChannelGroups(),
        SettingsAPI.fetchChannels('facebook'), // Filter by Facebook for now
      ]);
      setGroups(groupsData);
      setChannels(channelsData);
    } catch (err: any) {
      console.error('Error loading data:', err);
      setError(err.response?.data?.detail || 'Không thể tải dữ liệu');
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to get channel IDs from group
  const getGroupChannelIds = (group: ChannelGroup): string[] => {
    return group.channels.map(c => c.id);
  };

  // Helper to check if channel is in group
  const isChannelInGroup = (group: ChannelGroup, channelId: string): boolean => {
    return group.channels.some(c => c.id === channelId);
  };

  // Get channels currently in group
  const getChannelsInGroup = (group: ChannelGroup): Channel[] => {
    return group.channels;
  };

  // Get channels not in group
  const getAvailableChannels = (group: ChannelGroup): Channel[] => {
    const groupChannelIds = getGroupChannelIds(group);
    return channels.filter(c => !groupChannelIds.includes(c.id));
  };

  const handleCreateGroup = () => {
    // Create new group locally - will be saved when user clicks Save
    const newGroup: ChannelGroup = {
      id: `temp-${Date.now()}`, // Temporary ID
      user_id: 0,
      name: 'Nhóm mới',
      color_hex: '#3B82F6',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      channels: [],
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
      prev.map((g) => (g.id === groupId ? { ...g, color_hex: newColor } : g))
    );
  };

  const handleDeleteGroup = async (groupId: string) => {
    if (!window.confirm('Bạn có chắc muốn xóa nhóm này?')) {
      return;
    }

    // Skip API call for temporary groups
    if (groupId.startsWith('temp-')) {
      setGroups((prev) => prev.filter((g) => g.id !== groupId));
      return;
    }

    try {
      await SettingsAPI.deleteChannelGroup(groupId);
      await loadData(); // Reload after deletion
    } catch (err: any) {
      console.error('Error deleting group:', err);
      alert(err.response?.data?.detail || 'Không thể xóa nhóm');
    }
  };

  const handleAddChannelToGroup = (groupId: string, channelId: string) => {
    setGroups((prev) =>
      prev.map((g) => {
        if (g.id === groupId) {
          const channel = channels.find(c => c.id === channelId);
          if (channel && !isChannelInGroup(g, channelId)) {
            return { ...g, channels: [...g.channels, channel] };
          }
        }
        return g;
      })
    );
    setShowChannelSelector(null);
  };

  const handleRemoveChannelFromGroup = (groupId: string, channelId: string) => {
    setGroups((prev) =>
      prev.map((g) =>
        g.id === groupId
          ? { ...g, channels: g.channels.filter((c) => c.id !== channelId) }
          : g
      )
    );
  };

  // Save all groups - create new ones and update existing ones
  const handleSave = async () => {
    setError(null);
    try {
      // Process all groups
      for (const group of groups) {
        const channelIds = getGroupChannelIds(group);
        const payload = {
          name: group.name,
          color_hex: group.color_hex || '#3B82F6',
          channel_ids: channelIds,
        };

        if (group.id.startsWith('temp-')) {
          // Create new group
          await SettingsAPI.saveChannelGroup(payload);
        } else {
          // Update existing group
          await SettingsAPI.saveChannelGroup(payload, group.id);
        }
      }

      // Reload data after saving
      await loadData();
      alert('Đã lưu nhóm kênh thành công');
    } catch (err: any) {
      console.error('Error saving groups:', err);
      setError(err.response?.data?.detail || 'Lưu thất bại');
      alert(err.response?.data?.detail || 'Lưu thất bại');
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
                              value={group.color_hex || '#3B82F6'}
                              onChange={(e) =>
                                handleUpdateGroupColor(group.id, e.target.value)
                              }
                              title="Chọn màu"
                            />
                            <input
                              type="text"
                              className="input input-bordered input-sm w-24"
                              value={group.color_hex || '#3B82F6'}
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
                                  borderColor: group.color_hex || '#3B82F6',
                                  color: group.color_hex || '#3B82F6',
                                }}
                              >
                                <img
                                  src={channel.avatar_url || 'https://via.placeholder.com/20'}
                                  alt={channel.page_name}
                                  className="w-4 h-4 rounded-full"
                                />
                                <span className="text-xs">{channel.page_name}</span>
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
                                              src={channel.avatar_url || 'https://via.placeholder.com/20'}
                                              alt={channel.page_name}
                                              className="w-5 h-5 rounded-full"
                                            />
                                            <span className="text-sm">{channel.page_name}</span>
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

