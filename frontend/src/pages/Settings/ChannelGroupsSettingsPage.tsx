import React, { useState, useEffect } from 'react';
import * as SettingsAPI from '../../api/settings';
import type { Channel, ChannelGroup } from '../../api/settings';
import { toast } from 'react-toastify';
import { PageHeader, EmptyState, Badge } from '../../components/ui';

const PRESET_COLORS = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
  '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1',
];

const ChannelGroupsSettingsPage: React.FC = () => {
  const [groups, setGroups] = useState<ChannelGroup[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showChannelSelector, setShowChannelSelector] = useState<string | null>(null);
  const [draggedChannel, setDraggedChannel] = useState<Channel | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [groupsData, channelsData] = await Promise.all([
        SettingsAPI.fetchChannelGroups(),
        SettingsAPI.fetchChannels('facebook'),
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

  // Get channels not in any group
  const getUnassignedChannels = (): Channel[] => {
    const assignedIds = new Set(groups.flatMap(g => g.channels.map(c => c.id)));
    return channels.filter(c => !assignedIds.has(c.id));
  };

  // Get channels available for a specific group (not in that group)
  const getAvailableChannels = (group: ChannelGroup): Channel[] => {
    const groupChannelIds = new Set(group.channels.map(c => c.id));
    return channels.filter(c => !groupChannelIds.has(c.id));
  };

  const handleCreateGroup = () => {
    const newGroup: ChannelGroup = {
      id: `temp-${Date.now()}`,
      user_id: 0,
      name: 'Nhóm mới',
      color_hex: PRESET_COLORS[groups.length % PRESET_COLORS.length],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      channels: [],
    };
    setGroups([...groups, newGroup]);
  };

  const handleUpdateGroupName = (groupId: string, newName: string) => {
    setGroups(prev => prev.map(g => g.id === groupId ? { ...g, name: newName } : g));
  };

  const handleUpdateGroupColor = (groupId: string, newColor: string) => {
    setGroups(prev => prev.map(g => g.id === groupId ? { ...g, color_hex: newColor } : g));
  };

  const handleDeleteGroup = async (groupId: string) => {
    if (!window.confirm('Bạn có chắc muốn xóa nhóm này? Các kênh trong nhóm sẽ trở thành "Chưa gán nhóm".')) {
      return;
    }

    if (groupId.startsWith('temp-')) {
      setGroups(prev => prev.filter(g => g.id !== groupId));
      return;
    }

    try {
      await SettingsAPI.deleteChannelGroup(groupId);
      toast.success('Đã xóa nhóm kênh');
      await loadData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Không thể xóa nhóm');
    }
  };

  const handleAddChannelToGroup = (groupId: string, channelId: string) => {
    setGroups(prev => prev.map(g => {
      if (g.id === groupId) {
        const channel = channels.find(c => c.id === channelId);
        if (channel && !g.channels.some(c => c.id === channelId)) {
          return { ...g, channels: [...g.channels, channel] };
        }
      }
      return g;
    }));
    setShowChannelSelector(null);
  };

  const handleRemoveChannelFromGroup = (groupId: string, channelId: string) => {
    setGroups(prev => prev.map(g =>
      g.id === groupId
        ? { ...g, channels: g.channels.filter(c => c.id !== channelId) }
        : g
    ));
  };

  // Drag and drop handlers
  const handleDragStart = (channel: Channel) => {
    setDraggedChannel(channel);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDropOnGroup = (groupId: string) => {
    if (draggedChannel) {
      // Remove from other groups first
      setGroups(prev => prev.map(g => ({
        ...g,
        channels: g.channels.filter(c => c.id !== draggedChannel.id)
      })));
      // Add to target group
      handleAddChannelToGroup(groupId, draggedChannel.id);
      setDraggedChannel(null);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    try {
      for (const group of groups) {
        const channelIds = group.channels.map(c => c.id);
        const payload = {
          name: group.name,
          color_hex: group.color_hex || '#3B82F6',
          channel_ids: channelIds,
        };

        if (group.id.startsWith('temp-')) {
          await SettingsAPI.saveChannelGroup(payload);
        } else {
          await SettingsAPI.saveChannelGroup(payload, group.id);
        }
      }

      toast.success('Đã lưu cấu hình Nhóm kênh');
      await loadData();
    } catch (err: any) {
      console.error('Error saving groups:', err);
      toast.error(err.response?.data?.detail || 'Lưu thất bại');
    } finally {
      setIsSaving(false);
    }
  };

  const unassignedChannels = getUnassignedChannels();

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Nhóm kênh"
        subtitle="Phân loại Fanpage theo thương hiệu, thị trường hoặc team phụ trách"
        actions={
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50"
          >
            {isSaving ? (
              <>
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Đang lưu...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Lưu thay đổi
              </>
            )}
          </button>
        }
      />

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
          <span className="text-red-800">{error}</span>
          <button className="text-red-600 hover:text-red-800" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Đang tải dữ liệu...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Groups Column */}
          <div className="lg:col-span-2 space-y-4">
            {groups.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200">
                <EmptyState
                  icon="📁"
                  title="Chưa có nhóm kênh nào"
                  description="Nhóm kênh giúp bạn phân loại Fanpage theo thương hiệu, thị trường hoặc team phụ trách."
                  action={{
                    label: '+ Thêm Nhóm kênh đầu tiên',
                    onClick: handleCreateGroup,
                  }}
                />
              </div>
            ) : (
              groups.map(group => (
                <div
                  key={group.id}
                  className="bg-white rounded-xl border border-gray-200 p-4"
                  onDragOver={handleDragOver}
                  onDrop={() => handleDropOnGroup(group.id)}
                >
                  {/* Group Header */}
                  <div className="flex items-center gap-3 mb-4">
                    {/* Color Picker */}
                    <div className="relative">
                      <input
                        type="color"
                        value={group.color_hex || '#3B82F6'}
                        onChange={(e) => handleUpdateGroupColor(group.id, e.target.value)}
                        className="w-10 h-10 rounded-lg cursor-pointer border-2 border-gray-200"
                        title="Chọn màu"
                      />
                    </div>
                    
                    {/* Group Name */}
                    <input
                      type="text"
                      value={group.name}
                      onChange={(e) => handleUpdateGroupName(group.id, e.target.value)}
                      className="flex-1 text-lg font-semibold bg-transparent border-b-2 border-transparent hover:border-gray-300 focus:border-indigo-500 focus:outline-none px-1 py-1"
                      placeholder="Tên nhóm"
                    />
                    
                    {/* Channel Count */}
                    <Badge variant="neutral">{group.channels.length} kênh</Badge>
                    
                    {/* Delete Button */}
                    <button
                      onClick={() => handleDeleteGroup(group.id)}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Xóa nhóm"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                  
                  {/* Channels in Group */}
                  <div className="flex flex-wrap gap-2 min-h-[60px] p-3 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
                    {group.channels.length === 0 ? (
                      <p className="text-gray-400 text-sm w-full text-center py-4">
                        Kéo thả kênh vào đây hoặc bấm + để thêm
                      </p>
                    ) : (
                      group.channels.map(channel => (
                        <div
                          key={channel.id}
                          className="flex items-center gap-2 px-3 py-2 bg-white rounded-lg border shadow-sm"
                          style={{ borderColor: group.color_hex || '#3B82F6' }}
                        >
                          <img
                            src={channel.avatar_url || 'https://via.placeholder.com/24'}
                            alt={channel.page_name}
                            className="w-6 h-6 rounded-full"
                          />
                          <span className="text-sm font-medium">{channel.page_name}</span>
                          <button
                            onClick={() => handleRemoveChannelFromGroup(group.id, channel.id)}
                            className="text-gray-400 hover:text-red-600 ml-1"
                          >
                            ×
                          </button>
                        </div>
                      ))
                    )}
                    
                    {/* Add Channel Button */}
                    <div className="relative">
                      <button
                        onClick={() => setShowChannelSelector(showChannelSelector === group.id ? null : group.id)}
                        className="flex items-center gap-1 px-3 py-2 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Thêm kênh
                      </button>
                      
                      {showChannelSelector === group.id && (
                        <div className="absolute top-full left-0 mt-2 z-20 bg-white rounded-lg shadow-lg border border-gray-200 min-w-[250px] max-h-[300px] overflow-y-auto">
                          {getAvailableChannels(group).length === 0 ? (
                            <p className="text-sm text-gray-500 p-4 text-center">
                              Không còn kênh nào để thêm
                            </p>
                          ) : (
                            <div className="p-2">
                              {getAvailableChannels(group).map(channel => (
                                <button
                                  key={channel.id}
                                  onClick={() => handleAddChannelToGroup(group.id, channel.id)}
                                  className="w-full flex items-center gap-3 px-3 py-2 hover:bg-gray-50 rounded-lg transition-colors"
                                >
                                  <img
                                    src={channel.avatar_url || 'https://via.placeholder.com/24'}
                                    alt={channel.page_name}
                                    className="w-6 h-6 rounded-full"
                                  />
                                  <span className="text-sm">{channel.page_name}</span>
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
            
            {/* Add Group Button */}
            <button
              onClick={handleCreateGroup}
              className="w-full py-4 border-2 border-dashed border-gray-300 rounded-xl text-gray-500 hover:border-indigo-500 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
            >
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Thêm Nhóm kênh mới
              </span>
            </button>
          </div>
          
          {/* Unassigned Channels Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 p-4 sticky top-4">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Chưa gán nhóm
                <Badge variant="neutral">{unassignedChannels.length}</Badge>
              </h3>
              
              {unassignedChannels.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-8">
                  Tất cả kênh đã được gán vào nhóm
                </p>
              ) : (
                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                  {unassignedChannels.map(channel => (
                    <div
                      key={channel.id}
                      draggable
                      onDragStart={() => handleDragStart(channel)}
                      className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-move hover:bg-gray-100 transition-colors border border-transparent hover:border-indigo-200"
                    >
                      <img
                        src={channel.avatar_url || 'https://via.placeholder.com/32'}
                        alt={channel.page_name}
                        className="w-8 h-8 rounded-full"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{channel.page_name}</p>
                        <p className="text-xs text-gray-500">Kéo để gán nhóm</p>
                      </div>
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
                      </svg>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChannelGroupsSettingsPage;
