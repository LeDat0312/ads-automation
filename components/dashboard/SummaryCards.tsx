import React from 'react';

interface SummaryData {
  totalSpend: number;
  totalData: number;
  costPerData: number;
  totalCheckouts: number;
  costPerCheckout: number;
  totalPurchases: number;
  costPerPurchase: number;
  purchaseValue: number;
  activeAdsets: number;
  pausedAdsets: number;
  totalAdsets: number;
  adsetsRanToday: number;
  adsPercent?: number; // Chỉ E-Commerce
}

interface SummaryCardsProps {
  data: SummaryData | null;
  viewMode: 'lead' | 'ecommerce';
  loading?: boolean;
  currency?: string;
}

const formatCurrency = (value: number, currency: string = 'VND'): string => {
  if (currency === 'VND') {
    return new Intl.NumberFormat('vi-VN').format(Math.round(value)) + ' ₫';
  }
  return new Intl.NumberFormat('en-US', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  }).format(value) + ' $';
};

const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('vi-VN').format(value);
};

const SummaryCards: React.FC<SummaryCardsProps> = ({ 
  data, 
  viewMode, 
  loading = false,
  currency = 'VND'
}) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 animate-pulse">
            <div className="h-4 bg-slate-200 rounded w-24 mb-3"></div>
            <div className="h-8 bg-slate-300 rounded w-32"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-6">
        <p className="text-yellow-800">⚠️ Không có dữ liệu summary</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 mb-6">
      {/* Row 1: Chi tiêu & Kết quả */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* TỔNG CHI TIÊU */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-sm border border-blue-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-blue-700">💰 TỔNG CHI TIÊU</h3>
          </div>
          <p className="text-2xl font-bold text-blue-900">{formatCurrency(data.totalSpend, currency)}</p>
        </div>

        {viewMode === 'ecommerce' ? (
          <>
            {/* % ADS - E-COMMERCE */}
            <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl shadow-sm border border-red-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-red-700">📈 % ADS</h3>
              </div>
              <p className="text-2xl font-bold text-red-900">
                {data.adsPercent !== undefined ? `${data.adsPercent.toFixed(2)}%` : '-'}
              </p>
              <p className="text-xs text-red-600 mt-1">Chi tiêu / Giá trị mua</p>
            </div>

            {/* GIÁ TRỊ CHUYỂN ĐỔI - E-COMMERCE */}
            <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-xl shadow-sm border border-teal-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-teal-700">💎 GIÁ TRỊ MUA HÀNG</h3>
              </div>
              <p className="text-2xl font-bold text-teal-900">{formatCurrency(data.purchaseValue, currency)}</p>
            </div>

            {/* GIÁ DATA - E-COMMERCE */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl shadow-sm border border-purple-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-purple-700">💵 GIÁ DATA</h3>
              </div>
              <p className="text-2xl font-bold text-purple-900">{formatCurrency(data.costPerData, currency)}</p>
            </div>
          </>
        ) : (
          <>
            {/* TỔNG DATA - LEAD */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl shadow-sm border border-green-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-green-700">📊 TỔNG DATA</h3>
              </div>
              <p className="text-2xl font-bold text-green-900">{formatNumber(data.totalData)}</p>
              <p className="text-xs text-green-600 mt-1">Bình luận + Nhắn tin</p>
            </div>

            {/* GIÁ DATA - LEAD */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl shadow-sm border border-purple-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-purple-700">💵 GIÁ DATA</h3>
              </div>
              <p className="text-2xl font-bold text-purple-900">{formatCurrency(data.costPerData, currency)}</p>
            </div>

            {/* BẮT ĐẦU THANH TOÁN - LEAD */}
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl shadow-sm border border-orange-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-orange-700">🛒 BẮT ĐẦU TT</h3>
              </div>
              <p className="text-2xl font-bold text-orange-900">{formatNumber(data.totalCheckouts)}</p>
              <p className="text-xs text-orange-600 mt-1">{formatCurrency(data.costPerCheckout, currency)}/checkout</p>
            </div>
          </>
        )}
      </div>

      {/* Row 2: Purchase & Adsets */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {viewMode === 'ecommerce' ? (
          <>
            {/* BẮT ĐẦU THANH TOÁN - E-COMMERCE */}
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl shadow-sm border border-orange-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-orange-700">🛒 TỔNG CHECKOUT</h3>
              </div>
              <p className="text-2xl font-bold text-orange-900">{formatNumber(data.totalCheckouts)}</p>
              <p className="text-xs text-orange-600 mt-1">{formatCurrency(data.costPerCheckout, currency)}/checkout</p>
            </div>

            {/* LƯỢT MUA - E-COMMERCE */}
            <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl shadow-sm border border-pink-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-pink-700">🎯 TỔNG MUA HÀNG</h3>
              </div>
              <p className="text-2xl font-bold text-pink-900">{formatNumber(data.totalPurchases)}</p>
              <p className="text-xs text-pink-600 mt-1">{formatCurrency(data.costPerPurchase, currency)}/purchase</p>
            </div>
          </>
        ) : (
          <>
            {/* LƯỢT MUA - LEAD */}
            <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl shadow-sm border border-pink-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-pink-700">🎯 TỔNG MUA HÀNG</h3>
              </div>
              <p className="text-2xl font-bold text-pink-900">{formatNumber(data.totalPurchases)}</p>
              <p className="text-xs text-pink-600 mt-1">{formatCurrency(data.costPerPurchase, currency)}/purchase</p>
            </div>
          </>
        )}

        {/* TỔNG ADSETS */}
        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl shadow-sm border border-indigo-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-indigo-700">📋 TỔNG ADSETS</h3>
          </div>
          <p className="text-2xl font-bold text-indigo-900">{formatNumber(data.totalAdsets)}</p>
          <div className="flex gap-3 mt-2 text-xs">
            <span className="text-green-600">✅ {data.activeAdsets}</span>
            <span className="text-gray-600">⏸️ {data.pausedAdsets}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryCards;
