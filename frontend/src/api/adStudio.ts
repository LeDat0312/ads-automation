// NOTE: AdStudio - Updated to remove mock data and handle errors properly
import { Asset, SchedulePayload } from '../types/adStudio';

const API_BASE_URL = '/api';

/**
 * Backend response cho scrape endpoint
 */
interface ScrapeResponse {
  success: boolean;
  code: 'OK' | 'INVALID_URL' | 'UPSTREAM_ERROR' | 'PRIVATE_VIDEO' | 'UNKNOWN_ERROR';
  message: string;
  data?: Asset;
}

/**
 * API Error với detail code
 */
class ApiError extends Error {
  detail: string;
  status: number;
  
  constructor(message: string, detail: string, status: number) {
    super(message);
    this.detail = detail;
    this.status = status;
    this.name = 'ApiError';
  }
}

/**
 * Gọi backend để lấy video + caption từ TikTok
 * NOTE: AdStudio - Now handles ScrapeResponse format
 */
export async function fetchTiktokAsset(url: string, note?: string): Promise<Asset> {
  const response = await fetch(`${API_BASE_URL}/tiktok/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, note }),
  });

  const result: ScrapeResponse = await response.json();
  
  if (!result.success || !result.data) {
    throw new ApiError(
      result.message,
      result.code,
      response.status
    );
  }
  
  // NOTE: AdStudio - Debug log to verify API response
  console.log('[AdStudio] TikTok asset from API:', {
    id: result.data.id,
    platform: result.data.platform,
    videoUrl: result.data.videoUrl,
    thumbnailUrl: result.data.thumbnailUrl,
    duration: result.data.duration,
    hashtags: result.data.hashtags,
  });
  
  return result.data;
}

/**
 * Gọi backend để lấy video + caption từ Facebook
 * NOTE: AdStudio - No more mock fallback
 */
export async function fetchFacebookAsset(url: string, note?: string): Promise<Asset> {
  const response = await fetch(`${API_BASE_URL}/facebook/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, note }),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = data.detail || 'UNKNOWN_ERROR';
    throw new ApiError(
      `HTTP error! status: ${response.status}`,
      detail,
      response.status
    );
  }

  const asset: Asset = await response.json();
  return asset;
}

/**
 * Gọi backend để lên lịch đăng bài
 * NOTE: AdStudio - No more mock
 */
export async function schedulePost(payload: SchedulePayload): Promise<void> {
  // Chuẩn bị FormData nếu có file upload
  let body: FormData | string;
  let headers: HeadersInit = {};
  
  if (payload.thumbnailFile || payload.customVideoFile) {
    const formData = new FormData();
    formData.append('assetId', payload.assetId);
    formData.append('caption', payload.caption);
    formData.append('language', payload.language);
    formData.append('ctaText', payload.ctaText);
    formData.append('targetUrl', payload.targetUrl);
    formData.append('pageIds', JSON.stringify(payload.pageIds));
    formData.append('scheduleMode', payload.scheduleMode);
    
    if (payload.scheduleTime) {
      formData.append('scheduleTime', payload.scheduleTime);
    }
    
    formData.append('thumbnailSource', payload.thumbnailSource);
    
    if (payload.thumbnailFile) {
      formData.append('thumbnailFile', payload.thumbnailFile);
    }
    
    if (payload.videoUrl) {
      formData.append('videoUrl', payload.videoUrl);
    }
    
    if (payload.customVideoFile) {
      formData.append('customVideoFile', payload.customVideoFile);
    }
    
    body = formData;
  } else {
    headers = { 'Content-Type': 'application/json' };
    body = JSON.stringify(payload);
  }

  const response = await fetch(`${API_BASE_URL}/posts/schedule`, {
    method: 'POST',
    headers,
    body,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `HTTP error! status: ${response.status}`);
  }
}

/**
 * Lấy danh sách assets đã lưu
 * NOTE: AdStudio - Real API call
 */
export async function getAssets(): Promise<Asset[]> {
  const response = await fetch(`${API_BASE_URL}/ad-studio/assets`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data.items || [];
}

/**
 * Lấy danh sách bài đăng
 * NOTE: AdStudio - Real API call
 */
export async function getPosts(filters?: { status?: string; from?: string; to?: string }): Promise<any[]> {
  const queryParams = new URLSearchParams();
  if (filters?.status) queryParams.append('status', filters.status);
  if (filters?.from) queryParams.append('from_date', filters.from);
  if (filters?.to) queryParams.append('to_date', filters.to);

  const response = await fetch(`${API_BASE_URL}/ad-studio/posts?${queryParams.toString()}`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data.items || [];
}

/**
 * Lấy summary stats cho Dashboard
 * NOTE: AdStudio - Real API call
 */
export async function getSummary(range: '7d' | '30d' = '7d'): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/ad-studio/summary?range=${range}`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Lấy danh sách fanpages
 * NOTE: AdStudio - Real API call
 */
export async function getFanpages(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/ad-studio/pages`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data.items || [];
}

/**
 * Huỷ bài đăng
 * NOTE: AdStudio - Real API call
 */
export async function cancelPost(postId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/ad-studio/posts/${postId}/cancel`, {
    method: 'PATCH',
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `HTTP error! status: ${response.status}`);
  }
}

/**
 * Xóa asset khỏi bộ sưu tập
 * NOTE: AdStudio - Delete asset and local files
 */
export async function deleteAdStudioAsset(assetId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/ad-studio/assets/${assetId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `HTTP error! status: ${response.status}`);
  }
}

/**
 * Helper để check xem error có phải APIFY_KEY_MISSING không
 */
export function isApifyKeyMissing(error: any): boolean {
  return error instanceof ApiError && error.detail === 'APIFY_KEY_MISSING';
}

/**
 * Helper để check xem error có phải APIFY_SCRAPE_FAILED không
 */
export function isApifyScrapeFailed(error: any): boolean {
  return error instanceof ApiError && error.detail === 'APIFY_SCRAPE_FAILED';
}

export { ApiError };

// Alias functions for backward compatibility with AdStudioCardV2
export const scrapeTikTok = fetchTiktokAsset;
export const scrapeFacebook = fetchFacebookAsset;

