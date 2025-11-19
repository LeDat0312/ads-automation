import React, { useState, useMemo } from 'react';

interface AdsetBudget {
  adset_id: string;
  adset_name: string;
  current_budget: number;
}

interface BudgetAdjustmentModalProps {
  open: boolean;
  onClose: () => void;
  adsets: AdsetBudget[];
  currency?: string;
  onApply: (changes: { adset_id: string; new_budget: number }[]) => void;
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

const BudgetAdjustmentModal: React.FC<BudgetAdjustmentModalProps> = ({
  open,
  onClose,
  adsets,
  currency = 'VND',
  onApply
}) => {
  const [adjustmentType, setAdjustmentType] = useState<'percent' | 'fixed'>('percent');
  const [percentValue, setPercentValue] = useState<number>(10);
  const [fixedValue, setFixedValue] = useState<number>(0);

  const previewChanges = useMemo(() => {
    return adsets.map(adset => {
      let new_budget = adset.current_budget;
      
      if (adjustmentType === 'percent') {
        // Tăng/giảm theo %, giữ nguyên số thực
        new_budget = adset.current_budget * (1 + percentValue / 100);
      } else {
        // Đặt cứng
        new_budget = fixedValue;
      }

      return {
        adset_id: adset.adset_id,
        adset_name: adset.adset_name,
        old_budget: adset.current_budget,
        new_budget: new_budget
      };
    });
  }, [adsets, adjustmentType, percentValue, fixedValue]);

  const handleApply = () => {
    const changes = previewChanges.map(c => ({
      adset_id: c.adset_id,
      new_budget: c.new_budget
    }));
    onApply(changes);
    onClose();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-800">💰 Điều Chỉnh Ngân Sách</h2>
            <button 
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 text-2xl leading-none"
            >
              ×
            </button>
          </div>
          <p className="text-sm text-slate-600 mt-1">Đang điều chỉnh {adsets.length} adset(s)</p>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Adjustment Type */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-3">Loại Điều Chỉnh</label>
            <div className="flex gap-3">
              <button
                onClick={() => setAdjustmentType('percent')}
                className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                  adjustmentType === 'percent'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                }`}
              >
                📊 Tăng/Giảm theo %
              </button>
              <button
                onClick={() => setAdjustmentType('fixed')}
                className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                  adjustmentType === 'fixed'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                }`}
              >
                💵 Đặt Cứng
              </button>
            </div>
          </div>

          {/* Percent Adjustment */}
          {adjustmentType === 'percent' && (
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-3">Phần Trăm Thay Đổi</label>
              <div className="grid grid-cols-3 gap-2 mb-3">
                {[10, 20, 30].map(p => (
                  <button
                    key={p}
                    onClick={() => setPercentValue(p)}
                    className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
                      percentValue === p
                        ? 'border-green-500 bg-green-50 text-green-700'
                        : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                    }`}
                  >
                    +{p}%
                  </button>
                ))}
              </div>
              <div className="grid grid-cols-3 gap-2 mb-3">
                {[-10, -20, -30].map(p => (
                  <button
                    key={p}
                    onClick={() => setPercentValue(p)}
                    className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
                      percentValue === p
                        ? 'border-red-500 bg-red-50 text-red-700'
                        : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                    }`}
                  >
                    {p}%
                  </button>
                ))}
              </div>
              <input
                type="number"
                value={percentValue}
                onChange={(e) => setPercentValue(Number(e.target.value))}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Nhập % tùy chỉnh"
              />
            </div>
          )}

          {/* Fixed Budget */}
          {adjustmentType === 'fixed' && (
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-3">Ngân Sách Mới ({currency})</label>
              <input
                type="number"
                value={fixedValue}
                onChange={(e) => setFixedValue(Number(e.target.value))}
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
                placeholder={`Nhập ngân sách (${currency})`}
                min="0"
                step={currency === 'VND' ? '1000' : '0.01'}
              />
            </div>
          )}

          {/* Preview */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-3">👁️ Xem Trước Thay Đổi</label>
            <div className="border border-slate-200 rounded-lg overflow-hidden max-h-64 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-2 text-left font-semibold text-slate-700">Adset</th>
                    <th className="px-4 py-2 text-right font-semibold text-slate-700">Cũ</th>
                    <th className="px-4 py-2 text-center font-semibold text-slate-700">→</th>
                    <th className="px-4 py-2 text-right font-semibold text-slate-700">Mới</th>
                    <th className="px-4 py-2 text-right font-semibold text-slate-700">Thay Đổi</th>
                  </tr>
                </thead>
                <tbody>
                  {previewChanges.map((change, idx) => {
                    const diff = change.new_budget - change.old_budget;
                    const diffPercent = (diff / change.old_budget * 100).toFixed(1);
                    
                    return (
                      <tr key={change.adset_id} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
                        <td className="px-4 py-2 text-slate-700 max-w-xs truncate" title={change.adset_name}>
                          {change.adset_name}
                        </td>
                        <td className="px-4 py-2 text-right text-slate-600">
                          {formatCurrency(change.old_budget, currency)}
                        </td>
                        <td className="px-4 py-2 text-center text-slate-400">→</td>
                        <td className="px-4 py-2 text-right font-semibold text-blue-700">
                          {formatCurrency(change.new_budget, currency)}
                        </td>
                        <td className={`px-4 py-2 text-right text-xs font-medium ${
                          diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : 'text-slate-500'
                        }`}>
                          {diff > 0 ? '+' : ''}{formatCurrency(diff, currency)} ({diff > 0 ? '+' : ''}{diffPercent}%)
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-100 font-medium"
          >
            Hủy
          </button>
          <button
            onClick={handleApply}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium"
          >
            ✅ Áp Dụng
          </button>
        </div>
      </div>
    </div>
  );
};

export default BudgetAdjustmentModal;
