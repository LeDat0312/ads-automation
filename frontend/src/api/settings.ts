/**
 * Settings API Client - Channel Management
 * Real API calls matching backend endpoints
 */

import axios from 'axios';

// ==================== TYPES (Matching Backend Schemas) ====================

export interface Channel {
  id: string;
  user_id: number;
  platform: string;
  page_id: string;
  page_name: string;
  page_username?: string;
  avatar_url?: string;
  access_token_encrypted?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChannelGroup {
  id: string;
  user_id: number;
  name: string;
  color_hex?: string;
  created_at: string;
  updated_at: string;
  channels: Channel[];
}

export interface ChannelGroupCreate {
  name: string;
  color_hex?: string;
  channel_ids?: string[];
}

export interface ChannelGroupUpdate {
  name?: string;
  color_hex?: string;
  channel_ids?: string[];
}

export interface PostingSettings {
  id: string;
  user_id: number;
  channel_id: string;
  default_signature?: string;
  auto_comment_enabled: boolean;
  auto_comment_delay_seconds?: number;
  created_at: string;
  updated_at: string;
}

export interface AutoCommentTemplate {
  id: string;
  user_id: number;
  channel_id: string;
  content: string;
  media_url?: string;
  schedule_type: string; // "IMMEDIATE", "DELAYED", "AFTER_X_MINUTES", "CUSTOM"
  delay_minutes?: number;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface PostingSettingsRow {
  channel: Channel;
  settings: PostingSettings | null;
  auto_comments: AutoCommentTemplate[];
}

export interface FacebookPageImport {
  page_id: string;
  name: string;
  avatar?: string;
  access_token?: string;
  category?: string;
}

export interface PostingSettingsPayload {
  default_signature?: string;
  auto_comment_enabled: boolean;
  auto_comment_delay_seconds?: number;
  auto_comments: Array<{
    id?: string; // If present, update existing; if not, create new
    content: string;
    media_url?: string;
    schedule_type: string;
    delay_minutes?: number;
    is_active: boolean;
    sort_order: number;
  }>;
}

// ==================== CHANNELS API ====================

/**
 * Fetch list of connected channels
 * GET /api/channels
 */
export const fetchChannels = async (
  platform?: string,
  search?: string,
  is_active?: boolean
): Promise<Channel[]> => {
  try {
    const params: any = {};
    if (platform) params.platform = platform;
    if (search) params.search = search;
    if (is_active !== undefined) params.is_active = is_active;

    const response = await axios.get<Channel[]>('/api/channels', { params });
    return response.data;
  } catch (error: any) {
    console.error('Error fetching channels:', error);
    throw error;
  }
};

/**
 * Import/upsert Facebook pages from OAuth flow
 * POST /api/channels/import-facebook
 */
export const importFacebookChannels = async (
  pages: FacebookPageImport[]
): Promise<Channel[]> => {
  try {
    const response = await axios.post<Channel[]>('/api/channels/import-facebook', pages);
    return response.data;
  } catch (error: any) {
    console.error('Error importing Facebook channels:', error);
    throw error;
  }
};

/**
 * Update a channel
 * PATCH /api/channels/{channel_id}
 */
export const updateChannel = async (
  channelId: string,
  payload: {
    page_name?: string;
    page_username?: string;
    avatar_url?: string;
    is_active?: boolean;
  }
): Promise<Channel> => {
  try {
    const response = await axios.patch<Channel>(`/api/channels/${channelId}`, payload);
    return response.data;
  } catch (error: any) {
    console.error('Error updating channel:', error);
    throw error;
  }
};

/**
 * Delete a channel
 * DELETE /api/channels/{channel_id}
 */
export const deleteChannel = async (channelId: string): Promise<void> => {
  try {
    await axios.delete(`/api/channels/${channelId}`);
  } catch (error: any) {
    console.error('Error deleting channel:', error);
    throw error;
  }
};

// ==================== CHANNEL GROUPS API ====================

/**
 * Fetch list of channel groups
 * GET /api/channel-groups
 */
export const fetchChannelGroups = async (): Promise<ChannelGroup[]> => {
  try {
    const response = await axios.get<ChannelGroup[]>('/api/channel-groups');
    return response.data;
  } catch (error: any) {
    console.error('Error fetching channel groups:', error);
    throw error;
  }
};

/**
 * Create or update a channel group
 * POST /api/channel-groups (create) or PUT /api/channel-groups/{group_id} (update)
 */
export const saveChannelGroup = async (
  groupData: ChannelGroupCreate | ChannelGroupUpdate,
  groupId?: string
): Promise<ChannelGroup> => {
  try {
    if (groupId) {
      // Update existing group
      const response = await axios.put<ChannelGroup>(
        `/api/channel-groups/${groupId}`,
        groupData
      );
      return response.data;
    } else {
      // Create new group
      const response = await axios.post<ChannelGroup>('/api/channel-groups', groupData);
      return response.data;
    }
  } catch (error: any) {
    console.error('Error saving channel group:', error);
    throw error;
  }
};

/**
 * Delete a channel group
 * DELETE /api/channel-groups/{group_id}
 */
export const deleteChannelGroup = async (groupId: string): Promise<void> => {
  try {
    await axios.delete(`/api/channel-groups/${groupId}`);
  } catch (error: any) {
    console.error('Error deleting channel group:', error);
    throw error;
  }
};

// ==================== POSTING SETTINGS API ====================

/**
 * Fetch posting settings for all channels
 * GET /api/posting/settings
 */
export const fetchPostingSettings = async (): Promise<PostingSettingsRow[]> => {
  try {
    const response = await axios.get<PostingSettingsRow[]>('/api/posting/settings');
    return response.data;
  } catch (error: any) {
    console.error('Error fetching posting settings:', error);
    throw error;
  }
};

/**
 * Save posting settings for a channel
 * PUT /api/posting/settings/{channel_id}
 */
export const savePostingSettings = async (
  channelId: string,
  payload: PostingSettingsPayload
): Promise<PostingSettingsRow> => {
  try {
    const response = await axios.put<PostingSettingsRow>(
      `/api/posting/settings/${channelId}`,
      payload
    );
    return response.data;
  } catch (error: any) {
    console.error('Error saving posting settings:', error);
    throw error;
  }
};
