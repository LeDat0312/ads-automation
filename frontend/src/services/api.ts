import axios, { AxiosError } from 'axios';
import type {
  DashboardDataResponse,
  DashboardFilters,
  SettingsStatus,
  BudgetUpdateRequest,
  BudgetUpdateResponse,
  StatusUpdateRequest,
} from '@/types/dashboard';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Redirect to login if needed
      console.error('Unauthorized access');
    } else if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Dashboard API endpoints
// ============================================================================

/**
 * Get dashboard data (summary + table rows)
 * Main endpoint that returns both overview cards and detailed table data
 */
export async function getDashboardData(
  filters: DashboardFilters
): Promise<DashboardDataResponse> {
  const params: any = {
    view_mode: filters.view_mode,
    level: filters.level || 'adset',
    page: filters.page || 1,
    pageSize: filters.pageSize || 50,
    force_refresh: filters.force_refresh || 0,
  };

  // Add optional filters
  if (filters.account_ids) params.account_ids = filters.account_ids;
  if (filters.prefix) params.prefix = filters.prefix;
  if (filters.status && filters.status !== 'ALL') params.status = filters.status;
  if (filters.date_from) params.date_from = filters.date_from;
  if (filters.date_to) params.date_to = filters.date_to;
  if (filters.search) params.search = filters.search;
  if (filters.campaign_id) params.campaign_id = filters.campaign_id;

  const response = await api.get<DashboardDataResponse>('/dashboard/data', { params });
  return response.data;
}

/**
 * Get settings status
 * Check if user has configured Facebook accounts, tokens, etc.
 */
export async function getSettingsStatus(): Promise<SettingsStatus> {
  const response = await api.get<SettingsStatus>('/dashboard/settings-status');
  return response.data;
}

/**
 * Update budget for multiple adsets/campaigns
 */
export async function updateBudget(
  request: BudgetUpdateRequest
): Promise<BudgetUpdateResponse> {
  const response = await api.post<BudgetUpdateResponse>('/dashboard/budget/update', request);
  return response.data;
}

/**
 * Update status (activate/pause) for adsets/campaigns
 */
export async function updateStatus(
  request: StatusUpdateRequest
): Promise<{ success: boolean; message: string }> {
  const response = await api.post('/dashboard/status/update', request);
  return response.data;
}

/**
 * Force refresh data from Facebook API (bypass cache)
 */
export async function forceRefreshData(
  filters: DashboardFilters
): Promise<DashboardDataResponse> {
  return getDashboardData({ ...filters, force_refresh: 1 });
}

// ============================================================================
// Helper functions
// ============================================================================

/**
 * Handle API errors with user-friendly messages
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string; message?: string }>;
    
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    
    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
    
    if (axiosError.response?.status === 401) {
      return 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.';
    }
    
    if (axiosError.response?.status === 403) {
      return 'Bạn không có quyền thực hiện thao tác này.';
    }
    
    if (axiosError.response?.status === 500) {
      return 'Lỗi máy chủ. Vui lòng thử lại sau.';
    }
    
    if (axiosError.code === 'ECONNABORTED' || axiosError.message.includes('timeout')) {
      return 'Yêu cầu quá lâu. Vui lòng thử lại.';
    }
    
    if (axiosError.message === 'Network Error') {
      return 'Lỗi kết nối mạng. Vui lòng kiểm tra kết nối internet.';
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'Đã xảy ra lỗi không xác định.';
}

/**
 * Check if error is due to missing configuration
 */
export function isConfigurationError(error: unknown): boolean {
  const message = getErrorMessage(error).toLowerCase();
  return (
    message.includes('token not found') ||
    message.includes('không tìm thấy token') ||
    message.includes('configure in settings') ||
    message.includes('cấu hình')
  );
}

export default api;
