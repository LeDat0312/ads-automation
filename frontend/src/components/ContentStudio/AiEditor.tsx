/**
 * AI Editor Component
 * Biên tập và dịch caption bằng AI (Gemini/ChatGPT)
 */

import React, { useState, useEffect } from 'react';
import { ContentVariant, AiRewriteMode } from '../../types/contentStudio';
import { rewriteCaption } from '../../api/contentStudio';

interface AiEditorProps {
  variant: ContentVariant | null;
  onSave: (updatedVariant: Partial<ContentVariant>) => void;
  isLoading?: boolean;
}

const AiEditor: React.FC<AiEditorProps> = ({
  variant,
  onSave,
  isLoading = false
}) => {
  const [caption, setCaption] = useState('');
  const [captionLao, setCaptionLao] = useState('');
  const [title, setTitle] = useState('');
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [callToAction, setCallToAction] = useState('');
  const [hashtagInput, setHashtagInput] = useState('');
  const [isRewriting, setIsRewriting] = useState(false);
  const [aiVariants, setAiVariants] = useState<string[]>([]);

  useEffect(() => {
    if (variant) {
      setCaption(variant.caption);
      setCaptionLao(variant.captionLao);
      setTitle(variant.title);
      setHashtags(variant.hashtags);
      setCallToAction(variant.callToAction || '');
    }
  }, [variant]);

  const handleAiRewrite = async (mode: AiRewriteMode) => {
    if (!caption.trim()) return;

    setIsRewriting(true);
    try {
      const response = await rewriteCaption({
        sourceCaption: caption,
        sourceLang: 'vi',
        targetLang: 'lo',
        mode
      });

      if (mode === AiRewriteMode.GENERATE_VARIANTS && response.variants) {
        setAiVariants(response.variants);
      } else {
        setCaptionLao(response.rewrittenCaption);
      }
    } catch (error) {
      console.error('AI rewrite error:', error);
      alert('Lỗi khi dịch bằng AI. Vui lòng thử lại.');
    } finally {
      setIsRewriting(false);
    }
  };

  const handleAddHashtag = () => {
    if (hashtagInput.trim()) {
      const newTag = hashtagInput.trim().startsWith('#')
        ? hashtagInput.trim()
        : `#${hashtagInput.trim()}`;
      
      if (!hashtags.includes(newTag)) {
        setHashtags([...hashtags, newTag]);
      }
      setHashtagInput('');
    }
  };

  const handleRemoveHashtag = (tag: string) => {
    setHashtags(hashtags.filter(t => t !== tag));
  };

  const handleSave = () => {
    onSave({
      caption,
      captionLao,
      title,
      hashtags,
      callToAction
    });
  };

  if (!variant) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-12 text-center">
        <div className="text-gray-400 text-6xl mb-4">✏️</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Chọn nội dung để biên tập
        </h3>
        <p className="text-gray-500">
          Chọn một item từ bộ sưu tập để bắt đầu biên tập và dịch
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Column - Text Editing */}
      <div className="space-y-4">
        <div className="bg-white rounded-lg shadow-sm p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            📝 Biên tập nội dung
          </h3>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tiêu đề
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Nhập tiêu đề bài đăng..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Original Caption */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nội dung gốc (Tiếng Việt)
            </label>
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              rows={6}
              placeholder="Nhập hoặc dán nội dung gốc..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* AI Buttons */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleAiRewrite(AiRewriteMode.TRANSLATE)}
              disabled={isRewriting || !caption.trim()}
              className="px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              🤖 Dịch sang tiếng Lào
            </button>
            <button
              onClick={() => handleAiRewrite(AiRewriteMode.REWRITE_SALON_STYLE)}
              disabled={isRewriting || !caption.trim()}
              className="px-4 py-2 bg-pink-600 text-white text-sm rounded-lg hover:bg-pink-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              💅 Viết lại kiểu thẩm mỹ
            </button>
            <button
              onClick={() => handleAiRewrite(AiRewriteMode.GENERATE_VARIANTS)}
              disabled={isRewriting || !caption.trim()}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              🎲 Tạo 3 phiên bản
            </button>
          </div>

          {isRewriting && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              AI đang xử lý...
            </div>
          )}

          {/* AI Variants */}
          {aiVariants.length > 0 && (
            <div className="border border-blue-200 bg-blue-50 rounded-lg p-4 space-y-3">
              <p className="text-sm font-medium text-blue-900">
                🎯 3 phiên bản AI tạo ra:
              </p>
              {aiVariants.map((variant, index) => (
                <div
                  key={index}
                  className="bg-white p-3 rounded border border-blue-200"
                >
                  <p className="text-sm text-gray-700 mb-2">{variant}</p>
                  <button
                    onClick={() => {
                      setCaptionLao(variant);
                      setAiVariants([]);
                    }}
                    className="text-xs text-blue-600 hover:text-blue-700"
                  >
                    ✓ Chọn phiên bản này
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Lao Caption */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nội dung tiếng Lào
            </label>
            <textarea
              value={captionLao}
              onChange={(e) => setCaptionLao(e.target.value)}
              rows={6}
              placeholder="Nội dung sau khi dịch sẽ hiện ở đây..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Hashtags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Hashtags
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={hashtagInput}
                onChange={(e) => setHashtagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddHashtag()}
                placeholder="#themymyvien"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleAddHashtag}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Thêm
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {hashtags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                >
                  {tag}
                  <button
                    onClick={() => handleRemoveHashtag(tag)}
                    className="hover:text-blue-900"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Call to Action */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lời kêu gọi hành động
            </label>
            <input
              type="text"
              value={callToAction}
              onChange={(e) => setCallToAction(e.target.value)}
              placeholder="VD: Inbox ngay để được tư vấn miễn phí!"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={isLoading || !captionLao.trim()}
            className="w-full px-4 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            💾 Lưu & chuyển sang lên lịch
          </button>
        </div>
      </div>

      {/* Right Column - Media Preview */}
      <div className="space-y-4">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            👁️ Xem trước
          </h3>

          {/* Media Display */}
          {variant.media && variant.media.length > 0 ? (
            <div className="space-y-4">
              {variant.media.map((media, index) => (
                <div key={media.id} className="rounded-lg overflow-hidden bg-gray-100">
                  {media.type === 'video' ? (
                    <video
                      src={media.url}
                      controls
                      poster={media.thumbnailUrl}
                      className="w-full"
                    />
                  ) : (
                    <img
                      src={media.url}
                      alt={`Media ${index + 1}`}
                      className="w-full"
                    />
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">
              Không có media
            </div>
          )}

          {/* Preview Card */}
          <div className="mt-6 border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">{title || 'Tiêu đề bài đăng'}</h4>
            <p className="text-sm text-gray-700 whitespace-pre-wrap mb-3">
              {captionLao || caption || 'Nội dung sẽ hiện ở đây...'}
            </p>
            {hashtags.length > 0 && (
              <p className="text-sm text-blue-600">
                {hashtags.join(' ')}
              </p>
            )}
            {callToAction && (
              <p className="text-sm font-medium text-green-600 mt-2">
                {callToAction}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AiEditor;
