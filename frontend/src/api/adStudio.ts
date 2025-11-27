import { Asset, SchedulePayload } from '../types/adStudio';

/**
 * QUAN TRỌNG - BẢO MẬT APIFY API KEY:
 * 
 * - Frontend KHÔNG BAO GIỜ lưu trữ hoặc biết Apify API key
 * - Admin cấu hình Apify API key TẠI /settings (mục "Cấu hình Apify API key")
 * - Backend đọc key từ database/environment và dùng chung cho tất cả user
 * - Frontend chỉ gọi API nội bộ của backend, backend sẽ xử lý việc gọi Apify
 * 
 * Luồng hoạt động:
 * 1. User dán link TikTok/Facebook vào frontend
 * 2. Frontend gọi POST /api/tiktok/scrape hoặc /api/facebook/scrape
 * 3. Backend lấy Apify API key từ cấu hình hệ thống
 * 4. Backend gọi Apify actor tương ứng với key đó
 * 5. Backend parse kết quả và trả về object Asset cho frontend
 */

const API_BASE_URL = '/api';

/**
 * Gọi backend để lấy video + caption từ TikTok
 * Backend sẽ dùng Apify API key từ /settings để gọi TikTok Data Extractor actor
 */
export async function fetchTiktokAsset(url: string, note?: string): Promise<Asset> {
  try {
    const response = await fetch(`${API_BASE_URL}/tiktok/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, note }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const asset: Asset = await response.json();
    return asset;
  } catch (error) {
    console.error('[fetchTiktokAsset] Error:', error);
    
    // Mock data for development/testing
    console.warn('[fetchTiktokAsset] Using mock data');
    return {
      id: `tiktok-${Date.now()}`,
      platform: 'tiktok',
      sourceUrl: url,
      videoUrl: 'https://example.com/mock-video.mp4',
      thumbnailUrl: 'https://via.placeholder.com/300x400',
      captionOriginal: 'สวัสดีค่ะ! วันนี้เรามาแชร์เคล็ดลับดูแลผิวกันนะคะ 🌸✨\n\n#skincare #beauty #thailand',
      duration: 45,
      hashtags: ['skincare', 'beauty', 'thailand'],
      note,
    };
  }
}

/**
 * Gọi backend để lấy video + caption từ Facebook
 * Backend sẽ dùng Apify API key từ /settings để gọi Facebook actor
 */
export async function fetchFacebookAsset(url: string, note?: string): Promise<Asset> {
  try {
    const response = await fetch(`${API_BASE_URL}/facebook/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, note }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const asset: Asset = await response.json();
    return asset;
  } catch (error) {
    console.error('[fetchFacebookAsset] Error:', error);
    
    // Mock data for development/testing
    console.warn('[fetchFacebookAsset] Using mock data');
    return {
      id: `facebook-${Date.now()}`,
      platform: 'facebook',
      sourceUrl: url,
      videoUrl: 'https://example.com/mock-fb-video.mp4',
      thumbnailUrl: 'https://via.placeholder.com/300x400',
      captionOriginal: 'Khuyến mãi đặc biệt! Giảm giá 50% cho tất cả sản phẩm 🎉\n\n#sale #promotion #shopping',
      note,
    };
  }
}

/**
 * Gọi backend để lên lịch đăng bài
 * Backend sẽ lưu thông tin vào database và xử lý job schedule
 */
export async function schedulePost(payload: SchedulePayload): Promise<void> {
  try {
    // Chuẩn bị FormData nếu có file upload
    let body: FormData | string;
    
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
      body = JSON.stringify(payload);
    }

    const response = await fetch(`${API_BASE_URL}/posts/schedule`, {
      method: 'POST',
      headers: payload.thumbnailFile || payload.customVideoFile 
        ? {} 
        : { 'Content-Type': 'application/json' },
      body,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    console.log('[schedulePost] Success');
  } catch (error) {
    console.error('[schedulePost] Error:', error);
    
    // Mock cho development
    console.warn('[schedulePost] Mock mode - simulating success');
    return new Promise((resolve) => {
      setTimeout(() => {
        alert('Đã lưu vào lịch đăng thành công!');
        resolve();
      }, 1000);
    });
  }
}

/**
 * Lấy danh sách assets đã lưu
 * Bao gồm cả assets từ extension và assets đã tải về
 */
export async function getAssets(): Promise<Asset[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/assets`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const assets: Asset[] = await response.json();
    return assets;
  } catch (error) {
    console.error('[getAssets] Error:', error);
    return [];
  }
}

/**
 * Lấy danh sách bài đăng
 */
export async function getPosts(filters?: { status?: string; platform?: string }): Promise<any[]> {
  try {
    const queryParams = new URLSearchParams();
    if (filters?.status) queryParams.append('status', filters.status);
    if (filters?.platform) queryParams.append('platform', filters.platform);

    const response = await fetch(`${API_BASE_URL}/posts?${queryParams.toString()}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const posts = await response.json();
    return posts;
  } catch (error) {
    console.error('[getPosts] Error:', error);
    return [];
  }
}

/**
 * Lấy danh sách fanpages
 */
export async function getFanpages(): Promise<any[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/fanpages`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const fanpages = await response.json();
    return fanpages;
  } catch (error) {
    console.error('[getFanpages] Error:', error);
    return [];
  }
}
