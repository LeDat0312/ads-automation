import React, { useState, useEffect } from "react";
import { Dialog, Transition, Tab } from "@headlessui/react";
import { toast } from "react-toastify";
import {
  getPagesOfFacebookAccount,
  connectPagesFromSavedAccount,
  connectPageManualV2,
  FacebookPageSummary,
} from "../api/facebookChannels";
import { listFacebookAccounts, FacebookAccount } from "../api/facebookVia";

interface ConnectFacebookPageModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ConnectFacebookPageModal({ open, onClose, onSuccess }: ConnectFacebookPageModalProps) {
  // Step 1: Via selection
  const [viaAccounts, setViaAccounts] = useState<FacebookAccount[]>([]);
  const [selectedViaId, setSelectedViaId] = useState<number | null>(null);
  const [loadingVias, setLoadingVias] = useState(false);

  // Step 2: Page list (Tab 1)
  const [pages, setPages] = useState<FacebookPageSummary[]>([]);
  const [loadingPages, setLoadingPages] = useState(false);
  const [selectedPageIds, setSelectedPageIds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  // Tab 2: Manual
  const [manualPageId, setManualPageId] = useState("");
  const [manualDisplayName, setManualDisplayName] = useState("");
  const [useViaForManual, setUseViaForManual] = useState(true);

  // General
  const [submitting, setSubmitting] = useState(false);

  // Load Via accounts on mount
  useEffect(() => {
    if (open) {
      fetchViaAccounts();
      // Reset state
      setSelectedViaId(null);
      setPages([]);
      setSelectedPageIds([]);
      setSearchQuery("");
      setManualPageId("");
      setManualDisplayName("");
      setUseViaForManual(true);
    }
    // eslint-disable-next-line
  }, [open]);

  const fetchViaAccounts = async () => {
    setLoadingVias(true);
    try {
      const res = await listFacebookAccounts({ type: "fanpage" });
      setViaAccounts(res.data);
    } catch (e: any) {
      toast.error("Không thể tải danh sách Via. Vui lòng thử lại.");
    } finally {
      setLoadingVias(false);
    }
  };

  const handleLoadPages = async () => {
    if (!selectedViaId) {
      toast.error("Vui lòng chọn Via trước.");
      return;
    }
    setLoadingPages(true);
    setPages([]);
    setSelectedPageIds([]);
    try {
      const res = await getPagesOfFacebookAccount(selectedViaId);
      setPages(res.data);
      if (res.data.length === 0) {
        toast.info("Không tìm thấy Fanpage nào từ Via này.");
      }
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Không thể tải danh sách Fanpage. Vui lòng kiểm tra lại Via.");
    } finally {
      setLoadingPages(false);
    }
  };

  const handleConnectFromList = async () => {
    if (!selectedViaId) {
      toast.error("Vui lòng chọn Via.");
      return;
    }
    if (selectedPageIds.length === 0) {
      toast.error("Vui lòng chọn ít nhất một Fanpage.");
      return;
    }
    
    // Check if any selected pages are not admin
    const selectedPages = pages.filter(p => selectedPageIds.includes(p.id));
    const nonAdminPages = selectedPages.filter(p => !p.is_admin);
    
    setSubmitting(true);
    try {
      await connectPagesFromSavedAccount({
        facebook_account_id: selectedViaId,
        page_ids: selectedPageIds,
      });
      
      // Show appropriate success message
      if (nonAdminPages.length > 0) {
        toast.success(
          `Đã kết nối ${selectedPageIds.length} Fanpage thành công.\n\n` +
          `⚠️ Lưu ý: ${nonAdminPages.length} Fanpage chưa có quyền Quản trị viên. ` +
          `Bạn cần thêm Via làm QTV trước khi dùng tính năng đăng bài/auto comment.`,
          { autoClose: 7000 }
        );
      } else {
        toast.success("Kết nối Fanpage thành công. Tất cả đều có quyền Quản trị viên.");
      }
      
      onSuccess();
      onClose();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Không thể kết nối Fanpage. Vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleConnectManual = async () => {
    if (!manualPageId.trim()) {
      toast.error("Vui lòng nhập ID Trang Facebook.");
      return;
    }
    setSubmitting(true);
    try {
      const response = await connectPageManualV2({
        page_id: manualPageId.trim(),
        facebook_account_id: useViaForManual && selectedViaId ? selectedViaId : undefined,
        page_name_override: manualDisplayName.trim() || undefined,
      });
      
      const { is_admin, warning_message } = response.data;
      
      if (warning_message) {
        toast.warning(
          `Đã kết nối Fanpage.\n\n⚠️ ${warning_message}`,
          { autoClose: 7000 }
        );
      } else if (is_admin) {
        toast.success("Kết nối Fanpage thành công. Via đã có quyền Quản trị viên.");
      } else {
        toast.success("Kết nối Fanpage thành công.");
      }
      
      onSuccess();
      onClose();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Không thể kết nối Fanpage. Vui lòng kiểm tra lại ID Trang hoặc Via.");
    } finally {
      setSubmitting(false);
    }
  };

  const togglePageSelection = (pageId: string) => {
    setSelectedPageIds(prev =>
      prev.includes(pageId) ? prev.filter(id => id !== pageId) : [...prev, pageId]
    );
  };

  const filteredPages = pages.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Transition show={open} as={React.Fragment}>
      <Dialog as="div" className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto" onClose={onClose}>
        <div className="fixed inset-0 bg-black bg-opacity-40" aria-hidden="true" />
        <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl mx-auto relative z-10 my-8">
          <div className="p-6">
            <Dialog.Title className="text-xl font-bold mb-4">Kết nối Fanpage Facebook</Dialog.Title>

            {/* Step 1: Chọn Via */}
            <div className="mb-6 border-b pb-4">
              <label className="block font-medium mb-2">Chọn Via quản lý Fanpage</label>
              <p className="text-sm text-gray-600 mb-2">Via này sẽ được dùng để tải danh sách Fanpage và kết nối kênh.</p>
              <div className="flex gap-2">
                <select
                  className="flex-1 border rounded px-3 py-2"
                  value={selectedViaId || ""}
                  onChange={e => setSelectedViaId(e.target.value ? Number(e.target.value) : null)}
                  disabled={loadingVias}
                >
                  <option value="">Chọn Via...</option>
                  {viaAccounts.map(via => (
                    <option key={via.id} value={via.id}>{via.name}</option>
                  ))}
                </select>
                <button
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={handleLoadPages}
                  disabled={!selectedViaId || loadingPages}
                >
                  {loadingPages ? "Đang tải..." : "Tải danh sách Fanpage"}
                </button>
              </div>
            </div>

            {/* Step 2: Tabs */}
            <Tab.Group>
              <Tab.List className="flex border-b mb-4">
                <Tab className={({ selected }: { selected: boolean }) =>
                  `px-4 py-2 font-medium outline-none ${selected ? "border-b-2 border-blue-600 text-blue-600" : "text-gray-600 hover:text-gray-800"}`
                }>
                  Chọn từ danh sách
                </Tab>
                <Tab className={({ selected }: { selected: boolean }) =>
                  `px-4 py-2 font-medium outline-none ${selected ? "border-b-2 border-blue-600 text-blue-600" : "text-gray-600 hover:text-gray-800"}`
                }>
                  Nhập ID thủ công
                </Tab>
              </Tab.List>
              <Tab.Panels>
                {/* Tab 1: Chọn từ danh sách */}
                <Tab.Panel>
                  {pages.length === 0 && !loadingPages ? (
                    <div className="text-center py-8 text-gray-500">
                      Chọn Via và bấm "Tải danh sách Fanpage" để bắt đầu.
                    </div>
                  ) : (
                    <>
                      <input
                        type="text"
                        placeholder="Tìm Fanpage..."
                        className="border rounded px-3 py-2 w-full mb-3"
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                      />
                      <div className="max-h-96 overflow-y-auto border rounded">
                        <table className="min-w-full">
                          <thead className="bg-gray-50 sticky top-0">
                            <tr>
                              <th className="px-4 py-2 text-left w-12"></th>
                              <th className="px-4 py-2 text-left">Tên Page</th>
                              <th className="px-4 py-2 text-left">Quyền</th>
                              <th className="px-4 py-2 text-left">ID Page</th>
                            </tr>
                          </thead>
                          <tbody>
                            {filteredPages.length === 0 ? (
                              <tr>
                                <td colSpan={4} className="text-center py-4 text-gray-500">
                                  {searchQuery ? "Không tìm thấy Fanpage phù hợp." : "Không có Fanpage."}
                                </td>
                              </tr>
                            ) : filteredPages.map(page => (
                              <tr key={page.id} className="border-b hover:bg-gray-50">
                                <td className="px-4 py-2">
                                  <input
                                    type="checkbox"
                                    checked={selectedPageIds.includes(page.id)}
                                    onChange={() => togglePageSelection(page.id)}
                                    className="w-4 h-4"
                                  />
                                </td>
                                <td className="px-4 py-2">
                                  <div className="flex items-center gap-2">
                                    {page.picture_url && (
                                      <img src={page.picture_url} alt="" className="w-8 h-8 rounded-full" />
                                    )}
                                    <span className="font-medium">{page.name}</span>
                                  </div>
                                </td>
                                <td className="px-4 py-2">
                                  {page.is_admin ? (
                                    <span 
                                      className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-green-100 text-green-800"
                                      title="Via này đang là Quản trị viên. Có thể đăng bài, lên lịch và tự động bình luận."
                                    >
                                      ✓ QTV
                                    </span>
                                  ) : (
                                    <span 
                                      className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-yellow-100 text-yellow-800"
                                      title={page.warning_message || "Via này chưa là Quản trị viên"}
                                    >
                                      ⚠ Không phải QTV
                                    </span>
                                  )}
                                </td>
                                <td className="px-4 py-2 text-sm text-gray-600">{page.id}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {selectedPageIds.length > 0 && (
                        <p className="mt-2 text-sm text-gray-600">Đã chọn: {selectedPageIds.length} Fanpage</p>
                      )}
                    </>
                  )}
                  <div className="flex gap-2 justify-end mt-4">
                    <button
                      type="button"
                      className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300"
                      onClick={onClose}
                      disabled={submitting}
                    >
                      Hủy
                    </button>
                    <button
                      type="button"
                      className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                      onClick={handleConnectFromList}
                      disabled={submitting || selectedPageIds.length === 0}
                    >
                      {submitting ? "Đang kết nối..." : `Kết nối Fanpage đã chọn`}
                    </button>
                  </div>
                </Tab.Panel>

                {/* Tab 2: Nhập ID thủ công */}
                <Tab.Panel>
                  <div className="space-y-4">
                    <div>
                      <label className="block font-medium mb-1">
                        ID Trang Facebook <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        className="border rounded px-3 py-2 w-full"
                        placeholder="Ví dụ: 687520047771032"
                        value={manualPageId}
                        onChange={e => setManualPageId(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={useViaForManual}
                          onChange={e => setUseViaForManual(e.target.checked)}
                          className="w-4 h-4"
                        />
                        <span className="text-sm">Sử dụng Via đã chọn ở bước 1 để kiểm tra và kết nối</span>
                      </label>
                      {useViaForManual && !selectedViaId && (
                        <p className="text-xs text-yellow-600 mt-1">⚠️ Chưa chọn Via. Vui lòng chọn Via ở trên hoặc bỏ chọn tùy chọn này.</p>
                      )}
                    </div>
                    <div>
                      <label className="block font-medium mb-1">Tên hiển thị (tuỳ chọn)</label>
                      <input
                        type="text"
                        className="border rounded px-3 py-2 w-full"
                        placeholder="Để trống để tự động lấy từ Facebook"
                        value={manualDisplayName}
                        onChange={e => setManualDisplayName(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="flex gap-2 justify-end mt-6">
                    <button
                      type="button"
                      className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300"
                      onClick={onClose}
                      disabled={submitting}
                    >
                      Hủy
                    </button>
                    <button
                      type="button"
                      className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                      onClick={handleConnectManual}
                      disabled={submitting}
                    >
                      {submitting ? "Đang kết nối..." : "Kết nối"}
                    </button>
                  </div>
                </Tab.Panel>
              </Tab.Panels>
            </Tab.Group>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
