import React, { useMemo, useState, useRef, useEffect } from 'react';
import type { AdsetTableProps, AdsetRow, SortableColumn, ViewMode } from '@/types/dashboard';
import { formatCurrency, formatNumber, formatPercentage } from '@/utils/formatters';
import BudgetEditor from './BudgetEditor';

export const AdsetTable: React.FC<AdsetTableProps> = ({
  rows,
  viewMode,
  currentLevel = 'adset',
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
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>({});
  const [resizingColumn, setResizingColumn] = useState<string | null>(null);
  const tableRef = useRef<HTMLTableElement>(null);
  
  // Helper function to check if budget can be edited
  const canEditBudget = (row: AdsetRow, level: 'campaign' | 'adset' | 'ad'): boolean => {
    if (!row.budget_level) return false;
    if (level === 'campaign') {
      // Tab Chiến dịch: chỉ cho edit nếu budget_level === 'CAMPAIGN'
      return row.budget_level === 'CAMPAIGN';
    } else if (level === 'adset') {
      // Tab Nhóm quảng cáo: chỉ cho edit nếu budget_level === 'ADSET'
      return row.budget_level === 'ADSET';
    }
    return false;
  };

  // ✅ COMPLETELY DIFFERENT columns for Lead vs Ecom (per old dashboard)
  // Default column widths
  const defaultWidths: Record<string, number> = {
    select: 48,
    status: 80,
    name: 300,
    delivery: 96,
    budget: 128,
    spend: 128,
    results: 112,
    data_cost: 128,
    cost_per_checkout_initiated: 128,
    checkouts_initiated: 128,
    cost_per_purchase: 128,
    purchases: 112,
    cpm: 112,
    impressions: 128,
    reach: 128,
    frequency: 112,
    clicks: 112,
    ctr: 96,
    cpc: 112,
    ads_percent: 112,
    tlc: 96,
    purchase_value: 144,
  };

  const columns = useMemo(() => {
    if (viewMode === 'lead') {
      // Lead columns: Chọn, Bật/Tắt, Tên, Phân Phối, Ngân Sách, Chi Tiêu, Kết Quả, Giá DATA, Chi Phi/BĐTT, Bắt Đầu TT, Chi phí / LM, Lượt Mua, CPM, Hiển Thị, Tiếp Cận, Tần Suất, Nhấp, CTR, CPC
      return [
        { key: 'select', label: 'Chọn', sortable: false, width: columnWidths.select || defaultWidths.select, fixed: true },
        { key: 'status', label: 'Bật/Tắt', sortable: false, width: columnWidths.status || defaultWidths.status, fixed: true },
        { key: 'name', label: 'Tên', sortable: false, width: columnWidths.name || defaultWidths.name, fixed: true },
        { key: 'delivery', label: 'Phân Phối', sortable: false, width: columnWidths.delivery || defaultWidths.delivery },
        { key: 'budget', label: 'Ngân Sách', sortable: false, width: columnWidths.budget || defaultWidths.budget },
        { key: 'spend', label: 'Chi Tiêu', sortable: true, width: columnWidths.spend || defaultWidths.spend },
        { key: 'results', label: 'Kết Quả', sortable: true, width: columnWidths.results || defaultWidths.results },
        { key: 'data_cost', label: 'Giá DATA', sortable: true, width: columnWidths.data_cost || defaultWidths.data_cost },
        { key: 'cost_per_checkout_initiated', label: 'Chi Phí/BĐTT', sortable: true, width: columnWidths.cost_per_checkout_initiated || defaultWidths.cost_per_checkout_initiated },
        { key: 'checkouts_initiated', label: 'Bắt Đầu TT', sortable: true, width: columnWidths.checkouts_initiated || defaultWidths.checkouts_initiated },
        { key: 'cost_per_purchase', label: 'Chi phí / LM', sortable: true, width: columnWidths.cost_per_purchase || defaultWidths.cost_per_purchase },
        { key: 'purchases', label: 'Lượt Mua', sortable: true, width: columnWidths.purchases || defaultWidths.purchases },
        { key: 'cpm', label: 'CPM', sortable: true, width: columnWidths.cpm || defaultWidths.cpm },
        { key: 'impressions', label: 'Hiển Thị', sortable: true, width: columnWidths.impressions || defaultWidths.impressions },
        { key: 'reach', label: 'Tiếp Cận', sortable: true, width: columnWidths.reach || defaultWidths.reach },
        { key: 'frequency', label: 'Tần Suất', sortable: true, width: columnWidths.frequency || defaultWidths.frequency },
        { key: 'clicks', label: 'Nhấp', sortable: true, width: columnWidths.clicks || defaultWidths.clicks },
        { key: 'ctr', label: 'CTR', sortable: true, width: columnWidths.ctr || defaultWidths.ctr },
        { key: 'cpc', label: 'CPC', sortable: true, width: columnWidths.cpc || defaultWidths.cpc },
      ];
    } else {
      // Ecom columns: Chọn, Bật/Tắt, Tên, Phân Phối, Ngân Sách, Chi Tiêu, % ADS, Kết Quả, Giá DATA, TLC, Chi Phí/Bắt Đầu TT, Bắt Đầu TT, Chi Phí/Lượt Mua, Lượt Mua, Giá Trị CĐ, CPM, Hiển Thị, Tiếp Cận, Tần Suất, Nhấp, CTR, CPC
      return [
        { key: 'select', label: 'Chọn', sortable: false, width: columnWidths.select || defaultWidths.select, fixed: true },
        { key: 'status', label: 'Bật/Tắt', sortable: false, width: columnWidths.status || defaultWidths.status, fixed: true },
        { key: 'name', label: 'Tên', sortable: false, width: columnWidths.name || defaultWidths.name, fixed: true },
        { key: 'delivery', label: 'Phân Phối', sortable: false, width: columnWidths.delivery || defaultWidths.delivery },
        { key: 'budget', label: 'Ngân Sách', sortable: false, width: columnWidths.budget || defaultWidths.budget },
        { key: 'spend', label: 'Chi Tiêu', sortable: true, width: columnWidths.spend || defaultWidths.spend },
        { key: 'ads_percent', label: '% ADS', sortable: true, width: columnWidths.ads_percent || defaultWidths.ads_percent },
        { key: 'results', label: 'Kết Quả', sortable: true, width: columnWidths.results || defaultWidths.results },
        { key: 'data_cost', label: 'Giá DATA', sortable: true, width: columnWidths.data_cost || defaultWidths.data_cost },
        { key: 'tlc', label: 'TLC', sortable: true, width: columnWidths.tlc || defaultWidths.tlc },
        { key: 'cost_per_checkout_initiated', label: 'Chi Phí/Bắt Đầu TT', sortable: true, width: columnWidths.cost_per_checkout_initiated || defaultWidths.cost_per_checkout_initiated },
        { key: 'checkouts_initiated', label: 'Bắt Đầu TT', sortable: true, width: columnWidths.checkouts_initiated || defaultWidths.checkouts_initiated },
        { key: 'cost_per_purchase', label: 'Chi Phí/Lượt Mua', sortable: true, width: columnWidths.cost_per_purchase || defaultWidths.cost_per_purchase },
        { key: 'purchases', label: 'Lượt Mua', sortable: true, width: columnWidths.purchases || defaultWidths.purchases },
        { key: 'purchase_value', label: 'Giá Trị CĐ', sortable: true, width: columnWidths.purchase_value || defaultWidths.purchase_value },
        { key: 'cpm', label: 'CPM', sortable: true, width: columnWidths.cpm || defaultWidths.cpm },
        { key: 'impressions', label: 'Hiển Thị', sortable: true, width: columnWidths.impressions || defaultWidths.impressions },
        { key: 'reach', label: 'Tiếp Cận', sortable: true, width: columnWidths.reach || defaultWidths.reach },
        { key: 'frequency', label: 'Tần Suất', sortable: true, width: columnWidths.frequency || defaultWidths.frequency },
        { key: 'clicks', label: 'Nhấp', sortable: true, width: columnWidths.clicks || defaultWidths.clicks },
        { key: 'ctr', label: 'CTR', sortable: true, width: columnWidths.ctr || defaultWidths.ctr },
        { key: 'cpc', label: 'CPC', sortable: true, width: columnWidths.cpc || defaultWidths.cpc },
      ];
    }
  }, [viewMode, columnWidths]);

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
    if (!sortConfig || sortConfig.column !== column) {
      return (
        <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    return sortConfig.direction === 'asc' ? (
      <svg className="w-3 h-3 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="w-3 h-3 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
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
        <table className="min-w-full" style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead style={{ background: '#f9fafb' }}>
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`
                    ${col.sortable ? 'cursor-pointer hover:bg-gray-100 select-none' : ''}
                  `}
                  style={{
                    borderBottom: '1px solid #f3f4f6',
                    background: col.fixed ? '#f9fafb' : '#f9fafb',
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '14px',
                    position: col.fixed ? 'sticky' : 'relative',
                    top: 0,
                    zIndex: col.fixed ? 10 : 1,
                    width: typeof col.width === 'number' ? `${col.width}px` : undefined,
                    minWidth: typeof col.width === 'number' ? `${col.width}px` : undefined,
                    ...(col.key === 'select' ? { left: 0, padding: '8px' } :
                        col.key === 'status' ? { left: '3rem', padding: '8px' } :
                        col.key === 'name' ? { left: '5.5rem', padding: '12px' } :
                        { padding: '12px' }),
                    textAlign: (col.key === 'select' || col.key === 'status' || col.key === 'delivery') ? 'center' :
                               (col.key === 'name') ? 'left' :
                               (col.sortable || ['spend', 'results', 'data_cost', 'cost_per_checkout_initiated', 'checkouts_initiated', 'cost_per_purchase', 'purchases', 'cpm', 'impressions', 'reach', 'frequency', 'clicks', 'ctr', 'cpc', 'budget'].includes(col.key)) ? 'center' : 'left'
                  }}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className={`flex items-center gap-1 ${(col.key === 'select' || col.key === 'status' || col.key === 'delivery' || (col.sortable && col.key !== 'name')) ? 'justify-center' : 'justify-start'}`} style={{ position: 'relative' }}>
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
                    {!col.fixed && (
                      <div
                        className="absolute right-0 top-0 h-full w-1 cursor-col-resize hover:bg-indigo-400 bg-transparent"
                        style={{ width: '4px', marginRight: '-2px' }}
                        onMouseDown={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setResizingColumn(col.key);
                          const startX = e.clientX;
                          const startWidth = col.width;
                          
                          const handleMouseMove = (e: MouseEvent) => {
                            const diff = e.clientX - startX;
                            const newWidth = Math.max(50, startWidth + diff);
                            setColumnWidths(prev => ({ ...prev, [col.key]: newWidth }));
                          };
                          
                          const handleMouseUp = () => {
                            setResizingColumn(null);
                            document.removeEventListener('mousemove', handleMouseMove);
                            document.removeEventListener('mouseup', handleMouseUp);
                          };
                          
                          document.addEventListener('mousemove', handleMouseMove);
                          document.addEventListener('mouseup', handleMouseUp);
                        }}
                      />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody style={{ background: 'white' }}>
            {rows.map((row) => {
              const rowId = row.id || row.adset_id || row.campaign_id || row.ad_id || '';
              return (
                <TableRow
                  key={rowId}
                  row={row}
                  viewMode={viewMode}
                  currentLevel={currentLevel}
                  isSelected={selectedIds.has(rowId)}
                  onSelect={() => handleSelectRow(rowId)}
                  onStatusToggle={onStatusToggle}
                  onDrillDown={onDrillDown}
                  onOpenBudgetEditor={setBudgetEditorRow}
                  canEditBudget={canEditBudget}
                  columnWidths={columnWidths}
                  defaultWidths={defaultWidths}
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
  currentLevel: 'campaign' | 'adset' | 'ad';
  isSelected: boolean;
  onSelect: () => void;
  onStatusToggle?: (row: AdsetRow) => void;
  onDrillDown?: (level: 'campaign' | 'adset', id: string, name: string) => void;
  onOpenBudgetEditor?: (row: AdsetRow) => void;
  canEditBudget: (row: AdsetRow, level: 'campaign' | 'adset' | 'ad') => boolean;
  columnWidths: Record<string, number>;
  defaultWidths: Record<string, number>;
}

const TableRow: React.FC<TableRowProps> = ({ 
  row, 
  viewMode,
  currentLevel,
  isSelected, 
  onSelect,
  onStatusToggle,
  onOpenBudgetEditor,
  canEditBudget,
  columnWidths,
  defaultWidths,
}) => {
  const getColumnWidth = (key: string) => columnWidths[key] || defaultWidths[key] || 128;
  if (viewMode === 'lead') {
    return (
      <tr 
        style={{ 
          borderBottom: '1px solid #f3f4f6',
        }}
        className="hover:bg-[#f9fafb] transition-colors"
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
      >
        {/* Checkbox */}
        <td 
          className="sticky left-0 z-10 bg-white" 
          style={{ 
            left: 0,
            padding: '8px',
            fontSize: '14px',
            color: '#1f2937',
            borderBottom: '1px solid #f3f4f6',
            textAlign: 'center',
            width: `${getColumnWidth('select')}px`,
            minWidth: `${getColumnWidth('select')}px`
          }}
        >
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onSelect}
            className="rounded border-gray-300"
          />
        </td>

        {/* Status Toggle */}
        <td 
          className="sticky z-10 bg-white" 
          style={{ 
            left: '3rem',
            padding: '8px',
            fontSize: '14px',
            color: '#1f2937',
            borderBottom: '1px solid #f3f4f6',
            textAlign: 'center',
            width: `${getColumnWidth('status')}px`,
            minWidth: `${getColumnWidth('status')}px`
          }}
        >
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
        <td 
          className="sticky z-10 bg-white" 
          style={{ 
            left: '5.5rem',
            padding: '12px',
            fontSize: '14px',
            color: '#1f2937',
            borderBottom: '1px solid #f3f4f6',
            width: `${getColumnWidth('name')}px`,
            minWidth: `${getColumnWidth('name')}px`
          }}
        >
          <div className="font-semibold" style={{ fontSize: '14px', lineHeight: '1.4', fontWeight: 600 }}>
            {row.adset_name || row.campaign_name || row.ad_name || '-'}
          </div>
          {row.adset_id && (
            <div style={{ fontSize: '12px', marginTop: '2px', color: '#6b7280' }}>
              ID: {row.adset_id}
            </div>
          )}
        </td>

        {/* Delivery Status - chỉ icon tròn */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#1f2937', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('delivery')}px`, minWidth: `${getColumnWidth('delivery')}px` }}>
          <span 
            className="inline-block rounded-full"
            style={{
              width: '12px',
              height: '12px',
              backgroundColor: row.delivery === 'ACTIVE' ? '#22c55e' : (row.delivery === 'PAUSED' ? '#ef4444' : '#d1d5db')
            }}
            title={row.delivery === 'ACTIVE' ? 'Đang chạy' : row.delivery === 'PAUSED' ? 'Tạm dừng' : 'Không xác định'}
          />
        </td>

        {/* Budget */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#1f2937', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('budget')}px`, minWidth: `${getColumnWidth('budget')}px` }}>
          {(() => {
            const canEdit = canEditBudget(row, currentLevel);
            let budgetDisplay: string;
            if (canEdit) {
              budgetDisplay = formatCurrency(row.budget || 0, row.currency || 'VND');
            } else {
              // Nếu budget_level === 'CAMPAIGN' và đang ở tab 'adset' → hiển thị "Ngân sách chiến dịch"
              if (row.budget_level === 'CAMPAIGN' && currentLevel === 'adset') {
                budgetDisplay = 'Ngân sách chiến dịch';
              }
              // Nếu budget_level === 'ADSET' và đang ở tab 'campaign' → hiển thị "Ngân sách nhóm QC"
              else if (row.budget_level === 'ADSET' && currentLevel === 'campaign') {
                budgetDisplay = 'Ngân sách nhóm QC';
              }
              // Trường hợp khác: hiển thị số tiền (nếu có)
              else if (row.budget && row.budget > 0) {
                budgetDisplay = formatCurrency(row.budget, row.currency || 'VND');
              } else {
                // Nếu budget = 0 và không thể edit, hiển thị text tương ứng
                if (row.budget_level === 'CAMPAIGN') {
                  budgetDisplay = currentLevel === 'campaign' ? formatCurrency(row.budget || 0, row.currency || 'VND') : 'Ngân sách chiến dịch';
                } else {
                  budgetDisplay = currentLevel === 'adset' ? formatCurrency(row.budget || 0, row.currency || 'VND') : 'Ngân sách nhóm QC';
                }
              }
            }
            const budgetTitle = canEdit 
              ? 'Click để chỉnh sửa ngân sách'
              : `Ngân sách đang ở cấp ${row.budget_level === 'CAMPAIGN' ? 'chiến dịch' : 'nhóm quảng cáo'}. Chỉnh ở tab ${row.budget_level === 'CAMPAIGN' ? 'Chiến Dịch' : 'Nhóm Quảng Cáo'}`;
            
            if (canEdit && onOpenBudgetEditor) {
              return (
                <button
                  onClick={() => onOpenBudgetEditor(row)}
                  className="hover:text-indigo-600 hover:underline transition-colors cursor-pointer font-medium"
                  style={{ color: '#1f2937', background: 'none', border: 'none', padding: 0, fontSize: '14px' }}
                  title={budgetTitle}
                >
                  {budgetDisplay}
                </button>
              );
            } else {
              return (
                <span 
                  className="cursor-not-allowed opacity-60"
                  style={{ color: '#1f2937', fontSize: '14px' }}
                  title={budgetTitle}
                >
                  {budgetDisplay}
                </span>
              );
            }
          })()}
        </td>

        {/* Spend */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#1f2937', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('spend')}px`, minWidth: `${getColumnWidth('spend')}px` }}>
          {formatCurrency(row.spend, row.currency || 'VND')}
        </td>

        {/* Results (DATA) */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#22c55e', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('results')}px`, minWidth: `${getColumnWidth('results')}px` }}>
          {formatNumber(row.results)}
        </td>

        {/* Cost per DATA */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#9333ea', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('data_cost')}px`, minWidth: `${getColumnWidth('data_cost')}px` }}>
          {formatCurrency(row.data_cost, row.currency || 'VND')}
        </td>

        {/* Cost per Checkout Initiated (Chi Phí/BĐTT) */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('cost_per_checkout_initiated')}px`, minWidth: `${getColumnWidth('cost_per_checkout_initiated')}px` }}>
          {formatCurrency(row.cost_per_checkout_initiated || 0, row.currency || 'VND')}
        </td>

        {/* Checkouts Initiated (Bắt Đầu TT) */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('checkouts_initiated')}px`, minWidth: `${getColumnWidth('checkouts_initiated')}px` }}>
          {formatNumber(row.initiated_checkout || row.checkouts_initiated || 0)}
        </td>

        {/* Cost per Purchase (Chi phí / LM) */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('cost_per_purchase')}px`, minWidth: `${getColumnWidth('cost_per_purchase')}px` }}>
          {formatCurrency(row.cost_per_purchase || 0, row.currency || 'VND')}
        </td>

        {/* Purchases (Lượt Mua) */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#ec4899', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('purchases')}px`, minWidth: `${getColumnWidth('purchases')}px` }}>
          {formatNumber(row.purchases)}
        </td>

        {/* CPM */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('cpm')}px`, minWidth: `${getColumnWidth('cpm')}px` }}>
          {formatCurrency(row.cpm || 0, row.currency || 'VND')}
        </td>

        {/* Impressions */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('impressions')}px`, minWidth: `${getColumnWidth('impressions')}px` }}>
          {formatNumber(row.impressions)}
        </td>

        {/* Reach */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('reach')}px`, minWidth: `${getColumnWidth('reach')}px` }}>
          {formatNumber(row.reach || 0)}
        </td>

        {/* Frequency */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('frequency')}px`, minWidth: `${getColumnWidth('frequency')}px` }}>
          {(row.frequency || 0).toFixed(2)}
        </td>

        {/* Clicks */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('clicks')}px`, minWidth: `${getColumnWidth('clicks')}px` }}>
          {formatNumber(row.clicks || 0)}
        </td>

        {/* CTR */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('ctr')}px`, minWidth: `${getColumnWidth('ctr')}px` }}>
          {formatPercentage(row.ctr || 0)}%
        </td>

        {/* CPC */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('cpc')}px`, minWidth: `${getColumnWidth('cpc')}px` }}>
          {formatCurrency(row.cpc || 0, row.currency || 'VND')}
        </td>
      </tr>
    );
  } else {
    // E-COMMERCE
    return (
      <tr 
        style={{ 
          borderBottom: '1px solid #f3f4f6',
        }}
        className="hover:bg-[#f9fafb] transition-colors"
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
      >
        {/* Checkbox */}
        <td 
          className="sticky left-0 z-10 bg-white" 
          style={{ 
            left: 0,
            padding: '8px',
            fontSize: '14px',
            color: '#1f2937',
            borderBottom: '1px solid #f3f4f6',
            textAlign: 'center',
            width: `${getColumnWidth('select')}px`,
            minWidth: `${getColumnWidth('select')}px`
          }}
        >
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onSelect}
            className="rounded border-gray-300"
          />
        </td>

        {/* Status Toggle */}
        <td 
          className="sticky z-10 bg-white" 
          style={{ 
            left: '3rem',
            padding: '8px',
            fontSize: '14px',
            color: '#1f2937',
            borderBottom: '1px solid #f3f4f6',
            textAlign: 'center',
            width: `${getColumnWidth('status')}px`,
            minWidth: `${getColumnWidth('status')}px`
          }}
        >
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
        <td 
          className="sticky z-10 bg-white" 
          style={{ 
            left: '5.5rem',
            padding: '12px',
            fontSize: '14px',
            color: '#1f2937',
            borderBottom: '1px solid #f3f4f6',
            width: `${getColumnWidth('name')}px`,
            minWidth: `${getColumnWidth('name')}px`
          }}
        >
          <div className="font-semibold" style={{ fontSize: '14px', lineHeight: '1.4', fontWeight: 600 }}>
            {row.adset_name || row.campaign_name || row.ad_name || '-'}
          </div>
          {row.adset_id && (
            <div style={{ fontSize: '12px', marginTop: '2px', color: '#6b7280' }}>
              ID: {row.adset_id}
            </div>
          )}
        </td>

        {/* Delivery Status - chỉ icon tròn */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#1f2937', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('delivery')}px`, minWidth: `${getColumnWidth('delivery')}px` }}>
          <span 
            className="inline-block rounded-full"
            style={{
              width: '12px',
              height: '12px',
              backgroundColor: row.delivery === 'ACTIVE' ? '#22c55e' : (row.delivery === 'PAUSED' ? '#ef4444' : '#d1d5db')
            }}
            title={row.delivery === 'ACTIVE' ? 'Đang chạy' : row.delivery === 'PAUSED' ? 'Tạm dừng' : 'Không xác định'}
          />
        </td>

        {/* Budget */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#1f2937', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('budget')}px`, minWidth: `${getColumnWidth('budget')}px` }}>
          {(() => {
            const canEdit = canEditBudget(row, currentLevel);
            let budgetDisplay: string;
            if (canEdit) {
              budgetDisplay = formatCurrency(row.budget || 0, row.currency || 'VND');
            } else {
              // Nếu budget_level === 'CAMPAIGN' và đang ở tab 'adset' → hiển thị "Ngân sách chiến dịch"
              if (row.budget_level === 'CAMPAIGN' && currentLevel === 'adset') {
                budgetDisplay = 'Ngân sách chiến dịch';
              }
              // Nếu budget_level === 'ADSET' và đang ở tab 'campaign' → hiển thị "Ngân sách nhóm QC"
              else if (row.budget_level === 'ADSET' && currentLevel === 'campaign') {
                budgetDisplay = 'Ngân sách nhóm QC';
              }
              // Trường hợp khác: hiển thị số tiền (nếu có)
              else if (row.budget && row.budget > 0) {
                budgetDisplay = formatCurrency(row.budget, row.currency || 'VND');
              } else {
                // Nếu budget = 0 và không thể edit, hiển thị text tương ứng
                if (row.budget_level === 'CAMPAIGN') {
                  budgetDisplay = currentLevel === 'campaign' ? formatCurrency(row.budget || 0, row.currency || 'VND') : 'Ngân sách chiến dịch';
                } else {
                  budgetDisplay = currentLevel === 'adset' ? formatCurrency(row.budget || 0, row.currency || 'VND') : 'Ngân sách nhóm QC';
                }
              }
            }
            const budgetTitle = canEdit 
              ? 'Click để chỉnh sửa ngân sách'
              : `Ngân sách đang ở cấp ${row.budget_level === 'CAMPAIGN' ? 'chiến dịch' : 'nhóm quảng cáo'}. Chỉnh ở tab ${row.budget_level === 'CAMPAIGN' ? 'Chiến Dịch' : 'Nhóm Quảng Cáo'}`;
            
            if (canEdit && onOpenBudgetEditor) {
              return (
                <button
                  onClick={() => onOpenBudgetEditor(row)}
                  className="hover:text-indigo-600 hover:underline transition-colors cursor-pointer font-medium"
                  style={{ color: '#1f2937', background: 'none', border: 'none', padding: 0, fontSize: '14px' }}
                  title={budgetTitle}
                >
                  {budgetDisplay}
                </button>
              );
            } else {
              return (
                <span 
                  className="cursor-not-allowed opacity-60"
                  style={{ color: '#1f2937', fontSize: '14px' }}
                  title={budgetTitle}
                >
                  {budgetDisplay}
                </span>
              );
            }
          })()}
        </td>

        {/* Spend */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#1f2937', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('spend')}px`, minWidth: `${getColumnWidth('spend')}px` }}>
          {formatCurrency(row.spend, row.currency || 'VND')}
        </td>

        {/* % ADS */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#ef4444', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('ads_percent')}px`, minWidth: `${getColumnWidth('ads_percent')}px` }}>
          {formatPercentage(row.ads_percent || 0)}%
        </td>

        {/* Results (Kết quả) */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#22c55e', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('results')}px`, minWidth: `${getColumnWidth('results')}px` }}>
          {formatNumber(row.results)}
        </td>

        {/* Cost per DATA */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#9333ea', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('data_cost')}px`, minWidth: `${getColumnWidth('data_cost')}px` }}>
          {formatCurrency(row.data_cost, row.currency || 'VND')}
        </td>

        {/* TLC (Tỷ lệ chuyển đổi) */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('tlc')}px`, minWidth: `${getColumnWidth('tlc')}px` }}>
          {formatPercentage(row.tlc || (row.initiated_checkout && row.impressions ? (row.initiated_checkout / row.impressions) * 100 : 0))}%
        </td>

        {/* Cost per Checkout Initiated */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('cost_per_checkout_initiated')}px`, minWidth: `${getColumnWidth('cost_per_checkout_initiated')}px` }}>
          {formatCurrency(row.cost_per_checkout_initiated || 0, row.currency || 'VND')}
        </td>

        {/* Checkouts Initiated */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('checkouts_initiated')}px`, minWidth: `${getColumnWidth('checkouts_initiated')}px` }}>
          {formatNumber(row.initiated_checkout || row.checkouts_initiated || 0)}
        </td>

        {/* Cost per Purchase */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('cost_per_purchase')}px`, minWidth: `${getColumnWidth('cost_per_purchase')}px` }}>
          {formatCurrency(row.cost_per_purchase || 0, row.currency || 'VND')}
        </td>

        {/* Purchases */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#ec4899', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('purchases')}px`, minWidth: `${getColumnWidth('purchases')}px` }}>
          {formatNumber(row.purchases)}
        </td>

        {/* Purchase Value */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#22c55e', textAlign: 'center', fontWeight: 600, borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('purchase_value')}px`, minWidth: `${getColumnWidth('purchase_value')}px` }}>
          {formatCurrency(row.purchase_value, row.currency || 'VND')}
        </td>

        {/* CPM */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('cpm')}px`, minWidth: `${getColumnWidth('cpm')}px` }}>
          {formatCurrency(row.cpm || 0, row.currency || 'VND')}
        </td>

        {/* Impressions */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('impressions')}px`, minWidth: `${getColumnWidth('impressions')}px` }}>
          {formatNumber(row.impressions)}
        </td>

        {/* Reach */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('reach')}px`, minWidth: `${getColumnWidth('reach')}px` }}>
          {formatNumber(row.reach || 0)}
        </td>

        {/* Frequency */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('frequency')}px`, minWidth: `${getColumnWidth('frequency')}px` }}>
          {(row.frequency || 0).toFixed(2)}
        </td>

        {/* Clicks */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('clicks')}px`, minWidth: `${getColumnWidth('clicks')}px` }}>
          {formatNumber(row.clicks || 0)}
        </td>

        {/* CTR */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('ctr')}px`, minWidth: `${getColumnWidth('ctr')}px` }}>
          {formatPercentage(row.ctr || 0)}%
        </td>

        {/* CPC */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#6b7280', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('cpc')}px`, minWidth: `${getColumnWidth('cpc')}px` }}>
          {formatCurrency(row.cpc || 0, row.currency || 'VND')}
        </td>
      </tr>
    );
  }
};

export default AdsetTable;
