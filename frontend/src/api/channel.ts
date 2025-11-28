/**
 * Channel Management API Client
 * Tất cả API calls cho module Channel Management
 */

import axios from 'axios';
import type {
  FacebookPage,
  ChannelGroup,
  ChannelGroupCreate,
  ChannelGroupUpdate,
  ChannelGroupItemCreate,
  AutoCommentSchedule,
  AutoCommentScheduleCreate,
  SyncPagesResponse,
} from '../types/channel';

const API_BASE = '/api/channel';

// ==================== PAGES API ====================

export const getPages = async (search?: string, enabled?: boolean): Promise<FacebookPage[]> => {
  const params: any = {};
  if (search) params.search = search;
  if (enabled !== undefined) params.enabled = enabled;
  
  const response = await axios.get<FacebookPage[]>(`${API_BASE}/pages`, { params });
  return response.data;
};

export const syncPages = async (): Promise<SyncPagesResponse> => {
  const response = await axios.post<SyncPagesResponse>(`${API_BASE}/pages/sync`);
  return response.data;
};

export const enablePage = async (pageId: string, enabled: boolean): Promise<{ message: string }> => {
  const response = await axios.post<{ message: string }>(
    `${API_BASE}/pages/${pageId}/enable`,
    { enabled }
  );
  return response.data;
};

export const deletePage = async (pageId: string): Promise<{ message: string }> => {
  const response = await axios.delete<{ message: string }>(`${API_BASE}/pages/${pageId}`);
  return response.data;
};

// ==================== GROUPS API ====================

export const getGroups = async (): Promise<ChannelGroup[]> => {
  const response = await axios.get<ChannelGroup[]>(`${API_BASE}/groups`);
  return response.data;
};

export const createGroup = async (groupData: ChannelGroupCreate): Promise<ChannelGroup> => {
  const response = await axios.post<ChannelGroup>(`${API_BASE}/groups`, groupData);
  return response.data;
};

export const updateGroup = async (
  groupId: string,
  groupData: ChannelGroupUpdate
): Promise<ChannelGroup> => {
  const response = await axios.put<ChannelGroup>(`${API_BASE}/groups/${groupId}`, groupData);
  return response.data;
};

export const deleteGroup = async (groupId: string): Promise<{ message: string }> => {
  const response = await axios.delete<{ message: string }>(`${API_BASE}/groups/${groupId}`);
  return response.data;
};

// ==================== GROUP ITEMS API ====================

export const addPageToGroup = async (
  groupId: string,
  itemData: ChannelGroupItemCreate
): Promise<{ message: string }> => {
  const response = await axios.post<{ message: string }>(
    `${API_BASE}/groups/${groupId}/items`,
    itemData
  );
  return response.data;
};

export const removePageFromGroup = async (itemId: string): Promise<{ message: string }> => {
  const response = await axios.delete<{ message: string }>(
    `${API_BASE}/groups/items/${itemId}`
  );
  return response.data;
};

// ==================== AUTO COMMENT API ====================

export const scheduleAutoComment = async (
  scheduleData: AutoCommentScheduleCreate
): Promise<AutoCommentSchedule> => {
  const response = await axios.post<AutoCommentSchedule>(
    `${API_BASE}/auto-comment/schedule`,
    scheduleData
  );
  return response.data;
};

export const getAutoCommentSchedules = async (
  status?: string
): Promise<AutoCommentSchedule[]> => {
  const params: any = {};
  if (status) params.status = status;
  
  const response = await axios.get<AutoCommentSchedule[]>(
    `${API_BASE}/auto-comment/schedules`,
    { params }
  );
  return response.data;
};


