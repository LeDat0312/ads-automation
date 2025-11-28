/**
 * Types cho Ad Studio
 * Định nghĩa các types dùng chung cho hệ thống quản lý nội dung quảng cáo
 */

export type AssetPlatform = 'tiktok' | 'facebook' | 'other';

export type Asset = {
  id: string;
  platform: AssetPlatform;
  sourceUrl: string;
  videoUrl: string;           // Now points to local file: /media/ad_studio/{id}.mp4
  thumbnailUrl: string;       // Now points to local file: /media/ad_studio/{id}.jpg
  captionOriginal: string;
  duration?: number;
  hashtags?: string[];
  note?: string;
  videoSizeMb?: number;       // NEW - for display "HD (No watermark) - 12.5 MB"
  videoTitle?: string;        // NEW - user can set custom title
};

export type CallToAction = 
  | 'SEND_MESSAGE' 
  | 'LEARN_MORE' 
  | 'CALL_NOW' 
  | 'NONE';

export const CTA_OPTIONS: Record<CallToAction, string> = {
  SEND_MESSAGE: 'Gửi tin nhắn',
  LEARN_MORE: 'Xem thêm',
  CALL_NOW: 'Gọi ngay',
  NONE: 'Không dùng nút',
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
  videoTitle?: string;        // NEW
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
  sourceUrl?: string;
  videoTitle?: string;        // NEW
  caption: string;
  language: Language;
  ctaText: string;            // Now uses CallToAction type
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
  platform?: string;
};
