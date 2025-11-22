import React, { useState, useEffect, useRef } from 'react';
import type { AdsetRow, Currency } from '@/types/dashboard';
import { formatCurrency } from '@/utils/formatters';

interface BudgetEditorProps {
  row: AdsetRow;
  isOpen: boolean;
  onClose: () => void;
  onSave: (newBudget: number) => Promise<void>;
  currency: Currency;
}

export default function BudgetEditor({
  row,
  isOpen,
  onClose,
  onSave,
  currency,
}: BudgetEditorProps) {
  // ⭐ SIMPLE: Dùng current_budget từ backend (đã chuẩn hóa)
  const getCurrentBudget = (): number => {
    return row.current_budget || 0;
  };
  
  const originalBudget = getCurrentBudget();
  const [draftBudget, setDraftBudget] = useState<number>(originalBudget);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Reset when row changes or popup opens
  useEffect(() => {
    if (isOpen) {
      const currentBudget = getCurrentBudget();
      setDraftBudget(currentBudget);
      setError(null);
      // Focus input after a short delay
      setTimeout(() => {
        inputRef.current?.focus();
        inputRef.current?.select();
      }, 100);
    }
  }, [isOpen, row.current_budget]);

  // Adjust budget by percentage
  const adjustPercent = (deltaPercent: number) => {
    const base = originalBudget; // Always use original budget as base
    const next = Math.round(base * (1 + deltaPercent / 100));
    setDraftBudget(next);
    setError(null);
  };

  // Handle manual input
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value === '') {
      setDraftBudget(0);
      return;
    }
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue >= 0) {
      setDraftBudget(Math.round(numValue));
      setError(null);
    }
  };

  // Handle save
  const handleSave = async () => {
    if (draftBudget < 0) {
      setError('Ngân sách không thể âm');
      return;
    }

    if (draftBudget === originalBudget) {
      onClose();
      return;
    }

    try {
      setSaving(true);
      setError(null);
      await onSave(draftBudget);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Lỗi khi cập nhật ngân sách');
    } finally {
      setSaving(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    setDraftBudget(originalBudget);
    setError(null);
    onClose();
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !saving) {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-50"
        onClick={handleCancel}
      />

      {/* Popover - Beautiful Design */}
      <div
        className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-white rounded-2xl shadow-2xl w-[480px] overflow-hidden border border-gray-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header với gradient */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 text-white">
          <h3 className="text-xl font-bold mb-1 flex items-center gap-2">
            <span>💰</span>
            <span>Chỉnh sửa Ngân sách</span>
          </h3>
          <p className="text-sm text-indigo-100 truncate">
            {row.adset_name || row.campaign_name || 'Nhóm quảng cáo'}
          </p>
          {row.adset_id && (
            <p className="text-xs text-indigo-200 mt-1">
              ID: {row.adset_id}
            </p>
          )}
        </div>

        <div className="p-6">
          {/* Current Budget - Beautiful Card */}
          <div className="mb-6 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-indigo-100">
            <div className="text-xs font-medium text-indigo-600 mb-1 uppercase tracking-wide">Ngân sách hiện tại</div>
            <div className="text-2xl font-bold text-indigo-900">
              {formatCurrency(originalBudget, currency)}
            </div>
            <div className="text-xs text-indigo-600 mt-1">
              {currency}{row.budget_type === 'LIFETIME' ? '/trọn đời' : '/ngày'}
            </div>
          </div>

          {/* Input - Centered & Large */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-3 text-center">
              Ngân sách mới
            </label>
            <div className="relative">
              <input
                ref={inputRef}
                type="number"
                min="0"
                step="1000"
                value={draftBudget || ''}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                className="w-full px-6 py-4 border-2 border-indigo-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 text-2xl font-bold text-center text-gray-900 transition-all"
                placeholder="128525"
                disabled={saving}
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-gray-500 bg-white px-2">
                {currency}
              </div>
            </div>
          </div>

          {/* Percentage Buttons - Redesigned */}
          <div className="mb-6">
            <div className="text-xs font-semibold text-gray-600 mb-3 text-center uppercase tracking-wide">Điều chỉnh nhanh</div>
            <div className="space-y-2">
              {/* Giảm row */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-500 w-12">Giảm:</span>
                <div className="flex-1 grid grid-cols-3 gap-2">
                  <button
                    onClick={() => adjustPercent(-10)}
                    disabled={saving}
                    className="px-4 py-2.5 bg-gradient-to-br from-amber-50 to-amber-100 text-amber-700 rounded-lg hover:from-amber-100 hover:to-amber-200 transition-all text-sm font-bold border border-amber-200 disabled:opacity-50 transform hover:scale-105 active:scale-95"
                  >
                    -10%
                  </button>
                  <button
                    onClick={() => adjustPercent(-20)}
                    disabled={saving}
                    className="px-4 py-2.5 bg-gradient-to-br from-amber-50 to-amber-100 text-amber-700 rounded-lg hover:from-amber-100 hover:to-amber-200 transition-all text-sm font-bold border border-amber-200 disabled:opacity-50 transform hover:scale-105 active:scale-95"
                  >
                    -20%
                  </button>
                  <button
                    onClick={() => adjustPercent(-30)}
                    disabled={saving}
                    className="px-4 py-2.5 bg-gradient-to-br from-amber-50 to-amber-100 text-amber-700 rounded-lg hover:from-amber-100 hover:to-amber-200 transition-all text-sm font-bold border border-amber-200 disabled:opacity-50 transform hover:scale-105 active:scale-95"
                  >
                    -30%
                  </button>
                </div>
              </div>
              {/* Tăng row */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-500 w-12">Tăng:</span>
                <div className="flex-1 grid grid-cols-3 gap-2">
                  <button
                    onClick={() => adjustPercent(10)}
                    disabled={saving}
                    className="px-4 py-2.5 bg-gradient-to-br from-green-50 to-green-100 text-green-700 rounded-lg hover:from-green-100 hover:to-green-200 transition-all text-sm font-bold border border-green-200 disabled:opacity-50 transform hover:scale-105 active:scale-95"
                  >
                    +10%
                  </button>
                  <button
                    onClick={() => adjustPercent(20)}
                    disabled={saving}
                    className="px-4 py-2.5 bg-gradient-to-br from-green-50 to-green-100 text-green-700 rounded-lg hover:from-green-100 hover:to-green-200 transition-all text-sm font-bold border border-green-200 disabled:opacity-50 transform hover:scale-105 active:scale-95"
                  >
                    +20%
                  </button>
                  <button
                    onClick={() => adjustPercent(30)}
                    disabled={saving}
                    className="px-4 py-2.5 bg-gradient-to-br from-green-50 to-green-100 text-green-700 rounded-lg hover:from-green-100 hover:to-green-200 transition-all text-sm font-bold border border-green-200 disabled:opacity-50 transform hover:scale-105 active:scale-95"
                  >
                    +30%
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={handleCancel}
              disabled={saving}
              className="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium disabled:opacity-50"
            >
              Hủy
            </button>
            <button
              onClick={handleSave}
              disabled={saving || draftBudget < 0}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Đang lưu...' : 'Lưu'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

