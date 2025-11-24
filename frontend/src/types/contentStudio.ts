/**
 * Content Studio Type Definitions
 * Module quản lý nội dung và lên lịch đăng bài tự động
 */

// ==================== ENUMS ====================

export enum ContentSourceType {
  FACEBOOK_ADS_LIBRARY = 'facebook_ads_library',
  FACEBOOK_POST = 'facebook_post',
  TIKTOK = 'tiktok',
  COLLECTION = 'collection',
  MANUAL_UPLOAD = 'manual_upload'
}

export enum MediaType {
  IMAGE = 'image',
  VIDEO = 'video',
  CAROUSEL = 'carousel'
}

export enum PostStatus {
  DRAFT = 'draft',
  SCHEDULED = 'scheduled',
  PUBLISHING = 'publishing',
  PUBLISHED = 'published',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum ScheduleType {
  NOW = 'now',
  FIXED = 'fixed',
  RANDOM = 'random'
}

export enum AiRewriteMode {
  TRANSLATE = 'translate',
  REWRITE_SALON_STYLE = 'rewrite_salon_style',
  GENERATE_VARIANTS = 'generate_variants'
}

// ==================== ENTITIES ====================

export interface MediaAsset {
  id: string;
  url: string;
  thumbnailUrl?: string;
  type: MediaType;
  width?: number;
  height?: number;
  duration?: number; // For videos (in seconds)
  size?: number; // File size in bytes
  filename?: string;
  createdAt: string;
}

export interface ContentSource {
  id: string;
  sourceType: ContentSourceType;
  sourceUrl?: string;
  sourceId?: string; // TikTok video ID, Facebook post ID, etc.
  caption: string;
  captionLao?: string;
  media: MediaAsset[];
  authorName?: string;
  authorAvatar?: string;
  platform?: string;
  views?: number;
  likes?: number;
  comments?: number;
  shares?: number;
  fetchedAt: string;
  createdAt: string;
  userId: number;
}

export interface ContentVariant {
  id: string;
  sourceId: string;
  title: string;
  caption: string;
  captionLao: string;
  hashtags: string[];
  callToAction?: string;
  media: MediaAsset[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface FacebookPage {
  id: string;
  name: string;
  accessToken: string;
  avatar?: string;
  followers?: number;
  category?: string;
  groupTag?: string; // Nhóm fanpage (VD: "Thẩm mỹ viện Lào", "Chi nhánh 1")
  isActive: boolean;
  lastSyncAt?: string;
  userId: number;
}

export interface ScheduledPost {
  id: string;
  contentVariantId: string;
  pageId: string;
  scheduledAt: string;
  publishedAt?: string;
  status: PostStatus;
  error?: string;
  fbPostId?: string;
  fbPostUrl?: string;
  reach?: number;
  engagement?: number;
  createdBy: number;
  createdAt: string;
  updatedAt: string;
  
  // Populated fields
  contentVariant?: ContentVariant;
  page?: FacebookPage;
}

// ==================== REQUEST/RESPONSE DTOs ====================

export interface SearchContentRequest {
  query?: string;
  sourceType?: ContentSourceType;
  urls?: string[]; // Danh sách link để crawl
  page?: number;
  pageSize?: number;
}

export interface SearchContentResponse {
  items: ContentSource[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface AiRewriteRequest {
  sourceCaption: string;
  sourceLang?: string; // Default: 'vi'
  targetLang: string; // 'lo' for Lao
  mode: AiRewriteMode;
  customPrompt?: string;
}

export interface AiRewriteResponse {
  originalCaption: string;
  rewrittenCaption: string;
  variants?: string[]; // For GENERATE_VARIANTS mode
  tokensUsed?: number;
  modelUsed?: string; // 'gemini' or 'chatgpt'
}

export interface SchedulePostRequest {
  contentVariantId: string;
  pageIds: string[];
  scheduleType: ScheduleType;
  fixedTime?: string; // ISO datetime
  randomRangeMinutes?: number; // For random schedule
}

export interface SchedulePostResponse {
  success: boolean;
  scheduledPosts: ScheduledPost[];
  errors?: {
    pageId: string;
    error: string;
  }[];
}

export interface PostsFilterParams {
  status?: PostStatus;
  pageId?: string;
  startDate?: string;
  endDate?: string;
  search?: string;
  page?: number;
  pageSize?: number;
}

export interface PostsListResponse {
  items: ScheduledPost[];
  total: number;
  page: number;
  pageSize: number;
}

export interface UpdatePostRequest {
  caption?: string;
  captionLao?: string;
  scheduledAt?: string;
  status?: PostStatus;
}

export interface DashboardStats {
  postsToday: number;
  postsScheduled: number;
  postsPublishedToday: number;
  postsFailedToday: number;
}

export interface DailyStats {
  date: string;
  postsCount: number;
  publishedCount: number;
  failedCount: number;
}

export interface Stats7DaysResponse {
  days: DailyStats[];
  total: number;
}

// ==================== COLLECTION ====================

export interface Collection {
  id: string;
  name: string;
  description?: string;
  itemCount: number;
  coverImage?: string;
  isDefault: boolean;
  createdAt: string;
  userId: number;
}

export interface CollectionItem {
  id: string;
  collectionId: string;
  sourceId: string;
  addedAt: string;
  
  // Populated
  source?: ContentSource;
}

export interface AddToCollectionRequest {
  sourceIds: string[];
  collectionId?: string; // If not provided, add to default collection
}

// ==================== UPLOAD ====================

export interface UploadMediaRequest {
  files: File[];
  caption?: string;
}

export interface UploadMediaResponse {
  sources: ContentSource[];
  errors?: {
    filename: string;
    error: string;
  }[];
}
