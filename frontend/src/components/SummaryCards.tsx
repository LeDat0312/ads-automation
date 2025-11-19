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

  const currency = summary.currency || 'VND';

  // ✅ Different cards for Lead vs Ecom per DASHBOARD_SPEC.md
  const cards: CardConfig[] = viewMode === 'lead'
    ? [
        // Lead View: 6 cards
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
          title: 'Chi phí / DATA',
          value: formatCurrency(summary.costPerData || 0, currency),
          subtitle: 'Giá mỗi DATA',
          icon: '📊',
          gradient: 'from-teal-500 to-teal-600',
          textColor: 'text-teal-700',
          iconBg: 'bg-teal-100',
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
          title: 'Lượt Mua',
          value: formatNumber(summary.totalPurchases || 0),
          subtitle: 'Purchases',
          icon: '💵',
          gradient: 'from-emerald-500 to-emerald-600',
          textColor: 'text-emerald-700',
          iconBg: 'bg-emerald-100',
        },
        {
          title: 'Chi phí / Lượt Mua',
          value: formatCurrency(summary.costPerPurchase || 0, currency),
          subtitle: 'Cost per Purchase',
          icon: '📈',
          gradient: 'from-indigo-500 to-indigo-600',
          textColor: 'text-indigo-700',
          iconBg: 'bg-indigo-100',
        },
      ]
    : [
        // E-commerce View: 6 cards
        {
          title: 'Tổng Chi Tiêu',
          value: formatCurrency(summary.totalSpend, currency),
          icon: '💰',
          gradient: 'from-blue-500 to-blue-600',
          textColor: 'text-blue-700',
          iconBg: 'bg-blue-100',
        },
        {
          title: 'Giá trị chuyển đổi',
          value: formatCurrency(summary.purchaseValue || 0, currency),
          subtitle: 'Purchase Value',
          icon: '💵',
          gradient: 'from-green-500 to-green-600',
          textColor: 'text-green-700',
          iconBg: 'bg-green-100',
        },
        {
          title: '% ADS',
          value: formatPercentage(summary.adsPercent || 0),
          subtitle: 'Chi tiêu / Doanh số',
          icon: '📈',
          gradient: 'from-rose-500 to-rose-600',
          textColor: 'text-rose-700',
          iconBg: 'bg-rose-100',
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
          title: 'Lượt Mua',
          value: formatNumber(summary.totalPurchases || 0),
          subtitle: 'Purchases',
          icon: '🎯',
          gradient: 'from-emerald-500 to-emerald-600',
          textColor: 'text-emerald-700',
          iconBg: 'bg-emerald-100',
        },
        {
          title: 'Chi phí / Lượt Mua',
          value: formatCurrency(summary.costPerPurchase || 0, currency),
          subtitle: 'Cost per Purchase',
          icon: '💎',
          gradient: 'from-indigo-500 to-indigo-600',
          textColor: 'text-indigo-700',
          iconBg: 'bg-indigo-100',
        },
      ];

  return (
    <>
      {/* Main 6 cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
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

      {/* Bottom section: Adset counts (not cards, just stats bar) */}
      <div className="bg-white rounded-xl shadow-md p-4 mb-8 flex items-center justify-around">
        <div className="text-center">
          <div className="flex items-center gap-2 justify-center mb-1">
            <span className="text-lg">✅</span>
            <span className="text-sm font-medium text-gray-600">Adsets Hoạt Động</span>
          </div>
          <p className="text-2xl font-bold text-emerald-700">{formatNumber(summary.activeAdsets)}</p>
        </div>
        <div className="h-12 w-px bg-gray-200"></div>
        <div className="text-center">
          <div className="flex items-center gap-2 justify-center mb-1">
            <span className="text-lg">⏸️</span>
            <span className="text-sm font-medium text-gray-600">Adsets Tạm Dừng</span>
          </div>
          <p className="text-2xl font-bold text-amber-700">{formatNumber(summary.pausedAdsets)}</p>
        </div>
        <div className="h-12 w-px bg-gray-200"></div>
        <div className="text-center">
          <div className="flex items-center gap-2 justify-center mb-1">
            <span className="text-lg">📊</span>
            <span className="text-sm font-medium text-gray-600">Tổng Adsets</span>
          </div>
          <p className="text-2xl font-bold text-indigo-700">{formatNumber(summary.totalAdsets)}</p>
        </div>
      </div>
    </>
  );
}
