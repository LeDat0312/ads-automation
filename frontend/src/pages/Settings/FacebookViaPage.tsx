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
dayjs.locale("vi");

const TYPE_LABEL: Record<FacebookAccountType, string> = {
  fanpage: "Via cầm Fanpage",
  ads: "Via Automation Ads",
  both: "Cả hai",
};

const TYPE_BADGE: Record<FacebookAccountType, string> = {
  fanpage: "bg-blue-100 text-blue-700",
  ads: "bg-yellow-100 text-yellow-700",
  both: "bg-green-100 text-green-700",
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
    if (!window.confirm("Bạn có chắc muốn xoá Via này?")) return;
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
      
      // Reload danh sách để cập nhật last_verified_at
      fetchAccounts();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Token không còn hợp lệ hoặc bị hết hạn.");
    } finally {
      setVerifyingId(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <h1 className="text-2xl font-bold mb-2">Quản lý Via Facebook</h1>
      <p className="mb-4 text-gray-600">Lưu trữ và quản lý token Facebook (Via) để sử dụng cho Fanpage và tài khoản quảng cáo.</p>
      <div className="flex items-center gap-4 mb-4">
        <label className="font-medium">Lọc loại Via:</label>
        <select
          className="border rounded px-2 py-1"
          value={filter}
          onChange={e => setFilter(e.target.value as "" | "fanpage" | "ads" | "both")}
        >
          {FILTER_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <button
          className="ml-auto bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          onClick={() => { setEditAccount(null); setModalOpen(true); }}
        >
          + Thêm Via
        </button>
      </div>
      <div className="bg-white shadow rounded overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-4 py-2 text-left">Tên Via</th>
              <th className="px-4 py-2 text-left">Loại</th>
              <th className="px-4 py-2 text-left">Token</th>
              <th className="px-4 py-2 text-left">Trạng thái</th>
              <th className="px-4 py-2 text-left">Lần xác thực gần nhất</th>
              <th className="px-4 py-2 text-left">Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="text-center py-8">Đang tải...</td></tr>
            ) : accounts.length === 0 ? (
              <tr><td colSpan={6} className="text-center py-8">Chưa có Via nào.</td></tr>
            ) : accounts.map(acc => (
              <tr key={acc.id} className="border-b">
                <td className="px-4 py-2 font-medium">{acc.name}</td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${TYPE_BADGE[acc.token_type]}`}>{TYPE_LABEL[acc.token_type]}</span>
                </td>
                <td className="px-4 py-2 font-mono text-xs">{acc.masked_token}</td>
                <td className="px-4 py-2">
                  {acc.is_active ? <span className="text-green-600">Đang hoạt động</span> : <span className="text-gray-400">Tạm tắt</span>}
                </td>
                <td className="px-4 py-2 text-xs">
                  {acc.last_verified_at ? dayjs(acc.last_verified_at).format("DD/MM/YYYY HH:mm") : "Chưa xác thực"}
                </td>
                <td className="px-4 py-2 flex gap-2">
                  <button
                    className="bg-indigo-600 text-white px-2 py-1 rounded text-xs hover:bg-indigo-700 disabled:opacity-50"
                    disabled={!!verifyingId}
                    onClick={() => handleVerify(acc.id)}
                  >
                    {verifyingId === acc.id ? "Đang xác thực..." : "Xác thực token"}
                  </button>
                  <button
                    className="bg-yellow-500 text-white px-2 py-1 rounded text-xs hover:bg-yellow-600"
                    onClick={() => { setEditAccount(acc); setModalOpen(true); }}
                  >Sửa</button>
                  <button
                    className="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600"
                    onClick={() => handleDelete(acc.id)}
                  >Xóa</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
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
        <div className="fixed inset-0 bg-black bg-opacity-30" aria-hidden="true" />
        <div className="bg-white rounded shadow-lg p-6 w-full max-w-md mx-auto relative z-10">
          <Dialog.Title className="text-lg font-bold mb-2">{editAccount ? "Sửa Via Facebook" : "Thêm Via Facebook"}</Dialog.Title>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block font-medium mb-1">Tên Via <span className="text-red-500">*</span></label>
              <input
                type="text"
                className="border rounded px-3 py-2 w-full"
                value={name}
                onChange={e => setName(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block font-medium mb-1">Loại Via</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-1">
                  <input type="radio" name="type" value="fanpage" checked={tokenType === "fanpage"} onChange={() => setTokenType("fanpage")}/>
                  Via cầm Fanpage
                </label>
                <label className="flex items-center gap-1">
                  <input type="radio" name="type" value="ads" checked={tokenType === "ads"} onChange={() => setTokenType("ads")}/>
                  Via Automation Ads
                </label>
                <label className="flex items-center gap-1">
                  <input type="radio" name="type" value="both" checked={tokenType === "both"} onChange={() => setTokenType("both")}/>
                  Cả hai
                </label>
              </div>
            </div>
            <div>
              <label className="block font-medium mb-1">Access Token Facebook {editAccount ? <span className="text-xs text-gray-400">(để trống nếu không đổi)</span> : <span className="text-red-500">*</span>}</label>
              <input
                type="password"
                className="border rounded px-3 py-2 w-full font-mono"
                value={accessToken}
                onChange={e => setAccessToken(e.target.value)}
                placeholder="EAAFoR78zi...b5ZD"
                autoComplete="off"
                {...(editAccount ? {} : { required: true })}
              />
            </div>
            <div>
              <label className="block font-medium mb-1">Ghi chú (tuỳ chọn)</label>
              <textarea
                className="border rounded px-3 py-2 w-full"
                value={note}
                onChange={e => setNote(e.target.value)}
                rows={2}
                placeholder="Ví dụ: Via chính cho TikTok Shop"
              />
            </div>
            <div className="flex gap-2 justify-end mt-4">
              <button
                type="button"
                className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300"
                onClick={onClose}
                disabled={loading}
              >Hủy</button>
              <button
                type="submit"
                className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                disabled={loading}
              >{loading ? "Đang lưu..." : (editAccount ? "Cập nhật" : "Lưu Via")}</button>
            </div>
          </form>
        </div>
      </Dialog>
    </Transition>
  );
}
