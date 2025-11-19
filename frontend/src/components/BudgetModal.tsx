import { useState, useEffect } from 'react';
import { formatCurrency } from '@/utils/formatters';
import type { AdsetRow } from '@/types/dashboard';

interface BudgetModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedAdsets: AdsetRow[];
  onApply: (changes: { id: string; new_budget: number }[]) => void;
}

type BudgetMode = 'percent' | 'manual';

const percentOptions = [
  { value: -10, label: '-10%', color: 'amber' },
  { value: -20, label: '-20%', color: 'amber' },
  { value: -30, label: '-30%', color: 'amber' },
  { value: 10, label: '+10%', color: 'green' },
  { value: 20, label: '+20%', color: 'green' },
  { value: 30, label: '+30%', color: 'green' },
];

export default function BudgetModal({ isOpen, onClose, selectedAdsets, onApply }: BudgetModalProps) {
  const [mode, setMode] = useState<BudgetMode>('percent');
  const [selectedPercent, setSelectedPercent] = useState<number | null>(null);
  const [manualBudget, setManualBudget] = useState<string>('');
  const [previewChanges, setPreviewChanges] = useState<{ id: string; current: number; new: number; currency: string }[]>([]);

  useEffect(() => {
    if (mode === 'percent' && selectedPercent !== null) {
      const changes = selectedAdsets.map(adset => ({
        id: adset.adset_id,
        current: adset.budget || 0,
        // ✅ FIX: Use exact original budget, don't round until display
        new: (adset.budget || 0) * (1 + selectedPercent / 100),
        currency: adset.currency,
      }));
      setPreviewChanges(changes);
    } else if (mode === 'manual' && manualBudget) {
      const budget = parseFloat(manualBudget);
      if (!isNaN(budget) && budget > 0) {
        const changes = selectedAdsets.map(adset => ({
          id: adset.adset_id,
          current: adset.budget || 0,
          new: budget,
          currency: adset.currency,
        }));
        setPreviewChanges(changes);
      }
    } else {
      setPreviewChanges([]);
    }
  }, [mode, selectedPercent, manualBudget, selectedAdsets]);

  const handleApply = () => {
    const changes = previewChanges.map(change => ({
      id: change.id,
      new_budget: change.new,
    }));
    onApply(changes);
    handleClose();
  };

  const handleClose = () => {
    setMode('percent');
    setSelectedPercent(null);
    setManualBudget('');
    setPreviewChanges([]);
    onClose();
  };

  if (!isOpen) return null;

  const totalCurrentBudget = selectedAdsets.reduce((sum, adset) => sum + (adset.budget || 0), 0);
  const totalNewBudget = previewChanges.reduce((sum, change) => sum + change.new, 0);
  const budgetDifference = totalNewBudget - totalCurrentBudget;
  const currency = selectedAdsets[0]?.currency || 'USD';

  return (
    <>
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center"
        onClick={handleClose}
      >
        <div
          className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header - Gradient */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-5 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold flex items-center gap-2">
                  <span>💰</span>
                  <span>Điều chỉnh ngân sách</span>
                </h3>
                <p className="mt-2 text-sm text-indigo-100">
                  Đã chọn <span className="font-bold text-white bg-white/20 px-2 py-0.5 rounded">{selectedAdsets.length}</span> adset
                </p>
              </div>
              <button
                onClick={handleClose}
                className="text-white/80 hover:text-white transition-colors p-1 hover:bg-white/10 rounded-lg"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Body */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
            {/* Mode Selector - Beautiful Tabs */}
            <div className="flex gap-2 mb-6 bg-gray-100 p-1 rounded-xl">
              <button
                onClick={() => setMode('percent')}
                className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all transform ${
                  mode === 'percent'
                    ? 'bg-white text-indigo-600 shadow-md scale-105'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📊 Theo phần trăm
              </button>
              <button
                onClick={() => setMode('manual')}
                className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all transform ${
                  mode === 'manual'
                    ? 'bg-white text-indigo-600 shadow-md scale-105'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                ✏️ Nhập thủ công
              </button>
            </div>

            {/* Percent Mode */}
            {mode === 'percent' && (
              <div className="space-y-4">
                <p className="text-sm text-gray-600 mb-4">
                  Chọn mức thay đổi ngân sách cho tất cả adset đã chọn
                </p>
                <div className="grid grid-cols-3 gap-3">
                  {percentOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setSelectedPercent(option.value)}
                      className={`py-4 px-4 rounded-xl font-bold text-lg border-2 transition-all transform hover:scale-105 ${
                        selectedPercent === option.value
                          ? option.color === 'amber'
                            ? 'bg-amber-50 border-amber-500 text-amber-700 shadow-lg'
                            : 'bg-green-50 border-green-500 text-green-700 shadow-lg'
                          : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
                {selectedPercent !== null && (
                  <div className="mt-4 p-4 bg-indigo-50 rounded-xl text-center">
                    <p className="text-sm text-indigo-600 font-medium">
                      Ngân sách sẽ {selectedPercent > 0 ? 'tăng' : 'giảm'}{' '}
                      <span className="font-bold">{Math.abs(selectedPercent)}%</span>
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Manual Mode */}
            {mode === 'manual' && (
              <div className="space-y-4">
                <p className="text-sm text-gray-600 mb-4">
                  Nhập ngân sách mới áp dụng cho tất cả adset
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    value={manualBudget}
                    onChange={(e) => setManualBudget(e.target.value)}
                    placeholder="Nhập ngân sách..."
                    className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-xl text-lg focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all"
                    min="0"
                    step="1"
                  />
                  <span className="text-lg font-semibold text-gray-600">{currency}</span>
                </div>
                <div className="p-3 bg-amber-50 rounded-lg flex items-start gap-2 text-sm text-amber-800">
                  <span>⚠️</span>
                  <span>Lưu ý: Ngân sách mới sẽ được áp dụng cho tất cả {selectedAdsets.length} adset đã chọn</span>
                </div>
              </div>
            )}

            {/* Preview */}
            {previewChanges.length > 0 && (
              <div className="mt-6 border-t border-gray-200 pt-6">
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <span>👁️</span>
                  Xem trước thay đổi
                </h4>
                
                {/* Summary */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-600 mb-1">Tổng hiện tại</p>
                    <p className="text-lg font-bold text-gray-900">
                      {formatCurrency(totalCurrentBudget, currency)}
                    </p>
                  </div>
                  <div className="bg-indigo-50 rounded-lg p-4">
                    <p className="text-xs text-indigo-600 mb-1">Tổng mới</p>
                    <p className="text-lg font-bold text-indigo-900">
                      {formatCurrency(totalNewBudget, currency)}
                    </p>
                  </div>
                  <div className={`rounded-lg p-4 ${budgetDifference >= 0 ? 'bg-green-50' : 'bg-amber-50'}`}>
                    <p className={`text-xs mb-1 ${budgetDifference >= 0 ? 'text-green-600' : 'text-amber-600'}`}>
                      Chênh lệch
                    </p>
                    <p className={`text-lg font-bold ${budgetDifference >= 0 ? 'text-green-900' : 'text-amber-900'}`}>
                      {budgetDifference >= 0 ? '+' : ''}{formatCurrency(budgetDifference, currency)}
                    </p>
                  </div>
                </div>

                {/* Details */}
                <div className="max-h-48 overflow-y-auto border border-gray-200 rounded-lg">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium text-gray-600">Adset</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">Hiện tại</th>
                        <th className="px-4 py-2 text-center font-medium text-gray-600">→</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">Mới</th>
                      </tr>
                    </thead>
                    <tbody>
                      {previewChanges.map((change, idx) => (
                        <tr key={change.id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                          <td className="px-4 py-2 text-gray-900 truncate max-w-[200px]">
                            {selectedAdsets.find(a => a.adset_id === change.id)?.adset_name || change.id}
                          </td>
                          <td className="px-4 py-2 text-right text-gray-600">
                            {formatCurrency(change.current, change.currency as any)}
                          </td>
                          <td className="px-4 py-2 text-center text-gray-400">→</td>
                          <td className="px-4 py-2 text-right font-semibold text-indigo-600">
                            {formatCurrency(change.new, change.currency as any)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
            <button
              onClick={handleClose}
              className="px-6 py-2.5 text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Hủy
            </button>
            <button
              onClick={handleApply}
              disabled={previewChanges.length === 0}
              className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium shadow-lg shadow-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
            >
              Áp dụng thay đổi
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
