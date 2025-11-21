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
      <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
        <div className="flex items-center justify-between mb-4">
          <div className="w-10 h-10 rounded-[10px] bg-[#6366f1] flex items-center justify-center text-white text-lg">💰</div>
        </div>
        <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">TỔNG CHI TIÊU</h3>
        <p className="text-[32px] font-bold text-[#1f2937] leading-tight">{formatCurrency(summary.totalSpend, currency)}</p>
      </div>

      {viewMode === 'ecommerce' ? (
        <>
          {/* E-COMMERCE VIEW */}
          {/* Card 2: % ADS */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#ef4444] flex items-center justify-center text-white text-lg">📈</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">% ADS</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight mb-2">
              {summary.adsPercent !== undefined ? `${summary.adsPercent.toFixed(2)}%` : '0.00%'}
            </p>
            <p className="text-sm text-[#6b7280]">Chi tiêu / Giá trị chuyển đổi</p>
          </div>

          {/* Card 3: GIÁ TRỊ CHUYỂN ĐỔI */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#06b6d4] flex items-center justify-center text-white text-lg">🛒</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">GIÁ TRỊ CHUYỂN ĐỔI</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight mb-2">{formatCurrency(summary.purchaseValue || 0, currency)}</p>
            <p className="text-sm text-[#6b7280]">Tổng từ lượt mua</p>
          </div>

          {/* Card 4: ADSETS HOẠT ĐỘNG */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#8b5cf6] flex items-center justify-center text-white text-lg">▶️</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">ADSETS HOẠT ĐỘNG</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight">{formatNumber(summary.activeAdsets)}</p>
          </div>

          {/* Card 5: ADSETS ĐÃ TẠM DỪNG */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#8b5cf6] flex items-center justify-center text-white text-lg">⏸️</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">ADSETS ĐÃ TẠM DỪNG</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight">{formatNumber(summary.pausedAdsets)}</p>
          </div>

          {/* Card 6: TỔNG ADSETS */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#8b5cf6] flex items-center justify-center text-white text-lg">📊</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">TỔNG ADSETS</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight">{formatNumber(summary.totalAdsets)}</p>
          </div>
        </>
      ) : (
        <>
          {/* LEAD GENERATION VIEW */}
          {/* Card 2: TỔNG DATA */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#22c55e] flex items-center justify-center text-white text-lg">💬</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">TỔNG DATA</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight mb-2">{formatNumber(summary.totalData || 0)}</p>
            <p className="text-sm text-[#6b7280]">Bình luận + Tin nhắn</p>
          </div>

          {/* Card 3: TỔNG LEAD (BẮT ĐẦU TT) */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#06b6d4] flex items-center justify-center text-white text-lg">🛒</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">TỔNG LEAD</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight mb-2">{formatNumber(summary.totalLead || 0)}</p>
            <p className="text-sm text-[#6b7280]">Checkouts Initiated</p>
          </div>

          {/* Card 4: ADSETS HOẠT ĐỘNG */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#8b5cf6] flex items-center justify-center text-white text-lg">▶️</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">ADSETS HOẠT ĐỘNG</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight">{formatNumber(summary.activeAdsets)}</p>
          </div>

          {/* Card 5: ADSETS ĐÃ TẠM DỪNG */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#8b5cf6] flex items-center justify-center text-white text-lg">⏸️</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">ADSETS ĐÃ TẠM DỪNG</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight">{formatNumber(summary.pausedAdsets)}</p>
          </div>

          {/* Card 6: TỔNG ADSETS */}
          <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-[10px] bg-[#8b5cf6] flex items-center justify-center text-white text-lg">📊</div>
            </div>
            <h3 className="text-sm font-semibold text-[#6b7280] uppercase tracking-[0.5px] mb-3">TỔNG ADSET</h3>
            <p className="text-[32px] font-bold text-[#1f2937] leading-tight">{formatNumber(summary.totalAdsets)}</p>
          </div>
        </>
      )}
    </div>
  );
}
