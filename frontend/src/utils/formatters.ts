import type { Currency } from '@/types/dashboard';

/**
 * Format number với phân tách hàng nghìn
 */
export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '0';
  return new Intl.NumberFormat('vi-VN').format(Math.round(value));
}

/**
 * Format tiền tệ theo đúng currency
 * VND: không có số thập phân, dấu phân cách hàng nghìn = dấu chấm
 * USD: 2 số thập phân, dấu phân cách = dấu phẩy
 */
export function formatCurrency(
  value: number | null | undefined,
  currency: Currency = 'VND'
): string {
  if (value === null || value === undefined) return currency === 'VND' ? '0' : '$0.00';
  
  if (currency === 'VND') {
    // VND: no decimals, dot separator
    return new Intl.NumberFormat('vi-VN').format(Math.round(value));
  } else {
    // USD: 2 decimals
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  }
}

/**
 * Format phần trăm
 */
export function formatPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined) return '0';
  return value.toFixed(2);
}

/**
 * Parse date từ string sang Date object
 */
export function parseDate(dateString: string | null | undefined): Date | null {
  if (!dateString) return null;
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? null : date;
}

/**
 * Format date thành YYYY-MM-DD cho API
 */
export function formatDateForAPI(date: Date | null): string | null {
  if (!date) return null;
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Get date range presets
 */
export function getDatePreset(preset: string): { from: Date; to: Date } | null {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  const thisWeekStart = new Date(today);
  thisWeekStart.setDate(today.getDate() - today.getDay());
  
  const thisMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
  
  const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);
  
  switch (preset) {
    case 'today':
      return { from: today, to: today };
    case 'yesterday':
      return { from: yesterday, to: yesterday };
    case 'thisWeek':
      return { from: thisWeekStart, to: today };
    case 'thisMonth':
      return { from: thisMonthStart, to: today };
    case 'lastMonth':
      return { from: lastMonthStart, to: lastMonthEnd };
    default:
      return null;
  }
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function (this: any, ...args: Parameters<T>) {
    const context = this;
    
    if (timeout) clearTimeout(timeout);
    
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
}

/**
 * Calculate budget change
 */
export function calculateBudgetChange(
  originalBudget: number,
  percentOrValue: number | string,
  isPercent: boolean
): number {
  if (isPercent) {
    // Percent mode: originalBudget * (1 + percent/100)
    const percent = typeof percentOrValue === 'string' ? parseFloat(percentOrValue) : percentOrValue;
    return Math.round(originalBudget * (1 + percent / 100));
  } else {
    // Manual mode: direct value
    return typeof percentOrValue === 'string' ? parseFloat(percentOrValue) : percentOrValue;
  }
}

/**
 * Validate budget value
 */
export function isValidBudget(value: number): boolean {
  return !isNaN(value) && value > 0 && isFinite(value);
}

/**
 * Get status color class
 */
export function getStatusColor(status: string): string {
  switch (status?.toUpperCase()) {
    case 'ACTIVE':
      return 'bg-green-100 text-green-800';
    case 'PAUSED':
    case 'CAMPAIGN_PAUSED':
    case 'ADSET_PAUSED':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

/**
 * Get status label in Vietnamese
 */
export function getStatusLabel(status: string): string {
  switch (status?.toUpperCase()) {
    case 'ACTIVE':
      return 'Hoạt động';
    case 'PAUSED':
      return 'Đã tạm dừng';
    case 'CAMPAIGN_PAUSED':
      return 'Chiến dịch tạm dừng';
    case 'ADSET_PAUSED':
      return 'Nhóm QC tạm dừng';
    default:
      return 'Không xác định';
  }
}

/**
 * Download data as CSV
 */
export function downloadCSV(data: any[], filename: string): void {
  if (data.length === 0) return;
  
  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        return typeof value === 'string' && value.includes(',') 
          ? `"${value}"` 
          : value;
      }).join(',')
    )
  ].join('\n');
  
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${filename}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}
