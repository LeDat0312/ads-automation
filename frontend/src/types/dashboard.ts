// ============================================================================
// API Response Types - matching backend FastAPI /dashboard/data endpoint
// ============================================================================

export type ViewMode = 'lead' | 'ecommerce';
export type AccountType = 'LEAD_GENERATION' | 'E-COMMERCE';
export type AdsetStatus = 'ACTIVE' | 'PAUSED' | 'CAMPAIGN_PAUSED' | 'ADSET_PAUSED' | 'UNKNOWN';
export type Currency = 'VND' | 'USD';

// Adset row data from backend
export interface AdsetRow {
  // IDs
  adset_id: string;
  adset_name: string;
  campaign_id: string;
  campaign_name: string;
  account_id: string;
  account_name?: string;  // Account name for display
  prefix?: string;

  // Budget
  budget: number;
  budget_level: 'CAMPAIGN' | 'ADSET';
  currency: Currency;

  // Core metrics
  spend: number;
  impressions: number;
  clicks: number;
  reach: number;
  frequency: number;
  ctr: number;  // Click-through rate
  cpc: number;  // Cost per click
  cpm: number;  // Cost per mille (thousand impressions)

  // Results (Lead specific)
  results: number;  // comments + messages
  total_leads: number;  // Alias for results
  
  // Data breakdown
  data_cost: number;  // Cost per DATA (spend / results)
  
  // Checkouts
  initiated_checkout?: number;  // Lượt bắt đầu thanh toán (from backend)
  checkouts_initiated?: number;  // Alias for initiated_checkout
  cost_per_checkout_initiated?: number;  // Chi phí / Lượt bắt đầu TT
  
  // Purchases
  purchases: number;  // Lượt mua
  cost_per_purchase: number;  // Chi phí / Lượt mua
  purchase_value: number;  // Giá trị chuyển đổi từ lượt mua

  // E-Commerce specific
  ads_percent?: number;  // % ADS = spend / purchase_value (only for ecommerce)
  tlc?: number;  // Tỷ lệ chuyển đổi (purchases / results * 100)

  // Status fields
  delivery: AdsetStatus;  // effective_status
  configured_status?: string;
  effective_status?: string;
  campaign_configured_status?: string;
  campaign_effective_status?: string;
  is_active_now?: boolean;  // effective_status == 'ACTIVE'
  ran_today?: boolean;  // impressions > 0 or spend > 0

  // View mode
  view_mode: ViewMode;
}

// Summary metrics (global, not affected by table filters)
// Match backend response structure from /dashboard/data endpoint
export interface SummaryMetrics {
  // Common for both views
  totalSpend: number;
  activeAdsets: number;
  pausedAdsets: number;
  totalAdsets: number;
  
  // Lead Generation specific (from backend)
  totalData?: number;  // comments + messages (Lead only)
  avgGiaData?: number;  // Chi phí / DATA (Lead only)
  totalLead?: number;  // Bắt đầu thanh toán (Lead only)
  
  // E-Commerce specific (from backend)
  adsPercent?: number;  // % ADS (Ecommerce only)
  purchaseValue?: number;  // Giá trị chuyển đổi (Ecommerce only)
  
  // Currency
  currency?: Currency;  // VND or USD
}

// Pagination info
export interface PaginationInfo {
  page: number;
  page_size: number;
  total_rows: number;
  total_pages: number;
}

// Main dashboard data response
export interface DashboardDataResponse {
  summary: SummaryMetrics;
  details: {
    level: 'campaign' | 'adset' | 'ad';
    rows: AdsetRow[];
    pagination: PaginationInfo;
  };
}

// Settings status response
export interface SettingsStatus {
  hasAccounts: boolean;
  hasFacebookToken: boolean;
  hasTelegramToken: boolean;
  accountsCount?: number;
  message?: string;
}

// Filter options
export interface DashboardFilters {
  view_mode: ViewMode;
  level: 'campaign' | 'adset' | 'ad';
  account_ids?: string;
  prefix?: string;
  status?: 'ACTIVE' | 'PAUSED' | 'RAN_TODAY' | 'ALL';
  date_from: string;  // YYYY-MM-DD (required for URL sync)
  date_to: string;    // YYYY-MM-DD (required for URL sync)
  search?: string;
  campaign_id?: string;
  page?: number;
  pageSize?: number;
  force_refresh?: 0 | 1;  // 0=cache, 1=refresh
  // Additional filters for UI
  prefix_filter?: string;
  status_filter?: string;  // 'ran_today' | 'ACTIVE' | 'PAUSED'
}

// Budget operation
export interface BudgetOperation {
  level: 'CAMPAIGN' | 'ADSET';
  id: string;  // campaign_id or adset_id
  new_budget: number;  // VND / day
  reason?: string;
}

export interface BudgetUpdateRequest {
  operations: BudgetOperation[];
  view_mode?: ViewMode;
  adset_ids?: string[];  // For bulk budget update
}

export interface BudgetUpdateResponse {
  success: boolean;
  results: Array<{
    id: string;
    level: string;
    old_budget: number;
    new_budget: number;
    status: string;
  }>;
  errors?: Array<{
    id: string;
    error: string;
  }>;
  message: string;
}

// Status update
export interface StatusUpdateItem {
  id: string;
  new_status: 'ACTIVE' | 'PAUSED' | 'DELETED';
}

export interface StatusUpdateRequest {
  level: 'CAMPAIGN' | 'ADSET' | 'AD';
  items: StatusUpdateItem[];
  adset_ids?: string[];  // For bulk status update
}

// Sort configuration
export type SortDirection = 'asc' | 'desc';
export type SortableColumn = 
  | 'spend' 
  | 'results' 
  | 'data_cost' 
  | 'checkouts_initiated'
  | 'cost_per_checkout_initiated'
  | 'purchases'
  | 'cost_per_purchase'
  | 'purchase_value'
  | 'ads_percent'
  | 'impressions'
  | 'clicks'
  | 'cpm'
  | 'ctr'
  | 'cpc';

export interface SortConfig {
  column: SortableColumn | null;
  direction: SortDirection;
}

// Component props types
export interface SummaryCardsProps {
  summary: SummaryMetrics;
  viewMode: ViewMode;
  currency: Currency;
  loading?: boolean;
}

export interface AdsetTableProps {
  rows: AdsetRow[];
  viewMode: ViewMode;
  loading?: boolean;
  onSort?: (column: SortableColumn) => void;
  sortConfig?: SortConfig;
  selectedIds?: Set<string>;
  onSelectionChange?: (ids: Set<string>) => void;
  onStatusToggle?: (row: AdsetRow) => void;
  onBudgetUpdate?: (row: AdsetRow, newBudget: number) => Promise<void>;
  onDrillDown?: (level: 'campaign' | 'adset', id: string, name: string) => void;
  currency?: Currency;
}

export interface FiltersBarProps {
  filters: DashboardFilters;
  onFiltersChange: (filters: Partial<DashboardFilters>) => void;
  prefixes: string[];
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
}

export interface BudgetModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedAdsets: AdsetRow[];
  onSubmit: (operations: BudgetOperation[]) => Promise<void>;
  currency: Currency;
}

export interface StatusChipProps {
  status: AdsetStatus;
  size?: 'sm' | 'md';
}
