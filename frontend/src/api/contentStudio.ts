/**
 * Content Studio API Client
 * Tất cả API calls cho module Content Studio
 */

import axios from 'axios';
import type {
  SearchContentRequest,
  SearchContentResponse,
  ContentSource,
  AiRewriteRequest,
  AiRewriteResponse,
  SchedulePostRequest,
  SchedulePostResponse,
  PostsFilterParams,
  PostsListResponse,
  ScheduledPost,
  UpdatePostRequest,
  DashboardStats,
  Stats7DaysResponse,
  FacebookPage,
  Collection,
  CollectionItem,
  AddToCollectionRequest,
  UploadMediaResponse,
  ContentVariant,
} from '../types/contentStudio';

const API_BASE = '/api/content-studio';

// ==================== SEARCH & FETCH ====================

export const searchContent = async (params: SearchContentRequest): Promise<SearchContentResponse> => {
  const response = await axios.post<SearchContentResponse>(`${API_BASE}/search`, params);
  return response.data;
};

export const fetchFromUrls = async (urls: string[]): Promise<ContentSource[]> => {
  const response = await axios.post<{ items: ContentSource[] }>(`${API_BASE}/fetch-urls`, { urls });
  return response.data.items;
};

export const uploadMedia = async (files: File[], caption?: string): Promise<UploadMediaResponse> => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  if (caption) formData.append('caption', caption);
  
  const response = await axios.post<UploadMediaResponse>(`${API_BASE}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// ==================== COLLECTIONS ====================

export const getCollections = async (): Promise<Collection[]> => {
  const response = await axios.get<{ items: Collection[] }>(`${API_BASE}/collections`);
  return response.data.items;
};

export const getCollection = async (id: string): Promise<Collection> => {
  const response = await axios.get<Collection>(`${API_BASE}/collections/${id}`);
  return response.data;
};

export const getCollectionItems = async (collectionId: string): Promise<CollectionItem[]> => {
  const response = await axios.get<{ items: CollectionItem[] }>(`${API_BASE}/collections/${collectionId}/items`);
  return response.data.items;
};

export const createCollection = async (name: string, description?: string): Promise<Collection> => {
  const response = await axios.post<Collection>(`${API_BASE}/collections`, { name, description });
  return response.data;
};

export const addToCollection = async (request: AddToCollectionRequest): Promise<void> => {
  await axios.post(`${API_BASE}/collections/add-items`, request);
};

export const removeFromCollection = async (collectionId: string, sourceIds: string[]): Promise<void> => {
  await axios.post(`${API_BASE}/collections/${collectionId}/remove-items`, { sourceIds });
};

// ==================== CONTENT VARIANTS ====================

export const getContentVariants = async (sourceId?: string): Promise<ContentVariant[]> => {
  const params = sourceId ? { sourceId } : {};
  const response = await axios.get<{ items: ContentVariant[] }>(`${API_BASE}/variants`, { params });
  return response.data.items;
};

export const getContentVariant = async (id: string): Promise<ContentVariant> => {
  const response = await axios.get<ContentVariant>(`${API_BASE}/variants/${id}`);
  return response.data;
};

export const createContentVariant = async (data: {
  sourceId: string;
  title: string;
  caption: string;
  captionLao: string;
  hashtags: string[];
  callToAction?: string;
}): Promise<ContentVariant> => {
  const response = await axios.post<ContentVariant>(`${API_BASE}/variants`, data);
  return response.data;
};

export const updateContentVariant = async (id: string, data: Partial<ContentVariant>): Promise<ContentVariant> => {
  const response = await axios.patch<ContentVariant>(`${API_BASE}/variants/${id}`, data);
  return response.data;
};

export const deleteContentVariant = async (id: string): Promise<void> => {
  await axios.delete(`${API_BASE}/variants/${id}`);
};

// ==================== AI SERVICES ====================

export const rewriteCaption = async (request: AiRewriteRequest): Promise<AiRewriteResponse> => {
  const response = await axios.post<AiRewriteResponse>(`${API_BASE}/ai/rewrite-caption`, request);
  return response.data;
};

// ==================== FACEBOOK PAGES ====================

export const getFacebookPages = async (groupTag?: string): Promise<FacebookPage[]> => {
  const params = groupTag ? { groupTag } : {};
  const response = await axios.get<{ items: FacebookPage[] }>(`${API_BASE}/facebook/pages`, { params });
  return response.data.items;
};

export const syncFacebookPages = async (): Promise<FacebookPage[]> => {
  const response = await axios.post<{ items: FacebookPage[] }>(`${API_BASE}/facebook/pages/sync`);
  return response.data.items;
};

// ==================== SCHEDULER ====================

export const schedulePosts = async (request: SchedulePostRequest): Promise<SchedulePostResponse> => {
  const response = await axios.post<SchedulePostResponse>(`${API_BASE}/scheduler/schedule-post`, request);
  return response.data;
};

export const getScheduledPosts = async (params: PostsFilterParams): Promise<PostsListResponse> => {
  const response = await axios.get<PostsListResponse>(`${API_BASE}/scheduler/posts`, { params });
  return response.data;
};

export const getScheduledPost = async (id: string): Promise<ScheduledPost> => {
  const response = await axios.get<ScheduledPost>(`${API_BASE}/scheduler/posts/${id}`);
  return response.data;
};

export const updateScheduledPost = async (id: string, data: UpdatePostRequest): Promise<ScheduledPost> => {
  const response = await axios.patch<ScheduledPost>(`${API_BASE}/scheduler/posts/${id}`, data);
  return response.data;
};

export const deleteScheduledPost = async (id: string): Promise<void> => {
  await axios.delete(`${API_BASE}/scheduler/posts/${id}`);
};

export const publishPostNow = async (id: string): Promise<ScheduledPost> => {
  const response = await axios.post<ScheduledPost>(`${API_BASE}/scheduler/posts/${id}/publish-now`);
  return response.data;
};

// ==================== STATS & DASHBOARD ====================

export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await axios.get<DashboardStats>(`${API_BASE}/scheduler/stats/dashboard`);
  return response.data;
};

export const get7DaysStats = async (): Promise<Stats7DaysResponse> => {
  const response = await axios.get<Stats7DaysResponse>(`${API_BASE}/scheduler/stats/7d`);
  return response.data;
};
