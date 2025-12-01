import React, { useState } from 'react';
import { Dialog, Transition, Tab } from '@headlessui/react';

interface SpinContentModalProps {
  open: boolean;
  onClose: () => void;
  onInsert: (text: string) => void;
}

// Preset icon groups
const ICON_PRESETS = [
  {
    id: 'R1',
    name: 'Cảm xúc vui vẻ',
    icons: ['😊', '😄', '🥰', '😍', '🤗', '😘', '💕', '❤️'],
  },
  {
    id: 'R2',
    name: 'Thích thú',
    icons: ['👍', '👏', '🙌', '💪', '✨', '🌟', '⭐', '🎉'],
  },
  {
    id: 'R3',
    name: 'Hoa lá',
    icons: ['🌸', '🌺', '🌻', '🌷', '🌹', '💐', '🌼', '🏵️'],
  },
  {
    id: 'R4',
    name: 'Động vật dễ thương',
    icons: ['🐶', '🐱', '🐰', '🐻', '🐼', '🐨', '🦊', '🐹'],
  },
  {
    id: 'R5',
    name: 'Thức ăn',
    icons: ['🍕', '🍔', '🍟', '🌭', '🍿', '🧁', '🍰', '🎂'],
  },
  {
    id: 'R6',
    name: 'Đồ uống',
    icons: ['☕', '🍵', '🧃', '🥤', '🧋', '🍹', '🍸', '🥂'],
  },
];

const SpinContentModal: React.FC<SpinContentModalProps> = ({ open, onClose, onInsert }) => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [textSample, setTextSample] = useState('Sản phẩm tuyệt vời|Chất lượng cao|Giá cả hợp lý');

  const handleInsertIcon = (presetId: string) => {
    onInsert(`@icon{${presetId}}`);
    onClose();
  };

  const handleInsertText = () => {
    if (textSample.trim()) {
      onInsert(`#text{${textSample}}`);
      onClose();
    }
  };

  return (
    <Transition show={open} as={React.Fragment}>
      <Dialog as="div" className="fixed inset-0 z-50 overflow-y-auto" onClose={onClose}>
        <div className="min-h-screen px-4 text-center">
          <Transition.Child
            as={React.Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-40" />
          </Transition.Child>

          <span className="inline-block h-screen align-middle" aria-hidden="true">
            &#8203;
          </span>

          <Transition.Child
            as={React.Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <div className="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <Dialog.Title className="text-xl font-bold text-gray-900">
                  Spin Content
                </Dialog.Title>
                <button
                  onClick={onClose}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Tabs */}
              <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
                <Tab.List className="flex space-x-1 rounded-xl bg-indigo-50 p-1 mb-6">
                  <Tab
                    className={({ selected }) =>
                      `w-full rounded-lg py-2.5 text-sm font-medium leading-5 transition-all
                      ${
                        selected
                          ? 'bg-white text-indigo-700 shadow'
                          : 'text-indigo-600 hover:bg-white/[0.5] hover:text-indigo-700'
                      }`
                    }
                  >
                    Spin Icon
                  </Tab>
                  <Tab
                    className={({ selected }) =>
                      `w-full rounded-lg py-2.5 text-sm font-medium leading-5 transition-all
                      ${
                        selected
                          ? 'bg-white text-indigo-700 shadow'
                          : 'text-indigo-600 hover:bg-white/[0.5] hover:text-indigo-700'
                      }`
                    }
                  >
                    Spin Text
                  </Tab>
                </Tab.List>

                <Tab.Panels>
                  {/* Spin Icon Panel */}
                  <Tab.Panel>
                    <div className="space-y-4">
                      {/* Description */}
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <div className="text-2xl">💡</div>
                          <div>
                            <h4 className="font-medium text-blue-900 mb-1">Cách dùng Spin Icon</h4>
                            <p className="text-sm text-blue-800">
                              Khi dùng Spin Icon, hệ thống sẽ chọn ngẫu nhiên một icon từ bộ preset để thêm vào bình luận.
                              Ví dụ: <code className="bg-blue-100 px-1 rounded">@icon{'{R1}'}</code> sẽ random một trong các icon: 😊 😄 🥰 😍...
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Icon Presets */}
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {ICON_PRESETS.map((preset) => (
                          <div
                            key={preset.id}
                            className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 hover:bg-indigo-50/30 transition-all"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div>
                                <span className="font-medium text-gray-900">{preset.name}</span>
                                <code className="ml-2 text-xs bg-gray-100 px-2 py-0.5 rounded text-indigo-600">
                                  @icon{'{' + preset.id + '}'}
                                </code>
                              </div>
                              <button
                                onClick={() => handleInsertIcon(preset.id)}
                                className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                              >
                                Dùng
                              </button>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {preset.icons.map((icon, idx) => (
                                <span key={idx} className="text-2xl">
                                  {icon}
                                </span>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Tab.Panel>

                  {/* Spin Text Panel */}
                  <Tab.Panel>
                    <div className="space-y-4">
                      {/* Description */}
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <div className="text-2xl">💡</div>
                          <div>
                            <h4 className="font-medium text-green-900 mb-1">Cách dùng Spin Text</h4>
                            <p className="text-sm text-green-800 mb-2">
                              Thêm được tối đa 10 giá trị ngẫu nhiên, cách nhau bằng dấu <code className="bg-green-100 px-1 rounded">|</code>
                            </p>
                            <p className="text-sm text-green-800">
                              Cấu trúc: <code className="bg-green-100 px-1 rounded">#text{'{choice1|choice2|choice3}'}</code>
                            </p>
                            <p className="text-xs text-green-700 mt-2">
                              Ví dụ: "Sản phẩm <code className="bg-green-100 px-1 rounded">#text{'{tuyệt vời|chất lượng|đẳng cấp}'}</code>"
                              → Random thành "Sản phẩm tuyệt vời" hoặc "Sản phẩm chất lượng" hoặc "Sản phẩm đẳng cấp"
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Input */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Nhập các lựa chọn (cách nhau bằng dấu |)
                        </label>
                        <textarea
                          className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                          rows={4}
                          placeholder="Ví dụ: Sản phẩm tuyệt vời|Chất lượng cao|Giá cả hợp lý|Đáng mua nhất"
                          value={textSample}
                          onChange={(e) => setTextSample(e.target.value)}
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Tối đa 10 lựa chọn, mỗi lựa chọn cách nhau bằng dấu |
                        </p>
                      </div>

                      {/* Preview */}
                      {textSample && (
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                          <p className="text-sm font-medium text-gray-700 mb-2">Kết quả:</p>
                          <code className="text-sm bg-white px-3 py-2 rounded border border-gray-200 block">
                            #text{'{' + textSample + '}'}
                          </code>
                        </div>
                      )}

                      {/* Insert Button */}
                      <button
                        onClick={handleInsertText}
                        disabled={!textSample.trim()}
                        className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                      >
                        Chèn vào bình luận
                      </button>
                    </div>
                  </Tab.Panel>
                </Tab.Panels>
              </Tab.Group>
            </div>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
};

export default SpinContentModal;
