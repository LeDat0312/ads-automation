import type { SummaryMetrics, ViewMode } from '@/types/dashboard';
import { formatCurrency, formatNumber } from '@/utils/formatters';

interface SummaryCardsProps {
  summary: SummaryMetrics;
  viewMode: ViewMode;
  isLoading: boolean;
}

export default function SummaryCards({ summary, viewMode, isLoading }: SummaryCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 animate-pulse">
            <div className="h-4 bg-slate-200 rounded w-24 mb-3"></div>
            <div className="h-8 bg-slate-300 rounded w-32"></div>
          </div>
        ))}
      </div>
    );
  }

  const currency = summary.currency || 'VND';

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      {/* Card 1: TỔNG CHI TIÊU - Always show */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center text-white text-xl">💰</div>
        </div>
        <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">TỔNG CHI TIÊU</h3>
        <p className="text-2xl font-bold text-gray-900">{formatCurrency(summary.totalSpend, currency)}</p>
      </div>

      {viewMode === 'ecommerce' ? (
        <>
          {/* E-COMMERCE VIEW */}
          {/* Card 2: % ADS */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-red-500 flex items-center justify-center text-white text-xl">📊</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">% ADS</h3>
            <p className="text-2xl font-bold text-gray-900">
              {summary.adsPercent !== undefined ? `${summary.adsPercent.toFixed(2)}%` : '0.00%'}
            </p>
            <p className="text-xs text-gray-500 mt-1">Chi tiêu / Giá trị chuyển đổi</p>
          </div>

          {/* Card 3: GIÁ TRỊ CHUYỂN ĐỔI */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-cyan-500 flex items-center justify-center text-white text-xl">💎</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">GIÁ TRỊ CHUYỂN ĐỔI</h3>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(summary.purchaseValue || 0, currency)}</p>
            <p className="text-xs text-gray-500 mt-1">Tổng từ lượt mua</p>
          </div>

          {/* Card 4: ADSETS HOẠT ĐỘNG */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-green-500 flex items-center justify-center text-white text-xl">▶️</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">ADSETS HOẠT ĐỘNG</h3>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(summary.activeAdsets)}</p>
          </div>

          {/* Card 5: ADSETS ĐÃ TẠM DỪNG */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-gray-500 flex items-center justify-center text-white text-xl">⏸️</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">ADSETS ĐÃ TẠM DỪNG</h3>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(summary.pausedAdsets)}</p>
          </div>

          {/* Card 6: TỔNG ADSETS */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-indigo-500 flex items-center justify-center text-white text-xl">📊</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">TỔNG ADSETS</h3>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(summary.totalAdsets)}</p>
          </div>
        </>
      ) : (
        <>
          {/* LEAD GENERATION VIEW */}
          {/* Card 2: TỔNG DATA */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-green-500 flex items-center justify-center text-white text-xl">📊</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">TỔNG LEAD</h3>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(summary.totalData || summary.totalLead || 0)}</p>
            <p className="text-xs text-gray-500 mt-1">Bình luận + Tin nhắn</p>
          </div>

          {/* Card 3: GIÁ DATA TB */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-orange-500 flex items-center justify-center text-white text-xl">💵</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">GIÁ DATA TB</h3>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(summary.costPerData || summary.avgGiaData || 0, currency)}</p>
            <p className="text-xs text-gray-500 mt-1">Chi phí trên mỗi lượt bắt đầu thanh toán</p>
          </div>

          {/* Card 4: ADSETS HOẠT ĐỘNG */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-green-500 flex items-center justify-center text-white text-xl">▶️</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">ADSETS HOẠT ĐỘNG</h3>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(summary.activeAdsets)}</p>
          </div>

          {/* Card 5: ADSETS ĐÃ TẠM DỪNG */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-gray-500 flex items-center justify-center text-white text-xl">⏸️</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">ADSETS ĐÃ TẠM DỪNG</h3>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(summary.pausedAdsets)}</p>
          </div>

          {/* Card 6: TỔNG ADSETS */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-lg bg-indigo-500 flex items-center justify-center text-white text-xl">📊</div>
            </div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-1">TỔNG ADSET</h3>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(summary.totalAdsets)}</p>
          </div>
        </>
      )}
    </div>
  );
}
