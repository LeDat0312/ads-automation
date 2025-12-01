import React, { useState, useRef, useEffect } from 'react';
import { Dialog, Transition, Tab } from '@headlessui/react';

interface VideoEditorModalProps {
  open: boolean;
  onClose: () => void;
  videoUrl: string;
  onSave: (editedVideoUrl: string, thumbnailUrl?: string) => void;
}

type Tool = 'trim' | 'crop' | 'finetune' | 'filter' | 'annotate' | 'sticker' | 'resize';

interface Annotation {
  id: string;
  type: 'text' | 'rectangle';
  x: number;
  y: number;
  width: number;
  height: number;
  text?: string;
  color: string;
  fontSize?: number;
}

const FILTERS = [
  { id: 'none', name: 'Gốc', style: '' },
  { id: 'warm', name: 'Ấm', style: 'sepia(0.3) saturate(1.2)' },
  { id: 'cold', name: 'Lạnh', style: 'saturate(0.8) hue-rotate(180deg)' },
  { id: 'pastel', name: 'Pastel', style: 'saturate(0.7) brightness(1.1)' },
  { id: 'mono', name: 'Đen trắng', style: 'grayscale(1)' },
  { id: 'vintage', name: 'Vintage', style: 'sepia(0.5) contrast(1.1)' },
  { id: 'vivid', name: 'Sống động', style: 'saturate(1.5) contrast(1.1)' },
];

const CROP_PRESETS = [
  { id: '9:16', name: '9:16 (Reel)', ratio: 9 / 16 },
  { id: '1:1', name: '1:1 (Vuông)', ratio: 1 },
  { id: '4:5', name: '4:5 (Portrait)', ratio: 4 / 5 },
  { id: '16:9', name: '16:9 (Landscape)', ratio: 16 / 9 },
  { id: 'free', name: 'Tự do', ratio: 0 },
];

const VideoEditorModal: React.FC<VideoEditorModalProps> = ({
  open,
  onClose,
  videoUrl,
  onSave,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [activeTool, setActiveTool] = useState<Tool>('trim');
  
  // Trim state
  const [trimStart, setTrimStart] = useState(0);
  const [trimEnd, setTrimEnd] = useState(100);
  const [duration, setDuration] = useState(0);
  
  // Crop state
  const [cropPreset, setCropPreset] = useState('9:16');
  
  // Finetune state
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [saturation, setSaturation] = useState(100);
  const [temperature, setTemperature] = useState(0);
  
  // Filter state
  const [selectedFilter, setSelectedFilter] = useState('none');
  
  // Annotation state
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [annotationMode, setAnnotationMode] = useState<'text' | 'rectangle' | null>(null);
  const [annotationColor, setAnnotationColor] = useState('#FFFFFF');
  
  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.onloadedmetadata = () => {
        setDuration(videoRef.current?.duration || 0);
      };
    }
  }, [videoUrl]);

  const getFilterStyle = () => {
    const filter = FILTERS.find((f) => f.id === selectedFilter);
    let style = filter?.style || '';
    
    // Add finetune adjustments
    style += ` brightness(${brightness / 100}) contrast(${contrast / 100}) saturate(${saturation / 100})`;
    
    if (temperature !== 0) {
      style += temperature > 0 ? ` sepia(${temperature / 100})` : ` hue-rotate(${temperature}deg)`;
    }
    
    return style;
  };

  const handleAddAnnotation = (type: 'text' | 'rectangle') => {
    const newAnnotation: Annotation = {
      id: `ann-${Date.now()}`,
      type,
      x: 50,
      y: 50,
      width: type === 'text' ? 200 : 150,
      height: type === 'text' ? 40 : 100,
      text: type === 'text' ? 'Nhập text...' : undefined,
      color: annotationColor,
      fontSize: 24,
    };
    setAnnotations([...annotations, newAnnotation]);
  };

  const handleDeleteAnnotation = (id: string) => {
    setAnnotations(annotations.filter((a) => a.id !== id));
  };

  const handleSave = async () => {
    setIsProcessing(true);
    
    try {
      // TODO: Implement actual video processing with FFmpeg.wasm
      // For now, just return the original video with metadata
      
      // Simulate processing
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      // In real implementation:
      // 1. Use FFmpeg.wasm to trim video
      // 2. Apply filters using canvas
      // 3. Overlay annotations
      // 4. Export as new video file
      
      onSave(videoUrl);
      onClose();
    } catch (error) {
      console.error('Error processing video:', error);
      alert('Lỗi khi xử lý video');
    } finally {
      setIsProcessing(false);
    }
  };

  const tools: { id: Tool; icon: string; label: string }[] = [
    { id: 'trim', icon: '✂️', label: 'Cắt' },
    { id: 'crop', icon: '⬜', label: 'Crop' },
    { id: 'finetune', icon: '🎚️', label: 'Chỉnh' },
    { id: 'filter', icon: '✨', label: 'Filter' },
    { id: 'annotate', icon: '✏️', label: 'Chú thích' },
    { id: 'sticker', icon: '😀', label: 'Sticker' },
    { id: 'resize', icon: '📐', label: 'Resize' },
  ];

  return (
    <Transition show={open} as={React.Fragment}>
      <Dialog as="div" className="fixed inset-0 z-50 overflow-hidden" onClose={onClose}>
        <div className="min-h-screen">
          <Transition.Child
            as={React.Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black" />
          </Transition.Child>

          <div className="fixed inset-0 flex">
            {/* Left Toolbar */}
            <div className="w-20 bg-gray-900 flex flex-col items-center py-4 gap-2">
              {tools.map((tool) => (
                <button
                  key={tool.id}
                  onClick={() => setActiveTool(tool.id)}
                  className={`w-16 h-16 flex flex-col items-center justify-center rounded-lg transition-colors ${
                    activeTool === tool.id
                      ? 'bg-indigo-600 text-white'
                      : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  <span className="text-xl">{tool.icon}</span>
                  <span className="text-xs mt-1">{tool.label}</span>
                </button>
              ))}
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
              {/* Header */}
              <div className="h-14 bg-gray-900 flex items-center justify-between px-4">
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                
                <div className="flex items-center gap-2">
                  <span className="text-white text-sm">Zoom:</span>
                  <select className="bg-gray-800 text-white text-sm rounded px-2 py-1">
                    <option>40%</option>
                    <option>60%</option>
                    <option>80%</option>
                    <option>100%</option>
                  </select>
                </div>

                <button
                  onClick={handleSave}
                  disabled={isProcessing}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  {isProcessing ? 'Đang xử lý...' : 'Done'}
                </button>
              </div>

              {/* Video Preview */}
              <div className="flex-1 flex items-center justify-center p-8">
                <div className="relative bg-black rounded-lg overflow-hidden shadow-2xl">
                  <video
                    ref={videoRef}
                    src={videoUrl}
                    className="max-h-[60vh]"
                    style={{ filter: getFilterStyle() }}
                    controls
                  />
                  
                  {/* Annotations Overlay */}
                  <div className="absolute inset-0 pointer-events-none">
                    {annotations.map((ann) => (
                      <div
                        key={ann.id}
                        className="absolute pointer-events-auto cursor-move"
                        style={{
                          left: ann.x,
                          top: ann.y,
                          width: ann.width,
                          height: ann.height,
                        }}
                      >
                        {ann.type === 'rectangle' ? (
                          <div
                            className="w-full h-full border-2"
                            style={{ backgroundColor: ann.color, opacity: 0.8 }}
                          />
                        ) : (
                          <div
                            className="w-full h-full flex items-center justify-center"
                            style={{ color: ann.color, fontSize: ann.fontSize }}
                          >
                            {ann.text}
                          </div>
                        )}
                        <button
                          onClick={() => handleDeleteAnnotation(ann.id)}
                          className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div className="h-32 bg-gray-900 p-4">
                <div className="h-full bg-gray-800 rounded-lg overflow-hidden">
                  {/* Frame thumbnails would go here */}
                  <div className="h-full flex items-center px-4">
                    <div className="flex-1 h-16 bg-gray-700 rounded relative">
                      {/* Trim handles */}
                      <div
                        className="absolute top-0 bottom-0 left-0 w-1 bg-yellow-500 cursor-ew-resize"
                        style={{ left: `${trimStart}%` }}
                      />
                      <div
                        className="absolute top-0 bottom-0 right-0 w-1 bg-yellow-500 cursor-ew-resize"
                        style={{ right: `${100 - trimEnd}%` }}
                      />
                      <div
                        className="absolute top-0 bottom-0 bg-indigo-500/30"
                        style={{ left: `${trimStart}%`, right: `${100 - trimEnd}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Panel - Tool Options */}
            <div className="w-72 bg-gray-900 p-4 overflow-y-auto">
              {activeTool === 'trim' && (
                <div className="space-y-4">
                  <h3 className="text-white font-medium">Cắt video</h3>
                  <div>
                    <label className="text-gray-400 text-sm">Bắt đầu</label>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={trimStart}
                      onChange={(e) => setTrimStart(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <span className="text-white text-sm">{((trimStart / 100) * duration).toFixed(1)}s</span>
                  </div>
                  <div>
                    <label className="text-gray-400 text-sm">Kết thúc</label>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={trimEnd}
                      onChange={(e) => setTrimEnd(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <span className="text-white text-sm">{((trimEnd / 100) * duration).toFixed(1)}s</span>
                  </div>
                </div>
              )}

              {activeTool === 'crop' && (
                <div className="space-y-4">
                  <h3 className="text-white font-medium">Crop video</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {CROP_PRESETS.map((preset) => (
                      <button
                        key={preset.id}
                        onClick={() => setCropPreset(preset.id)}
                        className={`p-3 rounded-lg text-sm transition-colors ${
                          cropPreset === preset.id
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                      >
                        {preset.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {activeTool === 'finetune' && (
                <div className="space-y-4">
                  <h3 className="text-white font-medium">Chỉnh sửa</h3>
                  <div>
                    <label className="text-gray-400 text-sm">Độ sáng: {brightness}%</label>
                    <input
                      type="range"
                      min={50}
                      max={150}
                      value={brightness}
                      onChange={(e) => setBrightness(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-gray-400 text-sm">Tương phản: {contrast}%</label>
                    <input
                      type="range"
                      min={50}
                      max={150}
                      value={contrast}
                      onChange={(e) => setContrast(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-gray-400 text-sm">Bão hoà: {saturation}%</label>
                    <input
                      type="range"
                      min={0}
                      max={200}
                      value={saturation}
                      onChange={(e) => setSaturation(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-gray-400 text-sm">Nhiệt độ màu: {temperature}</label>
                    <input
                      type="range"
                      min={-50}
                      max={50}
                      value={temperature}
                      onChange={(e) => setTemperature(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </div>
              )}

              {activeTool === 'filter' && (
                <div className="space-y-4">
                  <h3 className="text-white font-medium">Bộ lọc</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {FILTERS.map((filter) => (
                      <button
                        key={filter.id}
                        onClick={() => setSelectedFilter(filter.id)}
                        className={`p-3 rounded-lg text-sm transition-colors ${
                          selectedFilter === filter.id
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                      >
                        {filter.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {activeTool === 'annotate' && (
                <div className="space-y-4">
                  <h3 className="text-white font-medium">Chú thích</h3>
                  <p className="text-gray-400 text-sm">
                    Thêm text hoặc hình chữ nhật để che chữ gốc
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleAddAnnotation('text')}
                      className="flex-1 p-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      + Text
                    </button>
                    <button
                      onClick={() => handleAddAnnotation('rectangle')}
                      className="flex-1 p-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      + Hình CN
                    </button>
                  </div>
                  <div>
                    <label className="text-gray-400 text-sm">Màu</label>
                    <input
                      type="color"
                      value={annotationColor}
                      onChange={(e) => setAnnotationColor(e.target.value)}
                      className="w-full h-10 rounded cursor-pointer"
                    />
                  </div>
                  {annotations.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-gray-400 text-sm">Danh sách ({annotations.length})</p>
                      {annotations.map((ann, idx) => (
                        <div
                          key={ann.id}
                          className="flex items-center justify-between p-2 bg-gray-800 rounded"
                        >
                          <span className="text-white text-sm">
                            {ann.type === 'text' ? '📝' : '⬜'} #{idx + 1}
                          </span>
                          <button
                            onClick={() => handleDeleteAnnotation(ann.id)}
                            className="text-red-400 hover:text-red-300"
                          >
                            Xoá
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTool === 'sticker' && (
                <div className="space-y-4">
                  <h3 className="text-white font-medium">Sticker</h3>
                  <div className="grid grid-cols-4 gap-2">
                    {['😀', '😍', '🔥', '💯', '👍', '❤️', '✨', '🎉', '💪', '🙌', '👏', '🤩'].map(
                      (emoji) => (
                        <button
                          key={emoji}
                          className="p-3 text-2xl bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
                        >
                          {emoji}
                        </button>
                      )
                    )}
                  </div>
                </div>
              )}

              {activeTool === 'resize' && (
                <div className="space-y-4">
                  <h3 className="text-white font-medium">Resize</h3>
                  <p className="text-gray-400 text-sm">
                    Xuất video với kích thước chuẩn
                  </p>
                  <div className="space-y-2">
                    <button className="w-full p-3 bg-indigo-600 text-white rounded-lg">
                      1080 × 1920 (Reel)
                    </button>
                    <button className="w-full p-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700">
                      1080 × 1080 (Vuông)
                    </button>
                    <button className="w-full p-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700">
                      1920 × 1080 (Ngang)
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default VideoEditorModal;
