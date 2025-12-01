import React, { useState } from 'react';
import { Transition } from '@headlessui/react';
import MediaUploadCard from './MediaUploadCard';

interface AutoCommentTemplateCardProps {
  index: number;
  template: {
    id: string;
    content: string;
    media_url?: string;
    delay_minutes?: number;
    is_active: boolean;
  };
  onUpdate: (updates: Partial<AutoCommentTemplateCardProps['template']>) => void;
  onDelete: () => void;
  onOpenSpinModal: () => void;
}

// Delay options
const DELAY_OPTIONS = [
  { label: 'Đăng ngay', value: 0 },
  { label: 'Sau 5 phút', value: 5 },
  { label: 'Sau 10 phút', value: 10 },
  { label: 'Sau 15 phút', value: 15 },
  { label: 'Sau 30 phút', value: 30 },
  { label: 'Sau 45 phút', value: 45 },
  { label: 'Sau 1 giờ', value: 60 },
  { label: 'Sau 2 giờ', value: 120 },
  { label: 'Sau 3 giờ', value: 180 },
  { label: 'Sau 6 giờ', value: 360 },
  { label: 'Sau 12 giờ', value: 720 },
  { label: 'Sau 24 giờ', value: 1440 },
  { label: 'Ngày mai cùng giờ', value: 1440 },
  { label: 'Sau 2 ngày', value: 2880 },
  { label: 'Sau 3 ngày', value: 4320 },
];

const AutoCommentTemplateCard: React.FC<AutoCommentTemplateCardProps> = ({
  index,
  template,
  onUpdate,
  onDelete,
  onOpenSpinModal,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const getDelayLabel = (minutes?: number) => {
    if (!minutes || minutes === 0) return 'Đăng ngay';
    const option = DELAY_OPTIONS.find((o) => o.value === minutes);
    if (option) return option.label;
    if (minutes < 60) return `Sau ${minutes} phút`;
    if (minutes < 1440) return `Sau ${Math.floor(minutes / 60)} giờ`;
    return `Sau ${Math.floor(minutes / 1440)} ngày`;
  };

  const handleMediaUpload = async (file: File): Promise<string> => {
    // TODO: Implement actual upload
    const url = URL.createObjectURL(file);
    onUpdate({ media_url: url });
    return url;
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      {/* Header - Always visible */}
      <div
        className={`p-4 flex items-center justify-between cursor-pointer transition-colors ${
          template.is_active ? 'bg-white hover:bg-gray-50' : 'bg-gray-100'
        }`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          {/* Expand/Collapse Icon */}
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>

          {/* Title */}
          <span className="font-medium text-gray-900">Mẫu #{index + 1}</span>

          {/* Status Badge */}
          {template.delay_minutes && template.delay_minutes > 0 && (
            <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">
              {getDelayLabel(template.delay_minutes)}
            </span>
          )}
        </div>

        <div className="flex items-center gap-3" onClick={(e) => e.stopPropagation()}>
          {/* Toggle Switch */}
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={template.is_active}
              onChange={(e) => onUpdate({ is_active: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
          </label>

          {/* Delete Button */}
          <button
            onClick={onDelete}
            className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
            title="Xoá mẫu"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Collapsible Content */}
      <Transition
        show={isExpanded}
        enter="transition-all duration-200 ease-out"
        enterFrom="opacity-0 max-h-0"
        enterTo="opacity-100 max-h-[1000px]"
        leave="transition-all duration-150 ease-in"
        leaveFrom="opacity-100 max-h-[1000px]"
        leaveTo="opacity-0 max-h-0"
      >
        <div className="p-4 border-t border-gray-200 space-y-4">
          {/* Content Textarea */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nội dung</label>
            <textarea
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
              rows={4}
              placeholder="Nhập nội dung bình luận..."
              value={template.content}
              onChange={(e) => onUpdate({ content: e.target.value })}
            />
            <div className="flex items-center justify-between mt-1">
              <p className="text-xs text-gray-500 flex items-center gap-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                </svg>
                Dùng #text{'{a|b|c}'} để random nội dung
              </p>
              <button
                onClick={onOpenSpinModal}
                className="text-xs text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1"
              >
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zM12 2a1 1 0 01.967.744L14.146 7.2 17.5 9.134a1 1 0 010 1.732l-3.354 1.935-1.18 4.455a1 1 0 01-1.933 0L9.854 12.8 6.5 10.866a1 1 0 010-1.732l3.354-1.935 1.18-4.455A1 1 0 0112 2z" />
                </svg>
                Dùng Spin Content
              </button>
            </div>
          </div>

          {/* Media Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Media (tuỳ chọn)
            </label>
            <MediaUploadCard
              mediaUrl={template.media_url}
              onUpload={handleMediaUpload}
              onRemove={() => onUpdate({ media_url: undefined })}
              accept="image/*,video/mp4"
              maxSizeMB={50}
            />
          </div>

          {/* Delay Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Thời gian đăng</label>
            <select
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={template.delay_minutes || 0}
              onChange={(e) => onUpdate({ delay_minutes: parseInt(e.target.value) })}
            >
              {DELAY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Transition>
    </div>
  );
};

export default AutoCommentTemplateCard;
