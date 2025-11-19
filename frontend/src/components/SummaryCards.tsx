import React from 'react';
import type { SummaryCardsProps } from '@/types/dashboard';
import { formatCurrency, formatNumber, formatPercentage } from '@/utils/formatters';

/**
 * Summary Cards Component
 * Hiển thị tóm tắt metrics ở đầu dashboard
 * 
 * Lead view: 6 cards
 *   - Tổng Chi Tiêu
 *   - Tổng DATA (Bình luận + Nhắn tin)
 *   - Bắt Đầu Thanh Toán (Checkouts Initiated)
 *   - Adsets Hoạt Động
 *   - Adsets Đã Tạm Dừng
 *   - Tổng Adsets
 * 
 * E-Commerce view: 6 cards
 *   - Tổng Chi Tiêu
 *   - % ADS
 *   - Doanh Số (Purchase Value)
 *   - Adsets Hoạt Động
 *   - Adsets Đã Tạm Dừng
 *   - Tổng Adsets
 */

interface CardData {
  title: string;
  value: string;
  subtitle?: string;
  icon: string;
  colorClass: string;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ 
  summary, 
  viewMode, 
  currency,
  loading = false 
}) => {
  // Build cards based on view mode
  const cards: CardData[] = viewMode === 'lead' 
    ? [
        {
          title: 'Tổng Chi Tiêu',
          value: formatCurrency(summary.totalSpend, currency),
          icon: '💰',
          colorClass: 'bg-blue-50 border-blue-200',
        },
        {
          title: 'Tổng DATA',
          value: formatNumber(summary.totalData),
          subtitle: 'Bình luận + Nhắn tin',
          icon: '💬',
          colorClass: 'bg-green-50 border-green-200',
        },
        {
          title: 'Bắt Đầu Thanh Toán',
          value: formatNumber(summary.totalCheckouts),
          subtitle: 'Checkouts Initiated',
          icon: '🛒',
          colorClass: 'bg-purple-50 border-purple-200',
        },
        {
          title: 'Adsets Hoạt Động',
          value: formatNumber(summary.activeAdsets),
          icon: '▶️',
          colorClass: 'bg-emerald-50 border-emerald-200',
        },
        {
          title: 'Adsets Đã Tạm Dừng',
          value: formatNumber(summary.pausedAdsets),
          icon: '⏸️',
          colorClass: 'bg-amber-50 border-amber-200',
        },
        {
          title: 'Tổng Adsets',
          value: formatNumber(summary.totalAdsets),
          icon: '📊',
          colorClass: 'bg-slate-50 border-slate-200',
        },
      ]
    : [
        {
          title: 'Tổng Chi Tiêu',
          value: formatCurrency(summary.totalSpend, currency),
          icon: '💰',
          colorClass: 'bg-blue-50 border-blue-200',
        },
        {
          title: '% ADS',
          value: `${formatPercentage(summary.adsPercent || 0)}%`,
          subtitle: 'Chi tiêu / Doanh số',
          icon: '📈',
          colorClass: 'bg-red-50 border-red-200',
        },
        {
          title: 'Doanh Số',
          value: formatCurrency(summary.purchaseValue, currency),
          subtitle: 'Giá trị từ lượt mua',
          icon: '🛒',
          colorClass: 'bg-green-50 border-green-200',
        },
        {
          title: 'Adsets Hoạt Động',
          value: formatNumber(summary.activeAdsets),
          icon: '▶️',
          colorClass: 'bg-emerald-50 border-emerald-200',
        },
        {
          title: 'Adsets Đã Tạm Dừng',
          value: formatNumber(summary.pausedAdsets),
          icon: '⏸️',
          colorClass: 'bg-amber-50 border-amber-200',
        },
        {
          title: 'Tổng Adsets',
          value: formatNumber(summary.totalAdsets),
          icon: '📊',
          colorClass: 'bg-slate-50 border-slate-200',
        },
      ];

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div
            key={i}
            className="bg-white border border-gray-200 rounded-lg p-4 animate-pulse"
          >
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
      {cards.map((card, index) => (
        <Card key={index} {...card} />
      ))}
    </div>
  );
};

const Card: React.FC<CardData> = ({ title, value, subtitle, icon, colorClass }) => {
  return (
    <div
      className={`
        ${colorClass} 
        border-2 rounded-lg p-4 
        transition-all duration-200 
        hover:shadow-md hover:scale-105
      `}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-700">{title}</h3>
        <span className="text-2xl">{icon}</span>
      </div>
      
      <div className="text-2xl font-bold text-gray-900 mb-1">
        {value}
      </div>
      
      {subtitle && (
        <div className="text-xs text-gray-600">
          {subtitle}
        </div>
      )}
    </div>
  );
};

export default SummaryCards;
