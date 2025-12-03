/**
 * preview.ts
 * Type definitions for Static Preview System
 */

export type PreviewMode = 'feed' | 'reel' | 'story';
export type PreviewDevice = 'mobile' | 'desktop';
export type CtaType = 'MESSENGER' | 'WHATSAPP' | 'CALL' | 'LEARN_MORE';

export interface PreviewData {
  // Page Info
  pageName: string;
  pageAvatarUrl?: string;
  isVerified?: boolean;
  isSponsored?: boolean;

  // Content
  caption: string;
  videoTitle?: string; // Chỉ cho Feed
  thumbnailUrl?: string; // Static thumbnail image
  
  // CTA
  ctaType?: CtaType;
  ctaText?: string; // Deprecated - use getCtaLabel instead

  // Mock Engagement (optional)
  reactionsCount?: number;
  commentsCount?: number;
  sharesCount?: number;
}

export interface PreviewProps {
  data: PreviewData;
  variant: PreviewDevice;
}

/**
 * Get CTA button label based on CTA type
 * Always returns Vietnamese text matching Facebook UI
 */
export function getCtaLabel(ctaType?: CtaType): string {
  if (!ctaType) return 'Gửi tin nhắn'; // Default
  
  switch (ctaType) {
    case 'MESSENGER':
      return 'Gửi tin nhắn';
    case 'WHATSAPP':
      return 'Nhắn tin WhatsApp';
    case 'CALL':
      return 'Gọi ngay';
    case 'LEARN_MORE':
      return 'Tìm hiểu thêm';
    default:
      return 'Gửi tin nhắn';
  }
}
