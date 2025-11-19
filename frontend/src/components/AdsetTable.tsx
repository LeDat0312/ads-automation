import React, { useMemo, useState } from 'react';
import type { AdsetTableProps, AdsetRow, SortableColumn, ViewMode } from '@/types/dashboard';
import { formatCurrency, formatNumber, formatPercentage } from '@/utils/formatters';
import BudgetEditor from './BudgetEditor';

export const AdsetTable: React.FC<AdsetTableProps> = ({
  rows,
  viewMode,
  loading = false,
  onSort,
  sortConfig,
  selectedIds = new Set(),
  onSelectionChange,
  onStatusToggle,
  onBudgetUpdate,
  onDrillDown,
  currency = 'VND',
}) => {
  const [budgetEditorRow, setBudgetEditorRow] = useState<AdsetRow | null>(null);

  // ✅ COMPLETELY DIFFERENT columns for Lead vs Ecom (per old dashboard)
  const columns = useMemo(() => {
    if (viewMode === 'lead') {
      // Lead columns: Chọn, Bật/Tắt, Tên, Phân Phối, Ngân Sách, Chi Tiêu, Kết Quả, Giá DATA, Chi Phí Bắt Đầu TT, Bắt Đầu TT, Lượt Mua, CPM, Hiển Thị, Tiếp Cận, Tần Suất, Nhấp, CTR, CPC
      return [
        { key: 'select', label: 'Chọn', sortable: false, width: 'w-16', fixed: true },
        { key: 'status', label: 'Bật/Tắt', sortable: false, width: 'w-24', fixed: true },
        { key: 'name', label: 'Tên', sortable: false, width: 'min-w-[300px]', fixed: true },
        { key: 'delivery', label: 'Phân Phối', sortable: false, width: 'w-28' },
        { key: 'budget', label: 'Ngân Sách', sortable: false, width: 'w-32' },
        { key: 'spend', label: 'Chi Tiêu', sortable: true, width: 'w-32' },
        { key: 'results', label: 'Kết Quả', sortable: true, width: 'w-28' },
        { key: 'data_cost', label: 'Giá DATA', sortable: true, width: 'w-32' },
        { key: 'cost_per_checkout', label: 'Chi Phí/Bắt Đầu TT', sortable: true, width: 'w-40' },
        { key: 'checkouts_initiated', label: 'Bắt Đầu TT', sortable: true, width: 'w-32' },
        { key: 'purchases', label: 'Lượt Mua', sortable: true, width: 'w-28' },
        { key: 'cpm', label: 'CPM', sortable: true, width: 'w-28' },
        { key: 'impressions', label: 'Hiển Thị', sortable: true, width: 'w-32' },
        { key: 'reach', label: 'Tiếp Cận', sortable: true, width: 'w-32' },
        { key: 'frequency', label: 'Tần Suất', sortable: true, width: 'w-28' },
        { key: 'clicks', label: 'Nhấp', sortable: true, width: 'w-28' },
        { key: 'ctr', label: 'CTR', sortable: true, width: 'w-24' },
        { key: 'cpc', label: 'CPC', sortable: true, width: 'w-28' },
      ];
    } else {
      // Ecom columns: Chọn, Bật/Tắt, Tên, Phân Phối, Ngân Sách, Chi Tiêu, % ADS, Kết Quả, Giá DATA, TLC, Bắt Đầu TT, Lượt Mua, Giá Trị CĐ, CPM, Hiển Thị, Tiếp Cận, Tần Suất, Nhấp, CTR, CPC
      return [
        { key: 'select', label: 'Chọn', sortable: false, width: 'w-16', fixed: true },
        { key: 'status', label: 'Bật/Tắt', sortable: false, width: 'w-24', fixed: true },
        { key: 'name', label: 'Tên', sortable: false, width: 'min-w-[300px]', fixed: true },
        { key: 'delivery', label: 'Phân Phối', sortable: false, width: 'w-28' },
        { key: 'budget', label: 'Ngân Sách', sortable: false, width: 'w-32' },
        { key: 'spend', label: 'Chi Tiêu', sortable: true, width: 'w-32' },
        { key: 'ads_percent', label: '% ADS', sortable: true, width: 'w-28' },
        { key: 'results', label: 'Kết Quả', sortable: true, width: 'w-28' },
        { key: 'data_cost', label: 'Giá DATA', sortable: true, width: 'w-32' },
        { key: 'tlc', label: 'TLC', sortable: true, width: 'w-24' },
        { key: 'checkouts_initiated', label: 'Bắt Đầu TT', sortable: true, width: 'w-32' },
        { key: 'purchases', label: 'Lượt Mua', sortable: true, width: 'w-28' },
        { key: 'purchase_value', label: 'Giá Trị CĐ', sortable: true, width: 'w-36' },
        { key: 'cpm', label: 'CPM', sortable: true, width: 'w-28' },
        { key: 'impressions', label: 'Hiển Thị', sortable: true, width: 'w-32' },
        { key: 'reach', label: 'Tiếp Cận', sortable: true, width: 'w-32' },
        { key: 'frequency', label: 'Tần Suất', sortable: true, width: 'w-28' },
        { key: 'clicks', label: 'Nhấp', sortable: true, width: 'w-28' },
        { key: 'ctr', label: 'CTR', sortable: true, width: 'w-24' },
        { key: 'cpc', label: 'CPC', sortable: true, width: 'w-28' },
      ];
    }
  }, [viewMode]);

  const handleSelectAll = () => {
    if (!onSelectionChange) return;
    
    if (selectedIds.size === rows.length) {
      onSelectionChange(new Set());
    } else {
      // Use id field (which can be campaign_id, adset_id, or ad_id depending on level)
      onSelectionChange(new Set(rows.map(r => r.id || r.adset_id || r.campaign_id || r.ad_id || '').filter(Boolean)));
    }
  };

  const handleSelectRow = (rowId: string) => {
    if (!onSelectionChange) return;
    
    const newSelection = new Set(selectedIds);
    if (newSelection.has(rowId)) {
      newSelection.delete(rowId);
    } else {
      newSelection.add(rowId);
    }
    onSelectionChange(newSelection);
  };

  const handleSort = (column: string) => {
    if (!onSort) return;
    const col = column as SortableColumn;
    const colDef = columns.find(c => c.key === column);
    if (colDef?.sortable) {
      onSort(col);
    }
  };

  const getSortIcon = (column: string) => {
    if (!sortConfig || sortConfig.column !== column) return '↕️';
    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Đang tải dữ liệu...</p>
        </div>
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="text-6xl mb-4">📊</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Không có dữ liệu</h3>
        <p className="text-gray-600">Thử điều chỉnh bộ lọc hoặc khoảng thời gian</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-b-lg shadow overflow-hidden border border-gray-200 border-t-0">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`
                    ${col.width}
                    ${col.fixed ? 'sticky left-0 z-10 bg-gray-50' : ''}
                    px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider
                    ${col.sortable ? 'cursor-pointer hover:bg-gray-100 select-none' : ''}
                  `}
                  style={
                    col.key === 'select' ? { left: 0 } :
                    col.key === 'status' ? { left: '3rem' } :
                    col.key === 'adset_name' ? { left: '7rem' } :
                    undefined
                  }
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center gap-1">
                    {col.key === 'select' ? (
                      <input
                        type="checkbox"
                        checked={selectedIds.size === rows.length && rows.length > 0}
                        onChange={handleSelectAll}
                        className="rounded border-gray-300"
                      />
                    ) : (
                      <>
                        <span>{col.label}</span>
                        {col.sortable && <span className="text-gray-400">{getSortIcon(col.key)}</span>}
                      </>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rows.map((row) => {
              const rowId = row.id || row.adset_id || row.campaign_id || row.ad_id || '';
              return (
                <TableRow
                  key={rowId}
                  row={row}
                  viewMode={viewMode}
                  isSelected={selectedIds.has(rowId)}
                  onSelect={() => handleSelectRow(rowId)}
                  onStatusToggle={onStatusToggle}
                  onDrillDown={onDrillDown}
                  onOpenBudgetEditor={setBudgetEditorRow}
                />
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Budget Editor Popup */}
      {budgetEditorRow && onBudgetUpdate && (
        <BudgetEditor
          row={budgetEditorRow}
          isOpen={!!budgetEditorRow}
          onClose={() => setBudgetEditorRow(null)}
          onSave={async (newBudget) => {
            await onBudgetUpdate(budgetEditorRow, newBudget);
            setBudgetEditorRow(null);
          }}
          currency={currency}
        />
      )}
    </div>
  );
};

interface TableRowProps {
  row: AdsetRow;
  viewMode: ViewMode;
  isSelected: boolean;
  onSelect: () => void;
  onStatusToggle?: (row: AdsetRow) => void;
  onDrillDown?: (level: 'campaign' | 'adset', id: string, name: string) => void;
  onOpenBudgetEditor?: (row: AdsetRow) => void;
}

const TableRow: React.FC<TableRowProps> = ({ 
  row, 
  viewMode, 
  isSelected, 
  onSelect,
  onStatusToggle,
  onOpenBudgetEditor,
}) => {
  const statusColor = row.is_active_now ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';

  if (viewMode === 'lead') {
    return (
      <tr className="hover:bg-gray-50">
        {/* Checkbox */}
        <td className="px-3 py-3 sticky left-0 z-10 bg-white" style={{ left: 0 }}>
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onSelect}
            className="rounded border-gray-300"
          />
        </td>

        {/* Status Toggle */}
        <td className="px-3 py-3 sticky z-10 bg-white" style={{ left: '4rem' }}>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={row.delivery === 'ACTIVE'}
              onChange={() => onStatusToggle?.(row)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
          </label>
        </td>

        {/* Name */}
        <td className="px-3 py-3 sticky z-10 bg-white" style={{ left: '8rem' }}>
          <div className="font-semibold text-gray-900 truncate" title={row.adset_name}>
            {row.adset_name}
          </div>
          <div className="text-xs text-gray-500 flex items-center gap-2">
            <span className="font-medium text-indigo-600">{row.prefix || 'N/A'}</span>
            <span>•</span>
            <span className="truncate max-w-[150px]" title={row.account_name}>{row.account_name}</span>
          </div>
        </td>

        {/* Delivery Status */}
        <td className="px-3 py-3">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}>
            {row.delivery === 'ACTIVE' ? 'Đang chạy' : 'Tạm dừng'}
          </span>
        </td>

        {/* Budget */}
        <td className="px-3 py-3 text-right">
          <button
            onClick={() => {
              const canEdit = row.budget_level === 'ADSET';
              if (canEdit && onOpenBudgetEditor) {
                onOpenBudgetEditor(row);
              }
            }}
            className={`
              text-gray-700 hover:text-indigo-600 hover:underline transition-colors text-sm
              ${row.budget_level === 'ADSET' ? 'cursor-pointer font-medium' : 'cursor-not-allowed opacity-60'}
            `}
            title={row.budget_level === 'ADSET' ? 'Click để chỉnh sửa' : 'Ngân sách ở cấp Chiến dịch'}
          >
            {formatCurrency(row.budget, row.currency)}
          </button>
        </td>

        {/* Spend */}
        <td className="px-3 py-3 text-right font-semibold text-gray-900 text-sm">
          {formatCurrency(row.spend, row.currency)}
        </td>

        {/* Results (DATA) */}
        <td className="px-3 py-3 text-right font-semibold text-green-600 text-sm">
          {formatNumber(row.results)}
        </td>

        {/* Cost per DATA */}
        <td className="px-3 py-3 text-right font-semibold text-teal-600 text-sm">
          {formatCurrency(row.data_cost, row.currency)}
        </td>

        {/* Cost per Checkout */}
        <td className="px-3 py-3 text-right text-gray-700 text-sm">
          {formatCurrency((row.initiated_checkout && row.initiated_checkout > 0) ? row.spend / row.initiated_checkout : 0, row.currency)}
        </td>

        {/* Checkouts Initiated */}
        <td className="px-3 py-3 text-right text-gray-700 text-sm">
          {formatNumber(row.initiated_checkout || row.checkouts_initiated || 0)}
        </td>

        {/* Purchases */}
        <td className="px-3 py-3 text-right font-semibold text-purple-600 text-sm">
          {formatNumber(row.purchases)}
        </td>

        {/* CPM */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatCurrency(row.cpm || 0, row.currency)}
        </td>

        {/* Impressions */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatNumber(row.impressions)}
        </td>

        {/* Reach */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatNumber(row.reach || 0)}
        </td>

        {/* Frequency */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {(row.frequency || 0).toFixed(2)}
        </td>

        {/* Clicks */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatNumber(row.clicks || 0)}
        </td>

        {/* CTR */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatPercentage(row.ctr || 0)}%
        </td>

        {/* CPC */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatCurrency(row.cpc || 0, row.currency)}
        </td>
      </tr>
    );
  } else {
    // E-COMMERCE
    return (
      <tr className="hover:bg-gray-50">
        {/* Checkbox */}
        <td className="px-3 py-3 sticky left-0 z-10 bg-white" style={{ left: 0 }}>
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onSelect}
            className="rounded border-gray-300"
          />
        </td>

        {/* Status Toggle */}
        <td className="px-3 py-3 sticky z-10 bg-white" style={{ left: '4rem' }}>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={row.delivery === 'ACTIVE'}
              onChange={() => onStatusToggle?.(row)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
          </label>
        </td>

        {/* Name */}
        <td className="px-3 py-3 sticky z-10 bg-white" style={{ left: '8rem' }}>
          <div className="font-semibold text-gray-900 truncate" title={row.adset_name}>
            {row.adset_name}
          </div>
          <div className="text-xs text-gray-500 flex items-center gap-2">
            <span className="font-medium text-indigo-600">{row.prefix || 'N/A'}</span>
            <span>•</span>
            <span className="truncate max-w-[150px]" title={row.account_name}>{row.account_name}</span>
          </div>
        </td>

        {/* Delivery Status */}
        <td className="px-3 py-3">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}>
            {row.delivery === 'ACTIVE' ? 'Đang chạy' : 'Tạm dừng'}
          </span>
        </td>

        {/* Budget */}
        <td className="px-3 py-3 text-right">
          <button
            onClick={() => {
              const canEdit = row.budget_level === 'CAMPAIGN';
              if (canEdit && onOpenBudgetEditor) {
                onOpenBudgetEditor(row);
              }
            }}
            className={`
              text-gray-700 hover:text-indigo-600 hover:underline transition-colors text-sm
              ${row.budget_level === 'CAMPAIGN' ? 'cursor-pointer font-medium' : 'cursor-not-allowed opacity-60'}
            `}
            title={row.budget_level === 'CAMPAIGN' ? 'Click để chỉnh sửa' : 'Ngân sách ở cấp Adset'}
          >
            {formatCurrency(row.budget, row.currency)}
          </button>
        </td>

        {/* Spend */}
        <td className="px-3 py-3 text-right font-semibold text-gray-900 text-sm">
          {formatCurrency(row.spend, row.currency)}
        </td>

        {/* % ADS */}
        <td className="px-3 py-3 text-right font-semibold text-rose-600 text-sm">
          {formatPercentage(row.ads_percent || 0)}%
        </td>

        {/* Results (Kết quả) */}
        <td className="px-3 py-3 text-right font-semibold text-green-600 text-sm">
          {formatNumber(row.results)}
        </td>

        {/* Cost per DATA */}
        <td className="px-3 py-3 text-right font-semibold text-teal-600 text-sm">
          {formatCurrency(row.data_cost, row.currency)}
        </td>

        {/* TLC (Tỷ lệ chuyển đổi) */}
        <td className="px-3 py-3 text-right text-gray-700 text-sm">
          {formatPercentage(row.tlc || (row.initiated_checkout && row.impressions ? (row.initiated_checkout / row.impressions) * 100 : 0))}%
        </td>

        {/* Checkouts Initiated */}
        <td className="px-3 py-3 text-right text-gray-700 text-sm">
          {formatNumber(row.initiated_checkout || row.checkouts_initiated || 0)}
        </td>

        {/* Purchases */}
        <td className="px-3 py-3 text-right font-semibold text-purple-600 text-sm">
          {formatNumber(row.purchases)}
        </td>

        {/* Purchase Value */}
        <td className="px-3 py-3 text-right font-semibold text-green-600 text-sm">
          {formatCurrency(row.purchase_value, row.currency)}
        </td>

        {/* CPM */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatCurrency(row.cpm || 0, row.currency)}
        </td>

        {/* Impressions */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatNumber(row.impressions)}
        </td>

        {/* Reach */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatNumber(row.reach || 0)}
        </td>

        {/* Frequency */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {(row.frequency || 0).toFixed(2)}
        </td>

        {/* Clicks */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatNumber(row.clicks || 0)}
        </td>

        {/* CTR */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatPercentage(row.ctr || 0)}%
        </td>

        {/* CPC */}
        <td className="px-3 py-3 text-right text-gray-600 text-sm">
          {formatCurrency(row.cpc || 0, row.currency)}
        </td>
      </tr>
    );
  }
};

export default AdsetTable;
