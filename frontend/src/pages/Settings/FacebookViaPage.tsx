import React, { useEffect, useState } from "react";
import {
  listFacebookAccounts,
  createFacebookAccount,
  updateFacebookAccount,
  deleteFacebookAccount,
  verifyFacebookAccount,
  FacebookAccount,
  FacebookAccountType,
} from "../../api/facebookVia";
import { Dialog, Transition } from "@headlessui/react";
import { toast } from "react-toastify";
import dayjs from "dayjs";
import "dayjs/locale/vi";
import { Badge, EmptyState, PageHeader } from "../../components/ui";

dayjs.locale("vi");

const TYPE_LABEL: Record<FacebookAccountType, string> = {
  fanpage: "Via cầm Fanpage",
  ads: "Via Automation Ads",
  both: "Cả hai",
};

const TYPE_BADGE_VARIANT: Record<FacebookAccountType, 'info' | 'warning' | 'success'> = {
  fanpage: "info",
  ads: "warning",
  both: "success",
};

const FILTER_OPTIONS = [
  { value: "", label: "Tất cả" },
  { value: "fanpage", label: "Via cầm Fanpage" },
  { value: "ads", label: "Via Automation Ads" },
  { value: "both", label: "Cả hai" },
];

export default function FacebookViaPage() {
  const [accounts, setAccounts] = useState<FacebookAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<"" | "fanpage" | "ads" | "both">("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editAccount, setEditAccount] = useState<FacebookAccount | null>(null);
  const [verifyingId, setVerifyingId] = useState<number | null>(null);

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const params = filter ? { type: filter as "fanpage" | "ads" | "both" } : undefined;
      const res = await listFacebookAccounts(params);
      setAccounts(res.data);
    } catch (e: any) {
      toast.error("Không thể tải danh sách Via. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
    // eslint-disable-next-line
  }, [filter]);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Bạn có chắc muốn xoá Via này? Các Fanpage đang sử dụng Via này sẽ không thể hoạt động.")) return;
    try {
      await deleteFacebookAccount(id);
      toast.success("Xoá Via thành công.");
      fetchAccounts();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Không thể xoá Via.");
    }
  };

  const handleVerify = async (id: number) => {
    setVerifyingId(id);
    try {
      const res = await verifyFacebookAccount(id);
      const data = res.data;
      
      if (data.valid) {
        toast.success(data.message || "Token còn hoạt động.");
      } else {
        toast.error(data.message || "Token không còn hợp lệ hoặc bị hết hạn.");
      }
      
      fetchAccounts();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Token không còn hợp lệ hoặc bị hết hạn.");
    } finally {
      setVerifyingId(null);
    }
  };

  const getStatusBadge = (account: FacebookAccount) => {
    if (!account.last_verified_at) {
      return <Badge variant="neutral">Chưa kiểm tra</Badge>;
    }
    if (account.is_active) {
      return <Badge variant="success">Đang hoạt động</Badge>;
    }
    return <Badge variant="error">Hết hạn</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Quản lý Via Facebook"
        subtitle="Lưu trữ và quản lý token Facebook (Via) để sử dụng cho Fanpage và tài khoản quảng cáo."
        actions={
          <button
            onClick={() => { setEditAccount(null); setModalOpen(true); }}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Thêm Via
          </button>
        }
      />

      {/* Toolbar */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex items-center gap-3">
            <label className="text-sm font-medium text-gray-700">Lọc loại Via:</label>
            <select
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={filter}
              onChange={e => setFilter(e.target.value as "" | "fanpage" | "ads" | "both")}
            >
              {FILTER_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>{accounts.length} Via</span>
            <span>•</span>
            <span>{accounts.filter(a => a.is_active).length} đang hoạt động</span>
          </div>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Đang tải danh sách Via...</p>
        </div>
      ) : accounts.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200">
          <EmptyState
            icon="🔑"
            title="Chưa có Via nào"
            description="Via là token Facebook dùng để quản lý Fanpage và chạy quảng cáo. Hãy thêm ít nhất 1 Via để kết nối Fanpage."
            action={{
              label: "+ Thêm Via đầu tiên",
              onClick: () => { setEditAccount(null); setModalOpen(true); },
            }}
          />
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Tên Via</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Loại</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Token</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Trạng thái</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Lần xác thực</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-900">Hành động</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {accounts.map(acc => (
                <tr key={acc.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-4">
                    <div className="font-medium text-gray-900">{acc.name}</div>
                    {acc.last_error && (
                      <div className="text-xs text-red-500 mt-1 truncate max-w-xs" title={acc.last_error}>
                        ⚠️ {acc.last_error.substring(0, 50)}...
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-4">
                    <Badge variant={TYPE_BADGE_VARIANT[acc.token_type]}>
                      {TYPE_LABEL[acc.token_type]}
                    </Badge>
                  </td>
                  <td className="px-4 py-4">
                    <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded text-gray-600">
                      {acc.masked_token}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    {getStatusBadge(acc)}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-500">
                    {acc.last_verified_at 
                      ? dayjs(acc.last_verified_at).format("DD/MM/YYYY HH:mm")
                      : <span className="text-gray-400">Chưa xác thực</span>
                    }
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={!!verifyingId}
                        onClick={() => handleVerify(acc.id)}
                      >
                        {verifyingId === acc.id ? (
                          <span className="flex items-center gap-1">
                            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                            Đang xác thực
                          </span>
                        ) : "Xác thực"}
                      </button>
                      <button
                        className="px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                        onClick={() => { setEditAccount(acc); setModalOpen(true); }}
                      >
                        Sửa
                      </button>
                      <button
                        className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        onClick={() => handleDelete(acc.id)}
                      >
                        Xóa
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      <FacebookViaFormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={() => { setModalOpen(false); fetchAccounts(); }}
        editAccount={editAccount}
      />
    </div>
  );
}

// Modal component
function FacebookViaFormModal({ open, onClose, onSuccess, editAccount }: {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editAccount: FacebookAccount | null;
}) {
  const [name, setName] = useState("");
  const [tokenType, setTokenType] = useState<FacebookAccountType>("fanpage");
  const [accessToken, setAccessToken] = useState("");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editAccount) {
      setName(editAccount.name);
      setTokenType(editAccount.token_type);
      setNote(editAccount.note || "");
      setAccessToken("");
    } else {
      setName("");
      setTokenType("fanpage");
      setNote("");
      setAccessToken("");
    }
  }, [editAccount, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (!name.trim()) {
        toast.error("Vui lòng nhập tên Via.");
        setLoading(false);
        return;
      }
      if (!editAccount && !accessToken.trim()) {
        toast.error("Vui lòng nhập Access Token.");
        setLoading(false);
        return;
      }
      if (editAccount) {
        await updateFacebookAccount(editAccount.id, {
          name,
          token_type: tokenType,
          access_token: accessToken || undefined,
          note,
        });
        toast.success("Cập nhật Via thành công.");
      } else {
        await createFacebookAccount({
          name,
          token_type: tokenType,
          access_token: accessToken,
          note,
        });
        toast.success("Thêm Via Facebook thành công.");
      }
      onSuccess();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Không thể lưu Via. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Transition show={open} as={React.Fragment}>
      <Dialog as="div" className="fixed inset-0 z-50 flex items-center justify-center" onClose={onClose}>
        <div className="fixed inset-0 bg-black bg-opacity-40" aria-hidden="true" />
        <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-auto relative z-10">
          <Dialog.Title className="text-xl font-bold mb-4">
            {editAccount ? "Sửa Via Facebook" : "Thêm Via Facebook"}
          </Dialog.Title>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tên Via <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="Ví dụ: Via chính - Quản lý Pages"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Loại Via</label>
              <div className="flex flex-wrap gap-3">
                {(['fanpage', 'ads', 'both'] as const).map(type => (
                  <label key={type} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="type"
                      value={type}
                      checked={tokenType === type}
                      onChange={() => setTokenType(type)}
                      className="text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="text-sm">{TYPE_LABEL[type]}</span>
                  </label>
                ))}
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Access Token Facebook
                {editAccount 
                  ? <span className="text-gray-400 font-normal ml-1">(để trống nếu không đổi)</span>
                  : <span className="text-red-500 ml-1">*</span>
                }
              </label>
              <input
                type="password"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 font-mono text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                value={accessToken}
                onChange={e => setAccessToken(e.target.value)}
                placeholder="EAAFoR78zi...b5ZD"
                autoComplete="off"
                {...(editAccount ? {} : { required: true })}
              />
              <p className="text-xs text-gray-500 mt-1">
                Lấy token từ Facebook Business Suite hoặc Graph API Explorer
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ghi chú (tuỳ chọn)</label>
              <textarea
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                value={note}
                onChange={e => setNote(e.target.value)}
                rows={2}
                placeholder="Ví dụ: Via chính cho TikTok Shop"
              />
            </div>
            
            <div className="flex gap-3 justify-end pt-4 border-t">
              <button
                type="button"
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                onClick={onClose}
                disabled={loading}
              >
                Hủy
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Đang lưu...
                  </span>
                ) : (editAccount ? "Cập nhật" : "Lưu Via")}
              </button>
            </div>
          </form>
        </div>
      </Dialog>
    </Transition>
  );
}
