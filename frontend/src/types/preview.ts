/**
 * preview.ts
 * Type definitions for Static Preview System
 */

export type PreviewMode = 'feed' | 'reel' | 'story';
export type PreviewDevice = 'mobile' | 'desktop';

export interface PreviewData {
  // Page Info
  pageName: string;
  pageAvatarUrl?: string;
  isVerified?: boolean;
  isSponsored?: boolean;

  // Content
  caption: string;
  thumbnailUrl?: string; // Static thumbnail image
  
  // CTA
  ctaText?: string;

  // Mock Engagement (optional)
  reactionsCount?: number;
  commentsCount?: number;
  sharesCount?: number;
}

export interface PreviewProps {
  data: PreviewData;
  variant: PreviewDevice;
}
