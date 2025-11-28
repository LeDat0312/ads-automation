import React, { useState, useEffect } from 'react';
import { getGroups, createGroup, updateGroup, deleteGroup, addPageToGroup, removePageFromGroup, getPages } from '../../api/channel';
import type { ChannelGroup, FacebookPage } from '../../types/channel';

const ChannelGroups: React.FC = () => {
  const [groups, setGroups] = useState<ChannelGroup[]>([]);
  const [pages, setPages] = useState<FacebookPage[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingGroup, setEditingGroup] = useState<ChannelGroup | null>(null);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupColor, setNewGroupColor] = useState('#3B82F6');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [groupsData, pagesData] = await Promise.all([
        getGroups(),
        getPages(undefined, true) // Only enabled pages
      ]);
      setGroups(groupsData);
      setPages(pagesData);
    } catch (error) {
      console.error('Error loading data:', error);
      alert('Lỗi khi tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async () => {
    if (!newGroupName.trim()) {
      alert('Vui lòng nhập tên nhóm');
      return;
    }

    try {
      await createGroup({
        name: newGroupName,
        color: newGroupColor
      });
      setShowCreateModal(false);
      setNewGroupName('');
      setNewGroupColor('#3B82F6');
      loadData();
    } catch (error: any) {
      console.error('Error creating group:', error);
      alert(error.response?.data?.detail || 'Lỗi khi tạo nhóm');
    }
  };

  const handleEditGroup = (group: ChannelGroup) => {
    setEditingGroup(group);
    setNewGroupName(group.name);
    setNewGroupColor(group.color);
    setShowEditModal(true);
  };

  const handleUpdateGroup = async () => {
    if (!editingGroup || !newGroupName.trim()) {
      return;
    }

    try {
      await updateGroup(editingGroup.id, {
        name: newGroupName,
        color: newGroupColor
      });
      setShowEditModal(false);
      setEditingGroup(null);
      loadData();
    } catch (error: any) {
      console.error('Error updating group:', error);
      alert(error.response?.data?.detail || 'Lỗi khi cập nhật nhóm');
    }
  };

  const handleDeleteGroup = async (group: ChannelGroup) => {
    if (!confirm(`Bạn có chắc muốn xóa nhóm "${group.name}"?`)) {
      return;
    }

    try {
      await deleteGroup(group.id);
      loadData();
    } catch (error: any) {
      console.error('Error deleting group:', error);
      alert(error.response?.data?.detail || 'Lỗi khi xóa nhóm');
    }
  };

  const handleAddPageToGroup = async (group: ChannelGroup, pageId: string) => {
    try {
      await addPageToGroup(group.id, { page_id: pageId });
      loadData();
    } catch (error: any) {
      console.error('Error adding page to group:', error);
      alert(error.response?.data?.detail || 'Lỗi khi thêm page vào nhóm');
    }
  };

  const handleRemovePageFromGroup = async (itemId: string) => {
    try {
      await removePageFromGroup(itemId);
      loadData();
    } catch (error: any) {
      console.error('Error removing page from group:', error);
      alert(error.response?.data?.detail || 'Lỗi khi xóa page khỏi nhóm');
    }
  };

  const getAvailablePages = (group: ChannelGroup): FacebookPage[] => {
    const groupPageIds = new Set(group.pages.map(p => p.id));
    return pages.filter(p => !groupPageIds.has(p.id));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">👥 Nhóm Kênh</h1>
              <p className="text-gray-600">Tổ chức các fanpage thành nhóm để quản lý dễ dàng</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold shadow-md transition-colors"
            >
              ➕ Tạo Nhóm Mới
            </button>
          </div>
        </div>

        {loading ? (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-600 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Đang tải...</p>
          </div>
        ) : groups.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <p className="text-gray-500 text-lg mb-4">Chưa có nhóm nào. Hãy tạo nhóm mới để bắt đầu.</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold"
            >
              ➕ Tạo Nhóm Đầu Tiên
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groups.map((group) => (
              <div
                key={group.id}
                className="bg-white rounded-xl shadow-lg overflow-hidden"
                style={{ borderTop: `4px solid ${group.color}` }}
              >
                {/* Group Header */}
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-bold text-gray-800">{group.name}</h3>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEditGroup(group)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDeleteGroup(group)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: group.color }}
                    ></div>
                    <span className="text-xs text-gray-500">{group.pages.length} pages</span>
                  </div>
                </div>

                {/* Pages in Group */}
                <div className="p-4 max-h-64 overflow-y-auto">
                  {group.pages.length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-4">Chưa có page nào</p>
                  ) : (
                    <div className="space-y-2">
                      {group.pages.map((page) => (
                        <div
                          key={page.id}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                        >
                          <div className="flex items-center gap-2 flex-1 min-w-0">
                            {page.page_avatar ? (
                              <img
                                src={page.page_avatar}
                                alt={page.page_name}
                                className="h-8 w-8 rounded-full flex-shrink-0"
                              />
                            ) : (
                              <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0">
                                <span className="text-xs">📄</span>
                              </div>
                            )}
                            <span className="text-sm font-medium text-gray-700 truncate">
                              {page.page_name}
                            </span>
                          </div>
                          <button
                            onClick={() => {
                              if (page.item_id) {
                                if (confirm(`Xóa "${page.page_name}" khỏi nhóm?`)) {
                                  handleRemovePageFromGroup(page.item_id);
                                }
                              }
                            }}
                            className="text-red-600 hover:text-red-800 text-xs ml-2"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Add Page Dropdown */}
                <div className="p-4 border-t border-gray-200">
                  <select
                    onChange={(e) => {
                      if (e.target.value) {
                        handleAddPageToGroup(group, e.target.value);
                        e.target.value = '';
                      }
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">➕ Thêm page vào nhóm...</option>
                    {getAvailablePages(group).map((page) => (
                      <option key={page.id} value={page.id}>
                        {page.page_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Tạo Nhóm Mới</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tên nhóm</label>
                  <input
                    type="text"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.target.value)}
                    placeholder="Nhập tên nhóm..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Màu sắc</label>
                  <div className="flex gap-2">
                    {['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'].map((color) => (
                      <button
                        key={color}
                        type="button"
                        onClick={() => setNewGroupColor(color)}
                        className={`w-10 h-10 rounded-full border-2 ${
                          newGroupColor === color ? 'border-gray-800' : 'border-gray-300'
                        }`}
                        style={{ backgroundColor: color }}
                      ></button>
                    ))}
                    <input
                      type="color"
                      value={newGroupColor}
                      onChange={(e) => setNewGroupColor(e.target.value)}
                      className="w-10 h-10 rounded-full border-2 border-gray-300 cursor-pointer"
                    />
                  </div>
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewGroupName('');
                    setNewGroupColor('#3B82F6');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Hủy
                </button>
                <button
                  onClick={handleCreateGroup}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Tạo
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {showEditModal && editingGroup && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Chỉnh Sửa Nhóm</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tên nhóm</label>
                  <input
                    type="text"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Màu sắc</label>
                  <div className="flex gap-2">
                    {['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'].map((color) => (
                      <button
                        key={color}
                        type="button"
                        onClick={() => setNewGroupColor(color)}
                        className={`w-10 h-10 rounded-full border-2 ${
                          newGroupColor === color ? 'border-gray-800' : 'border-gray-300'
                        }`}
                        style={{ backgroundColor: color }}
                      ></button>
                    ))}
                    <input
                      type="color"
                      value={newGroupColor}
                      onChange={(e) => setNewGroupColor(e.target.value)}
                      className="w-10 h-10 rounded-full border-2 border-gray-300 cursor-pointer"
                    />
                  </div>
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingGroup(null);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Hủy
                </button>
                <button
                  onClick={handleUpdateGroup}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Cập nhật
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChannelGroups;

