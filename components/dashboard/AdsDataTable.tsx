import React, { useState, useMemo } from 'react';

interface AdsetRow {
  adset_id: string;
  adset_name: string;
  campaign_name: string;
  delivery: string;
  budget: number;
  spend: number;
  results: number;
  total_leads: number;
  data_cost: number;
  cost_per_checkout_initiated: number;
  checkouts_initiated: number;
  cost_per_purchase: number;
  purchases: number;
  purchase_value: number;
  ads_percent?: number;
  cpm: number;
  impressions: number;
  reach: number;
  frequency: number;
  clicks: number;
  ctr: number;
  cpc: number;
}

interface AdsDataTableProps {
  rows: AdsetRow[];
  viewMode: 'lead' | 'ecommerce';
  currency?: string;
  loading?: boolean;
  onBudgetAdjust?: (adsetIds: string[]) => void;
  onToggleStatus?: (adsetIds: string[]) => void;
}

type SortField = keyof AdsetRow | null;
type SortDirection = 'asc' | 'desc' | null;

const formatCurrency = (value: number, currency: string = 'VND'): string => {
  if (currency === 'VND') {
    return new Intl.NumberFormat('vi-VN').format(Math.round(value));
  }
  return new Intl.NumberFormat('en-US', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  }).format(value);
};

const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('vi-VN').format(value);
};

const AdsDataTable: React.FC<AdsDataTableProps> = ({
  rows,
  viewMode,
  currency = 'VND',
  loading = false,
  onBudgetAdjust,
  onToggleStatus
}) => {
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());
  const [sortField, setSortField] = useState<SortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);

  // Sort logic
  const sortedRows = useMemo(() => {
    if (!sortField || !sortDirection) return rows;

    return [...rows].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];

      if (aVal === bVal) return 0;
      
      const comparison = aVal > bVal ? 1 : -1;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [rows, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Cycle: asc -> desc -> null
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortField(null);
        setSortDirection(null);
      }
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return '⇅';
    if (sortDirection === 'asc') return '↑';
    if (sortDirection === 'desc') return '↓';
    return '⇅';
  };

  const toggleRow = (adsetId: string) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(adsetId)) {
      newSelected.delete(adsetId);
    } else {
      newSelected.add(adsetId);
    }
    setSelectedRows(newSelected);
  };

  const toggleAll = () => {
    if (selectedRows.size === rows.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(rows.map(r => r.adset_id)));
    }
  };

  const handleBudgetAdjust = () => {
    if (selectedRows.size === 0) {
      alert('Vui lòng chọn ít nhất 1 adset');
      return;
    }
    onBudgetAdjust?.(Array.from(selectedRows));
  };

  const handleToggleStatus = () => {
    if (selectedRows.size === 0) {
      alert('Vui lòng chọn ít nhất 1 adset');
      return;
    }
    onToggleStatus?.(Array.from(selectedRows));
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-10 bg-slate-200 rounded"></div>
          {[1,2,3,4,5].map(i => (
            <div key={i} className="h-16 bg-slate-100 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200">
      {/* Toolbar */}
      <div className="p-4 border-b border-slate-200 flex gap-3">
        <button
          onClick={handleBudgetAdjust}
          disabled={selectedRows.size === 0}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium"
        >
          💰 Điều Chỉnh Ngân Sách ({selectedRows.size})
        </button>
        <button
          onClick={handleToggleStatus}
          disabled={selectedRows.size === 0}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium"
        >
          🔄 Bật/Tắt ({selectedRows.size})
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="sticky left-0 bg-slate-50 px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selectedRows.size === rows.length && rows.length > 0}
                  onChange={toggleAll}
                  className="rounded border-slate-300"
                />
              </th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Bật/Tắt</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700 min-w-[200px]">Tên</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Phân Phối</th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700">Ngân Sách</th>
              
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('spend')}>
                Chi Tiêu {getSortIcon('spend')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('results')}>
                DATA {getSortIcon('results')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700">Kết Quả</th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('data_cost')}>
                Giá DATA {getSortIcon('data_cost')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('cost_per_checkout_initiated')}>
                Chi Phí/Bắt Đầu TT {getSortIcon('cost_per_checkout_initiated')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('checkouts_initiated')}>
                Bắt Đầu TT {getSortIcon('checkouts_initiated')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('cost_per_purchase')}>
                Chi Phí/Lượt Mua {getSortIcon('cost_per_purchase')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('purchases')}>
                Lượt Mua {getSortIcon('purchases')}
              </th>
              
              {viewMode === 'ecommerce' && (
                <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('ads_percent')}>
                  % ADS {getSortIcon('ads_percent')}
                </th>
              )}
              
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('cpm')}>
                CPM {getSortIcon('cpm')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('impressions')}>
                Hiển Thị {getSortIcon('impressions')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('reach')}>
                Tiếp Cận {getSortIcon('reach')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('frequency')}>
                Tần Suất {getSortIcon('frequency')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('clicks')}>
                Nhấp {getSortIcon('clicks')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('ctr')}>
                CTR {getSortIcon('ctr')}
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('cpc')}>
                CPC {getSortIcon('cpc')}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedRows.map((row) => (
              <tr key={row.adset_id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="sticky left-0 bg-white px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedRows.has(row.adset_id)}
                    onChange={() => toggleRow(row.adset_id)}
                    className="rounded border-slate-300"
                  />
                </td>
                <td className="px-4 py-3">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked={row.delivery === 'ACTIVE'} />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </td>
                <td className="px-4 py-3 font-medium text-slate-800 max-w-xs truncate" title={row.adset_name}>
                  {row.adset_name}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    row.delivery === 'ACTIVE' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {row.delivery}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-slate-600">{formatCurrency(row.budget, currency)}</td>
                <td className="px-4 py-3 text-right font-semibold text-blue-900">{formatCurrency(row.spend, currency)}</td>
                <td className="px-4 py-3 text-right font-semibold text-green-900">{formatNumber(row.results)}</td>
                <td className="px-4 py-3 text-right text-slate-600">{formatNumber(row.total_leads)}</td>
                <td className="px-4 py-3 text-right font-semibold text-purple-900">{formatCurrency(row.data_cost, currency)}</td>
                <td className="px-4 py-3 text-right text-slate-600">{formatCurrency(row.cost_per_checkout_initiated, currency)}</td>
                <td className="px-4 py-3 text-right text-slate-600">{formatNumber(row.checkouts_initiated)}</td>
                <td className="px-4 py-3 text-right text-slate-600">{formatCurrency(row.cost_per_purchase, currency)}</td>
                <td className="px-4 py-3 text-right font-semibold text-pink-900">{formatNumber(row.purchases)}</td>
                
                {viewMode === 'ecommerce' && (
                  <td className="px-4 py-3 text-right font-semibold text-red-900">
                    {row.ads_percent !== undefined ? `${row.ads_percent.toFixed(2)}%` : '-'}
                  </td>
                )}
                
                <td className="px-4 py-3 text-right text-slate-600">{formatCurrency(row.cpm, currency)}</td>
                <td className="px-4 py-3 text-right text-slate-600">{formatNumber(row.impressions)}</td>
                <td className="px-4 py-3 text-right text-slate-600">{formatNumber(row.reach)}</td>
                <td className="px-4 py-3 text-right text-slate-600">{row.frequency.toFixed(2)}</td>
                <td className="px-4 py-3 text-right text-slate-600">{formatNumber(row.clicks)}</td>
                <td className="px-4 py-3 text-right text-slate-600">{row.ctr.toFixed(2)}%</td>
                <td className="px-4 py-3 text-right text-slate-600">{formatCurrency(row.cpc, currency)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {rows.length === 0 && (
        <div className="p-12 text-center text-slate-500">
          <p className="text-lg">📭 Không có dữ liệu</p>
          <p className="text-sm mt-2">Thử điều chỉnh bộ lọc hoặc khoảng thời gian</p>
        </div>
      )}
    </div>
  );
};

export default AdsDataTable;
