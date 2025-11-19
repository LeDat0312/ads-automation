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
  const [draftBudget, setDraftBudget] = useState<number>(row.budget);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const originalBudget = row.budget;

  // Reset when row changes or popup opens
  useEffect(() => {
    if (isOpen) {
      setDraftBudget(row.budget);
      setError(null);
      // Focus input after a short delay
      setTimeout(() => {
        inputRef.current?.focus();
        inputRef.current?.select();
      }, 100);
    }
  }, [isOpen, row.budget]);

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

      {/* Popover */}
      <div
        className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-white rounded-xl shadow-2xl p-6 w-96"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            Điều chỉnh ngân sách
          </h3>
          <p className="text-sm text-gray-600">
            {row.adset_name || row.campaign_name || 'Nhóm quảng cáo'}
          </p>
          {row.budget_level === 'CAMPAIGN' && (
            <p className="text-xs text-amber-600 mt-1">
              ⚠️ Ngân sách ở cấp Chiến dịch
            </p>
          )}
        </div>

        {/* Current Budget Display */}
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="text-xs text-gray-600 mb-1">Ngân sách hiện tại</div>
          <div className="text-lg font-semibold text-gray-900">
            {formatCurrency(originalBudget, currency)}
          </div>
        </div>

        {/* Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ngân sách mới ({currency}/ngày)
          </label>
          <input
            ref={inputRef}
            type="number"
            min="0"
            step="1000"
            value={draftBudget || ''}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-lg font-semibold"
            placeholder="Nhập số tiền"
            disabled={saving}
          />
        </div>

        {/* Percentage Buttons */}
        <div className="mb-4">
          <div className="text-xs text-gray-600 mb-2">Điều chỉnh nhanh</div>
          <div className="grid grid-cols-3 gap-2 mb-2">
            <button
              onClick={() => adjustPercent(-30)}
              disabled={saving}
              className="px-3 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium disabled:opacity-50"
            >
              -30%
            </button>
            <button
              onClick={() => adjustPercent(-20)}
              disabled={saving}
              className="px-3 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium disabled:opacity-50"
            >
              -20%
            </button>
            <button
              onClick={() => adjustPercent(-10)}
              disabled={saving}
              className="px-3 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium disabled:opacity-50"
            >
              -10%
            </button>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => adjustPercent(10)}
              disabled={saving}
              className="px-3 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors text-sm font-medium disabled:opacity-50"
            >
              +10%
            </button>
            <button
              onClick={() => adjustPercent(20)}
              disabled={saving}
              className="px-3 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors text-sm font-medium disabled:opacity-50"
            >
              +20%
            </button>
            <button
              onClick={() => adjustPercent(30)}
              disabled={saving}
              className="px-3 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors text-sm font-medium disabled:opacity-50"
            >
              +30%
            </button>
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
    </>
  );
}

