/**
 * Settings API Client - Channel Management
 * API calls cho module Quản lý kênh trong Settings
 */

import axios from 'axios';

// ==================== TYPES ====================

export interface Channel {
  id: string;
  name: string;
  pageId: string;
  avatarUrl?: string;
  ownerName?: string;
  platform: 'facebook';
}

export interface ChannelGroup {
  id: string;
  name: string;
  color: string;
  channelIds: string[];
}

export interface ChannelGroupCreate {
  name: string;
  color: string;
  channelIds?: string[];
}

export interface ChannelGroupUpdate {
  name?: string;
  color?: string;
  channelIds?: string[];
}

export interface BulkComment {
  id: string;
  content: string;
  mediaUrl?: string;
  delayMinutes?: number;
  sendTimeMode: 'IMMEDIATELY' | 'AFTER_POST' | 'AT_SCHEDULED_TIME';
}

export interface PostingConfig {
  shareToStory: boolean;
  commentsByChannel: Record<string, BulkComment[]>;
}

// ==================== CHANNELS API ====================

/**
 * Fetch list of connected channels
 * GET /api/channels
 */
export const fetchChannels = async (): Promise<Channel[]> => {
  try {
    const response = await axios.get<Channel[]>('/api/channels');
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      console.warn('API /api/channels not found, using mock data');
      return [];
    }
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
    if (error.response?.status === 404) {
      console.warn('API /api/channel-groups not found, using mock data');
      return [];
    }
    throw error;
  }
};

/**
 * Create a new channel group
 * POST /api/channel-groups
 */
export const createChannelGroup = async (
  groupData: ChannelGroupCreate
): Promise<ChannelGroup> => {
  try {
    const response = await axios.post<ChannelGroup>('/api/channel-groups', groupData);
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      console.warn('API /api/channel-groups not found');
      throw new Error('API endpoint not available');
    }
    throw error;
  }
};

/**
 * Update a channel group
 * PUT /api/channel-groups/{id}
 */
export const updateChannelGroup = async (
  groupId: string,
  groupData: ChannelGroupUpdate
): Promise<ChannelGroup> => {
  try {
    const response = await axios.put<ChannelGroup>(
      `/api/channel-groups/${groupId}`,
      groupData
    );
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      console.warn('API /api/channel-groups/{id} not found');
      throw new Error('API endpoint not available');
    }
    throw error;
  }
};

/**
 * Delete a channel group
 * DELETE /api/channel-groups/{id}
 */
export const deleteChannelGroup = async (groupId: string): Promise<void> => {
  try {
    await axios.delete(`/api/channel-groups/${groupId}`);
  } catch (error: any) {
    if (error.response?.status === 404) {
      console.warn('API DELETE /api/channel-groups/{id} not found');
      throw new Error('API endpoint not available');
    }
    throw error;
  }
};

// ==================== POSTING CONFIG API ====================

/**
 * Fetch posting configuration
 * GET /api/posting/config
 */
export const fetchPostingConfig = async (): Promise<PostingConfig> => {
  try {
    const response = await axios.get<PostingConfig>('/api/posting/config');
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      console.warn('API /api/posting/config not found, using default config');
      return {
        shareToStory: false,
        commentsByChannel: {},
      };
    }
    throw error;
  }
};

/**
 * Save posting configuration
 * PUT /api/posting/config
 */
export const savePostingConfig = async (
  config: PostingConfig
): Promise<PostingConfig> => {
  try {
    const response = await axios.put<PostingConfig>('/api/posting/config', config);
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      console.warn('API PUT /api/posting/config not found');
      throw new Error('API endpoint not available');
    }
    throw error;
  }
};

