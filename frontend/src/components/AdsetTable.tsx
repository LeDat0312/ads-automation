import React, { useMemo } from 'react';
import type { AdsetTableProps, AdsetRow, SortableColumn } from '@/types/dashboard';
import { formatCurrency, formatNumber, formatPercentage, getStatusColor, getStatusLabel } from '@/utils/formatters';

export const AdsetTable: React.FC<AdsetTableProps> = ({
  rows,
  viewMode,
  loading = false,
  onSort,
  sortConfig,
  selectedIds = new Set(),
  onSelectionChange,
}) => {
  const isEcommerce = viewMode === 'ecommerce';

  // Column definitions
  const columns = useMemo(() => {
    const baseColumns = [
      { key: 'select', label: 'Chọn', sortable: false, width: 'w-12' },
      { key: 'status', label: 'Trạng thái', sortable: false, width: 'w-32' },
      { key: 'adset_name', label: 'Tên Nhóm QC', sortable: false, width: 'min-w-[250px]' },
      { key: 'campaign_name', label: 'Chiến dịch', sortable: false, width: 'min-w-[200px]' },
      { key: 'budget', label: 'Ngân sách', sortable: false, width: 'w-32' },
      { key: 'spend', label: 'Chi tiêu', sortable: true, width: 'w-32' },
      { key: 'results', label: 'DATA', sortable: true, width: 'w-24' },
      { key: 'data_cost', label: 'Giá DATA', sortable: true, width: 'w-28' },
      { key: 'checkouts_initiated', label: 'Bắt đầu TT', sortable: true, width: 'w-28' },
      { key: 'cost_per_checkout_initiated', label: 'Chi phí/TT', sortable: true, width: 'w-28' },
      { key: 'purchases', label: 'Lượt mua', sortable: true, width: 'w-28' },
      { key: 'cost_per_purchase', label: 'Chi phí/Mua', sortable: true, width: 'w-28' },
    ];

    if (isEcommerce) {
      baseColumns.push({
        key: 'ads_percent',
        label: '% ADS',
        sortable: true,
        width: 'w-24',
      });
    }

    baseColumns.push(
      { key: 'purchase_value', label: 'Giá trị CV', sortable: true, width: 'w-32' },
      { key: 'cpm', label: 'CPM', sortable: true, width: 'w-24' },
      { key: 'impressions', label: 'Hiển thị', sortable: true, width: 'w-28' },
      { key: 'reach', label: 'Tiếp cận', sortable: true, width: 'w-28' },
      { key: 'clicks', label: 'Nhấp', sortable: true, width: 'w-24' },
      { key: 'ctr', label: 'CTR', sortable: true, width: 'w-20' },
      { key: 'cpc', label: 'CPC', sortable: true, width: 'w-24' }
    );

    return baseColumns;
  }, [isEcommerce]);

  const handleSelectAll = () => {
    if (!onSelectionChange) return;
    
    if (selectedIds.size === rows.length) {
      onSelectionChange(new Set());
    } else {
      onSelectionChange(new Set(rows.map(r => r.adset_id)));
    }
  };

  const handleSelectRow = (adsetId: string) => {
    if (!onSelectionChange) return;
    
    const newSelection = new Set(selectedIds);
    if (newSelection.has(adsetId)) {
      newSelection.delete(adsetId);
    } else {
      newSelection.add(adsetId);
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
                    px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider
                    ${col.sortable ? 'cursor-pointer hover:bg-gray-100 select-none' : ''}
                  `}
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
            {rows.map((row) => (
              <TableRow
                key={row.adset_id}
                row={row}
                isEcommerce={isEcommerce}
                isSelected={selectedIds.has(row.adset_id)}
                onSelect={() => handleSelectRow(row.adset_id)}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

interface TableRowProps {
  row: AdsetRow;
  isEcommerce: boolean;
  isSelected: boolean;
  onSelect: () => void;
}

const TableRow: React.FC<TableRowProps> = ({ row, isEcommerce, isSelected, onSelect }) => {
  const statusColor = getStatusColor(row.delivery);
  const statusLabel = getStatusLabel(row.delivery);

  return (
    <tr className="hover:bg-gray-50">
      {/* Select */}
      <td className="px-4 py-3">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={onSelect}
          className="rounded border-gray-300"
        />
      </td>

      {/* Status */}
      <td className="px-4 py-3">
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}>
          {statusLabel}
        </span>
      </td>

      {/* Adset Name */}
      <td className="px-4 py-3">
        <div className="font-semibold text-gray-900 truncate" title={row.adset_name}>
          {row.adset_name}
        </div>
        <div className="text-xs text-gray-500 truncate" title={row.adset_id}>
          ID: {row.adset_id}
        </div>
      </td>

      {/* Campaign Name */}
      <td className="px-4 py-3">
        <div className="text-gray-700 truncate" title={row.campaign_name}>
          {row.campaign_name}
        </div>
      </td>

      {/* Budget */}
      <td className="px-4 py-3 text-right text-gray-700">
        {formatCurrency(row.budget, row.currency)}
      </td>

      {/* Spend */}
      <td className="px-4 py-3 text-right font-semibold text-gray-900">
        {formatCurrency(row.spend, row.currency)}
      </td>

      {/* DATA (Results) */}
      <td className="px-4 py-3 text-right font-semibold text-green-600">
        {formatNumber(row.results)}
      </td>

      {/* Giá DATA */}
      <td className="px-4 py-3 text-right font-semibold text-purple-600">
        {formatCurrency(row.data_cost, row.currency)}
      </td>

      {/* Checkouts Initiated */}
      <td className="px-4 py-3 text-right text-gray-700">
        {formatNumber(row.checkouts_initiated)}
      </td>

      {/* Cost per Checkout */}
      <td className="px-4 py-3 text-right text-gray-700">
        {formatCurrency(row.cost_per_checkout_initiated, row.currency)}
      </td>

      {/* Purchases */}
      <td className="px-4 py-3 text-right font-semibold text-pink-600">
        {formatNumber(row.purchases)}
      </td>

      {/* Cost per Purchase */}
      <td className="px-4 py-3 text-right text-gray-700">
        {formatCurrency(row.cost_per_purchase, row.currency)}
      </td>

      {/* % ADS (Ecommerce only) */}
      {isEcommerce && (
        <td className="px-4 py-3 text-right font-semibold text-red-600">
          {formatPercentage(row.ads_percent || 0)}%
        </td>
      )}

      {/* Purchase Value */}
      <td className="px-4 py-3 text-right text-gray-700">
        {formatCurrency(row.purchase_value, row.currency)}
      </td>

      {/* CPM */}
      <td className="px-4 py-3 text-right text-gray-600">
        {formatCurrency(row.cpm, row.currency)}
      </td>

      {/* Impressions */}
      <td className="px-4 py-3 text-right text-gray-600">
        {formatNumber(row.impressions)}
      </td>

      {/* Reach */}
      <td className="px-4 py-3 text-right text-gray-600">
        {formatNumber(row.reach)}
      </td>

      {/* Clicks */}
      <td className="px-4 py-3 text-right text-gray-600">
        {formatNumber(row.clicks)}
      </td>

      {/* CTR */}
      <td className="px-4 py-3 text-right text-gray-600">
        {row.ctr.toFixed(2)}%
      </td>

      {/* CPC */}
      <td className="px-4 py-3 text-right text-gray-600">
        {formatCurrency(row.cpc, row.currency)}
      </td>
    </tr>
  );
};

export default AdsetTable;
