import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import * as SettingsAPI from '../../api/settings';
import type { Channel } from '../../api/settings';
import ConnectFacebookPageModal from '../../components/ConnectFacebookPageModal';
import { Badge, SuccessBanner, EmptyState, PageHeader, StatusSwitch } from '../../components/ui';
import { toast } from 'react-toastify';

// Helper to check if channel was created recently (within 7 days)
const isNewChannel = (createdAt: string): boolean => {
  const created = new Date(createdAt);
  const now = new Date();
  const diffDays = (now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24);
  return diffDays <= 7;
};

const ChannelsSettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChannels, setSelectedChannels] = useState<Set<string>>(new Set());
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [showSuccessBanner, setShowSuccessBanner] = useState(false);
  const [togglingChannelId, setTogglingChannelId] = useState<string | null>(null);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [autoCommentFilter, setAutoCommentFilter] = useState<'all' | 'configured' | 'not_configured'>('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await SettingsAPI.fetchChannels('facebook');
      setChannels(data);
    } catch (err: any) {
      console.error('Error loading channels:', err);
      setError(err.response?.data?.detail || 'Không thể tải danh sách kênh');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnectSuccess = () => {
    toast.success('Kết nối Fanpage thành công!', {
      autoClose: 5000,
    });
    loadChannels().then(() => {
      // Show success banner after reload
      setShowSuccessBanner(true);
    });
  };

  const handleDeleteChannel = async (channelId: string) => {
    if (!window.confirm('Bạn có chắc muốn xóa kênh này? Hành động này không thể hoàn tác.')) {
      return;
    }

    try {
      await SettingsAPI.deleteChannel(channelId);
      toast.success('Đã xóa kênh thành công');
      await loadChannels();
    } catch (err: any) {
      console.error('Error deleting channel:', err);
      toast.error(err.response?.data?.detail || 'Không thể xóa kênh');
    }
  };

  const handleToggleChannel = async (channel: Channel) => {
    setTogglingChannelId(channel.id);
    try {
      await SettingsAPI.updateChannel(channel.id, { is_active: !channel.is_active });
      toast.success(channel.is_active ? 'Đã tắt kênh' : 'Đã bật kênh');
      await loadChannels();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Không thể cập nhật trạng thái kênh');
    } finally {
      setTogglingChannelId(null);
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

  // Filter channels
  const filteredChannels = channels.filter((channel) => {
    // Search filter
    const matchesSearch = 
      channel.page_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      channel.page_id.includes(searchQuery);
    
    // Status filter
    const matchesStatus = 
      statusFilter === 'all' ||
      (statusFilter === 'active' && channel.is_active) ||
      (statusFilter === 'inactive' && !channel.is_active);
    
    // Auto comment filter (TODO: need backend support)
    const matchesAutoComment = autoCommentFilter === 'all';
    
    return matchesSearch && matchesStatus && matchesAutoComment;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Kênh đã kết nối"
        subtitle="Quản lý các kênh Facebook Page đã kết nối"
        actions={
          <button
            onClick={() => setShowConnectModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Thêm kênh
          </button>
        }
      />

      {/* Success Banner - Show after connecting */}
      {showSuccessBanner && (
        <SuccessBanner
          title="Hoàn tất kết nối Fanpage"
          description="Tiếp theo, hãy cấu hình Nhóm kênh và Cài đặt đăng bài & bình luận để tự động hoá Fanpage này."
          icon="🎉"
          onDismiss={() => setShowSuccessBanner(false)}
          actions={[
            {
              label: 'Gán vào Nhóm kênh',
              onClick: () => navigate('/settings/channel-groups'),
              variant: 'primary',
            },
            {
              label: 'Thiết lập đăng bài & bình luận',
              onClick: () => navigate('/settings/posting'),
              variant: 'secondary',
            },
          ]}
        />
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
          <span className="text-red-800">{error}</span>
          <button className="text-red-600 hover:text-red-800" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Toolbar */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex-1 flex gap-3 items-center flex-wrap">
            {/* Search */}
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Tìm kiếm kênh..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 w-64"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            {/* Filter Button */}
            <div className="relative">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${
                  showFilters ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                Bộ lọc
              </button>
              
              {/* Filter Dropdown */}
              {showFilters && (
                <div className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-10">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Trạng thái kênh</label>
                      <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value as any)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                      >
                        <option value="all">Tất cả</option>
                        <option value="active">Đang bật</option>
                        <option value="inactive">Đang tắt</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Auto bình luận</label>
                      <select
                        value={autoCommentFilter}
                        onChange={(e) => setAutoCommentFilter(e.target.value as any)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                      >
                        <option value="all">Tất cả</option>
                        <option value="configured">Đã cấu hình</option>
                        <option value="not_configured">Chưa cấu hình</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Stats */}
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>{channels.length} kênh</span>
            <span>•</span>
            <span>{channels.filter(c => c.is_active).length} đang hoạt động</span>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Đang tải danh sách kênh...</p>
        </div>
      ) : filteredChannels.length === 0 ? (
        /* Empty State */
        <div className="bg-white rounded-xl border border-gray-200">
          <EmptyState
            icon="📺"
            title={searchQuery ? 'Không tìm thấy kênh nào' : 'Chưa có kênh nào được kết nối'}
            description={
              searchQuery
                ? 'Thử tìm kiếm với từ khóa khác'
                : 'Kết nối Fanpage Facebook để bắt đầu quản lý và tự động hoá nội dung.'
            }
            action={
              !searchQuery
                ? {
                    label: '+ Kết nối Fanpage đầu tiên',
                    onClick: () => setShowConnectModal(true),
                  }
                : undefined
            }
          />
        </div>
      ) : (
        /* Channels Table */
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    checked={selectedChannels.size === filteredChannels.length && filteredChannels.length > 0}
                    onChange={handleSelectAll}
                  />
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Kênh</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">ID</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Người phụ trách</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Trạng thái</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-900">Hành động</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredChannels.map((channel) => (
                <tr key={channel.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-4">
                    <input
                      type="checkbox"
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      checked={selectedChannels.has(channel.id)}
                      onChange={() => handleToggleSelect(channel.id)}
                    />
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-3">
                      <img
                        src={channel.avatar_url || 'https://via.placeholder.com/40'}
                        alt={channel.page_name}
                        className="w-10 h-10 rounded-full object-cover border border-gray-200"
                      />
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900">{channel.page_name}</span>
                          {isNewChannel(channel.created_at) && (
                            <Badge variant="info" size="sm">Mới</Badge>
                          )}
                        </div>
                        <div className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                          <span>📘</span>
                          <span>Facebook Page</span>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-gray-600 font-mono bg-gray-100 px-2 py-1 rounded">
                      {channel.page_id}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <button className="text-sm text-indigo-600 hover:text-indigo-800 hover:underline">
                      {channel.page_username || 'Gán người phụ trách'}
                    </button>
                  </td>
                  <td className="px-4 py-4">
                    <StatusSwitch
                      checked={channel.is_active}
                      onChange={() => handleToggleChannel(channel)}
                      loading={togglingChannelId === channel.id}
                    />
                  </td>
                  <td className="px-4 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => navigate(`/settings/posting`)}
                        className="px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                      >
                        Cấu hình
                      </button>
                      <button
                        onClick={() => handleDeleteChannel(channel.id)}
                        className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        Xóa
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Bulk Actions */}
      {selectedChannels.size > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-4">
          <span className="font-medium">Đã chọn {selectedChannels.size} kênh</span>
          <div className="h-4 w-px bg-gray-600"></div>
          <button className="hover:text-indigo-300 transition-colors">Thao tác hàng loạt</button>
          <button
            className="hover:text-gray-300 transition-colors"
            onClick={() => setSelectedChannels(new Set())}
          >
            Bỏ chọn
          </button>
        </div>
      )}

      {/* Connect Facebook Page Modal */}
      <ConnectFacebookPageModal
        open={showConnectModal}
        onClose={() => setShowConnectModal(false)}
        onSuccess={handleConnectSuccess}
      />
    </div>
  );
};

export default ChannelsSettingsPage;
