import React, { useRef, useState } from 'react';

interface MediaUploadCardProps {
  mediaUrl?: string;
  onUpload: (file: File) => Promise<string>; // Returns URL after upload
  onRemove: () => void;
  accept?: string; // e.g., "image/*,video/mp4"
  maxSizeMB?: number;
}

const MediaUploadCard: React.FC<MediaUploadCardProps> = ({
  mediaUrl,
  onUpload,
  onRemove,
  accept = 'image/*,video/mp4',
  maxSizeMB = 50,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
      setUploadError(`File quá lớn. Tối đa ${maxSizeMB}MB`);
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      await onUpload(file);
    } catch (error: any) {
      setUploadError(error.message || 'Lỗi khi tải lên');
    } finally {
      setIsUploading(false);
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const isVideo = mediaUrl?.match(/\.(mp4|mov|avi|webm)$/i);
  const isImage = mediaUrl && !isVideo;

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg overflow-hidden hover:border-indigo-400 transition-colors">
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileSelect}
        className="hidden"
      />

      {!mediaUrl ? (
        // Empty state
        <button
          onClick={handleClick}
          disabled={isUploading}
          className="w-full p-6 text-center hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          {isUploading ? (
            <div className="flex flex-col items-center gap-2">
              <svg className="animate-spin h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <p className="text-sm text-gray-600">Đang tải lên...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <div>
                <p className="text-sm font-medium text-gray-700">Không có media</p>
                <p className="text-xs text-gray-500 mt-1">Click để tải lên ảnh hoặc video</p>
              </div>
              <p className="text-xs text-gray-400 mt-2">Tối đa {maxSizeMB}MB</p>
            </div>
          )}
        </button>
      ) : (
        // Media preview
        <div className="relative group">
          {isImage && (
            <img src={mediaUrl} alt="Preview" className="w-full h-48 object-cover" />
          )}
          {isVideo && (
            <video src={mediaUrl} className="w-full h-48 object-cover" controls />
          )}

          {/* Overlay with actions */}
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center gap-2">
            <button
              onClick={handleClick}
              className="opacity-0 group-hover:opacity-100 transition-opacity px-3 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-100 text-sm font-medium"
            >
              Thay đổi
            </button>
            <button
              onClick={onRemove}
              className="opacity-0 group-hover:opacity-100 transition-opacity px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium"
            >
              Xoá
            </button>
          </div>
        </div>
      )}

      {uploadError && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-200">
          <p className="text-xs text-red-600">{uploadError}</p>
        </div>
      )}
    </div>
  );
};

export default MediaUploadCard;
