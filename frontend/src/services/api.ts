import axios, { AxiosError } from 'axios';
import type {
  DashboardDataResponse,
  DashboardFilters,
  SettingsStatus,
  BudgetUpdateRequest,
  BudgetUpdateResponse,
  StatusUpdateRequest,
} from '@/types/dashboard';

// ⚠️ MOCK MODE: Set to true to use mock data without backend
const USE_MOCK_DATA = false; // Change to true to test without backend

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
  // 🎭 MOCK MODE: Return mock data if enabled
  if (USE_MOCK_DATA) {
    const { mockLeadDashboardData, mockEcommerceDashboardData } = await import('./mockData');
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    return filters.view_mode === 'lead' ? mockLeadDashboardData : mockEcommerceDashboardData;
  }

  const params: any = {
    view_mode: filters.view_mode,
    level: filters.level || 'adset',
    page: filters.page || 1,
    pageSize: filters.pageSize || 50,
    force_refresh: filters.force_refresh || 0,
  };

  // Add optional filters
  if (filters.account_ids) params.account_ids = filters.account_ids;
  if (filters.prefix || filters.prefix_filter) params.prefix = filters.prefix || filters.prefix_filter;
  if (filters.status && filters.status !== 'ALL') params.status = filters.status;
  if (filters.status_filter && filters.status_filter !== 'ALL') params.status = filters.status_filter;
  if (filters.date_from) params.date_from = filters.date_from;
  if (filters.date_to) params.date_to = filters.date_to;
  if (filters.search) params.search = filters.search;
  if (filters.campaign_id) params.campaign_id = filters.campaign_id;
  if (filters.adset_id) params.adset_id = filters.adset_id;
  
  // Add sort parameters
  if (filters.sort_by) params.sort_by = filters.sort_by;
  if (filters.sort_order) params.sort_order = filters.sort_order;

  const response = await api.get<DashboardDataResponse>('/dashboard/data', { params });
  return response.data;
}

/**
 * Get settings status
 * Check if user has configured Facebook accounts, tokens, etc.
 */
export async function getSettingsStatus(): Promise<SettingsStatus> {
  // 🎭 MOCK MODE
  if (USE_MOCK_DATA) {
    const { mockSettingsStatus } = await import('./mockData');
    await new Promise(resolve => setTimeout(resolve, 200));
    return mockSettingsStatus;
  }

  const response = await api.get<SettingsStatus>('/dashboard/settings-status');
  return response.data;
}

/**
 * Get filter options (accounts and prefixes)
 */
export async function getDashboardFilters(viewMode?: 'ecommerce' | 'lead'): Promise<{
  accounts: Array<{ id: string; name: string; type: string; enabled: boolean }>;
  prefixes: Array<{ id: string; name: string; description: string }>;
}> {
  // 🎭 MOCK MODE
  if (USE_MOCK_DATA) {
    const { mockFilterOptions } = await import('./mockData');
    await new Promise(resolve => setTimeout(resolve, 200));
    return mockFilterOptions as any;
  }

  const params: any = {};
  if (viewMode) params.view_mode = viewMode;
  const response = await api.get('/dashboard/filters', { params });
  return response.data;
}

/**
 * Update budget for multiple adsets/campaigns
 */
export async function updateBudget(
  request: BudgetUpdateRequest
): Promise<BudgetUpdateResponse> {
  // 🎭 MOCK MODE
  if (USE_MOCK_DATA) {
    await new Promise(resolve => setTimeout(resolve, 800));
    console.log('🎭 MOCK: Budget update request:', request);
    return {
      success: true,
      results: request.operations.map(op => ({
        id: op.id,
        level: op.level,
        old_budget: 500000,
        new_budget: op.new_budget,
        status: 'ok',
      })),
      message: `Updated ${request.operations.length} items (MOCK)`,
    };
  }

  const response = await api.post<BudgetUpdateResponse>('/dashboard/budget/update', request);
  return response.data;
}

/**
 * Update status (activate/pause) for adsets/campaigns
 */
export async function updateStatus(
  request: StatusUpdateRequest
): Promise<{ success: boolean; message: string }> {
  // 🎭 MOCK MODE
  if (USE_MOCK_DATA) {
    await new Promise(resolve => setTimeout(resolve, 600));
    console.log('🎭 MOCK: Status update request:', request);
    return {
      success: true,
      message: `Updated ${request.items.length} items to ${request.items[0]?.new_status} (MOCK)`,
    };
  }

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
