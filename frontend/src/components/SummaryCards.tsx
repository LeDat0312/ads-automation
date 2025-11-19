import React from 'react';
import type { SummaryMetrics, ViewMode } from '@/types/dashboard';
import { formatCurrency, formatNumber, formatPercentage } from '@/utils/formatters';

interface SummaryCardsProps {
  summary: SummaryMetrics;
  viewMode: ViewMode;
  isLoading: boolean;
}

interface CardConfig {
  title: string;
  value: string | number;
  icon: string;
  gradient: string;
  textColor: string;
  iconBg: string;
  subtitle?: string;
}

export default function SummaryCards({ summary, viewMode, isLoading }: SummaryCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
            <div className="flex items-start justify-between mb-4">
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-12 w-12 bg-gray-200 rounded-xl"></div>
            </div>
            <div className="h-10 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  const currency = summary.currency || 'USD';

  const cards: CardConfig[] = viewMode === 'lead' 
  const cards: CardConfig[] = viewMode === 'lead'
    ? [
        {
          title: 'Tổng Chi Tiêu',
          value: formatCurrency(summary.totalSpend, currency),
          icon: '💰',
          gradient: 'from-blue-500 to-blue-600',
          textColor: 'text-blue-700',
          iconBg: 'bg-blue-100',
        },
        {
          title: 'Tổng DATA',
          value: formatNumber(summary.totalData),
          subtitle: 'Bình luận + Nhắn tin',
          icon: '💬',
          gradient: 'from-green-500 to-green-600',
          textColor: 'text-green-700',
          iconBg: 'bg-green-100',
        },
        {
          title: 'Bắt Đầu Thanh Toán',
          value: formatNumber(summary.totalCheckouts || 0),
          subtitle: 'Checkouts Initiated',
          icon: '🛒',
          gradient: 'from-purple-500 to-purple-600',
          textColor: 'text-purple-700',
          iconBg: 'bg-purple-100',
        },
        {
          title: 'Adsets Hoạt Động',
          value: formatNumber(summary.activeAdsets),
          icon: '✅',
          gradient: 'from-emerald-500 to-emerald-600',
          textColor: 'text-emerald-700',
          iconBg: 'bg-emerald-100',
        },
        {
          title: 'Adsets Tạm Dừng',
          value: formatNumber(summary.pausedAdsets),
          icon: '⏸️',
          gradient: 'from-amber-500 to-amber-600',
          textColor: 'text-amber-700',
          iconBg: 'bg-amber-100',
        },
        {
          title: 'Tổng Adsets',
          value: formatNumber(summary.totalAdsets),
          icon: '📊',
          gradient: 'from-indigo-500 to-indigo-600',
          textColor: 'text-indigo-700',
          iconBg: 'bg-indigo-100',
        },
      ]
    : [
        {
          title: 'Tổng Chi Tiêu',
          value: formatCurrency(summary.totalSpend, currency),
          icon: '💰',
          gradient: 'from-blue-500 to-blue-600',
          textColor: 'text-blue-700',
          iconBg: 'bg-blue-100',
        },
        {
          title: '% ADS',
          value: formatPercentage(summary.adsPercent || 0),
          subtitle: 'Chi phí quảng cáo / Doanh số',
          icon: '📈',
          gradient: 'from-rose-500 to-rose-600',
          textColor: 'text-rose-700',
          iconBg: 'bg-rose-100',
        },
        {
          title: 'Doanh Số',
          value: formatCurrency(summary.purchaseValue || 0, currency),
          subtitle: 'Purchase Value',
          icon: '💵',
          gradient: 'from-green-500 to-green-600',
          textColor: 'text-green-700',
          iconBg: 'bg-green-100',
        },
        {
          title: 'Adsets Hoạt Động',
          value: formatNumber(summary.activeAdsets),
          icon: '✅',
          gradient: 'from-emerald-500 to-emerald-600',
          textColor: 'text-emerald-700',
          iconBg: 'bg-emerald-100',
        },
        {
          title: 'Adsets Tạm Dừng',
          value: formatNumber(summary.pausedAdsets),
          icon: '⏸️',
          gradient: 'from-amber-500 to-amber-600',
          textColor: 'text-amber-700',
          iconBg: 'bg-amber-100',
        },
        {
          title: 'Tổng Adsets',
          value: formatNumber(summary.totalAdsets),
          icon: '📊',
          gradient: 'from-indigo-500 to-indigo-600',
          textColor: 'text-indigo-700',
          iconBg: 'bg-indigo-100',
        },
      ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {cards.map((card, index) => (
        <div
          key={index}
          className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden group"
        >
          <div className={`h-1.5 bg-gradient-to-r ${card.gradient}`}></div>
          <div className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{card.title}</p>
                {card.subtitle && (
                  <p className="text-xs text-gray-400">{card.subtitle}</p>
                )}
              </div>
              <div className={`${card.iconBg} p-3 rounded-xl group-hover:scale-110 transition-transform duration-300`}>
                <span className="text-2xl">{card.icon}</span>
              </div>
            </div>
            <p className={`text-3xl font-bold ${card.textColor}`}>
              {card.value}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
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
