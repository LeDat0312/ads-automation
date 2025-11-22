import React, { useMemo, useState } from 'react';
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
  totals,
}) => {
  const [budgetEditorRow, setBudgetEditorRow] = useState<AdsetRow | null>(null);
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>({});
  
  // Helper function to get column width
  const getColumnWidth = (key: string) => columnWidths[key] || defaultWidths[key] || 128;
  
  // Helper function to check if budget can be edited
  // ✅ CHO PHÉP CHỈNH TẤT CẢ: adset budget VÀ campaign budget (CBO)
  const canEditBudget = (_row: AdsetRow, _level: 'campaign' | 'adset' | 'ad'): boolean => {
    // ✅ MỚI: Cho phép chỉnh ngân sách ở cả 2 cấp (campaign & adset)
    // KHÔNG CÒN hạn chế phải chuyển tab
    return true;  // User có thể chỉnh mọi loại ngân sách
  };

  // ✅ COMPLETELY DIFFERENT columns for Lead vs Ecom (per old dashboard)
  // Default column widths
  const defaultWidths: Record<string, number> = {
    select: 48,
    status: 80,
    name: 180,  // Giảm từ 300 xuống 180 để tiết kiệm không gian
    delivery: 80,  // Giảm từ 96 xuống 80
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
        { key: 'budget', label: 'Ngân Sách', sortable: true, width: columnWidths.budget || defaultWidths.budget },
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
        { key: 'budget', label: 'Ngân Sách', sortable: true, width: columnWidths.budget || defaultWidths.budget },
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
      <div className="bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden">
        <div className="min-h-[260px] flex flex-col items-center justify-center gap-4 p-12">
          <div className="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center">
            <svg className="w-10 h-10 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Không có dữ liệu</h3>
            <p className="text-sm text-gray-600">Thử điều chỉnh bộ lọc hoặc khoảng thời gian</p>
          </div>
        </div>
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
                    ...(col.key === 'select' ? { 
                        left: 0, 
                        padding: '8px',
                        width: `${getColumnWidth('select')}px`,
                        minWidth: `${getColumnWidth('select')}px`
                      } :
                        col.key === 'status' ? { 
                        left: `${getColumnWidth('select')}px`, 
                        padding: '8px',
                        width: `${getColumnWidth('status')}px`,
                        minWidth: `${getColumnWidth('status')}px`
                      } :
                        col.key === 'name' ? { 
                        left: `${getColumnWidth('select') + getColumnWidth('status')}px`, 
                        padding: '8px 12px',
                        width: `${getColumnWidth('name')}px`,
                        minWidth: `${getColumnWidth('name')}px`
                      } :
                        { 
                        padding: '12px',
                        width: `${getColumnWidth(col.key)}px`,
                        minWidth: `${getColumnWidth(col.key)}px`
                      }),
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
                        className="absolute right-0 top-0 h-full cursor-col-resize hover:bg-indigo-400 bg-transparent transition-colors"
                        style={{ 
                          width: '6px', 
                          marginRight: '-3px',
                          zIndex: 10
                        }}
                        onMouseDown={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          const startX = e.clientX;
                          // Lấy width hiện tại từ state hoặc default
                          const currentWidth = getColumnWidth(col.key);
                          let lastWidth = currentWidth;
                          
                          const handleMouseMove = (e: MouseEvent) => {
                            const diff = e.clientX - startX;
                            const newWidth = Math.max(50, Math.min(500, currentWidth + diff));
                            if (Math.abs(newWidth - lastWidth) > 1) {  // Chỉ update nếu thay đổi > 1px để tối ưu performance
                              lastWidth = newWidth;
                              setColumnWidths(prev => ({ ...prev, [col.key]: newWidth }));
                            }
                          };
                          
                          const handleMouseUp = () => {
                            document.removeEventListener('mousemove', handleMouseMove);
                            document.removeEventListener('mouseup', handleMouseUp);
                            // Reset cursor và user selection
                            document.body.style.cursor = '';
                            document.body.style.userSelect = '';
                          };
                          
                          // Set cursor và disable text selection khi bắt đầu resize
                          document.body.style.cursor = 'col-resize';
                          document.body.style.userSelect = 'none';
                          document.addEventListener('mousemove', handleMouseMove);
                          document.addEventListener('mouseup', handleMouseUp);
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#818cf8';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'transparent';
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
            
            {/* Tổng kết row */}
            {totals && (
              <tr style={{ 
                background: '#f9fafb', 
                borderTop: '2px solid #e5e7eb',
                fontWeight: 600
              }}>
                {/* Chọn, Bật/Tắt, Tên - 3 cột đầu */}
                <td colSpan={3} style={{ padding: '12px', textAlign: 'left', fontSize: '14px', color: '#1f2937', fontWeight: 600 }}>
                  Tổng
                </td>
                {/* Phân Phối */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#1f2937' }}></td>
                {/* Ngân Sách */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#1f2937' }}></td>
                {/* Chi Tiêu */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#1f2937', fontWeight: 600 }}>
                  {formatCurrency(totals.spend || 0, currency)}
                </td>
                {/* % ADS (chỉ Ecommerce) */}
                {viewMode === 'ecommerce' && (
                  <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#ef4444', fontWeight: 600 }}>
                    {formatPercentage(totals.ads_percent || 0)}%
                  </td>
                )}
                {/* Kết Quả */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#22c55e', fontWeight: 600 }}>
                  {formatNumber(totals.results || 0)}
                </td>
                {/* Giá DATA */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#9333ea', fontWeight: 600 }}>
                  {formatCurrency(totals.data_cost || 0, currency)}
                </td>
                {/* TLC (chỉ Ecommerce) */}
                {viewMode === 'ecommerce' && (
                  <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                    {formatPercentage(totals.tlc || 0)}%
                  </td>
                )}
                {/* Chi Phí/BĐTT */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {formatCurrency(totals.cost_per_checkout_initiated || 0, currency)}
                </td>
                {/* Bắt Đầu TT */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {formatNumber(totals.initiated_checkout || 0)}
                </td>
                {/* Chi phí / LM */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {formatCurrency(totals.cost_per_purchase || 0, currency)}
                </td>
                {/* Lượt Mua */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: viewMode === 'ecommerce' ? '#ec4899' : '#22c55e', fontWeight: 600 }}>
                  {formatNumber(totals.purchases || 0)}
                </td>
                {/* Giá Trị CĐ (chỉ Ecommerce) */}
                {viewMode === 'ecommerce' && (
                  <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#22c55e', fontWeight: 600 }}>
                    {formatCurrency(totals.purchase_value || 0, currency)}
                  </td>
                )}
                {/* CPM */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {formatCurrency(totals.cpm || 0, currency)}
                </td>
                {/* Hiển Thị */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {formatNumber(totals.impressions || 0)}
                </td>
                {/* Tiếp Cận */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {formatNumber(totals.reach || 0)}
                </td>
                {/* Tần Suất */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {(totals.frequency || 0).toFixed(2)}
                </td>
                {/* Nhấp */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {formatNumber(totals.clicks || 0)}
                </td>
                {/* CTR */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {formatPercentage(totals.ctr || 0)}%
                </td>
                {/* CPC */}
                <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
                  {formatCurrency(totals.cpc || 0, currency)}
                </td>
              </tr>
            )}
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
          currentLevel={currentLevel}
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

// ⭐ Helper function: Get budget display text
const getBudgetDisplay = (row: AdsetRow, canEdit: boolean): { display: string; value: number; title: string } => {
  const budgetValue = row.current_budget || 0;
  const isLifetime = row.budget_type === 'LIFETIME';
  const levelText = row.budget_level === 'CAMPAIGN' ? 'chiến dịch' : 'nhóm QC';
  
  let budgetDisplay: string;
  
  if (budgetValue > 0) {
    if (canEdit) {
      budgetDisplay = formatCurrency(budgetValue, row.currency || 'VND');
    } else {
      budgetDisplay = isLifetime
        ? `Ngân sách ${levelText} trọn đời (${formatCurrency(budgetValue, row.currency || 'VND')})`
        : `Ngân sách ${levelText} (${formatCurrency(budgetValue, row.currency || 'VND')}/ngày)`;
    }
  } else {
    budgetDisplay = `Ngân sách ${levelText}`;
  }
  
  const budgetTitle = canEdit 
    ? 'Click để chỉnh sửa ngân sách'
    : budgetDisplay;
    
  return { display: budgetDisplay, value: budgetValue, title: budgetTitle };
};

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
            left: `${getColumnWidth('select')}px`,
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
              checked={(() => {
                // 🔹 FIX: Ưu tiên configured_status, sau đó effective_status, cuối cùng delivery
                const status = (row.configured_status || row.effective_status || row.delivery || 'UNKNOWN').toUpperCase();
                return status === 'ACTIVE';
              })()}
              onChange={() => onStatusToggle?.(row)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
          </label>
        </td>

        {/* Name - Width cố định nhưng có thể resize */}
        <td 
          className="sticky z-10 bg-white" 
          style={{ 
            left: `${getColumnWidth('select') + getColumnWidth('status')}px`,
            padding: '8px 10px',
            fontSize: '14px',
            color: '#1f2937',
            borderBottom: '1px solid #f3f4f6',
            width: `${getColumnWidth('name')}px`,
            minWidth: `${getColumnWidth('name')}px`,
            maxWidth: `${getColumnWidth('name')}px`
          }}
        >
          <div className="font-semibold truncate" style={{ fontSize: '14px', lineHeight: '1.3', fontWeight: 600 }}>
            {row.adset_name || row.campaign_name || row.ad_name || '-'}
          </div>
          {row.adset_id && (
            <div className="truncate" style={{ fontSize: '11px', marginTop: '1px', color: '#6b7280' }}>
              {row.adset_id}
            </div>
          )}
        </td>

        {/* Delivery Status - chỉ icon tròn, sát với tên */}
        <td style={{ 
          padding: '8px 4px', 
          fontSize: '14px', 
          color: '#1f2937', 
          textAlign: 'center', 
          borderBottom: '1px solid #f3f4f6', 
          width: `${getColumnWidth('delivery')}px`, 
          minWidth: `${getColumnWidth('delivery')}px` 
        }}>
          <span 
            className="inline-block rounded-full"
            style={{
              width: '12px',
              height: '12px',
              backgroundColor: (row.effective_status || row.delivery || 'UNKNOWN') === 'ACTIVE' ? '#22c55e' : ((row.effective_status || row.delivery || 'UNKNOWN') === 'PAUSED' ? '#ef4444' : '#d1d5db')
            }}
            title={(row.effective_status || row.delivery || 'UNKNOWN') === 'ACTIVE' ? 'Đang chạy' : (row.effective_status || row.delivery || 'UNKNOWN') === 'PAUSED' ? 'Tạm dừng' : 'Không xác định'}
          />
        </td>

        {/* Budget */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#1f2937', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('budget')}px`, minWidth: `${getColumnWidth('budget')}px` }}>
          {(() => {
            const canEdit = canEditBudget(row, currentLevel);
            let budgetDisplay: string;
            let budgetValue: number | null = null;
            
            // Xác định budget value và loại (daily/lifetime)
            const usingCampaignBudget = row.using_campaign_budget || (row.budget_level === 'CAMPAIGN');
            const isCampaignLevel = currentLevel === 'campaign';
            
            if (isCampaignLevel && row.budget_level === 'CAMPAIGN') {
              // Tab Campaign, row là campaign
              if (row.campaign_daily_budget && row.campaign_daily_budget > 0) {
                budgetValue = row.campaign_daily_budget;
                budgetDisplay = canEdit 
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách chiến dịch (${formatCurrency(budgetValue, row.currency || 'VND')}/ngày)`;
              } else if (row.campaign_lifetime_budget && row.campaign_lifetime_budget > 0) {
                budgetValue = row.campaign_lifetime_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách chiến dịch trọn đời (${formatCurrency(budgetValue, row.currency || 'VND')})`;
              } else {
                budgetDisplay = 'Ngân sách chiến dịch';
              }
            } else if (usingCampaignBudget) {
              // Adset đang dùng campaign budget (CBO)
              if (row.campaign_daily_budget && row.campaign_daily_budget > 0) {
                budgetValue = row.campaign_daily_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách chiến dịch (${formatCurrency(budgetValue, row.currency || 'VND')}/ngày)`;
              } else if (row.campaign_lifetime_budget && row.campaign_lifetime_budget > 0) {
                budgetValue = row.campaign_lifetime_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách chiến dịch trọn đời (${formatCurrency(budgetValue, row.currency || 'VND')})`;
              } else {
                budgetDisplay = 'Ngân sách chiến dịch';
              }
            } else {
              // Adset có budget riêng
              if (row.adset_daily_budget && row.adset_daily_budget > 0) {
                budgetValue = row.adset_daily_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách nhóm QC (${formatCurrency(budgetValue, row.currency || 'VND')}/ngày)`;
              } else if (row.adset_lifetime_budget && row.adset_lifetime_budget > 0) {
                budgetValue = row.adset_lifetime_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách nhóm QC trọn đời (${formatCurrency(budgetValue, row.currency || 'VND')})`;
              } else {
                budgetDisplay = 'Ngân sách nhóm QC';
              }
            }
            
            const budgetTitle = canEdit 
              ? 'Click để chỉnh sửa ngân sách'
              : budgetDisplay;
            
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
          {row.cost_per_purchase != null ? formatCurrency(row.cost_per_purchase, row.currency || 'VND') : '-'}
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
            left: `${getColumnWidth('select')}px`,
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
              checked={(() => {
                // 🔹 FIX: Ưu tiên configured_status, sau đó effective_status, cuối cùng delivery
                const status = (row.configured_status || row.effective_status || row.delivery || 'UNKNOWN').toUpperCase();
                return status === 'ACTIVE';
              })()}
              onChange={() => onStatusToggle?.(row)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
          </label>
        </td>

        {/* Name - Width cố định nhưng có thể resize */}
        <td 
          className="sticky z-10 bg-white" 
          style={{ 
            left: `${getColumnWidth('select') + getColumnWidth('status')}px`,
            padding: '8px 10px',
            fontSize: '14px',
            color: '#1f2937',
            borderBottom: '1px solid #f3f4f6',
            width: `${getColumnWidth('name')}px`,
            minWidth: `${getColumnWidth('name')}px`,
            maxWidth: `${getColumnWidth('name')}px`
          }}
        >
          <div className="font-semibold truncate" style={{ fontSize: '14px', lineHeight: '1.3', fontWeight: 600 }}>
            {row.adset_name || row.campaign_name || row.ad_name || '-'}
          </div>
          {row.adset_id && (
            <div className="truncate" style={{ fontSize: '11px', marginTop: '1px', color: '#6b7280' }}>
              {row.adset_id}
            </div>
          )}
        </td>

        {/* Delivery Status - chỉ icon tròn, sát với tên */}
        <td style={{ 
          padding: '8px 4px', 
          fontSize: '14px', 
          color: '#1f2937', 
          textAlign: 'center', 
          borderBottom: '1px solid #f3f4f6', 
          width: `${getColumnWidth('delivery')}px`, 
          minWidth: `${getColumnWidth('delivery')}px` 
        }}>
          <span 
            className="inline-block rounded-full"
            style={{
              width: '12px',
              height: '12px',
              backgroundColor: (row.effective_status || row.delivery || 'UNKNOWN') === 'ACTIVE' ? '#22c55e' : ((row.effective_status || row.delivery || 'UNKNOWN') === 'PAUSED' ? '#ef4444' : '#d1d5db')
            }}
            title={(row.effective_status || row.delivery || 'UNKNOWN') === 'ACTIVE' ? 'Đang chạy' : (row.effective_status || row.delivery || 'UNKNOWN') === 'PAUSED' ? 'Tạm dừng' : 'Không xác định'}
          />
        </td>

        {/* Budget */}
        <td style={{ padding: '12px', fontSize: '14px', color: '#1f2937', textAlign: 'center', borderBottom: '1px solid #f3f4f6', width: `${getColumnWidth('budget')}px`, minWidth: `${getColumnWidth('budget')}px` }}>
          {(() => {
            const canEdit = canEditBudget(row, currentLevel);
            let budgetDisplay: string;
            let budgetValue: number | null = null;
            
            // Xác định budget value và loại (daily/lifetime)
            const usingCampaignBudget = row.using_campaign_budget || (row.budget_level === 'CAMPAIGN');
            const isCampaignLevel = currentLevel === 'campaign';
            
            if (isCampaignLevel && row.budget_level === 'CAMPAIGN') {
              // Tab Campaign, row là campaign
              if (row.campaign_daily_budget && row.campaign_daily_budget > 0) {
                budgetValue = row.campaign_daily_budget;
                budgetDisplay = canEdit 
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách chiến dịch (${formatCurrency(budgetValue, row.currency || 'VND')}/ngày)`;
              } else if (row.campaign_lifetime_budget && row.campaign_lifetime_budget > 0) {
                budgetValue = row.campaign_lifetime_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách chiến dịch trọn đời (${formatCurrency(budgetValue, row.currency || 'VND')})`;
              } else {
                budgetDisplay = 'Ngân sách chiến dịch';
              }
            } else if (usingCampaignBudget) {
              // Adset đang dùng campaign budget (CBO)
              if (row.campaign_daily_budget && row.campaign_daily_budget > 0) {
                budgetValue = row.campaign_daily_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách chiến dịch (${formatCurrency(budgetValue, row.currency || 'VND')}/ngày)`;
              } else if (row.campaign_lifetime_budget && row.campaign_lifetime_budget > 0) {
                budgetValue = row.campaign_lifetime_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách chiến dịch trọn đời (${formatCurrency(budgetValue, row.currency || 'VND')})`;
              } else {
                budgetDisplay = 'Ngân sách chiến dịch';
              }
            } else {
              // Adset có budget riêng
              if (row.adset_daily_budget && row.adset_daily_budget > 0) {
                budgetValue = row.adset_daily_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách nhóm QC (${formatCurrency(budgetValue, row.currency || 'VND')}/ngày)`;
              } else if (row.adset_lifetime_budget && row.adset_lifetime_budget > 0) {
                budgetValue = row.adset_lifetime_budget;
                budgetDisplay = canEdit
                  ? formatCurrency(budgetValue, row.currency || 'VND')
                  : `Ngân sách nhóm QC trọn đời (${formatCurrency(budgetValue, row.currency || 'VND')})`;
              } else {
                budgetDisplay = 'Ngân sách nhóm QC';
              }
            }
            
            const budgetTitle = canEdit 
              ? 'Click để chỉnh sửa ngân sách'
              : budgetDisplay;
            
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
          {formatPercentage(row.tlc || 0)}%
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
