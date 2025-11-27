/**
 * Types cho Ad Studio
 * Định nghĩa các types dùng chung cho hệ thống quản lý nội dung quảng cáo
 */

export type AssetPlatform = 'tiktok' | 'facebook' | 'other';

export type Asset = {
  id: string;
  platform: AssetPlatform;
  sourceUrl: string;
  videoUrl: string;
  thumbnailUrl: string;
  captionOriginal: string;
  duration?: number;
  hashtags?: string[];
  note?: string;
};

export type ScheduleMode = 'NOW' | 'RANDOM_2H' | 'EXACT_TIME';

export type Language = 'la' | 'vi' | 'th';

export type ThumbnailSource = 'FRAME' | 'UPLOAD';

export type PostStatus = 'published' | 'scheduled' | 'draft' | 'failed' | 'cancelled';

export type Post = {
  id: string;
  caption: string;
  thumbnailUrl: string;
  channels: string[];
  scheduledTime: string;
  status: PostStatus;
  creator: string;
  videoUrl?: string;
};

export type DashboardStats = {
  totalPosts: number;
  publishedPosts: number;
  scheduledPosts: number;
  draftPosts: number;
  failedPosts: number;
};

export type SchedulePayload = {
  assetId: string;
  caption: string;
  language: Language;
  ctaText: string;
  targetUrl: string;
  pageIds: string[];
  scheduleMode: ScheduleMode;
  scheduleTime?: string;
  thumbnailSource: ThumbnailSource;
  thumbnailFile?: File;
  videoUrl?: string;
  customVideoFile?: File;
};

export type Fanpage = {
  id: string;
  name: string;
};
