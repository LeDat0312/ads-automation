import React, { useState, useEffect } from 'react';
import { fetchChannels, fetchChannelGroups } from '../../api/settings';
import type { Channel, ChannelGroup } from '../../api/settings';

interface ChannelSelectorProps {
  selectedChannelIds: string[];
  onSelectionChange: (channelIds: string[]) => void;
}

const ChannelSelector: React.FC<ChannelSelectorProps> = ({
  selectedChannelIds,
  onSelectionChange,
}) => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [groups, setGroups] = useState<ChannelGroup[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [channelsData, groupsData] = await Promise.all([
        fetchChannels('facebook', undefined, true),
        fetchChannelGroups(),
      ]);
      setChannels(channelsData);
      setGroups(groupsData);
    } catch (error) {
      console.error('Error loading channels:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredChannels = channels.filter((channel) => {
    // Filter by group
    if (selectedGroupId !== 'all') {
      const group = groups.find((g) => g.id === selectedGroupId);
      if (!group || !group.channels.some((c: Channel) => c.id === channel.id)) {
        return false;
      }
    }

    // Filter by search
    if (searchQuery) {
      return channel.page_name.toLowerCase().includes(searchQuery.toLowerCase());
    }

    return true;
  });

  const toggleChannel = (channelId: string) => {
    if (selectedChannelIds.includes(channelId)) {
      onSelectionChange(selectedChannelIds.filter((id) => id !== channelId));
    } else {
      onSelectionChange([...selectedChannelIds, channelId]);
    }
  };

  const toggleAll = () => {
    if (selectedChannelIds.length === filteredChannels.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(filteredChannels.map((c) => c.id));
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-1">
          Chọn kênh ({selectedChannelIds.length}/{channels.length})
        </h3>
        <p className="text-xs text-gray-500">Chọn Fanpage để đăng bài</p>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-gray-200 space-y-3">
        {/* Group Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Nhóm kênh</label>
          <select
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            value={selectedGroupId}
            onChange={(e) => setSelectedGroupId(e.target.value)}
          >
            <option value="all">Tất cả nhóm</option>
            {groups.map((group) => (
              <option key={group.id} value={group.id}>
                {group.name} ({group.channels.length})
              </option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Tìm kiếm</label>
          <input
            type="text"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Tìm kiếm fanpage..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Channel List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="text-sm text-gray-500 mt-2">Đang tải...</p>
          </div>
        ) : filteredChannels.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-4xl mb-2">📡</div>
            <p className="text-sm text-gray-500">Không tìm thấy kênh nào</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredChannels.map((channel) => {
              const isSelected = selectedChannelIds.includes(channel.id);
              return (
                <label
                  key={channel.id}
                  className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleChannel(channel.id)}
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <img
                    src={channel.avatar_url || 'https://via.placeholder.com/40'}
                    alt={channel.page_name}
                    className="w-10 h-10 rounded-full"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {channel.page_name}
                    </p>
                    <p className="text-xs text-gray-500">Fanpage</p>
                  </div>
                </label>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Đã chọn: {selectedChannelIds.length} kênh</span>
          <button
            onClick={toggleAll}
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            {selectedChannelIds.length === filteredChannels.length ? 'Bỏ chọn tất cả' : 'Chọn tất cả'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChannelSelector;
