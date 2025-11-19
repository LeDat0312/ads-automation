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

  // ✅ COMPLETELY DIFFERENT columns for Lead vs Ecom (per DASHBOARD_SPEC.md)
  const columns = useMemo(() => {
    if (viewMode === 'lead') {
      // Lead columns: Checkbox, Trạng thái, Tên, Ngân sách, Chi tiêu, DATA, Giá DATA, Bắt đầu TT, Lượt mua, Chi phí/Lượt mua, Impressions
      return [
        { key: 'select', label: '', sortable: false, width: 'w-12', fixed: true },
        { key: 'status', label: 'Trạng thái', sortable: false, width: 'w-28', fixed: true },
        { key: 'adset_name', label: 'Tên nhóm QC', sortable: false, width: 'min-w-[280px]', fixed: true },
        { key: 'budget', label: 'Ngân sách', sortable: false, width: 'w-32' },
        { key: 'spend', label: 'Chi tiêu', sortable: true, width: 'w-32' },
        { key: 'results', label: 'DATA', sortable: true, width: 'w-28' },
        { key: 'data_cost', label: 'Giá DATA', sortable: true, width: 'w-32' },
        { key: 'checkouts_initiated', label: 'Bắt đầu TT', sortable: true, width: 'w-32' },
        { key: 'purchases', label: 'Lượt mua', sortable: true, width: 'w-28' },
        { key: 'cost_per_purchase', label: 'Chi phí/Lượt mua', sortable: true, width: 'w-36' },
        { key: 'impressions', label: 'Impressions', sortable: true, width: 'w-32' },
      ];
    } else {
      // Ecom columns: Checkbox, Trạng thái, Tên, Ngân sách, Chi tiêu, Giá trị mua, % ADS, Bắt đầu TT, Lượt mua, Chi phí/Lượt mua
      return [
        { key: 'select', label: '', sortable: false, width: 'w-12', fixed: true },
        { key: 'status', label: 'Trạng thái', sortable: false, width: 'w-28', fixed: true },
        { key: 'adset_name', label: 'Tên nhóm QC', sortable: false, width: 'min-w-[280px]', fixed: true },
        { key: 'budget', label: 'Ngân sách', sortable: false, width: 'w-32' },
        { key: 'spend', label: 'Chi tiêu', sortable: true, width: 'w-32' },
        { key: 'purchase_value', label: 'Giá trị mua', sortable: true, width: 'w-36' },
        { key: 'ads_percent', label: '% ADS', sortable: true, width: 'w-28' },
        { key: 'checkouts_initiated', label: 'Bắt đầu TT', sortable: true, width: 'w-32' },
        { key: 'purchases', label: 'Lượt mua', sortable: true, width: 'w-28' },
        { key: 'cost_per_purchase', label: 'Chi phí/Lượt mua', sortable: true, width: 'w-36' },
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
    <div className="bg-white rounded-lg shadow overflow-hidden">
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
  onDrillDown,
  onOpenBudgetEditor,
}) => {
  const statusIcon = row.is_active_now ? '✅' : '⏸️';
  const statusColor = row.is_active_now ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';

  if (viewMode === 'lead') {
    // Lead row: Checkbox, Status, Name(+prefix+account), Budget, Spend, DATA, Cost/DATA, Checkouts, Purchases, Cost/Purchase, Impressions
    return (
      <tr className="hover:bg-gray-50">
        {/* Checkbox - Fixed */}
        <td className="px-4 py-3 sticky left-0 z-10 bg-white" style={{ left: 0 }}>
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onSelect}
            className="rounded border-gray-300"
          />
        </td>

        {/* Status - Fixed with Toggle */}
        <td className="px-4 py-3 sticky z-10 bg-white" style={{ left: '3rem' }}>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={row.delivery === 'ACTIVE'}
              onChange={() => onStatusToggle?.(row)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            <span className="ml-2 text-xs font-medium text-gray-700">
              {row.delivery === 'ACTIVE' ? 'Bật' : 'Tắt'}
            </span>
          </label>
        </td>

        {/* Adset Name - Fixed with Drill-down */}
        <td className="px-4 py-3 sticky z-10 bg-white" style={{ left: '7rem' }}>
          <div className="font-semibold text-gray-900 truncate" title={row.adset_name}>
            {row.adset_name}
          </div>
          <div className="text-xs text-gray-500 flex items-center gap-2">
            <span className="font-medium text-indigo-600">{row.prefix || 'N/A'}</span>
            <span>•</span>
            {row.campaign_name && onDrillDown ? (
              <button
                onClick={() => onDrillDown('campaign', row.campaign_id, row.campaign_name)}
                className="text-indigo-600 hover:text-indigo-800 hover:underline truncate max-w-[150px]"
                title={`Click để xem chi tiết chiến dịch: ${row.campaign_name}`}
              >
                {row.campaign_name}
              </button>
            ) : (
              <span className="truncate max-w-[150px]" title={row.account_name}>{row.account_name}</span>
            )}
          </div>
        </td>

        {/* Budget - Clickable */}
        <td className="px-4 py-3 text-right">
          <button
            onClick={() => {
              // In lead view, can edit if budget_level is ADSET
              const canEdit = row.budget_level === 'ADSET';
              if (canEdit && onOpenBudgetEditor) {
                onOpenBudgetEditor(row);
              }
            }}
            className={`
              text-gray-700 hover:text-indigo-600 hover:underline transition-colors
              ${row.budget_level === 'ADSET'
                ? 'cursor-pointer font-medium'
                : 'cursor-not-allowed opacity-60'
              }
            `}
            title={
              row.budget_level === 'ADSET'
                ? 'Click để chỉnh sửa ngân sách'
                : 'Ngân sách ở cấp Chiến dịch'
            }
          >
            {formatCurrency(row.budget, row.currency)}
          </button>
        </td>

        {/* Spend */}
        <td className="px-4 py-3 text-right font-semibold text-gray-900">
          {formatCurrency(row.spend, row.currency)}
        </td>

        {/* DATA (results) */}
        <td className="px-4 py-3 text-right font-semibold text-green-600">
          {formatNumber(row.results)}
        </td>

        {/* Cost per DATA */}
        <td className="px-4 py-3 text-right font-semibold text-teal-600">
          {formatCurrency(row.data_cost, row.currency)}
        </td>

        {/* Checkouts Initiated */}
        <td className="px-4 py-3 text-right text-gray-700">
          {formatNumber(row.initiated_checkout || row.checkouts_initiated || 0)}
        </td>

        {/* Purchases */}
        <td className="px-4 py-3 text-right font-semibold text-purple-600">
          {formatNumber(row.purchases)}
        </td>

        {/* Cost per Purchase */}
        <td className="px-4 py-3 text-right text-gray-700">
          {formatCurrency(row.cost_per_purchase, row.currency)}
        </td>

        {/* Impressions */}
        <td className="px-4 py-3 text-right text-gray-600">
          {formatNumber(row.impressions)}
        </td>
      </tr>
    );
  } else {
    // Ecom row: Checkbox, Status, Name(+prefix+account), Budget, Spend, Purchase Value, % ADS, Checkouts, Purchases, Cost/Purchase
    return (
      <tr className="hover:bg-gray-50">
        {/* Checkbox - Fixed */}
        <td className="px-4 py-3 sticky left-0 z-10 bg-white" style={{ left: 0 }}>
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onSelect}
            className="rounded border-gray-300"
          />
        </td>

        {/* Status - Fixed */}
        <td className="px-4 py-3 sticky z-10 bg-white" style={{ left: '3rem' }}>
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}>
            {statusIcon}
          </span>
        </td>

        {/* Adset Name - Fixed */}
        <td className="px-4 py-3 sticky z-10 bg-white" style={{ left: '7rem' }}>
          <div className="font-semibold text-gray-900 truncate" title={row.adset_name}>
            {row.adset_name}
          </div>
          <div className="text-xs text-gray-500 flex items-center gap-2">
            <span className="font-medium text-indigo-600">{row.prefix || 'N/A'}</span>
            <span>•</span>
            <span className="truncate max-w-[150px]" title={row.account_name}>{row.account_name}</span>
          </div>
        </td>

        {/* Budget - Clickable */}
        <td className="px-4 py-3 text-right">
          <button
            onClick={() => {
              // In ecommerce view, can edit if budget_level is CAMPAIGN
              const canEdit = row.budget_level === 'CAMPAIGN';
              if (canEdit && onOpenBudgetEditor) {
                onOpenBudgetEditor(row);
              }
            }}
            className={`
              text-gray-700 hover:text-indigo-600 hover:underline transition-colors
              ${row.budget_level === 'CAMPAIGN'
                ? 'cursor-pointer font-medium'
                : 'cursor-not-allowed opacity-60'
              }
            `}
            title={
              row.budget_level === 'CAMPAIGN'
                ? 'Click để chỉnh sửa ngân sách'
                : 'Ngân sách ở cấp Nhóm quảng cáo'
            }
          >
            {formatCurrency(row.budget, row.currency)}
          </button>
        </td>

        {/* Spend */}
        <td className="px-4 py-3 text-right font-semibold text-gray-900">
          {formatCurrency(row.spend, row.currency)}
        </td>

        {/* Purchase Value */}
        <td className="px-4 py-3 text-right font-semibold text-green-600">
          {formatCurrency(row.purchase_value, row.currency)}
        </td>

        {/* % ADS */}
        <td className="px-4 py-3 text-right font-semibold text-rose-600">
          {formatPercentage(row.ads_percent || 0)}%
        </td>

        {/* Checkouts Initiated */}
        <td className="px-4 py-3 text-right text-gray-700">
          {formatNumber(row.initiated_checkout || row.checkouts_initiated || 0)}
        </td>

        {/* Purchases */}
        <td className="px-4 py-3 text-right font-semibold text-purple-600">
          {formatNumber(row.purchases)}
        </td>

        {/* Cost per Purchase */}
        <td className="px-4 py-3 text-right text-gray-700">
          {formatCurrency(row.cost_per_purchase, row.currency)}
        </td>
      </tr>
    );
  }
};

export default AdsetTable;
