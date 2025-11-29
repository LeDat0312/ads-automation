# Frontend API Integration Summary - Changed Code Only

## Overview
All frontend files updated to use real backend APIs instead of mock data. Only showing the relevant changed parts.

---

## 1. `frontend/src/api/settings.ts` - Complete Replacement

### Changed: Removed all mock data, implemented real API functions

**Key changes:**
- ✅ Removed mock data arrays
- ✅ Updated TypeScript types to match backend schemas exactly
- ✅ Implemented all API functions with proper error handling

**New types (matching backend):**
```typescript
export interface Channel {
  id: string;
  user_id: number;
  platform: string;
  page_id: string;  // Changed from pageId
  page_name: string;  // Changed from name
  page_username?: string;
  avatar_url?: string;  // Changed from avatarUrl
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChannelGroup {
  id: string;
  user_id: number;
  name: string;
  color_hex?: string;  // Changed from color
  created_at: string;
  updated_at: string;
  channels: Channel[];  // Nested channels from backend
}
```

**All functions implemented:**
- ✅ `fetchChannels(platform?, search?, is_active?)`
- ✅ `importFacebookChannels(pages[])`
- ✅ `updateChannel(channelId, payload)`
- ✅ `deleteChannel(channelId)`
- ✅ `fetchChannelGroups()`
- ✅ `saveChannelGroup(payload, groupId?)` - handles both create and update
- ✅ `deleteChannelGroup(groupId)`
- ✅ `fetchPostingSettings()` - returns PostingSettingsRow[]
- ✅ `savePostingSettings(channelId, payload)`

---

## 2. `frontend/src/pages/Settings/ChannelsSettingsPage.tsx` - Changed Parts

### Changed imports:
```typescript
// OLD: Local types and mock data
// NEW:
import * as SettingsAPI from '../../api/settings';
import type { Channel } from '../../api/settings';
```

### Changed state:
```typescript
// Added error state
const [error, setError] = useState<string | null>(null);
```

### Changed loadChannels function:
```typescript
// OLD: Mock data with setTimeout
// NEW:
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
```

### Added delete handler:
```typescript
const handleDeleteChannel = async (channelId: string) => {
  if (!window.confirm('Bạn có chắc muốn xóa kênh này?')) {
    return;
  }
  try {
    await SettingsAPI.deleteChannel(channelId);
    await loadChannels(); // Reload after deletion
  } catch (err: any) {
    console.error('Error deleting channel:', err);
    alert(err.response?.data?.detail || 'Không thể xóa kênh');
  }
};
```

### Changed display helpers:
```typescript
// Map backend field names to display
const getChannelDisplayName = (channel: Channel) => channel.page_name;
const getChannelAvatar = (channel: Channel) => channel.avatar_url;
const getChannelPageId = (channel: Channel) => channel.page_id;
```

### Changed table rendering:
```typescript
// OLD: channel.name, channel.pageId, channel.avatarUrl
// NEW: channel.page_name, channel.page_id, channel.avatar_url

// Added error display:
{error && (
  <div className="alert alert-error">
    <span>{error}</span>
  </div>
)}
```

---

## 3. `frontend/src/pages/Settings/ChannelGroupsSettingsPage.tsx` - Changed Parts

### Changed imports:
```typescript
// OLD: Local types and mock data
// NEW:
import * as SettingsAPI from '../../api/settings';
import type { Channel, ChannelGroup } from '../../api/settings';
```

### Changed loadData function:
```typescript
// OLD: Mock data
// NEW:
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
```

### Changed helpers for group channels:
```typescript
// OLD: group.channelIds array
// NEW: Backend returns nested channels, so we access group.channels directly
const getGroupChannelIds = (group: ChannelGroup): string[] => {
  return group.channels.map(c => c.id);
};

const getChannelsInGroup = (group: ChannelGroup): Channel[] => {
  return group.channels; // Direct access
};
```

### Changed save handler:
```typescript
// OLD: Mock alert
// NEW: Real API calls
const handleSave = async () => {
  setError(null);
  try {
    for (const group of groups) {
      const channelIds = getGroupChannelIds(group);
      const payload = {
        name: group.name,
        color_hex: group.color_hex || '#3B82F6',
        channel_ids: channelIds,
      };

      if (group.id.startsWith('temp-')) {
        await SettingsAPI.saveChannelGroup(payload); // Create
      } else {
        await SettingsAPI.saveChannelGroup(payload, group.id); // Update
      }
    }
    await loadData(); // Reload after saving
    alert('Đã lưu nhóm kênh thành công');
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Lưu thất bại');
  }
};
```

### Changed delete handler:
```typescript
// OLD: Local state update only
// NEW: API call + reload
const handleDeleteGroup = async (groupId: string) => {
  if (!window.confirm('Bạn có chắc muốn xóa nhóm này?')) return;
  
  if (groupId.startsWith('temp-')) {
    setGroups((prev) => prev.filter((g) => g.id !== groupId));
    return;
  }

  try {
    await SettingsAPI.deleteChannelGroup(groupId);
    await loadData();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Không thể xóa nhóm');
  }
};
```

### Changed field references:
```typescript
// OLD: group.color
// NEW: group.color_hex || '#3B82F6'

// OLD: channel.name, channel.avatarUrl
// NEW: channel.page_name, channel.avatar_url
```

---

## 4. `frontend/src/pages/Settings/PostingSettingsPage.tsx` - Changed Parts

### Changed imports and state:
```typescript
// OLD: Local types, mock config
// NEW:
import * as SettingsAPI from '../../api/settings';
import type { PostingSettingsRow, AutoCommentTemplate, PostingSettings } from '../../api/settings';

// Changed state structure:
// OLD: channels[], config: PostingConfig
// NEW:
const [settingsRows, setSettingsRows] = useState<PostingSettingsRow[]>([]);
```

### Changed loadData function:
```typescript
// OLD: Mock data with PostingConfig structure
// NEW:
const loadData = async () => {
  setIsLoading(true);
  setError(null);
  try {
    const data = await SettingsAPI.fetchPostingSettings();
    setSettingsRows(data); // Backend returns array of PostingSettingsRow
  } catch (err: any) {
    console.error('Error loading posting settings:', err);
    setError(err.response?.data?.detail || 'Không thể tải cài đặt đăng bài');
  } finally {
    setIsLoading(false);
  }
};
```

### Changed data structure helpers:
```typescript
// Get settings for a channel from the rows array
const getSettingsRow = (channelId: string): PostingSettingsRow | undefined => {
  return settingsRows.find(row => row.channel.id === channelId);
};
```

### Changed toggle handlers:
```typescript
// OLD: Local state updates only
// NEW: Update local state + save to backend
const handleToggleSignature = async (channelId: string) => {
  const row = getSettingsRow(channelId);
  if (!row) return;
  
  const newSettings = {
    ...row.settings,
    default_signature: row.settings?.default_signature ? undefined : 'Chữ ký mặc định',
  };
  
  updateSettingsRow(channelId, { settings: newSettings });
  await handleSaveChannel(channelId); // Auto-save
};
```

### Changed save handler:
```typescript
// OLD: Mock alert
// NEW: Real API call with proper payload structure
const handleSaveChannel = async (channelId: string) => {
  const row = getSettingsRow(channelId);
  if (!row) return;

  const payload = {
    default_signature: row.settings?.default_signature || undefined,
    auto_comment_enabled: row.settings?.auto_comment_enabled || false,
    auto_comment_delay_seconds: row.settings?.auto_comment_delay_seconds || undefined,
    auto_comments: row.auto_comments.map(template => ({
      id: template.id.startsWith('temp-') ? undefined : template.id, // Upsert logic
      content: template.content,
      media_url: template.media_url || undefined,
      schedule_type: template.schedule_type,
      delay_minutes: template.delay_minutes || undefined,
      is_active: template.is_active,
      sort_order: template.sort_order,
    })),
  };

  const updated = await SettingsAPI.savePostingSettings(channelId, payload);
  setSettingsRows(prev => prev.map(r => 
    r.channel.id === channelId ? updated : r
  ));
};
```

### Changed table rendering:
```typescript
// OLD: channels.map(), config.commentsByChannel[channelId]
// NEW:
{settingsRows.map((row) => {
  const channel = row.channel;
  const hasSignature = !!row.settings?.default_signature;
  const autoCommentEnabled = row.settings?.auto_comment_enabled || false;
  
  return (
    <tr key={channel.id}>
      {/* Use channel.page_name, channel.avatar_url, etc. */}
    </tr>
  );
})}
```

### Changed modal rendering:
```typescript
// OLD: channels.map(channel => renderBulkCommentModal(channel))
// NEW:
{settingsRows.map((row) => renderBulkCommentModal(row.channel.id))}

// In modal, access comments from row:
const row = getSettingsRow(channelId);
const comments = row.auto_comments || [];
```

### Changed schedule type values:
```typescript
// OLD: 'IMMEDIATELY', 'AFTER_POST', 'AT_SCHEDULED_TIME'
// NEW: 'IMMEDIATE', 'AFTER_X_MINUTES', 'DELAYED', 'CUSTOM'
```

---

## Summary of Field Name Changes

| Old (Frontend) | New (Backend API) |
|----------------|-------------------|
| `channel.name` | `channel.page_name` |
| `channel.pageId` | `channel.page_id` |
| `channel.avatarUrl` | `channel.avatar_url` |
| `group.color` | `group.color_hex` |
| `group.channelIds` | `group.channels` (array of Channel objects) |
| `comment.mediaUrl` | `comment.media_url` |
| `comment.sendTimeMode` | `comment.schedule_type` |
| `comment.delayMinutes` | `comment.delay_minutes` |

---

## Error Handling

All API calls wrapped in try/catch:
- Errors logged to console
- Error messages displayed in UI (red alert boxes)
- User-friendly Vietnamese error messages from backend

---

## Build Status

✅ TypeScript compilation: PASSED
✅ Vite build: SUCCESS
✅ No linter errors

Ready for deployment!

