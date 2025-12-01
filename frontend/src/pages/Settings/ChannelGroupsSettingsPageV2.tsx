import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import {
  fetchChannels,
  fetchChannelGroups,
  saveChannelGroup,
  deleteChannelGroup,
} from '../../api/settings';
import type { Channel, ChannelGroup, ChannelGroupCreate } from '../../api/settings';
import { PageHeader } from '../../components/ui';

// Color presets
const COLOR_PRESETS = [
  '#3B82F6', // Blue
  '#22C55E', // Green
  '#EF4444', // Red
  '#F59E0B', // Amber
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#F97316', // Orange
  '#6366F1', // Indigo
  '#14B8A6', // Teal
];

const ChannelGroupsSettingsPageV2: React.FC = () => {
  // Data state
  const [groups, setGroups] = useState<ChannelGroup[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Selection state
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [isCreatingNew, setIsCreatingNew] = useState(false);

  // Form state
  const [formName, setFormName] = useState('');
  const [formColor, setFormColor] = useState('#3B82F6');
  const [formChannelIds, setFormChannelIds] = useState<string[]>([]);
  const [channelSearch, setChannelSearch] = useState('');

  // Action state
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [groupsData, channelsData] = await Promise.all([
        fetchChannelGroups(),
        fetchChannels(),
      ]);
      setGroups(groupsData);
      setChannels(channelsData);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Không thể tải dữ liệu');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectGroup = (group: ChannelGroup) => {
    setSelectedGroupId(group.id);
    setIsCreatingNew(false);
    setFormName(group.name);
    setFormColor(group.color_hex || '#3B82F6');
    setFormChannelIds(group.channels.map((c) => c.id));
  };

  const handleCreateNew = () => {
    setSelectedGroupId(null);
    setIsCreatingNew(true);
    setFormName('');
    setFormColor('#3B82F6');
    setFormChannelIds([]);
  };

  const handleSave = async () => {
    // Validation
    if (!formName.trim()) {
      toast.error('Vui lòng nhập tên nhóm');
      return;
    }

    if (formChannelIds.length === 0) {
      toast.error('Vui lòng chọn ít nhất 1 kênh');
      return;
    }

    setIsSaving(true);
    try {
      const payload: ChannelGroupCreate = {
        name: formName.trim(),
        color_hex: formColor,
        channel_ids: formChannelIds,
      };

      await saveChannelGroup(payload, isCreatingNew ? undefined : selectedGroupId || undefined);
      
      toast.success(`Đã lưu nhóm kênh "${formName}"`);
      await loadData();
      
      // Reset form if creating new
      if (isCreatingNew) {
        setIsCreatingNew(false);
        setSelectedGroupId(null);
      }
    } catch (error: any) {
      console.error('Error saving group:', error);
      const detail = error.response?.data?.detail || 'Không lưu được nhóm kênh';
      toast.error(detail);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedGroupId) return;
    
    const group = groups.find((g) => g.id === selectedGroupId);
    if (!confirm(`Bạn có chắc muốn xoá nhóm "${group?.name}"?`)) return;

    setIsDeleting(true);
    try {
      await deleteChannelGroup(selectedGroupId);
      toast.success(`Đã xoá nhóm "${group?.name}"`);
      await loadData();
      setSelectedGroupId(null);
      setIsCreatingNew(false);
    } catch (error: any) {
      console.error('Error deleting group:', error);
      toast.error(error.response?.data?.detail || 'Không thể xoá nhóm');
    } finally {
      setIsDeleting(false);
    }
  };

  const toggleChannel = (channelId: string) => {
    setFormChannelIds((prev) =>
      prev.includes(channelId)
        ? prev.filter((id) => id !== channelId)
        : [...prev, channelId]
    );
  };

  const filteredChannels = channels.filter((c) =>
    c.page_name.toLowerCase().includes(channelSearch.toLowerCase())
  );

  const selectedGroup = selectedGroupId
    ? groups.find((g) => g.id === selectedGroupId)
    : null;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Nhóm kênh"
        subtitle="Tổ chức các Fanpage thành nhóm để quản lý dễ dàng hơn"
      />

      {isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Đang tải...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Group List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <h3 className="font-semibold text-gray-900">Danh sách nhóm</h3>
                <p className="text-sm text-gray-500 mt-1">{groups.length} nhóm</p>
              </div>

              <div className="divide-y divide-gray-200 max-h-[500px] overflow-y-auto">
                {groups.map((group) => (
                  <button
                    key={group.id}
                    onClick={() => handleSelectGroup(group)}
                    className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                      selectedGroupId === group.id ? 'bg-indigo-50 border-l-4 border-indigo-600' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-4 h-4 rounded-full flex-shrink-0"
                        style={{ backgroundColor: group.color_hex || '#3B82F6' }}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{group.name}</p>
                        <p className="text-sm text-gray-500">{group.channels.length} kênh</p>
                      </div>
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </button>
                ))}
              </div>

              {/* Add New Button */}
              <div className="p-4 border-t border-gray-200 bg-gray-50">
                <button
                  onClick={handleCreateNew}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Thêm nhóm kênh
                </button>
              </div>
            </div>
          </div>

          {/* Right: Group Form */}
          <div className="lg:col-span-2">
            {!selectedGroup && !isCreatingNew ? (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <div className="text-6xl mb-4">📁</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Chọn hoặc tạo nhóm</h3>
                <p className="text-gray-500 mb-4">
                  Chọn một nhóm từ danh sách bên trái hoặc tạo nhóm mới
                </p>
                <button
                  onClick={handleCreateNew}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  + Tạo nhóm mới
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-gray-200">
                {/* Form Header */}
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900">
                    {isCreatingNew ? 'Tạo nhóm mới' : `Chỉnh sửa: ${selectedGroup?.name}`}
                  </h3>
                </div>

                <div className="p-4 space-y-6">
                  {/* Group Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tên nhóm <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Ví dụ: Phun Xăm, Nâng Mũi..."
                      value={formName}
                      onChange={(e) => setFormName(e.target.value)}
                    />
                  </div>

                  {/* Color Picker */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Màu nhóm
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {COLOR_PRESETS.map((color) => (
                        <button
                          key={color}
                          onClick={() => setFormColor(color)}
                          className={`w-8 h-8 rounded-full border-2 transition-all ${
                            formColor === color
                              ? 'border-gray-900 scale-110'
                              : 'border-transparent hover:scale-105'
                          }`}
                          style={{ backgroundColor: color }}
                        />
                      ))}
                      <input
                        type="color"
                        value={formColor}
                        onChange={(e) => setFormColor(e.target.value)}
                        className="w-8 h-8 rounded-full cursor-pointer"
                        title="Chọn màu khác"
                      />
                    </div>
                  </div>

                  {/* Channel Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Kênh trong nhóm <span className="text-red-500">*</span>
                    </label>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Available Channels */}
                      <div className="border border-gray-200 rounded-lg overflow-hidden">
                        <div className="p-3 bg-gray-50 border-b border-gray-200">
                          <p className="text-sm font-medium text-gray-700">Tất cả kênh</p>
                          <input
                            type="text"
                            className="w-full mt-2 border border-gray-300 rounded px-3 py-1.5 text-sm"
                            placeholder="Tìm kiếm..."
                            value={channelSearch}
                            onChange={(e) => setChannelSearch(e.target.value)}
                          />
                        </div>
                        <div className="max-h-64 overflow-y-auto">
                          {filteredChannels
                            .filter((c) => !formChannelIds.includes(c.id))
                            .map((channel) => (
                              <button
                                key={channel.id}
                                onClick={() => toggleChannel(channel.id)}
                                className="w-full p-3 flex items-center gap-3 hover:bg-gray-50 border-b border-gray-100 last:border-0"
                              >
                                <img
                                  src={channel.avatar_url || 'https://via.placeholder.com/32'}
                                  alt={channel.page_name}
                                  className="w-8 h-8 rounded-full"
                                />
                                <div className="flex-1 text-left min-w-0">
                                  <p className="text-sm font-medium text-gray-900 truncate">
                                    {channel.page_name}
                                  </p>
                                  <p className="text-xs text-gray-500">{channel.page_id}</p>
                                </div>
                                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                              </button>
                            ))}
                          {filteredChannels.filter((c) => !formChannelIds.includes(c.id)).length === 0 && (
                            <p className="p-4 text-sm text-gray-500 text-center">
                              {channelSearch ? 'Không tìm thấy' : 'Tất cả kênh đã được thêm'}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Selected Channels */}
                      <div className="border border-gray-200 rounded-lg overflow-hidden">
                        <div className="p-3 bg-indigo-50 border-b border-indigo-200">
                          <p className="text-sm font-medium text-indigo-700">
                            Kênh trong nhóm ({formChannelIds.length})
                          </p>
                        </div>
                        <div className="max-h-64 overflow-y-auto">
                          {formChannelIds.map((channelId) => {
                            const channel = channels.find((c) => c.id === channelId);
                            if (!channel) return null;
                            return (
                              <button
                                key={channel.id}
                                onClick={() => toggleChannel(channel.id)}
                                className="w-full p-3 flex items-center gap-3 hover:bg-red-50 border-b border-gray-100 last:border-0 group"
                              >
                                <img
                                  src={channel.avatar_url || 'https://via.placeholder.com/32'}
                                  alt={channel.page_name}
                                  className="w-8 h-8 rounded-full"
                                />
                                <div className="flex-1 text-left min-w-0">
                                  <p className="text-sm font-medium text-gray-900 truncate">
                                    {channel.page_name}
                                  </p>
                                  <p className="text-xs text-gray-500">{channel.page_id}</p>
                                </div>
                                <svg className="w-5 h-5 text-gray-400 group-hover:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            );
                          })}
                          {formChannelIds.length === 0 && (
                            <p className="p-4 text-sm text-gray-500 text-center">
                              Chưa có kênh nào. Click vào kênh bên trái để thêm.
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Form Actions */}
                <div className="p-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
                  {!isCreatingNew && selectedGroupId && (
                    <button
                      onClick={handleDelete}
                      disabled={isDeleting}
                      className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                    >
                      {isDeleting ? 'Đang xoá...' : 'Xoá nhóm'}
                    </button>
                  )}
                  <div className="flex-1" />
                  <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                  >
                    {isSaving ? (
                      <>
                        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Đang lưu...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Lưu nhóm
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChannelGroupsSettingsPageV2;
