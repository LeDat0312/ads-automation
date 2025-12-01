import React, { useState, useRef } from 'react';
import { Dialog, Transition, Tab } from '@headlessui/react';

interface ThumbnailModalProps {
  open: boolean;
  onClose: () => void;
  videoUrl?: string;
  onApply: (thumbnail: File | string) => void; // File for upload, string for video frame
}

const ThumbnailModal: React.FC<ThumbnailModalProps> = ({
  open,
  onClose,
  videoUrl,
  onApply,
}) => {
  const [selectedTab, setSelectedTab] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);

  const handleCaptureFrame = () => {
    if (!videoRef.current) return;

    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'thumbnail.jpg', { type: 'image/jpeg' });
        onApply(file);
        onClose();
      }
    }, 'image/jpeg', 0.9);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Vui lòng chọn file ảnh');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('File quá lớn. Tối đa 5MB');
      return;
    }

    setUploadedImage(file);
    setUploadPreview(URL.createObjectURL(file));
  };

  const handleApplyUpload = () => {
    if (uploadedImage) {
      onApply(uploadedImage);
      onClose();
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setUploadedImage(file);
      setUploadPreview(URL.createObjectURL(file));
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
            <div className="fixed inset-0 bg-black bg-opacity-50" />
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
            <div className="inline-block w-full max-w-3xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <Dialog.Title className="text-xl font-bold text-gray-900">
                  Chọn Thumbnail
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
                    Chọn từ video
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
                    Tải ảnh lên
                  </Tab>
                </Tab.List>

                <Tab.Panels>
                  {/* Video Frame Tab */}
                  <Tab.Panel>
                    <div className="space-y-4">
                      {videoUrl ? (
                        <>
                          <div className="bg-gray-100 rounded-lg overflow-hidden">
                            <video
                              ref={videoRef}
                              src={videoUrl}
                              controls
                              className="w-full"
                              style={{ maxHeight: '400px' }}
                            />
                          </div>
                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <p className="text-sm text-blue-800">
                              💡 Di chuyển video đến frame mong muốn, sau đó bấm "Chụp thumbnail" để lưu.
                            </p>
                          </div>
                          <button
                            onClick={handleCaptureFrame}
                            className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                          >
                            Chụp thumbnail
                          </button>
                        </>
                      ) : (
                        <div className="text-center py-12">
                          <div className="text-4xl mb-2">🎬</div>
                          <p className="text-gray-500">Chưa có video để chọn thumbnail</p>
                        </div>
                      )}
                    </div>
                  </Tab.Panel>

                  {/* Upload Tab */}
                  <Tab.Panel>
                    <div className="space-y-4">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleFileSelect}
                        className="hidden"
                      />

                      {!uploadPreview ? (
                        <div
                          onDrop={handleDrop}
                          onDragOver={(e) => e.preventDefault()}
                          onClick={() => fileInputRef.current?.click()}
                          className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-indigo-400 hover:bg-indigo-50/30 transition-all cursor-pointer"
                        >
                          <svg
                            className="w-16 h-16 text-gray-400 mx-auto mb-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                          </svg>
                          <p className="text-gray-700 font-medium mb-1">
                            Click để chọn ảnh hoặc kéo thả vào đây
                          </p>
                          <p className="text-sm text-gray-500">PNG, JPG, GIF - Tối đa 5MB</p>
                        </div>
                      ) : (
                        <>
                          <div className="relative">
                            <img
                              src={uploadPreview}
                              alt="Preview"
                              className="w-full rounded-lg"
                              style={{ maxHeight: '400px', objectFit: 'contain' }}
                            />
                            <button
                              onClick={() => {
                                setUploadedImage(null);
                                setUploadPreview(null);
                              }}
                              className="absolute top-2 right-2 p-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          </div>
                          <button
                            onClick={handleApplyUpload}
                            className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                          >
                            Áp dụng thumbnail
                          </button>
                        </>
                      )}
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

export default ThumbnailModal;
